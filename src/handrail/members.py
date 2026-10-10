"""The members of a guard as the checks read them: each member's section,
and the project with every grade the file left out filled in.

Validation and the checks both start here, so a member is turned into a
section, and a blank grade into its shape's default, in one place.
"""

from __future__ import annotations

from dataclasses import dataclass

from handrail import shapes
from handrail.materials import with_default_grades
from handrail.project import SAME_AS_TOP, Project
from handrail.registry import Registry
from handrail.shapes import Section


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


def resolve(project: Project, registry: Registry) -> Members:
    """Look up every section and fill in the default grades. Raises
    ShapeNotFound for a designation the database does not have."""
    rail = shapes.section(project.top_rail.section)
    post = shapes.section(project.post.section)
    own = project.intermediate_rail.member  # its own section, or None
    inter = shapes.section(own.section) if own else None
    return Members(with_default_grades(project, registry, rail, post, inter), rail, post, inter)
