"""The line a fillet weld is checked on: its length and its section modulus
as a line, so forces come out per inch of weld (docs/brief/welds.md, W3).

Four lines, one for each way a member meets what it is welded to:

- **The ring**: a round member welded all around (W1, W3). The post at the
  rail and at the baseplate, the intermediate rail at the post.
- **The rounded rectangle**: a rectangular member welded all around, straight
  runs on its flats and quarter-circle arcs at its corners, on its outside
  surface (S6-6). A rectangular post on the baseplate, and a rectangular
  branch on a round chord (S6-9).
- **The face pair**: a rectangular post welded to the baseplate on one pair
  of opposite faces, two parallel straight lines stopping at the tangent
  points (S6-6).
- **Table K5.1**: a rectangular branch on a rectangular chord, on the
  effective weld properties of AISC 360-22 Table K5.1 (S6-8).

Every line but the ring has two section moduli, one for a load across the
guard and one for a load along the rail. ``Line.S_for`` gives the one a
direction case bends.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from handrail.calc import PI, Line as CalcLine, Sheet, Sym, minimum
from handrail.dimensions import Dimension
from handrail.directions import DIRECTIONS, Direction, unknown
from handrail.materials import yield_stress
from handrail.orientation import PostAxes
from handrail.project import FACES_PARALLEL, FACES_PERPENDICULAR
from handrail.registry import Registry
from handrail.shapes import Section
from handrail.units import Q_

LINE_METHOD = "ej.weld.line_method"
ROUNDED = "ej.weld.line.rounded_rectangle"
FACE_PAIR = "ej.weld.line.face_pair"
CORNER_COEFF = "ej.weld.line.corner_radius_coeff"
K5 = "aisc360.K5.nonuniform"
K5_MAPPING = "ej.weld.k5.case_mapping"
BE, BE_COEFF, BE_CAP = "aisc360.eq.K1-1", "aisc360.eq.K1-1.coeff", "aisc360.K5.1.Be_cap"
TRANSVERSE, LONGITUDINAL = "transverse", "longitudinal"


@dataclass
class Ring:
    """A weld line. Named for the first one, the ring of a round member; the
    others fill ``S_by`` and say in their own words where a force is uniform."""

    w: Sym
    L_w: Sym
    S_w: Sym | None  # None where the line carries no moment (Check 4b, a simple shear connection)
    t_e: Sym
    lines: list[CalcLine]
    # A line that is not a ring: its section modulus for bending by a load
    # across the guard (TRANSVERSE) and by a load along the rail (LONGITUDINAL).
    S_by: dict[str, Sym] = field(default_factory=dict)
    uniform: str = "uniform around the ring"      # how the notes say a force is spread over the line
    every_point: str = "at every point of the ring"

    def S_for(self, direction: Direction) -> Sym | None:
        """The section modulus the moment of this direction case acts on."""
        if not self.S_by:
            return self.S_w
        if direction in (Direction.OUTWARD, Direction.INWARD):
            return self.S_by[TRANSVERSE]
        if direction == Direction.LONGITUDINAL:
            return self.S_by[LONGITUDINAL]
        if direction in (Direction.DOWNWARD, Direction.UPWARD):
            return None  # a vertical case has no moment at the weld
        unknown("Weld line", "direction case", direction, DIRECTIONS)


def _throat(sh: Sheet, w: Sym) -> Sym:
    return sh.line("t_e", "t_e", sh.coeff("aisc360.J2.2a.throat.coeff") * w, "Effective throat, equal-leg fillet",
                   cite_ids=("aisc360.J2.2a.throat",), unit="inch")


def ring(registry: Registry, sec: Section, size: Dimension, member: str = "post", symbol: str = "D",
         bending: bool = True) -> Ring:
    """Line properties of a fillet weld all around a round member (W3): the
    post for Checks 3 and 7, the intermediate rail for Check 4b. Without
    bending (Check 4b) the section modulus S_w is not needed or printed."""
    sh = Sheet(registry)
    sh.heading("Weld properties")
    D = sh.given("D", symbol, sec.OD, f"{sec.label}: outside diameter; the weld ring is the {member} perimeter", sec.source)
    w = sh.given("w", "w", size.value, f"Fillet weld leg size, all around ({size.entered} as entered)", "Input")
    L_w = sh.line("L_w", "L_w", PI * D, f"Weld length: the {member} perimeter", cite_ids=(LINE_METHOD,), unit="inch")
    S_w = None
    if bending:
        S_w = sh.line("S_w", "S_w", PI * D**2 / 4, "Section modulus of the ring as a line", cite_ids=(LINE_METHOD,),
                      unit="inch**2")
    t_e = sh.line("t_e", "t_e", sh.coeff("aisc360.J2.2a.throat.coeff") * w, "Effective throat, equal-leg fillet",
                  cite_ids=("aisc360.J2.2a.throat",), unit="inch")
    return Ring(w=w, L_w=L_w, S_w=S_w, t_e=t_e, lines=sh.lines)


@dataclass(frozen=True)
class Side:
    """One outside dimension of a rectangular member at its weld, as printed."""

    key: str
    symbol: str
    value: Q_
    note: str


def _corner_radius(sh: Sheet, sec: Section) -> Sym:
    t = sh.given("t_des_w", 't_"des"', sec.tdes, f"Design wall thickness, {sec.label}: it sets the outside corner radius",
                 sec.source)
    return sh.line("R_o", "R_o", sh.coeff(CORNER_COEFF) * t, "Outside corner radius", cite_ids=(ROUNDED,), unit="inch")


def _rounded_modulus(sh: Sheet, tag: str, load: str, a: Sym, b: Sym, R: Sym) -> Sym:
    """Section modulus of the rounded rectangle as a line, for bending in the
    direction of its side b, about the axis parallel to its side a: the two
    flats parallel to the axis, the two across it, and the four corner arcs."""
    y_c = sh.line(f"y_c_{tag}", f'y_("c,{tag}")', b / 2 - R, f"Distance from the axis to the corner arc centers, {load}",
                  cite_ids=(ROUNDED,), unit="inch")
    I = sh.line(f"I_w_{tag}", f'I_("w,{tag}")',
                2 * (a - 2 * R) * (b / 2) ** 2 + (b - 2 * R) ** 3 / 6 + 2 * PI * R * y_c**2 + 8 * y_c * R**2 + PI * R**3,
                f"Moment of inertia of the weld line, {load}: flats and corner arcs", cite_ids=(ROUNDED,),
                unit="inch**3")
    return sh.line(f"S_w_{tag}", f'S_("w,{tag}")', I / (b / 2), f"Section modulus of the weld line, {load}",
                   cite_ids=(ROUNDED,), unit="inch**2")


def rounded_rectangle(registry: Registry, sec: Section, size: Dimension, member: str, along: Side, across: Side,
                      bending: bool = True) -> Ring:
    """Line properties of a fillet weld all around a rectangular member, on
    its outside surface (S6-6). ``along`` is its dimension parallel to the
    rail and ``across`` the one perpendicular to it, so a load across the
    guard bends the line over ``across`` and a load along the rail over
    ``along``. Without bending (Check 4b) only the length is printed, and
    the two sides are whatever the caller names them."""
    sh = Sheet(registry)
    sh.heading("Weld properties")
    a = sh.given(along.key, along.symbol, along.value, f"{sec.label}: {along.note}; the weld line is the {member} outline",
                 sec.source)
    b = sh.given(across.key, across.symbol, across.value, across.note, sec.source)
    R = _corner_radius(sh, sec)
    w = sh.given("w", "w", size.value, f"Fillet weld leg size, all around ({size.entered} as entered)", "Input")
    L_w = sh.line("L_w", "L_w", 2 * (a - 2 * R) + 2 * (b - 2 * R) + 2 * PI * R,
                  f"Weld length: the {member} outline, four flats and four corner arcs", cite_ids=(ROUNDED,), unit="inch")
    S_by = {}
    if bending:
        S_by = {TRANSVERSE: _rounded_modulus(sh, "t", "a load across the guard", a, b, R),
                LONGITUDINAL: _rounded_modulus(sh, "l", "a load along the rail", b, a, R)}
    return Ring(w=w, L_w=L_w, S_w=None, t_e=_throat(sh, w), lines=sh.lines, S_by=S_by,
                uniform="uniform along the weld line", every_point="at every point of the weld line")


def face_pair(registry: Registry, sec: Section, size: Dimension, pattern: str, axes: PostAxes) -> Ring:
    """Line properties of a fillet weld on one pair of opposite faces of a
    rectangular post (S6-6): two parallel straight lines, each the flat
    width of its face. Bent about the axis parallel to the lines they are
    the extreme fibers; bent about the other, each line bends about its
    own middle."""
    if pattern == FACES_PARALLEL:
        face, apart, which, other = axes.parallel, axes.perpendicular, "parallel to the rail", "perpendicular to the rail"
        strong, weak = TRANSVERSE, LONGITUDINAL
    elif pattern == FACES_PERPENDICULAR:
        face, apart, which, other = axes.perpendicular, axes.parallel, "perpendicular to the rail", "parallel to the rail"
        strong, weak = LONGITUDINAL, TRANSVERSE
    else:
        raise ValueError(f"face pair: base_pattern {pattern!r}; expected {FACES_PARALLEL!r} or {FACES_PERPENDICULAR!r}")
    words = {TRANSVERSE: "a load across the guard", LONGITUDINAL: "a load along the rail"}
    sh = Sheet(registry)
    sh.heading("Weld properties")
    a = sh.given("a_face", 'a_"face"', face, f"{sec.label}: outside width of each welded face, the faces {which}",
                 sec.source)
    d = sh.given("d_faces", 'd_"faces"', apart, f"Distance between the two weld lines: the post's outside dimension {other}",
                 sec.source)
    R = _corner_radius(sh, sec)
    w = sh.given("w", "w", size.value, f"Fillet weld leg size, each welded face ({size.entered} as entered)", "Input")
    l_w = sh.line("l_w", "l_w", a - 2 * R, "Length of each weld line: the flat of its face, between the tangent points",
                  cite_ids=(FACE_PAIR,), unit="inch")
    L_w = sh.line("L_w", "L_w", 2 * l_w, "Weld length: the two lines", cite_ids=(FACE_PAIR,), unit="inch")
    S_strong = sh.line(f"S_w_{strong[0]}", f'S_("w,{strong[0]}")', l_w * d,
                       f"Section modulus of the weld lines, {words[strong]}: the lines are the extreme fibers",
                       cite_ids=(FACE_PAIR,), unit="inch**2")
    S_weak = sh.line(f"S_w_{weak[0]}", f'S_("w,{weak[0]}")', l_w**2 / 3,
                     f"Section modulus of the weld lines, {words[weak]}: each line bends about its own middle",
                     cite_ids=(FACE_PAIR,), unit="inch**2")
    return Ring(w=w, L_w=L_w, S_w=None, t_e=_throat(sh, w), lines=sh.lines, S_by={strong: S_strong, weak: S_weak},
                uniform="uniform along the weld lines", every_point="at every point of the weld lines")


def table_k5_1(registry: Registry, size: Dimension, chord: Section, chord_grade: str, chord_name: str, face: Side,
               branch: Section, branch_grade: str, branch_name: str, depth: Side, width: Side,
               bending: bool = True) -> Ring:
    """Effective weld properties of a rectangular branch on a rectangular
    chord, AISC 360-22 Table K5.1, T-connection at 90 degrees (S6-8).
    ``face`` is the width B of the chord face the branch lands on; ``depth``
    is the branch's dimension H_b along the chord's axis and ``width`` its
    dimension B_b across the chord face, outside dimensions as the
    equations are written. The effective width B_e is Eq. K1-1's, held to
    the table's cap as the table prints it: the branch is at 90 degrees.

    In-plane bending of the branch is a load along the chord, and
    out-of-plane bending a load across it. Without bending (Check 4b) only
    the effective length is printed."""
    sh = Sheet(registry)
    sh.heading("Weld properties")
    B = sh.given(face.key, face.symbol, face.value, f"{chord.label}: {face.note}", chord.source)
    t = sh.given("t_chord", "t", chord.tdes, f"{chord_name} design wall thickness, the chord", chord.source)
    Fy = yield_stress(registry, chord_grade, chord).line(sh, "F_y_chord", "F_y")
    Hb = sh.given(depth.key, depth.symbol, depth.value, f"{branch.label}: {depth.note}", branch.source)
    Bb = sh.given(width.key, width.symbol, width.value, width.note, branch.source)
    tb = sh.given("t_branch", "t_b", branch.tdes, f"{branch_name} design wall thickness, the branch", branch.source)
    Fyb = yield_stress(registry, branch_grade, branch).line(sh, "F_y_branch", 'F_"yb"')
    Be_K1 = sh.line("B_e_K1", 'B_("e,K1")', sh.coeff(BE_COEFF) / (B / t) * (Fy * t / (Fyb * tb)) * Bb,
                    "Effective width of the branch across the chord face", cite_ids=(BE,), unit="inch")
    Be = sh.line("B_e", "B_e", minimum(Be_K1, Bb / 2),
                 "Effective width: B_e/2 not more than B_b/4, the branch being at 90 degrees", cite_ids=(BE_CAP,),
                 unit="inch")
    w = sh.given("w", "w", size.value, f"Fillet weld leg size, all around ({size.entered} as entered)", "Input")
    L_w = sh.line("L_w", "l_e", 2 * Hb + 2 * Be, "Effective weld length", cite_ids=("aisc360.eq.K5-5", K5), unit="inch")
    S_by = {}
    if bending:
        S_by = {
            LONGITUDINAL: sh.line("S_w_l", 'S_"ip"', Hb**2 / 3 + Be * Hb,
                                  "Effective section modulus of the weld as a line, in-plane bending: a load along "
                                  "the rail", cite_ids=("aisc360.eq.K5-6", K5_MAPPING), unit="inch**2"),
            TRANSVERSE: sh.line("S_w_t", 'S_"op"', Hb * Bb + Bb**2 / 3 - (Bb - Be) ** 3 / (3 * Bb),
                                "Effective section modulus of the weld as a line, out-of-plane bending: a load across "
                                "the guard", cite_ids=("aisc360.eq.K5-7", K5_MAPPING), unit="inch**2"),
        }
    return Ring(w=w, L_w=L_w, S_w=None, t_e=_throat(sh, w), lines=sh.lines, S_by=S_by,
                uniform="uniform over the effective weld length", every_point="at every point of the effective weld")

