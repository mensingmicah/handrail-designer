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
