"""Which registry entry holds each material value the checks read, and
which grade a member takes when its grade is left out.

The values themselves are registry entries (CLAUDE.md rule 1); this module
only maps a grade, a shape and a wall thickness to the id of an entry. A
grade with no entries for a shape is one the tool does not support for it,
and validation stops on it (validate.py).

Fy and Fu are keyed by grade and shape (docs/brief/inputs.md, S5-5), and
by nominal wall thickness for ASTM A618 Gr Ia, Ib and II (S5-7). The
defaults by shape are the engineer's decisions in the brief, not registry
entries (inputs.md, "Inputs"); the standard grade lists they are tested
against are entries (AISC Manual Table 2-4).
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any

from handrail.calc import Sheet, Sym, fmt_quantity_plain
from handrail.errors import SectionStop
from handrail.project import OWN_SECTION, Member, Project
from handrail.registry import Registry
from handrail.shapes import PIPE, ROUND_HSS, ROUND_TUBE, Section
from handrail.stops import Stop


@dataclass(frozen=True)
class Grade:
    """The Fy and Fu entries of one grade for one shape. ``by_wall``: each
    entry holds a value per range of nominal wall thickness (S5-7)."""

    Fy: str
    Fu: str
    by_wall: bool = False


def _round_hss(name: str) -> Grade:
    return Grade(f"material.{name}.hss_round.Fy", f"material.{name}.hss_round.Fu")


def _a618(name: str) -> Grade:
    # Stored by wall range, not by shape: slice 6's rectangular A618 reads the same entries (S5-7).
    return Grade(f"material.{name}.Fy", f"material.{name}.Fu", by_wall=True)


# Every grade a round hollow section can take: the pipe grade and the round
# HSS grades of AISC Manual Table 2-4. One table for the three round hollow
# families: a grade outside the standard list for a database section's
# shape is an unusual pairing, allowed with a warning (S5-5), and a custom
# round tube takes every one of them.
_ROUND_HOLLOW: dict[str, Grade] = {
    "A53 Gr B": Grade("material.A53_GrB.Fy", "material.A53_GrB.Fu"),
    "A500 Gr B": _round_hss("A500_GrB"),
    "A500 Gr C": _round_hss("A500_GrC"),
    "A501 Gr A": _round_hss("A501_GrA"),
    "A501 Gr B": _round_hss("A501_GrB"),
    "A618 Gr Ia": _a618("A618_GrIa"),
    "A618 Gr Ib": _a618("A618_GrIb"),
    "A618 Gr II": _a618("A618_GrII"),
    "A618 Gr III": Grade("material.A618_GrIII.Fy", "material.A618_GrIII.Fu"),
    "A847": _round_hss("A847"),
    "A1085 Gr A": _round_hss("A1085_GrA"),
}
# Grades by section family. A family with no table is one the tool has no
# grades for yet (the per-joint tables stop it first, joints.py).
GRADES: dict[str, dict[str, Grade]] = {PIPE: _ROUND_HOLLOW, ROUND_HSS: _ROUND_HOLLOW, ROUND_TUBE: _ROUND_HOLLOW}

# Grades whose design wall is the nominal wall under AISC 360-22 B4.2 (S5-6).
# A database section in one still runs on its published properties, with a
# printed note (properties.grade_notes).
NOMINAL_DESIGN_WALL = ("A1085 Gr A",)

# The grade a member takes when the project file leaves it out (S5-5).
DEFAULT_GRADE = {PIPE: "A53 Gr B", ROUND_HSS: "A500 Gr B", ROUND_TUBE: "A500 Gr B"}
# The entry listing the standard grades of each database shape (Table 2-4).
STANDARD_GRADES = {PIPE: "material.grades.pipe", ROUND_HSS: "material.grades.hss_round"}

# The two ranges of a by-wall-range entry, and the entries holding their limits.
THIN, THICK = "up_to_thin_limit", "up_to_thick_limit"
THIN_LIMIT, THICK_LIMIT = "material.A618.wall.thin_limit", "material.A618.wall.thick_limit"

# Fu entry for each baseplate grade accepted: A36 only, for all of v1 (W12).
BASEPLATE_FU = {"A36": "material.A36.Fu"}
BASEPLATE_GRADES = tuple(BASEPLATE_FU)
# F_EXX entry for each electrode accepted: E70XX only (W12).
FEXX_ENTRY = {"E70XX": "material.E70XX.FEXX"}


@dataclass(frozen=True)
class Stress:
    """Fy or Fu as a check reads it: the registry entry, which wall range of
    a by-wall-range entry ("" for a plain one), and the printed note."""

    entry: str
    note: str
    range: str = ""

    def line(self, sh: Sheet, key: str, typst: str) -> Sym:
        """The value as its own calc line, cited to its entry."""
        return sh.code_value(key, typst, self.entry, self.note, select=self.range)

    def quantity(self, registry: Registry) -> Any:
        entry = registry.get(self.entry)
        return entry.in_range(self.range) if self.range else entry.quantity


def supported(family: str) -> list[str]:
    """The grades the tool has Fy and Fu entries for, for a section of this family."""
    return list(GRADES.get(family, {}))


def _wall_range(registry: Registry, grade: str, sec: Section, member: str) -> tuple[str, str]:
    """Which range of a by-wall-range grade the section's nominal wall falls
    in, and the words the note adds (S5-7). A wall of exactly the thin limit
    takes the thin range. Stops above the thick limit, where AISC Manual
    Table 2-4 gives no value."""
    thin, thick = registry.get(THIN_LIMIT), registry.get(THICK_LIMIT)
    t = sec.tnom
    if t <= thin.quantity:
        return THIN, f", wall up to {fmt_quantity_plain(thin.quantity)}"
    if t <= thick.quantity:
        return THICK, f", wall over {fmt_quantity_plain(thin.quantity)} to {fmt_quantity_plain(thick.quantity)}"
    raise SectionStop(
        f"{member or 'Section'} {sec.label}, {grade}: nominal wall {fmt_quantity_plain(t)} is over "
        f"{fmt_quantity_plain(thick.quantity)}, the thickest wall {thick.cite} gives Fy and Fu for in this grade. "
        f"The tool does not check this section in this grade.",
        stop=Stop.GRADE_WALL_OVER_LIMIT
    )


def _stress(registry: Registry, grade: str, sec: Section, which: str, what: str, member: str) -> Stress:
    grades = GRADES.get(sec.family, {})
    if grade not in grades:
        raise SectionStop(unsupported_message(member or sec.label, grade, sec.family), stop=Stop.GRADE_UNSUPPORTED)
    g = grades[grade]
    entry = g.Fy if which == "Fy" else g.Fu
    if not g.by_wall:
        return Stress(entry, f"{what}, {grade}")
    wall, words = _wall_range(registry, grade, sec, member)
    return Stress(entry, f"{what}, {grade}{words}", wall)


def yield_stress(registry: Registry, grade: str, sec: Section, member: str = "") -> Stress:
    """Fy of this grade for this section. ``member`` names the member in a stop's message."""
    return _stress(registry, grade, sec, "Fy", "Yield stress", member)


def tensile_strength(registry: Registry, grade: str, sec: Section, member: str = "") -> Stress:
    """Fu of this grade for this section."""
    return _stress(registry, grade, sec, "Fu", "Tensile strength", member)


def baseplate_tensile_strength(grade: str) -> Stress:
    return Stress(BASEPLATE_FU[grade], f"Tensile strength, baseplate {grade}")


def unsupported_message(member: str, grade: str, family: str) -> str:
    """The grade and the grades supported for the member's shape."""
    grades = supported(family)
    if not grades:
        return f"{member} grade {grade!r}: this version has no grades for a section of the family {family}"
    return f"{member} grade {grade!r}: for {family} this version supports {', '.join(grades)} only"


def default_grade(registry: Registry, family: str, top_rail_grade: str | None = None) -> str:
    """The grade a member of this family takes when its grade is left out:
    its shape's default (S5-5). An intermediate rail of its own section is
    given the top rail's grade, and takes it when that grade is on the
    standard list for its own shape, or is any grade a custom round tube
    accepts, for a custom round tube (S5-10, refining S4-1)."""
    if top_rail_grade is not None:
        if family in STANDARD_GRADES:
            standard = registry.get(STANDARD_GRADES[family]).value
        else:
            standard = supported(family)
        if top_rail_grade in standard:
            return top_rail_grade
    return DEFAULT_GRADE.get(family, "")


def _with_default(registry: Registry, member: Member, family: str, top_rail_grade: str | None = None) -> Member:
    if member.grade or not member.grade_defaulted:
        return member  # entered, or already filled in
    return dataclasses.replace(member, grade=default_grade(registry, family, top_rail_grade))


def with_default_grades(project: Project, registry: Registry, rail: Section, post: Section,
                        inter: Section | None) -> Project:
    """The project with every grade the file left out filled in (S5-5,
    S5-10). ``inter`` is the intermediate rail's own section, or None. A
    family with no default keeps its blank grade, which no shape supports."""
    top = _with_default(registry, project.top_rail, rail.family)
    intermediate = project.intermediate_rail
    own = intermediate.member
    if intermediate.state == OWN_SECTION and own is not None and inter is not None:
        intermediate = dataclasses.replace(intermediate, member=_with_default(registry, own, inter.family, top.grade))
    return dataclasses.replace(project, top_rail=top, post=_with_default(registry, project.post, post.family),
                               intermediate_rail=intermediate)
