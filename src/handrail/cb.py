"""The lateral-torsional buckling modification factor Cb (AISC 360-22
Eq. F1-1), written once (docs/brief/checks.md, S6-4).

Cb comes from the moment diagram of the load case being checked, on the
axis being bent: the maximum moment in the unbraced length and the moments
at its quarter point, centerline and three-quarter point. Every member this
tool bends with a lateral-torsional limit state is either a simple span
under a uniform load, a point load at midspan, or both (a rail), or a
cantilever (the post), so those are the two functions here. Slice 7's flat
bar uses them unchanged.

A rail's unbraced length is its span, so the quarter points of the
unbraced length are the quarter points of the span.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from handrail import beams
from handrail.calc import Expr, Sheet, Sym, absolute, compare, maximum

F1_1 = "aisc360.eq.F1-1"
CANTILEVER = "aisc360.F1.c.cantilever_cb"


@dataclass(frozen=True)
class SpanLoad:
    """One load on the simple span, as its load case factors it."""

    load: Expr             # the factored load: a force per length, or a force at midspan
    uniform: bool          # a uniform load; otherwise a point load at midspan
    opposes: bool = False  # acts against the other load (the upward case)


def _moment_at(loads: Sequence[SpanLoad], L: Sym, x: Expr) -> Expr:
    """The net moment at distance x from a support, x no more than L/2."""
    total: Expr | None = None
    for ld in loads:
        part = beams.uniform_moment_at(ld.load, L, x) if ld.uniform else beams.point_moment_at(ld.load, x)
        if total is None:
            total = part
        else:
            total = total - part if ld.opposes else total + part
    if total is None:
        raise ValueError("Cb needs at least one load on the span")
    return total


def simple_span(sh: Sheet, L: Sym, M_mid: Sym, loads: Sequence[SpanLoad]) -> Sym:
    """Cb for a simple span of unbraced length L under these loads, printing
    the quarter-point moments, the maximum moment and Eq. F1-1. ``M_mid`` is
    the moment these loads give at midspan, the case's required moment
    about this axis, already printed.

    With every load acting the same way the maximum is at midspan. A point
    load opposing a uniform one (the upward case) can leave a second
    extreme between the support and midspan, where the diagram has
    reversed; it is found and compared when the point load is the smaller.
    """
    cites = tuple(dict.fromkeys(beams.CASE1_MX if ld.uniform else beams.CASE7_MX for ld in loads))
    opposed = any(ld.opposes for ld in loads)

    def moment(x: Expr) -> Expr:
        net = _moment_at(loads, L, x)
        return absolute(net) if opposed else net

    x_A = sh.line("x_A", "x_A", L / 4, "Quarter point of the unbraced length", unit="inch")
    M_A = sh.line("M_A", "M_A", moment(x_A), "Moment at the quarter point", cite_ids=cites, unit="lbf*inch")
    M_B = sh.line("M_B", "M_B", M_mid, "Moment at the centerline: the required moment about this axis",
                  unit="lbf*inch")
    M_C = sh.line("M_C", "M_C", M_A, "Moment at the three-quarter point: the diagram is symmetric about midspan",
                  unit="lbf*inch")

    M_max = None
    uniform = [ld for ld in loads if ld.uniform]
    point = [ld for ld in loads if not ld.uniform]
    if opposed and len(uniform) == 1 and len(point) == 1:
        # M(x) = P x/2 - w x (L - x)/2 has a stationary point at x0 = L/2 -
        # P/(2w), inside the half span when P < w L.
        P = sh.line("P_net", 'P_"net"', point[0].load, "Point load, factored", unit="lbf")
        W = sh.line("W_net", 'W_"net"', uniform[0].load * L, "Uniform load over the span, factored", unit="lbf")
        holds = compare(P.stated(), ">=", W.stated())
        if holds:
            sh.decision(holds, "The moment does not reverse: maximum at midspan", "")
        else:
            sh.decision(holds, "The moment reverses between the support and midspan",
                        "The maximum is the larger of the moment at midspan and the opposite moment at x_0")
            x_0 = sh.line("x_0", "x_0", L / 2 - point[0].load / (2 * uniform[0].load),
                          "Where the opposite moment peaks", cite_ids=cites, unit="inch")
            M_0 = sh.line("M_0", "M_0", moment(x_0), "Moment at x_0", cite_ids=cites, unit="lbf*inch")
            M_max = sh.line("M_max", 'M_"max"', maximum(M_B, M_0), "Maximum moment in the unbraced length",
                            unit="lbf*inch")
    if M_max is None:
        M_max = sh.line("M_max", 'M_"max"', M_B, "Maximum moment in the unbraced length: at midspan",
                        unit="lbf*inch")

    c = F1_1 + ".coeff_"
    return sh.line(
        "C_b", "C_b",
        sh.coeff(c + "numerator") * M_max
        / (sh.coeff(c + "max") * M_max + sh.coeff(c + "quarter") * M_A + sh.coeff(c + "center") * M_B
           + sh.coeff(c + "quarter") * M_C),
        "Lateral-torsional buckling modification factor, from this case's moment diagram", cite_ids=(F1_1,))


def cantilever(sh: Sheet) -> Sym:
    """Cb for a cantilever whose free end is unbraced: 1.0 (AISC 360-22 F1(c))."""
    return sh.code_value("C_b", "C_b", CANTILEVER,
                         "Lateral-torsional buckling modification factor: a cantilever with its free end unbraced")
