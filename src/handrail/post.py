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
    DB, DIRECTIONS, DISTRIBUTED, DOWNWARD, FY_ENTRY, LOAD_TYPES, UPWARD,
    Case, Check, Loading, SectionStop, combo_text, exempt_case, flexural_capacity,
)
from handrail.demand import (
    ASD, HORIZONTAL_KIND, Demand, Given, Wording, demand, live_at_post,
)
from handrail.project import Project
from handrail.registry import Entry, Registry
from handrail.shapes import PipeSection


@dataclass
class PostCase(Case):
    """A Check 5 case, with the values its envelope row prints."""

    Pr: object = None                 # required axial strength (sense gives its direction)
    sense: str = ""                   # "compression" or "tension"
    Mr: object = None                 # required flexural strength; None in the axial-only cases
    P_allow: object = None            # Pc (compression) or Pt (tension)
    M_allow: object = None            # Mc; None in the axial-only cases
    equation: str = ""                # the equation the ratio comes from, as printed
    second_order: float | None = None  # alpha Pr/Pe, moment cases only


# ---------------------------------------------------------------------------
# Check 5 capacity: flexure, compression and tension, each computed once
# ---------------------------------------------------------------------------


@dataclass
class Compression:
    head: list[Line]   # Fy, E and lambda; the flexure block prints these too, so moment cases skip them
    body: list[Line]
    E: Sym
    Lc: Sym
    Lc_line: Line      # the printed L_c line, which the Dimensions page lists
    Pc: Sym
    Pn_entry: Entry    # the equation Pn comes from, named in the envelope's Equation column
    flags: list[str]
    summary_flag: str


def compression_capacity(registry: Registry, project: Project, post: PipeSection) -> Compression:
    """Classify per Table B4.1a and compute Pc per Chapter E. Raises SectionStop."""
    grade = project.post.grade
    head = Sheet(registry)
    Fy = head.code_value("F_y", FY_ENTRY[grade], f"Yield stress, {grade}")
    E = head.code_value("E", "material.steel.E", "Modulus of elasticity")
    # The same D/t line the flexure block prints, so moment cases skip it here.
    head.given("lambda", post.D_t, "lambda = D/t, tabulated (design wall)", DB)

    sh = Sheet(registry)
    lr_e = registry.get("aisc360.B4.1a.round_hss.lambda_r")
    # lambda_(r,c): a moment case also prints the flexure block's lambda_r (Table B4.1b).
    lr = sh.line("lambda_(r,c)", sh.coeff(lr_e.id) * E / Fy, "Slender limit, round HSS in compression")
    D_t = post.D_t
    if D_t > lr.value:
        raise SectionStop(
            f"{post.label}: wall is slender in compression, D/t = {D_t:g} > lambda_r = {lr_e.value}E/Fy = "
            f"{fmt_sig(lr.value)} ({lr_e.cite}). The tool does not check slender sections."
        )
    sh.decision(f"lambda = {D_t:g} <= lambda_(r,c) = {fmt_sig(lr.value)}", "Nonslender",
                "Section classification, compression: no noncompact category",
                cite_ids=("aisc360.B4.1a.classification",))

    K = sh.code_value("K", "aisc360.CA7.K_fixed_free", "Effective length factor, fixed-free (recommended design value)")
    h = sh.given("h", project.post_height.value, "Post height, top of concrete to top rail centerline", "Input")
    Lc = sh.line("L_c", K * h, "Effective length, with the unbraced length taken as the post height h",
                 cite_ids=("aisc360.E2.effective_length", "ej.post.unbraced_length"), unit="inch")
    Lc_line = sh.lines[-1]
    r = sh.given("r", post.r, "Radius of gyration", DB)
    slenderness = sh.line("frac(L_c, r)", Lc / r, "Effective slenderness ratio", cite_ids=("aisc360.eq.E3-4",))

    note_e = registry.get("aisc360.E2.user_note.slenderness")
    limit = registry.get("aisc360.E2.user_note.slenderness.limit").value
    flags, summary_flag = [], ""
    if slenderness.value > limit:
        sh.decision(f"frac(L_c, r) = {fmt_sig(slenderness.value)} > {limit}", "FLAG: exceeds the recommended limit",
                    f"{note_e.value} A recommendation, not a requirement: flagged, and the calc continues.",
                    cite_ids=(note_e.id,))
        flags.append(f"SLENDERNESS: {post.label} Lc/r = {fmt_sig(slenderness.value)} exceeds {limit}, "
                     f"the limit recommended by the {note_e.cite}. Flagged; the calc continues.")
        summary_flag = f"Lc/r = {fmt_sig(slenderness.value)} > {limit}, flagged"
    else:
        sh.decision(f"frac(L_c, r) = {fmt_sig(slenderness.value)} <= {limit}", "Within the recommended limit",
                    note_e.value, cite_ids=(note_e.id,))

    branch = sh.coeff("aisc360.E3.branch_limit") * sqrt(E / Fy)
    lim = sh.line(branch.symbolic(), branch, "Limit between inelastic and elastic buckling")
    Fe = sh.line("F_e", PI**2 * E / slenderness**2, "Elastic buckling stress",
                 cite_ids=("aisc360.eq.E3-4",), unit="ksi")
    # Each branch's equation entry is fetched only on its own branch, so the
    # DRAFT list names only the equation the calc used.
    if slenderness.value <= lim.value:
        e32 = registry.get("aisc360.eq.E3-2")
        sh.decision(f"frac(L_c, r) = {fmt_sig(slenderness.value)} <= {fmt_sig(lim.value)}",
                    f"Inelastic buckling: {e32.equation_number}", "", cite_ids=("aisc360.E3.branch_limit",))
        FyFe = sh.line("frac(F_y, F_e)", Fy / Fe, f"Exponent in {e32.equation_number}", cite_ids=(e32.id,))
        Fcr = sh.line('F_"cr"', sh.coeff("aisc360.eq.E3-2.base") ** FyFe * Fy, "Critical stress",
                      cite_ids=(e32.id,), unit="ksi")
    else:
        e33 = registry.get("aisc360.eq.E3-3")
        sh.decision(f"frac(L_c, r) = {fmt_sig(slenderness.value)} > {fmt_sig(lim.value)}",
                    f"Elastic buckling: {e33.equation_number}", "", cite_ids=("aisc360.E3.branch_limit",))
        Fcr = sh.line('F_"cr"', sh.coeff("aisc360.eq.E3-3.coeff") * Fe, "Critical stress",
                      cite_ids=(e33.id,), unit="ksi")
    A = sh.given("A_g", post.A, "Gross area", DB)
    e31 = registry.get("aisc360.eq.E3-1")
    Pn = sh.line("P_n", Fcr * A, "Nominal compressive strength", cite_ids=(e31.id,), unit="lbf")
    Om = sh.code_value("Omega_c", "aisc360.E1.omega_c", "Safety factor for compression (ASD)")
    Pc = sh.line("P_c", Pn / Om, "Allowable compressive strength", cite_ids=("aisc360.eq.B3-2",), unit="lbf")
    return Compression(head=head.lines, body=sh.lines, E=E, Lc=Lc, Lc_line=Lc_line, Pc=Pc, Pn_entry=e31,
                       flags=flags, summary_flag=summary_flag)


@dataclass
class Tension:
    lines: list[Line]
    Pt: Sym
    Pn_entry: Entry    # the equation Pn comes from, named in the envelope's Equation column


def tension_capacity(registry: Registry, project: Project, post: PipeSection) -> Tension:
    """Tensile yielding on the gross section, §D2(a)."""
    sh = Sheet(registry)
    grade = project.post.grade
    Fy = sh.code_value("F_y", FY_ENTRY[grade], f"Yield stress, {grade}")
    A = sh.given("A_g", post.A, "Gross area", DB)
    d21 = registry.get("aisc360.eq.D2-1")
    Pn = sh.line("P_n", Fy * A, "Nominal tensile strength: yielding on the gross section",
                 cite_ids=(d21.id,), unit="lbf")
    Om = sh.code_value("Omega_t", "aisc360.D2.omega_t", "Safety factor for tension (ASD)")
    Pt = sh.line("P_t", Pn / Om, "Allowable tensile strength", cite_ids=("aisc360.eq.B3-2",), unit="lbf")
    return Tension(lines=sh.lines, Pt=Pt, Pn_entry=d21)


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
# Check 5 cases: capacity, the shared demand (demand.py), and the ratio
# ---------------------------------------------------------------------------

# Check 5 prints required strengths and factors the moment (M_r = 1.0 M_L).
WORDING = Wording(
    where={DOWNWARD: "vertical at the top of the post",
           HORIZONTAL_KIND: "horizontal ({direction}) at the top of the post",
           UPWARD: "upward at the top of the post"},
    axial="P_r",
    axial_notes={DOWNWARD: "Required axial strength, compression; no moment",
                 HORIZONTAL_KIND: "Required axial strength: dead load, compression",
                 UPWARD: "Required axial strength: net tension, guard load opposing dead load"},
    factored="moment", factored_symbol="M_r", factored_note="Required flexural strength",
    moment_symbol="M_L", moment_note="Live-load moment at the top of the baseplate",
    moment_cite="aisc_manual.t3-23.case22.M",
)


def _demand(registry, project, loading, direction, load_type) -> Demand:
    acting_down = ", acting down" if direction == UPWARD else ""
    dead = Given("P_D", loading.P_D, f"D at the post: axial dead load{acting_down}", "Loading")
    arm = Given('L_"post"', loading.L_post, "Cantilever length, h - t_p (critical section at the top of the baseplate)",
                "Loading")
    return demand(registry, project, loading, direction, load_type, ASD, WORDING, dead, arm)


def _downward(registry, project, loading, cap: Capacity5, load_type) -> PostCase:
    sh = Sheet(registry)
    sh.heading("Capacity")
    sh.lines.extend(cap.compression.head + cap.compression.body)
    d = _demand(registry, project, loading, DOWNWARD, load_type)
    sh.lines.extend(d.lines)
    Pr, Pc = d.P, cap.compression.Pc
    ratio = sh.line('"Ratio"', Pr / Pc, "Axial only; Chapter E ratio reported", cite_ids=("aisc360.eq.B3-2",),
                    ratio=True)
    return PostCase(DOWNWARD, load_type, "checked", d.label,
                    demand=Pr.value, capacity=Pc.value, ratio=ratio.value, lines=sh.lines,
                    Pr=Pr.value, sense=d.sense, P_allow=Pc.value,
                    equation=f"Pr/Pc ({cap.compression.Pn_entry.equation_number})")


def _moment_case(registry, project, post, loading, cap: Capacity5, direction, load_type) -> PostCase:
    sh = Sheet(registry)
    comp = cap.compression
    sh.heading("Capacity")
    sh.lines.extend(cap.flexure + comp.body)
    d = _demand(registry, project, loading, direction, load_type)
    sh.lines.extend(d.lines)
    Pr, Mr = d.P, d.M

    # Second-order effects: a ratio and a stop, not an amplifier (plan D1).
    I = sh.given("I", post.I, "Moment of inertia", DB)
    Pe = sh.line("P_e", PI**2 * comp.E * I / comp.Lc**2, "Elastic critical buckling load, at the compression Lc",
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
    sh.decision(f"frac(alpha P_r, P_e) <= {lim.value}",
                sentence.value.format(ratio=fmt_sig(a_ratio.value)), "", cite_ids=(lim.id,))

    Pc, Mc = comp.Pc, cap.Mc
    t = registry.get("aisc360.H1.1.threshold")
    PrPc = sh.line("frac(P_r, P_c)", Pr / Pc, "Axial ratio, selects the interaction equation", cite_ids=(t.id,))
    # Each equation entry is fetched only on its own branch, as for Chapter E.
    if PrPc.value >= t.value:
        eq = registry.get("aisc360.eq.H1-1a")
        sh.decision(f"frac(P_r, P_c) = {fmt_sig(PrPc.value)} >= {t.value}", eq.equation_number, "",
                    cite_ids=(t.id,))
        ratio = sh.line('"Ratio"', PrPc + sh.fraction("aisc360.eq.H1-1a.coeff") * (Mr / Mc),
                        "Combined axial and flexure", cite_ids=(eq.id,), ratio=True)
    else:
        eq = registry.get("aisc360.eq.H1-1b")
        sh.decision(f"frac(P_r, P_c) = {fmt_sig(PrPc.value)} < {t.value}", eq.equation_number, "",
                    cite_ids=(t.id,))
        ratio = sh.line('"Ratio"', Pr / (sh.coeff("aisc360.eq.H1-1b.coeff") * Pc) + Mr / Mc,
                        "Combined axial and flexure", cite_ids=(eq.id,), ratio=True)
    return PostCase(direction, load_type, "checked", d.label,
                    demand=Mr.value, capacity=Mc.value, ratio=ratio.value, lines=sh.lines,
                    Pr=Pr.value, sense=d.sense, Mr=Mr.value, P_allow=Pc.value, M_allow=Mc.value,
                    equation=eq.equation_number,
                    second_order=a_ratio.value)


def _upward(registry, project, loading, cap: Capacity5, load_type) -> PostCase:
    d = _demand(registry, project, loading, UPWARD, load_type)
    if d.P is None:
        return PostCase(UPWARD, load_type, "not checked", d.label, remark=d.remark)
    tension = cap.tension()
    sh = Sheet(registry)
    sh.heading("Capacity")
    sh.lines.extend(tension.lines)
    sh.lines.extend(d.lines)
    Pr = d.P
    ratio = sh.line('"Ratio"', Pr / tension.Pt, "Axial only; Chapter D ratio reported",
                    cite_ids=("aisc360.eq.B3-2",), ratio=True)
    return PostCase(UPWARD, load_type, "checked", d.label,
                    demand=Pr.value, capacity=tension.Pt.value, ratio=ratio.value, lines=sh.lines,
                    Pr=Pr.value, sense=d.sense, P_allow=tension.Pt.value,
                    equation=f"Pr/Pt ({tension.Pn_entry.equation_number})")


def check_5(registry: Registry, project: Project, post: PipeSection, loading: Loading) -> Check:
    cap = _capacity(registry, project, post)
    chk = Check(5, "Post combined axial and flexure", "P_r, M_r", "P_c, M_c", flags=cap.flags,
                summary_flag=cap.compression.summary_flag, derived_lengths=[cap.compression.Lc_line])
    for direction in DIRECTIONS:
        for lt in LOAD_TYPES:
            if lt == DISTRIBUTED and loading.exempt:
                chk.cases.append(exempt_case(registry, direction, PostCase))
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
    V = live_at_post(sh, "V_L", load_type, loading, project, f"horizontal ({direction.lower()}) at the top of the post")
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
                chk.cases.append(exempt_case(registry, direction))
                continue
            chk.cases.append(_deflection_case(registry, project, post, loading, direction, lt))
    return chk
