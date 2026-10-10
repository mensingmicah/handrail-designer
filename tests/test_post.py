"""Checks 5 and 6 against an independent plain-arithmetic calc.

Dev section, not a hand case: Pipe2STD rail over 6'-0" on a Pipe2STD post,
h = 42 in, t_p = 1/2 in. Every expected value is recomputed here with plain
floats in lb, in and ksi, so the calc-line machinery is checked against a
second implementation. These are same-author tests; the hand cases (2 and 3)
are the independent check.
"""

import dataclasses
import math
import re

import pytest

from handrail import dimensions, engine, post, shapes
from handrail.calc import fmt_sig
from handrail.errors import SectionStop
from handrail.project import (
    NO_INTERMEDIATE, Baseplate, DeflectionLimit, IntermediateRail, Loads, Member, Project, ProjectInfo, Welds,
)
from handrail.registry import Registry
from handrail.units import Q_

E, FY = 29000.0, 35.0                 # ksi (registry values, restated for the plain calc)
OM_B = OM_C = OM_T = 1.67
K, ALPHA = 2.1, 1.6
P, W_L = 200.0, 50.0 / 12             # lb, lb/in


def project(rail="Pipe2STD", span="6'-0\"", post_section="Pipe2STD", h="42", tp="1/2", **kw):
    return Project(
        info=ProjectInfo(name="Test"), span=dimensions.parse(span),
        top_rail=Member(rail, "A53 Gr B"), post=Member(post_section, "A53 Gr B"),
        post_height=dimensions.parse(h), baseplate_thickness=dimensions.parse(tp),
        welds=Welds(dimensions.parse("1/8"), dimensions.parse("1/4")),
        **{"baseplate": Baseplate(dimensions.parse("30"), dimensions.parse("30")),
           "intermediate_rail": IntermediateRail(NO_INTERMEDIATE), **kw},
    )


def plain(rail="Pipe2STD", L=72.0, post_section="Pipe2STD", h=42.0, tp=0.5, P=P, w=W_L):
    """Check 5 by hand in plain floats: {(direction, load type): (ratio, equation, alpha Pr/Pe)}."""
    r_, p = shapes.pipe(rail), shapes.pipe(post_section)
    A, I, Z, r = p.A.m_as("in^2"), p.I.m_as("in^4"), p.Z.m_as("in^3"), p.r.m_as("inch")
    Lp = h - tp
    PD = r_.W.m_as("lbf/inch") * L + p.W.m_as("lbf/inch") * Lp
    Lc = K * h
    lam = Lc / r
    Fe = math.pi**2 * E / lam**2
    Fcr = 0.658 ** (FY / Fe) * FY if lam <= 4.71 * math.sqrt(E / FY) else 0.877 * Fe
    Pc = Fcr * A * 1000 / OM_C
    Pt = FY * A * 1000 / OM_T
    assert p.D_t <= 0.07 * E / FY  # compact: Mn = Mp
    Mc = FY * Z * 1000 / OM_B
    Pe = math.pi**2 * E * 1000 * I / Lc**2
    live = {"Concentrated": P, "Distributed": w * L}
    out = {}
    for lt, V in live.items():
        out[("Downward", lt)] = ((PD + V) / Pc, "Pr/Pc (Eq. E3-1)", None)
        a = ALPHA * PD / Pe
        if PD / Pc >= 0.2:
            ratio, eq = PD / Pc + 8 / 9 * V * Lp / Mc, "Eq. H1-1a"
        else:
            ratio, eq = PD / (2 * Pc) + V * Lp / Mc, "Eq. H1-1b"
        for d in ("Outward", "Inward", "Longitudinal"):
            out[(d, lt)] = (ratio, eq, a)
        out[("Upward", lt)] = ((V - 0.6 * PD) / Pt, "Pr/Pt (Eq. D2-1)", None)
    return out


@pytest.fixture
def check5():
    return engine.run(project(), Registry()).check(5)


def test_every_case_matches_plain_calc(check5):
    assert check5.number == 5
    expected = plain()
    for c in check5.checked:
        ratio, eq, a = expected[(c.direction, c.load_type)]
        assert c.ratio == pytest.approx(ratio, rel=1e-9), c.label
        assert c.equation == eq, c.label
        if a is None:
            assert c.second_order is None
        else:
            assert c.second_order == pytest.approx(a, rel=1e-9), c.label


def test_envelope_lists_every_direction_and_load_type_and_checks_longitudinal(check5):
    assert [(c.direction, c.load_type, c.status) for c in check5.cases] == [
        (d, lt, "checked")
        for d in ("Downward", "Outward", "Inward", "Upward", "Longitudinal")
        for lt in ("Concentrated", "Distributed")
    ]


def test_capacities_match_plain_calc(check5):
    # Pipe2STD at h = 42 in: Lc/r = 88.2/0.791 = 111.5 < 4.71 sqrt(E/Fy) = 135.6, so Eq. E3-2.
    lines = check5.controlling.lines
    val = {ln.symbol: ln.value for ln in lines if ln.kind == "value"}
    lam = 88.2 / 0.791
    Fe = math.pi**2 * E / lam**2
    Fcr = 0.658 ** (FY / Fe) * FY
    assert val["L_c"].m_as("inch") == pytest.approx(88.2, rel=1e-12)
    assert val["frac(L_c, r)"] == pytest.approx(lam, rel=1e-12)
    assert val["F_e"].m_as("ksi") == pytest.approx(Fe, rel=1e-12)
    assert val['F_"cr"'].m_as("ksi") == pytest.approx(Fcr, rel=1e-12)
    assert val["P_c"].m_as("lbf") == pytest.approx(Fcr * 1.02 * 1000 / 1.67, rel=1e-12)
    assert val["M_c"].m_as("lbf*inch") == pytest.approx(35 * 0.713 * 1000 / 1.67, rel=1e-12)
    assert any(ln.text == "Inelastic buckling: Eq. E3-2" for ln in lines if ln.kind == "decision")


def test_elastic_branch_uses_eq_E3_3():
    # Pipe1-1/2STD at h = 42 in: Lc/r = 88.2/0.626 = 140.9 > 135.6.
    reg = Registry()
    chk = engine.run(project(post_section="Pipe1-1/2STD"), reg).check(5)
    down = next(c for c in chk.checked if c.direction == "Downward")
    val = {ln.symbol: ln.value for ln in down.lines if ln.kind == "value"}
    Fe = math.pi**2 * E / (88.2 / 0.626) ** 2
    assert val['F_"cr"'].m_as("ksi") == pytest.approx(0.877 * Fe, rel=1e-12)
    used = {e.id for e in reg.used}
    assert "aisc360.eq.E3-3" in used and "aisc360.eq.E3-2" not in used


def test_tension_capacity_matches_plain_calc(check5):
    up = next(c for c in check5.checked if c.direction == "Upward")
    assert up.capacity.m_as("lbf") == pytest.approx(35 * 1.02 * 1000 / 1.67, rel=1e-12)


# --- D8: axial-only cases use their own chapter ------------------------------


def test_downward_ratio_is_Pr_over_Pc_not_half_of_it(check5):
    for c in check5.checked:
        if c.direction == "Downward":
            pr_pc = (c.Pr / c.capacity).m_as("dimensionless")
            assert c.ratio == pytest.approx(pr_pc, rel=1e-12)  # Eq. H1-1b with Mr = 0 would give pr_pc / 2
            assert c.equation == "Pr/Pc (Eq. E3-1)"


@pytest.mark.parametrize("direction, note", [("Downward", "Axial only; Chapter E ratio reported"),
                                             ("Upward", "Axial only; Chapter D ratio reported")])
def test_axial_only_cases_carry_the_D8_margin_note(check5, direction, note):
    for c in check5.checked:
        if c.direction == direction:
            ratio_line = next(ln for ln in c.lines if ln.symbol == '"Ratio"')
            assert ratio_line.note == note
            assert c.Mr is None


def test_upward_with_no_net_tension_is_listed_not_checked():
    # Heavy rail, small guard loads: 0.6 P_D exceeds P_L, so the post stays in compression.
    loads = Loads(concentrated=Q_(10, "lbf"), uniform=Q_(1, "lbf/ft"))
    chk = engine.run(project(rail="Pipe12STD", loads=loads), Registry()).check(5)
    up = [c for c in chk.cases if c.direction == "Upward"]
    assert len(up) == 2
    for c in up:
        assert c.status == "not checked"
        assert c.remark == "No net tension (0.6D >= 1.0L); compression covered by downward"


# --- D1: second-order ratio and stop ------------------------------------------


def test_moment_cases_print_the_second_order_sentence(check5):
    reg = Registry()
    sentence = reg.get("ej.second_order.negligible").value
    for c in check5.checked:
        if c.direction in ("Outward", "Inward", "Longitudinal"):
            texts = [ln.text for ln in c.lines if ln.kind == "decision"]
            assert sentence.format(ratio=fmt_sig(c.second_order)) in texts


def test_second_order_ratio_above_the_limit_stops_naming_case_ratio_and_limit():
    # A 103 lb/ft rail over 12'-0" on a Pipe2STD post: 1.6 P_D / P_e is about 0.088.
    s2, s26 = shapes.pipe("Pipe2STD"), shapes.pipe("Pipe26STD")
    PD = s26.W.m_as("lbf/inch") * 144 + s2.W.m_as("lbf/inch") * 41.5
    a = 1.6 * PD / (math.pi**2 * E * 1000 * s2.I.m_as("in^4") / 88.2**2)
    assert a > 0.05  # the premise
    lim = Registry().get("ej.second_order.limit")
    expected = (rf"outward, concentrated case of Check 5: alpha Pr/Pe = {re.escape(fmt_sig(a))} > "
                rf"{lim.value} \({re.escape(lim.cite)}\)")
    with pytest.raises(SectionStop, match=expected):
        engine.run(project(rail="Pipe26STD", span="12'-0\""), Registry())


def test_downward_above_the_second_order_limit_does_not_stop():
    # Test case 2's geometry (plan D1, D7): Pipe1-1/2STD rail over 7'-0" on a
    # Pipe1-1/2STD post at h = 42 in. The downward distributed case would exceed
    # 0.05 if it were checked; it has no moment, so it is not.
    s = shapes.pipe("Pipe1-1/2STD")
    PD = s.W.m_as("lbf/inch") * (84 + 41.5)
    Pe = math.pi**2 * E * 1000 * s.I.m_as("in^4") / 88.2**2
    assert 1.6 * (PD + W_L * 84) / Pe > 0.05  # the premise
    chk = engine.run(project(rail="Pipe1-1/2STD", span="7'-0\"", post_section="Pipe1-1/2STD"),
                     Registry()).check(5)
    down = [c for c in chk.checked if c.direction == "Downward"]
    assert len(down) == 2 and all(c.second_order is None for c in down)


# --- H1-1a: machinery only (no realistic guard post reaches Pr/Pc >= 0.2) --------


def test_eq_H1_1a_arithmetic_with_an_artificial_dead_load():
    reg = Registry()
    proj = project(post_section="Pipe8STD")
    p8 = shapes.pipe("Pipe8STD")
    # A Pipe8STD post under a Pipe2STD rail fails W8 at validation; only the
    # loading is wanted here, so compute past it.
    base = engine.compute(proj, reg)
    loading = dataclasses.replace(base.loading, P_D=Q_(40000, "lbf"))
    cap = post._capacity(reg, proj, p8)
    c = post._moment_case(reg, proj, p8, loading, cap, "Outward", "Concentrated")
    A, Z, r = p8.A.m_as("in^2"), p8.Z.m_as("in^3"), p8.r.m_as("inch")
    lam = 88.2 / r
    Fe = math.pi**2 * E / lam**2
    Pc = 0.658 ** (FY / Fe) * FY * A * 1000 / 1.67
    assert 40000 / Pc >= 0.2  # the premise
    Mc = FY * Z * 1000 / 1.67
    assert c.equation == "Eq. H1-1a"
    assert c.ratio == pytest.approx(40000 / Pc + 8 / 9 * 200 * 41.5 / Mc, rel=1e-9)
    ratio_line = next(ln for ln in c.lines if ln.symbol == '"Ratio"')
    assert 'frac("8", "9")' in ratio_line.symbolic  # printed as the fraction, not 0.8889


# --- Classification and flags ---------------------------------------------------


def test_slender_in_compression_is_a_hard_stop_naming_ratio_and_limit():
    # D/t = 100: noncompact in flexure (lambda_p = 58, lambda_r = 257), slender in
    # compression (lambda_r = 0.11 E/Fy = 91.1).
    reg = Registry()
    lr = reg.get("aisc360.B4.1a.round_hss.lambda_r")
    fake = dataclasses.replace(shapes.pipe("Pipe2STD"), D_t=100, label="FakePipe")
    expected = (rf"FakePipe: wall is slender in compression, D/t = 100 > lambda_r = "
                rf"{re.escape(str(lr.value))}E/Fy = {re.escape(fmt_sig(lr.value * E / FY))} "
                rf"\({re.escape(lr.cite)}\)")
    with pytest.raises(SectionStop, match=expected):
        post.compression_capacity(reg, project(), fake)


def test_slenderness_over_200_is_flagged_and_the_calc_continues():
    # Pipe1STD at h = 42 in: Lc/r = 88.2/0.423 = 208.5.
    chk = engine.run(project(post_section="Pipe1STD"), Registry()).check(5)
    assert any(f.startswith("SLENDERNESS: Pipe1STD Lc/r = 208.5 exceeds 200") for f in chk.flags)
    assert chk.checked  # the calc continued
    down = next(c for c in chk.checked if c.direction == "Downward")
    flag = [ln for ln in down.lines if ln.kind == "decision" and ln.text.startswith("FLAG")]
    assert len(flag) == 1


def test_flexure_and_compression_limits_print_under_distinct_symbols(check5):
    # A moment case prints both blocks: lambda_r (Table B4.1b, flexure) and
    # lambda_(r,c) (Table B4.1a, compression) must not share a symbol.
    out = next(c for c in check5.checked if c.direction == "Outward")
    vals = {ln.symbol: ln.value for ln in out.lines if ln.kind == "value"}
    assert vals["lambda_r"] != vals["lambda_(r,c)"]
    assert any(ln.symbol.startswith("lambda = ") and "lambda_(r,c)" in ln.symbol
               for ln in out.lines if ln.kind == "decision")


@pytest.mark.parametrize("direction", ["Downward", "Outward"])
def test_lambda_prints_before_every_decision_that_uses_it(check5, direction):
    c = next(c for c in check5.checked if c.direction == direction)
    first_use = next(i for i, ln in enumerate(c.lines) if ln.kind == "decision" and ln.symbol.startswith("lambda "))
    assert any(ln.symbol == "lambda" and ln.kind == "value" for ln in c.lines[:first_use])


def test_effective_length_cites_the_unbraced_length_judgement(check5):
    reg = Registry()
    down = next(c for c in check5.checked if c.direction == "Downward")
    Lc = next(ln for ln in down.lines if ln.symbol == "L_c")
    assert Lc.symbolic == "K h"
    assert reg.get("ej.post.unbraced_length").cite in Lc.cite


def test_slenderness_within_200_raises_no_flag(check5):
    assert not any(f.startswith("SLENDERNESS") for f in check5.flags)


def test_exemption_removes_the_distributed_post_cases():
    loads = Loads(uniform_exempt=True, exemption_statement="Roof not occupied.")
    chk = engine.run(project(loads=loads), Registry()).check(5)
    dist = [c for c in chk.cases if c.load_type == "Distributed"]
    assert len(dist) == 5 and all(c.status == "exempt" for c in dist)


def test_tension_entries_are_not_listed_when_no_upward_case_is_checked():
    loads = Loads(concentrated=Q_(10, "lbf"), uniform=Q_(1, "lbf/ft"))
    reg = Registry()
    engine.run(project(rail="Pipe12STD", loads=loads), reg)
    used = {e.id for e in reg.used}
    assert "aisc360.eq.D2-1" not in used and "aisc360.D2.omega_t" not in used


# ---------------------------------------------------------------------------
# Check 6: cantilever deflection
# ---------------------------------------------------------------------------


@pytest.fixture
def check6():
    return engine.run(project(), Registry()).check(6)


def test_deflection_matches_plain_calc(check6):
    assert check6.number == 6
    EI = E * 1000 * 0.627
    allow = 41.5 / 60
    for c in check6.checked:
        V = {"Concentrated": P, "Distributed": W_L * 72}[c.load_type]
        delta = V * 41.5**3 / (3 * EI)
        assert c.demand.m_as("inch") == pytest.approx(delta, rel=1e-12), c.label
        assert c.capacity.m_as("inch") == pytest.approx(allow, rel=1e-12)
        assert c.ratio == pytest.approx(delta / allow, rel=1e-12)


def test_deflection_envelope_checks_the_horizontal_cases_only(check6):
    assert [(c.direction, c.load_type, c.status) for c in check6.cases] == [
        ("Downward", None, "not checked"),
        ("Outward", "Concentrated", "checked"), ("Outward", "Distributed", "checked"),
        ("Inward", "Concentrated", "checked"), ("Inward", "Distributed", "checked"),
        ("Upward", None, "not checked"),
        ("Longitudinal", "Concentrated", "checked"), ("Longitudinal", "Distributed", "checked"),
    ]
    for c in check6.cases:
        if c.status == "not checked":
            assert c.remark == "Vertical load: no lateral deflection of the post"


def test_deflection_limit_ratio_is_the_engineers_input():
    chk = engine.run(project(post_deflection=DeflectionLimit(ratio=90)), Registry()).check(6)
    for c in chk.checked:
        assert c.capacity.m_as("inch") == pytest.approx(41.5 / 90, rel=1e-12)


def test_post_deflection_bypass_computes_nothing():
    chk = engine.run(project(post_deflection=DeflectionLimit(ratio=60, bypass=True)), Registry()).check(6)
    assert chk.bypassed and chk.cases == [] and chk.verdict == "Bypassed by engineer"


def test_post_deflection_cites_the_post_limit_not_the_rail_limit(check6):
    reg = Registry()
    post_cite, rail_cite = reg.get("ej.deflection.limit.post").cite, reg.get("ej.deflection.limit").cite
    allow = next(ln for ln in check6.controlling.lines if ln.symbol == 'Delta_"allow"')
    assert post_cite in allow.cite and rail_cite not in allow.cite
