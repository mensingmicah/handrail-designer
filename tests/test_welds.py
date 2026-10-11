"""The weld ring (welds.py) against plain arithmetic, and its stops.

Same-author machinery tests, like test_checks.py and test_post.py: every
expected value is recomputed here with plain floats in lb, in and ksi.
Test case 4 (an independent calc) is the independent check of the welds.
"""

import dataclasses
import math

import pytest

from handrail import dimensions, shapes, welds
from handrail.calc import Sheet, Sym
from handrail.errors import SectionStop
from handrail.materials import Stress
from handrail.registry import Registry
from handrail.units import Q_

P15 = shapes.section("Pipe1-1/2STD")  # D = 1.900 in, t_des = 0.135 in


def _ring(size="1/8", sec=P15):
    reg = Registry()
    return reg, welds.ring(reg, sec, dimensions.parse(size))


def test_ring_properties_match_plain_calc():
    _, rg = _ring("1/4")
    D = 1.9
    assert rg.L_w.value.m_as("inch") == pytest.approx(math.pi * D, rel=1e-12)
    assert rg.S_w.value.m_as("inch**2") == pytest.approx(math.pi * D**2 / 4, rel=1e-12)
    assert rg.t_e.value.m_as("inch") == pytest.approx(0.707 * 0.25, rel=1e-12)


def _parts(t1, t2):
    return (welds.Part("t_1", 't_1', Q_(t1, "inch"), "Part 1", "Input"), welds.Part("t_2", 't_2', Q_(t2, "inch"), "Part 2", "Input"))


@pytest.mark.parametrize("t1, t2, w, ok", [
    (0.135, 0.5, "1/8", True),     # thinner part 0.135 in: minimum 1/8, met exactly
    (0.3, 0.5, "1/8", False),      # thinner part 0.3 in: minimum 3/16
    (0.3, 0.5, "3/16", True),
    (0.6, 0.8, "3/16", False),     # thinner part 0.6 in: minimum 1/4
    (0.8, 1.0, "1/4", False),      # thinner part over 3/4: minimum 5/16
])
def test_minimum_size_uses_the_thinner_part_joined(t1, t2, w, ok):
    reg, rg = _ring(w)
    limits = welds.size_limits(reg, rg.w, _parts(t1, t2))
    assert (limits.failure == "") is ok
    decisions = [ln for ln in limits.lines if ln.kind == "decision"]
    assert decisions[0].text == ("OK" if ok else "NG: below the minimum size")
    assert decisions[1].text == "Not applicable"  # no maximum size at a T-joint (W11)
    if not ok:
        assert "below the minimum size" in limits.failure and "Table J2.4" in limits.failure


def test_forces_with_moment_take_the_larger_fiber():
    """W10: compression from dead load adds to bending compression, so that
    side governs; both sides are printed."""
    reg, rg = _ring()
    sh = Sheet(reg)
    P, V, M = Sym("P", Q_(30, "lbf")), Sym("V", Q_(350, "lbf")), Sym("M", Q_(14525, "lbf*inch"))
    f = welds.ring_forces(sh, rg, P, "compression", V, M)
    L, S = math.pi * 1.9, math.pi * 1.9**2 / 4
    fa, fb, fv = 30 / L, 14525 / S, 350 / L
    assert f.f_n.value.m_as("lbf/inch") == pytest.approx(fa + fb, rel=1e-12)
    assert f.f_r.value.m_as("lbf/inch") == pytest.approx(math.hypot(fa + fb, fv), rel=1e-12)
    assert f.fiber == "compression side"
    tension = next(ln for ln in sh.lines if ln.symbol == 'f_(n,"t")')
    assert tension.value.m_as("lbf/inch") == pytest.approx(fb - fa, rel=1e-12)


def test_tension_with_moment_names_the_tension_side():
    reg, rg = _ring()
    sh = Sheet(reg)
    f = welds.ring_forces(sh, rg, Sym("P", Q_(30, "lbf")), "tension", None, Sym("M", Q_(1000, "lbf*inch")))
    assert f.fiber == "tension side" and f.f_v is None


def test_axial_only_is_uniform():
    reg, rg = _ring()
    sh = Sheet(reg)
    f = welds.ring_forces(sh, rg, Sym("P", Q_(250, "lbf")), "compression")
    assert f.fiber == "uniform" and f.f_b is None and f.f_v is None
    assert f.f_r.value.m_as("lbf/inch") == pytest.approx(250 / (math.pi * 1.9), rel=1e-12)


def test_theta_90_gives_k_ds_1_5():
    reg, _ = _ring()
    sh = Sheet(reg)
    theta, k = welds.directional_increase(sh, reg, Sym("f_r", Q_(100, "lbf/inch")))
    assert theta.value.m_as("degree") == 90
    assert k.value == 1.5
    printed = next(ln for ln in sh.lines if ln.symbol == "theta")
    assert printed.result == '"90.00°"'


def test_the_elected_increase_prints_the_line_saying_it_is_the_engineers_election():
    """W2 as revised 2026-10-10: after k_ds, a line says the increase is
    applied at the engineer's election, citing Eq. J2-5 and the STI basis."""
    reg, _ = _ring()
    sh = Sheet(reg)
    welds.directional_increase(sh, reg, Sym("f_r", Q_(100, "lbf/inch")))
    assert [ln.kind for ln in sh.lines] == ["value", "value", "value", "decision"]
    line = sh.lines[-1]
    assert line.symbol == '"Directional strength increase"' and line.text == "Applied at the engineer's election"
    assert line.note == reg.entries[welds.ELECTED].value
    assert "at the engineer's election" in line.note and "Steel Tube Institute" in line.note
    assert line.cite == f"AISC 360-22 Eq. J2-5; {reg.entries[welds.ELECTED].cite}" and "STI" in line.cite


def test_k_ds_is_1_0_and_no_theta_where_the_increase_is_not_elected():
    reg, _ = _ring()
    head, k_ds = welds.baseplate_k_ds(reg, elected=False)
    theta, k = k_ds(Sheet(reg), Sym("f_r", Q_(100, "lbf/inch")))
    assert theta is None and k.value == 1.0
    assert [(ln.key, ln.value, ln.cite) for ln in head] == [("k_ds", 1.0, "AISC 360-22 §J2.4(a)(3)")]
    assert "not elected by the engineer" in head[0].note
    used = {e.id for e in reg.used}
    assert welds.NOT_ELECTED in used and welds.ELECTED not in used and "aisc360.eq.J2-5" not in used


def test_the_elected_k_ds_prints_nothing_in_the_head():
    reg, _ = _ring()
    head, k_ds = welds.baseplate_k_ds(reg, elected=True)
    theta, k = k_ds(Sheet(reg), Sym("f_r", Q_(100, "lbf/inch")))
    assert head == [] and theta is not None and theta.value.m_as("degree") == 90 and k.value == 1.5
    assert welds.NOT_ELECTED not in {e.id for e in reg.used}


def test_strength_ratio_is_the_larger_of_weld_and_base_metal():
    reg, rg = _ring("1/4")
    wm = welds.weld_metal(reg, "E70XX")
    bm = welds.base_metal(reg, "Base metal", Stress("material.A36.Fu", "A36"),
                          welds.Part("t_p", "t_p", Q_(0.5, "inch"), "Baseplate", "Input"))
    sh = Sheet(reg)
    f_r = Sym("f_r", Q_(5000, "lbf/inch"))
    s = welds.strength(sh, rg, wm, Sym("k_ds", 1.5), f_r, bm, f_r, "Baseplate fusion face")
    weld_allow = 0.6 * 70e3 * 0.707 * 0.25 * 1.5 / 2.0
    base_allow = 0.6 * 58e3 * 0.5 / 2.0
    assert s.weld_allow.value.m_as("lbf/inch") == pytest.approx(weld_allow, rel=1e-12)
    assert s.weld_ratio.value == pytest.approx(5000 / weld_allow, rel=1e-12)
    assert s.base_ratio.value == pytest.approx(5000 / base_allow, rel=1e-12)
    assert s.ratio.value == pytest.approx(max(5000 / weld_allow, 5000 / base_allow), rel=1e-12)


def test_strength_without_base_metal_demand_is_the_weld_metal_ratio():
    reg, rg = _ring()
    wm = welds.weld_metal(reg, "E70XX")
    bm = welds.base_metal(reg, "Base metal", Stress("material.A53_GrB.Fu", "A53 Gr B"),
                          welds.Part("t_des", 't_"des"', Q_(0.135, "inch"), "Rail wall", "DB"))
    s = welds.strength(Sheet(reg), rg, wm, Sym("k_ds", 1.0), Sym("f_r", Q_(100, "lbf/inch")), bm, None, "")
    assert s.base_ratio is None and s.ratio.value == s.weld_ratio.value


# ---------------------------------------------------------------------------
# Check 3: top rail weld to post (dev section, not a test case)
# ---------------------------------------------------------------------------

from handrail import engine
from handrail.project import (
    NO_INTERMEDIATE, Baseplate, IntermediateRail, Loads, Member, Project, ProjectInfo, Welds,
)

P_CONC, W_PLF = 200.0, 50.0  # lb, lb/ft (registry code values, restated for the plain calc)


def project(rail="Pipe2STD", post="Pipe2STD", span="6'-0\"", r2p="1/8", p2b="1/4", tp="1/2", elected=False, **kw):
    """``elected``: the engineer's election of the directional increase at
    the post to baseplate weld, off by default as in a project file."""
    return Project(info=ProjectInfo(name="Test"), span=dimensions.parse(span),
                   top_rail=Member(rail, "A53 Gr B"), post=Member(post, "A53 Gr B"),
                   post_height=dimensions.parse("42"), baseplate_thickness=dimensions.parse(tp),
                   welds=Welds(dimensions.parse(r2p), dimensions.parse(p2b), directional_increase=elected),
                   **{"baseplate": Baseplate(dimensions.parse("30"), dimensions.parse("30")),
                      "intermediate_rail": IntermediateRail(NO_INTERMEDIATE), **kw})


def plain_check_3(rail="Pipe2STD", post="Pipe2STD", L_ft=6.0, w=0.125, P=P_CONC, w_plf=W_PLF):
    """Check 3 by hand in plain floats: {(direction, load type): (f_r, ratio) or None}."""
    r, p = shapes.section(rail), shapes.section(post)
    D, e = p.OD.m_as("inch"), r.OD.m_as("inch") / 2
    Lw, Sw = math.pi * D, math.pi * D**2 / 4
    weld = 0.60 * 70e3 * 0.707 * w * 1.0 / 2.00
    base = 0.60 * 60e3 * r.tdes.m_as("inch") / 2.00
    Dl = r.W.m_as("lbf/ft") * L_ft
    out = {}
    for lt, Lv in (("Concentrated", P), ("Distributed", w_plf * L_ft)):
        f = (Dl + Lv) / Lw
        out[("Downward", lt)] = (f, f / weld)
        fa, fb, fv = Dl / Lw, Lv * e / Sw, Lv / Lw
        fr = math.hypot(fa + fb, fv)
        for d in ("Outward", "Inward", "Longitudinal"):
            out[(d, lt)] = (fr, max(fr / weld, fv / base))
        net = Lv - 0.6 * Dl
        out[("Upward", lt)] = (net / Lw, net / Lw / weld) if net > 0 else None
    return out


def test_check_3_matches_plain_calc():
    chk = engine.run(project(), Registry()).check(3)
    expected = plain_check_3()
    assert len(chk.cases) == 10
    for c in chk.cases:
        exp = expected[(c.direction, c.load_type)]
        assert c.status == "checked", c.label
        assert c.f_r.m_as("lbf/inch") == pytest.approx(exp[0], rel=1e-9), c.label
        assert c.ratio == pytest.approx(exp[1], rel=1e-9), c.label
        assert c.k_ds == 1.0 and c.theta is None
    assert chk.controlling.direction == "Outward" and chk.verdict == "OK"


def test_check_3_fibers_and_base_metal_line_by_case():
    chk = engine.run(project(), Registry()).check(3)
    by = {(c.direction, c.load_type): c for c in chk.checked}
    assert by[("Downward", "Concentrated")].fiber == "uniform"
    assert by[("Downward", "Concentrated")].base_ratio is None  # no in-plane force on the rail face
    out = by[("Outward", "Distributed")]
    assert out.fiber == "compression side" and out.base_ratio is not None
    assert by[("Upward", "Concentrated")].sense == "tension"


def test_a_weld_below_minimum_size_is_ng_whatever_its_ratio():
    # 1/16 in against the 1/8 in minimum for a 0.154 in nominal pipe wall; the ratio itself is under 1.0.
    chk = engine.run(project(r2p="1/16"), Registry()).check(3)
    assert chk.controlling.ratio < 1.0
    assert chk.failures and "below the minimum size" in chk.failures[0]
    assert not chk.ok and chk.verdict == "NG" and chk.summary_flag == "below minimum size"
    assert not chk.min_size_ok and engine.run(project(), Registry()).check(3).min_size_ok


def test_upward_with_no_net_tension_is_listed_not_checked():
    loads = Loads(concentrated=Q_(10, "lbf"), uniform=Q_(1, "lbf/ft"))
    chk = engine.run(project(rail="Pipe12STD", post="Pipe12STD", loads=loads), Registry()).check(3)
    up = [c for c in chk.cases if c.direction == "Upward"]
    assert [c.status for c in up] == ["not checked", "not checked"]
    assert all(c.remark == "No net tension (0.6D >= 1.0L); compression covered by downward" for c in up)
    assert plain_check_3("Pipe12STD", "Pipe12STD", P=10, w_plf=1)[("Upward", "Concentrated")] is None


def test_check_3_exempt_distributed_cases():
    loads = Loads(uniform_exempt=True, exemption_statement="Not occupied.")
    chk = engine.run(project(loads=loads), Registry()).check(3)
    assert all(c.status == "exempt" for c in chk.cases if c.load_type == "Distributed")


# ---------------------------------------------------------------------------
# Check 7: post weld to baseplate (dev section, not a test case)
# ---------------------------------------------------------------------------


def plain_check_7(rail="Pipe2STD", post="Pipe2STD", L_ft=6.0, h=42.0, tp=0.5, w=0.25, P=P_CONC, w_plf=W_PLF,
                  k_ds=1.0):
    """Check 7 by hand in plain floats: {(direction, load type): (f_r, ratio)}.
    ``k_ds``: 1.0 as the default; 1.5 where the increase is elected, theta
    being 90 deg at the governing fiber."""
    r, p = shapes.section(rail), shapes.section(post)
    D, arm = p.OD.m_as("inch"), h - tp
    Lw, Sw = math.pi * D, math.pi * D**2 / 4
    weld = 0.60 * 70e3 * 0.707 * w * k_ds / 2.00
    base = 0.60 * 58e3 * tp / 2.00
    PD = r.W.m_as("lbf/ft") * L_ft + p.W.m_as("lbf/inch") * arm
    out = {}
    for lt, Lv in (("Concentrated", P), ("Distributed", w_plf * L_ft)):
        f = (PD + Lv) / Lw
        out[("Downward", lt)] = (f, max(f / weld, f / base))
        fa, fb, fv = PD / Lw, Lv * arm / Sw, Lv / Lw
        fr = math.hypot(fa + fb, fv)
        for d in ("Outward", "Inward", "Longitudinal"):
            out[(d, lt)] = (fr, max(fr / weld, fr / base))
        net = (Lv - 0.6 * PD) / Lw
        out[("Upward", lt)] = (net, max(net / weld, net / base))
    return out


def test_check_7_matches_plain_calc_with_no_increase_by_default():
    """W2 as revised 2026-10-10: the increase is not automatic. A project
    that does not elect it takes k_ds = 1.0 in every case, with no theta."""
    chk = engine.run(project(), Registry()).check(7)
    expected = plain_check_7(k_ds=1.0)
    assert len(chk.checked) == 10
    for c in chk.checked:
        f_r, ratio = expected[(c.direction, c.load_type)]
        assert c.f_r.m_as("lbf/inch") == pytest.approx(f_r, rel=1e-9), c.label
        assert c.ratio == pytest.approx(ratio, rel=1e-9), c.label
        assert c.theta is None and c.k_ds == 1.0, c.label
    assert chk.controlling.label == "Outward, distributed"


def test_check_7_matches_plain_calc_with_the_increase_elected():
    """Elected, Check 7 is what it was while the increase was automatic."""
    chk = engine.run(project(elected=True), Registry()).check(7)
    expected = plain_check_7(k_ds=1.5)
    assert len(chk.checked) == 10
    for c in chk.checked:
        f_r, ratio = expected[(c.direction, c.load_type)]
        assert c.f_r.m_as("lbf/inch") == pytest.approx(f_r, rel=1e-9), c.label
        assert c.ratio == pytest.approx(ratio, rel=1e-9), c.label
        assert c.theta.m_as("degree") == 90 and c.k_ds == 1.5, c.label
    assert chk.controlling.label == "Outward, distributed"


def test_the_election_changes_check_7_only():
    """The rail to post weld stays at k_ds = 1.0 whatever is elected, and no
    other check reads the election."""
    off, on = engine.run(project(), Registry()), engine.run(project(elected=True), Registry())
    for number in (1, 2, 3, 5, 6):
        assert [c.ratio for c in off.check(number).checked] == [c.ratio for c in on.check(number).checked], number
    assert all(c.k_ds == 1.0 and c.theta is None for c in on.check(3).checked)
    c_off, c_on = off.check(7).controlling, on.check(7).controlling
    assert c_off.weld_ratio == pytest.approx(1.5 * c_on.weld_ratio, rel=1e-12)
    assert c_off.base_ratio == c_on.base_ratio  # the baseplate's base metal line has no k_ds


def test_the_election_line_prints_only_where_the_increase_is_elected():
    def decisions(elected):
        c = engine.run(project(elected=elected), Registry()).check(7).controlling
        return [ln.text for ln in c.lines if ln.kind == "decision"]

    assert "Applied at the engineer's election" in decisions(True)
    assert "Applied at the engineer's election" not in decisions(False)


def test_check_7_theta_is_computed_at_the_governing_point():
    c = engine.run(project(elected=True), Registry()).check(7).controlling
    printed = {ln.symbol: ln for ln in c.lines if ln.kind == "value"}
    assert printed["theta"].symbolic == "arccos(frac(f_parallel, f_r))"
    assert 'sin(theta)^("1.5")' in printed['k_"ds"'].symbolic


@pytest.mark.parametrize("elected", [False, True])
def test_check_7_stops_on_a_post_that_is_not_round(elected):
    """The Check 7 joint's table inside the weld code, past validation:
    Check 7 on a post of a stand-in family stops before the weld is
    computed, whether or not the increase is elected."""
    reg = Registry()
    res = engine.compute(project(elected=elected), reg)
    rectangular = dataclasses.replace(res.post, family="rectangular HSS", label="FakeTube")
    with pytest.raises(SectionStop, match=r"FakeTube \(rectangular HSS\): the directional strength increase "
                                          r"rule for this section family has not been drafted"):
        welds.check_7(reg, res.project, rectangular, res.loading)


def test_both_weld_checks_run_in_check_number_order():
    res = engine.run(project(), Registry())
    assert [c.number for c in res.checks] == [1, 2, 3, "4a", "4b", 5, 6, 7]


def test_minimum_size_reads_the_nominal_wall_and_strength_the_design_wall():
    """Table J2.4 takes the physical wall, t_nom; the fusion-face strength line
    keeps t_des (W4). Pipe5STD straddles the 1/4 in row limit: t_nom = 0.258
    gives a 3/16 in minimum, where t_des = 0.241 would give 1/8 in."""
    p5 = shapes.section("Pipe5STD")
    assert p5.tnom.m_as("inch") > 0.25 >= p5.tdes.m_as("inch")  # the premise
    res = engine.run(project(rail="Pipe5STD", post="Pipe5STD", r2p="1/8", p2b="1/8"), Registry())
    for n in (3, 7):
        chk = res.check(n)
        head = {ln.symbol: ln for ln in chk.checked[0].lines if ln.kind == "value"}
        assert head['t_"min"'].value == p5.tnom, n
        assert head['w_"min"'].value.m_as("inch") == 0.1875, n
        assert chk.failures and chk.verdict == "NG", n
    rail_face = {ln.symbol: ln for ln in res.check(3).checked[0].lines if ln.kind == "value"}
    assert rail_face['t_"rail"'].value == p5.tdes


def test_thin_baseplate_base_metal_governs_and_sets_demand_and_capacity():
    """t_p = 1/4 in, with the directional increase elected: base metal
    0.60(58 ksi)(0.25 in)/2.00 = 4,350 lb/in is below the 1/4 in weld's
    0.60(70)(0.707)(0.25)(1.5)/2.00 = 5,568 lb/in, so base metal governs Check
    7. Demand and capacity come from that line, as the summary prints them.
    (Not elected, the weld's 3,712 lb/in is the lower and weld metal governs.)"""
    from handrail import report

    res = engine.run(project(tp="1/4", elected=True), Registry())
    c = res.check(7).controlling
    assert c.governs == "base metal"
    assert c.base_ratio > c.weld_ratio and c.ratio == c.base_ratio
    assert c.demand == c.base_demand == c.f_r
    assert c.capacity == c.base_allow
    assert c.capacity.m_as("lbf/inch") == pytest.approx(0.60 * 58e3 * 0.25 / 2.00, rel=1e-12)
    assert c.ratio == pytest.approx((c.demand / c.capacity).m_as(""), rel=1e-12)
    assert report._demand_capacity(c)[1].endswith("(base metal)")
    # Check 3 in the same run: weld metal governs, demand f_r over the weld capacity.
    c3 = res.check(3).controlling
    assert c3.governs == "weld metal" and c3.demand == c3.f_r and c3.capacity == c3.weld_allow


def test_every_weld_case_ratio_is_its_demand_over_its_capacity():
    for tp in ("1/2", "1/4"):
        for elected in (False, True):
            res = engine.run(project(tp=tp, elected=elected), Registry())
            for n in (3, 7):
                for c in res.check(n).checked:
                    assert c.ratio == pytest.approx((c.demand / c.capacity).m_as(""), rel=1e-12), (tp, n, c.label)


def test_check_3_prints_the_rail_dead_load_with_the_loading_page_symbol():
    res = engine.run(project(), Registry())
    c3 = res.check(3).checked[0]
    symbols = [ln.symbol for ln in c3.lines if ln.kind == "value"]
    assert 'D_"rail"' in symbols and "P_D" not in symbols
    assert any(ln.symbol == 'D_"rail"' for ln in res.loading.lines)  # the same symbol on the loading page
    c7 = res.check(7).checked[0]
    assert "P_D" in [ln.symbol for ln in c7.lines if ln.kind == "value"]


@pytest.mark.parametrize("t, w_min", [
    (0.25, 0.125),      # exactly at the 1/4 in limit: the "to 1/4 in" row
    (0.2501, 0.1875),
    (0.5, 0.1875),      # exactly at 1/2 in
    (0.5001, 0.25),
    (0.75, 0.25),       # exactly at 3/4 in
    (0.7501, 0.3125),
])
def test_table_j2_4_rows_include_their_upper_limit(t, w_min):
    reg, rg = _ring("1/8")
    limits = welds.size_limits(reg, rg.w, _parts(t, 1.0))
    printed = next(ln for ln in limits.lines if ln.symbol == 'w_"min"')
    assert printed.value.m_as("inch") == w_min


# ---------------------------------------------------------------------------
# Thin material at a weld: a warning, not a stop (Micah, 2026-10-10)
# ---------------------------------------------------------------------------

THIN = "THIN MATERIAL AT WELD: "


def _thin(chk):
    return [f for f in chk.flags if f.startswith(THIN)]


def test_a_part_under_an_eighth_inch_is_warned_of_and_one_at_exactly_an_eighth_is_not():
    reg = Registry()
    assert welds.thin_material(reg, _parts(0.125, 0.5)) == []
    [warning] = welds.thin_material(reg, _parts(0.1249, 0.5))
    assert warning.startswith(
        THIN + "Part 1, 0.1249 in, is thinner than 0.1250 in: the joined material is below the AWS D1.1 "
        "thickness range, and the welding procedure is the engineer's responsibility (for example AWS D1.3, "
        "sheet steel). ")
    assert warning.endswith("applies to carbon and low-alloy steel 1/8 in (3 mm) or thicker "
                            "(AWS D1.1/D1.1M:2020, Clause 1).")
    both = welds.thin_material(reg, _parts(0.1, 0.11))
    assert [w.split(",")[0] for w in both] == [THIN + "Part 1", THIN + "Part 2"]


def test_the_thin_limit_is_read_for_every_weld_and_the_warnings_words_only_when_a_part_is_under_it():
    reg = Registry()
    assert welds.thin_material(reg, _parts(0.2, 0.5)) == []
    used = {e.id for e in reg.used}
    assert welds.THIN_LIMIT in used and not {welds.THIN_WARNING, welds.THIN_SCOPE} & used
    welds.thin_material(reg, _parts(0.1, 0.5))
    assert {welds.THIN_LIMIT, welds.THIN_WARNING, welds.THIN_SCOPE} <= {e.id for e in reg.used}


def test_no_weld_of_pipe_2_std_on_a_half_inch_baseplate_is_warned_of():
    res = engine.run(project(), Registry())
    assert not any(_thin(res.check(n)) for n in (3, 7))


def test_a_thin_baseplate_is_warned_of_at_the_post_to_baseplate_weld_only():
    """Either part joined: the baseplate, as entered, counts as the walls do."""
    res = engine.run(project(tp="3/32"), Registry())
    [warning] = _thin(res.check(7))
    assert warning.startswith(THIN + "Baseplate thickness, 0.09375 in, is thinner than 0.1250 in")
    assert _thin(res.check(3)) == []


def test_the_warning_is_not_a_failure():
    """A warning, not a stop: the check is computed, and its verdict is the
    ratio's and the minimum size line's, as without the warning."""
    res = engine.run(project(tp="3/32"), Registry())
    chk = res.check(7)
    assert _thin(chk) and chk.cases and chk.summary_flag == ""
    assert not any("THIN" in f for f in chk.failures)
