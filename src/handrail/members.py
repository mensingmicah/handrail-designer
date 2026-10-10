"""The members of a guard as the checks read them: each member's section,
and the project with every grade the file left out filled in.

Validation and the checks both start here, so a member is turned into a
section, and a blank grade into its shape's default, in one place. A
standard section is looked up in the shapes database; a custom round tube
is computed from the dimensions entered (tube.py). The grades are filled
in between the two: a default needs only the member's family, and a custom
tube's design wall needs its grade (AISC 360-22 B4.2).
"""

from __future__ import annotations

from dataclasses import dataclass

from handrail import shapes
from handrail.materials import with_default_grades
from handrail.project import SAME_AS_TOP, Member, Project
from handrail.registry import Registry
from handrail.shapes import ROUND_TUBE, Section
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


def resolve(project: Project, registry: Registry) -> Members:
    """Look up or compute every section and fill in the default grades.
    Raises ShapeNotFound for a designation the database does not have."""
    own_member = project.intermediate_rail.member  # its own section, or None
    rail, post, own = _standard(project.top_rail), _standard(project.post), _standard(own_member)
    project = with_default_grades(project, registry, _family(rail), _family(post),
                                  None if own_member is None else _family(own))
    own_member = project.intermediate_rail.member
    return Members(project, _section(registry, project.top_rail, rail), _section(registry, project.post, post),
                   None if own_member is None else _section(registry, own_member, own))
