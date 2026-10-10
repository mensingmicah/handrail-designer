"""PDF rendering: stamps, footer, and a real compile (dev section, not test case 1)."""

import dataclasses
import itertools
from pathlib import Path

import pytest
import typst

from handrail import dimensions, engine, report
from handrail.calc import typst_str
from handrail.project import (
    NO_INTERMEDIATE, SAME_AS_TOP, Baseplate, DeflectionLimit, IntermediateRail, Loads, Member, Project, ProjectInfo,
    Welds,
)
from handrail.registry import Registry
from handrail.units import Q_
from handrail.version import Stamp
from test_intermediate import project as slice4_project


def run(**kw):
    kw.setdefault("welds", Welds(dimensions.parse("1/8"), dimensions.parse("1/4")))
    kw.setdefault("baseplate", Baseplate(dimensions.parse("30"), dimensions.parse("30")))
    kw.setdefault("intermediate_rail", IntermediateRail(NO_INTERMEDIATE))
    p = Project(info=ProjectInfo(name='Name with #hash, *stars*, "quotes" and $dollar'),
                span=dimensions.parse("6'-0\""), top_rail=Member("Pipe2STD", "A53 Gr B"),
                post=Member("Pipe2STD", "A53 Gr B"), post_height=dimensions.parse("42"),
                baseplate_thickness=dimensions.parse("1/2"), **kw)
    reg = Registry()
    return engine.run(p, reg), reg


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


def _reading_late(monkeypatch, reg, entry_id):
    """Make build_source read a registry entry at the very end of the body:
    the reaction tables are the last thing it builds."""
    real = report._reactions

    def reactions_with_a_late_read(results):
        out = real(results)
        reg.get(entry_id)
        return out

    monkeypatch.setattr(report, "_reactions", reactions_with_a_late_read)


def test_a_registry_read_late_in_the_build_is_still_listed_as_drafted(monkeypatch):
    """Issue #11, option A: the DRAFT stamp and the list are filled last,
    after the whole body is built, so an entry read anywhere in the build
    is stamped and listed. Before, the list was taken near the top, and an
    entry read after that point printed without either."""
    res, reg = run()
    late = "asce7.guard.uniform.exemption.2"  # an entry this calc does not otherwise read
    assert late not in {e.id for e in reg.used}
    mark_drafted(reg, late)
    _reading_late(monkeypatch, reg, late)
    src = report.build_source(res, reg, CLEAN)
    assert "#let draft = true" in src
    listed = src.split("== Draft code values")[1].split("\n= ")[0]
    assert f'"{late}"' in listed


def test_a_late_read_alone_is_enough_to_stamp_the_calc_draft(monkeypatch):
    """The stamp, not only the list: with every other entry verified, the one
    drafted entry read at the end of the build still makes the calc DRAFT."""
    res, reg = run()
    for i, e in reg.entries.items():
        reg.entries[i] = dataclasses.replace(e, status="verified")
    late = "asce7.guard.uniform.exemption.2"
    assert "#let draft = false" in report.build_source(res, reg, CLEAN)  # nothing drafted yet
    mark_drafted(reg, late)
    _reading_late(monkeypatch, reg, late)
    src = report.build_source(res, reg, CLEAN)
    assert "#let draft = true" in src
    listed = src.split("== Draft code values")[1].split("\n= ")[0]
    assert listed.count('"Entry"') == 1 and f'"{late}"' in listed
    # The list sits where it always has: in the front matter, before the dimensions page.
    assert src.index("== Sketch") < src.index("== Draft code values") < src.index("= Dimensions")


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
    from handrail.results import Check

    res, reg = run()
    monkeypatch.setattr(Check, "verdict", property(lambda self: "SENTINEL"))
    src = report.build_source(res, reg, CLEAN)
    # One closing line per computed check; a check not computed (Check 4a with
    # no intermediate rail) prints its observation line instead.
    assert src.count('#h(10pt) #"SENTINEL"') == len([c for c in res.checks if c.computed])


def _printed_equations(lines):
    """The display equations the renderer prints for these calc lines, split at "="."""
    import re

    src = report._lines(lines)
    return [[part.replace(" ", "") for part in eq.split(" = ")]
            for eq in re.findall(r"\$display\((.*?)\)\$\]", src)]


def test_mn_over_omega_prints_its_symbol_once():
    res, _ = run()
    eqs = _printed_equations(res.checks[0].controlling.lines)
    mn_om = [eq for eq in eqs if eq[0] == "frac(M_n,Omega_b)"]
    assert len(mn_om) == 1
    _, *rest = mn_om[0]
    assert "frac(M_n,Omega_b)" not in rest  # printed once: symbol, then substitution, then result
    assert rest[0].startswith("frac((")    # the substituted values come straight after the symbol


def test_no_printed_line_repeats_a_part_side_by_side():
    res, _ = run()
    for chk in (c for c in res.checks if c.computed):
        for eq in _printed_equations(chk.controlling.lines):
            for a, b in itertools.pairwise(eq):
                assert a != b, f"repeated part in printed line: {' = '.join(eq)}"


def test_a_slash_symbol_is_refused():
    from handrail.calc import Sheet, Sym

    sh = Sheet(Registry())
    a, b = Sym("M_n", Q_(1, "lbf*inch")), Sym("Omega_b", 1.67)
    with pytest.raises(ValueError, match="frac"):
        sh.line("M_n_over_Omega_b", "M_n / Omega_b", a / b, note="", cite="")


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
        res = engine.run(dataclasses.replace(base, post=Member(post, "A53 Gr B")), reg)
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
    res, _ = run()
    chk5 = res.check(5)
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
    c = res.check(5).controlling
    assert c.Mr is not None
    assert f'"Pr = {report.fmt_quantity_plain(c.Pr)}; Mr = {report.fmt_quantity_plain(c.Mr)}"' in summary
    assert f'"Pc = {report.fmt_quantity_plain(c.P_allow)}; Mc = {report.fmt_quantity_plain(c.M_allow)}"' in summary
    for n in ("1. ", "2. ", "3. ", "5. ", "6. ", "7. "):
        assert f'"{n}' in summary


def test_slenderness_flag_prints_in_the_check_5_summary_row():
    p = Project(info=ProjectInfo(name="t"), span=dimensions.parse("6'-0\""),
                top_rail=Member("Pipe2STD", "A53 Gr B"), post=Member("Pipe1STD", "A53 Gr B"),
                post_height=dimensions.parse("42"), baseplate_thickness=dimensions.parse("1/2"),
                welds=Welds(dimensions.parse("1/8"), dimensions.parse("1/4")),
                baseplate=Baseplate(dimensions.parse("30"), dimensions.parse("30")),
                intermediate_rail=IntermediateRail(NO_INTERMEDIATE))
    reg = Registry()
    res = engine.run(p, reg)
    src = report.build_source(res, reg, CLEAN)
    summary = src.split("= Summary")[1]
    assert "(Lc/r = 208.5 > 200, flagged)" in summary
    assert "SLENDERNESS: Pipe1STD" in src  # the flag box on the Check 5 page


def test_second_order_sentence_is_printed_in_the_controlling_moment_case():
    res, _ = run()
    src = report._lines(res.check(5).controlling.lines)
    assert "Second-order effects negligible: αPr/Pe = " in src
    assert "amplification taken as 1.0." in src


def test_table_stroke_is_a_parameter_not_a_string_patch():
    # Issue #4, item 7.
    assert report._table([], [["a", "b"]], "(auto, 1fr)", stroke="none") == (
        '#table(columns: (auto, 1fr), stroke: none, "a", "b")')
    assert "stroke" not in report._table([], [["a", "b"]], "(auto, 1fr)")
    res, reg = run()
    assert 'stroke: none, "Project"' in report.build_source(res, reg, CLEAN)


# ---------------------------------------------------------------------------
# Slice 3: the weld pages
# ---------------------------------------------------------------------------


def test_dimensions_page_echoes_both_weld_sizes_and_lists_e():
    res, reg = run()
    src = report.build_source(res, reg, CLEAN)
    dims = src.split("= Dimensions")[1].split("\n= ")[0]
    assert '"Fillet weld, top rail to post", "1/8", "1/8\\"", "0.1250 in"' in dims
    assert '"Fillet weld, post to baseplate", "1/4", "1/4\\"", "0.2500 in"' in dims
    assert ('"Eccentricity: rail centerline to the weld plane at the rail underside", '
            '[$e = frac(d_"rail", "2")$], "1.188 in", "Check 3"') in dims


def test_weld_checks_print_in_check_number_order_with_their_envelopes():
    res, reg = run()
    src = report.build_source(res, reg, CLEAN)
    heads = [ln for ln in src.splitlines() if ln.startswith("= Check ")]
    assert [h.split(":")[0] for h in heads] == ["= Check 1", "= Check 2", "= Check 3", "= Check 4a",
                                                "= Check 4b", "= Check 5", "= Check 6", "= Check 7"]
    check_3 = src.split("= Check 3: Top rail weld to post")[1].split("\n= ")[0]
    check_7 = src.split("= Check 7: Post weld to baseplate")[1].split("\n= ")[0]
    # theta and k_ds are an envelope column only where k_ds comes from theta (Check 7).
    assert "[$theta$ \\ $k_\"ds\"$]" in check_7 and "[$theta$" not in check_3
    assert '"90.00°\\n1.500"' in check_7
    assert '"Weld 1,856 lb/in\\nBase —"' in check_3  # no in-plane force on the rail face, downward
    assert "Covered by Check 5" in check_3 and "Covered by Check 5" in check_7


def test_summary_rows_for_the_welds_name_the_governing_line():
    res, reg = run()
    summary = report.build_source(res, reg, CLEAN).split("= Summary")[1]
    assert '"3. Top rail weld to post"' in summary and '"7. Post weld to baseplate"' in summary
    c7 = res.check(7).controlling
    assert f'"{report.fmt_quantity_plain(c7.weld_allow)} (weld metal)"' in summary


def test_a_weld_below_minimum_size_closes_ng_with_the_reason_and_its_true_sign():
    res, reg = run(welds=Welds(dimensions.parse("1/16"), dimensions.parse("1/4")))
    src = report.build_source(res, reg, CLEAN)
    check_3 = src.split("= Check 3: Top rail weld to post")[1].split("\n= ")[0]
    ratio = report.fmt_ratio(res.check(3).controlling.ratio)
    assert f'"Ratio" = {ratio} <= 1.00$ #h(6pt) #"; below minimum size"#h(10pt) #"NG"' in check_3
    assert "BELOW MINIMUM SIZE: Fillet weld w = 0.06250 in is below the minimum size 0.1250 in" in check_3
    summary = src.split("= Summary")[1]
    assert '"NG (below minimum size)"' in summary


# ---------------------------------------------------------------------------
# Slice 4: the intermediate rail, B x N and the reaction tables (S4-7)
# ---------------------------------------------------------------------------


def _slice4_source(**kw):
    """Case 5's guard (test_intermediate.project): its own Pipe1-1/4STD intermediate rail, B x N = 6 x 8 in."""

    reg = Registry()
    res = engine.run(slice4_project(**kw), reg)
    return res, report.build_source(res, reg, CLEAN)


def _section(src, start, end="\n= "):
    return src.split(start)[1].split(end)[0]


def test_dimensions_page_echoes_b_and_n_and_the_intermediate_weld():
    _, src = _slice4_source()
    dims = _section(src, "= Dimensions")
    assert '"Baseplate B, parallel to the rail", "6", "6\\"", "6.000 in"' in dims
    assert '"Baseplate N, perpendicular to the rail", "8", "8\\"", "8.000 in"' in dims
    assert '"Fillet weld, intermediate rail to post", "1/8"' in dims
    assert '"Check 4b"' not in dims  # a simple shear connection: no eccentricity, no derived length
    _, src = _slice4_source(state=SAME_AS_TOP)
    assert "intermediate rail to post" not in _section(src, "= Dimensions")


def test_section_properties_page_names_the_intermediate_rail_in_each_state():
    _, src = _slice4_source()
    page = _section(src, "= Section properties")
    assert '#text("Intermediate rail: Pipe1-1/4STD, A53 Gr B.")' in page
    assert page.count('"Pipe1-1/4STD: outside diameter"') == 1
    _, src = _slice4_source(state=SAME_AS_TOP)
    assert '#text("Intermediate rail: same section and grade as the top rail.")' in src
    _, src = _slice4_source(state=NO_INTERMEDIATE)
    assert '#text("Intermediate rail: none.")' in src


def test_reaction_tables_follow_the_summary_with_signed_n_and_their_notes():
    res, src = _slice4_source()
    assert src.index("= Summary") < src.index("= Anchor reactions")
    page = _section(src, "= Anchor reactions", "\n= Never")
    assert '"Baseplate: B = 6.000 in (parallel to rail) × N = 8.000 in (perpendicular to rail)"' in page
    lateral = _section(page, "== Lateral set", "== Upward set")
    upward = page.split("== Upward set")[1]
    assert '"480.0 lb", "−49.54 lb (compression)", "20,160 lb-in"' in lateral
    assert '"0 lb", "+430.5 lb (tension)", "0 lb-in"' in upward
    for part in (lateral, upward):
        assert typst_str(report.REACTION_CONVENTION) in part
        assert '"Governing load type", "Distributed"' in part
        for name in ("top rail", "intermediate rail", "post", "baseplate"):
            assert f'"D, {name}"' in part
        assert 'strong("D, total"), strong("55.04 lb")' in part
        assert "0.9D" in part and "1.6L" in part and "Engineering judgement (EOR): anchor reactions" in part
    assert typst_str(report.SAME_PLANE) in lateral and report.SAME_PLANE not in upward
    assert typst_str(res.reactions.lateral_note) in lateral and res.reactions.lateral_note not in upward


def test_no_upward_set_prints_its_status():
    _, src = _slice4_source(loads=Loads(concentrated=Q_(20, "lbf"), uniform=Q_(2, "lbf/ft")))
    upward = src.split("== Upward set")[1]
    assert '#"No net uplift (0.9D >= 1.6L): no upward set."' in upward
    assert "(tension)" not in upward


def test_summary_rows_for_check_4_in_each_state():
    _, src = _slice4_source()
    summary = _section(src, "= Summary")
    assert '"4a. Intermediate rail", "1,023 lb-in", "6,392 lb-in", "0.16", "Downward, bending", "OK"' in summary
    assert '"4b. Intermediate rail weld to post"' in summary and '"Downward, component"' in summary
    _, src = _slice4_source(state=SAME_AS_TOP)
    summary = _section(src, "= Summary")
    assert '"4a. Intermediate rail", "", "", "", "", "Controlled by Checks 1 and 2"' in summary
    assert '"4b. Intermediate rail weld to post", "", "", "", "", "Controlled by Check 3"' in summary
    _, src = _slice4_source(state=NO_INTERMEDIATE)
    summary = _section(src, "= Summary")
    assert '"4a. Intermediate rail", "", "", "", "", "None"' in summary


def test_check_4a_prints_the_governing_bending_and_deflection_cases():
    _, src = _slice4_source()
    page = _section(src, "= Check 4a: Intermediate rail")
    assert "Controlling case: Downward, bending" in page
    assert "Governing deflection case: Downward, deflection" in page


def test_front_matter_names_the_intermediate_rail_and_the_reactions():
    _, src = _slice4_source()
    assert "intermediate rail and its weld to the post" in src and "anchor reactions]" in src


def test_slice_4_pdf_compiles(tmp_path):
    for kw in ({}, {"state": "same as top rail"}, {"state": "none"}):
        _, src = _slice4_source(**kw)
        typ = tmp_path / "s4.typ"
        typ.write_text(src, encoding="utf-8")
        typst.compile(str(typ), output=str(tmp_path / "s4.pdf"))
