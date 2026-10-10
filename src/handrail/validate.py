"""Input validation: the checks on the inputs that need more than one
field, or a lookup. It runs before anything is computed (engine.run).
"""

from __future__ import annotations

from typing import cast

from handrail import joints, materials, members
from handrail.calc import fmt_quantity_plain, fmt_sig
from handrail.joints import JointMember
from handrail.materials import BASEPLATE_GRADES, FEXX_ENTRY
from handrail.project import SAME_AS_TOP, Member, Project, ProjectError
from handrail.registry import Registry
from handrail.shapes import Section
from handrail.stops import Stop


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


def validate(project: Project, registry: Registry) -> None:
    """The input checks that need more than one field, or a lookup. Raises an
    InputError naming what it checked and why. Runs before compute, so no
    check runs on inputs that fail.

    - the sections exist;
    - the section families at each joint are a pair its table lists as
      allowed (joints.py, S5-9; before the tables, W7 and S4-12's stop on a
      section that is not round hollow);
    - each grade is one the tool supports for its member's shape (S5-5), and
      the electrode and the baseplate grade are ones it supports (W12);
    - the post is no wider than the rail (W8);
    - the post grade's Fu/Fy keeps its wall at the weld covered by Check 5 (W5);
    - the intermediate rail is no wider than the post (S4-11);
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

    D_rail, D_post = rail.OD, post.OD
    if D_post > D_rail:
        raise ProjectError(
            f"The post ({post.label}, OD {fmt_quantity_plain(D_post)}) is wider than the top rail "
            f"({rail.label}, OD {fmt_quantity_plain(D_rail)}). The coped post to rail underside detail "
            f"requires post OD <= rail OD. Check the inputs.", stop=Stop.SECTION_POST_WIDER_THAN_RAIL
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

    member = project.intermediate_member
    if member is not None:
        same = project.intermediate_rail.state == SAME_AS_TOP
        sec = rail if same else cast(Section, inter)
        if sec.OD > D_post:
            how = ("With same_as_top_rail = true it takes the top rail's section: uncheck same_as_top_rail and "
                   "enter a section no wider than the post." if same else
                   "Enter a section no wider than the post.")
            raise ProjectError(
                f"The intermediate rail ({sec.label}, OD {fmt_quantity_plain(sec.OD)}) is wider than the post "
                f"({post.label}, OD {fmt_quantity_plain(D_post)}). Its end is coped to the side of the post, "
                f"which requires intermediate rail OD <= post OD. {how}",
                stop=Stop.SECTION_INTERMEDIATE_WIDER_THAN_POST
            )

    for name, d, orientation in (("B", project.baseplate.B, "parallel to the rail"),
                                 ("N", project.baseplate.N, "perpendicular to the rail")):
        if d.value < D_post:
            raise ProjectError(
                f"[baseplate] {name} = {d.entered} ({orientation}) is smaller than the post OD "
                f"({post.label}, {fmt_quantity_plain(D_post)}). Check the inputs.",
                stop=Stop.BASEPLATE_SMALLER_THAN_POST
            )
