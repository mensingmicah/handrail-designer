"""The section properties block of the calc: each member's properties as
calc lines, with where each value comes from.
"""

from __future__ import annotations

from handrail.calc import Line, Sheet
from handrail.registry import Registry
from handrail.shapes import Section


def section_lines(registry: Registry, sec: Section, with_r: bool = False) -> list[Line]:
    """Section properties as published. The post block adds r, which only
    the compression check uses; the rail block prints as it did in slice 1."""
    sh = Sheet(registry)
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
