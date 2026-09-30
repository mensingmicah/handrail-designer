"""Checks 5 and 6: the post, over the envelope (docs/plans/slice-2.md).

Check 5 is combined axial and flexure at the critical section, the top of
the baseplate (D4). Check 6 is cantilever deflection over h - t_p.

Both guard loads act at the top of the post: the concentrated load P, and
the distributed load reaching the post as w_L times the span (the tributary
length). They are separate load types, never concurrent.

Direction cases (plan, Envelope):
- Downward: Pr = D + L, compression, no moment. Ratio Pr/Pc (Chapter E, D8).
- Outward, inward, longitudinal: Pr = D, compression; Mr = L (h - t_p).
  §H1.1, plus alpha Pr/Pe against the second-order limit (D1). The three
  are identical for a round post; all are listed so the envelope is explicit.
- Upward: Pr = 1.0L - 0.6D, tension. Ratio Pr/Pt (Chapter D, D8), or no
  net tension when 0.6D >= L.
Check 6 is live load only in the three horizontal cases; downward and
upward are listed as vertical, with no lateral deflection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from handrail.calc import PI, Const, Line, Sheet, Sym, fmt_sig, sqrt
from handrail.checks import (
    COMBO, DB, DIRECTIONS, DISTRIBUTED, FY_ENTRY, LOAD_TYPES, CONCENTRATED,
    Case, Check, Loading, SectionStop, combo_text, flexural_capacity,
)
from handrail.project import Project
from handrail.registry import Registry
from handrail.shapes import PipeSection
from handrail.units import Q_

TRIBUTARY = "Stated assumption: the tributary length is the span"


@dataclass
class PostCase(Case):
    """A Check 5 case, with the values its envelope row prints."""

    Pr: object = None                 # required axial strength (sense gives its direction)
    sense: str = ""                   # "compression" or "tension"
    Mr: object = None                 # required flexural strength; None in the axial-only cases
    equation: str = ""                # the equation the ratio comes from, as printed
    second_order: float | None = None  # alpha Pr/Pe, moment cases only


# ---------------------------------------------------------------------------
# Check 5 capacity: flexure, compression and tension, each computed once
# ---------------------------------------------------------------------------


@dataclass
class Compression:
    head: list[Line]   # Fy and E; the flexure block prints these too, so moment cases skip them
    body: list[Line]
    E: Sym
    Lc: Sym
    Pc: Sym
    flags: list[str]


def compression_capacity(registry: Registry, project: Project, post: PipeSection) -> Compression:
    """Classify per Table B4.1a and compute Pc per Chapter E. Raises SectionStop."""
    grade = project.post.grade
    head = Sheet(registry)
    Fy = head.code_value("F_y", FY_ENTRY[grade], f"Yield stress, {grade}")
    E = head.code_value("E", "material.steel.E", "Modulus of elasticity")

    sh = Sheet(registry)
    lr_e = registry.get("aisc360.B4.1a.round_hss.lambda_r")
    lr = sh.line("lambda_r", sh.coeff(lr_e.id) * E / Fy, "Slender limit, round HSS in compression")
    D_t = post.D_t
    if D_t > lr.value:
        raise SectionStop(
            f"{post.label}: wall is slender in compression, D/t = {D_t:g} > lambda_r = {lr_e.value}E/Fy = "
            f"{fmt_sig(lr.value)} ({lr_e.cite}). The tool does not check slender sections."
        )
    sh.decision(f"lambda = {D_t:g} <= lambda_r = {fmt_sig(lr.value)}", "Nonslender",
                "Section classification, compression: no noncompact category",
                cite_ids=("aisc360.B4.1a.classification",))

    K = sh.code_value("K", "aisc360.CA7.K_fixed_free", "Effective length factor, fixed-free (recommended design value)")
    h = sh.given("h", project.post_height.value, "Post height: L = h for the effective length (plan D3)", "Input")
    Lc = sh.line("L_c", K * h, "Effective length", cite_ids=("aisc360.E2.effective_length",), unit="inch")
    r = sh.given("r", post.r, "Radius of gyration", DB)
    slenderness = sh.line("frac(L_c, r)", Lc / r, "Effective slenderness ratio", cite_ids=("aisc360.eq.E3-4",))

    note_e = registry.get("aisc360.E2.user_note.slenderness")
    limit = registry.get("aisc360.E2.user_note.slenderness.limit").value
    flags = []
    if slenderness.value > limit:
        sh.decision(f"frac(L_c, r) = {fmt_sig(slenderness.value)} > {limit}", "FLAG: exceeds the recommended limit",
                    f"{note_e.value} Flagged; the calc continues (plan D6).", cite_ids=(note_e.id,))
        flags.append(f"SLENDERNESS: {post.label} Lc/r = {fmt_sig(slenderness.value)} exceeds {limit}, "
                     f"the limit recommended by the {note_e.cite}. Flagged; the calc continues.")
    else:
        sh.decision(f"frac(L_c, r) = {fmt_sig(slenderness.value)} <= {limit}", "Within the recommended limit",
                    note_e.value, cite_ids=(note_e.id,))

    branch = sh.coeff("aisc360.E3.branch_limit") * sqrt(E / Fy)
    lim = sh.line(branch.symbolic(), branch, "Limit between inelastic and elastic buckling")
    Fe = sh.line("F_e", PI**2 * E / slenderness**2, "Elastic buckling stress",
                 cite_ids=("aisc360.eq.E3-4",), unit="ksi")
    if slenderness.value <= lim.value:
        sh.decision(f"frac(L_c, r) = {fmt_sig(slenderness.value)} <= {fmt_sig(lim.value)}",
                    "Inelastic buckling: Eq. E3-2", "", cite_ids=("aisc360.E3.branch_limit",))
        Fcr = sh.line('F_"cr"', sh.coeff("aisc360.eq.E3-2.base") ** (Fy / Fe) * Fy, "Critical stress",
                      cite_ids=("aisc360.eq.E3-2",), unit="ksi")
    else:
        sh.decision(f"frac(L_c, r) = {fmt_sig(slenderness.value)} > {fmt_sig(lim.value)}",
                    "Elastic buckling: Eq. E3-3", "", cite_ids=("aisc360.E3.branch_limit",))
        Fcr = sh.line('F_"cr"', sh.coeff("aisc360.eq.E3-3.coeff") * Fe, "Critical stress",
                      cite_ids=("aisc360.eq.E3-3",), unit="ksi")
    A = sh.given("A_g", post.A, "Gross area", DB)
    Pn = sh.line("P_n", Fcr * A, "Nominal compressive strength", cite_ids=("aisc360.eq.E3-1",), unit="lbf")
    Om = sh.code_value("Omega_c", "aisc360.E1.omega_c", "Safety factor for compression (ASD)")
    Pc = sh.line("P_c", Pn / Om, "Allowable compressive strength", cite_ids=("aisc360.eq.B3-2",), unit="lbf")
    return Compression(head=head.lines, body=sh.lines, E=E, Lc=Lc, Pc=Pc, flags=flags)


@dataclass
class Tension:
    lines: list[Line]
    Pt: Sym


def tension_capacity(registry: Registry, project: Project, post: PipeSection) -> Tension:
    """Tensile yielding on the gross section, §D2(a)."""
    sh = Sheet(registry)
    grade = project.post.grade
    Fy = sh.code_value("F_y", FY_ENTRY[grade], f"Yield stress, {grade}")
    A = sh.given("A_g", post.A, "Gross area", DB)
    Pn = sh.line("P_n", Fy * A, "Nominal tensile strength: yielding on the gross section",
                 cite_ids=("aisc360.eq.D2-1",), unit="lbf")
    Om = sh.code_value("Omega_t", "aisc360.D2.omega_t", "Safety factor for tension (ASD)")
    Pt = sh.line("P_t", Pn / Om, "Allowable tensile strength", cite_ids=("aisc360.eq.B3-2",), unit="lbf")
    return Tension(lines=sh.lines, Pt=Pt)


@dataclass
class Capacity5:
    flexure: list[Line]
    Mc: Sym
    compression: Compression
    tension: Callable[[], Tension]  # computed on first use, so an unused §D2 is not listed as used
    flags: list[str] = field(default_factory=list)


def _capacity(registry: Registry, project: Project, post: PipeSection) -> Capacity5:
    flex = flexural_capacity(registry, post, project.post.grade)
    sh = Sheet(registry)
    sh.lines.extend(flex.lines)
    Mc = sh.line("M_c", flex.allow, "Allowable flexural strength, as used in Chapter H",
                 cite_ids=("aisc360.eq.B3-2",), unit="lbf*inch")
    comp = compression_capacity(registry, project, post)
    cache: list[Tension] = []

    def tension() -> Tension:
        if not cache:
            cache.append(tension_capacity(registry, project, post))
        return cache[0]

    return Capacity5(flexure=sh.lines, Mc=Mc, compression=comp, tension=tension,
                     flags=flex.flags + comp.flags)


# ---------------------------------------------------------------------------
# Check 5 demand, per case
# ---------------------------------------------------------------------------


def _live_at_post(sh: Sheet, symbol: str, load_type: str, loading: Loading, project: Project, where: str) -> Sym:
    """The guard load reaching the top of the post: P, or w_L over the tributary length."""
    if load_type == CONCENTRATED:
        return sh.given(symbol, loading.P, f"Concentrated guard load P, {where}", "Loading")
    w = sh.given("w_L", loading.w_L, "Uniform guard load", "Loading")
    L = sh.given("L", project.span.value, "Span: the tributary length for the post", "Input")
    return sh.line(symbol, w * L, f"Uniform guard load collected over the span, {where}", cite=TRIBUTARY, unit="lbf")


def _downward(registry, project, loading, cap: Capacity5, load_type) -> PostCase:
    sh = Sheet(registry)
    sh.heading("Capacity")
    sh.lines.extend(cap.compression.head + cap.compression.body)
    sh.heading(f"Demand: downward, {load_type.lower()} load")
    combo = registry.get(COMBO)
    PD = sh.given("P_D", loading.P_D, "D at the post: axial dead load", "Loading")
    PL = _live_at_post(sh, "P_L", load_type, loading, project, "vertical at the top of the post")
    Pr = sh.line("P_r", sh.factor(combo.id, "D") * PD + sh.factor(combo.id, "L") * PL,
                 "Required axial strength, compression; no moment", unit="lbf")
    Pc = cap.compression.Pc
    ratio = sh.line('"Ratio"', Pr / Pc, "Axial only; Chapter E ratio reported", cite_ids=("aisc360.eq.B3-2",),
                    ratio=True)
    return PostCase("Downward", load_type, "checked", f"{combo_text(combo)}, axial\n{combo.cite}",
                    demand=Pr.value, capacity=Pc.value, ratio=ratio.value, lines=sh.lines,
                    Pr=Pr.value, sense="compression", equation="Pr/Pc (Ch. E)")


def _moment_case(registry, project, post, loading, cap: Capacity5, direction, load_type) -> PostCase:
    sh = Sheet(registry)
    comp = cap.compression
    sh.heading("Capacity")
    sh.lines.extend(cap.flexure + comp.body)
    sh.heading(f"Demand: {direction.lower()}, {load_type.lower()} load")
    combo = registry.get(COMBO)
    PD = sh.given("P_D", loading.P_D, "D at the post: axial dead load", "Loading")
    Pr = sh.line("P_r", sh.factor(combo.id, "D") * PD, "Required axial strength: dead load, compression",
                 unit="lbf")
    V = _live_at_post(sh, "V_L", load_type, loading, project, f"horizontal ({direction.lower()}) at the top of the post")
    Lp = sh.given('L_"post"', loading.L_post, "Cantilever length, h - t_p (critical section at the top of the baseplate)",
                  "Loading")
    ML = sh.line("M_L", V * Lp, "Live-load moment at the top of the baseplate",
                 cite_ids=("aisc_manual.t3-23.case22.M",), unit="lbf*inch")
    Mr = sh.line("M_r", sh.factor(combo.id, "L") * ML, "Required flexural strength", unit="lbf*inch")

    # Second-order effects: a ratio and a stop, not an amplifier (plan D1).
    I = sh.given("I", post.I, "Moment of inertia", DB)
    Pe = sh.line("P_e", PI**2 * comp.E * I / comp.Lc**2, "Elastic critical buckling load, Lc = K h",
                 cite_ids=("aisc360.eq.A-8-5", "ej.second_order.pe_length"), unit="lbf")
    alpha = sh.coeff("aisc360.app8.alpha_asd")
    a_ratio = sh.line("frac(alpha P_r, P_e)", alpha * Pr / Pe, "Second-order ratio")
    lim = registry.get("ej.second_order.limit")
    label = f"{direction}, {load_type.lower()}"
    if a_ratio.value > lim.value:
        raise SectionStop(
            f"Second-order effects are not negligible in the {label.lower()} case of Check 5: "
            f"alpha Pr/Pe = {fmt_sig(a_ratio.value)} > {lim.value} ({lim.cite}). "
            f"The tool does not amplify for second-order effects."
        )
    sentence = registry.get("ej.second_order.negligible")
    sh.decision(f"frac(alpha P_r, P_e) = {fmt_sig(a_ratio.value)} <= {lim.value}",
                sentence.value.format(ratio=fmt_sig(a_ratio.value)), "", cite_ids=(lim.id, sentence.id))

    Pc, Mc = comp.Pc, cap.Mc
    PrPc = sh.line("frac(P_r, P_c)", Pr / Pc, "Axial ratio, selects the interaction equation")
    t = registry.get("aisc360.H1.1.threshold")
    if PrPc.value >= t.value:
        sh.decision(f"frac(P_r, P_c) = {fmt_sig(PrPc.value)} >= {t.value}", "Eq. H1-1a", "", cite_ids=(t.id,))
        ratio = sh.line('"Ratio"', PrPc + sh.fraction("aisc360.eq.H1-1a.coeff") * (Mr / Mc),
                        "Combined axial and flexure", cite_ids=("aisc360.eq.H1-1a",), ratio=True)
        equation = "H1-1a"
    else:
        sh.decision(f"frac(P_r, P_c) = {fmt_sig(PrPc.value)} < {t.value}", "Eq. H1-1b", "", cite_ids=(t.id,))
        ratio = sh.line('"Ratio"', Pr / (sh.coeff("aisc360.eq.H1-1b.coeff") * Pc) + Mr / Mc,
                        "Combined axial and flexure", cite_ids=("aisc360.eq.H1-1b",), ratio=True)
        equation = "H1-1b"
    axes = {"D": "axial", "L": "horizontal"}
    return PostCase(direction, load_type, "checked", f"{combo_text(combo, axes, ', ')}\n{combo.cite}",
                    demand=Mr.value, capacity=Mc.value, ratio=ratio.value, lines=sh.lines,
                    Pr=Pr.value, sense="compression", Mr=Mr.value, equation=f"Eq. {equation}",
                    second_order=a_ratio.value)


def _upward(registry, project, loading, cap: Capacity5, load_type) -> PostCase:
    sh = Sheet(registry)
    combo = registry.get("ej.combo.bending.upward")
    label = f"{combo_text(combo)}, net axial\n{combo.cite}"
    demand = Sheet(registry)
    demand.heading(f"Demand: upward, {load_type.lower()} load")
    PD = demand.given("P_D", loading.P_D, "D at the post: axial dead load, acting down", "Loading")
    PL = _live_at_post(demand, "P_L", load_type, loading, project, "upward at the top of the post")
    # One expression gives both the printed value and the decision (ADR 0002).
    net = demand.factor(combo.id, "L") * PL - demand.factor(combo.id, "D") * PD
    if not net.eval() > Q_(0, "lbf"):
        return PostCase("Upward", load_type, "not checked", label,
                        remark="No net tension (0.6D >= L); compression covered by downward")
    tension = cap.tension()
    sh.heading("Capacity")
    sh.lines.extend(tension.lines)
    sh.lines.extend(demand.lines)
    Pr = sh.line("P_r", net, "Required axial strength: net tension, guard load opposing dead load", unit="lbf")
    ratio = sh.line('"Ratio"', Pr / tension.Pt, "Axial only; Chapter D ratio reported",
                    cite_ids=("aisc360.eq.B3-2",), ratio=True)
    return PostCase("Upward", load_type, "checked", label,
                    demand=Pr.value, capacity=tension.Pt.value, ratio=ratio.value, lines=sh.lines,
                    Pr=Pr.value, sense="tension", equation="Pr/Pt (Ch. D)")


def check_5(registry: Registry, project: Project, post: PipeSection, loading: Loading) -> Check:
    cap = _capacity(registry, project, post)
    chk = Check(5, "Post combined axial and flexure", "P_r, M_r", "P_c, M_c", flags=cap.flags)
    for direction in DIRECTIONS:
        for lt in LOAD_TYPES:
            if lt == DISTRIBUTED and loading.exempt:
                exemption = registry.get("asce7.guard.uniform.exemption.intro")
                chk.cases.append(PostCase(direction, lt, "exempt",
                                          remark=f"Uniform load not considered ({exemption.cite})"))
            elif direction == "Downward":
                chk.cases.append(_downward(registry, project, loading, cap, lt))
            elif direction == "Upward":
                chk.cases.append(_upward(registry, project, loading, cap, lt))
            else:
                chk.cases.append(_moment_case(registry, project, post, loading, cap, direction, lt))
    return chk


# ---------------------------------------------------------------------------
# Check 6: cantilever deflection, live load only, horizontal cases
# ---------------------------------------------------------------------------


def _deflection_case(registry, project, post, loading, direction, load_type) -> Case:
    sh = Sheet(registry)
    combo = registry.get("ej.combo.deflection.L_only")
    Lp = sh.given('L_"post"', loading.L_post, "Cantilever length, h - t_p", "Loading")
    E = sh.code_value("E", "material.steel.E", "Modulus of elasticity")
    I = sh.given("I", post.I, "Moment of inertia", DB)
    V = _live_at_post(sh, "V_L", load_type, loading, project, f"horizontal ({direction.lower()}) at the top of the post")
    DL = sh.line("Delta_L", V * Lp**3 / (3 * E * I), "Live-load deflection at the top of the post",
                 cite_ids=("aisc_manual.t3-23.case22.delta",), unit="inch")
    D = sh.line("Delta", sh.factor(combo.id, "L") * DL, "Live load only; dead load acts axially", unit="inch")
    r = project.post_deflection.ratio
    lim = Const(int(r) if float(r).is_integer() else r)
    Dallow = sh.line('Delta_"allow"', Lp / lim, f"Limit (h - t_p)/{lim.value}",
                     cite_ids=("ej.deflection.limit.post",), unit="inch")
    ratio = sh.line('"Ratio"', D / Dallow, "Deflection / limit", cite_ids=("ej.deflection.limit.post",), ratio=True)
    return Case(direction, load_type, "checked", f"{combo_text(combo)}, horizontal\n{combo.cite}",
                demand=D.value, capacity=Dallow.value, ratio=ratio.value, lines=sh.lines)


def check_6(registry: Registry, project: Project, post: PipeSection, loading: Loading) -> Check:
    chk = Check(6, "Post deflection", "Delta", 'Delta_"allow"')
    if project.post_deflection.bypass:
        chk.bypassed = True
        return chk
    for direction in DIRECTIONS:
        if direction in ("Downward", "Upward"):
            chk.cases.append(Case(direction, None, "not checked",
                                  remark="Vertical load: no lateral deflection of the post"))
            continue
        for lt in LOAD_TYPES:
            if lt == DISTRIBUTED and loading.exempt:
                exemption = registry.get("asce7.guard.uniform.exemption.intro")
                chk.cases.append(Case(direction, lt, "exempt",
                                      remark=f"Uniform load not considered ({exemption.cite})"))
                continue
            chk.cases.append(_deflection_case(registry, project, post, loading, direction, lt))
    return chk
