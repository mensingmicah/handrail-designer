"""Check 4: the intermediate rail (docs/plans/slice-4.md).

Check 4a is the member: the component load P_c as a point load at midspan
of the simple span (S4-3), in two cases (S4-10):

- Horizontal: P_c alone, not combined with dead load. M = P_c L/4;
  deflection P_c L^3/(48EI), live load only.
- Downward: P_c plus the intermediate rail's dead load on the same axis,
  ASD D + L. M = w_D L^2/8 + P_c L/4; deflection D + L, the serviceability
  combination of Check 2.

Neither case is concurrent with the top-rail guard loads. For a round
section the downward case always governs; the horizontal case is listed so
the envelope is explicit. The deflection limit is the intermediate rail's
own (own section) or Check 2's (same as the top rail), each bypassable.

Same as the top rail with P_c <= P, Check 4a is not computed: Checks 1 and
2 already run that section, span and dead load at P (S4-2). With no
intermediate rail it prints "none".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from handrail import beams
from handrail.calc import Const, Line, Sheet, compare, fmt_quantity_plain, term
from handrail.flexure import flexural_capacity
from handrail.loading import COMBO, combo_text
from handrail.directions import COMPONENT, COMPONENT_DIRECTIONS, DOWNWARD, HORIZONTAL, Direction, unknown
from handrail.project import NO_INTERMEDIATE, SAME_AS_TOP, DeflectionLimit, Member, Project
from handrail.registry import Registry
from handrail.results import Case, Check, Loading
from handrail.shapes import DB, PipeSection

BENDING, DEFLECTION = "Bending", "Deflection"
MIDSPAN, DOWN = "ej.component.midspan", "ej.component.downward"
NONE_TEXT = "None: no intermediate rail."


@dataclass
class ComponentCase(Case):
    """A Check 4a case: one direction of the component load and one limit state."""

    limit_state: str = ""  # BENDING or DEFLECTION

    @property
    def label(self) -> str:
        return f"{self.direction}, {self.limit_state.lower()}"


def _bending_case(registry: Registry, project: Project, loading: Loading, cap, head: list[Line],
                  direction: Direction) -> ComponentCase:
    sh = Sheet(registry)
    sh.lines.extend(head)
    sh.heading("Capacity")
    sh.lines.extend(cap.lines)
    sh.heading(f"Demand: {direction.lower()}, component load")
    combo, down = registry.get(COMBO), registry.get(DOWN)
    L = sh.given("L", "L", project.span.value, "Span, simple beam", "Input")
    Pc = sh.given("P_c", "P_c", loading.P_c, "Component load, a point load at midspan", "Loading")
    ML = beams.point_moment(sh, "M_L", "M_L", Pc, L, "Component load moment, midspan", cite_ids=(MIDSPAN,))
    if direction == DOWNWARD:
        wD = sh.given("w_D_int", 'w_(D,"int")', loading.w_D_int, "Intermediate rail self-weight", "Loading")
        MD = beams.uniform_moment(sh, "M_D", "M_D", wD, L, "Dead-load moment, midspan")
        M = sh.line("M_a", "M_a", sh.factor(combo.id, "D") * MD + sh.factor(combo.id, "L") * ML,
                    "Required flexural strength: D and L on the same axis", cite_ids=(down.id,), unit="lbf*inch")
        label = f"{combo_text(combo)}, vertical\n{combo.cite}; {down.cite}"
    elif direction == HORIZONTAL:
        M = sh.line("M_a", "M_a", sh.factor(combo.id, "L") * ML,
                    "Required flexural strength: the component load alone, not combined with dead load",
                    cite_ids=(down.id,), unit="lbf*inch")
        label = f"{float(combo.value['L'])!r}L horizontal, alone\n{combo.cite}; {down.cite}"
    else:
        unknown("Check 4a", "component load direction", direction, COMPONENT_DIRECTIONS)
    ratio = sh.line("Ratio", '"Ratio"', M / cap.allow, "Demand / capacity", cite_ids=("aisc360.eq.B3-2",), ratio=True)
    return ComponentCase(direction, COMPONENT, "checked", label, demand=M.value, capacity=cap.allow.value,
                         ratio=ratio.value, lines=sh.lines, limit_state=BENDING)


def _deflection_case(registry: Registry, project: Project, inter: PipeSection, loading: Loading,
                     limit: DeflectionLimit, head: list[Line], direction: Direction) -> ComponentCase:
    sh = Sheet(registry)
    sh.lines.extend(head)
    L = sh.given("L", "L", project.span.value, "Span, simple beam", "Input")
    E = sh.code_value("E", "E", "material.steel.E", "Modulus of elasticity")
    I = sh.given("I_int", 'I_"int"', inter.I, f"Moment of inertia, {inter.label}", DB)
    Pc = sh.given("P_c", "P_c", loading.P_c, "Component load, a point load at midspan", "Loading")
    DL = beams.point_deflection(sh, "Delta_L", "Delta_L", Pc, L, E, I, "Component load deflection, midspan",
                                cite_ids=(MIDSPAN,))
    if direction == DOWNWARD:
        combo = registry.get("ej.combo.deflection.D_plus_L")
        wD = sh.given("w_D_int", 'w_(D,"int")', loading.w_D_int, "Intermediate rail self-weight", "Loading")
        DD = beams.uniform_deflection(sh, "Delta_D", "Delta_D", wD, L, E, I, "Dead-load deflection, midspan")
        D = sh.line("Delta", "Delta", sh.factor(combo.id, "D") * DD + sh.factor(combo.id, "L") * DL,
                    "D and L on the same (vertical) axis", cite_ids=(DOWN,), unit="inch")
        axis = "vertical"
    elif direction == HORIZONTAL:
        combo = registry.get("ej.combo.deflection.L_only")
        D = sh.line("Delta", "Delta", sh.factor(combo.id, "L") * DL, "Component load only", unit="inch")
        axis = "horizontal"
    else:
        unknown("Check 4a", "component load direction", direction, COMPONENT_DIRECTIONS)
    r = limit.ratio
    lim = Const(int(r) if float(r).is_integer() else r)
    Dallow = sh.line("Delta_allow", 'Delta_"allow"', L / lim, f"Limit L/{lim.value}", cite_ids=("ej.deflection.limit",),
                     unit="inch")
    ratio = sh.line("Ratio", '"Ratio"', D / Dallow, "Deflection / limit", cite_ids=("ej.deflection.limit",), ratio=True)
    return ComponentCase(direction, COMPONENT, "checked", f"{combo_text(combo)}, {axis}\n{combo.cite}",
                         demand=D.value, capacity=Dallow.value, ratio=ratio.value, lines=sh.lines,
                         limit_state=DEFLECTION)


def check_4a(registry: Registry, project: Project, inter: PipeSection | None, loading: Loading) -> Check:
    """The intermediate rail member: the full check, the same-as-top
    observation (S4-2), or "none"."""
    chk = Check("4a", "Intermediate rail", "M_a, Delta", 'M_n / Omega_b, Delta_"allow"')
    state = project.intermediate_rail.state
    if state == NO_INTERMEDIATE:
        chk.observation, chk.result = NONE_TEXT, "None"
        return chk

    same = state == SAME_AS_TOP
    limit = project.rail_deflection if same else project.intermediate_rail.deflection
    head: list[Line] = []
    if same:
        P, Pc = loading.P, loading.P_c
        # One comparison: it decides, and when it fails it prints what it found (ADR 0002).
        covered = compare(term("P_c", Pc), "<=", term("P", P))
        if covered:
            text = registry.get("ej.intermediate.same_as_top").value
            chk.observation = text.format(Pc=fmt_quantity_plain(Pc), P=fmt_quantity_plain(P))
            if limit.bypass:
                chk.observation += " Deflection follows Check 2, which the engineer bypassed."
            chk.result = "Controlled by Checks 1 and 2"
            return chk
        # The one guard (S4-2): a component load above P runs the full check.
        sh = Sheet(registry)
        sh.decision(covered, "Computed in full",
                    "Same section as the top rail, but the component load exceeds the concentrated guard load, "
                    "so Checks 1 and 2 do not cover it", cite_ids=("ej.intermediate.same_as_top",))
        head = sh.lines

    # Past the "none" return above there is an intermediate rail: its section and its member.
    inter = cast(PipeSection, inter)
    grade = cast(Member, project.intermediate_member).grade
    cap = flexural_capacity(registry, inter, grade)
    chk.flags = cap.flags
    for direction in COMPONENT_DIRECTIONS:
        chk.cases.append(_bending_case(registry, project, loading, cap, head, direction))
    for direction in COMPONENT_DIRECTIONS:
        if limit.bypass:
            chk.cases.append(ComponentCase(direction, COMPONENT, "bypassed", limit_state=DEFLECTION,
                                           remark="Deflection bypassed by engineer"))
        else:
            chk.cases.append(_deflection_case(registry, project, inter, loading, limit, head, direction))
    return chk
