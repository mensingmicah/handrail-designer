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
from handrail.checks import SectionStop
from handrail.registry import Registry
from handrail.units import Q_

P15 = shapes.pipe("Pipe1-1/2STD")  # D = 1.900 in, t_des = 0.135 in


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
    return (welds.Part('t_1', Q_(t1, "inch"), "Part 1", "Input"), welds.Part('t_2', Q_(t2, "inch"), "Part 2", "Input"))


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
    reg, rg = _ring()
    sh = Sheet(reg)
    theta, k = welds.directional_increase(sh, reg, Sym("f_r", Q_(100, "lbf/inch")), P15)
    assert theta.value.m_as("degree") == 90
    assert k.value == 1.5
    printed = next(ln for ln in sh.lines if ln.symbol == "theta")
    assert printed.result == '"90.00°"'


def test_directional_increase_stops_on_a_section_that_is_not_round():
    # W2, with a stand-in family: only pipe can be entered today.
    reg, rg = _ring()
    rect = dataclasses.replace(P15, family="rectangular HSS", label="FakeTube")
    with pytest.raises(SectionStop, match=r"FakeTube \(rectangular HSS\): the directional strength increase "
                                          r"rule for this section family has not been drafted"):
        welds.directional_increase(Sheet(reg), reg, Sym("f_r", Q_(100, "lbf/inch")), rect)


def test_strength_ratio_is_the_larger_of_weld_and_base_metal():
    reg, rg = _ring("1/4")
    wm = welds.weld_metal(reg, "E70XX")
    bm = welds.base_metal(reg, "Base metal", "material.A36.Fu", "A36",
                          welds.Part("t_p", Q_(0.5, "inch"), "Baseplate", "Input"))
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
    bm = welds.base_metal(reg, "Base metal", "material.A53_GrB.Fu", "A53 Gr B",
                          welds.Part('t_"des"', Q_(0.135, "inch"), "Rail wall", "DB"))
    s = welds.strength(Sheet(reg), rg, wm, Sym("k_ds", 1.0), Sym("f_r", Q_(100, "lbf/inch")), bm, None, "")
    assert s.base_ratio is None and s.ratio.value == s.weld_ratio.value
