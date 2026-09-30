"""Checks 1 and 2: top rail bending and top rail deflection, over the envelope.

Every direction case and load type is computed and kept (the envelope table
lists them all); only the controlling case's calc lines are printed in full
(docs/plans/slice-1.md, D2).

Load types: the concentrated load P at midspan and the distributed load w
are separate and never concurrent (ASCE 7-22 §4.5.1.1).

Direction cases (docs/BRIEF.md, decisions; slice 1 plan):
- Downward: D + L on the vertical axis.
- Outward, inward: D on the vertical axis, L on the horizontal axis. Bending
  combines them by SRSS against one capacity, exact for a round section.
  Deflection is L only, on the horizontal axis. Both are listed although
  they are identical for a round section, so the envelope is explicit.
- Upward: bending 0.6D + 1.0L, net on the vertical axis (engineering
  judgement); deflection L only.
- Longitudinal: the rail carries it axially; listed, not checked.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from handrail.calc import Const, Line, Sheet, Sym, absolute, fmt_quantity_plain, fmt_sig, minimum, mtext, sqrt
from handrail.project import Member, Project, ProjectError
from handrail.registry import Entry, Registry
from handrail.shapes import PipeSection
from handrail.units import Q_

DIRECTIONS = ("Downward", "Outward", "Inward", "Upward", "Longitudinal")
CONCENTRATED, DISTRIBUTED = "Concentrated", "Distributed"
LOAD_TYPES = (CONCENTRATED, DISTRIBUTED)

DB = "AISC Shapes Database v16.0"
COMBO = "asce7.combo.asd.D_plus_L"

# Fy entry for each grade this slice supports.
FY_ENTRY = {"A53 Gr B": "material.A53_GrB.Fy"}


class SectionStop(Exception):
    """A hard stop: the tool will not check this section (slender, or out of range)."""


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------


@dataclass
class Case:
    direction: str
    load_type: str | None
    status: str  # "checked", "exempt", "not checked"
    combination: str = ""
    demand: object = None
    capacity: object = None
    ratio: float | None = None
    lines: list[Line] = field(default_factory=list)
    remark: str = ""

    @property
    def label(self) -> str:
        return f"{self.direction}, {self.load_type.lower()}" if self.load_type else self.direction


@dataclass
class Check:
    number: int
    title: str
    demand_label: str    # Typst math
    capacity_label: str  # Typst math
    cases: list[Case] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    bypassed: bool = False

    @property
    def checked(self) -> list[Case]:
        return [c for c in self.cases if c.status == "checked"]

    @property
    def controlling(self) -> Case | None:
        # Highest ratio; ties go to the first case in envelope order.
        best = None
        for c in self.checked:
            if best is None or c.ratio > best.ratio:
                best = c
        return best

    @property
    def ok(self) -> bool:
        return self.bypassed or self.controlling.ratio <= 1.0

    @property
    def verdict(self) -> str:
        if self.bypassed:
            return "Bypassed by engineer"
        return "OK" if self.ok else "NG"


@dataclass
class Loading:
    P: object          # concentrated guard load
    w_L: object        # uniform guard load, or None when exempt
    w_D: object        # top rail self-weight
    exempt: bool
    exemption_statement: str
    lines: list[Line]


@dataclass
class Results:
    project: Project
    rail: PipeSection
    loading: Loading
    section_lines: list[Line]
    checks: list[Check]


# ---------------------------------------------------------------------------
# Material, loading, section properties
# ---------------------------------------------------------------------------


def require_supported_grade(member: Member) -> None:
    """Refuse a grade this slice has no Fy entry for.

    The brief's unusual-pairing warning (a grade outside the shape's standard
    list) returns when a slice accepts more than one grade; with A53 Gr B the
    only grade allowed, it could never fire.
    """
    if member.grade not in FY_ENTRY:
        raise ProjectError(
            f"top rail grade {member.grade!r}: slice 1 supports {', '.join(FY_ENTRY)} only"
        )


def build_loading(project: Project, registry: Registry, rail: PipeSection) -> Loading:
    sh = Sheet(registry)
    ld = project.loads

    code_P = registry.get("asce7.guard.concentrated")
    if ld.concentrated is None:
        P = sh.code_value("P", code_P.id, "Concentrated guard load, any direction, any point on the top rail")
    else:
        P = sh.input(
            "P", ld.concentrated,
            f"Concentrated guard load, engineer override (code value {fmt_quantity_plain(code_P.quantity)})",
            cite=f"Input; {code_P.cite}",
        )

    code_w = registry.get("asce7.guard.uniform")
    if ld.uniform_exempt:
        sh.decision(
            "w_L", "Not considered",
            f"Uniform guard load exempted by the engineer: {ld.exemption_statement}",
            cite=registry.get("asce7.guard.uniform.exemption.intro").cite,
        )
        w_L = None
    elif ld.uniform is None:
        w_L = sh.code_value("w_L", code_w.id, f"Uniform guard load, {code_w.value} lb/ft, any direction; "
                            "not concurrent with P").value
    else:
        w_L = sh.input(
            "w_L", ld.uniform,
            f"Uniform guard load, engineer override: {ld.uniform.m_as('lbf/ft'):g} lb/ft "
            f"(code value {code_w.quantity.m_as('lbf/ft'):g} lb/ft)",
            cite=f"Input; {code_w.cite}",
        ).value

    w_D = sh.given("w_D", rail.W, f"Top rail self-weight: tabulated W = {rail.W.m_as('lbf/ft'):g} lb/ft", DB).value
    return Loading(P=P.value, w_L=w_L, w_D=w_D, exempt=ld.uniform_exempt,
                   exemption_statement=ld.exemption_statement, lines=sh.lines)


def section_lines(registry: Registry, rail: PipeSection) -> list[Line]:
    sh = Sheet(registry)
    sh.given("D", rail.OD, f"{rail.label}: outside diameter", DB)
    sh.given('t_"nom"', rail.tnom, "Nominal wall thickness", DB)
    sh.given('t_"des"', rail.tdes, "Design wall thickness", DB)
    sh.given("A", rail.A, "Area (design wall)", DB)
    sh.given("W", rail.W, f"Nominal weight: tabulated {rail.W.m_as('lbf/ft'):g} lb/ft (nominal wall)", DB)
    sh.given("I", rail.I, "Moment of inertia", DB)
    sh.given("S", rail.S, "Elastic section modulus", DB)
    sh.given("Z", rail.Z, "Plastic section modulus", DB)
    sh.given("D slash t", rail.D_t, "Diameter-to-thickness ratio, tabulated", DB)
    return sh.lines


# ---------------------------------------------------------------------------
# Check 1: flexural capacity (AISC 360-22 §F8) and demand
# ---------------------------------------------------------------------------


@dataclass
class Capacity:
    """Allowable flexural strength, computed once and shared by every case."""

    allow: Sym          # M_n/Omega_b, as a symbol the demand lines divide by
    lines: list[Line]   # printed at the head of the controlling case
    flags: list[str]


def flexural_capacity(registry: Registry, rail: PipeSection, grade: str) -> Capacity:
    """Classify the section and compute M_n/Omega_b. Raises SectionStop.

    Every coefficient and citation in the printed lines and the stop
    messages is read from its registry entry (CLAUDE.md rule 1).
    """
    sh = Sheet(registry)
    app = registry.get("aisc360.F8.applicability")
    lp_e = registry.get("aisc360.B4.1b.round_hss.lambda_p")
    lr_e = registry.get("aisc360.B4.1b.round_hss.lambda_r")
    f82 = registry.get("aisc360.eq.F8-2")

    sh.decision(
        mtext(f"{rail.label}, {grade}"), "Designed as round HSS",
        "Pipe is designed under the round HSS provisions",
        cite_ids=("aisc360.pipe_as_round_hss",),
    )
    Fy = sh.code_value("F_y", FY_ENTRY[grade], f"Yield stress, {grade}")
    E = sh.code_value("E", "material.steel.E", "Modulus of elasticity")
    lam = sh.given("lambda", rail.D_t, "lambda = D/t, tabulated (design wall)", DB)
    lim = sh.line("lambda_\"lim\"", sh.coeff(app.id) * E / Fy, "Applicability limit on D/t")
    lp = sh.line("lambda_p", sh.coeff(lp_e.id) * E / Fy, "Compact limit, round HSS in flexure")
    lr = sh.line("lambda_r", sh.coeff(lr_e.id) * E / Fy, "Noncompact limit, round HSS in flexure")

    D_t, name = rail.D_t, rail.label
    if not D_t < lim.value:
        raise SectionStop(
            f"{name}: D/t = {D_t:g} is not less than the {app.cite} limit "
            f"{app.value}E/Fy = {fmt_sig(lim.value)}. The tool does not check this section."
        )
    if D_t > lr.value:
        raise SectionStop(
            f"{name}: wall is slender in flexure, D/t = {D_t:g} > lambda_r = {lr_e.value}E/Fy = "
            f"{fmt_sig(lr.value)} ({lr_e.cite}). The tool does not check slender sections."
        )
    sh.decision(
        f"lambda = {D_t:g} < lambda_\"lim\" = {fmt_sig(lim.value)}", "Applies",
        "Applicability", cite_ids=(app.id,),
    )

    Z = sh.given("Z", rail.Z, "Plastic section modulus", DB)
    Mp = sh.line("M_p", Fy * Z, "Plastic moment (yielding)", cite_ids=("aisc360.eq.F8-1",),
                 unit="lbf*inch")
    flags = []
    if D_t <= lp.value:
        sh.decision(f"lambda = {D_t:g} <= lambda_p = {fmt_sig(lp.value)}", "Compact",
                    "Section classification", cite_ids=("aisc360.B4.1b.classification",))
        sh.decision(mtext("Compact wall"), "Local buckling does not apply",
                    "", cite_ids=("aisc360.F8.nominal_strength",))
        Mn = sh.line("M_n", Mp, "Nominal flexural strength", cite_ids=("aisc360.F8.nominal_strength",),
                     unit="lbf*inch")
    else:
        sh.decision(f"lambda_p = {fmt_sig(lp.value)} < lambda = {D_t:g} <= lambda_r = {fmt_sig(lr.value)}",
                    "NONCOMPACT", "Section classification: reduced capacity",
                    cite_ids=("aisc360.B4.1b.classification",))
        flags.append(
            f"NONCOMPACT: {name} D/t = {D_t:g} exceeds lambda_p = {fmt_sig(lp.value)} "
            f"(lambda_r = {fmt_sig(lr.value)}); Mn reduced by local buckling, {f82.cite}."
        )
        S = sh.given("S", rail.S, "Elastic section modulus", DB)
        Mlb = sh.line("M_(n,\"LB\")", (sh.coeff("aisc360.eq.F8-2.coeff") * E / lam + Fy) * S,
                      "Local buckling, noncompact wall", cite_ids=(f82.id,), unit="lbf*inch")
        Mn = sh.line("M_n", minimum(Mp, Mlb), "Lower of yielding and local buckling",
                     cite_ids=("aisc360.F8.nominal_strength",), unit="lbf*inch")
    Om = sh.code_value("Omega_b", "aisc360.F1.omega_b", "Safety factor for flexure (ASD)")
    Ma = sh.line("M_n / Omega_b", Mn / Om, "Allowable flexural strength",
                 cite_ids=("aisc360.eq.B3-2",), unit="lbf*inch")
    return Capacity(allow=Ma, lines=sh.lines, flags=flags)


def _live_moment(sh: Sheet, load_type: str, L: Sym, loading: Loading) -> Sym:
    if load_type == CONCENTRATED:
        P = sh.given("P", loading.P, "Concentrated guard load at midspan", "Loading")
        return sh.line("M_L", P * L / 4, "Live-load moment, midspan",
                       cite_ids=("aisc_manual.t3-23.case7.M",), unit="lbf*inch")
    w = sh.given("w_L", loading.w_L, "Uniform guard load", "Loading")
    return sh.line("M_L", w * L**2 / 8, "Live-load moment, midspan",
                   cite_ids=("aisc_manual.t3-23.case1.M",), unit="lbf*inch")


def combo_text(entry: Entry, axes: dict[str, str] | None = None, joiner: str = " + ") -> str:
    """Combination label generated from the factors the expression uses: '0.6D + 1.0L'.

    With ``axes`` ({"D": "vertical", "L": "horizontal"}), each term carries its axis.
    """
    terms = []
    for load, factor in entry.value.items():
        term = f"{float(factor)!r}{load}"
        terms.append(f"{term} {axes[load]}" if axes else term)
    return joiner.join(terms)


def _bending_case(registry, project, rail, loading, cap: Capacity, direction, load_type) -> Case:
    sh = Sheet(registry)
    sh.heading("Capacity")
    sh.lines.extend(cap.lines)
    Ma_allow = cap.allow
    sh.heading(f"Demand: {direction.lower()}, {load_type.lower()} load")
    L = sh.given("L", project.span.value, "Span, simple beam", "Input")
    wD = sh.given("w_D", loading.w_D, "Top rail self-weight", "Loading")
    MD = sh.line("M_D", wD * L**2 / 8, "Dead-load moment, midspan",
                 cite_ids=("aisc_manual.t3-23.case1.M",), unit="lbf*inch")
    ML = _live_moment(sh, load_type, L, loading)

    if direction == "Downward":
        combo = registry.get(COMBO)
        M = sh.line("M_a", sh.factor(combo.id, "D") * MD + sh.factor(combo.id, "L") * ML,
                    "Required flexural strength: D and L on the same axis", unit="lbf*inch")
        label = f"{combo_text(combo)}, vertical\n{combo.cite}"
    elif direction in ("Outward", "Inward"):
        combo, srss = registry.get(COMBO), registry.get("ej.bending.srss_round")
        Mv = sh.line("M_(a,v)", sh.factor(combo.id, "D") * MD, "Vertical axis: dead load", unit="lbf*inch")
        Mh = sh.line("M_(a,h)", sh.factor(combo.id, "L") * ML, f"Horizontal axis: guard load {direction.lower()}",
                     unit="lbf*inch")
        M = sh.line("M_a", sqrt(Mv**2 + Mh**2),
                    "Resultant moment: exact for a round section, one capacity",
                    cite_ids=(srss.id,), unit="lbf*inch")
        label = (f"{combo_text(combo, {'D': 'vertical', 'L': 'horizontal'}, ', ')}, SRSS\n"
                 f"{combo.cite}; {srss.cite}")
    else:  # Upward
        combo = registry.get("ej.combo.bending.upward")
        fD, fL = sh.factor(combo.id, "D"), sh.factor(combo.id, "L")
        net = fD.value * MD.value - fL.value * ML.value  # dead load acts down, guard load up
        sense = "net upward" if net < 0 else "net downward"
        M = sh.line("M_a", absolute(fD * MD - fL * ML),
                    f"Net vertical moment, guard load opposing dead load: {sense}", unit="lbf*inch")
        label = f"{combo_text(combo)}, net vertical\n{combo.cite}"

    ratio = sh.line('"Ratio"', M / Ma_allow, "Demand / capacity", cite_ids=("aisc360.eq.B3-2",), ratio=True)
    return Case(direction, load_type, "checked", label,
                demand=M.value, capacity=Ma_allow.value, ratio=ratio.value, lines=sh.lines)


# ---------------------------------------------------------------------------
# Check 2: deflection
# ---------------------------------------------------------------------------


def _deflection_case(registry, project, rail, loading, direction, load_type) -> Case:
    sh = Sheet(registry)
    L = sh.given("L", project.span.value, "Span, simple beam", "Input")
    E = sh.code_value("E", "material.steel.E", "Modulus of elasticity")
    I = sh.given("I", rail.I, "Moment of inertia", DB)
    if load_type == CONCENTRATED:
        P = sh.given("P", loading.P, "Concentrated guard load at midspan", "Loading")
        DL = sh.line("Delta_L", P * L**3 / (48 * E * I), "Live-load deflection, midspan",
                     cite_ids=("aisc_manual.t3-23.case7.delta",), unit="inch")
    else:
        w = sh.given("w_L", loading.w_L, "Uniform guard load", "Loading")
        DL = sh.line("Delta_L", 5 * w * L**4 / (384 * E * I), "Live-load deflection, midspan",
                     cite_ids=("aisc_manual.t3-23.case1.delta",), unit="inch")
    if direction == "Downward":
        combo = registry.get("ej.combo.deflection.D_plus_L")
        wD = sh.given("w_D", loading.w_D, "Top rail self-weight", "Loading")
        DD = sh.line("Delta_D", 5 * wD * L**4 / (384 * E * I), "Dead-load deflection, midspan",
                     cite_ids=("aisc_manual.t3-23.case1.delta",), unit="inch")
        D = sh.line("Delta", sh.factor(combo.id, "D") * DD + sh.factor(combo.id, "L") * DL,
                    "D and L on the same (vertical) axis", unit="inch")
        axis = "vertical"
    else:
        combo = registry.get("ej.combo.deflection.L_only")
        note = "Live load only" + (": opposes dead load, dead load not credited" if direction == "Upward" else "")
        D = sh.line("Delta", sh.factor(combo.id, "L") * DL, note, unit="inch")
        axis = "vertical" if direction == "Upward" else "horizontal"
    label = f"{combo_text(combo)}, {axis}\n{combo.cite}"

    r = project.rail_deflection.ratio
    lim = Const(int(r) if float(r).is_integer() else r)
    Dallow = sh.line('Delta_"allow"', L / lim, f"Limit L/{lim.value}",
                     cite_ids=("ej.deflection.limit",), unit="inch")
    ratio = sh.line('"Ratio"', D / Dallow, "Deflection / limit", cite_ids=("ej.deflection.limit",), ratio=True)
    return Case(direction, load_type, "checked", label,
                demand=D.value, capacity=Dallow.value, ratio=ratio.value, lines=sh.lines)


# ---------------------------------------------------------------------------
# Envelope
# ---------------------------------------------------------------------------


def _envelope(case_fn, registry, project, rail, loading) -> list[Case]:
    cases = []
    for direction in DIRECTIONS:
        if direction == "Longitudinal":
            cases.append(Case(direction, None, "not checked",
                              remark="Rail carries the longitudinal load axially; not checked"))
            continue
        for lt in LOAD_TYPES:
            if lt == DISTRIBUTED and loading.exempt:
                exemption = registry.get("asce7.guard.uniform.exemption.intro")
                cases.append(Case(direction, lt, "exempt",
                                  remark=f"Uniform load not considered ({exemption.cite})"))
                continue
            cases.append(case_fn(registry, project, rail, loading, direction, lt))
    return cases


def check_1(registry, project, rail, loading) -> Check:
    cap = flexural_capacity(registry, rail, project.top_rail.grade)
    chk = Check(1, "Top rail bending", "M_a", "M_n / Omega_b", flags=cap.flags)

    def case(registry, project, rail, loading, direction, load_type):
        return _bending_case(registry, project, rail, loading, cap, direction, load_type)

    chk.cases = _envelope(case, registry, project, rail, loading)
    return chk


def check_2(registry, project, rail, loading) -> Check:
    chk = Check(2, "Top rail deflection", "Delta", 'Delta_"allow"')
    if project.rail_deflection.bypass:
        chk.bypassed = True
        return chk
    chk.cases = _envelope(_deflection_case, registry, project, rail, loading)
    return chk


def run(project: Project, registry: Registry) -> Results:
    from handrail import shapes

    rail = shapes.pipe(project.top_rail.section)
    require_supported_grade(project.top_rail)
    loading = build_loading(project, registry, rail)
    props = section_lines(registry, rail)
    checks = [check_1(registry, project, rail, loading), check_2(registry, project, rail, loading)]
    return Results(project, rail, loading, props, checks)
