"""Input validation: the checks on the inputs that need more than one
field, or a lookup. It runs before anything is computed (engine.run).
"""

from __future__ import annotations

from typing import cast

from handrail import joints, materials, members
from handrail.calc import compare, fmt_g, fmt_quantity_plain, fmt_sig, number
from handrail.joints import JointMember
from handrail.materials import BASEPLATE_GRADES, FEXX_ENTRY
from handrail.orientation import post_axes, rail_axes
from handrail.project import SAME_AS_TOP, Member, Project, ProjectError
from handrail.registry import Registry
from handrail.shapes import Section
from handrail.stops import Stop
from handrail.units import Q_
from handrail.welds import base_pattern


def require_supported_grade(registry: Registry, member: Member, sec: Section, name: str) -> None:
    """Refuse a grade the tool has no Fy and Fu entries for, for the
    member's shape, naming the grade and the grades supported for that
    shape. Both values are needed: Fy for the member checks, Fu for the
    fusion face of a weld (Check 3's rail side, Check 4b's post and
    intermediate rail walls) and the post wall's Fu/Fy guard.

    A grade whose Fy and Fu go by wall thickness (A618, S5-7) also stops
    here when the member's nominal wall is over the thickest wall it has
    values for (materials.py).
    """
    if member.grade not in materials.supported(sec.family):
        raise ProjectError(materials.unsupported_message(name, member.grade, sec.family),
                           stop=Stop.GRADE_UNSUPPORTED)
    materials.yield_stress(registry, member.grade, sec, name.capitalize())


OD_TOLERANCE = "ej.section.od_tolerance"
CHORD_LIMIT = "aisc360.K.round_chord.D_over_t_max"
CHORD_STOP = "ej.weld.chord_D_over_t_stop"


def require_chord_within_limit(registry: Registry, sec: Section, name: str) -> None:
    """Refuse a round top rail whose D/t is over the Chapter K limit of
    applicability for the chord of a round T-connection (S5-3, kept by
    S6-13). The rail wall at the post is checked under a round post
    (S6-10) and is a stated assumption under a rectangular one (S6-9),
    and either way only up to the limit. D/t is the value the section's
    classification uses (design wall).

    The limit is read for every calc with a round rail, so each lists it
    while it is drafted. The decision behind the stop is read only when it
    stops.
    """
    limit = registry.get(CHORD_LIMIT)
    over = compare(number(sec.D_t, fmt_g), ">", number(limit.value))
    if over:
        rule = registry.get(CHORD_STOP)
        raise ProjectError(
            f"{name} {sec.label}: D/t = {sec.ratio_text(sec.D_t)} {over.op} {over.right.text}, the limit of applicability "
            f"for the chord of a round T-connection ({limit.cite}). The rail wall at the post is checked, or held "
            f"as a stated assumption, only within the Chapter K limits of applicability ({rule.cite}). "
            f"The tool does not check this section as a chord.",
            stop=Stop.SECTION_CHORD_D_T_OVER_LIMIT
        )


BRANCH_LIMIT, BRANCH_COEFF = "aisc360.K3.1A.branch_D_over_t_max", "aisc360.K3.1A.branch_D_over_t_coeff"
WIDTH_RATIO_MIN = "aisc360.K3.1A.width_ratio_min"


def require_round_branch_within_limits(registry: Registry, project: Project, rail: Section, post: Section) -> None:
    """Refuse a round post on a round rail outside the branch limits of
    AISC 360-22 Tables K3.1A and K4.1A (S6-13), where the chord check of
    Check 3 is computed (S6-10): the post's D/t over 50, or over 0.05
    E/Fyb, or the width ratio Db/D not over 0.2.

    The width ratio's upper bound, Db/D <= 1.0, is W8's test, with its OD
    tolerance (S5-4); it is not made a second time here (plan, open item 2).
    """
    rule = LIMITS_STOP
    limit = registry.get(BRANCH_LIMIT)
    ratio = number(post.D_t, fmt_g)
    over = compare(ratio, ">", number(limit.value))
    if over:
        raise ProjectError(
            f"post {post.label}: D/t = {post.ratio_text(post.D_t)} {over.op} {over.right.text}, the limit of "
            f"applicability for the branch of a round T-connection ({limit.cite}; {registry.get(rule).cite}). The tool "
            f"does not check this section as a branch on a round rail.", stop=Stop.SECTION_BRANCH_D_T_OVER_LIMIT)
    coeff = registry.get(BRANCH_COEFF)
    E = registry.get("material.steel.E").quantity
    Fyb = materials.yield_stress(registry, project.post.grade, post).quantity(registry)
    by_grade = (coeff.value * E / Fyb).m_as("dimensionless")
    over = compare(ratio, ">", number(by_grade, fmt_sig))
    if over:
        raise ProjectError(
            f"post {post.label}, {project.post.grade}: D/t = {post.ratio_text(post.D_t)} {over.op} {coeff.value}E/Fyb = "
            f"{over.right.text}, the limit of applicability for the branch of a round T-connection ({coeff.cite}; "
            f"{registry.get(rule).cite}). The tool does not check this section as a branch on a round rail.",
            stop=Stop.SECTION_BRANCH_D_T_OVER_LIMIT)
    low = registry.get(WIDTH_RATIO_MIN)
    width = (post.OD / rail.OD).m_as("dimensionless")
    within = compare(number(width, fmt_sig), ">", number(low.value))
    if not within:
        raise ProjectError(
            f"post {post.label} on top rail {rail.label}: Db/D = {within.left.text} {within.op} {within.right.text}. "
            f"The width ratio of a round T-connection must be over {low.value} ({low.cite}; "
            f"{registry.get(rule).cite}). The tool does not check a post this narrow against its rail.",
            stop=Stop.JOINT_CHECK3_WIDTH_RATIO_BELOW_LIMIT)


CHORD_WALL_LIMIT = "aisc360.K1.3.rect_chord.wall_max"
FY_LIMIT, FY_FU_LIMIT, FY_FU_EXCEPTION = "aisc360.K1.3.Fy_max", "aisc360.K1.3.Fy_Fu_max", "aisc360.K1.3.A500_GrC_note"
LIMITS_STOP = "ej.weld.chord_limits_stop"
WIDTH_RULE = "ej.weld.width_rule"


def require_rect_chord_within_limit(registry: Registry, sec: Section, name: str) -> None:
    """Refuse a rectangular chord whose B/t or H/t is over the Chapter K
    limit of applicability (S6-13), on the outside dimensions and the
    design wall. The chord wall's local strength is a stated assumption
    there (S6-12), made only up to the limit."""
    limit = registry.get(CHORD_WALL_LIMIT)
    r = sec.rect
    for letter, side in (("B", r.B), ("H", r.H)):
        ratio = (side / sec.tdes).m_as("dimensionless")
        over = compare(number(ratio, fmt_sig), ">", number(limit.value))
        if over:
            rule = registry.get(LIMITS_STOP)
            raise ProjectError(
                f"{name} {sec.label}: {letter}/t = {over.left.text} {over.op} {over.right.text}, the limit of "
                f"applicability for the chord of a rectangular HSS connection ({limit.cite}), on the outside "
                f"dimension {fmt_quantity_plain(side)} and the design wall {fmt_quantity_plain(sec.tdes)}. The local "
                f"strength of the rail wall at the post is a stated assumption, not a check, and it is not assumed "
                f"for a chord over the limit ({rule.cite}). The tool does not check this section as a chord.",
                stop=Stop.SECTION_CHORD_WALL_OVER_LIMIT
            )


def require_material_within_limits(registry: Registry, member: Member, sec: Section, name: str) -> None:
    """Refuse a member at the rail to post joint whose grade is outside the
    Chapter K material limits (S6-13): Fy over 52 ksi, or Fy/Fu over 0.8.
    ASTM A500 Grade C is the tables' named exception to the second: it
    passes whatever its ratio."""
    Fy = materials.yield_stress(registry, member.grade, sec).quantity(registry)
    Fu = materials.tensile_strength(registry, member.grade, sec).quantity(registry)
    fy_max = registry.get(FY_LIMIT)
    over = compare(number(Fy, fmt_quantity_plain), ">", number(fy_max.quantity, fmt_quantity_plain))
    if over:
        rule = registry.get(LIMITS_STOP)
        raise ProjectError(
            f"{name} {sec.label}, {member.grade}: Fy = {over.left.text} {over.op} {over.right.text}, the limit of "
            f"applicability for an HSS connection ({fy_max.cite}; {rule.cite}). The tool does not check this "
            f"grade at the rail to post joint.", stop=Stop.JOINT_CHECK3_FY_OVER_LIMIT)
    ratio_max = registry.get(FY_FU_LIMIT)
    ratio = (Fy / Fu).m_as("dimensionless")
    over = compare(number(ratio, fmt_sig), ">", number(ratio_max.value))
    if over:
        # Read only when the ratio is over: the exception decides nothing else.
        exception = registry.get(FY_FU_EXCEPTION)
        if member.grade in exception.value:
            return
        rule = registry.get(LIMITS_STOP)
        raise ProjectError(
            f"{name} {sec.label}, {member.grade}: Fy/Fu = {over.left.text} {over.op} {over.right.text}, the "
            f"ductility limit of applicability for an HSS connection ({ratio_max.cite}; {rule.cite}). The tool "
            f"does not check this grade at the rail to post joint.", stop=Stop.JOINT_CHECK3_FY_FU_OVER_LIMIT)


def wider(registry: Registry, a: Q_, b: Q_) -> bool:
    """Whether outside diameter ``a`` is wider than ``b`` for the width
    comparisons W8 and S4-11: greater by more than the tolerance within
    which two outside diameters are equal (S5-4). The database rounds a
    round HSS's OD (2.38 in for HSS2.375) and stores a pipe's exactly
    (2.375 in), so a pipe and an HSS of one size differ on paper only.

    The tolerance is read only when it decides, so a calc whose members
    are no wider than they may be does not list it as used.
    """
    if not a > b:
        return False
    # Round the difference to 0.0001 in so a float such as 1.91 - 1.90 =
    # 0.010000000000000009 in counts as exactly 0.01 in, which is equal.
    difference = round((a - b).to("in").magnitude, 4)
    return difference > registry.get(OD_TOLERANCE).quantity.to("in").magnitude


def validate(project: Project, registry: Registry) -> None:
    """The input checks that need more than one field, or a lookup. Raises an
    InputError naming what it checked and why. Runs before compute, so no
    check runs on inputs that fail.

    - the sections exist;
    - the section families at each joint are a pair its table lists as
      allowed (joints.py, S5-9; before the tables, W7 and S4-12's stop on a
      section that is not round hollow);
    - the rail to post joint is within the Chapter K limits of applicability
      (S5-3, S6-13): the top rail's wall slenderness, and its grade's Fy and
      Fy/Fu; for a round post on a round rail the post's too, with the
      width ratio's lower bound;
    - each grade is one the tool supports for its member's shape (S5-5), and
      the electrode and the baseplate grade are ones it supports (W12);
    - the post is no wider than the rail (W8), ODs within 0.01 in being
      equal (S5-4);
    - the post grade's Fu/Fy keeps its wall at the weld covered by Check 5 (W5);
    - the intermediate rail is no wider than the post (S4-11), with the same
      tolerance;
    - the baseplate is no smaller in plan than the post OD (S4-6).
    """
    m = members.resolve(project, registry)
    project, rail, post, inter = m.project, m.rail, m.post, m.own

    # The section families at each joint (S5-9): a pair its table does not
    # list as allowed stops here, before anything is computed. They come
    # before the grades, because a grade is supported for a shape: a family
    # the tool does not have yet has no grades to name.
    at_post = JointMember("post", post)
    joints.CHECK_3.require(chord=JointMember("top rail", rail), branch=at_post, error=ProjectError)
    if project.intermediate_member is not None:
        same = project.intermediate_rail.state == SAME_AS_TOP
        # Its own section was looked up above when it is not the top rail's.
        branch = rail if same else cast(Section, inter)
        joints.CHECK_4B.require(chord=at_post, branch=JointMember("intermediate rail", branch), error=ProjectError)
    joints.CHECK_7.require(at_post, error=ProjectError)
    # The post to baseplate weld's pattern (S6-6): the same test Check 7 makes.
    base_pattern(registry, project, post, error=ProjectError)

    # The chord's wall slenderness at the rail to post joint (S5-3, S6-13):
    # the top rail's D/t, or B/t and H/t. The post is a chord at the
    # intermediate rail, but no force is normal to its wall there, and
    # Check 4b has no applicability stop (S6-11, S6-13).
    if rail.is_round:
        require_chord_within_limit(registry, rail, "top rail")
    else:
        require_rect_chord_within_limit(registry, rail, "top rail")

    require_supported_grade(registry, project.top_rail, rail, "top rail")
    require_supported_grade(registry, project.post, post, "post")
    own = project.intermediate_rail.member  # its own section, or None
    if own:
        require_supported_grade(registry, own, cast(Section, inter), "intermediate rail")
    electrode = project.welds.electrode
    if electrode not in FEXX_ENTRY:
        raise ProjectError(f"[welds] electrode {electrode!r}: this version supports {', '.join(FEXX_ENTRY)} only",
                           stop=Stop.WELD_ELECTRODE_UNSUPPORTED)
    if project.baseplate.grade not in BASEPLATE_GRADES:
        raise ProjectError(f"[baseplate] grade {project.baseplate.grade!r}: this version supports "
                           f"{', '.join(BASEPLATE_GRADES)} only", stop=Stop.BASEPLATE_GRADE_UNSUPPORTED)

    round_on_round = rail.is_round and post.is_round

    # The width rule (W8, S6-9): the post no wider across the rail than the
    # rail itself. Exact where either is rectangular; two round members
    # within the OD tolerance are equal (S5-4).
    rail_ax, post_ax = rail_axes(rail, project.top_rail.long_side), post_axes(post, project.post.long_side)
    if round_on_round:
        D_rail, D_post = rail.OD, post.OD
        if wider(registry, D_post, D_rail):
            raise ProjectError(
                f"The post ({post.label}, OD {fmt_quantity_plain(D_post)}) is wider than the top rail "
                f"({rail.label}, OD {fmt_quantity_plain(D_rail)}). The coped post to rail underside detail "
                f"requires post OD <= rail OD. Check the inputs.", stop=Stop.SECTION_POST_WIDER_THAN_RAIL
            )
    elif post_ax.perpendicular > rail_ax.width:
        rule = registry.get(WIDTH_RULE)
        raise ProjectError(
            f"The post ({post.label}, {fmt_quantity_plain(post_ax.perpendicular)} perpendicular to the rail) is "
            f"wider than the top rail ({rail.label}, {fmt_quantity_plain(rail_ax.width)} wide). The post is welded "
            f"to the rail's underside, and a branch may not be wider than its chord ({rule.cite}). Check the "
            f"sections and their long_side.", stop=Stop.SECTION_POST_WIDER_THAN_RAIL
        )

    grade = project.post.grade
    Fy = materials.yield_stress(registry, grade, post).quantity(registry)
    Fu = materials.tensile_strength(registry, grade, post).quantity(registry)
    limit = registry.get("ej.weld.post_wall.fu_fy_min")
    ratio = Fu / Fy
    if ratio < limit.value:
        raise ProjectError(
            f"post grade {grade}: Fu/Fy = {fmt_sig(ratio.m_as('dimensionless'))} is below {limit.value} ({limit.cite}). "
            f"The post wall at the weld is covered by Check 5 only while yielding governs over rupture; "
            f"the tool does not check this grade's post wall at the weld.", stop=Stop.GRADE_POST_FU_FY_BELOW_LIMIT
        )

    # The Chapter K limits of applicability at the rail to post joint
    # (S6-13), after the post grade's own guard above, which is the older
    # stop and names what it protects. A round post on a round rail, where the chord check is
    # computed: every limit, for the chord and for the branch. Where the
    # chord wall is a stated assumption (a rectangular rail, or a round and
    # a rectangular member meeting): the chord's own material limits only.
    if round_on_round:
        require_round_branch_within_limits(registry, project, rail, post)
        require_material_within_limits(registry, project.top_rail, rail, "top rail")
        require_material_within_limits(registry, project.post, post, "post")
    else:
        require_material_within_limits(registry, project.top_rail, rail, "top rail")

    member = project.intermediate_member
    if member is not None:
        same = project.intermediate_rail.state == SAME_AS_TOP
        sec = rail if same else cast(Section, inter)
        how = ("With same_as_top_rail = true it takes the top rail's section: uncheck same_as_top_rail and "
               "enter a section no wider than the post." if same else
               "Enter a section no wider than the post.")
        if sec.is_round and post.is_round:
            if wider(registry, sec.OD, post.OD):
                raise ProjectError(
                    f"The intermediate rail ({sec.label}, OD {fmt_quantity_plain(sec.OD)}) is wider than the post "
                    f"({post.label}, OD {fmt_quantity_plain(post.OD)}). Its end is coped to the side of the post, "
                    f"which requires intermediate rail OD <= post OD. {how}",
                    stop=Stop.SECTION_INTERMEDIATE_WIDER_THAN_POST
                )
        else:
            # The width rule at the post face (S4-11, S6-9), exact.
            width = rail_axes(sec, member.long_side).width
            if width > post_ax.perpendicular:
                rule = registry.get(WIDTH_RULE)
                raise ProjectError(
                    f"The intermediate rail ({sec.label}, {fmt_quantity_plain(width)} wide) is wider than the post "
                    f"({post.label}, {fmt_quantity_plain(post_ax.perpendicular)} perpendicular to the rail). Its end "
                    f"is welded to the side of the post, and a branch may not be wider than its chord "
                    f"({rule.cite}). {how}",
                    stop=Stop.SECTION_INTERMEDIATE_WIDER_THAN_POST
                )

    # The baseplate no smaller in plan than the post, in each direction
    # (S4-6; S6-14 item 8): B against the post's dimension parallel to the
    # rail, N against the one perpendicular to it. A round post has one.
    for name, d, orientation, side in (("B", project.baseplate.B, "parallel to the rail", post_ax.parallel),
                                       ("N", project.baseplate.N, "perpendicular to the rail", post_ax.perpendicular)):
        if d.value < side:
            what = "OD" if post.is_round else f"dimension {orientation}"
            raise ProjectError(
                f"[baseplate] {name} = {d.entered} ({orientation}) is smaller than the post {what} "
                f"({post.label}, {fmt_quantity_plain(side)}). Check the inputs.",
                stop=Stop.BASEPLATE_SMALLER_THAN_POST
            )
