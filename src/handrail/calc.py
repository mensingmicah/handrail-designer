"""Calc lines: each line of the printed calc is defined once (ADR 0002).

A formula is written once in Python as an expression built from ``Sym`` and
``Const`` objects, for example ``P * L / 4``. Python operators on these build
an expression tree instead of a number. The same tree is then

- evaluated, with pint units, to give the value the checks use, and
- rendered twice for the PDF: symbolically (PL/4) and with the values
  substituted ((200 lb)(84 in)/4).

The printed formula and the computed one are the same object, so they cannot
drift apart. Rendering produces Typst math source.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

from handrail.registry import Entry, Registry
from handrail.units import Q_, ureg

# ---------------------------------------------------------------------------
# Number and unit display (docs/BRIEF.md, Output: 3 significant figures,
# ratios to 2 decimals, fixed units lb, lb-in, ksi, in, in^3, in^4)
# ---------------------------------------------------------------------------

# (pint unit to display in, Typst unit text, exponent printed on the unit)
_DISPLAY = [
    (ureg.inch, "in", None),
    (ureg.lbf, "lb", None),
    (ureg.lbf * ureg.inch, "lb-in", None),
    (ureg.ksi, "ksi", None),
    (ureg.lbf / ureg.inch, "lb/in", None),
    (ureg.inch**2, "in", 2),
    (ureg.inch**3, "in", 3),
    (ureg.inch**4, "in", 4),
]


def fmt_sig(x: float, sig: int = 3) -> str:
    """Format to ``sig`` significant figures, with thousands separators."""
    if x == 0 or not math.isfinite(x):
        return "0" if x == 0 else str(x)
    decimals = sig - 1 - math.floor(math.log10(abs(x)))
    r = round(x, decimals)
    # Rounding can carry up a digit (9.996 -> 10.0); recompute decimals.
    if r != 0 and math.floor(math.log10(abs(r))) != math.floor(math.log10(abs(x))):
        decimals -= 1
        r = round(x, decimals)
    if decimals <= 0:
        return f"{int(round(r)):,}"
    return f"{r:,.{decimals}f}"


def fmt_ratio(x: float) -> str:
    return f"{x:.2f}"


def display(q) -> tuple[float, str, int | None]:
    """Return (magnitude, unit text, unit exponent) in the fixed display units."""
    if not hasattr(q, "units"):
        return float(q), "", None
    if q.dimensionless:
        return float(q.to("dimensionless").magnitude), "", None
    for unit, text, exp in _DISPLAY:
        if q.dimensionality == unit.dimensionality:
            return q.to(unit).magnitude, text, exp
    raise ValueError(f"no display unit for {q.units} ({q.dimensionality})")


def fmt_quantity(q, ratio: bool = False) -> str:
    """Typst math for a quantity: a text block like "4,200 lb-in", or "0.293 in"^4."""
    mag, unit, exp = display(q)
    num = fmt_ratio(mag) if ratio else fmt_sig(mag)
    text = f'"{num} {unit}"' if unit else f'"{num}"'
    return f"{text}^{exp}" if exp else text


def fmt_quantity_plain(q, ratio: bool = False) -> str:
    """Plain text (not math) for tables: '4,200 lb-in', '0.293 in^4'."""
    mag, unit, exp = display(q)
    num = fmt_ratio(mag) if ratio else fmt_sig(mag)
    sup = {2: "²", 3: "³", 4: "⁴"}.get(exp, "")
    return f"{num} {unit}{sup}".strip()


# ---------------------------------------------------------------------------
# Expression tree
# ---------------------------------------------------------------------------

# Precedence, for deciding where parentheses are needed when rendering.
_ADD, _MUL, _POW, _ATOM = 1, 2, 3, 4


class Expr:
    prec = _ATOM

    def eval(self): ...
    def symbolic(self) -> str: ...
    def substituted(self) -> str: ...

    def entries(self) -> list[Entry]:
        return []

    # Operators build the tree rather than computing.
    def __add__(self, o): return BinOp("+", self, _wrap(o))
    def __radd__(self, o): return BinOp("+", _wrap(o), self)
    def __sub__(self, o): return BinOp("-", self, _wrap(o))
    def __rsub__(self, o): return BinOp("-", _wrap(o), self)
    def __mul__(self, o): return BinOp("*", self, _wrap(o))
    def __rmul__(self, o): return BinOp("*", _wrap(o), self)
    def __truediv__(self, o): return BinOp("/", self, _wrap(o))
    def __rtruediv__(self, o): return BinOp("/", _wrap(o), self)
    def __pow__(self, n): return BinOp("^", self, _wrap(n))


def _wrap(x) -> Expr:
    if isinstance(x, Expr):
        return x
    if isinstance(x, (int, float)):
        return Const(x)
    raise TypeError(f"cannot use {type(x).__name__} in a calc expression")


def _paren(e: Expr, text: str, min_prec: int) -> str:
    return f"({text})" if e.prec < min_prec else text


@dataclass(eq=False)
class Sym(Expr):
    """A named quantity: an input, a registry value or a computed line."""

    typst: str       # Typst math for the symbol, e.g. 'M_n', 'Omega_b', 't_"des"'
    value: object    # pint quantity or float

    def eval(self):
        return self.value

    def symbolic(self) -> str:
        return self.typst

    def substituted(self) -> str:
        text = fmt_quantity(self.value)
        mag = display(self.value)[0]
        # Parenthesize quantities with units, or negatives, so juxtaposition reads.
        needs = (hasattr(self.value, "units") and not self.value.dimensionless) or mag < 0
        return f"({text})" if needs else text


@dataclass(eq=False)
class Const(Expr):
    """A pure number in a formula. If it comes from the registry, carry the entry."""

    value: float
    entry: Entry | None = None

    def eval(self):
        return self.value

    def symbolic(self) -> str:
        return f'"{_plain_number(self.value)}"'

    def substituted(self) -> str:
        return self.symbolic()

    def entries(self):
        return [self.entry] if self.entry else []


def _plain_number(x: float) -> str:
    """Exact coefficient text as written: 0.07, 4, 384, 1.0 (never rounded)."""
    if isinstance(x, int):
        return f"{x:,}"
    return repr(float(x))


_FUNC_EVAL: dict[str, Callable] = {
    "sqrt": lambda a: a**0.5,
    "min": min,
    "max": max,
    "abs": abs,
}


@dataclass(eq=False)
class BinOp(Expr):
    op: str
    a: Expr
    b: Expr

    @property
    def prec(self):
        return {"+": _ADD, "-": _ADD, "*": _MUL, "/": _ATOM, "^": _POW}[self.op]

    def eval(self):
        a, b = self.a.eval(), self.b.eval()
        return {
            "+": lambda: a + b,
            "-": lambda: a - b,
            "*": lambda: a * b,
            "/": lambda: a / b,
            "^": lambda: a**b,
        }[self.op]()

    def _render(self, part: str) -> str:
        a, b = getattr(self.a, part)(), getattr(self.b, part)()
        if self.op == "/":
            return f"frac({a}, {b})"  # a fraction bar needs no parentheses
        if self.op == "^":
            return f"{_paren(self.a, a, _ATOM)}^({b})"
        if self.op == "*":
            sep = " dot " if part == "substituted" and not _starts_paren(b) else " "
            return f"{_paren(self.a, a, _MUL)}{sep}{_paren(self.b, b, _MUL)}"
        return f"{a} {self.op} {_paren(self.b, b, _MUL if self.op == '-' else _ADD)}"

    def symbolic(self):
        return self._render("symbolic")

    def substituted(self):
        return self._render("substituted")

    def entries(self):
        return self.a.entries() + self.b.entries()


def _starts_paren(s: str) -> bool:
    return s.startswith("(")


@dataclass(eq=False)
class Func(Expr):
    name: str
    args: tuple[Expr, ...]

    def eval(self):
        return _FUNC_EVAL[self.name](*(a.eval() for a in self.args))

    def _render(self, part: str) -> str:
        parts = [getattr(a, part)() for a in self.args]
        if self.name == "sqrt":
            return f"sqrt({parts[0]})"
        if self.name == "abs":
            return f"abs({parts[0]})"
        return f'"{self.name}"({", ".join(parts)})'

    def symbolic(self):
        return self._render("symbolic")

    def substituted(self):
        return self._render("substituted")

    def entries(self):
        return [e for a in self.args for e in a.entries()]


def sqrt(x: Expr) -> Expr:
    return Func("sqrt", (_wrap(x),))


def absolute(x: Expr) -> Expr:
    return Func("abs", (_wrap(x),))


def minimum(*xs: Expr) -> Expr:
    return Func("min", tuple(_wrap(x) for x in xs))


# ---------------------------------------------------------------------------
# Lines and the sheet that collects them
# ---------------------------------------------------------------------------


@dataclass
class Line:
    """One printed calc line: the record the PDF prints (ADR 0002)."""

    symbol: str                 # Typst math
    value: object               # full-precision pint quantity or float
    note: str                   # margin note
    cite: str                   # printed citation(s)
    symbolic: str | None = None     # Typst math of the formula, if computed
    substituted: str | None = None  # Typst math with values substituted
    ratio: bool = False         # display to 2 decimals
    text: str | None = None     # for decision lines: the stated result
    kind: str = "value"         # "value", "decision", "heading"

    @property
    def result(self) -> str:
        return fmt_quantity(self.value, ratio=self.ratio)


@dataclass
class Sheet:
    """Collects calc lines in order and resolves registry citations.

    Every registry read goes through the Sheet's Registry, which records it
    for the DRAFT list.
    """

    registry: Registry
    lines: list[Line] = field(default_factory=list)

    # -- values that enter the calc -------------------------------------
    def input(self, typst: str, value, note: str, cite: str = "Input") -> Sym:
        self.lines.append(Line(typst, value, note, cite))
        return Sym(typst, value)

    def given(self, typst: str, value, note: str, cite: str) -> Sym:
        """A value taken from a non-registry source that is printed with its source
        (a database property, or an engineering decision recorded in the brief)."""
        return self.input(typst, value, note, cite)

    def code_value(self, typst: str, entry_id: str, note: str) -> Sym:
        """A registry value printed as its own line."""
        e = self.registry.get(entry_id)
        value = e.quantity
        self.lines.append(Line(typst, value, note, e.cite))
        return Sym(typst, value)

    def coeff(self, entry_id: str) -> Const:
        """A registry coefficient used inside a formula; cited on that line."""
        e = self.registry.get(entry_id)
        return Const(e.quantity, e)

    def factor(self, entry_id: str, key: str) -> Const:
        """One load factor out of a registry 'factors' entry."""
        e = self.registry.get(entry_id)
        return Const(float(e.value[key]), e)

    # -- computed lines ---------------------------------------------------
    def line(
        self,
        typst: str,
        expr: Expr,
        note: str,
        cite: str | None = None,
        cite_ids: tuple[str, ...] = (),
        unit: str | None = None,
        ratio: bool = False,
    ) -> Sym:
        """Evaluate ``expr``, record the line, and return it as a new symbol.

        The printed citation joins ``cite_ids`` (registry entries for the
        equation), any registry coefficients inside ``expr``, and ``cite``
        (a non-registry source, such as the brief).
        """
        value = expr.eval()
        if unit is not None:
            value = value.to(unit)
        elif hasattr(value, "units") and value.dimensionless:
            value = float(value.to("dimensionless").magnitude)
        cites = [self.registry.get(i).cite for i in cite_ids]
        cites += [e.cite for e in expr.entries()]
        if cite:
            cites.append(cite)
        self.lines.append(
            Line(
                symbol=typst, value=value, note=note, cite="; ".join(dict.fromkeys(cites)),
                symbolic=expr.symbolic(), substituted=expr.substituted(), ratio=ratio,
            )
        )
        return Sym(typst, value)

    def decision(self, statement: str, result: str, note: str, cite: str = "", cite_ids: tuple[str, ...] = ()) -> None:
        """A comparison with a stated outcome, e.g. λ ≤ λp → compact."""
        cites = [self.registry.get(i).cite for i in cite_ids] + ([cite] if cite else [])
        self.lines.append(
            Line(symbol=statement, value=None, note=note, cite="; ".join(cites), text=result, kind="decision")
        )

    def heading(self, text: str) -> None:
        self.lines.append(Line(symbol=text, value=None, note="", cite="", kind="heading"))
