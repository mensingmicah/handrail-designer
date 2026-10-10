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
import operator
import re
from dataclasses import dataclass, field
from typing import Callable

from handrail.registry import Entry, Registry
from handrail.units import ureg

# ---------------------------------------------------------------------------
# Number and unit display (docs/brief/output.md: 4 significant figures,
# ratios to 2 decimals or 3 when they would read 1.00, fixed units lb, lb-in,
# ksi, in, in^3, in^4)
# ---------------------------------------------------------------------------

# Angles print in degrees, written straight after the number (90°). pint
# treats an angle as dimensionless, so display() checks for it first.
DEGREE = "°"

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
    (ureg.lbf / ureg.inch**3, "lb/in", 3),  # steel unit weight (the baseplate weight, slice 4)
]


def fmt_sig(x: float, sig: int = 4) -> str:
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


def typst_str(s: str) -> str:
    """A Typst string literal. User text goes into Typst only this way, so it is
    printed as text and never read as markup or code."""
    out = []
    for ch in str(s):
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ord(ch) < 32:
            out.append(" ")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def mtext(s: str) -> str:
    """Upright text inside Typst math."""
    return typst_str(s)


def fmt_ratio(x: float) -> str:
    """Ratio display (docs/brief/output.md): two decimals; three when two
    would read 1.00; four when a failing ratio (over 1.0) would still read
    1.000 at three."""
    two = f"{x:.2f}"
    if two != "1.00":
        return two
    three = f"{x:.3f}"
    if three == "1.000" and x > 1.0:
        return f"{x:.4f}"
    return three


def display(q) -> tuple[float, str, int | None]:
    """Return (magnitude, unit text, unit exponent) in the fixed display units."""
    if not hasattr(q, "units"):
        return float(q), "", None
    if q.units == ureg.degree:
        return q.magnitude, DEGREE, None
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
    text = f'"{num}{_unit_gap(unit)}{unit}"'
    return f"{text}^{exp}" if exp else text


def _unit_gap(unit: str) -> str:
    return "" if unit in ("", DEGREE) else " "


def fmt_quantity_plain(q, ratio: bool = False) -> str:
    """Plain text (not math) for tables: '4,200 lb-in', '0.293 in^4'."""
    mag, unit, exp = display(q)
    num = fmt_ratio(mag) if ratio else fmt_sig(mag)
    sup = {2: "²", 3: "³", 4: "⁴"}.get(exp, "")
    return f"{num}{_unit_gap(unit)}{unit}{sup}"


def fmt_g(x: float) -> str:
    """A tabulated ratio as published, without trailing zeros: 15.4, 300."""
    return f"{x:g}"


# ---------------------------------------------------------------------------
# Comparisons: one definition per decision line (ADR 0002 applied to decisions)
# ---------------------------------------------------------------------------

_HOLDS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
# The relation that is true when the one asked for is not.
_COMPLEMENT = {"<": ">=", "<=": ">", ">": "<=", ">=": "<"}
# The same relation read from the other side: a < b is b > a.
_FLIPPED = {"<": ">", "<=": ">=", ">": "<", ">=": "<=", "=": "="}


@dataclass(frozen=True)
class Term:
    """One side of a comparison: the text it prints as (Typst math in a calc
    line, plain text in a message) and the value compared."""

    text: str
    value: object


def term(symbol: str, value, fmt: Callable[[object], str] | None = None) -> Term:
    """A side printed as 'symbol = value'. The value is given once, so the
    number printed is the number compared."""
    return Term(f"{symbol} = {(fmt or fmt_quantity)(value)}", value)


def number(value, fmt: Callable[[object], str] = str) -> Term:
    """A side printed as the bare number, as written unless ``fmt`` is given."""
    return Term(fmt(value), value)


@dataclass(frozen=True)
class Comparison:
    """A comparison that has been evaluated.

    ``holds`` says whether the relation asked for held, and is what an
    ``if`` tests. ``left``, ``op`` and ``right`` state the relation that is
    true: the one asked for when it held, its complement when it did not.
    The printed relation and the branch taken therefore come from one
    evaluation and cannot drift apart.
    """

    left: Term
    op: str
    right: Term
    holds: bool

    def __bool__(self) -> bool:
        return self.holds

    @property
    def text(self) -> str:
        return f"{self.left.text} {self.op} {self.right.text}"

    def flipped(self) -> Comparison:
        """The same true relation, read from the other side."""
        return Comparison(self.right, _FLIPPED[self.op], self.left, self.holds)


def compare(left: Term, op: str, right: Term) -> Comparison:
    """Evaluate ``left op right`` (op is <, <=, > or >=). The result is true
    or false as the relation held, and prints the relation that is true."""
    holds = bool(_HOLDS[op](left.value, right.value))
    return Comparison(left, op if holds else _COMPLEMENT[op], right, holds)


def order(left: Term, right: Term, rel_tol: float = 0.0) -> Comparison:
    """Which of <, = or > holds between two values; the caller branches on
    ``op``. Values within ``rel_tol`` (relative to the larger) are equal."""
    a, b = left.value, right.value
    if abs(a - b) <= rel_tol * max(a, b):
        op = "="
    else:
        op = "<" if a < b else ">"
    return Comparison(left, op, right, True)


def chain(first: Comparison, second: Comparison) -> str:
    """Two true relations sharing their middle term, printed as one:
    a < b and b <= c print as a < b <= c."""
    if first.right is not second.left:
        raise ValueError(f"cannot chain {first.text!r} and {second.text!r}: they do not share a middle term")
    return f"{first.text} {second.op} {second.right.text}"


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

    def stated(self, fmt: Callable[[object], str] | None = None) -> Term:
        """This line as one side of a comparison: 'symbol = value'."""
        return term(self.typst, self.value, fmt)


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


@dataclass(eq=False)
class MathConst(Expr):
    """A mathematical constant, such as pi: printed by name in both the symbolic
    and the substituted form, so it is never shown rounded. Not a code value."""

    typst: str
    value: float

    def eval(self):
        return self.value

    def symbolic(self) -> str:
        return self.typst

    def substituted(self) -> str:
        return self.typst


PI = MathConst("pi", math.pi)


def _plain_number(x: float) -> str:
    """Exact coefficient text as written: 0.07, 4, 384, 1.0 (never rounded)."""
    if isinstance(x, int):
        return f"{x:,}"
    return repr(float(x))


def _sin(angle) -> float:
    return math.sin(angle.to("radian").magnitude)


def _arccos(x):
    # x is a ratio: a plain float, or a dimensionless pint quantity.
    ratio = x.to("dimensionless").magnitude if hasattr(x, "units") else x
    return ureg.Quantity(math.degrees(math.acos(ratio)), "degree")


_FUNC_EVAL: dict[str, Callable] = {
    "sqrt": lambda a: a**0.5,
    "min": min,
    "max": max,
    "abs": abs,
    "sin": _sin,
    "arccos": _arccos,
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
            # A fraction symbol, such as Lc/r, needs parentheses to take an exponent.
            base = f"({a})" if a.startswith("frac(") else _paren(self.a, a, _ATOM)
            return f"{base}^({b})"
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
        if self.name in ("sin", "arccos"):  # Typst math operators
            return f"{self.name}({parts[0]})"
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


def maximum(*xs: Expr) -> Expr:
    return Func("max", tuple(_wrap(x) for x in xs))


def sin(angle: Expr) -> Expr:
    """Sine of an angle quantity (degrees or radians)."""
    return Func("sin", (_wrap(angle),))


def arccos(x: Expr) -> Expr:
    """Inverse cosine of a ratio, as an angle in degrees."""
    return Func("arccos", (_wrap(x),))


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
    key: str = ""               # stable identifier, never printed (see Sheet)

    @property
    def result(self) -> str:
        return fmt_quantity(self.value, ratio=self.ratio)


_KEY = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


def _key(key: str) -> str:
    """A line key is a plain name: letters, digits and underscores. Refusing
    anything else catches a key and a Typst symbol passed in the wrong order."""
    if not isinstance(key, str) or not _KEY.fullmatch(key):
        raise ValueError(f"calc-line key {key!r}: a key is a plain name (letters, digits, underscores), "
                         f"given before the Typst symbol")
    return key


@dataclass
class Sheet:
    """Collects calc lines in order and resolves registry citations.

    Every registry read goes through the Sheet's Registry, which records it
    for the DRAFT list.

    Every value line takes a key as its first argument: a plain name for
    the quantity ("M_n", "L_c_over_r"), separate from the Typst symbol it
    prints as. The key is never printed. Tests and tools find a line by its
    key, so rewording a printed symbol cannot break or silently redirect a
    lookup (issues #8 and #21). A key names one line within the block it is
    printed in (a case, the loading, a section's properties).
    """

    registry: Registry
    lines: list[Line] = field(default_factory=list)

    # -- values that enter the calc -------------------------------------
    def input(self, key: str, typst: str, value, note: str, cite: str = "Input") -> Sym:
        self.lines.append(Line(typst, value, note, cite, key=_key(key)))
        return Sym(typst, value)

    def given(self, key: str, typst: str, value, note: str, cite: str) -> Sym:
        """A value taken from a non-registry source that is printed with its source
        (a database property, or an engineering decision recorded in the brief)."""
        return self.input(key, typst, value, note, cite)

    def code_value(self, key: str, typst: str, entry_id: str, note: str) -> Sym:
        """A registry value printed as its own line."""
        e = self.registry.get(entry_id)
        value = e.quantity
        self.lines.append(Line(typst, value, note, e.cite, key=_key(key)))
        return Sym(typst, value)

    def coeff(self, entry_id: str) -> Const:
        """A registry coefficient used inside a formula; cited on that line."""
        e = self.registry.get(entry_id)
        return Const(e.quantity, e)

    def fraction(self, entry_id: str) -> Expr:
        """A registry coefficient held as {numerator, denominator}; prints as a fraction."""
        e = self.registry.get(entry_id)
        return Const(e.value["numerator"], e) / Const(e.value["denominator"], e)

    def factor(self, entry_id: str, key: str) -> Const:
        """One load factor out of a registry 'factors' entry."""
        e = self.registry.get(entry_id)
        return Const(float(e.value[key]), e)

    # -- computed lines ---------------------------------------------------
    def line(
        self,
        key: str,
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
        if "/" in typst:
            # Typst typesets "a / b" and "frac(a, b)" identically, but as text they
            # differ, so a slash symbol defeats the renderer's "don't repeat the
            # symbol as its own formula" check (printed "Mn/Ωb = Mn/Ωb = ...").
            raise ValueError(f"calc-line symbol {typst!r}: write fractions as frac(a, b), not a / b")
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
                symbolic=expr.symbolic(), substituted=expr.substituted(), ratio=ratio, key=_key(key),
            )
        )
        return Sym(typst, value)

    def decision(self, statement: str | Comparison, result: str, note: str, cite: str = "",
                 cite_ids: tuple[str, ...] = (), key: str = "") -> None:
        """A statement with a stated outcome, e.g. λ ≤ λp → compact. A
        relation between values is passed as the Comparison that was
        evaluated (compare, order), so the line prints the relation the code
        acted on; plain text is for statements that compare nothing. A
        decision takes a key only where something reads its outcome."""
        if isinstance(statement, Comparison):
            statement = statement.text
        cites = [self.registry.get(i).cite for i in cite_ids] + ([cite] if cite else [])
        self.lines.append(
            Line(symbol=statement, value=None, note=note, cite="; ".join(cites), text=result, kind="decision",
                 key=_key(key) if key else "")
        )

    def heading(self, text: str) -> None:
        self.lines.append(Line(symbol=text, value=None, note="", cite="", kind="heading"))
