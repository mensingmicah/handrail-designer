"""Simple-beam formulas, AISC Manual Table 3-23, each written once (ADR 0002).

Checks 1 and 2 (the top rail) and Check 4a (the intermediate rail) use
them. Each takes the load as the symbol it prints with (P, w_L, P_c,
w_D, w_(D,"int")), the line's own key, symbol and note, and any citation
beyond the Table 3-23 case, which prints after it.

The two moments at a distance x from a support are for Cb (cb.py), which
needs the moment at the quarter points of the span. They return the
expression only, for the line that sums the loads of a case.
"""

from __future__ import annotations

from handrail.calc import Expr, Sheet, Sym

CASE1_M, CASE1_DELTA = "aisc_manual.t3-23.case1.M", "aisc_manual.t3-23.case1.delta"
CASE7_M, CASE7_DELTA = "aisc_manual.t3-23.case7.M", "aisc_manual.t3-23.case7.delta"
CASE1_MX, CASE7_MX = "aisc_manual.t3-23.case1.Mx", "aisc_manual.t3-23.case7.Mx"


def uniform_moment_at(w: Expr, L: Sym, x: Expr) -> Expr:
    """Uniformly distributed load: Mx = w x (L - x)/2 (Case 1)."""
    return w * x * (L - x) / 2


def point_moment_at(P: Expr, x: Expr) -> Expr:
    """Concentrated load at center: Mx = P x/2, for x no more than L/2 (Case 7)."""
    return P * x / 2


def point_moment(sh: Sheet, key: str, symbol: str, P: Sym, L: Sym, note: str,
                 cite_ids: tuple[str, ...] = ()) -> Sym:
    """Concentrated load at center: M = P L/4 (Case 7)."""
    return sh.line(key, symbol, P * L / 4, note, cite_ids=(CASE7_M, *cite_ids), unit="lbf*inch")


def uniform_moment(sh: Sheet, key: str, symbol: str, w: Sym, L: Sym, note: str,
                   cite_ids: tuple[str, ...] = ()) -> Sym:
    """Uniformly distributed load: M = w L^2/8 (Case 1)."""
    return sh.line(key, symbol, w * L**2 / 8, note, cite_ids=(CASE1_M, *cite_ids), unit="lbf*inch")


def point_deflection(sh: Sheet, key: str, symbol: str, P: Sym, L: Sym, E: Sym, I: Sym, note: str,
                     cite_ids: tuple[str, ...] = ()) -> Sym:
    """Concentrated load at center: Delta = P L^3/(48 E I) (Case 7)."""
    return sh.line(key, symbol, P * L**3 / (48 * E * I), note, cite_ids=(CASE7_DELTA, *cite_ids), unit="inch")


def uniform_deflection(sh: Sheet, key: str, symbol: str, w: Sym, L: Sym, E: Sym, I: Sym, note: str,
                       cite_ids: tuple[str, ...] = ()) -> Sym:
    """Uniformly distributed load: Delta = 5 w L^4/(384 E I) (Case 1)."""
    return sh.line(key, symbol, 5 * w * L**4 / (384 * E * I), note, cite_ids=(CASE1_DELTA, *cite_ids), unit="inch")
