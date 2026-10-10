"""Running a calc: validate the inputs, then compute every check in order.

This module only sets the order. Each check's engineering is in its own
module, and none of them imports this one, so every import here is at the
top of the file.
"""

from __future__ import annotations

from handrail import shapes
from handrail.intermediate import check_4a
from handrail.loading import build_loading
from handrail.post import check_5, check_6
from handrail.project import SAME_AS_TOP, Project
from handrail.properties import section_lines
from handrail.rail import check_1, check_2
from handrail.reactions import reaction_sets
from handrail.registry import Registry
from handrail.results import Results
from handrail.validate import validate
from handrail.welds import check_3, check_4b, check_7


def compute(project: Project, registry: Registry) -> Results:
    """Every check, on inputs validate() has accepted.

    A separate entry point so a test can compute a case that validation
    refuses (docs/plans/slice-3.md, T1); the CLI always validates first.
    """
    rail = shapes.section(project.top_rail.section)
    post = shapes.section(project.post.section)
    member = project.intermediate_member
    same = project.intermediate_rail.state == SAME_AS_TOP
    inter = None if member is None else rail if same else shapes.section(member.section)
    loading = build_loading(project, registry, rail, post, inter)
    props = section_lines(registry, rail)
    post_props = section_lines(registry, post, with_r=True)
    inter_props = section_lines(registry, inter) if inter is not None and not same else []
    checks = [check_1(registry, project, rail, loading), check_2(registry, project, rail, loading),
              check_3(registry, project, rail, post, loading),
              check_4a(registry, project, inter, loading), check_4b(registry, project, post, inter, loading),
              check_5(registry, project, post, loading), check_6(registry, project, post, loading),
              check_7(registry, project, post, loading)]
    reactions = reaction_sets(registry, project, loading)
    return Results(project, rail, post, loading, props, post_props, checks, inter, inter_props, reactions)


def run(project: Project, registry: Registry) -> Results:
    """Validate, then compute: the order the CLI uses."""
    validate(project, registry)
    return compute(project, registry)
