"""The section properties block of the calc: each member's properties as
calc lines, with where each value comes from.
"""

from __future__ import annotations

from handrail.calc import Line, Sheet
from handrail.registry import Registry
from handrail.shapes import DB, PipeSection


def section_lines(registry: Registry, sec: PipeSection, with_r: bool = False) -> list[Line]:
    """Section properties as published. The post block adds r, which only
    the compression check uses; the rail block prints as it did in slice 1."""
    sh = Sheet(registry)
    sh.given("D", "D", sec.OD, f"{sec.label}: outside diameter", DB)
    sh.given("t_nom", 't_"nom"', sec.tnom, "Nominal wall thickness", DB)
    sh.given("t_des", 't_"des"', sec.tdes, "Design wall thickness", DB)
    sh.given("A", "A", sec.A, "Area (design wall)", DB)
    sh.given("W", "W", sec.W, f"Nominal weight: tabulated {sec.W.m_as('lbf/ft'):g} lb/ft (nominal wall)", DB)
    sh.given("I", "I", sec.I, "Moment of inertia", DB)
    sh.given("S", "S", sec.S, "Elastic section modulus", DB)
    sh.given("Z", "Z", sec.Z, "Plastic section modulus", DB)
    if with_r:
        sh.given("r", "r", sec.r, "Radius of gyration", DB)
    sh.given("D_over_t", "D slash t", sec.D_t, "Diameter-to-thickness ratio, tabulated", DB)
    return sh.lines
