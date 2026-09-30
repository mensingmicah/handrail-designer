"""Checks 1 and 2 against an independent plain-arithmetic calc.

These use Pipe2STD over 6'-0" (not test case 1). Every expected value is
recomputed here with plain floats in lb and in, so the calc-line machinery
is checked against a second, independent implementation.
"""

import dataclasses
import re

import pytest

from handrail import checks, dimensions, shapes
from handrail.calc import fmt_sig
from handrail.checks import SectionStop
from handrail.project import DeflectionLimit, Loads, Member, Project, ProjectInfo
from handrail.registry import Registry

E, FY, OMEGA = 29000.0, 35.0, 1.67  # ksi, ksi, - (registry values, restated for the plain calc)
P, W_L = 200.0, 50.0 / 12  # lb, lb/in


def project(section="Pipe2STD", span="6'-0\"", **kw):
    return Project(
        info=ProjectInfo(name="Test"),
        span=dimensions.parse(span),
        top_rail=Member(section=section, grade="A53 Gr B"),
        **kw,
    )


def plain(section="Pipe2STD", L=72.0):
    """Hand-style calc in plain floats: {(check, direction, load type): ratio}."""
    s = shapes.pipe(section)
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
    return checks.run(project(), Registry())


def test_every_case_matches_plain_calc(results):
    expected = plain()
    for chk in results.checks:
        for c in chk.checked:
            assert c.ratio == pytest.approx(expected[(chk.number, c.direction, c.load_type)], rel=1e-9), (
                chk.number, c.label)


def test_envelope_lists_every_direction_and_load_type(results):
    for chk in results.checks:
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
    for chk in results.checks:
        top = max(v for (n, *_), v in expected.items() if n == chk.number)
        assert chk.controlling.ratio == pytest.approx(top)


def test_tie_goes_to_first_listed_direction(results):
    # Outward and inward are identical for a round section; outward is listed first.
    chk2 = results.checks[1]
    horizontal = [c for c in chk2.checked if c.direction in ("Outward", "Inward")]
    best = max(horizontal, key=lambda c: c.ratio)
    assert best.direction == "Outward"


def test_noncompact_section_uses_eq_F8_2_and_is_flagged():
    res = checks.run(project(section="Pipe26STD", span="12'-0\""), Registry())
    chk1 = res.checks[0]
    assert chk1.flags and "NONCOMPACT" in chk1.flags[0]
    expected = plain("Pipe26STD", L=144.0)
    for c in chk1.checked:
        assert c.ratio == pytest.approx(expected[(1, c.direction, c.load_type)], rel=1e-9)


def _fake(D_t):
    s = shapes.pipe("Pipe2STD")
    return dataclasses.replace(s, D_t=D_t, label="FakePipe")


def test_slender_wall_is_a_hard_stop_naming_ratio_and_limit():
    reg = Registry()
    lr = reg.get("aisc360.B4.1b.round_hss.lambda_r")
    E, Fy = reg.get("material.steel.E").value, reg.get("material.A53_GrB.Fy").value
    expected = (rf"slender.*D/t = 300 > lambda_r = {re.escape(str(lr.value))}E/Fy = "
                rf"{re.escape(fmt_sig(lr.value * E / Fy))} \({re.escape(lr.cite)}\)")
    with pytest.raises(SectionStop, match=expected):
        checks.flexural_capacity(reg, _fake(300), "A53 Gr B")


def test_beyond_F8_limit_is_a_hard_stop():
    reg = Registry()
    app = reg.get("aisc360.F8.applicability")
    E, Fy = reg.get("material.steel.E").value, reg.get("material.A53_GrB.Fy").value
    expected = (rf"D/t = 400 is not less than the {re.escape(app.cite)} limit "
                rf"{re.escape(str(app.value))}E/Fy = {re.escape(fmt_sig(app.value * E / Fy))}")
    with pytest.raises(SectionStop, match=expected):
        checks.flexural_capacity(reg, _fake(400), "A53 Gr B")


def test_exemption_removes_distributed_cases():
    res = checks.run(project(loads=Loads(uniform_exempt=True, exemption_statement="Roof not occupied.")), Registry())
    for chk in res.checks:
        dist = [c for c in chk.cases if c.load_type == "Distributed"]
        assert dist and all(c.status == "exempt" for c in dist)
    assert res.loading.w_L is None


def test_deflection_bypass_computes_nothing():
    res = checks.run(project(rail_deflection=DeflectionLimit(bypass=True)), Registry())
    chk2 = res.checks[1]
    assert chk2.bypassed and chk2.cases == [] and chk2.verdict == "Bypassed by engineer"


def test_unsupported_grade_is_refused():
    from handrail.project import ProjectError

    p = dataclasses.replace(project(), top_rail=Member("Pipe2STD", "A500 Gr B"))
    with pytest.raises(ProjectError, match="A53 Gr B only"):
        checks.run(p, Registry())


def test_drafted_entries_used_are_tracked():
    reg = Registry()
    checks.run(project(), reg)
    used = {e.id for e in reg.drafted_used}
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
    res = checks.run(project(), reg)
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
