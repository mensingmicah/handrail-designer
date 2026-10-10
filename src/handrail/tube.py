"""A custom round tube: a section computed from the dimensions entered
(docs/brief/inputs.md, "Custom round tube input", S5-8).

The engineer enters the outside diameter and the nominal wall. The design
wall follows by AISC 360-22 B4.2 from the grade, and every property is a
calc line computed from the outside diameter and the design wall; the
weight is computed on the nominal wall. Each formula is written once, here
(ADR 0002), and prints with its registry citation.

``properties`` holds the formulas alone, on a given outside diameter,
nominal wall and design wall, so the property-formula test can run them on
database rows and compare the results with AISC's published values
(docs/plans/slice-5.md, T3).
"""

from __future__ import annotations

from dataclasses import dataclass

from handrail.calc import PI, Sheet, Sym, sqrt
from handrail.dimensions import Dimension
from handrail.materials import NOMINAL_DESIGN_WALL
from handrail.registry import Registry
from handrail.shapes import CUSTOM, ROUND_TUBE, Axis, Section

WALL_AS_ENTERED = "ej.section.custom_wall_nominal"
DESIGN_WALL = "aisc360.B4.2.design_wall"
DESIGN_WALL_COEFF = "aisc360.B4.2.coeff"
NOMINAL_WALL = "aisc360.B4.2.nominal_wall"
DENSITY = "material.steel.density"
G = "geometry.round_tube."


@dataclass
class Properties:
    """A round tube's computed properties, each the symbol of its calc line."""

    A: Sym
    W: Sym
    I: Sym
    S: Sym
    Z: Sym
    r: Sym
    D_t: Sym


def label(OD: Dimension, wall: Dimension) -> str:
    """A custom round tube as the calc names it: "Round tube 2.375 × 0.055 (custom)"."""
    return f"Round tube {OD.value.m_as('inch'):g} × {wall.value.m_as('inch'):g} (custom)"


def properties(sh: Sheet, D: Sym, t_nom: Sym, t_des: Sym) -> Properties:
    """Properties of a hollow circle of outside diameter D: area, moment of
    inertia, section moduli, radius of gyration and D/t on the design wall,
    and the weight on the nominal wall (S5-8). In the order the section
    page prints a database section's values, each with the line it needs
    before it."""
    D_i = sh.line("D_i", "D_i", D - 2 * t_des, "Inside diameter, on the design wall",
                  cite_ids=(G + "inside_diameter",), unit="inch")
    A = sh.line("A", "A", PI / 4 * (D**2 - D_i**2), "Area (design wall)", cite_ids=(G + "A",), unit="inch**2")
    D_i_nom = sh.line("D_i_nom", 'D_"i,nom"', D - 2 * t_nom, "Inside diameter, on the nominal wall (for the weight)",
                      cite_ids=(G + "inside_diameter",), unit="inch")
    A_nom = sh.line("A_nom", 'A_"nom"', PI / 4 * (D**2 - D_i_nom**2), "Area on the nominal wall (for the weight)",
                    cite_ids=(G + "A",), unit="inch**2")
    rho = sh.code_value("rho", "rho", DENSITY, "Steel unit weight")
    W = sh.line("W", "W", rho * A_nom, "Weight per unit length: steel unit weight times the area on the nominal wall",
                cite_ids=(G + "weight",), unit="lbf/ft")
    I = sh.line("I", "I", PI / 64 * (D**4 - D_i**4), "Moment of inertia", cite_ids=(G + "I",), unit="inch**4")
    S = sh.line("S", "S", I / (D / 2), "Elastic section modulus", cite_ids=(G + "S",), unit="inch**3")
    Z = sh.line("Z", "Z", (D**3 - D_i**3) / 6, "Plastic section modulus", cite_ids=(G + "Z",), unit="inch**3")
    r = sh.line("r", "r", sqrt(I / A), "Radius of gyration", cite_ids=(G + "r",), unit="inch")
    D_t = sh.line("D_over_t", "D slash t", D / t_des, "Diameter-to-thickness ratio, computed (design wall)",
                  cite_ids=(G + "D_over_t",))
    return Properties(A=A, W=W, I=I, S=S, Z=Z, r=r, D_t=D_t)


def round_tube(registry: Registry, OD: Dimension, wall: Dimension, grade: str) -> Section:
    """The section of a custom round tube in this grade. The wall entered is
    the nominal wall (S5-8); the design wall is 0.93 of it, or the nominal
    wall itself for a grade AISC 360-22 B4.2 gives the nominal wall to
    (A1085, S5-6). The section keeps the lines that computed it, which the
    section properties page prints."""
    sh = Sheet(registry)
    name = label(OD, wall)
    D = sh.input("D", "D", OD.value, f"{name}: outside diameter ({OD.entered} as entered)")
    as_entered = registry.get(WALL_AS_ENTERED)
    t_nom = sh.input("t_nom", 't_"nom"', wall.value, f"Nominal wall thickness ({wall.entered} as entered)",
                     cite=f"Input; {as_entered.cite}")
    if grade in NOMINAL_DESIGN_WALL:
        t_des = sh.line("t_des", 't_"des"', t_nom, f"Design wall thickness: the nominal wall, {grade}",
                        cite_ids=(NOMINAL_WALL,), unit="inch")
    else:
        t_des = sh.line("t_des", 't_"des"', sh.coeff(DESIGN_WALL_COEFF) * t_nom, "Design wall thickness",
                        cite_ids=(DESIGN_WALL,), unit="inch")
    p = properties(sh, D, t_nom, t_des)
    axis = Axis(I=p.I.value, S=p.S.value, Z=p.Z.value, r=p.r.value)  # a round section: x = y (S5-1)
    return Section(label=name, family=ROUND_TUBE, source=CUSTOM, W=p.W.value, A=p.A.value, OD=D.value,
                   tnom=t_nom.value, tdes=t_des.value, D_t=p.D_t.value, x=axis, y=axis,
                   custom=True, computed=tuple(sh.lines))
