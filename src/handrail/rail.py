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

from handrail import beams
from handrail.calc import Const, Sheet, Sym, absolute, sqrt
from handrail.directions import CONCENTRATED, DIRECTIONS, DISTRIBUTED, LOAD_TYPES, Direction, LoadType, unknown
from handrail.flexure import Capacity, flexural_capacity
from handrail.loading import COMBO, combo_text, exempt_case
from handrail.results import Case, Check, Loading
from handrail.units import Q_

# ---------------------------------------------------------------------------
# Check 1: bending
# ---------------------------------------------------------------------------


def _live_moment(sh: Sheet, load_type: LoadType, L: Sym, loading: Loading) -> Sym:
    if load_type == CONCENTRATED:
        P = sh.given("P", "P", loading.P, "Concentrated guard load at midspan", "Loading")
        return beams.point_moment(sh, "M_L", "M_L", P, L, "Live-load moment, midspan")
    if load_type == DISTRIBUTED:
        w = sh.given("w_L", "w_L", loading.w_L, "Uniform guard load", "Loading")
        return beams.uniform_moment(sh, "M_L", "M_L", w, L, "Live-load moment, midspan")
    unknown("Check 1", "guard load type", load_type, LOAD_TYPES)


def _bending_case(registry, project, rail, loading, cap: Capacity, direction, load_type) -> Case:
    sh = Sheet(registry)
    sh.heading("Capacity")
    sh.lines.extend(cap.lines)
    Ma_allow = cap.allow
    sh.heading(f"Demand: {direction.lower()}, {load_type.lower()} load")
    L = sh.given("L", "L", project.span.value, "Span, simple beam", "Input")
    wD = sh.given("w_D", "w_D", loading.w_D, "Top rail self-weight", "Loading")
    MD = beams.uniform_moment(sh, "M_D", "M_D", wD, L, "Dead-load moment, midspan")
    ML = _live_moment(sh, load_type, L, loading)

    if direction == Direction.DOWNWARD:
        combo = registry.get(COMBO)
        M = sh.line("M_a", "M_a", sh.factor(combo.id, "D") * MD + sh.factor(combo.id, "L") * ML,
                    "Required flexural strength: D and L on the same axis", unit="lbf*inch")
        label = f"{combo_text(combo)}, vertical\n{combo.cite}"
    elif direction in (Direction.OUTWARD, Direction.INWARD):
        combo, srss = registry.get(COMBO), registry.get("ej.bending.srss_round")
        Mv = sh.line("M_a_v", "M_(a,v)", sh.factor(combo.id, "D") * MD, "Vertical axis: dead load", unit="lbf*inch")
        Mh = sh.line("M_a_h", "M_(a,h)", sh.factor(combo.id, "L") * ML, f"Horizontal axis: guard load {direction.lower()}",
                     unit="lbf*inch")
        M = sh.line("M_a", "M_a", sqrt(Mv**2 + Mh**2),
                    "Resultant moment: exact for a round section, one capacity",
                    cite_ids=(srss.id,), unit="lbf*inch")
        label = (f"{combo_text(combo, {'D': 'vertical', 'L': 'horizontal'}, ', ')}, SRSS\n"
                 f"{combo.cite}; {srss.cite}")
    elif direction == Direction.UPWARD:
        combo = registry.get("ej.combo.bending.upward")
        # One expression gives both the printed magnitude and the stated sense (ADR 0002).
        # Dead load acts down (+), the guard load up (-).
        net = sh.factor(combo.id, "D") * MD - sh.factor(combo.id, "L") * ML
        sense = "net upward" if net.eval() < Q_(0, "lbf*inch") else "net downward"
        M = sh.line("M_a", "M_a", absolute(net),
                    f"Net vertical moment, guard load opposing dead load: {sense}", unit="lbf*inch")
        label = f"{combo_text(combo)}, net vertical\n{combo.cite}"
    else:
        unknown("Check 1", "direction case", direction, DIRECTIONS)

    ratio = sh.line("Ratio", '"Ratio"', M / Ma_allow, "Demand / capacity", cite_ids=("aisc360.eq.B3-2",), ratio=True)
    return Case(direction, load_type, "checked", label,
                demand=M.value, capacity=Ma_allow.value, ratio=ratio.value, lines=sh.lines)


# ---------------------------------------------------------------------------
# Check 2: deflection
# ---------------------------------------------------------------------------


def _deflection_case(registry, project, rail, loading, direction, load_type) -> Case:
    sh = Sheet(registry)
    L = sh.given("L", "L", project.span.value, "Span, simple beam", "Input")
    E = sh.code_value("E", "E", "material.steel.E", "Modulus of elasticity")
    I = sh.given("I", "I", rail.I, "Moment of inertia", rail.source)
    if load_type == CONCENTRATED:
        P = sh.given("P", "P", loading.P, "Concentrated guard load at midspan", "Loading")
        DL = beams.point_deflection(sh, "Delta_L", "Delta_L", P, L, E, I, "Live-load deflection, midspan")
    elif load_type == DISTRIBUTED:
        w = sh.given("w_L", "w_L", loading.w_L, "Uniform guard load", "Loading")
        DL = beams.uniform_deflection(sh, "Delta_L", "Delta_L", w, L, E, I, "Live-load deflection, midspan")
    else:
        unknown("Check 2", "guard load type", load_type, LOAD_TYPES)
    if direction == Direction.DOWNWARD:
        combo = registry.get("ej.combo.deflection.D_plus_L")
        wD = sh.given("w_D", "w_D", loading.w_D, "Top rail self-weight", "Loading")
        DD = beams.uniform_deflection(sh, "Delta_D", "Delta_D", wD, L, E, I, "Dead-load deflection, midspan")
        D = sh.line("Delta", "Delta", sh.factor(combo.id, "D") * DD + sh.factor(combo.id, "L") * DL,
                    "D and L on the same (vertical) axis", unit="inch")
        axis = "vertical"
    elif direction in (Direction.OUTWARD, Direction.INWARD, Direction.UPWARD):
        upward = direction == Direction.UPWARD
        combo = registry.get("ej.combo.deflection.L_only")
        note = "Live load only" + (": opposes dead load, dead load not credited" if upward else "")
        D = sh.line("Delta", "Delta", sh.factor(combo.id, "L") * DL, note, unit="inch")
        axis = "vertical" if upward else "horizontal"
    else:
        unknown("Check 2", "direction case", direction, DIRECTIONS)
    label = f"{combo_text(combo)}, {axis}\n{combo.cite}"

    r = project.rail_deflection.ratio
    lim = Const(int(r) if float(r).is_integer() else r)
    Dallow = sh.line("Delta_allow", 'Delta_"allow"', L / lim, f"Limit L/{lim.value}",
                     cite_ids=("ej.deflection.limit",), unit="inch")
    ratio = sh.line("Ratio", '"Ratio"', D / Dallow, "Deflection / limit", cite_ids=("ej.deflection.limit",), ratio=True)
    return Case(direction, load_type, "checked", label,
                demand=D.value, capacity=Dallow.value, ratio=ratio.value, lines=sh.lines)


# ---------------------------------------------------------------------------
# Envelope
# ---------------------------------------------------------------------------


def _envelope(case_fn, registry, project, rail, loading) -> list[Case]:
    cases = []
    for direction in DIRECTIONS:
        if direction == Direction.LONGITUDINAL:
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
