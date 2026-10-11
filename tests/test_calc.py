import pint
import pytest

from handrail.calc import (Sheet, Sym, Term, chain, compare, fmt_g, fmt_quantity, fmt_ratio, fmt_sig, minimum,
                           number, order, sqrt, term)
from handrail.registry import Registry
from handrail.units import Q_


@pytest.mark.parametrize(
    "x, text",
    [
        (4200, "4,200"),
        (14735.2, "14,740"),
        (8823.353, "8,823"),
        (29000, "29,000"),
        (0.293, "0.2930"),
        (0.0012345, "0.001234"),
        (1.6666, "1.667"),
        (9.9996, "10.00"),
        (84, "84.00"),
        (-3.14159, "-3.142"),
    ],
)
def test_four_significant_figures(x, text):
    assert fmt_sig(x) == text


@pytest.mark.parametrize(
    "x, text",
    [
        (0.8765, "0.88"),
        (0.994, "0.99"),
        (0.996, "0.996"),   # would read 1.00: show three decimals
        (1.0, "1.000"),     # exactly 1.0 passes: three decimals
        (0.9996, "1.000"),  # passing: the four-decimal rule is for failing ratios only
        (1.0004, "1.0004"), # failing but reads 1.000 at three: show four
        (1.004, "1.004"),
        (1.006, "1.01"),
    ],
)
def test_ratio_two_decimals_or_three_near_one(x, text):
    assert fmt_ratio(x) == text


def test_display_units_are_fixed():
    assert fmt_quantity(Q_(350, "lbf * ft")) == '"4,200 lb-in"'
    assert fmt_quantity(Q_(35000, "psi")) == '"35.00 ksi"'
    assert fmt_quantity(Q_(0.293, "in^4")) == '"0.2930 in"^4'
    assert fmt_quantity(Q_(50, "lbf/ft")) == '"4.167 lb/in"'


def test_one_definition_gives_value_formula_and_substitution():
    sheet = Sheet(Registry())
    P = Sym("P", Q_(200, "lbf"))
    L = Sym("L", Q_(84, "inch"))
    M = sheet.line("M", "M", P * L / 4, note="midspan moment", cite="test")
    line = sheet.lines[-1]
    assert M.value.m_as("lbf*inch") == pytest.approx(4200)
    assert line.symbolic == 'frac(P L, "4")'
    assert line.substituted == 'frac(("200.0 lb") ("84.00 in"), "4")'
    assert line.result == '"4,200 lb-in"'


def test_srss_and_min_render_and_evaluate():
    sheet = Sheet(Registry())
    a = Sym("M_D", Q_(3, "lbf*inch"))
    b = Sym("M_L", Q_(4, "lbf*inch"))
    M = sheet.line("M", "M", sqrt(a**2 + b**2), note="", cite="")
    assert M.value.m_as("lbf*inch") == pytest.approx(5)
    assert sheet.lines[-1].symbolic == "sqrt(M_D^(\"2\") + M_L^(\"2\"))"
    m = sheet.line("M_n", "M_n", minimum(a, b), note="", cite="")
    assert m.value.m_as("lbf*inch") == pytest.approx(3)


def test_registry_coefficients_are_cited_and_tracked():
    reg = Registry()
    sheet = Sheet(reg)
    E = sheet.code_value("E", "E", "material.steel.E", note="")
    Fy = Sym("F_y", Q_(35, "ksi"))
    # any registry coefficient works for the mechanism; use E as a stand-in cite
    sheet.line("x", "x", E / Fy, note="", cite_ids=("material.steel.E",))
    assert sheet.lines[-1].cite == "AISC 360-22, Symbols"
    assert sheet.lines[-1].value == pytest.approx(29000 / 35)  # dimensionless -> float
    assert "material.steel.E" in [e.id for e in reg.used]


def test_mixing_incompatible_units_raises():
    sheet = Sheet(Registry())
    P = Sym("P", Q_(200, "lbf"))
    L = Sym("L", Q_(84, "inch"))
    with pytest.raises(pint.DimensionalityError):
        sheet.line("bad", "bad", P + L, note="", cite="")


def test_feet_and_inches_combine_correctly():
    # A units slip (feet read as inches) is impossible: pint converts.
    sheet = Sheet(Registry())
    w = Sym("w", Q_(50, "lbf/ft"))
    L = Sym("L", Q_(7, "ft"))
    M = sheet.line("M", "M", w * L**2 / 8, note="", cite="")
    assert M.value.m_as("lbf*inch") == pytest.approx(50 / 12 * 84**2 / 8)


def test_rendered_lines_compile_in_typst(tmp_path):
    import typst

    sheet = Sheet(Registry())
    P = Sym("P", Q_(200, "lbf"))
    L = Sym("L", Q_(84, "inch"))
    w = Sym("w", Q_(50, "lbf/ft"))
    E = Sym("E", Q_(29000, "ksi"))
    I = Sym("I", Q_(0.293, "in^4"))
    t = Sym('t_"des"', Q_(0.135, "inch"))
    sheet.line("M", "M", P * L / 4, note="", cite="")
    sheet.line("Delta", "Delta", 5 * w * L**4 / (384 * E * I), note="", cite="")
    sheet.line("M_x", "M_x", sqrt(P**2 + (w * L) ** 2) * t - P * t, note="", cite="")
    body = "\n".join(
        f"$ {ln.symbol} = {ln.symbolic} = {ln.substituted} = {ln.result} $" for ln in sheet.lines
    )
    src = tmp_path / "t.typ"
    src.write_text(body, encoding="utf-8")
    pdf = typst.compile(str(src))
    assert pdf[:4] == b"%PDF"


# ---------------------------------------------------------------------------
# Comparisons: one definition per decision line (issue #21, item 2)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("a, op, b, holds, printed", [
    (1.0, "<=", 2.0, True, "a = 1 <= b = 2"),
    (2.0, "<=", 2.0, True, "a = 2 <= b = 2"),   # the relation asked for prints, not "="
    (3.0, "<=", 2.0, False, "a = 3 > b = 2"),   # not held: the complement prints
    (3.0, "<", 2.0, False, "a = 3 >= b = 2"),
    (1.0, ">", 2.0, False, "a = 1 <= b = 2"),
    (1.0, ">=", 2.0, False, "a = 1 < b = 2"),
    (2.0, ">=", 2.0, True, "a = 2 >= b = 2"),
])
def test_a_comparison_prints_the_relation_that_is_true(a, op, b, holds, printed):
    c = compare(term("a", a, fmt_g), op, term("b", b, fmt_g))
    assert bool(c) is holds and c.holds is holds
    assert c.text == printed


def test_a_comparison_compares_quantities_in_any_units():
    c = compare(term("w", Q_(0.125, "inch")), ">=", term("L", Q_(1, "ft")))
    assert not c and c.text == 'w = "0.1250 in" < L = "12.00 in"'


def test_order_finds_which_of_three_relations_holds():
    a, b = term("a", 1.0, fmt_g), term("b", 2.0, fmt_g)
    assert order(a, b).op == "<" and order(b, a).op == ">" and order(a, a).op == "="
    assert order(a, b).text == "a = 1 < b = 2"
    near = term("c", 1.0 + 1e-12, fmt_g)
    assert order(a, near).op == "<" and order(a, near, rel_tol=1e-9).op == "="
    # The same true relation read from the other side.
    assert order(a, b).flipped().text == "b = 2 > a = 1"


def test_a_bare_number_prints_as_written():
    assert number(200).text == "200" and number(0.05).text == "0.05"
    assert number(135.57, fmt_sig).text == "135.6"
    assert compare(Term("x", 0.01), ">", number(0.05)).text == "x <= 0.05"


def test_chained_relations_share_their_middle_term():
    lo, mid, hi = term("p", 58.0, fmt_g), term("x", 70.0, fmt_g), term("r", 257.0, fmt_g)
    compact, slender = compare(mid, "<=", lo), compare(mid, ">", hi)
    assert not compact and not slender
    assert chain(compact.flipped(), slender) == "p = 58 < x = 70 <= r = 257"
    with pytest.raises(ValueError, match="do not share a middle term"):
        chain(compact, slender)


def test_a_decision_line_prints_the_comparison_it_was_given():
    sheet = Sheet(Registry())
    w, w_min = Sym("w", Q_(0.125, "inch")), Sym('w_"min"', Q_(0.1875, "inch"))
    meets = compare(w.stated(), ">=", w_min.stated())
    sheet.decision(meets, "NG", "Minimum size")
    assert not meets
    assert sheet.lines[-1].symbol == 'w = "0.1250 in" < w_"min" = "0.1875 in"'
    assert sheet.lines[-1].kind == "decision" and sheet.lines[-1].text == "NG"
