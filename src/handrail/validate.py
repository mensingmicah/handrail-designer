"""Input validation: the checks on the inputs that need more than one
field, or a lookup. It runs before anything is computed (engine.run).
"""

from __future__ import annotations

from handrail import shapes
from handrail.calc import fmt_quantity_plain, fmt_sig
from handrail.materials import BASEPLATE_GRADES, FEXX_ENTRY, FU_ENTRY, FY_ENTRY
from handrail.project import SAME_AS_TOP, Member, Project, ProjectError
from handrail.registry import Registry


def require_supported_grade(member: Member, name: str) -> None:
    """Refuse a grade this slice has no Fy or no Fu entry for. Both are
    needed: Fy for the member checks, Fu for the fusion face of a weld
    (Check 3's rail side, Check 4b's post and intermediate rail walls) and
    the post wall's Fu/Fy guard.

    The brief's unusual-pairing warning (a grade outside the shape's standard
    list) returns when a slice accepts more than one grade; with A53 Gr B the
    only grade allowed, it could never fire.
    """
    if member.grade not in FY_ENTRY or member.grade not in FU_ENTRY:
        supported = [g for g in FY_ENTRY if g in FU_ENTRY]
        raise ProjectError(
            f"{name} grade {member.grade!r}: this version supports {', '.join(supported)} only"
        )


def validate(project: Project, registry: Registry) -> None:
    """The input checks that need more than one field, or a lookup. Raises an
    InputError naming what it checked and why. Runs before compute, so no
    check runs on inputs that fail.

    - the sections exist, and each grade and the electrode is one this
      version supports (W12);
    - the rail, the post and the intermediate rail are round hollow sections
      (W7, extended to the intermediate rail by S4-12);
    - the post is no wider than the rail (W8);
    - the post grade's Fu/Fy keeps its wall at the weld covered by Check 5 (W5);
    - the intermediate rail is no wider than the post (S4-11);
    - the baseplate is no smaller in plan than the post OD (S4-6).
    """
    rail = shapes.pipe(project.top_rail.section)
    post = shapes.pipe(project.post.section)
    require_supported_grade(project.top_rail, "top rail")
    require_supported_grade(project.post, "post")
    own = project.intermediate_rail.member  # its own section, or None
    inter = shapes.pipe(own.section) if own else None
    if own:
        require_supported_grade(own, "intermediate rail")
    electrode = project.welds.electrode
    if electrode not in FEXX_ENTRY:
        raise ProjectError(f"[welds] electrode {electrode!r}: this version supports {', '.join(FEXX_ENTRY)} only")
    if project.baseplate.grade not in BASEPLATE_GRADES:
        raise ProjectError(f"[baseplate] grade {project.baseplate.grade!r}: this version supports "
                           f"{', '.join(BASEPLATE_GRADES)} only")

    members = [("top rail", rail), ("post", post)] + ([("intermediate rail", inter)] if inter else [])
    for member, sec in members:
        if sec.family not in shapes.ROUND_HOLLOW:
            raise ProjectError(
                f"{member} {sec.label} ({sec.family}) is not a round hollow section. The stated assumption "
                f"that the rail wall's local strength at the post is not checked has been decided only for "
                f"a round hollow rail on a round hollow post, not for this section."
            )

    D_rail, D_post = rail.OD, post.OD
    if D_post > D_rail:
        raise ProjectError(
            f"The post ({post.label}, OD {fmt_quantity_plain(D_post)}) is wider than the top rail "
            f"({rail.label}, OD {fmt_quantity_plain(D_rail)}). The coped post to rail underside detail "
            f"requires post OD <= rail OD. Check the inputs."
        )

    grade = project.post.grade
    Fy, Fu = registry.get(FY_ENTRY[grade]).quantity, registry.get(FU_ENTRY[grade]).quantity
    limit = registry.get("ej.weld.post_wall.fu_fy_min")
    ratio = Fu / Fy
    if ratio < limit.value:
        raise ProjectError(
            f"post grade {grade}: Fu/Fy = {fmt_sig(ratio.m_as('dimensionless'))} is below {limit.value} ({limit.cite}). "
            f"The post wall at the weld is covered by Check 5 only while yielding governs over rupture; "
            f"the tool does not check this grade's post wall at the weld."
        )

    member = project.intermediate_member
    if member is not None:
        same = project.intermediate_rail.state == SAME_AS_TOP
        sec = rail if same else inter
        if sec.OD > D_post:
            how = ("With same_as_top_rail = true it takes the top rail's section: uncheck same_as_top_rail and "
                   "enter a section no wider than the post." if same else
                   "Enter a section no wider than the post.")
            raise ProjectError(
                f"The intermediate rail ({sec.label}, OD {fmt_quantity_plain(sec.OD)}) is wider than the post "
                f"({post.label}, OD {fmt_quantity_plain(D_post)}). Its end is coped to the side of the post, "
                f"which requires intermediate rail OD <= post OD. {how}"
            )

    for name, d, orientation in (("B", project.baseplate.B, "parallel to the rail"),
                                 ("N", project.baseplate.N, "perpendicular to the rail")):
        if d.value < D_post:
            raise ProjectError(
                f"[baseplate] {name} = {d.entered} ({orientation}) is smaller than the post OD "
                f"({post.label}, {fmt_quantity_plain(D_post)}). Check the inputs."
            )
