"""The weld ring: one method for the weld checks (docs/brief/welds.md, W1-W12, S4-8 to S4-12).

A round member welded all around with a fillet weld is a ring of that
member's diameter D. Checks 3 (rail to post) and 7 (post to baseplate) use
the post's ring; Check 4b (intermediate rail to post) uses the intermediate
rail's, with the roles of Check 3 reversed: the intermediate rail is the
branch and the post wall the chord.

- Weld as a line, elastic (W3): L_w = pi D, S_w = pi D^2/4, so forces come
  out per inch of weld. Shear V/L_w is taken as uniform around the ring; the
  axial force P/L_w is uniform; bending M/S_w peaks at the extreme fibers.
- No bearing credit (W10): the weld carries everything, in compression as in
  tension. Both extreme fibers are evaluated and the larger resultant governs.
- At an extreme fiber the weld axis is perpendicular to the plane of bending,
  so theta = 90 deg there. The §J2.4 directional increase k_ds applies on
  round hollow sections only (W2); Check 3 takes k_ds = 1.0.
- Weld metal: F_nw t_e k_ds / Omega per inch. Base metal at a fusion face:
  shear rupture, 0.60 Fu t / Omega per inch (W5, W6). In Checks 3 and 7 the
  post wall is covered by Check 5 (W5; the Fu/Fy guard is in validate.py).
  Check 4b does not rely on that: there the post wall is the chord, and its
  base metal is checked directly, with the intermediate rail wall's.
- Minimum size per Table J2.4 on the thinner part joined, walls at their
  nominal thickness, is pass/fail; no maximum size is checked (W11).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast
from collections.abc import Callable

from handrail import joints
from handrail.calc import (PI, Line, Sheet, Sym, absolute, arccos, compare, fmt_quantity_plain, maximum, minimum,
                           mtext, order, sin, sqrt, term)
from handrail.demand import ASD, Given, Wording, demand
from handrail.directions import (
    COMPONENT, COMPONENT_DIRECTIONS, DIRECTIONS, DISTRIBUTED, DOWNWARD, HORIZONTAL, LOAD_TYPES, Direction, Kind,
    LoadType, unknown,
)
from handrail.dimensions import Dimension
from handrail.errors import SectionStop
from handrail.intermediate import NONE_TEXT
from handrail.joints import JointMember
from handrail.loading import COMBO, combo_text, exempt_case
from handrail.materials import FEXX_ENTRY, Stress, baseplate_tensile_strength, tensile_strength
from handrail.project import NO_INTERMEDIATE, SAME_AS_TOP, Member, Project
from handrail.registry import Registry
from handrail.results import Case, Check, Loading
from handrail.shapes import Section
from handrail.units import Q_

LINE_METHOD = "ej.weld.line_method"
NO_BEARING = "ej.weld.no_bearing"
PER_INCH = "lbf/inch"


@dataclass
class WeldCase(Case):
    """A weld check case, with the values its envelope row prints."""

    sense: str = ""            # axial force on the ring: "compression" or "tension"
    f_a: Any = None         # axial force per inch
    f_b: Any = None         # bending force per inch at the extreme fiber; None without moment
    f_v: Any = None         # shear per inch; None without horizontal load
    f_n: Any = None         # normal force per inch at the governing fiber; None with shear only (Check 4b)
    f_r: Any = None         # resultant per inch at the governing fiber
    fiber: str = ""            # "compression side", "tension side" or "uniform"
    theta: Any = None       # angle of f_r to the weld axis; None where k_ds is not computed from it
    k_ds: float | None = None
    weld_allow: Any = None  # weld metal R_n/Omega per inch
    base_allow: Any = None  # base metal R_n/Omega per inch at the checked fusion face
    base_demand: Any = None  # force per inch on the base metal line; None when the face sees none
    weld_ratio: float | None = None
    base_ratio: float | None = None  # None when the fusion face sees no force in this case
    governs: str = ""          # the line demand, capacity and ratio come from: "weld metal" or "base metal"


# ---------------------------------------------------------------------------
# Computed once per check
# ---------------------------------------------------------------------------


@dataclass
class WeldCheck(Check):
    """A weld check, with the result of its minimum size line."""

    min_size_ok: bool = True
    base_governs: str = ""  # Check 4b's governing fusion face: "post wall" or "intermediate rail wall"


@dataclass
class Ring:
    w: Sym
    L_w: Sym
    S_w: Sym | None  # None where the ring carries no moment (Check 4b, a simple shear connection)
    t_e: Sym
    lines: list[Line]


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


@dataclass
class Part:
    """A part the weld joins, as printed: line key, symbol, thickness, note, source."""

    key: str
    symbol: str
    t: Any
    note: str
    source: str


def nominal_wall(name: str, member: str, sec: Section) -> Part:
    """A wall as a part joined for the minimum size: nominal thickness, the
    physical wall, because Table J2.4 is a heat-input rule, not a strength
    provision (welds.md, fillet size limits). Strength lines use t_des (W4)."""
    return Part(f"t_{name}_nom", f't_"{name},nom"', sec.tnom, f"{member} nominal wall thickness, {sec.label}", sec.source)


@dataclass
class SizeLimits:
    lines: list[Line]
    failure: str  # "" when the weld meets the minimum size

    @property
    def ok(self) -> bool:
        return not self.failure


def size_limits(registry: Registry, w: Sym, parts: tuple[Part, Part]) -> SizeLimits:
    """Minimum size per Table J2.4 on the thinner part joined, pass/fail; the
    maximum size along edges does not apply to these T-joints (W11)."""
    sh = Sheet(registry)
    table = registry.get("aisc360.J2.4.min_size")
    sh.heading("Fillet size limits")
    t1, t2 = (sh.given(p.key, p.symbol, p.t, p.note, p.source) for p in parts)
    t_min = sh.line("t_min", 't_"min"', minimum(t1, t2), "Thinner part joined", cite_ids=(table.id,), unit="inch")
    row = next(r for r in table.value if t_min.value <= Q_(r["t_max_in"], "inch"))
    w_min = sh.given("w_min", 'w_"min"', Q_(row["w_min_in"], "inch"), "Minimum fillet size for the thinner part joined",
                     table.cite)
    failure = ""
    # One comparison gives the pass or fail and the relation printed (ADR 0002).
    meets = compare(w.stated(), ">=", w_min.stated())
    if meets:
        sh.decision(meets, "OK", "Minimum size", cite_ids=(table.id,))
    else:
        sh.decision(meets, "NG: below the minimum size", "Minimum size: the check fails whatever its ratio",
                    cite_ids=(table.id,))
        failure = (f"Fillet weld w = {fmt_quantity_plain(w.value)} is below the minimum size "
                   f"{fmt_quantity_plain(w_min.value)} for the thinner part joined, "
                   f"t = {fmt_quantity_plain(t_min.value)} ({table.cite}).")
    not_applicable = registry.get("ej.weld.max_size_not_applicable")
    sh.decision(mtext("Maximum fillet size"), "Not applicable", not_applicable.value,
                cite_ids=("aisc360.J2.2b.max_size_edges", not_applicable.id))
    return SizeLimits(lines=sh.lines, failure=failure)


@dataclass
class WeldMetal:
    Fnw: Sym
    Om: Sym
    lines: list[Line]


def weld_metal(registry: Registry, electrode: str) -> WeldMetal:
    sh = Sheet(registry)
    sh.heading("Weld metal")
    FEXX = sh.code_value("F_EXX", 'F_"EXX"', FEXX_ENTRY[electrode], f"Electrode classification strength, {electrode}")
    Fnw = sh.line("F_nw", 'F_"nw"', sh.coeff("aisc360.J2.5.fnw.coeff") * FEXX, "Nominal stress of the weld metal",
                  cite_ids=("aisc360.J2.5.fnw",), unit="ksi")
    Om = sh.code_value("Omega_w", "Omega_w", "aisc360.J2.5.omega_w", "Safety factor, fillet weld (ASD)")
    return WeldMetal(Fnw=Fnw, Om=Om, lines=sh.lines)


@dataclass
class BaseMetal:
    allow: Sym
    lines: list[Line]


def base_metal(registry: Registry, heading: str, Fu_of: Stress, part: Part,
               sub: str = "BM", key: str = "BM") -> BaseMetal:
    """Shear rupture of the base metal at a fusion face, per inch of weld (W5, W6).
    ``sub`` (the printed subscript) and ``key`` (in the line keys) tell two
    fusion faces apart in one check (Check 4b)."""
    sh = Sheet(registry)
    sh.heading(heading)
    Fu = Fu_of.line(sh, f"F_u_{key}", "F_u")
    t = sh.given(part.key, part.symbol, part.t, part.note, part.source)
    R = sh.line(f"R_n_{key}", f'R_(n,"{sub}")', sh.coeff("aisc360.eq.J4-4.coeff") * Fu * t,
                "Shear rupture at the fusion face, per inch of weld",
                cite_ids=("aisc360.eq.J4-4", "aisc_manual.part9.base_metal"), unit=PER_INCH)
    Om = sh.code_value(f"Omega_{key}", 'Omega_"BM"', "aisc360.J4.2.omega_rupture", "Safety factor, shear rupture (ASD)")
    allow = sh.line(f"R_n_{key}_over_Omega", f'frac(R_(n,"{sub}"), Omega_"BM")', R / Om, "Allowable base metal strength per inch",
                    cite_ids=("aisc360.eq.B3-2",), unit=PER_INCH)
    return BaseMetal(allow=allow, lines=sh.lines)


def post_wall_covered(registry: Registry) -> list[Line]:
    """The printed line for the post side of either weld (W5)."""
    sh = Sheet(registry)
    covered = registry.get("ej.weld.post_wall_covered")
    sh.decision(mtext("Post wall at the weld"), "Covered by Check 5", covered.value, cite_ids=(covered.id,))
    return sh.lines


# ---------------------------------------------------------------------------
# Per case
# ---------------------------------------------------------------------------


@dataclass
class RingForces:
    f_a: Sym | None  # None where the ring carries no axial force (Check 4b)
    f_b: Sym | None
    f_v: Sym | None
    f_n: Sym | None  # None where the ring carries shear only (Check 4b)
    f_r: Sym
    fiber: str


SIDE = {"compression": '"c"', "tension": '"t"'}


def ring_forces(sh: Sheet, rg: Ring, P: Sym, sense: str, V: Sym | None = None, M: Sym | None = None) -> RingForces:
    """Forces per inch of weld at the governing point of the ring (W3, W10).

    P is the axial force's magnitude and ``sense`` its direction. With a
    moment, the side of bending whose stress has the same sense as P adds
    to it; the other side subtracts. Both are printed and the larger governs.
    """
    f_a = sh.line("f_a", "f_a", P / rg.L_w, f"Axial force per inch of weld, {sense}, uniform around the ring",
                  cite_ids=(LINE_METHOD,), unit=PER_INCH)
    f_b = None
    if M is None:
        f_n = sh.line("f_n", "f_n", f_a, "Normal force per inch: no moment, the same at every point of the ring",
                      cite_ids=(NO_BEARING,), unit=PER_INCH)
        fiber = "uniform"
    else:
        f_b = sh.line("f_b", "f_b", M / rg.S_w, "Bending force per inch at the extreme fiber", cite_ids=(LINE_METHOD,),
                      unit=PER_INCH)
        other = "tension" if sense == "compression" else "compression"
        add = sh.line(f"f_n_{sense}", f"f_(n,{SIDE[sense]})", f_a + f_b, f"Normal force per inch, {sense} side of bending: "
                      f"axial and bending add", cite_ids=(NO_BEARING,), unit=PER_INCH)
        sub = sh.line(f"f_n_{other}", f"f_(n,{SIDE[other]})", absolute(f_a - f_b), f"Normal force per inch, {other} side of bending",
                      cite_ids=(NO_BEARING,), unit=PER_INCH)
        # The larger governs, a tie going to the side where axial and bending
        # add; the line prints the comparison that chose it (ADR 0002).
        larger = compare(add.stated(), ">=", sub.stated())
        gov, side = add, sense
        if not larger:
            larger = compare(sub.stated(), ">=", add.stated())
            gov, side = sub, other
        fiber = f"{side} side"
        sh.decision(larger, f"{side.capitalize()} side governs", "No bearing credit: both extreme fibers checked",
                    cite_ids=(NO_BEARING,))
        f_n = sh.line("f_n", "f_n", gov, f"Normal force per inch at the governing fiber, {side} side",
                      cite_ids=(NO_BEARING,), unit=PER_INCH)
    if V is None:
        f_v = None
        f_r = sh.line("f_r", "f_r", f_n, "Resultant per inch: normal force only", cite_ids=(LINE_METHOD,), unit=PER_INCH)
    else:
        f_v = sh.line("f_v", "f_v", V / rg.L_w, "Shear per inch of weld, taken as uniform around the ring",
                      cite_ids=(LINE_METHOD,), unit=PER_INCH)
        f_r = sh.line("f_r", "f_r", sqrt(f_n**2 + f_v**2), "Resultant per inch at the governing fiber: vector sum",
                      cite_ids=(LINE_METHOD,), unit=PER_INCH)
    return RingForces(f_a=f_a, f_b=f_b, f_v=f_v, f_n=f_n, f_r=f_r, fiber=fiber)


def shear_only(sh: Sheet, rg: Ring, V: Sym) -> RingForces:
    """Forces per inch of weld for a simple shear connection (Check 4b,
    Micah 2026-10-09): the reaction in the ring's plane, taken as uniform
    around the ring (W3); no axial force and no moment."""
    f_v = sh.line("f_v", "f_v", V / rg.L_w, "Shear per inch of weld, taken as uniform around the ring",
                  cite_ids=(LINE_METHOD,), unit=PER_INCH)
    f_r = sh.line("f_r", "f_r", f_v, "Resultant per inch: shear only, no axial force and no moment",
                  cite_ids=(LINE_METHOD,), unit=PER_INCH)
    return RingForces(f_a=None, f_b=None, f_v=f_v, f_n=None, f_r=f_r, fiber="uniform")


def directional_increase(sh: Sheet, registry: Registry, f_r: Sym, section: Section) -> tuple[Sym, Sym]:
    """theta at the governing point and k_ds from it, for a post the Check 7
    joint's table lists as allowed (W2; joints.py). Returns (theta, k_ds).
    Raises SectionStop otherwise: validation makes the same test, and this
    one holds when a calc is computed without it."""
    joints.CHECK_7.require(JointMember("post", section), error=SectionStop)
    line_method = registry.get(LINE_METHOD)
    f_par = sh.given("f_parallel", "f_parallel", Q_(0, PER_INCH), "Force component along the weld axis: at the extreme "
                     "fiber the weld axis is perpendicular to the plane of bending, and V acts in that plane",
                     line_method.cite)
    theta = sh.line("theta", "theta", arccos(f_par / f_r), "Angle between the resultant and the weld axis",
                    cite_ids=("aisc360.eq.J2-5", LINE_METHOD), unit="degree")
    k_ds = sh.line("k_ds", 'k_"ds"', sh.coeff("aisc360.eq.J2-5.base")
                   + sh.coeff("aisc360.eq.J2-5.coeff") * sin(theta) ** sh.coeff("aisc360.eq.J2-5.exponent"),
                   "Directional strength increase", cite_ids=("aisc360.eq.J2-5", "ej.weld.directional_round_hss"))
    return theta, k_ds


@dataclass
class Strength:
    weld_allow: Sym
    weld_ratio: Sym
    base_ratio: Sym | None
    ratio: Sym


def strength(sh: Sheet, rg: Ring, wm: WeldMetal, k_ds: Sym, f_r: Sym, base: BaseMetal,
             base_demand: Sym | None, base_note: str) -> Strength:
    """Weld metal and base metal ratios; the check ratio is the larger.
    ``base_demand`` is None when the fusion face sees no force in the case."""
    R = sh.line("R_n", "R_n", wm.Fnw * rg.t_e * k_ds, "Nominal fillet weld strength per inch",
                cite_ids=("aisc360.J2.4.fillet_strength",), unit=PER_INCH)
    allow = sh.line("R_n_over_Omega_w", "frac(R_n, Omega_w)", R / wm.Om, "Allowable weld metal strength per inch",
                    cite_ids=("aisc360.eq.B3-2",), unit=PER_INCH)
    r_w = sh.line("Ratio_w", '"Ratio"_w', f_r / allow, "Weld metal: demand / capacity", cite_ids=("aisc360.eq.B3-2",),
                  ratio=True)
    if base_demand is None:
        ratio = sh.line("Ratio", '"Ratio"', r_w, "Weld metal governs: no force on the base metal line in this case",
                        cite_ids=("aisc360.eq.B3-2",), ratio=True)
        return Strength(weld_allow=allow, weld_ratio=r_w, base_ratio=None, ratio=ratio)
    r_bm = sh.line("Ratio_BM", '"Ratio"_"BM"', base_demand / base.allow, base_note, cite_ids=("aisc360.eq.B3-2",), ratio=True)
    ratio = sh.line("Ratio", '"Ratio"', maximum(r_w, r_bm), "The larger of weld metal and base metal",
                    cite_ids=("aisc360.eq.B3-2",), ratio=True)
    return Strength(weld_allow=allow, weld_ratio=r_w, base_ratio=r_bm, ratio=ratio)


# ---------------------------------------------------------------------------
# The envelope, shared by Checks 3 and 7 (W10)
# ---------------------------------------------------------------------------


def weld_wording(where: str, moment_note: str, moment_cite: str) -> Wording:
    """What a weld check's demand block prints: forces on the weld, the shear
    factored before the moment. ``where`` is where the guard load acts."""
    return Wording(
        where={Kind.DOWNWARD: f"vertical, {where}", Kind.HORIZONTAL: f"horizontal ({{direction}}), {where}",
               Kind.UPWARD: f"upward, {where}"},
        axial="P",
        axial_notes={Kind.DOWNWARD: "Axial force on the weld, compression; no moment",
                     Kind.HORIZONTAL: "Axial force on the weld: dead load, compression",
                     Kind.UPWARD: "Axial force on the weld: net tension, guard load opposing dead load"},
        factored="shear", factored_symbol="V", factored_note="Horizontal force on the weld",
        moment_symbol="M", moment_note=moment_note, moment_cite=moment_cite,
    )


@dataclass
class WeldLines:
    """What a weld check's strength lines need: the ring, the weld metal and
    base metal, and how k_ds and the base metal demand are found. Checks 3,
    4b and 7 each set their own."""

    rg: Ring
    wm: WeldMetal
    base: BaseMetal
    head: list[Line]              # printed at the top of every case
    k_ds: Callable[[Sheet, Sym], tuple[Sym | None, Sym]]  # (theta or None, k_ds) at the governing point
    base_demand: Callable[[RingForces], Sym | None]       # the force on the base metal line, or None
    base_note: str


@dataclass
class WeldSetup(WeldLines):
    """Checks 3 and 7: the weld lines plus the guard-load envelope's demand."""

    wording: Wording              # what the demand block prints
    dead: Given                   # the axial dead load on the ring
    arm: Sym                      # moment arm of V to the weld, printed in the head


def _weld_case(registry: Registry, project: Project, loading: Loading, ws: WeldSetup,
               direction: Direction, load_type: LoadType) -> WeldCase:
    d = demand(registry, project, loading, direction, load_type, ASD, ws.wording, ws.dead, ws.arm)
    if d.P is None:
        return WeldCase(direction, load_type, "not checked", d.label, remark=d.remark)
    sh = Sheet(registry)
    sh.lines.extend(ws.head)
    sh.lines.extend(d.lines)
    f = ring_forces(sh, ws.rg, d.P, d.sense, d.V, d.M)
    return _weld_result(sh, ws, f, direction, load_type, d.label, d.sense)


def _weld_result(sh: Sheet, ws: WeldLines, f: RingForces, direction: Direction, load_type: LoadType, label: str,
                 sense: str) -> WeldCase:
    """k_ds, the weld metal and base metal lines, and the case. Demand and
    capacity come from the line the ratio comes from; a tie goes to the weld
    metal, as the printed max() does."""
    theta, k_ds = ws.k_ds(sh, f.f_r)
    bd = ws.base_demand(f)
    s = strength(sh, ws.rg, ws.wm, k_ds, f.f_r, ws.base, bd, ws.base_note)
    if s.base_ratio is not None and s.base_ratio.value > s.weld_ratio.value:
        # A base metal ratio means the face has a demand.
        governs, demand_value, capacity_value = "base metal", cast(Sym, bd).value, ws.base.allow.value
    else:
        governs, demand_value, capacity_value = "weld metal", f.f_r.value, s.weld_allow.value
    return WeldCase(direction, load_type, "checked", label,
                    demand=demand_value, capacity=capacity_value, ratio=s.ratio.value, lines=sh.lines,
                    sense=sense, f_a=f.f_a.value if f.f_a else None, f_b=f.f_b.value if f.f_b else None,
                    f_v=f.f_v.value if f.f_v else None, f_n=f.f_n.value if f.f_n else None, f_r=f.f_r.value,
                    fiber=f.fiber,
                    theta=theta.value if theta else None, k_ds=k_ds.value, weld_allow=s.weld_allow.value,
                    base_allow=ws.base.allow.value, base_demand=bd.value if bd else None,
                    weld_ratio=s.weld_ratio.value,
                    base_ratio=s.base_ratio.value if s.base_ratio else None, governs=governs)


def _min_size(chk: WeldCheck, limits: SizeLimits) -> None:
    """A weld below the minimum size fails the check whatever its ratio (W11)."""
    chk.min_size_ok = limits.ok
    if limits.failure:
        chk.failures.append(limits.failure)
        chk.flags.append(f"BELOW MINIMUM SIZE: {limits.failure}")
        chk.summary_flag = "below minimum size"


def _weld_check(chk: WeldCheck, registry: Registry, project: Project, loading: Loading, ws: WeldSetup,
                limits: SizeLimits) -> WeldCheck:
    _min_size(chk, limits)
    for direction in DIRECTIONS:
        for lt in LOAD_TYPES:
            if lt == DISTRIBUTED and loading.exempt:
                chk.cases.append(exempt_case(registry, direction, WeldCase))
            else:
                chk.cases.append(_weld_case(registry, project, loading, ws, direction, lt))
    return chk


# ---------------------------------------------------------------------------
# Check 3: top rail weld to post
# ---------------------------------------------------------------------------


def check_3(registry: Registry, project: Project, rail: Section, post: Section, loading: Loading) -> Check:
    """The rail to post weld: a flat ring of the post perimeter at the rail's
    underside, loaded at e = d_rail/2 (W1); k_ds = 1.0 (W2); base metal on
    the rail side, in-plane force only (W6); the rail wall's normal force is
    not checked (W7)."""
    rg = ring(registry, post, project.welds.rail_to_post)
    ecc = Sheet(registry)
    ecc.heading("Eccentricity")
    d = ecc.given("d_rail", 'd_"rail"', rail.OD, f"{rail.label}: outside diameter, the rail depth", rail.source)
    e = ecc.line("e", "e", d / 2, "Eccentricity: rail centerline to the weld plane at the rail underside",
                 cite_ids=("ej.weld.ring_model",), unit="inch")
    e_line = ecc.lines[-1]
    limits = size_limits(registry, rg.w, (nominal_wall("rail", "Top rail", rail), nominal_wall("post", "Post", post)))
    wm = weld_metal(registry, project.welds.electrode)
    kd = Sheet(registry)
    k_ds = kd.code_value("k_ds", 'k_"ds"', "ej.weld.branch_kds",
                         "No directional increase at the rail to post weld (a branch-to-chord joint)")
    grade = project.top_rail.grade
    t_rail = Part("t_rail", 't_"rail"', rail.tdes, f"Top rail design wall thickness, {rail.label}", rail.source)  # W4
    base = base_metal(registry, "Base metal: rail fusion face", tensile_strength(registry, grade, rail), t_rail)
    normal = registry.get("ej.weld.rail_wall_normal")
    walls = Sheet(registry)
    walls.decision(mtext("Rail wall, normal force"), "Not checked", normal.value, cite_ids=(normal.id,))
    head = (rg.lines + ecc.lines + limits.lines + wm.lines + kd.lines + base.lines + walls.lines
            + post_wall_covered(registry))
    ws = WeldSetup(
        rg=rg, wm=wm, base=base, head=head,
        wording=weld_wording("on the rail at the post", "Moment at the weld plane: V at the rail centerline, arm e",
                             "ej.weld.ring_model"),
        dead=Given("D_rail", 'D_"rail"', loading.D_rail,
                   "Top rail dead load at the weld: w_D over the span (the tributary length)", "Loading"),
        arm=e,
        k_ds=lambda _sh, _f_r: (None, k_ds),
        base_demand=lambda f: f.f_v,
        base_note="Rail fusion face: in-plane shear only",
    )
    chk = WeldCheck(3, "Top rail weld to post", "f_r", "frac(R_n, Omega_w)", derived_lengths=[e_line])
    return _weld_check(chk, registry, project, loading, ws, limits)


# ---------------------------------------------------------------------------
# Check 7: post weld to baseplate
# ---------------------------------------------------------------------------


def check_7(registry: Registry, project: Project, post: Section, loading: Loading) -> Check:
    """The post to baseplate weld: a ring of the post perimeter at the top of
    the baseplate, moment arm h - t_p; k_ds from theta at the governing point
    (W2); base metal on the baseplate side against the resultant (W5)."""
    rg = ring(registry, post, project.welds.post_to_baseplate)
    arm = Sheet(registry)
    arm.heading("Moment arm")
    L_post = arm.given("L_post", 'L_"post"', loading.L_post,
                       "Moment arm, h - t_p: guard load at the top rail centerline, weld at the top of the baseplate",
                       "Loading")
    t_p = Part("t_p", "t_p", project.baseplate_thickness.value, "Baseplate thickness", "Input")
    limits = size_limits(registry, rg.w, (nominal_wall("post", "Post", post), t_p))
    wm = weld_metal(registry, project.welds.electrode)
    grade = project.baseplate.grade
    base = base_metal(registry, "Base metal: baseplate fusion face", baseplate_tensile_strength(grade), t_p)
    head = rg.lines + arm.lines + limits.lines + wm.lines + base.lines + post_wall_covered(registry)
    ws = WeldSetup(
        rg=rg, wm=wm, base=base, head=head,
        wording=weld_wording("at the top of the post", "Moment at the top of the baseplate",
                             "aisc_manual.t3-23.case22.M"),
        dead=Given("P_D", "P_D", loading.P_D, "D at the post: axial dead load at the top of the baseplate", "Loading"),
        arm=L_post,
        k_ds=lambda sh, f_r: directional_increase(sh, registry, f_r, post),
        base_demand=lambda f: f.f_r,
        base_note="Baseplate fusion face: the resultant per inch",
    )
    chk = WeldCheck(7, "Post weld to baseplate", "f_r", "frac(R_n, Omega_w)")
    return _weld_check(chk, registry, project, loading, ws, limits)


# ---------------------------------------------------------------------------
# Check 4b: intermediate rail weld to post
# ---------------------------------------------------------------------------

INT_RING = "ej.weld.intermediate_ring_model"


def _reaction_4b(registry: Registry, project: Project, loading: Loading, direction: Direction
                 ) -> tuple[Sheet, Sym, str]:
    """The weld reaction R (S4-9): the component load adjacent to the post,
    so this end takes the full P_c, with the intermediate rail's dead-load
    end reaction; ASD D + L, the component load as L. Returns the demand
    lines, R and the combination label."""
    sh = Sheet(registry)
    sh.heading(f"Demand: {direction.lower()}, component load")
    combo, down = registry.get(COMBO), registry.get("ej.component.downward")
    wD = sh.given("w_D_int", 'w_(D,"int")', loading.w_D_int, "Intermediate rail self-weight", "Loading")
    L = sh.given("L", "L", project.span.value, "Span, simple beam", "Input")
    RD = sh.line("R_D", "R_D", wD * L / 2, "Dead-load end reaction at the post", cite_ids=("aisc_manual.t3-23.case1.R",),
                 unit="lbf")
    Pc = sh.given("P_c", "P_c", loading.P_c, "Component load adjacent to the post: the full P_c to this end",
                  registry.get(INT_RING).cite)
    gD, gL = sh.factor(combo.id, "D"), sh.factor(combo.id, "L")
    if direction == DOWNWARD:
        R = sh.line("R", "R", gD * RD + gL * Pc, "Weld reaction: dead and component loads in the same (vertical) "
                    "direction, in the ring's plane", cite_ids=(INT_RING, down.id), unit="lbf")
        label = f"{combo_text(combo)}, vertical\n{combo.cite}; {down.cite}"
    elif direction == HORIZONTAL:
        R = sh.line("R", "R", sqrt((gL * Pc) ** 2 + (gD * RD) ** 2), "Weld reaction: horizontal component load and "
                    "vertical dead-load reaction at right angles, both in the ring's plane", cite_ids=(INT_RING,),
                    unit="lbf")
        label = f"{combo_text(combo, {'D': 'vertical', 'L': 'horizontal'}, ', ')}, vector sum\n{combo.cite}"
    else:
        unknown("Check 4b", "component load direction", direction, COMPONENT_DIRECTIONS)
    return sh, R, label


def check_4b(registry: Registry, project: Project, post: Section, inter: Section | None,
             loading: Loading) -> WeldCheck:
    """The intermediate rail to post weld (S4-8 to S4-12): a flat ring of the
    intermediate rail's perimeter at the post face, a simple shear
    connection consistent with the simple-span member, so the reaction R
    acts at the weld with no end moment (Micah 2026-10-09, revising S4-9 and
    S4-12); k_ds = 1.0, a branch-to-chord joint (W2); base metal on both
    connected walls, the post wall (the chord) and the intermediate rail wall
    (the branch), each in shear rupture against the in-plane shear, the lower
    allowable governing (Micah 2026-10-09, the W5 rule); the post wall's chord
    limit states are not checked (W7, extended). Same as the top rail with R <= P
    and the post wall no thinner than the rail wall, the observation line
    instead (S4-8; wall guard, Micah 2026-10-09); with no intermediate rail,
    "none"."""
    chk = WeldCheck("4b", "Intermediate rail weld to post", "f_r", "frac(R_n, Omega_w)")
    state = project.intermediate_rail.state
    if state == NO_INTERMEDIATE:
        chk.observation, chk.result = NONE_TEXT, "None"
        return chk

    # Past the "none" return above there is an intermediate rail: its section and its member.
    inter = cast(Section, inter)
    int_member = cast(Member, project.intermediate_member)
    same = state == SAME_AS_TOP
    head_guard: list[Line] = []
    if same:
        # R is the larger of the two cases (the downward one, R_D + P_c, always
        # is); its lines print under the observation, so R can be traced.
        reactions = [_reaction_4b(registry, project, loading, direction) for direction in COMPONENT_DIRECTIONS]
        rsh, R, _ = max(reactions, key=lambda t: t[1].value)
        P = loading.P
        # Two guards (Micah, 2026-10-09): R <= P, and the post wall, Check
        # 4b's chord, no thinner than the rail wall, Check 3's chord, whose
        # base metal line Check 3 checks.
        # Each guard is one comparison: it decides, and when it fails it
        # prints the relation it found (ADR 0002).
        t_post, t_rail = post.tdes, inter.tdes
        within_P = compare(R.stated(), "<=", term("P", P))
        wall_covered = compare(term('t_"des,post"', t_post), ">=", term('t_"des,rail"', t_rail))
        if within_P and wall_covered:
            text = registry.get("ej.weld.intermediate.same_as_top").value
            chk.observation = text.format(R=fmt_quantity_plain(R.value), P=fmt_quantity_plain(P),
                                          t_post=fmt_quantity_plain(t_post), t_rail=fmt_quantity_plain(t_rail))
            chk.observation_lines = rsh.lines
            chk.result = "Controlled by Check 3"
            return chk
        g = Sheet(registry)
        if not within_P:
            g.decision(within_P, "Computed in full",
                       "Same section as the top rail, but the weld reaction exceeds the concentrated guard load, "
                       "so Check 3 does not cover it", cite_ids=("ej.weld.intermediate.same_as_top",))
        if not wall_covered:
            g.decision(wall_covered, "Computed in full",
                       "Same section as the top rail, but the post wall (the chord here) is thinner than the rail "
                       "wall (the chord in Check 3), so Check 3's base metal line does not cover it",
                       cite_ids=("ej.weld.intermediate.same_as_top",))
        head_guard = g.lines

    model = Sheet(registry)
    model.heading("Connection model")
    simple = registry.get("ej.weld.intermediate_simple_shear")
    model.decision(mtext("Intermediate rail to post weld"), "Simple shear connection", simple.value,
                   cite_ids=(simple.id, INT_RING))
    # Its own section always has its own weld size (project.py requires it).
    size = project.welds.rail_to_post if same else cast(Dimension, project.welds.intermediate_rail_to_post)
    rg = ring(registry, inter, size, member="intermediate rail", symbol='D_"int"', bending=False)
    limits = size_limits(registry, rg.w, (nominal_wall("int", "Intermediate rail", inter),
                                          nominal_wall("post", "Post", post)))
    wm = weld_metal(registry, project.welds.electrode)
    kd = Sheet(registry)
    k_ds = kd.code_value("k_ds", 'k_"ds"', "ej.weld.branch_kds",
                         "No directional increase at the intermediate rail to post weld (a branch-to-chord joint)")
    # Base metal at both fusion faces, each in shear rupture against the
    # in-plane shear; the lower allowable governs (Micah, 2026-10-09). W4: t_des.
    post_grade, int_grade = project.post.grade, int_member.grade
    t_post = Part("t_post", 't_"post"', post.tdes, f"Post design wall thickness, {post.label}", post.source)
    t_int = Part("t_int", 't_"int"', inter.tdes, f"Intermediate rail design wall thickness, {inter.label}", inter.source)
    base_post = base_metal(registry, "Base metal: post wall fusion face (chord)",
                           tensile_strength(registry, post_grade, post), t_post, sub="BM,post", key="BM_post")
    base_int = base_metal(registry, "Base metal: intermediate rail wall fusion face (branch)",
                          tensile_strength(registry, int_grade, inter), t_int, sub="BM,int", key="BM_int")
    both = registry.get("ej.weld.intermediate_base_metal")
    gov = Sheet(registry)
    # One three-way comparison picks the governing face and prints <, = or > (ADR 0002).
    lower = order(base_int.allow.stated(), base_post.allow.stated())
    if lower.op == "<":  # a tie goes to the post wall, the chord, as Check 3 checks its chord
        base, chk.base_governs = base_int, "intermediate rail wall"
    else:
        base, chk.base_governs = base_post, "post wall"
    gov.decision(lower, f"{chk.base_governs.capitalize()} governs", both.value, cite_ids=(both.id,))
    chord = registry.get("ej.weld.post_wall_chord_intermediate")
    walls = Sheet(registry)
    walls.decision(mtext("Post wall, chord limit states"), "Not checked", chord.value, cite_ids=(chord.id,))
    head = (head_guard + rg.lines + model.lines + limits.lines + wm.lines + kd.lines + base_post.lines
            + base_int.lines + gov.lines + walls.lines)
    ws = WeldLines(
        rg=rg, wm=wm, base=base, head=head,
        k_ds=lambda _sh, _f_r: (None, k_ds),
        base_demand=lambda f: f.f_v,
        base_note=f"Base metal, {chk.base_governs} fusion face (governs): in-plane shear only",
    )
    _min_size(chk, limits)
    for direction in COMPONENT_DIRECTIONS:
        dsh, R, label = _reaction_4b(registry, project, loading, direction)
        sh = Sheet(registry)
        sh.lines.extend(ws.head)
        sh.lines.extend(dsh.lines)
        f = shear_only(sh, rg, R)
        chk.cases.append(_weld_result(sh, ws, f, direction, COMPONENT, label, ""))
    return chk
