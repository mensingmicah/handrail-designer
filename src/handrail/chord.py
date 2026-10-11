"""The rail wall at a round post: the AISC 360-22 Chapter K chord limit
states, checked inside Check 3 (docs/brief/welds.md, S6-10).

The post is the branch of a T-connection at 90 degrees and the rail the
chord. In each guard load case the post puts on the rail wall the forces
the rail to post weld carries (the weld envelope, W10):

- downward, upward: branch axial force, D + L or L - 0.6D;
- outward, inward: out-of-plane moment V e, with the dead load axial;
- longitudinal: in-plane moment V e, with the dead load axial;

with e half the rail's diameter. Each action has a chord plastification
strength (Eqs. K3-2, K4-1, K4-3) and, where the post is narrower than the
rail's inside (Db < D - 2t), a shear yielding (punching) strength (Eqs.
K3-1, K4-2, K4-4); the lower is the available strength, and a case combines
its actions by Eq. K4-5.

The chord-stress parameter Qf (Eq. K1-3) needs the rail's own moment at
the post. The tool's simple span has none there, so the same case's
midspan moment stands in for it, a bound on the continuous rail's hogging
moment; only the part that stresses the rail's underside counts, and in
the upward case the underside is in tension and Qf = 1.0.

This is computed for a round post on a round rail only. A rectangular
rail, and a round member meeting a rectangular one, keep the stated
assumption (S6-9, S6-12). The result has its own summary row and its own
values (S6-16 item 1): Check 3's ratio stays the weld's.

It prints compactly (S6-1): one table of every case, the governing case's
lines in full, and any other case's whose ratio is over the print
threshold.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from handrail import beams
from handrail.calc import PI, Line, Sheet, Sym, Term, compare, fmt_ratio, minimum, mtext, number, term
from handrail.demand import ASD, Given, Wording, demand
from handrail.directions import (
    CONCENTRATED, DIRECTIONS, DISTRIBUTED, LOAD_TYPES, Direction, Kind, LoadType, kind, unknown,
)
from handrail.loading import COMBO, exempt_case
from handrail.materials import yield_stress
from handrail.project import Project
from handrail.registry import Registry
from handrail.results import Case, Check, Loading
from handrail.shapes import Section

ACTIONS = "ej.weld.chord.actions"
PARAMS = "aisc360.K1.1.parameters"
PUNCHING = "aisc360.K3.1.punching_condition"
LOWEST = "aisc360.K3.2.lowest_limit_state"
OMEGA_PL, OMEGA_V = "aisc360.K3.1.omega_plastification", "aisc360.K3.1.omega_punching"
MRO = "ej.weld.chord.Mro"
THRESHOLD = "ej.weld.chord.print_threshold"
PLASTIFICATION, PUNCH = "chord plastification", "shear yielding (punching)"
IN_PLANE, OUT_OF_PLANE = "in-plane", "out-of-plane"
NUMBER = "3 (chord wall)"


@dataclass
class ChordCase(Case):
    """One guard load case of the chord check, with what its table row prints."""

    Pr: Any = None           # branch axial force on the rail wall
    sense: str = ""          # "compression" or "tension"
    Mr: Any = None           # branch moment; None in the vertical cases
    plane: str = ""          # IN_PLANE or OUT_OF_PLANE; "" in the vertical cases
    Qf: float | None = None
    Pc: Any = None           # available axial strength
    P_state: str = ""        # the limit state Pc comes from
    Mc: Any = None           # available flexural strength; None in the vertical cases
    M_state: str = ""
    ok: bool = True          # this case's own ratio against 1.00, for its table row
    no_strength: bool = False  # Qf came out at zero or below: no ratio, and the check is NG


@dataclass
class ChordCheck(Check):
    """The chord check of Check 3, with whether punching applies and which
    cases print their lines in full."""

    punching: bool = False
    full: list[ChordCase] = field(default_factory=list)   # the governing case first
    threshold: float = 0.0   # a case over this ratio prints its lines in full


WORDING = Wording(
    where={Kind.DOWNWARD: "vertical, on the rail at the post",
           Kind.HORIZONTAL: "horizontal ({direction}), on the rail at the post",
           Kind.UPWARD: "upward, on the rail at the post"},
    axial="P_r",
    axial_notes={Kind.DOWNWARD: "Branch axial force on the rail wall, compression; no moment",
                 Kind.HORIZONTAL: "Branch axial force on the rail wall: dead load, compression",
                 Kind.UPWARD: "Branch axial force on the rail wall: net tension, guard load opposing dead load"},
    factored="shear", factored_symbol="V", factored_note="Horizontal force at the rail centerline",
    moment_symbol="M_r", moment_note="Branch moment on the rail wall: V at the rail centerline, arm e",
    moment_cite=ACTIONS,
)


@dataclass
class _Joint:
    """What every case of one joint shares: the head lines and their symbols."""

    lines: list[Line]
    Fy: Sym
    t: Sym
    Db: Sym
    beta: Sym
    gamma: Sym
    e: Sym
    Fc: Sym
    S: Sym
    Om_pl: Sym
    Om_v: Sym | None       # where shear yielding (punching) applies


def _joint(registry: Registry, project: Project, rail: Section, post: Section) -> _Joint:
    sh = Sheet(registry)
    sh.heading("Rail wall at the post: chord and branch")
    actions = registry.get(ACTIONS)
    sh.decision(mtext("Rail wall at the post"), "Checked: chord limit states", actions.value, cite_ids=(actions.id,))
    Fy = yield_stress(registry, project.top_rail.grade, rail).line(sh, "F_y", "F_y")
    D = sh.given("D", "D", rail.OD, f"{rail.label}: outside diameter of the chord, the rail", rail.source)
    t = sh.given("t", "t", rail.tdes, "Design wall thickness of the chord", rail.source)
    Db = sh.given("D_b", "D_b", post.OD, f"{post.label}: outside diameter of the branch, the post", post.source)
    beta = sh.line("beta", "beta", Db / D, "Width ratio", cite_ids=(PARAMS,))
    gamma = sh.line("gamma", "gamma", D / (2 * t), "Chord slenderness ratio", cite_ids=(PARAMS,))
    e = sh.line("e", "e", D / 2, "Eccentricity: rail centerline to the rail's underside", cite_ids=(ACTIONS,), unit="inch")
    Om_pl = sh.code_value("Omega_pl", 'Omega_"pl"', OMEGA_PL, "Safety factor, chord plastification (ASD)")

    # Punching is a limit state only where the post fits inside the rail's
    # wall. One comparison decides and prints (ADR 0002).
    inside = sh.line("D_inside", 'D_"in"', D - 2 * t, "Chord diameter less two walls", cite_ids=(PUNCHING,), unit="inch")
    applies = compare(Db.stated(), "<", inside.stated())
    Om_v = None
    if applies:
        sh.decision(applies, "Shear yielding (punching) applies", "The post is narrower than the inside of the rail",
                    cite_ids=(PUNCHING,))
        Om_v = sh.code_value("Omega_v", "Omega_v", OMEGA_V, "Safety factor, shear yielding (punching) (ASD)")
    else:
        sh.decision(applies, "Shear yielding (punching) does not apply",
                    "The post is not narrower than the inside of the rail", cite_ids=(PUNCHING,))

    mro = registry.get(MRO)
    sh.decision(mtext("Rail moment at the post, for Q_f"), "The same case's midspan moment, as a bound", mro.value,
                cite_ids=(mro.id,))
    Fc = sh.line("F_c", "F_c", sh.coeff("aisc360.K1.1.Fc_asd") * Fy, "Available stress in the chord (ASD)", unit="ksi")
    S = sh.given("S", "S", rail.S, "Elastic section modulus of the chord", rail.source)
    return _Joint(sh.lines, Fy, t, Db, beta, gamma, e, Fc, S, Om_pl, Om_v)


def _chord_stress(sh: Sheet, registry: Registry, project: Project, loading: Loading, j: _Joint, k: Kind,
                  load_type: LoadType) -> Sym:
    """Qf for one case (S6-10): from the rail's own moment where its
    underside is in compression, and 1.0 where it is in tension."""
    if k is Kind.UPWARD:
        return sh.code_value("Q_f", "Q_f", "aisc360.K1.3.Qf_tension",
                             "Chord-stress parameter: the rail's underside is in tension in the upward case")
    if k not in (Kind.DOWNWARD, Kind.HORIZONTAL):
        unknown("Chord check", "kind of direction case", k, Kind)
    sh.heading("Chord stress")
    combo = registry.get(COMBO)
    L = sh.given("L", "L", project.span.value, "Span, simple beam", "Input")
    wD = sh.given("w_D", "w_D", loading.w_D, "Top rail self-weight", "Loading")
    MD = beams.uniform_moment(sh, "M_D", "M_D", wD, L, "Dead-load moment of the rail, midspan")
    if k is Kind.DOWNWARD:
        if load_type == CONCENTRATED:
            # Keyed apart from the branch axial force, which the demand keys "P".
            P = sh.given("P_guard", "P", loading.P, "Concentrated guard load at midspan", "Loading")
            ML = beams.point_moment(sh, "M_L", "M_L", P, L, "Live-load moment of the rail, midspan")
        elif load_type == DISTRIBUTED:
            w = sh.given("w_L", "w_L", loading.w_L, "Uniform guard load", "Loading")
            ML = beams.uniform_moment(sh, "M_L", "M_L", w, L, "Live-load moment of the rail, midspan")
        else:
            unknown("Chord check", "guard load type", load_type, LOAD_TYPES)
        Mro = sh.line("M_ro", 'M_"ro"', sh.factor(combo.id, "D") * MD + sh.factor(combo.id, "L") * ML,
                      "Rail moment for Q_f: the vertical moment of this case, D and L", cite_ids=(MRO,), unit="lbf*inch")
    else:
        Mro = sh.line("M_ro", 'M_"ro"', sh.factor(combo.id, "D") * MD,
                      "Rail moment for Q_f: the dead-load moment; the horizontal guard load leaves the underside on "
                      "the neutral axis", cite_ids=(MRO,), unit="lbf*inch")
    U = sh.line("U", "U", Mro / (j.Fc * j.S), "Chord utilization, with no axial force in the rail",
                cite_ids=("aisc360.eq.K1-6",))
    return sh.line("Q_f", "Q_f", 1 - sh.coeff("aisc360.eq.K1-3.coeff") * U * (1 + U),
                   "Chord-stress interaction parameter: the rail's underside in compression",
                   cite_ids=("aisc360.eq.K1-3",))


def _available(sh: Sheet, key: str, symbol: str, plastification: Sym, punching: Sym, what: str,
               unit: str) -> tuple[Sym, str]:
    """The available strength for one action where shear yielding (punching)
    applies: the lower of it and chord plastification, naming the limit
    state it comes from."""
    # A tie goes to chord plastification, the limit state that always applies.
    lower = compare(plastification.stated(), "<=", punching.stated())
    state = PLASTIFICATION if lower else PUNCH
    sh.decision(lower, f"{state.capitalize()} governs", f"{what}: the lowest of the applicable limit states",
                cite_ids=(LOWEST,))
    return sh.line(key, symbol, minimum(plastification, punching), what, cite_ids=(LOWEST,), unit=unit), state


def _within_unity(ratio: Sym) -> bool:
    """One case's ratio against 1.00, as Check.within_unity compares the
    controlling one: on the ratio as printed."""
    return compare(term('"Ratio"', ratio.value, fmt_ratio), "<=", Term("1.00", 1.0)).holds


def _case(registry: Registry, project: Project, loading: Loading, j: _Joint, direction: Direction,
          load_type: LoadType) -> ChordCase:
    dead = Given("D_rail", 'D_"rail"', loading.D_rail,
                 "Top rail dead load at the post: w_D over the span (the tributary length)", "Loading")
    d = demand(registry, project, loading, direction, load_type, ASD, WORDING, dead, j.e)
    if d.P is None:
        return ChordCase(direction, load_type, "not checked", d.label, remark=d.remark)
    k = kind(direction)
    sh = Sheet(registry)
    sh.lines.extend(j.lines)
    sh.lines.extend(d.lines)
    Qf = _chord_stress(sh, registry, project, loading, j, k, load_type)
    # Eq. K1-3 falls to zero near U = 1.39 and goes negative past it. A
    # strength of zero or less has no ratio: the case is NG outright, never
    # divided into the demand.
    none = compare(Qf.stated(), "<=", number(0))
    if none:
        sh.decision(none, "No available strength", "The rail's own stress leaves its wall no strength at the post",
                    cite_ids=("aisc360.eq.K1-3",))
        return ChordCase(direction, load_type, "not checked", d.label, lines=sh.lines, no_strength=True, ok=False,
                         remark="NG: the rail's own stress leaves its wall no strength at the post (Q_f not over 0)")

    sh.heading("Available strengths")
    Pn = sh.line("P_n", "P_n",
                 j.Fy * j.t**2 * (sh.coeff("aisc360.eq.K3-2.coeff_constant")
                                  + sh.coeff("aisc360.eq.K3-2.coeff_beta") * j.beta**2)
                 * j.gamma ** sh.coeff("aisc360.eq.K3-2.exponent") * Qf,
                 "Chord plastification under branch axial load; the branch is at 90 degrees",
                 cite_ids=("aisc360.eq.K3-2",), unit="lbf")
    name_P = "Available axial strength"
    if j.Om_v is None:
        Pc = sh.line("P_c", "P_c", Pn / j.Om_pl, f"{name_P}: chord plastification", cite_ids=("aisc360.eq.B3-2",),
                     unit="lbf")
        P_state = PLASTIFICATION
    else:
        Pc_pl = sh.line("P_c_pl", 'P_("c,pl")', Pn / j.Om_pl, f"{name_P}, chord plastification",
                        cite_ids=("aisc360.eq.B3-2",), unit="lbf")
        Pc_v = sh.line("P_c_v", 'P_("c,v")', sh.coeff("aisc360.eq.K3-1.coeff") * j.Fy * j.t * PI * j.Db / j.Om_v,
                       f"{name_P}, shear yielding (punching); the branch is at 90 degrees",
                       cite_ids=("aisc360.eq.K3-1", "aisc360.eq.B3-2"), unit="lbf")
        Pc, P_state = _available(sh, "P_c", "P_c", Pc_pl, Pc_v, name_P, "lbf")
    Pr = d.P

    if d.M is None:
        ratio = sh.line("Ratio", '"Ratio"', Pr / Pc, "Branch axial force alone", cite_ids=("aisc360.eq.K4-5",), ratio=True)
        return ChordCase(direction, load_type, "checked", d.label, demand=Pr.value, capacity=Pc.value,
                         ratio=ratio.value, lines=sh.lines, Pr=Pr.value, sense=d.sense, Qf=Qf.value,
                         Pc=Pc.value, P_state=P_state, ok=_within_unity(ratio))

    Mr = d.M
    if direction == Direction.LONGITUDINAL:
        plane, sub, punch_eq = IN_PLANE, "ip", "aisc360.eq.K4-2"
        Mn = sh.line("M_n", 'M_"n-ip"',
                     sh.coeff("aisc360.eq.K4-1.coeff") * j.Fy * j.t**2
                     * j.gamma ** sh.coeff("aisc360.eq.K4-1.exponent") * j.beta * j.Db * Qf,
                     "Chord plastification under branch in-plane bending", cite_ids=("aisc360.eq.K4-1",),
                     unit="lbf*inch")
    elif direction in (Direction.OUTWARD, Direction.INWARD):
        plane, sub, punch_eq = OUT_OF_PLANE, "op", "aisc360.eq.K4-4"
        Mn = sh.line("M_n", 'M_"n-op"',
                     j.Fy * j.t**2 * j.Db * (sh.coeff("aisc360.eq.K4-3.coeff")
                                             / (1 - sh.coeff("aisc360.eq.K4-3.coeff_beta") * j.beta)) * Qf,
                     "Chord plastification under branch out-of-plane bending", cite_ids=("aisc360.eq.K4-3",),
                     unit="lbf*inch")
    else:
        unknown("Chord check", "horizontal direction case", direction, [x for x in DIRECTIONS if kind(x) is Kind.HORIZONTAL])
    name_M = f"Available {plane} flexural strength"
    if j.Om_v is None:
        Mc = sh.line("M_c", f'M_"c-{sub}"', Mn / j.Om_pl, f"{name_M}: chord plastification",
                     cite_ids=("aisc360.eq.B3-2",), unit="lbf*inch")
        M_state = PLASTIFICATION
    else:
        Mc_pl = sh.line("M_c_pl", f'M_("c-{sub},pl")', Mn / j.Om_pl, f"{name_M}, chord plastification",
                        cite_ids=("aisc360.eq.B3-2",), unit="lbf*inch")
        Mc_v = sh.line("M_c_v", f'M_("c-{sub},v")', sh.coeff(f"{punch_eq}.coeff") * j.Fy * j.t * j.Db**2 / j.Om_v,
                       f"{name_M}, shear yielding (punching); the branch is at 90 degrees",
                       cite_ids=(punch_eq, "aisc360.eq.B3-2"), unit="lbf*inch")
        Mc, M_state = _available(sh, "M_c", f'M_"c-{sub}"', Mc_pl, Mc_v, name_M, "lbf*inch")
    if plane == IN_PLANE:
        ratio = sh.line("Ratio", '"Ratio"', Pr / Pc + (Mr / Mc) ** 2, "Branch axial force and in-plane moment combined",
                        cite_ids=("aisc360.eq.K4-5",), ratio=True)
    else:
        ratio = sh.line("Ratio", '"Ratio"', Pr / Pc + Mr / Mc, "Branch axial force and out-of-plane moment combined",
                        cite_ids=("aisc360.eq.K4-5",), ratio=True)
    return ChordCase(direction, load_type, "checked", d.label, demand=Mr.value, capacity=Mc.value,
                     ratio=ratio.value, lines=sh.lines, Pr=Pr.value, sense=d.sense, Mr=Mr.value, plane=plane,
                     Qf=Qf.value, Pc=Pc.value, P_state=P_state, Mc=Mc.value, M_state=M_state, ok=_within_unity(ratio))


def chord_check(registry: Registry, project: Project, rail: Section, post: Section, loading: Loading) -> ChordCheck:
    """The chord limit states of a round rail at a round post, over the
    envelope of the rail to post weld."""
    j = _joint(registry, project, rail, post)
    chk = ChordCheck(NUMBER, "Top rail wall at the post", "P_r, M_r", "P_c, M_c", punching=j.Om_v is not None)
    for direction in DIRECTIONS:
        for lt in LOAD_TYPES:
            if lt == DISTRIBUTED and loading.exempt:
                chk.cases.append(exempt_case(registry, direction, ChordCase))
            else:
                chk.cases.append(_case(registry, project, loading, j, direction, lt))
    cases = [c for c in chk.cases if isinstance(c, ChordCase)]
    without = [c for c in cases if c.no_strength]
    if without:
        failure = ("the rail's own stress leaves its wall no strength at the post ("
                   + "; ".join(c.label.lower() for c in without) + ")")
        chk.failures.append(failure)
        chk.flags.append(f"NO CHORD STRENGTH: {failure}")
        chk.summary_flag = "no chord strength"
    # The governing case prints in full always; any other does over the
    # threshold (S6-1), and so does a case with no strength, which has no
    # ratio to compare. The threshold is read once, to decide what prints.
    chk.threshold = registry.get(THRESHOLD).value
    ctrl = chk.controlling
    chk.full = [c for c in cases if c is ctrl or c.no_strength
                or (c.status == "checked" and (c.ratio or 0.0) > chk.threshold)]
    chk.full.sort(key=lambda c: c is not ctrl)
    return chk
