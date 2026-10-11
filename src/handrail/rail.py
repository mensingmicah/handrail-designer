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

A rectangular or square rail (S6-2, S6-4) has two axes. Each case puts its
vertical moment on the axis a vertical load bends and its horizontal moment
on the other, each against its own AISC 360-22 F7 strength with its own
Cb, and the outward and inward cases combine the two by section H1.1 in
place of SRSS. Deflection is about the axis the case bends.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from handrail import beams, cb
from handrail.calc import Const, Sheet, Sym, absolute, sqrt
from handrail.directions import CONCENTRATED, DIRECTIONS, DISTRIBUTED, LOAD_TYPES, Direction, LoadType, unknown
from handrail.flexure import Capacity, Unbraced, flexural_capacity, rect_axis_capacity, rect_limits
from handrail.loading import COMBO, combo_text, exempt_case
from handrail.orientation import RailAxes, axis, rail_axes
from handrail.results import Case, Check, Loading
from handrail.shapes import Section
from handrail.units import Q_

BIAXIAL = "ej.bending.biaxial_rect"
H1_1B = "aisc360.eq.H1-1b"
SPAN_UNBRACED = "Laterally unbraced length: the span between posts"


@dataclass
class BiaxialCase(Case):
    """A Check 1 case of a rectangular rail: the moment about the axis a
    vertical load bends and, in the outward and inward cases, the moment
    about the axis the horizontal guard load bends, each with its own
    allowable strength. The envelope and the summary print both."""

    axis_v: str = ""    # the axis the vertical moment is about
    M_v: Any = None
    Mc_v: Any = None
    axis_h: str = ""    # the axis the horizontal moment is about; "" in a vertical case
    M_h: Any = None
    Mc_h: Any = None

# ---------------------------------------------------------------------------
# Check 1: bending
# ---------------------------------------------------------------------------


def _live(sh: Sheet, load_type: LoadType, L: Sym, loading: Loading) -> tuple[Sym, Sym]:
    """The guard load of this type and its midspan moment, each as its own line."""
    if load_type == CONCENTRATED:
        P = sh.given("P", "P", loading.P, "Concentrated guard load at midspan", "Loading")
        return P, beams.point_moment(sh, "M_L", "M_L", P, L, "Live-load moment, midspan")
    if load_type == DISTRIBUTED:
        w = sh.given("w_L", "w_L", loading.w_L, "Uniform guard load", "Loading")
        return w, beams.uniform_moment(sh, "M_L", "M_L", w, L, "Live-load moment, midspan")
    unknown("Check 1", "guard load type", load_type, LOAD_TYPES)


def _live_moment(sh: Sheet, load_type: LoadType, L: Sym, loading: Loading) -> Sym:
    return _live(sh, load_type, L, loading)[1]


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


def _rect_bending_case(registry, project, rail: Section, axes: RailAxes, loading, direction, load_type,
                       flags: list[str]) -> BiaxialCase:
    """One case of a rectangular rail. The demand prints first: the Cb of
    each axis comes from that axis's own loads in this case (S6-4)."""
    sh = Sheet(registry)
    v, h = axes.vertical, axes.horizontal
    uniform_live = load_type == DISTRIBUTED
    sh.heading(f"Demand: {direction.lower()}, {load_type.lower()} load")
    L = sh.given("L", "L", project.span.value, "Span, simple beam", "Input")
    wD = sh.given("w_D", "w_D", loading.w_D, "Top rail self-weight", "Loading")
    MD = beams.uniform_moment(sh, "M_D", "M_D", wD, L, "Dead-load moment, midspan")
    live, ML = _live(sh, load_type, L, loading)

    Mh, loads_h = None, []
    if direction == Direction.DOWNWARD:
        combo = registry.get(COMBO)
        fD, fL = sh.factor(combo.id, "D"), sh.factor(combo.id, "L")
        Mv = sh.line(f"M_r_{v}", f'M_"r{v}"', fD * MD + fL * ML,
                     f"Required flexural strength about the {v} axis: D and L, both vertical", unit="lbf*inch")
        loads_v = [cb.SpanLoad(fD * wD, True), cb.SpanLoad(fL * live, uniform_live)]
        label = f"{combo_text(combo)}, vertical\n{combo.cite}"
    elif direction in (Direction.OUTWARD, Direction.INWARD):
        combo, biaxial = registry.get(COMBO), registry.get(BIAXIAL)
        fD, fL = sh.factor(combo.id, "D"), sh.factor(combo.id, "L")
        Mv = sh.line(f"M_r_{v}", f'M_"r{v}"', fD * MD, f"Required flexural strength about the {v} axis: dead load, vertical",
                     unit="lbf*inch")
        Mh = sh.line(f"M_r_{h}", f'M_"r{h}"', fL * ML,
                     f"Required flexural strength about the {h} axis: guard load {direction.lower()}", unit="lbf*inch")
        loads_v = [cb.SpanLoad(fD * wD, True)]
        loads_h = [cb.SpanLoad(fL * live, uniform_live)]
        label = (f"{combo_text(combo, {'D': 'vertical', 'L': 'horizontal'}, ', ')}, each on its own axis\n"
                 f"{combo.cite}; {biaxial.cite}")
    elif direction == Direction.UPWARD:
        combo = registry.get("ej.combo.bending.upward")
        fD, fL = sh.factor(combo.id, "D"), sh.factor(combo.id, "L")
        # One expression gives both the printed magnitude and the stated sense (ADR 0002).
        # Dead load acts down (+), the guard load up (-).
        net = fD * MD - fL * ML
        sense = "net upward" if net.eval() < Q_(0, "lbf*inch") else "net downward"
        Mv = sh.line(f"M_r_{v}", f'M_"r{v}"', absolute(net),
                     f"Net vertical moment about the {v} axis, guard load opposing dead load: {sense}",
                     unit="lbf*inch")
        loads_v = [cb.SpanLoad(fD * wD, True), cb.SpanLoad(fL * live, uniform_live, opposes=True)]
        label = f"{combo_text(combo)}, net vertical\n{combo.cite}"
    else:
        unknown("Check 1", "direction case", direction, DIRECTIONS)

    def unbraced(M_mid: Sym, loads: list[cb.SpanLoad]) -> Unbraced:
        return Unbraced(L, SPAN_UNBRACED, lambda s: cb.simple_span(s, L, M_mid, loads))

    sh.heading("Section")
    lim = rect_limits(sh, rail, project.top_rail.grade)
    sh.heading(f"Capacity about the {v} axis (vertical load)")
    Mcv = rect_axis_capacity(sh, lim, rail, v, unbraced(Mv, loads_v), flags)
    if Mh is None:
        ratio = sh.line("Ratio", '"Ratio"', Mv / Mcv, "Demand / capacity", cite_ids=("aisc360.eq.B3-2",), ratio=True)
        return BiaxialCase(direction, load_type, "checked", label, demand=Mv.value, capacity=Mcv.value,
                           ratio=ratio.value, lines=sh.lines, axis_v=v, M_v=Mv.value, Mc_v=Mcv.value)
    sh.heading(f"Capacity about the {h} axis (horizontal load)")
    Mch = rect_axis_capacity(sh, lim, rail, h, unbraced(Mh, loads_h), flags)
    sh.heading("Interaction")
    ratio = sh.line("Ratio", '"Ratio"', Mv / Mcv + Mh / Mch, "Both axes combined, with no axial force",
                    cite_ids=(H1_1B, BIAXIAL), ratio=True)
    return BiaxialCase(direction, load_type, "checked", label, demand=Mh.value, capacity=Mch.value,
                       ratio=ratio.value, lines=sh.lines, axis_v=v, M_v=Mv.value, Mc_v=Mcv.value,
                       axis_h=h, M_h=Mh.value, Mc_h=Mch.value)


# ---------------------------------------------------------------------------
# Check 2: deflection
# ---------------------------------------------------------------------------


def _inertia(sh: Sheet, project, rail: Section, direction) -> Sym:
    """The moment of inertia the case deflects on: a round section's one
    value, or a rectangular section's about the axis this case bends."""
    if rail.is_round:
        return sh.given("I", "I", rail.I, "Moment of inertia", rail.source)
    axes = rail_axes(rail, project.top_rail.long_side)
    if direction in (Direction.DOWNWARD, Direction.UPWARD):
        name, load = axes.vertical, "vertical"
    elif direction in (Direction.OUTWARD, Direction.INWARD):
        name, load = axes.horizontal, "horizontal"
    else:
        unknown("Check 2", "direction case", direction, DIRECTIONS)
    return sh.given("I", f"I_{name}", axis(rail, name).I, f"Moment of inertia about the {name} axis ({load} load)",
                    rail.source)


def _deflection_case(registry, project, rail, loading, direction, load_type) -> Case:
    sh = Sheet(registry)
    L = sh.given("L", "L", project.span.value, "Span, simple beam", "Input")
    E = sh.code_value("E", "E", "material.steel.E", "Modulus of elasticity")
    I = _inertia(sh, project, rail, direction)
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
    if not rail.is_round:
        axes = rail_axes(rail, project.top_rail.long_side)
        flags: list[str] = []
        chk = Check(1, "Top rail bending", "M_r", "M_c")

        def rect_case(registry, project, rail, loading, direction, load_type):
            return _rect_bending_case(registry, project, rail, axes, loading, direction, load_type, flags)

        chk.cases = _envelope(rect_case, registry, project, rail, loading)
        chk.flags = list(dict.fromkeys(flags))  # each wall's flag once, however many cases met it
        return chk
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
