"""The anchor reaction sets (docs/brief/loads-and-envelope.md, S4-4 to S4-7).

LRFD reactions at the top of concrete, for direct input into anchor
software; reporting, not a pass/fail check. Two sets, each simultaneous:

- Lateral: the horizontal guard load at the top of the post, in any
  horizontal direction, 0.9D + 1.6L. V = 1.6L, N = 0.9D compression,
  M = V h (V and M in the same vertical plane).
- Upward, only when 1.6L > 0.9D: N = 1.6L - 0.9D tension, V = 0, M = 0.

Both come from the shared per-direction demand function (demand.py), with
the reaction combination and the moment arm h, where Checks 5 and 7 use
the ASD combinations and h - t_p. Each set uses the larger guard load
type at the top of the post, P or w s, and names it (S4-5). D is the top
rail, the intermediate rail, the post (over h - t_p, as D at the post)
and the baseplate, W_bp = rho B N t_p, which enters the reactions only
(S4-6).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from handrail.calc import Line, Sheet, fmt_quantity, mtext
from handrail.checks import CONCENTRATED, DISTRIBUTED, DOWNWARD, UPWARD, Loading
from handrail.demand import HORIZONTAL_KIND, Combinations, Given, Wording, demand
from handrail.project import Project
from handrail.registry import Registry

COMBO = "ej.combo.reaction"
LOCATION = "ej.reaction.location"
LATERAL = "Lateral"
BOTH = "Concentrated and distributed"  # the load type named when P = w s (S4-5)

# 0.9D + 1.6L in both sets: with the dead load (lateral) and against it (upward).
COMBINATIONS = Combinations(with_dead=COMBO, against_dead=COMBO)

# The calc lines print the factored base forces V_u, N_u and M_u; the
# reaction table prints them as V, N and M (S4-7). N_u prints as a
# magnitude, its sense in the note; the table gives N its sign.
WORDING = Wording(
    where={DOWNWARD: "vertical at the top of the post",
           HORIZONTAL_KIND: "horizontal at the top of the post, in any horizontal direction",
           UPWARD: "upward at the top of the post"},
    axial="abs(N_u)",
    axial_notes={DOWNWARD: "Axial force at the base, compression",
                 HORIZONTAL_KIND: "Axial force at the base: dead load, compression",
                 UPWARD: "Axial force at the base: net tension (uplift), guard load opposing dead load"},
    factored="shear", factored_symbol="V_u", factored_note="Base shear",
    moment_symbol="M_u", moment_note="Base moment at the top of concrete: V_u at the top rail centerline, arm h",
    moment_cite=LOCATION,
)


@dataclass
class ReactionSet:
    name: str                  # "Lateral" or "Upward"
    load_type: str             # the governing guard load type, as named (S4-5)
    combination: str           # the label, as printed
    present: bool              # False: no upward set (no net uplift)
    V: object = None           # factored base shear (lbf)
    N: object = None           # factored axial force, signed, tension positive (lbf)
    M: object = None           # factored base moment (lbf*inch)
    lines: list[Line] = field(default_factory=list)
    remark: str = ""           # why the set is absent


@dataclass
class Reactions:
    head: list[Line]                     # the dead load at the base and the governing load type
    dead: list[tuple[str, object]]       # the D breakdown as the table prints it, then the total
    sets: list[ReactionSet]
    lateral_note: str                    # printed with the lateral set (S4-4)


def _governing_load_type(sh: Sheet, project: Project, loading: Loading) -> tuple[str, str]:
    """The larger guard load type at the top of the post (S4-5): (the type the
    demand runs, the type the set names)."""
    sh.heading("Governing guard load type")
    P = sh.given("P", loading.P, "Concentrated guard load P, at the top of the post", "Loading")
    if loading.exempt:
        sh.decision(mtext("Uniform load exempt"), "Concentrated load P governs",
                    "With the exemption, P is the only guard load type", cite_ids=(LOCATION,))
        return CONCENTRATED, CONCENTRATED
    w = sh.given("w_L", loading.w_L, "Uniform guard load", "Loading")
    L = sh.given("L", project.span.value, "Span: the tributary length for the post", "Input")
    wL = sh.line("w_L L", w * L, "Uniform guard load collected over the span, at the top of the post",
                 cite_ids=(LOCATION,), unit="lbf")
    # One comparison gives both the printed statement and the choice (ADR 0002).
    # Equal to within rounding of the inputs is a tie: one set names both.
    if abs(P.value - wL.value) <= 1e-9 * max(P.value, wL.value):
        sh.decision(f"P = {fmt_quantity(P.value)} = w_L L = {fmt_quantity(wL.value)}", "Both types, one set",
                    "Equal at the top of the post: one set names both", cite_ids=(LOCATION,))
        return CONCENTRATED, BOTH
    if P.value > wL.value:
        sh.decision(f"P = {fmt_quantity(P.value)} > w_L L = {fmt_quantity(wL.value)}",
                    "Concentrated load P governs", "The larger at the top of the post", cite_ids=(LOCATION,))
        return CONCENTRATED, CONCENTRATED
    sh.decision(f"w_L L = {fmt_quantity(wL.value)} > P = {fmt_quantity(P.value)}",
                "Distributed load governs", "The larger at the top of the post", cite_ids=(LOCATION,))
    return DISTRIBUTED, DISTRIBUTED


def reaction_sets(registry: Registry, project: Project, loading: Loading) -> Reactions:
    head = Sheet(registry)
    head.heading("Dead load at the base")
    parts = [head.given('D_"rail"', loading.D_rail, "Top rail", "Loading")]
    names = ["Top rail"]
    if loading.D_int is not None:
        parts.append(head.given('D_"int"', loading.D_int, "Intermediate rail", "Loading"))
        names.append("Intermediate rail")
    parts.append(head.given('D_"post"', loading.D_post, "Post, over h - t_p", "Loading"))
    names.append("Post")
    rho = head.code_value("rho", "material.steel.density", "Steel unit weight")
    B = head.given("B", project.baseplate.B.value, "Baseplate, parallel to the rail", "Input")
    N = head.given("N", project.baseplate.N.value, "Baseplate, perpendicular to the rail", "Input")
    tp = head.given("t_p", project.baseplate_thickness.value, "Baseplate thickness", "Input")
    W_bp = head.line('W_"bp"', rho * B * N * tp, "Baseplate weight: in the reaction sets only, below the critical "
                     "section of Checks 5 and 7", cite_ids=(LOCATION,), unit="lbf")
    parts.append(W_bp)
    names.append("Baseplate")
    total = parts[0]
    for p in parts[1:]:
        total = total + p
    D = head.line("D", total, "Dead load at the base", cite_ids=(LOCATION,), unit="lbf")
    run_type, named = _governing_load_type(head, project, loading)

    dead = Given("D", D.value, "Dead load at the base", "Reactions")
    arm = Given("h", project.post_height.value, "Moment arm: top rail centerline to top of concrete", "Input")
    sets = []
    for name in (LATERAL, UPWARD):
        d = demand(registry, project, loading, name, run_type, COMBINATIONS, WORDING, dead, arm)
        if d.P is None:
            f = registry.get(COMBO).value  # the factors in the net uplift the demand found not positive
            sets.append(ReactionSet(name, named, d.label, False, lines=d.lines,
                                    remark=f"No net uplift ({float(f['D'])!r}D >= {float(f['L'])!r}L): "
                                           f"no upward set"))
            continue
        if name == LATERAL:
            sets.append(ReactionSet(name, named, d.label, True, V=d.V.value, N=-d.P.value, M=d.M.value,
                                    lines=d.lines))
        else:
            zero_V, zero_M = 0 * d.P.value, 0 * d.P.value * project.post_height.value
            sets.append(ReactionSet(name, named, d.label, True, V=zero_V, N=d.P.value, M=zero_M, lines=d.lines))
    dead_rows = [(n, p.value) for n, p in zip(names, parts)] + [("Total D", D.value)]
    return Reactions(head=head.lines, dead=dead_rows, sets=sets,
                     lateral_note=registry.get("ej.reaction.lateral_note").value)
