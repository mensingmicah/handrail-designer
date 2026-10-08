"""PDF rendering: stamps, footer, and a real compile (dev section, not test case 1)."""

import dataclasses
from pathlib import Path

import pytest

from handrail import checks, dimensions, report
from handrail.calc import typst_str
from handrail.project import DeflectionLimit, Member, Project, ProjectInfo, Welds
from handrail.registry import Registry
from handrail.version import Stamp


def run(**kw):
    p = Project(info=ProjectInfo(name='Name with #hash, *stars*, "quotes" and $dollar'),
                span=dimensions.parse("6'-0\""), top_rail=Member("Pipe2STD", "A53 Gr B"),
                post=Member("Pipe2STD", "A53 Gr B"), post_height=dimensions.parse("42"),
                baseplate_thickness=dimensions.parse("1/2"), welds=Welds(dimensions.parse("1/8"), dimensions.parse("1/4")), **kw)
    reg = Registry()
    return checks.run(p, reg), reg


def mark_drafted(reg, *ids):
    """Treat entries as drafted, so these tests don't depend on the live review status."""
    for i in ids:
        reg.entries[i] = dataclasses.replace(reg.entries[i], status="drafted")


CLEAN = Stamp("0.1.0", "abc1234", False, "def5678", False)
DIRTY = Stamp("0.1.0", "abc1234", True, "def5678", True)


def test_draft_stamp_and_list_of_drafted_entries_used():
    res, reg = run()
    mark_drafted(reg, "aisc360.F1.omega_b", "asce7.guard.uniform.exemption.2")
    src = report.build_source(res, reg, CLEAN)
    assert "#let draft = true" in src
    assert '"aisc360.F1.omega_b"' in src
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
    check_2 = src.split("= Check 2: Top rail deflection")[1].split("\n= ")[0]
    assert "Bypassed by engineer" in check_2
    assert "Delta_L" not in check_2
    assert "Delta_L" in src  # Check 6 still computes: the bypass is per check


def test_bypassed_post_deflection_shows_no_calculation():
    res, reg = run(post_deflection=DeflectionLimit(ratio=60, bypass=True))
    src = report.build_source(res, reg, CLEAN)
    check_6 = src.split("= Check 6: Post deflection")[1].split("\n= ")[0]
    assert "Bypassed by engineer" in check_6
    assert "Delta_L" not in check_6


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
    assert src.count('#h(10pt) #"SENTINEL"') == len(res.checks)  # one closing line per check


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
    mark_drafted(reg, "aisc360.B3.2.asd")
    src = report.build_source(res, reg, CLEAN)
    e = reg.get("aisc360.B3.2.asd")
    assert f'"Design method: {e.value} per {e.cite}"' in src
    # Read before the DRAFT list is taken, so it is listed while it is drafted.
    assert f'"{e.id}"' in src


def _brief_stated_assumptions():
    """The bullets under "Stated assumptions" in docs/brief/output.md, each joined onto one line."""
    text = (Path(__file__).parents[1] / "docs" / "brief" / "output.md").read_text(encoding="utf-8")
    section = text.split("## Stated assumptions", 1)[1].split("\n## ", 1)[0]
    return [" ".join(b.split()) for b in section.split("\n- ")[1:]]


def test_locked_assumptions_are_the_briefs_stated_assumptions_in_order():
    assert list(report.LOCKED_ASSUMPTIONS) == _brief_stated_assumptions()


def test_front_matter_prints_every_locked_assumption():
    res, reg = run()
    src = report.build_source(res, reg, CLEAN)
    for a in report.LOCKED_ASSUMPTIONS:
        assert f"+ #{typst_str(a)}" in src


def test_check_1_states_that_ltb_does_not_apply():
    res, reg = run()
    lines = res.checks[0].controlling.lines
    ltb = [ln for ln in lines if ln.kind == "decision" and "Lateral-torsional" in (ln.text or "")]
    assert len(ltb) == 1
    assert ltb[0].cite == reg.get("aisc360.F8.no_ltb").cite


# ---------------------------------------------------------------------------
# Slice 2: the post pages
# ---------------------------------------------------------------------------


def test_dimensions_page_echoes_h_and_tp_and_prints_the_derived_lengths():
    res, reg = run()
    src = report.build_source(res, reg, CLEAN)
    assert '"Post height h, top of concrete to top rail centerline", "42", "3\'-6\\"", "42.00 in"' in src
    assert '"Baseplate thickness t_p", "1/2", "1/2\\"", "0.5000 in"' in src
    # Each derived length prints the formula of the line that computed it.
    assert ('"Post cantilever length, top of baseplate to top rail centerline", [$L_"post" = h - t_p$], '
            '"41.50 in", "Loading"') in src
    assert ('"Effective length, with the unbraced length taken as the post height h", [$L_c = K h$], '
            '"88.20 in", "Check 5"') in src


def test_printed_calc_never_cites_the_development_plan():
    # A sealed calc can't point a reviewer at an internal plan (PR #17 review, item 5).
    # A Pipe1STD post at h = 42 in has Lc/r above 200, so the slenderness flag prints too.
    base = run()[0].project
    for post in ("Pipe2STD", "Pipe1STD"):
        reg = Registry()
        res = checks.run(dataclasses.replace(base, post=Member(post, "A53 Gr B")), reg)
        src = report.build_source(res, reg, CLEAN)
        assert "plan D" not in src, post
    assert "A recommendation, not a requirement: flagged, and the calc continues." in src


def test_section_properties_page_has_a_post_block_with_r():
    res, reg = run()
    src = report.build_source(res, reg, CLEAN)
    props = src.split("= Section properties")[1].split("\n= ")[0]
    assert '"Post: Pipe2STD, A53 Gr B."' in props
    assert "Radius of gyration" in props


def test_check_5_envelope_prints_alpha_ratio_only_for_moment_cases():
    res, reg = run()
    chk5 = res.checks[2]
    table = report._envelope_5(chk5)
    for c in chk5.checked:
        if c is not chk5.controlling:  # the controlling row is bold, so its cells are wrapped
            assert f'"{c.direction}", "{c.load_type}"' in table
    # downward and upward rows carry a dash in the moment and alpha Pr/Pe columns
    assert table.count('"—"') == 2 * 4
    # A cell's second line is a "\n" escape inside its Typst string literal.
    assert '"Eq. H1-1b"' in table and '"Pr/Pc\\n(Eq. E3-1)"' in table and '"Pr/Pt\\n(Eq. D2-1)"' in table
    # every checked row prints each capacity under its demand (brief, output.md)
    for c in chk5.checked:
        P_cap = "Pt" if c.sense == "tension" else "Pc"
        assert f'\\n{P_cap} = {report.fmt_quantity_plain(c.P_allow)}"' in table
        if c.M_allow is not None:
            assert f'{report.fmt_quantity_plain(c.Mr)}\\nMc = {report.fmt_quantity_plain(c.M_allow)}"' in table


def test_summary_prints_the_check_5_axial_and_moment_terms():
    res, reg = run()
    src = report.build_source(res, reg, CLEAN)
    summary = src.split("= Summary")[1]
    c = res.checks[2].controlling
    assert c.Mr is not None
    assert f'"Pr = {report.fmt_quantity_plain(c.Pr)}; Mr = {report.fmt_quantity_plain(c.Mr)}"' in summary
    assert f'"Pc = {report.fmt_quantity_plain(c.P_allow)}; Mc = {report.fmt_quantity_plain(c.M_allow)}"' in summary
    for n in ("1. ", "2. ", "5. ", "6. "):
        assert f'"{n}' in summary


def test_slenderness_flag_prints_in_the_check_5_summary_row():
    p = Project(info=ProjectInfo(name="t"), span=dimensions.parse("6'-0\""),
                top_rail=Member("Pipe2STD", "A53 Gr B"), post=Member("Pipe1STD", "A53 Gr B"),
                post_height=dimensions.parse("42"), baseplate_thickness=dimensions.parse("1/2"),
                welds=Welds(dimensions.parse("1/8"), dimensions.parse("1/4")),)
    reg = Registry()
    res = checks.run(p, reg)
    src = report.build_source(res, reg, CLEAN)
    summary = src.split("= Summary")[1]
    assert "(Lc/r = 208.5 > 200, flagged)" in summary
    assert "SLENDERNESS: Pipe1STD" in src  # the flag box on the Check 5 page


def test_second_order_sentence_is_printed_in_the_controlling_moment_case():
    res, reg = run()
    src = report._lines(res.checks[2].controlling.lines)
    assert "Second-order effects negligible: αPr/Pe = " in src
    assert "amplification taken as 1.0." in src


def test_table_stroke_is_a_parameter_not_a_string_patch():
    # Issue #4, item 7.
    assert report._table([], [["a", "b"]], "(auto, 1fr)", stroke="none") == (
        '#table(columns: (auto, 1fr), stroke: none, "a", "b")')
    assert "stroke" not in report._table([], [["a", "b"]], "(auto, 1fr)")
    res, reg = run()
    assert 'stroke: none, "Project"' in report.build_source(res, reg, CLEAN)
