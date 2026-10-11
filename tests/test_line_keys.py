"""Stable line keys (issues #8 and #21, item 4).

Every value line of the printed calc carries a key: a plain name for the
quantity, separate from the Typst symbol it prints as and never printed.
tests/test_hand_cases.py finds values by key, so rewording a printed symbol
cannot break or redirect a lookup. These tests hold the two properties that
lookup relies on, over every block the test cases and the example print.
"""

import pytest

from handrail.calc import Sheet, Sym
from handrail.registry import Registry
from handrail.units import Q_
from test_golden import CASES, EXAMPLE
from test_hand_cases import run_case


def _blocks(res):
    """(name, lines) for every block of calc lines a calc prints."""
    yield "loading", res.loading.lines
    yield "top rail section", res.section_lines
    yield "post section", res.post_section_lines
    yield "intermediate rail section", res.inter_section_lines
    for chk in res.checks:
        yield f"Check {chk.number} observation", chk.observation_lines
        for c in chk.cases:
            yield f"Check {chk.number}, {c.label}", c.lines
    yield "reactions head", res.reactions.head
    for s in res.reactions.sets:
        yield f"reactions, {s.name} set", s.lines


@pytest.fixture(scope="module", params=[*CASES, EXAMPLE], ids=lambda p: p.stem)
def blocks(request):
    _, res = run_case(request.param)
    return list(_blocks(res))


def test_every_value_line_has_a_key(blocks):
    for name, lines in blocks:
        missing = [ln.symbol for ln in lines if ln.kind == "value" and not ln.key]
        assert not missing, f"{name}: value lines with no key: {missing}"


def test_a_key_names_one_quantity_within_a_block(blocks):
    """Lines that share a key in one block (a value printed twice, such as
    t_p in Check 7's size limits and its base metal) must be equal, so
    reading a value by key is never ambiguous."""
    for name, lines in blocks:
        seen = {}
        for ln in lines:
            if ln.kind != "value":
                continue
            if ln.key in seen:
                assert ln.value == seen[ln.key], f"{name}: key {ln.key!r} names two different values"
            seen[ln.key] = ln.value


def test_a_key_is_never_printed():
    """The key is not in the Typst source: adding or renaming one cannot
    change a printed calc."""
    from handrail import report

    sh = Sheet(Registry())
    sh.given("zz_unlikely_key", "x", Q_(1, "inch"), "note", "Input")
    sh.line("zz_other_key", "y", Sym("x", Q_(1, "inch")) * 2, "note", cite="test")
    sh.decision("x", "OK", "note", key="zz_decision_key")
    assert "zz_" not in report._lines(sh.lines)


@pytest.mark.parametrize("key", ["", "M_n / Omega_b", 'L_"post"', "frac(a, b)", "9x", "a b", None])
def test_a_key_must_be_a_plain_name(key):
    """A key and a symbol swapped, or a key left out, stops at once."""
    sh = Sheet(Registry())
    with pytest.raises(ValueError, match="calc-line key"):
        sh.given(key, "x", Q_(1, "inch"), "note", "Input")
    with pytest.raises(ValueError, match="calc-line key"):
        sh.line(key, "x", Sym("a", Q_(1, "inch")) * 2, "note", cite="test")
