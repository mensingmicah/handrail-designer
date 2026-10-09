"""Checks 1 and 2: top rail bending and top rail deflection, over the envelope.

Every direction case and load type is computed and kept (the envelope table
lists them all); only the controlling case's calc lines are printed in full
(docs/plans/slice-1.md, D2).

Load types: the concentrated load P at midspan and the distributed load w
are separate and never concurrent (ASCE 7-22 §4.5.1.1).

Direction cases (docs/brief/loads-and-envelope.md; slice 1 plan):
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
from handrail.errors import InputError
from handrail.project import SAME_AS_TOP, Member, Project, ProjectError
from handrail.registry import Entry, Registry
from handrail.shapes import PipeSection
from handrail.units import Q_

DIRECTIONS = ("Downward", "Outward", "Inward", "Upward", "Longitudinal")
CONCENTRATED, DISTRIBUTED = "Concentrated", "Distributed"
LOAD_TYPES = (CONCENTRATED, DISTRIBUTED)

DB = "AISC Shapes Database v16.0"
COMBO = "asce7.combo.asd.D_plus_L"

# Fy entry for each rail and post grade this slice supports.
FY_ENTRY = {"A53 Gr B": "material.A53_GrB.Fy"}
# Fu entry for each grade a weld's fusion face can be (W12): the rail and
# post grades, and the baseplate.
FU_ENTRY = {"A53 Gr B": "material.A53_GrB.Fu", "A36": "material.A36.Fu"}
# Baseplate grades accepted: A36 only, for all of v1 (W12).
BASEPLATE_GRADES = ("A36",)
# F_EXX entry for each electrode accepted: E70XX only (W12).
FEXX_ENTRY = {"E70XX": "material.E70XX.FEXX"}


class SectionStop(InputError):
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
    number: int | str    # "4a" and "4b": the intermediate rail's two parts
    title: str
    demand_label: str    # Typst math
    capacity_label: str  # Typst math
    cases: list[Case] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    summary_flag: str = ""  # short flag text printed in the summary row (e.g. Lc/r above 200)
    failures: list[str] = field(default_factory=list)  # NG whatever the ratio (a weld below minimum size)
    bypassed: bool = False
    derived_lengths: list[Line] = field(default_factory=list)  # listed on the Dimensions page
    # A check not computed (Check 4a or 4b): the line printed in place of the
    # envelope, and the summary row's result, with no ratio and no OK or NG
    # of its own ("Controlled by Checks 1 and 2", "None").
    observation: str = ""
    observation_lines: list[Line] = field(default_factory=list)  # printed under it, so its values can be traced
    result: str = ""

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
    def computed(self) -> bool:
        return not self.bypassed and not self.result

    @property
    def ok(self) -> bool:
        # A check not computed defers to the checks it names; it fails nothing itself.
        return not self.computed or (not self.failures and self.controlling.ratio <= 1.0)

    @property
    def verdict(self) -> str:
        if self.bypassed:
            return "Bypassed by engineer"
        if self.result:
            return self.result
        return "OK" if self.ok else "NG"


@dataclass
class Loading:
    P: object          # concentrated guard load
    w_L: object        # uniform guard load, or None when exempt
    w_D: object        # top rail self-weight
    L_post: object     # post cantilever length, h - t_p
    D_rail: object     # top rail dead load delivered to the post, w_D times the span
    P_D: object        # axial dead load at the top of the baseplate (D at the post)
    exempt: bool
    exemption_statement: str
    lines: list[Line]
    derived_lengths: list[Line]  # listed on the Dimensions page
    # The intermediate rail's self-weight and its dead load delivered to the
    # post, w_D,int times the span; None when there is no intermediate rail.
    w_D_int: object = None
    D_int: object = None
    P_c: object = None  # the component load on the intermediate rail (S4-3); None without one


@dataclass
class Results:
    project: Project
    rail: PipeSection
    post: PipeSection
    loading: Loading
    section_lines: list[Line]       # top rail
    post_section_lines: list[Line]
    checks: list[Check]
    inter: PipeSection | None = None  # the intermediate rail's section: the top rail's, its own, or None
    inter_section_lines: list[Line] = field(default_factory=list)  # its own section only

    def check(self, number: int) -> Check:
        return next(c for c in self.checks if c.number == number)

    @property
    def derived_lengths(self) -> list[tuple[Line, str]]:
        """Each derived length with where it is computed: the line itself, so the
        Dimensions page prints the formula that computed the value (ADR 0002)."""
        out = [(ln, "Loading") for ln in self.loading.derived_lengths]
        out += [(ln, f"Check {c.number}") for c in self.checks for ln in c.derived_lengths]
        return out


# ---------------------------------------------------------------------------
# Material, loading, section properties
# ---------------------------------------------------------------------------


def require_supported_grade(member: Member, name: str) -> None:
    """Refuse a grade this slice has no Fy or no Fu entry for. Both are
    needed: Fy for the member checks, Fu for the fusion face of a weld
    (Check 3's rail side) and the post wall's Fu/Fy guard.

    The brief's unusual-pairing warning (a grade outside the shape's standard
    list) returns when a slice accepts more than one grade; with A53 Gr B the
    only grade allowed, it could never fire.
    """
    if member.grade not in FY_ENTRY or member.grade not in FU_ENTRY:
        supported = [g for g in FY_ENTRY if g in FU_ENTRY]
        raise ProjectError(
            f"{name} grade {member.grade!r}: this version supports {', '.join(supported)} only"
        )


def build_loading(project: Project, registry: Registry, rail: PipeSection, post: PipeSection,
                  inter: PipeSection | None = None) -> Loading:
    """The guard loads and the dead load at the post. ``inter`` is the
    intermediate rail's section (the top rail's when it is the same), or
    None when there is none."""
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

    P_c = None
    if inter is not None:
        code_Pc = registry.get("asce7.guard.component")
        if ld.component is None:
            P_c = sh.code_value("P_c", code_Pc.id, "Component load on the intermediate rail, horizontal; also "
                                "applied downward (engineering judgement)").value
        else:
            P_c = sh.input(
                "P_c", ld.component,
                f"Component load on the intermediate rail, engineer override "
                f"(code value {fmt_quantity_plain(code_Pc.quantity)})",
                cite=f"Input; {code_Pc.cite}",
            ).value

    w_D = sh.given("w_D", rail.W, f"Top rail self-weight: tabulated W = {rail.W.m_as('lbf/ft'):g} lb/ft", DB)

    # Dead load reaching the post (docs/plans/slice-2.md, D2). The critical
    # section is the top of the baseplate (D4), so the post weight is taken
    # over h - t_p, the same cantilever length Checks 5 and 6 use.
    sh.heading("Dead load at the post")
    dl = "ej.post.axial_dead_load"
    h = sh.given("h", project.post_height.value, "Post height, top of concrete to top rail centerline", "Input")
    tp = sh.given("t_p", project.baseplate_thickness.value, "Baseplate thickness", "Input")
    L_post = sh.line('L_"post"', h - tp, "Post cantilever length, top of baseplate to top rail centerline",
                     cite="Stated assumption: post fixed at the top of the baseplate", unit="inch")
    L_post_line = sh.lines[-1]
    W_post = sh.given('W_"post"', post.W,
                      f"Post self-weight: {post.label}, tabulated W = {post.W.m_as('lbf/ft'):g} lb/ft", DB)
    D_post = sh.line('D_"post"', W_post * L_post, "Post dead load, full weight at the base",
                     cite_ids=(dl,), unit="lbf")
    s = sh.given("L", project.span.value, "Span: the tributary length for the post (stated assumption)", "Input")
    D_rail = sh.line('D_"rail"', w_D * s, "Top rail dead load delivered to the post", cite_ids=(dl,), unit="lbf")
    if inter is None:
        P_D = sh.line("P_D", D_rail + D_post, "D at the post: axial dead load at the top of the baseplate",
                      cite_ids=(dl,), unit="lbf")
        w_D_int = D_int = None
    else:
        # The intermediate rail frames into the side of the post below the
        # rail to post weld, so its dead load reaches D at the post but not
        # Check 3's D (docs/plans/slice-4.md, where the dead load goes).
        same = " (same section as the top rail)" if inter is rail else ""
        w_D_int = sh.given('w_(D,"int")', inter.W, f"Intermediate rail self-weight: {inter.label}{same}, "
                           f"tabulated W = {inter.W.m_as('lbf/ft'):g} lb/ft", DB)
        D_int = sh.line('D_"int"', w_D_int * s, "Intermediate rail dead load delivered to the post",
                        cite_ids=(dl,), unit="lbf")
        P_D = sh.line("P_D", D_rail + D_int + D_post, "D at the post: axial dead load at the top of the baseplate",
                      cite_ids=(dl,), unit="lbf")
        w_D_int, D_int = w_D_int.value, D_int.value
    return Loading(P=P.value, w_L=w_L, w_D=w_D.value, L_post=L_post.value, D_rail=D_rail.value, P_D=P_D.value,
                   exempt=ld.uniform_exempt, exemption_statement=ld.exemption_statement, lines=sh.lines,
                   derived_lengths=[L_post_line], w_D_int=w_D_int, D_int=D_int, P_c=P_c)


def section_lines(registry: Registry, sec: PipeSection, with_r: bool = False) -> list[Line]:
    """Section properties as published. The post block adds r, which only
    the compression check uses; the rail block prints as it did in slice 1."""
    sh = Sheet(registry)
    sh.given("D", sec.OD, f"{sec.label}: outside diameter", DB)
    sh.given('t_"nom"', sec.tnom, "Nominal wall thickness", DB)
    sh.given('t_"des"', sec.tdes, "Design wall thickness", DB)
    sh.given("A", sec.A, "Area (design wall)", DB)
    sh.given("W", sec.W, f"Nominal weight: tabulated {sec.W.m_as('lbf/ft'):g} lb/ft (nominal wall)", DB)
    sh.given("I", sec.I, "Moment of inertia", DB)
    sh.given("S", sec.S, "Elastic section modulus", DB)
    sh.given("Z", sec.Z, "Plastic section modulus", DB)
    if with_r:
        sh.given("r", sec.r, "Radius of gyration", DB)
    sh.given("D slash t", sec.D_t, "Diameter-to-thickness ratio, tabulated", DB)
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
    sh.decision(
        mtext("Round HSS"), "Lateral-torsional buckling does not apply",
        "Limit states: yielding and local buckling only; Lb and Cb do not enter",
        cite_ids=("aisc360.F8.no_ltb",),
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
        # Fetched only here: Registry.get records every lookup for the DRAFT list,
        # and a compact calc must not list an equation it never used.
        f82 = registry.get("aisc360.eq.F8-2")
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
    Ma = sh.line("frac(M_n, Omega_b)", Mn / Om, "Allowable flexural strength",
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
        # One expression gives both the printed magnitude and the stated sense (ADR 0002).
        # Dead load acts down (+), the guard load up (-).
        net = sh.factor(combo.id, "D") * MD - sh.factor(combo.id, "L") * ML
        sense = "net upward" if net.eval() < Q_(0, "lbf*inch") else "net downward"
        M = sh.line("M_a", absolute(net),
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


def exempt_case(registry: Registry, direction: str, case_type: type[Case] = Case) -> Case:
    """The distributed-load row when the engineer exempts the uniform load:
    listed in the envelope, not checked. Every check builds it here."""
    exemption = registry.get("asce7.guard.uniform.exemption.intro")
    return case_type(direction, DISTRIBUTED, "exempt", remark=f"Uniform load not considered ({exemption.cite})")


def _envelope(case_fn, registry, project, rail, loading) -> list[Case]:
    cases = []
    for direction in DIRECTIONS:
        if direction == "Longitudinal":
            cases.append(Case(direction, None, "not checked",
                              remark="Rail carries the longitudinal load axially; not checked"))
            continue
        for lt in LOAD_TYPES:
            if lt == DISTRIBUTED and loading.exempt:
                cases.append(exempt_case(registry, direction))
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


def _fu_fy_guard(registry: Registry, grade: str, member: str, covered: str) -> None:
    """Stop when a wall's coverage by a member check fails: the member check
    covers the wall at a weld only while yielding governs over rupture,
    Fu/Fy >= 1.20 (W5; S4-12 for the intermediate rail)."""
    Fy, Fu = registry.get(FY_ENTRY[grade]).quantity, registry.get(FU_ENTRY[grade]).quantity
    limit = registry.get("ej.weld.post_wall.fu_fy_min")
    ratio = Fu / Fy
    if ratio < limit.value:
        raise ProjectError(
            f"{member} grade {grade}: Fu/Fy = {fmt_sig(ratio.m_as('dimensionless'))} is below {limit.value} "
            f"({limit.cite}). The {member} wall at the weld is covered by {covered} only while yielding governs "
            f"over rupture; the tool does not check this grade's {member} wall at the weld."
        )


def validate(project: Project, registry: Registry) -> None:
    """The input checks that need more than one field, or a lookup. Raises an
    InputError naming what it checked and why. Runs before compute, so no
    check runs on inputs that fail.

    - the sections exist, and each grade and the electrode is one this
      version supports (W12);
    - the rail, the post and the intermediate rail are round hollow sections
      (W7, extended to the intermediate rail by S4-12);
    - the post is no wider than the rail (W8);
    - the post grade's Fu/Fy keeps its wall at the weld covered by Check 5 (W5);
    - the intermediate rail is no wider than the post (S4-11), the span is at
      least twice the post OD (S4-12), and the intermediate rail grade's
      Fu/Fy keeps its wall at the weld covered by the member check (S4-12);
    - the baseplate is no smaller in plan than the post OD (S4-6).
    """
    from handrail import shapes

    rail = shapes.pipe(project.top_rail.section)
    post = shapes.pipe(project.post.section)
    require_supported_grade(project.top_rail, "top rail")
    require_supported_grade(project.post, "post")
    own = project.intermediate_rail.member  # its own section, or None
    inter = shapes.pipe(own.section) if own else None
    if own:
        require_supported_grade(own, "intermediate rail")
    electrode = project.welds.electrode
    if electrode not in FEXX_ENTRY:
        raise ProjectError(f"[welds] electrode {electrode!r}: this version supports {', '.join(FEXX_ENTRY)} only")
    if project.baseplate.grade not in BASEPLATE_GRADES:
        raise ProjectError(f"[baseplate] grade {project.baseplate.grade!r}: this version supports "
                           f"{', '.join(BASEPLATE_GRADES)} only")

    members = [("top rail", rail), ("post", post)] + ([("intermediate rail", inter)] if inter else [])
    for member, sec in members:
        if sec.family not in shapes.ROUND_HOLLOW:
            raise ProjectError(
                f"{member} {sec.label} ({sec.family}) is not a round hollow section. The stated assumption "
                f"that the rail wall's local strength at the post is not checked has been decided only for "
                f"a round hollow rail on a round hollow post, not for this section."
            )

    D_rail, D_post = rail.OD, post.OD
    if D_post > D_rail:
        raise ProjectError(
            f"The post ({post.label}, OD {fmt_quantity_plain(D_post)}) is wider than the top rail "
            f"({rail.label}, OD {fmt_quantity_plain(D_rail)}). The coped post to rail underside detail "
            f"requires post OD <= rail OD. Check the inputs."
        )

    _fu_fy_guard(registry, project.post.grade, "post", "Check 5")

    member = project.intermediate_member
    if member is not None:
        same = project.intermediate_rail.state == SAME_AS_TOP
        sec = rail if same else inter
        if sec.OD > D_post:
            how = ("With same_as_top_rail = true it takes the top rail's section: uncheck same_as_top_rail and "
                   "enter a section no wider than the post." if same else
                   "Enter a section no wider than the post.")
            raise ProjectError(
                f"The intermediate rail ({sec.label}, OD {fmt_quantity_plain(sec.OD)}) is wider than the post "
                f"({post.label}, OD {fmt_quantity_plain(D_post)}). Its end is coped to the side of the post, "
                f"which requires intermediate rail OD <= post OD. {how}"
            )
        span = project.span
        if span.value < 2 * D_post:
            raise ProjectError(
                f"The span ({span.entered}) is less than twice the post OD (2 x {fmt_quantity_plain(D_post)} = "
                f"{fmt_quantity_plain(2 * D_post)}). The intermediate rail wall at the post is covered by its "
                f"member check only when L >= 2 D_post. Check the inputs."
            )
        _fu_fy_guard(registry, member.grade, "intermediate rail",
                     "Checks 1 and 2" if same else "Check 4a")

    for name, d, orientation in (("B", project.baseplate.B, "parallel to the rail"),
                                 ("N", project.baseplate.N, "perpendicular to the rail")):
        if d.value < D_post:
            raise ProjectError(
                f"[baseplate] {name} = {d.entered} ({orientation}) is smaller than the post OD "
                f"({post.label}, {fmt_quantity_plain(D_post)}). Check the inputs."
            )


def compute(project: Project, registry: Registry) -> Results:
    """Every check, on inputs validate() has accepted.

    A separate entry point so a test can compute a case that validation
    refuses (docs/plans/slice-3.md, T1); the CLI always validates first.
    """
    # Imported here, not at the top: post.py and welds.py build on this
    # module's Case, Check and Loading, so a top-level import would be circular.
    from handrail import shapes
    from handrail.intermediate import check_4a
    from handrail.post import check_5, check_6
    from handrail.welds import check_3, check_4b, check_7

    rail = shapes.pipe(project.top_rail.section)
    post = shapes.pipe(project.post.section)
    member = project.intermediate_member
    same = project.intermediate_rail.state == SAME_AS_TOP
    inter = None if member is None else rail if same else shapes.pipe(member.section)
    loading = build_loading(project, registry, rail, post, inter)
    props = section_lines(registry, rail)
    post_props = section_lines(registry, post, with_r=True)
    inter_props = section_lines(registry, inter) if inter is not None and not same else []
    checks = [check_1(registry, project, rail, loading), check_2(registry, project, rail, loading),
              check_3(registry, project, rail, post, loading),
              check_4a(registry, project, inter, loading), check_4b(registry, project, post, inter, loading),
              check_5(registry, project, post, loading), check_6(registry, project, post, loading),
              check_7(registry, project, post, loading)]
    return Results(project, rail, post, loading, props, post_props, checks, inter, inter_props)


def run(project: Project, registry: Registry) -> Results:
    """Validate, then compute: the order the CLI uses."""
    validate(project, registry)
    return compute(project, registry)
