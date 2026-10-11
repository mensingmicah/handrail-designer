"""The members of a guard as the checks read them: each member's section,
and the project with every grade the file left out filled in.

Validation and the checks both start here, so a member is turned into a
section, and a blank grade into its shape's default, in one place. A
standard section is looked up in the shapes database; a custom round tube
is computed from the dimensions entered (tube.py). The grades are filled
in between the two: a default needs only the member's family, and a custom
tube's design wall needs its grade (AISC 360-22 B4.2).

A rectangular member's orientation is tested here too (S6-2), since only
here is it known whether a section is round, square or neither. It is
tested on every path to the checks, with validation or without.
"""

from __future__ import annotations

from dataclasses import dataclass

from handrail import shapes
from handrail.materials import with_default_grades
from handrail.project import POST_LONG_SIDE, RAIL_LONG_SIDE, SAME_AS_TOP, Member, Project, ProjectError
from handrail.registry import Registry
from handrail.shapes import ROUND_TUBE, Section
from handrail.stops import Stop
from handrail.tube import round_tube


@dataclass(frozen=True)
class Members:
    project: Project      # every grade filled in (S5-5, S5-10)
    rail: Section
    post: Section
    own: Section | None   # the intermediate rail's own section; None when it has none

    @property
    def inter(self) -> Section | None:
        """The intermediate rail's section: its own, the top rail's when it
        is the same, or None when there is no intermediate rail."""
        if self.project.intermediate_member is None:
            return None
        return self.rail if self.project.intermediate_rail.state == SAME_AS_TOP else self.own


def _standard(member: Member | None) -> Section | None:
    """The member's database section, or None for a custom tube or no member."""
    return None if member is None or member.custom else shapes.section(member.section)


def _section(registry: Registry, member: Member, standard: Section | None) -> Section:
    """The member's section: the one looked up, or the custom tube computed in its grade."""
    if standard is not None:
        return standard
    if member.OD is None or member.wall_nominal is None:
        raise ValueError(f"member {member!r} has neither a section nor a custom tube's dimensions")  # a bug: the reader requires one
    return round_tube(registry, member.OD, member.wall_nominal, member.grade)


def _family(standard: Section | None) -> str:
    return ROUND_TUBE if standard is None else standard.family


def _require_long_side(member: Member, sec: Section, table: str, words: tuple[str, str]) -> None:
    """A rectangular member that is not square needs its orientation, and
    nothing else may have one (S6-2). A forgotten orientation stops: the
    tool never picks one. One given for a round or a square member stops as
    a conflicting input."""
    given = member.long_side
    if sec.is_round or sec.rect.square:
        if given:
            what = "round" if sec.is_round else "square"
            raise ProjectError(
                f"[{table}] long_side = {given!r} is given, but {sec.label} is a {what} section and has no long "
                f"side. Remove long_side, or check the section.", stop=Stop.MEMBER_LONG_SIDE_NOT_APPLICABLE)
        return
    if not given:
        raise ProjectError(
            f"[{table}] is missing 'long_side': {sec.label} is not square, and the tool never assumes which way "
            f'round a member is built. Give long_side = "{words[0]}" or "{words[1]}".',
            stop=Stop.MEMBER_LONG_SIDE_MISSING)


def resolve(project: Project, registry: Registry) -> Members:
    """Look up or compute every section, fill in the default grades and
    test each member's orientation. Raises ShapeNotFound for a designation
    the database does not have."""
    own_member = project.intermediate_rail.member  # its own section, or None
    rail, post, own = _standard(project.top_rail), _standard(project.post), _standard(own_member)
    project = with_default_grades(project, registry, _family(rail), _family(post),
                                  None if own_member is None else _family(own))
    own_member = project.intermediate_rail.member
    m = Members(project, _section(registry, project.top_rail, rail), _section(registry, project.post, post),
                None if own_member is None else _section(registry, own_member, own))
    _require_long_side(project.top_rail, m.rail, "top_rail", RAIL_LONG_SIDE)
    _require_long_side(project.post, m.post, "post", POST_LONG_SIDE)
    if own_member is not None and m.own is not None:
        _require_long_side(own_member, m.own, "intermediate_rail", RAIL_LONG_SIDE)
    return m
