"""Stand-in sections for the machinery tests.

A test reaches a branch no database section reaches by taking a real section
and changing one of its values: a D/t no pipe has, an outside diameter a
hundredth of an inch wider. Some of those values belong to the section and
some to its outline (shapes.Round, shapes.Rectangle); this puts each change
where it belongs, so a test names the value and not where it is stored.

Machinery only. Nothing built here is a test case value (CLAUDE.md rule 5).
"""

import dataclasses

from handrail.shapes import Section

OUTLINE_FIELDS = frozenset({"OD", "D_t", "H", "B", "b_t", "h_t", "J"})


def replace(sec: Section, **changes) -> Section:
    """The section with these values changed, outline values included."""
    outline = {k: v for k, v in changes.items() if k in OUTLINE_FIELDS}
    rest = {k: v for k, v in changes.items() if k not in OUTLINE_FIELDS}
    if outline:
        rest["outline"] = dataclasses.replace(sec.outline, **outline)
    return dataclasses.replace(sec, **rest)
