"""Running a calc: validate the inputs, then compute every check in order.

This module only sets the order. Each check's engineering is in its own
module, and none of them imports this one, so every import here is at the
top of the file.
"""

from __future__ import annotations

from handrail import members
from handrail.intermediate import check_4a
from handrail.loading import build_loading
from handrail.post import check_5, check_6
from handrail.project import SAME_AS_TOP, Project
from handrail.properties import grade_notes, section_lines
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
    m = members.resolve(project, registry)
    project, rail, post, inter = m.project, m.rail, m.post, m.inter
    same = project.intermediate_rail.state == SAME_AS_TOP
    loading = build_loading(project, registry, rail, post, inter)
    props = section_lines(registry, rail)
    post_props = section_lines(registry, post, with_r=True)
    own = inter is not None and not same  # the intermediate rail has its own section
    inter_props = section_lines(registry, inter) if inter is not None and own else []
    rail_notes = grade_notes(registry, rail, project.top_rail.grade)
    post_notes = grade_notes(registry, post, project.post.grade)
    inter_member = project.intermediate_member
    inter_notes = (grade_notes(registry, inter, inter_member.grade)
                   if inter is not None and inter_member is not None and own else [])
    checks = [check_1(registry, project, rail, loading), check_2(registry, project, rail, loading),
              check_3(registry, project, rail, post, loading),
              check_4a(registry, project, inter, loading), check_4b(registry, project, post, inter, loading),
              check_5(registry, project, post, loading), check_6(registry, project, post, loading),
              check_7(registry, project, post, loading)]
    reactions = reaction_sets(registry, project, loading)
    return Results(project, rail, post, loading, props, post_props, checks, inter, inter_props, reactions,
                   rail_notes=rail_notes, post_notes=post_notes, inter_notes=inter_notes)


def run(project: Project, registry: Registry) -> Results:
    """Validate, then compute: the order the CLI uses."""
    validate(project, registry)
    return compute(project, registry)
