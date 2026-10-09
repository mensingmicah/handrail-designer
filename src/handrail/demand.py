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

from handrail.calc import Line, Sheet, Sym
from handrail.checks import COMBO, CONCENTRATED, DOWNWARD, UPWARD, Loading, combo_text
from handrail.project import Project
from handrail.registry import Registry
from handrail.units import Q_

TRIBUTARY = "Stated assumption: the tributary length is the span"

# The three kinds of direction case: downward, upward, and the horizontal
# kind, which is outward, inward and longitudinal (and the reaction sets'
# lateral): the guard load horizontal, the dead load axial.
HORIZONTAL_KIND = "horizontal"


def kind(direction: str) -> str:
    return direction if direction in (DOWNWARD, UPWARD) else HORIZONTAL_KIND


def live_at_post(sh: Sheet, symbol: str, load_type: str, loading: Loading, project: Project, where: str) -> Sym:
    """The guard load reaching the top of the post: P, or w_L over the tributary length."""
    if load_type == CONCENTRATED:
        return sh.given(symbol, loading.P, f"Concentrated guard load P, {where}", "Loading")
    w = sh.given("w_L", loading.w_L, "Uniform guard load", "Loading")
    L = sh.given("L", project.span.value, "Span: the tributary length for the post", "Input")
    return sh.line(symbol, w * L, f"Uniform guard load collected over the span, {where}", cite=TRIBUTARY, unit="lbf")


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

    symbol: str
    value: object
    note: str
    source: str

    def put(self, sh: Sheet) -> Sym:
        return sh.given(self.symbol, self.value, self.note, self.source)


@dataclass(frozen=True)
class Wording:
    """What a demand block prints. ``where`` and ``axial_notes`` are keyed by
    kind (DOWNWARD, HORIZONTAL_KIND, UPWARD); "{direction}" in ``where`` is
    filled with the direction.

    ``factored`` says which horizontal line carries the live-load factor:
    "shear" prints V = gamma_L V_L, then M = V times the arm (the welds);
    "moment" prints M_L = V_L times the arm, then M_r = gamma_L M_L (Check 5).
    """

    where: dict[str, str]
    axial: str                 # symbol of the axial line
    axial_notes: dict[str, str]
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


def demand(registry: Registry, project: Project, loading: Loading, direction: str, load_type: str,
           combos: Combinations, wording: Wording, dead: Given, arm: Sym | Given) -> Demand:
    """The demand for one direction case and load type. ``arm`` is printed
    in the block when it is a Given, and used as is when it is a Sym already
    printed above the block."""
    sh = Sheet(registry)
    sh.heading(f"Demand: {direction.lower()}, {load_type.lower()} load")
    PD = dead.put(sh)
    k = kind(direction)
    where = wording.where[k].format(direction=direction.lower())
    note = wording.axial_notes[k]

    if k == DOWNWARD:
        combo = registry.get(combos.with_dead)
        label = f"{combo_text(combo)}, axial\n{combo.cite}"
        PL = live_at_post(sh, "P_L", load_type, loading, project, where)
        P = sh.line(wording.axial, sh.factor(combo.id, "D") * PD + sh.factor(combo.id, "L") * PL, note, unit="lbf")
        return Demand(label, sh.lines, P, "compression")

    if k == UPWARD:
        combo = registry.get(combos.against_dead)
        label = f"{combo_text(combo)}, net axial\n{combo.cite}"
        PL = live_at_post(sh, "P_L", load_type, loading, project, where)
        # One expression gives both the printed value and the decision (ADR 0002).
        net = sh.factor(combo.id, "L") * PL - sh.factor(combo.id, "D") * PD
        if not net.eval() > Q_(0, "lbf"):
            no_net = f"{float(combo.value['D'])!r}D >= {float(combo.value['L'])!r}L"  # the factors in net
            return Demand(label, sh.lines, None, "tension",
                          remark=f"No net tension ({no_net}); compression covered by downward")
        P = sh.line(wording.axial, net, note, unit="lbf")
        return Demand(label, sh.lines, P, "tension")

    combo = registry.get(combos.with_dead)
    label = f"{combo_text(combo, {'D': 'axial', 'L': 'horizontal'}, ', ')}\n{combo.cite}"
    P = sh.line(wording.axial, sh.factor(combo.id, "D") * PD, note, unit="lbf")
    VL = live_at_post(sh, "V_L", load_type, loading, project, where)
    gamma_L = sh.factor(combo.id, "L")
    if wording.factored == "shear":
        V = sh.line(wording.factored_symbol, gamma_L * VL, wording.factored_note, unit="lbf")
        a = arm.put(sh) if isinstance(arm, Given) else arm
        M = sh.line(wording.moment_symbol, V * a, wording.moment_note, cite_ids=(wording.moment_cite,),
                    unit="lbf*inch")
        return Demand(label, sh.lines, P, "compression", V=V, M=M)
    a = arm.put(sh) if isinstance(arm, Given) else arm
    ML = sh.line(wording.moment_symbol, VL * a, wording.moment_note, cite_ids=(wording.moment_cite,),
                 unit="lbf*inch")
    M = sh.line(wording.factored_symbol, gamma_L * ML, wording.factored_note, unit="lbf*inch")
    return Demand(label, sh.lines, P, "compression", M=M)
