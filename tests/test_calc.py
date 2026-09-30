import pint
import pytest

from handrail.calc import Sheet, Sym, fmt_quantity, fmt_ratio, fmt_sig, minimum, sqrt
from handrail.registry import Registry
from handrail.units import Q_


@pytest.mark.parametrize(
    "x, text",
    [
        (4200, "4,200"),
        (14735.2, "14,700"),
        (29000, "29,000"),
        (0.293, "0.293"),
        (0.0012345, "0.00123"),
        (1.6666, "1.67"),
        (9.996, "10.0"),
        (84, "84.0"),
        (-3.14159, "-3.14"),
    ],
)
def test_three_significant_figures(x, text):
    assert fmt_sig(x) == text


def test_ratio_two_decimals():
    assert fmt_ratio(0.8765) == "0.88"


def test_display_units_are_fixed():
    assert fmt_quantity(Q_(350, "lbf * ft")) == '"4,200 lb-in"'
    assert fmt_quantity(Q_(35000, "psi")) == '"35.0 ksi"'
    assert fmt_quantity(Q_(0.293, "in^4")) == '"0.293 in"^4'
    assert fmt_quantity(Q_(50, "lbf/ft")) == '"4.17 lb/in"'


def test_one_definition_gives_value_formula_and_substitution():
    sheet = Sheet(Registry())
    P = Sym("P", Q_(200, "lbf"))
    L = Sym("L", Q_(84, "inch"))
    M = sheet.line("M", P * L / 4, note="midspan moment", cite="test")
    line = sheet.lines[-1]
    assert M.value.m_as("lbf*inch") == pytest.approx(4200)
    assert line.symbolic == 'frac(P L, "4")'
    assert line.substituted == 'frac(("200 lb") ("84.0 in"), "4")'
    assert line.result == '"4,200 lb-in"'


def test_srss_and_min_render_and_evaluate():
    sheet = Sheet(Registry())
    a = Sym("M_D", Q_(3, "lbf*inch"))
    b = Sym("M_L", Q_(4, "lbf*inch"))
    M = sheet.line("M", sqrt(a**2 + b**2), note="", cite="")
    assert M.value.m_as("lbf*inch") == pytest.approx(5)
    assert sheet.lines[-1].symbolic == "sqrt(M_D^(\"2\") + M_L^(\"2\"))"
    m = sheet.line("M_n", minimum(a, b), note="", cite="")
    assert m.value.m_as("lbf*inch") == pytest.approx(3)


def test_registry_coefficients_are_cited_and_tracked():
    reg = Registry()
    sheet = Sheet(reg)
    E = sheet.code_value("E", "material.steel.E", note="")
    Fy = Sym("F_y", Q_(35, "ksi"))
    # any registry coefficient works for the mechanism; use E as a stand-in cite
    sheet.line("x", E / Fy, note="", cite_ids=("material.steel.E",))
    assert sheet.lines[-1].cite == "AISC 360-22, Symbols"
    assert sheet.lines[-1].value == pytest.approx(29000 / 35)  # dimensionless -> float
    assert "material.steel.E" in [e.id for e in reg.drafted_used]


def test_mixing_incompatible_units_raises():
    sheet = Sheet(Registry())
    P = Sym("P", Q_(200, "lbf"))
    L = Sym("L", Q_(84, "inch"))
    with pytest.raises(pint.DimensionalityError):
        sheet.line("bad", P + L, note="", cite="")


def test_feet_and_inches_combine_correctly():
    # A units slip (feet read as inches) is impossible: pint converts.
    sheet = Sheet(Registry())
    w = Sym("w", Q_(50, "lbf/ft"))
    L = Sym("L", Q_(7, "ft"))
    M = sheet.line("M", w * L**2 / 8, note="", cite="")
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
    sheet.line("M", P * L / 4, note="", cite="")
    sheet.line("Delta", 5 * w * L**4 / (384 * E * I), note="", cite="")
    sheet.line("M_x", sqrt(P**2 + (w * L) ** 2) * t - P * t, note="", cite="")
    body = "\n".join(
        f"$ {ln.symbol} = {ln.symbolic} = {ln.substituted} = {ln.result} $" for ln in sheet.lines
    )
    src = tmp_path / "t.typ"
    src.write_text(body, encoding="utf-8")
    pdf = typst.compile(str(src))
    assert pdf[:4] == b"%PDF"
