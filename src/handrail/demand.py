"""The demand in each direction case: one function for the post, the welds
and, from slice 4, the anchor reaction sets (docs/plans/slice-4.md; issue #4).

Every direction case puts a guard load at the top of the post (or on the
rail at the post), with the dead load acting axially:

- Downward: P = gamma_D D + gamma_L L, compression; no moment.
- Outward, inward, longitudinal (and the reaction sets' lateral): P =
  gamma_D D, compression; the guard load horizontal, with a moment equal
  to it times the moment arm.
- Upward: P = gamma_L L - gamma_D D, tension, or no net tension.

The load combination is data: registry entries holding the D and L factors,
and the printed label is generated from them. The moment arm is an input:
h - t_p for Checks 5 and 7 (the top of the baseplate), the eccentricity e
for Check 3, and h for the reaction sets (the top of concrete). What a
demand block prints, its symbols and notes, is the caller's Wording, so
each check prints exactly what it printed before the function was shared.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from handrail.calc import Line, Sheet, Sym, Term, compare
from handrail.directions import CONCENTRATED, DISTRIBUTED, LOAD_TYPES, Direction, Kind, LoadType, kind, unknown
from handrail.loading import COMBO, combo_text
from handrail.project import Project
from handrail.registry import Registry
from handrail.results import Loading

TRIBUTARY = "Stated assumption: the tributary length is the span"


def live_at_post(sh: Sheet, key: str, symbol: str, load_type: LoadType, loading: Loading, project: Project,
                 where: str) -> Sym:
    """The guard load reaching the top of the post: P, or w_L over the tributary length."""
    if load_type == CONCENTRATED:
        return sh.given(key, symbol, loading.P, f"Concentrated guard load P, {where}", "Loading")
    if load_type == DISTRIBUTED:
        w = sh.given("w_L", "w_L", loading.w_L, "Uniform guard load", "Loading")
        L = sh.given("L", "L", project.span.value, "Span: the tributary length for the post", "Input")
        return sh.line(key, symbol, w * L, f"Uniform guard load collected over the span, {where}", cite=TRIBUTARY,
                       unit="lbf")
    unknown("Guard load at the post", "guard load type", load_type, LOAD_TYPES)


@dataclass(frozen=True)
class Combinations:
    """The load combinations a demand uses, each a registry entry holding the
    D and L factors: one where the dead load acts with or beside the guard
    load (downward and horizontal cases), one where the guard load opposes
    it (upward)."""

    with_dead: str
    against_dead: str


# ASCE 7-22 ASD D + L, and 0.6D + 1.0L for upward (engineering judgement):
# Checks 3, 5 and 7.
ASD = Combinations(with_dead=COMBO, against_dead="ej.combo.bending.upward")


@dataclass(frozen=True)
class Given:
    """A value the demand block prints as a given line."""

    key: str
    symbol: str
    value: Any
    note: str
    source: str

    def put(self, sh: Sheet) -> Sym:
        return sh.given(self.key, self.symbol, self.value, self.note, self.source)


@dataclass(frozen=True)
class Wording:
    """What a demand block prints. ``where`` and ``axial_notes`` are keyed by
    the kind of direction case (directions.Kind); "{direction}" in ``where``
    is filled with the direction.

    ``factored`` says which horizontal line carries the live-load factor:
    "shear" prints V = gamma_L V_L, then M = V times the arm (the welds);
    "moment" prints M_L = V_L times the arm, then M_r = gamma_L M_L (Check 5).

    The symbols are the caller's; the line keys are the demand's own and the
    same for every caller: "P" the axial force, "P_L" or "V_L" the guard
    load at the post, "V" the factored horizontal force (shear wording),
    "M_L" the unfactored moment (moment wording) and "M" the factored moment.
    """

    where: dict[Kind, str]
    axial: str                 # symbol of the axial line
    axial_notes: dict[Kind, str]
    factored: str              # "shear" or "moment"
    factored_symbol: str       # "V" (shear) or "M_r" (moment)
    factored_note: str
    moment_symbol: str         # the line arm times the horizontal load: "M" or "M_L"
    moment_note: str
    moment_cite: str           # registry entry for that line


@dataclass
class Demand:
    """One direction case's demand. P is None when the upward case has no
    net tension; V is the factored horizontal force where the wording prints
    it; M is the factored moment, horizontal cases only."""

    label: str                 # the combination, as the envelope prints it
    lines: list[Line]
    P: Sym | None
    sense: str                 # "compression" or "tension"
    V: Sym | None = None
    M: Sym | None = None
    remark: str = ""           # why there is no P
    no_net: str = ""           # the comparison that found no net tension, as text: "0.6D >= 1.0L"


def demand(registry: Registry, project: Project, loading: Loading, direction: Direction, load_type: LoadType,
           combos: Combinations, wording: Wording, dead: Given, arm: Sym | Given) -> Demand:
    """The demand for one direction case and load type. ``arm`` is printed
    in the block when it is a Given, and used as is when it is a Sym already
    printed above the block. A direction that is not a direction case stops
    (directions.kind), before anything is computed."""
    k = kind(direction)
    sh = Sheet(registry)
    sh.heading(f"Demand: {direction.lower()}, {load_type.lower()} load")
    PD = dead.put(sh)
    where = wording.where[k].format(direction=direction.lower())
    note = wording.axial_notes[k]

    if k is Kind.DOWNWARD:
        combo = registry.get(combos.with_dead)
        label = f"{combo_text(combo)}, axial\n{combo.cite}"
        PL = live_at_post(sh, "P_L", "P_L", load_type, loading, project, where)
        P = sh.line("P", wording.axial, sh.factor(combo.id, "D") * PD + sh.factor(combo.id, "L") * PL, note, unit="lbf")
        return Demand(label, sh.lines, P, "compression")

    if k is Kind.UPWARD:
        combo = registry.get(combos.against_dead)
        label = f"{combo_text(combo)}, net axial\n{combo.cite}"
        PL = live_at_post(sh, "P_L", "P_L", load_type, loading, project, where)
        # The two factored terms give the printed value (their difference) and
        # the decision (their comparison), which prints as it was evaluated (ADR 0002).
        up, down = sh.factor(combo.id, "L") * PL, sh.factor(combo.id, "D") * PD
        net = up - down
        no_tension = compare(Term(f"{float(combo.value['D'])!r}D", down.eval()), ">=",
                             Term(f"{float(combo.value['L'])!r}L", up.eval()))
        if no_tension:
            return Demand(label, sh.lines, None, "tension", no_net=no_tension.text,
                          remark=f"No net tension ({no_tension.text}); compression covered by downward")
        P = sh.line("P", wording.axial, net, note, unit="lbf")
        return Demand(label, sh.lines, P, "tension")

    if k is not Kind.HORIZONTAL:
        unknown("Demand", "kind of direction case", k, Kind)
    combo = registry.get(combos.with_dead)
    label = f"{combo_text(combo, {'D': 'axial', 'L': 'horizontal'}, ', ')}\n{combo.cite}"
    P = sh.line("P", wording.axial, sh.factor(combo.id, "D") * PD, note, unit="lbf")
    VL = live_at_post(sh, "V_L", "V_L", load_type, loading, project, where)
    gamma_L = sh.factor(combo.id, "L")
    if wording.factored == "shear":
        V = sh.line("V", wording.factored_symbol, gamma_L * VL, wording.factored_note, unit="lbf")
        a = arm.put(sh) if isinstance(arm, Given) else arm
        M = sh.line("M", wording.moment_symbol, V * a, wording.moment_note, cite_ids=(wording.moment_cite,),
                    unit="lbf*inch")
        return Demand(label, sh.lines, P, "compression", V=V, M=M)
    a = arm.put(sh) if isinstance(arm, Given) else arm
    ML = sh.line("M_L", wording.moment_symbol, VL * a, wording.moment_note, cite_ids=(wording.moment_cite,),
                 unit="lbf*inch")
    M = sh.line("M", wording.factored_symbol, gamma_L * ML, wording.factored_note, unit="lbf*inch")
    return Demand(label, sh.lines, P, "compression", M=M)
