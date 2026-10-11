"""The section properties block of the calc: each member's properties as
calc lines, with where each value comes from.
"""

from __future__ import annotations

from handrail import materials
from handrail.calc import Line, Sheet, mtext
from handrail.project import HORIZONTAL, PARALLEL, PERPENDICULAR, VERTICAL
from handrail.registry import Registry
from handrail.shapes import PIPE, RECT_HSS, ROUND_HSS, Section

# A database shape as the unusual-pairing warning names it.
SHAPE_NAME = {PIPE: "pipe", ROUND_HSS: "round HSS", RECT_HSS: "rectangular HSS"}
UNUSUAL_PAIRING = "ej.grade.unusual_pairing"
A1085_NOTE = "ej.grade.A1085_database_note"


def grade_notes(registry: Registry, sec: Section, grade: str) -> list[str]:
    """What the section page prints under a member about its grade. Both
    are for a database section only; a custom tube takes every grade it
    accepts as usual, and its A1085 wall is the nominal wall.

    - An unusual pairing (S5-5): a grade outside the standard list for the
      section's shape, AISC Manual Table 2-4. Allowed, with this warning.
    - A1085 (S5-6): AISC 360-22 B4.2 permits the nominal wall, and the
      database's properties are on 0.93 of it. The note says so, and how to
      get the credit.
    """
    if sec.family not in materials.STANDARD_GRADES:
        return []
    notes = []
    if grade not in registry.get(materials.STANDARD_GRADES[sec.family]).value:
        warning = registry.get(UNUSUAL_PAIRING)
        notes.append("UNUSUAL PAIRING: " + warning.value.format(grade=grade, shape=SHAPE_NAME[sec.family]))
    if grade in materials.NOMINAL_DESIGN_WALL:
        notes.append(registry.get(A1085_NOTE).value)
    return notes


# The sentence printed under a rectangular member for each orientation (S6-2).
ORIENTATION = {
    VERTICAL: "ej.section.orientation.rail_vertical",
    HORIZONTAL: "ej.section.orientation.rail_horizontal",
    PERPENDICULAR: "ej.section.orientation.post_perpendicular",
    PARALLEL: "ej.section.orientation.post_parallel",
}
SQUARE = "ej.section.orientation.square"


def _orientation(sh: Sheet, sec: Section, long_side: str) -> None:
    """Which axis each load bends, derived from the orientation entered and
    printed, never entered (S6-2)."""
    if sec.rect.square:
        entry, statement = sh.registry.get(SQUARE), "Square section"
    else:
        entry, statement = sh.registry.get(ORIENTATION[long_side]), f"long_side = {long_side}"
    sh.decision(mtext(statement), entry.value, "Orientation, and the axis each load bends", cite_ids=(entry.id,))


def _rect_lines(sh: Sheet, sec: Section) -> None:
    """A rectangular or square HSS as published: both outside dimensions,
    both axes, the torsional constant and both wall ratios."""
    r = sec.rect
    sh.given("H", "H", r.H, f"{sec.label}: outside dimension of the longer side", sec.source)
    sh.given("B", "B", r.B, "Outside dimension of the shorter side", sec.source)
    sh.given("t_nom", 't_"nom"', sec.tnom, "Nominal wall thickness", sec.source)
    sh.given("t_des", 't_"des"', sec.tdes, "Design wall thickness", sec.source)
    sh.given("A", "A", sec.A, "Area (design wall)", sec.source)
    sh.given("W", "W", sec.W, f"Nominal weight: tabulated {sec.W.m_as('lbf/ft'):g} lb/ft (nominal wall)", sec.source)
    for name, ax, which in (("x", sec.x, "strong"), ("y", sec.y, "weak")):
        about = f"about the {name} axis" + ("" if r.square else f", the {which} axis")
        sh.given(f"I_{name}", f"I_{name}", ax.I, f"Moment of inertia {about}", sec.source)
        sh.given(f"S_{name}", f"S_{name}", ax.S, f"Elastic section modulus {about}", sec.source)
        sh.given(f"Z_{name}", f"Z_{name}", ax.Z, f"Plastic section modulus {about}", sec.source)
        sh.given(f"r_{name}", f"r_{name}", ax.r, f"Radius of gyration {about}", sec.source)
    sh.given("J", "J", r.J, "Torsional constant", sec.source)
    sh.given("b_over_t", "b slash t", r.b_t, "Width-to-thickness ratio of the shorter walls, tabulated", sec.source)
    sh.given("h_over_t", "h slash t", r.h_t, "Width-to-thickness ratio of the longer walls, tabulated", sec.source)


def section_lines(registry: Registry, sec: Section, with_r: bool = False, long_side: str = "") -> list[Line]:
    """Section properties: as published for a database section, and for a
    custom section the lines that computed them from the dimensions entered
    (tube.py). The post block adds r, which only the compression check
    uses; the rail block prints as it did in slice 1. A rectangular section
    prints both axes, and under them which axis each load bends
    (``long_side`` is the member's orientation, blank for a square)."""
    if sec.is_round and sec.custom:
        return [ln for ln in sec.computed if with_r or ln.key != "r"]
    sh = Sheet(registry)
    if not sec.is_round:
        if sec.custom:
            sh.lines.extend(sec.computed)
        else:
            _rect_lines(sh, sec)
        _orientation(sh, sec, long_side)
        return sh.lines
    sh.given("D", "D", sec.OD, f"{sec.label}: outside diameter", sec.source)
    sh.given("t_nom", 't_"nom"', sec.tnom, "Nominal wall thickness", sec.source)
    sh.given("t_des", 't_"des"', sec.tdes, "Design wall thickness", sec.source)
    sh.given("A", "A", sec.A, "Area (design wall)", sec.source)
    sh.given("W", "W", sec.W, f"Nominal weight: tabulated {sec.W.m_as('lbf/ft'):g} lb/ft (nominal wall)", sec.source)
    sh.given("I", "I", sec.I, "Moment of inertia", sec.source)
    sh.given("S", "S", sec.S, "Elastic section modulus", sec.source)
    sh.given("Z", "Z", sec.Z, "Plastic section modulus", sec.source)
    if with_r:
        sh.given("r", "r", sec.r, "Radius of gyration", sec.source)
    sh.given("D_over_t", "D slash t", sec.D_t, "Diameter-to-thickness ratio, tabulated", sec.source)
    return sh.lines
