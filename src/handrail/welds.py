"""The weld ring: one method for both weld checks (docs/brief/welds.md, W1-W12).

A round post welded all around with a fillet weld is a ring of the post's
diameter D. Checks 3 (rail to post) and 7 (post to baseplate) both use it.

- Weld as a line, elastic (W3): L_w = pi D, S_w = pi D^2/4, so forces come
  out per inch of weld. Shear V/L_w is taken as uniform around the ring; the
  axial force P/L_w is uniform; bending M/S_w peaks at the extreme fibers.
- No bearing credit (W10): the weld carries everything, in compression as in
  tension. Both extreme fibers are evaluated and the larger resultant governs.
- At an extreme fiber the weld axis is perpendicular to the plane of bending,
  so theta = 90 deg there. The §J2.4 directional increase k_ds applies on
  round hollow sections only (W2); Check 3 takes k_ds = 1.0.
- Weld metal: F_nw t_e k_ds / Omega per inch. Base metal at a fusion face:
  shear rupture, 0.60 Fu t / Omega per inch (W5, W6). The post wall is
  covered by Check 5 (W5; the Fu/Fy guard is in checks.validate).
- Minimum size per Table J2.4 on the thinner part joined is pass/fail; no
  maximum size is checked (W11).
"""

from __future__ import annotations

from dataclasses import dataclass

from handrail.calc import (PI, Line, Sheet, Sym, absolute, arccos, fmt_quantity, fmt_quantity_plain, maximum,
                           minimum, mtext, sin, sqrt)
from handrail.checks import DB, FEXX_ENTRY, SectionStop, Case
from handrail.dimensions import Dimension
from handrail.registry import Registry
from handrail.shapes import ROUND_HOLLOW, PipeSection
from handrail.units import Q_

LINE_METHOD = "ej.weld.line_method"
NO_BEARING = "ej.weld.no_bearing"
PER_INCH = "lbf/inch"


@dataclass
class WeldCase(Case):
    """A weld check case, with the values its envelope row prints."""

    sense: str = ""            # axial force on the ring: "compression" or "tension"
    f_a: object = None         # axial force per inch
    f_b: object = None         # bending force per inch at the extreme fiber; None without moment
    f_v: object = None         # shear per inch; None without horizontal load
    f_n: object = None         # normal force per inch at the governing fiber
    f_r: object = None         # resultant per inch at the governing fiber
    fiber: str = ""            # "compression side", "tension side" or "uniform"
    theta: object = None       # angle of f_r to the weld axis; None where k_ds is not computed from it
    k_ds: float | None = None
    weld_allow: object = None  # weld metal R_n/Omega per inch
    base_allow: object = None  # base metal R_n/Omega per inch at the checked fusion face
    weld_ratio: float | None = None
    base_ratio: float | None = None  # None when the fusion face sees no force in this case


# ---------------------------------------------------------------------------
# Computed once per check
# ---------------------------------------------------------------------------


@dataclass
class Ring:
    D: Sym
    w: Sym
    L_w: Sym
    S_w: Sym
    t_e: Sym
    lines: list[Line]


def ring(registry: Registry, post: PipeSection, size: Dimension) -> Ring:
    """Line properties of a fillet weld all around the post (W3)."""
    sh = Sheet(registry)
    sh.heading("Weld properties")
    D = sh.given("D", post.OD, f"{post.label}: outside diameter; the weld ring is the post perimeter", DB)
    w = sh.given("w", size.value, f"Fillet weld leg size, all around ({size.entered} as entered)", "Input")
    L_w = sh.line("L_w", PI * D, "Weld length: the post perimeter", cite_ids=(LINE_METHOD,), unit="inch")
    S_w = sh.line("S_w", PI * D**2 / 4, "Section modulus of the ring as a line", cite_ids=(LINE_METHOD,),
                  unit="inch**2")
    t_e = sh.line("t_e", sh.coeff("aisc360.J2.2a.throat.coeff") * w, "Effective throat, equal-leg fillet",
                  cite_ids=("aisc360.J2.2a.throat",), unit="inch")
    return Ring(D=D, w=w, L_w=L_w, S_w=S_w, t_e=t_e, lines=sh.lines)


@dataclass
class Part:
    """A part the weld joins, as printed: symbol, thickness, note, source."""

    symbol: str
    t: object
    note: str
    source: str


@dataclass
class SizeLimits:
    lines: list[Line]
    failure: str  # "" when the weld meets the minimum size


def size_limits(registry: Registry, w: Sym, parts: tuple[Part, Part]) -> SizeLimits:
    """Minimum size per Table J2.4 on the thinner part joined, pass/fail; the
    maximum size along edges does not apply to these T-joints (W11)."""
    sh = Sheet(registry)
    table = registry.get("aisc360.J2.4.min_size")
    sh.heading("Fillet size limits")
    t1, t2 = (sh.given(p.symbol, p.t, p.note, p.source) for p in parts)
    t_min = sh.line('t_"min"', minimum(t1, t2), "Thinner part joined", cite_ids=(table.id,), unit="inch")
    row = next(r for r in table.value if t_min.value <= Q_(r["t_max_in"], "inch"))
    w_min = sh.given('w_"min"', Q_(row["w_min_in"], "inch"), "Minimum fillet size for the thinner part joined",
                     table.cite)
    failure = ""
    if w.value >= w_min.value:
        sh.decision(f"w = {fmt_quantity(w.value)} >= w_\"min\" = {fmt_quantity(w_min.value)}", "OK",
                    "Minimum size", cite_ids=(table.id,))
    else:
        sh.decision(f"w = {fmt_quantity(w.value)} < w_\"min\" = {fmt_quantity(w_min.value)}",
                    "NG: below the minimum size", "Minimum size: the check fails whatever its ratio",
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
    FEXX = sh.code_value('F_"EXX"', FEXX_ENTRY[electrode], f"Electrode classification strength, {electrode}")
    Fnw = sh.line('F_"nw"', sh.coeff("aisc360.J2.5.fnw.coeff") * FEXX, "Nominal stress of the weld metal",
                  cite_ids=("aisc360.J2.5.fnw",), unit="ksi")
    Om = sh.code_value("Omega_w", "aisc360.J2.5.omega_w", "Safety factor, fillet weld (ASD)")
    return WeldMetal(Fnw=Fnw, Om=Om, lines=sh.lines)


@dataclass
class BaseMetal:
    allow: Sym
    lines: list[Line]


def base_metal(registry: Registry, heading: str, Fu_entry: str, Fu_note: str, part: Part) -> BaseMetal:
    """Shear rupture of the base metal at a fusion face, per inch of weld (W5, W6)."""
    sh = Sheet(registry)
    sh.heading(heading)
    Fu = sh.code_value("F_u", Fu_entry, Fu_note)
    t = sh.given(part.symbol, part.t, part.note, part.source)
    R = sh.line('R_(n,"BM")', sh.coeff("aisc360.eq.J4-4.coeff") * Fu * t,
                "Shear rupture at the fusion face, per inch of weld",
                cite_ids=("aisc360.eq.J4-4", "aisc_manual.part9.base_metal"), unit=PER_INCH)
    Om = sh.code_value('Omega_"BM"', "aisc360.J4.2.omega_rupture", "Safety factor, shear rupture (ASD)")
    allow = sh.line('frac(R_(n,"BM"), Omega_"BM")', R / Om, "Allowable base metal strength per inch",
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
    f_a: Sym
    f_b: Sym | None
    f_v: Sym | None
    f_n: Sym
    f_r: Sym
    fiber: str


SIDE = {"compression": '"c"', "tension": '"t"'}


def ring_forces(sh: Sheet, rg: Ring, P: Sym, sense: str, V: Sym | None = None, M: Sym | None = None) -> RingForces:
    """Forces per inch of weld at the governing point of the ring (W3, W10).

    P is the axial force's magnitude and ``sense`` its direction. With a
    moment, the side of bending whose stress has the same sense as P adds
    to it; the other side subtracts. Both are printed and the larger governs.
    """
    f_a = sh.line("f_a", P / rg.L_w, f"Axial force per inch of weld, {sense}, uniform around the ring",
                  cite_ids=(LINE_METHOD,), unit=PER_INCH)
    f_b = None
    if M is None:
        f_n = sh.line("f_n", f_a, "Normal force per inch: no moment, the same at every point of the ring",
                      cite_ids=(NO_BEARING,), unit=PER_INCH)
        fiber = "uniform"
    else:
        f_b = sh.line("f_b", M / rg.S_w, "Bending force per inch at the extreme fiber", cite_ids=(LINE_METHOD,),
                      unit=PER_INCH)
        other = "tension" if sense == "compression" else "compression"
        add = sh.line(f"f_(n,{SIDE[sense]})", f_a + f_b, f"Normal force per inch, {sense} side of bending: "
                      f"axial and bending add", cite_ids=(NO_BEARING,), unit=PER_INCH)
        sub = sh.line(f"f_(n,{SIDE[other]})", absolute(f_a - f_b), f"Normal force per inch, {other} side of bending",
                      cite_ids=(NO_BEARING,), unit=PER_INCH)
        gov, side = (add, sense) if add.value >= sub.value else (sub, other)
        low = sub if gov is add else add
        fiber = f"{side} side"
        sh.decision(f"{gov.typst} = {fmt_quantity(gov.value)} >= {low.typst} = {fmt_quantity(low.value)}",
                    f"{side.capitalize()} side governs", "No bearing credit: both extreme fibers checked",
                    cite_ids=(NO_BEARING,))
        f_n = sh.line("f_n", gov, f"Normal force per inch at the governing fiber, {side} side", unit=PER_INCH)
    if V is None:
        f_v = None
        f_r = sh.line("f_r", f_n, "Resultant per inch: normal force only", cite_ids=(LINE_METHOD,), unit=PER_INCH)
    else:
        f_v = sh.line("f_v", V / rg.L_w, "Shear per inch of weld, taken as uniform around the ring",
                      cite_ids=(LINE_METHOD,), unit=PER_INCH)
        f_r = sh.line("f_r", sqrt(f_n**2 + f_v**2), "Resultant per inch at the governing fiber: vector sum",
                      cite_ids=(LINE_METHOD,), unit=PER_INCH)
    return RingForces(f_a=f_a, f_b=f_b, f_v=f_v, f_n=f_n, f_r=f_r, fiber=fiber)


def directional_increase(sh: Sheet, registry: Registry, f_r: Sym, section: PipeSection) -> tuple[Sym, Sym]:
    """theta at the governing point and k_ds from it, on a round hollow
    section only (W2). Returns (theta, k_ds). Raises SectionStop otherwise."""
    if section.family not in ROUND_HOLLOW:
        raise SectionStop(
            f"{section.label} ({section.family}): the directional strength increase rule for this section "
            f"family has not been drafted. The tool applies the increase only to round hollow sections."
        )
    line_method = registry.get(LINE_METHOD)
    f_par = sh.given("f_parallel", Q_(0, PER_INCH), "Force component along the weld axis: at the extreme "
                     "fiber the weld axis is perpendicular to the plane of bending, and V acts in that plane",
                     line_method.cite)
    theta = sh.line("theta", arccos(f_par / f_r), "Angle between the resultant and the weld axis",
                    cite_ids=("aisc360.eq.J2-5", LINE_METHOD), unit="degree")
    k_ds = sh.line("k_ds", sh.coeff("aisc360.eq.J2-5.base")
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
    R = sh.line("R_n", wm.Fnw * rg.t_e * k_ds, "Nominal fillet weld strength per inch",
                cite_ids=("aisc360.J2.4.fillet_strength",), unit=PER_INCH)
    allow = sh.line("frac(R_n, Omega_w)", R / wm.Om, "Allowable weld metal strength per inch",
                    cite_ids=("aisc360.eq.B3-2",), unit=PER_INCH)
    r_w = sh.line('"Ratio"_w', f_r / allow, "Weld metal: demand / capacity", cite_ids=("aisc360.eq.B3-2",),
                  ratio=True)
    if base_demand is None:
        ratio = sh.line('"Ratio"', r_w, "Weld metal governs: no force on the base metal line in this case",
                        cite_ids=("aisc360.eq.B3-2",), ratio=True)
        return Strength(weld_allow=allow, weld_ratio=r_w, base_ratio=None, ratio=ratio)
    r_bm = sh.line('"Ratio"_"BM"', base_demand / base.allow, base_note, cite_ids=("aisc360.eq.B3-2",), ratio=True)
    ratio = sh.line('"Ratio"', maximum(r_w, r_bm), "The larger of weld metal and base metal",
                    cite_ids=("aisc360.eq.B3-2",), ratio=True)
    return Strength(weld_allow=allow, weld_ratio=r_w, base_ratio=r_bm, ratio=ratio)
