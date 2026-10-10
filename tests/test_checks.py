"""Checks 1 and 2 against an independent plain-arithmetic calc.

These use Pipe2STD over 6'-0" (not test case 1). Every expected value is
recomputed here with plain floats in lb and in, so the calc-line machinery
is checked against a second, independent implementation.
"""

import dataclasses
import re

import pytest

from handrail import dimensions, engine, flexure, materials, shapes
from handrail.calc import fmt_sig
from handrail.errors import SectionStop
from handrail.project import (
    NO_INTERMEDIATE, Baseplate, DeflectionLimit, IntermediateRail, Loads, Member, Project, ProjectError, ProjectInfo,
    Welds,
)
from handrail.registry import Registry
from handrail.results import Case, Check
from handrail.units import Q_

E, FY, OMEGA = 29000.0, 35.0, 1.67  # ksi, ksi, - (registry values, restated for the plain calc)
P, W_L = 200.0, 50.0 / 12  # lb, lb/in


def project(section="Pipe2STD", span="6'-0\"", post="Pipe2STD", h="42", tp="1/2", **kw):
    return Project(
        info=ProjectInfo(name="Test"),
        span=dimensions.parse(span),
        top_rail=Member(section=section, grade="A53 Gr B"),
        post=Member(section=post, grade="A53 Gr B"),
        post_height=dimensions.parse(h),
        baseplate_thickness=dimensions.parse(tp),
        welds=Welds(dimensions.parse("1/8"), dimensions.parse("1/4")),
        **{"baseplate": Baseplate(dimensions.parse("30"), dimensions.parse("30")),
           "intermediate_rail": IntermediateRail(NO_INTERMEDIATE), **kw},
    )


def plain(section="Pipe2STD", L=72.0):
    """Hand-style calc in plain floats: {(check, direction, load type): ratio}."""
    s = shapes.section(section)
    I, Z, S, Dt = s.I.m_as("in^4"), s.Z.m_as("in^3"), s.S.m_as("in^3"), s.D_t
    wD = s.W.m_as("lbf/inch")
    Mn = FY * 1000 * Z
    if Dt > 0.07 * E / FY:
        Mn = min(Mn, (0.021 * E / Dt + FY) * 1000 * S)
    Ma = Mn / OMEGA
    MD = wD * L**2 / 8
    ML = {"Concentrated": P * L / 4, "Distributed": W_L * L**2 / 8}
    Ei = E * 1000 * I
    DL = {"Concentrated": P * L**3 / (48 * Ei), "Distributed": 5 * W_L * L**4 / (384 * Ei)}
    DD = 5 * wD * L**4 / (384 * Ei)
    out = {}
    for lt in ("Concentrated", "Distributed"):
        out[(1, "Downward", lt)] = (MD + ML[lt]) / Ma
        out[(1, "Outward", lt)] = (MD**2 + ML[lt] ** 2) ** 0.5 / Ma
        out[(1, "Inward", lt)] = out[(1, "Outward", lt)]
        out[(1, "Upward", lt)] = abs(0.6 * MD - ML[lt]) / Ma
        out[(2, "Downward", lt)] = (DD + DL[lt]) / (L / 120)
        for d in ("Outward", "Inward", "Upward"):
            out[(2, d, lt)] = DL[lt] / (L / 120)
    return out


@pytest.fixture
def results():
    return engine.run(project(), Registry())


def test_every_case_matches_plain_calc(results):
    expected = plain()
    for chk in results.checks[:2]:  # Checks 1 and 2 (the rail)
        for c in chk.checked:
            assert c.ratio == pytest.approx(expected[(chk.number, c.direction, c.load_type)], rel=1e-9), (
                chk.number, c.label)


def test_envelope_lists_every_direction_and_load_type(results):
    for chk in results.checks[:2]:  # Checks 1 and 2 (the rail)
        labels = [(c.direction, c.load_type, c.status) for c in chk.cases]
        assert labels == [
            ("Downward", "Concentrated", "checked"), ("Downward", "Distributed", "checked"),
            ("Outward", "Concentrated", "checked"), ("Outward", "Distributed", "checked"),
            ("Inward", "Concentrated", "checked"), ("Inward", "Distributed", "checked"),
            ("Upward", "Concentrated", "checked"), ("Upward", "Distributed", "checked"),
            ("Longitudinal", None, "not checked"),
        ]


def test_controlling_is_the_highest_ratio(results):
    expected = plain()
    for chk in results.checks[:2]:  # Checks 1 and 2 (the rail)
        top = max(v for (n, *_), v in expected.items() if n == chk.number)
        assert chk.controlling.ratio == pytest.approx(top)


def _check_with(*cases):
    chk = Check(1, "t", "M_a", "M_n")
    chk.cases = [Case(d, lt, "checked", ratio=r) for d, lt, r in cases]
    return chk


def test_tie_between_directions_goes_to_first_in_envelope_order():
    chk = _check_with(("Downward", "Concentrated", 0.5), ("Outward", "Concentrated", 0.7),
                      ("Inward", "Concentrated", 0.7))
    assert chk.controlling.direction == "Outward"
    # Order decides it, not the name: reversed, the first listed still wins.
    chk = _check_with(("Inward", "Concentrated", 0.7), ("Outward", "Concentrated", 0.7))
    assert chk.controlling.direction == "Inward"


def test_the_verdict_and_the_printed_sign_are_one_comparison():
    """Issue #21, item 2: Check.ok and the closing line's relation both come
    from within_unity, so they cannot disagree."""
    for ratio, ok, printed in ((0.46, True, '"Ratio" = 0.46 <= 1.00'), (1.0, True, '"Ratio" = 1.000 <= 1.00'),
                               (1.004, False, '"Ratio" = 1.004 > 1.00')):
        chk = _check_with(("Downward", "Concentrated", ratio))
        assert chk.ok is ok and chk.within_unity.holds is ok
        assert chk.within_unity.text == printed
        assert chk.verdict == ("OK" if ok else "NG")


def test_tie_between_load_types_goes_to_first_in_envelope_order():
    chk = _check_with(("Downward", "Concentrated", 0.7), ("Downward", "Distributed", 0.7))
    assert chk.controlling.load_type == "Concentrated"
    chk = _check_with(("Downward", "Distributed", 0.7), ("Downward", "Concentrated", 0.7))
    assert chk.controlling.load_type == "Distributed"


def test_outward_and_inward_tie_exactly_for_a_round_section(results):
    # This is why the tie rule matters: the two cases produce identical ratios.
    for chk in results.checks[:2]:  # Checks 1 and 2 (the rail)
        by = {(c.direction, c.load_type): c.ratio for c in chk.checked}
        for lt in ("Concentrated", "Distributed"):
            assert by[("Outward", lt)] == by[("Inward", lt)]


def test_noncompact_section_uses_eq_F8_2_and_is_flagged():
    # A 103 lb/ft rail needs a post that keeps alpha Pr/Pe under the second-order limit.
    # Its D/t of 74.5 is over the chord limit of 50 (S5-3), so validation refuses it and
    # the checks are reached through the compute step: no A53 Gr B rail can be noncompact
    # under that limit (lambda_p = 58).
    res = engine.compute(project(section="Pipe26STD", span="12'-0\"", post="Pipe12STD"), Registry())
    chk1 = res.checks[0]
    assert chk1.flags and "NONCOMPACT" in chk1.flags[0]
    expected = plain("Pipe26STD", L=144.0)
    for c in chk1.checked:
        assert c.ratio == pytest.approx(expected[(1, c.direction, c.load_type)], rel=1e-9)


def _fake(D_t):
    s = shapes.section("Pipe2STD")
    return dataclasses.replace(s, D_t=D_t, label="FakePipe")


def test_slender_wall_is_a_hard_stop_naming_ratio_and_limit():
    reg = Registry()
    lr = reg.get("aisc360.B4.1b.round_hss.lambda_r")
    E, Fy = reg.get("material.steel.E").value, reg.get("material.A53_GrB.Fy").value
    expected = (rf"slender.*D/t = 300 > lambda_r = {re.escape(str(lr.value))}E/Fy = "
                rf"{re.escape(fmt_sig(lr.value * E / Fy))} \({re.escape(lr.cite)}\)")
    with pytest.raises(SectionStop, match=expected):
        flexure.flexural_capacity(reg, _fake(300), "A53 Gr B")


def test_beyond_F8_limit_is_a_hard_stop():
    reg = Registry()
    app = reg.get("aisc360.F8.applicability")
    E, Fy = reg.get("material.steel.E").value, reg.get("material.A53_GrB.Fy").value
    expected = (rf"D/t = 400 is not less than the {re.escape(app.cite)} limit "
                rf"{re.escape(str(app.value))}E/Fy = {re.escape(fmt_sig(app.value * E / Fy))}")
    with pytest.raises(SectionStop, match=expected):
        flexure.flexural_capacity(reg, _fake(400), "A53 Gr B")


def test_exemption_removes_distributed_cases():
    res = engine.run(project(loads=Loads(uniform_exempt=True, exemption_statement="Roof not occupied.")), Registry())
    for chk in res.checks[:2]:  # Checks 1 and 2 (the rail)
        dist = [c for c in chk.cases if c.load_type == "Distributed"]
        assert dist and all(c.status == "exempt" for c in dist)
    assert res.loading.w_L is None


def test_deflection_bypass_computes_nothing():
    res = engine.run(project(rail_deflection=DeflectionLimit(bypass=True)), Registry())
    chk2 = res.checks[1]
    assert chk2.bypassed and chk2.cases == [] and chk2.verdict == "Bypassed by engineer"


def test_unsupported_grade_is_refused():
    p = dataclasses.replace(project(), top_rail=Member("Pipe2STD", "A992"))
    with pytest.raises(ProjectError, match="top rail grade 'A992': for AISC pipe this version supports A53 Gr B, "):
        engine.run(p, Registry())


def test_every_supported_grade_has_both_its_fy_and_its_fu_entry():
    """Issue #4: a grade with Fy and no Fu must never get as far as Check
    3's rail fusion face. A grade is one record holding both entries
    (materials.Grade), and each entry exists in the registry."""
    reg = Registry()
    for family, grades in materials.GRADES.items():
        for name, grade in grades.items():
            for entry_id in (grade.Fy, grade.Fu):
                entry = reg.get(entry_id)
                assert entry.unit == ("ksi by wall range" if grade.by_wall else "ksi"), f"{family}, {name}: {entry_id}"


def test_entries_used_are_tracked():
    reg = Registry()
    engine.run(project(), reg)
    used = {e.id for e in reg.used}
    for needed in ("asce7.guard.concentrated", "asce7.guard.uniform", "material.A53_GrB.Fy",
                   "aisc360.F1.omega_b", "aisc360.eq.F8-1", "aisc_manual.t3-23.case7.M",
                   "aisc_manual.t3-23.case1.delta", "asce7.combo.asd.D_plus_L"):
        assert needed in used
    # The exemption text is only for the form's info box; the calc doesn't use it.
    assert "asce7.guard.uniform.exemption.2" not in used


def test_all_case_lines_compile_in_typst(tmp_path, results):
    import typst

    out = []
    for chk in results.checks:
        for c in chk.checked:
            for ln in c.lines:
                if ln.kind == "value" and ln.symbolic:
                    out.append(f"$ {ln.symbol} = {ln.symbolic} = {ln.substituted} = {ln.result} $")
                elif ln.kind == "value":
                    out.append(f"$ {ln.symbol} = {ln.result} $")
    src = tmp_path / "t.typ"
    src.write_text("\n".join(out), encoding="utf-8")
    assert typst.compile(str(src))[:4] == b"%PDF"


def test_capacity_is_printed_once_at_the_head_of_every_bending_case(results):
    chk1 = results.checks[0]
    heads = [c.lines[1:4] for c in chk1.checked]
    # the same Line objects in every case: capacity was computed once, not per case
    assert all(x is y for h in heads for x, y in zip(h, heads[0]))
    assert sum(1 for ln in chk1.controlling.lines if ln.symbol == "M_n") == 1


def test_combination_labels_are_generated_from_the_factors_used():
    reg = Registry()
    res = engine.run(project(), reg)
    up = next(c for c in res.checks[0].checked if c.direction == "Upward")
    f = reg.get("ej.combo.bending.upward").value
    assert up.combination.startswith(f"{float(f['D'])!r}D + {float(f['L'])!r}L")
    # ...and the printed expression multiplies by exactly those factors
    Ma = next(ln for ln in up.lines if ln.symbol == "M_a")
    assert f'"{float(f["D"])!r}" M_D' in Ma.symbolic and f'"{float(f["L"])!r}" M_L' in Ma.symbolic
    down = next(c for c in res.checks[1].checked if c.direction == "Downward")
    assert reg.get("ej.combo.deflection.D_plus_L").cite in down.combination


def test_upward_margin_note_states_the_net_sense(results):
    up = [c for c in results.checks[0].checked if c.direction == "Upward"]
    for c in up:
        Ma = next(ln for ln in c.lines if ln.symbol == "M_a")
        assert "net upward" in Ma.note  # guard load exceeds 0.6 x dead load for this rail


def test_every_formula_line_prints_a_citation(results):
    """Rule 1: every computed line cites a registry entry (or its source for givens)."""
    for chk in results.checks:
        for c in chk.checked:
            for ln in c.lines:
                if ln.kind == "value" and ln.symbolic and ln.symbolic != ln.symbol:
                    assert ln.cite, f"no citation on {ln.symbol} = {ln.symbolic}"


@pytest.mark.parametrize("section, span, listed", [("Pipe2STD", "6'-0\"", False), ("Pipe26STD", "12'-0\"", True)])
def test_eq_F8_2_is_listed_as_used_only_for_a_noncompact_section(section, span, listed):
    reg = Registry()
    # A compact post; under the Pipe2STD rail it fails W8 at validation, which
    # is not under test here, so compute past it.
    res = engine.compute(project(section=section, span=span, post="Pipe12STD"), reg)
    assert bool(res.checks[0].flags) is listed  # noncompact flag raised only for Pipe26STD
    used = {e.id for e in reg.used}
    assert ("aisc360.eq.F8-2" in used) is listed
    assert ("aisc360.eq.F8-2.coeff" in used) is listed


def test_upward_margin_note_states_net_downward_when_dead_load_wins():
    # Heavy rail, small guard load: 0.6 M_D exceeds M_L, so the net moment acts down.
    loads = Loads(concentrated=Q_(10, "lbf"), uniform=Q_(1, "lbf/ft"))
    res = engine.run(project(section="Pipe12STD", loads=loads), Registry())
    for c in res.checks[0].checked:
        if c.direction == "Upward":
            Ma = next(ln for ln in c.lines if ln.symbol == "M_a")
            MD = next(ln for ln in c.lines if ln.symbol == "M_D").value
            ML = next(ln for ln in c.lines if ln.symbol == "M_L").value
            assert 0.6 * MD > ML  # the premise of the test
            assert "net downward" in Ma.note


# ---------------------------------------------------------------------------
# Slice 2: post section and dead load at the post (dev section, not a hand case)
# ---------------------------------------------------------------------------


def test_post_radius_of_gyration_is_the_database_rx():
    assert shapes.section("Pipe2STD").r.m_as("inch") == 0.791
    assert shapes.section("Pipe1-1/2STD").r.m_as("inch") == 0.626


def test_dead_load_at_the_post_matches_plain_calc(results):
    # Pipe2STD rail over 6'-0" on a Pipe2STD post, h = 42 in, t_p = 1/2 in:
    # D_post = 3.66 lb/ft x 41.5 in / 12 = 12.6575 lb; D_rail = 3.66 lb/ft x 6 ft = 21.96 lb.
    ld = results.loading
    assert ld.L_post.m_as("inch") == pytest.approx(41.5, rel=1e-12)
    assert ld.P_D.m_as("lbf") == pytest.approx(12.6575 + 21.96, rel=1e-12)
    lines = {ln.symbol: ln for ln in ld.lines if ln.kind == "value"}
    assert lines['D_"post"'].value.m_as("lbf") == pytest.approx(12.6575, rel=1e-12)
    assert lines['D_"rail"'].value.m_as("lbf") == pytest.approx(21.96, rel=1e-12)


def test_dead_load_lines_cite_the_post_dead_load_entry(results):
    cite = Registry().get("ej.post.axial_dead_load").cite
    for sym in ('D_"post"', 'D_"rail"', "P_D"):
        ln = next(ln for ln in results.loading.lines if ln.symbol == sym)
        assert cite in ln.cite


def test_post_block_adds_r_and_rail_block_is_unchanged(results):
    rail_syms = [ln.symbol for ln in results.section_lines]
    post_syms = [ln.symbol for ln in results.post_section_lines]
    assert "r" not in rail_syms
    assert post_syms == rail_syms[:-1] + ["r", rail_syms[-1]]


# ---------------------------------------------------------------------------
# Slice 3, T1: run() is validate() then compute()
# ---------------------------------------------------------------------------


def test_run_validates_before_computing(monkeypatch):
    calls = []
    monkeypatch.setattr(engine, "validate", lambda p, r: calls.append("validate"))
    monkeypatch.setattr(engine, "compute", lambda p, r: calls.append("compute"))
    engine.run(project(), Registry())
    assert calls == ["validate", "compute"]


def test_compute_alone_skips_only_the_validation():
    a, b = engine.run(project(), Registry()), engine.compute(project(), Registry())
    for x, y in zip(a.checks, b.checks):
        assert [c.ratio for c in x.checked] == [c.ratio for c in y.checked]
