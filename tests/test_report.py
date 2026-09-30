"""PDF rendering: stamps, footer, and a real compile (dev section, not test case 1)."""

import pytest

from handrail import checks, dimensions, report
from handrail.project import DeflectionLimit, Member, Project, ProjectInfo
from handrail.registry import Registry
from handrail.version import Stamp


def run(**kw):
    p = Project(info=ProjectInfo(name='Name with #hash, *stars*, "quotes" and $dollar'),
                span=dimensions.parse("6'-0\""), top_rail=Member("Pipe2STD", "A53 Gr B"), **kw)
    reg = Registry()
    return checks.run(p, reg), reg


CLEAN = Stamp("0.1.0", "abc1234", False, "def5678", False)
DIRTY = Stamp("0.1.0", "abc1234", True, "def5678", True)


def test_draft_stamp_and_list_of_drafted_entries_used():
    res, reg = run()
    src = report.build_source(res, reg, CLEAN)
    assert "#let draft = true" in src
    for e in reg.drafted_used:
        assert f'"{e.id}"' in src
    # entries the calc did not use are not listed
    assert '"asce7.guard.uniform.exemption.2"' not in src


def test_no_draft_stamp_when_every_entry_used_is_verified(monkeypatch):
    res, reg = run()
    monkeypatch.setattr(Registry, "drafted_used", property(lambda self: []))
    src = report.build_source(res, reg, CLEAN)
    assert "#let draft = false" in src


def test_footer_marks_uncommitted_changes():
    res, reg = run()
    assert "uncommitted changes" not in report.build_source(res, reg, CLEAN)
    src = report.build_source(res, reg, DIRTY)
    assert '"Tool 0.1.0 (abc1234) uncommitted changes"' in src
    assert '"Registry def5678 uncommitted changes"' in src


def test_bypassed_check_shows_no_calculation():
    res, reg = run(rail_deflection=DeflectionLimit(bypass=True))
    src = report.build_source(res, reg, CLEAN)
    assert "Bypassed by engineer" in src
    assert "Check 2: Top rail deflection" in src
    assert "Delta_L" not in src


def test_pdf_compiles_with_hostile_project_text(tmp_path):
    res, reg = run()
    out = report.render_pdf(res, reg, DIRTY, tmp_path / "calc.pdf")
    assert out.read_bytes()[:4] == b"%PDF"
    assert not (tmp_path / "calc.typ").exists()  # intermediate source cleaned up


def test_closing_verdict_is_the_checks_own_and_never_reads_1_00_beside_NG():
    res, reg = run()
    chk = res.checks[0]
    for c in chk.checked:  # force a controlling ratio just over 1.0
        c.ratio = 1.004 if c is chk.checked[0] else 0.5
    src = report.build_source(res, reg, CLEAN)
    assert '"Ratio" = 1.004 > 1.00$ #h(10pt) #"NG"' in src
    assert "1.00 > 1.00" not in src


def test_closing_line_prints_the_checks_verdict_not_a_recomputed_one(monkeypatch):
    # A sentinel verdict proves the page prints Check.verdict rather than
    # recomputing OK/NG from the ratio.
    from handrail.checks import Check

    res, reg = run()
    monkeypatch.setattr(Check, "verdict", property(lambda self: "SENTINEL"))
    src = report.build_source(res, reg, CLEAN)
    assert src.count('#h(10pt) #"SENTINEL"') == 2  # Checks 1 and 2


def _printed_equations(lines):
    """The display equations the renderer prints for these calc lines, split at "="."""
    import re

    src = report._lines(lines)
    return [[part.replace(" ", "") for part in eq.split(" = ")]
            for eq in re.findall(r"\$display\((.*?)\)\$\]", src)]


def test_mn_over_omega_prints_its_symbol_once():
    res, reg = run()
    eqs = _printed_equations(res.checks[0].controlling.lines)
    mn_om = [eq for eq in eqs if eq[0] == "frac(M_n,Omega_b)"]
    assert len(mn_om) == 1
    symbol, *rest = mn_om[0]
    assert "frac(M_n,Omega_b)" not in rest  # printed once: symbol, then substitution, then result
    assert rest[0].startswith("frac((")    # the substituted values come straight after the symbol


def test_no_printed_line_repeats_a_part_side_by_side():
    res, reg = run()
    for chk in res.checks:
        for eq in _printed_equations(chk.controlling.lines):
            for a, b in zip(eq, eq[1:]):
                assert a != b, f"repeated part in printed line: {' = '.join(eq)}"


def test_a_slash_symbol_is_refused():
    from handrail.calc import Sheet, Sym
    from handrail.units import Q_

    sh = Sheet(Registry())
    a, b = Sym("M_n", Q_(1, "lbf*inch")), Sym("Omega_b", 1.67)
    with pytest.raises(ValueError, match="frac"):
        sh.line("M_n / Omega_b", a / b, note="", cite="")


def test_front_matter_states_the_design_method_from_the_registry():
    res, reg = run()
    src = report.build_source(res, reg, CLEAN)
    e = reg.get("aisc360.B3.2.asd")
    assert f'"Design method: {e.value} per {e.cite}"' in src
    # Read before the DRAFT list is taken, so it is listed while it is drafted.
    assert f'"{e.id}"' in src


def test_check_1_states_that_ltb_does_not_apply():
    res, reg = run()
    lines = res.checks[0].controlling.lines
    ltb = [ln for ln in lines if ln.kind == "decision" and "Lateral-torsional" in (ln.text or "")]
    assert len(ltb) == 1
    assert ltb[0].cite == reg.get("aisc360.F8.no_ltb").cite
