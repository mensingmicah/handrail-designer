"""A custom rectangular tube: a section computed from the dimensions entered
(docs/brief/checks.md, S6-3 and S6-4; S6-14 item 6).

The engineer enters the two outside dimensions, H the longer and B the
shorter, and the nominal wall. There is no corner radius input. The design
wall follows by AISC 360-22 B4.2 from the grade, as for a round tube, and
every property is a calc line:

- A, and I, S, Z and r about both axes: exact geometry on a rounded
  rectangle, outside corner radius twice the design wall and inside radius
  the design wall, the radii the Shapes Database's own properties are built
  on. Each outline (outside and inside) is the rectangle less its four
  corners, a corner being a square of the radius less its quarter circle.
- J from the wall's midline, corner radius 1.5 times the design wall
  (Commentary to AISC 360-22 H3).
- b/t and h/t on the outside dimension less three times the design wall
  (AISC 360-22 B4.1b(d)), the rule for a corner radius that is not known.
  It implies a different radius from the properties' on purpose, as the
  database's own two columns do.
- The weight on the nominal wall, with the outside radius at twice it.

Each formula is written once, here (ADR 0002), and prints with its registry
citation. ``properties`` holds the formulas alone, on given dimensions and
walls, so the property-formula test can run them on database rows and
compare the results with AISC's published values (docs/plans/slice-6.md,
T4).
"""

from __future__ import annotations

from dataclasses import dataclass

from handrail.calc import PI, Expr, Sheet, Sym, compare, fmt_quantity_plain, sqrt, term
from handrail.dimensions import Dimension
from handrail.project import ProjectError
from handrail.registry import Registry
from handrail.shapes import CUSTOM, RECT_TUBE, Axis, Rectangle, Section
from handrail.stops import Stop
from handrail.tube import DENSITY, walls

G = "geometry.rect_tube."
RADIUS = "ej.section.rect_tube.corner_radius"
RADIUS_COEFF = RADIUS + ".outside_coeff"
NO_FLAT = "ej.section.rect_tube.no_flat"
WIDTH, WIDTH_COEFF = "aisc360.B4.1b.d.width", "aisc360.B4.1b.d.coeff"
MIDLINE_AREA, MIDLINE_COEFF = "aisc360.CH3.midline_area", "aisc360.CH3.midline_radius_coeff"
J_FORMULA = "ej.section.rect_tube.J"


@dataclass
class Properties:
    """A rectangular tube's computed properties, each the symbol of its calc line."""

    A: Sym
    W: Sym
    Ix: Sym
    Sx: Sym
    Zx: Sym
    rx: Sym
    Iy: Sym
    Sy: Sym
    Zy: Sym
    ry: Sym
    J: Sym
    b_t: Sym
    h_t: Sym


def label(H: Dimension, B: Dimension, wall: Dimension) -> str:
    """A custom rectangular tube as the calc names it: "Rect. tube 2 × 1 × 0.083 (custom)"."""
    return (f"Rect. tube {H.value.m_as('inch'):g} × {B.value.m_as('inch'):g} × "
            f"{wall.value.m_as('inch'):g} (custom)")


def _area(b: Expr, h: Expr, R: Expr) -> Expr:
    """Area of a b by h rectangle with corners of radius R."""
    return b * h - (4 - PI) * R**2


def _about(sh: Sheet, axis: str, tag: str, which: str, b: Expr, h: Expr, R: Expr) -> tuple[Sym, Sym]:
    """I and Z of one outline (``tag`` "o" outside, "i" inside) about the
    axis parallel to its side b, h being its dimension in the direction of
    bending. Each corner takes away a square of the radius and gives back
    its quarter circle, each at its own distance from the axis."""
    sub = f"{axis}{tag}"
    c_sq = sh.line(f"c_sq_{sub}", f'c_("sq,{sub}")', h / 2 - R / 2,
                   f"{which} outline, {axis} axis: distance to the centroid of a corner square",
                   cite_ids=(G + "corner_centroids",), unit="inch")
    c_qc = sh.line(f"c_qc_{sub}", f'c_("qc,{sub}")', h / 2 - R + 4 * R / (3 * PI),
                   f"{which} outline, {axis} axis: distance to the centroid of a corner's quarter circle",
                   cite_ids=(G + "corner_centroids",), unit="inch")
    quarter = PI * R**2 / 4
    I = sh.line(f"I_{sub}", f'I_"{sub}"',
                b * h**3 / 12 - 4 * ((R**4 / 12 + R**2 * c_sq**2) - ((PI / 16 - 4 / (9 * PI)) * R**4 + quarter * c_qc**2)),
                f"{which} outline: moment of inertia about the {axis} axis", cite_ids=(G + "I",), unit="inch**4")
    Z = sh.line(f"Z_{sub}", f'Z_"{sub}"', b * h**2 / 4 - 4 * (R**2 * c_sq - quarter * c_qc),
                f"{which} outline: plastic section modulus about the {axis} axis", cite_ids=(G + "Z",), unit="inch**3")
    return I, Z


def properties(sh: Sheet, H: Sym, B: Sym, t_nom: Sym, t_des: Sym) -> Properties:
    """Properties of a rectangular tube H by B: area, and I, S, Z and r about
    both axes, on the design wall; J on the wall's midline; the two wall
    ratios; and the weight on the nominal wall (S6-3, S6-4). In the order
    the section page prints a database section's values, each with the
    lines it needs before it."""
    k = sh.coeff(RADIUS_COEFF)
    R_o = sh.line("R_o", "R_o", k * t_des, "Outside corner radius", cite_ids=(RADIUS,), unit="inch")
    R_i = sh.line("R_i", "R_i", t_des, "Inside corner radius: the design wall", cite_ids=(RADIUS,), unit="inch")
    H_i = sh.line("H_i", "H_i", H - 2 * t_des, "Inside dimension of the longer side",
                  cite_ids=(G + "inside_dimensions",), unit="inch")
    B_i = sh.line("B_i", "B_i", B - 2 * t_des, "Inside dimension of the shorter side",
                  cite_ids=(G + "inside_dimensions",), unit="inch")
    A_o = sh.line("A_o", "A_o", _area(B, H, R_o), "Area within the outside outline", cite_ids=(G + "A",),
                  unit="inch**2")
    A_i = sh.line("A_i", "A_i", _area(B_i, H_i, R_i), "Area within the inside outline", cite_ids=(G + "A",),
                  unit="inch**2")
    A = sh.line("A", "A", A_o - A_i, "Area (design wall)", cite_ids=(G + "A",), unit="inch**2")

    R_on = sh.line("R_o_nom", 'R_"o,nom"', k * t_nom, "Outside corner radius on the nominal wall (for the weight)",
                   cite_ids=(G + "weight",), unit="inch")
    A_nom = sh.line("A_nom", 'A_"nom"', _area(B, H, R_on) - _area(B - 2 * t_nom, H - 2 * t_nom, t_nom),
                    "Area on the nominal wall (for the weight)", cite_ids=(G + "A",), unit="inch**2")
    rho = sh.code_value("rho", "rho", DENSITY, "Steel unit weight")
    W = sh.line("W", "W", rho * A_nom, "Weight per unit length: steel unit weight times the area on the nominal wall",
                cite_ids=(G + "weight",), unit="lbf/ft")

    def axis(name: str, which: str, b_o: Sym, h_o: Sym, b_i: Sym, h_i: Sym) -> tuple[Sym, Sym, Sym, Sym]:
        about = f"about the {name} axis" + ("" if H.value == B.value else f", the {which} axis")
        I_o, Z_o = _about(sh, name, "o", "Outside", b_o, h_o, R_o)
        I_i, Z_i = _about(sh, name, "i", "Inside", b_i, h_i, R_i)
        I = sh.line(f"I_{name}", f"I_{name}", I_o - I_i, f"Moment of inertia {about}", cite_ids=(G + "I",),
                    unit="inch**4")
        S = sh.line(f"S_{name}", f"S_{name}", I / (h_o / 2), f"Elastic section modulus {about}",
                    cite_ids=(G + "S",), unit="inch**3")
        Z = sh.line(f"Z_{name}", f"Z_{name}", Z_o - Z_i, f"Plastic section modulus {about}", cite_ids=(G + "Z",),
                    unit="inch**3")
        r = sh.line(f"r_{name}", f"r_{name}", sqrt(I / A), f"Radius of gyration {about}", cite_ids=(G + "r",),
                    unit="inch")
        return I, S, Z, r

    Ix, Sx, Zx, rx = axis("x", "strong", B, H, B_i, H_i)
    Iy, Sy, Zy, ry = axis("y", "weak", H, B, H_i, B_i)

    R_m = sh.line("R_m", "R_m", sh.coeff(MIDLINE_COEFF) * t_des, "Corner radius of the wall's midline", unit="inch")
    A_m = sh.line("A_m", "A_m", (H - t_des) * (B - t_des) - (4 - PI) * R_m**2, "Area enclosed by the wall's midline",
                  cite_ids=(MIDLINE_AREA,), unit="inch**2")
    p_m = sh.line("p_m", "p_m", 2 * ((H - t_des) + (B - t_des)) - 2 * (4 - PI) * R_m, "Perimeter of the wall's midline",
                  cite_ids=(G + "midline_perimeter",), unit="inch")
    J = sh.line("J", "J", 4 * A_m**2 * t_des / p_m, "Torsional constant", cite_ids=(J_FORMULA,), unit="inch**4")

    c = sh.coeff(WIDTH_COEFF)
    b_t = sh.line("b_over_t", "b slash t", (B - c * t_des) / t_des,
                  "Width-to-thickness ratio of the shorter walls, computed (design wall)", cite_ids=(WIDTH,))
    h_t = sh.line("h_over_t", "h slash t", (H - c * t_des) / t_des,
                  "Width-to-thickness ratio of the longer walls, computed (design wall)", cite_ids=(WIDTH,))
    return Properties(A=A, W=W, Ix=Ix, Sx=Sx, Zx=Zx, rx=rx, Iy=Iy, Sy=Sy, Zy=Zy, ry=ry, J=J, b_t=b_t, h_t=h_t)


def rect_tube(registry: Registry, H: Dimension, B: Dimension, wall: Dimension, grade: str) -> Section:
    """The section of a custom rectangular tube in this grade. The wall
    entered is the nominal wall (S5-8); the design wall is 0.93 of it, or
    the nominal wall itself for a grade AISC 360-22 B4.2 gives the nominal
    wall to (A1085, S5-6). A wall that leaves no flat between the corners of
    the shorter side stops (S6-14 item 6). The section keeps the lines that
    computed it, which the section properties page prints."""
    sh = Sheet(registry)
    name = label(H, B, wall)
    Hs = sh.input("H", "H", H.value, f"{name}: outside dimension of the longer side ({H.entered} as entered)")
    Bs = sh.input("B", "B", B.value, f"Outside dimension of the shorter side ({B.entered} as entered)")
    t_nom, t_des = walls(sh, wall, grade)

    # The shorter wall's flat is B less two outside radii. Evaluated once:
    # the stop and its message come from the one comparison (ADR 0002).
    radii = 2 * registry.get(RADIUS_COEFF).value  # the two outside corner radii of one side, in wall thicknesses
    flat = compare(term("B", Bs.value, fmt_quantity_plain), ">",
                   term(f"{radii:g} t_des", radii * t_des.value, fmt_quantity_plain))
    if not flat:
        rule = registry.get(NO_FLAT)
        raise ProjectError(
            f"{name}: {flat.text}, the two outside corner radii of the shorter side "
            f"({registry.get(RADIUS).cite}). The wall leaves no flat between its corners ({rule.cite}). "
            f"The wall entered is the nominal wall thickness. Check the inputs.",
            stop=Stop.MEMBER_RECT_WALL_LEAVES_NO_FLAT)

    p = properties(sh, Hs, Bs, t_nom, t_des)
    return Section(label=name, family=RECT_TUBE, source=CUSTOM, W=p.W.value, A=p.A.value,
                   outline=Rectangle(H=Hs.value, B=Bs.value, b_t=p.b_t.value, h_t=p.h_t.value, J=p.J.value),
                   tnom=t_nom.value, tdes=t_des.value,
                   x=Axis(I=p.Ix.value, S=p.Sx.value, Z=p.Zx.value, r=p.rx.value),
                   y=Axis(I=p.Iy.value, S=p.Sy.value, Z=p.Zy.value, r=p.ry.value),
                   custom=True, computed=tuple(sh.lines))
