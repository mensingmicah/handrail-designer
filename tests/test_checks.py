"""Checks 1 and 2 against an independent plain-arithmetic calc.

These use Pipe2STD over 6'-0" (not test case 1). Every expected value is
recomputed here with plain floats in lb and in, so the calc-line machinery
is checked against a second, independent implementation.
"""

import dataclasses

import pytest

from handrail import checks, dimensions, shapes
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
    from handrail.calc import Sheet

    with pytest.raises(SectionStop, match=r"slender.*D/t = 300.*lambda_r = 0.31E/Fy = 256"):
        checks.flexural_capacity(Sheet(Registry()), _fake(300), "A53 Gr B")


def test_beyond_F8_limit_is_a_hard_stop():
    from handrail.calc import Sheet

    with pytest.raises(SectionStop, match=r"D/t = 400.*§F8 limit 0.45E/Fy = 372"):
        checks.flexural_capacity(Sheet(Registry()), _fake(400), "A53 Gr B")


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
