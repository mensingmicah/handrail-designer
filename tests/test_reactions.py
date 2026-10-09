"""Slice 4: the anchor reaction sets (reactions.py) against plain arithmetic.

Same-author machinery tests (docs/plans/slice-4.md, T3). Test case 5 (an
independent calc) is the independent check; Micah recomputes its sets at
the release review (ADR 0007).
"""

import pytest

from handrail import shapes
from handrail.checks import CONCENTRATED, DISTRIBUTED
from handrail.demand import ASD, Given, demand
from handrail.post import WORDING as CHECK_5_WORDING
from handrail.project import NO_INTERMEDIATE, SAME_AS_TOP, Loads
from handrail.reactions import BOTH, COMBINATIONS, WORDING
from handrail.registry import Registry
from handrail.units import Q_
from test_intermediate import run

P2, P125 = shapes.pipe("Pipe2STD"), shapes.pipe("Pipe1-1/4STD")
RHO = 490.0 / 1728  # lb/in^3 (registry value, restated for the plain calc)
H, TP, L = 42.0, 0.5, 72.0


def _lb(q):
    return q.m_as("lbf")


def _sets(res):
    return {s.name: s for s in res.reactions.sets}


def plain_D(inter=P125):
    """D at the base by hand: top rail, intermediate rail, post over h - t_p, baseplate 6 x 8 x 1/2."""
    D = P2.W.m_as("lbf/inch") * L + P2.W.m_as("lbf/inch") * (H - TP) + RHO * 6 * 8 * TP
    return D + (inter.W.m_as("lbf/inch") * L if inter is not None else 0.0)


def test_reaction_sets_match_plain_calc():
    res = run()
    D, wL = plain_D(), 50.0 / 12 * L  # w s = 300 lb > P = 200 lb: distributed governs
    sets = _sets(res)
    lat, up = sets["Lateral"], sets["Upward"]
    assert lat.load_type == up.load_type == DISTRIBUTED
    assert _lb(lat.V) == pytest.approx(1.6 * wL, rel=1e-9)
    assert _lb(lat.N) == pytest.approx(-0.9 * D, rel=1e-9)  # compression, negative
    assert lat.M.m_as("lbf*inch") == pytest.approx(1.6 * wL * H, rel=1e-9)  # arm h, the top of concrete
    assert _lb(up.N) == pytest.approx(1.6 * wL - 0.9 * D, rel=1e-9)  # tension, positive
    assert _lb(up.V) == 0 and up.M.m_as("lbf*inch") == 0
    total = dict(res.reactions.dead)["Total D"]
    assert _lb(total) == pytest.approx(D, rel=1e-9)
    assert [n for n, _ in res.reactions.dead] == ["Top rail", "Intermediate rail", "Post", "Baseplate", "Total D"]
    assert _lb(dict(res.reactions.dead)["Baseplate"]) == pytest.approx(RHO * 6 * 8 * TP, rel=1e-9)
    assert lat.combination.startswith("0.9D axial, 1.6L horizontal\nEngineering judgement")


def test_the_moment_arm_is_h_for_the_reactions_and_h_minus_tp_for_check_5():
    """T3 (Micah, 2026-10-09): the shared demand function, the same load,
    two arms: the lateral set's M with h and Check 5's with h - t_p."""
    res = run()
    project, loading, reg = res.project, res.loading, Registry()
    h = Given("h", project.post_height.value, "arm", "Input")
    hp = Given('L_"post"', loading.L_post, "arm", "Loading")
    dead = Given("P_D", loading.P_D, "dead", "Loading")
    m_reaction = demand(reg, project, loading, "Lateral", CONCENTRATED, COMBINATIONS, WORDING, dead, h).M
    m_check5 = demand(reg, project, loading, "Outward", CONCENTRATED, ASD, CHECK_5_WORDING, dead, hp).M
    assert m_reaction.value.m_as("lbf*inch") == pytest.approx(1.6 * 200 * H, rel=1e-12)
    assert m_check5.value.m_as("lbf*inch") == pytest.approx(1.0 * 200 * (H - TP), rel=1e-12)
    # And in the full run: the lateral set uses h, Check 5 uses h - t_p.
    assert _sets(res)["Lateral"].M.m_as("lbf*inch") == pytest.approx(1.6 * 300 * H, rel=1e-9)
    c5 = next(c for c in res.check(5).checked if c.direction == "Outward" and c.load_type == DISTRIBUTED)
    assert c5.Mr.m_as("lbf*inch") == pytest.approx(300 * (H - TP), rel=1e-9)


def test_the_reaction_dead_load_carries_the_intermediate_rail_only_when_there_is_one():
    # The dead load path (T3), the reactions' part.
    for state, inter in ((NO_INTERMEDIATE, None), (SAME_AS_TOP, P2)):
        res = run(state=state)
        assert _lb(dict(res.reactions.dead)["Total D"]) == pytest.approx(plain_D(inter), rel=1e-9)
        assert ("Intermediate rail" in dict(res.reactions.dead)) == (inter is not None)


def test_no_net_uplift_gives_no_upward_set_with_its_status():
    # P = 20 lb, w s = 12 lb: 1.6 x 20 = 32 lb < 0.9 D (about 50 lb).
    res = run(loads=Loads(concentrated=Q_(20, "lbf"), uniform=Q_(2, "lbf/ft")))
    up = _sets(res)["Upward"]
    assert not up.present and up.N is None
    assert up.remark == "No net uplift (0.9D >= 1.6L): no upward set"
    assert _sets(res)["Lateral"].present and _sets(res)["Lateral"].load_type == CONCENTRATED


def test_p_equal_to_w_s_gives_one_set_naming_both_types():
    # w s = 50 lb/ft x 4 ft = 200 lb = P. The span is 48 in >= 2 D_post.
    res = run(span="4'-0\"")
    for s in res.reactions.sets:
        assert s.load_type == BOTH
    decision = next(ln for ln in res.reactions.head if ln.kind == "decision")
    assert decision.text == "Both types, one set"
    assert _lb(_sets(res)["Lateral"].V) == pytest.approx(1.6 * 200, rel=1e-9)


def test_with_the_exemption_p_is_the_only_type():
    res = run(loads=Loads(uniform_exempt=True, exemption_statement="Exempt."))
    assert {s.load_type for s in res.reactions.sets} == {CONCENTRATED}
    assert _lb(_sets(res)["Lateral"].V) == pytest.approx(1.6 * 200, rel=1e-9)
    decision = next(ln for ln in res.reactions.head if ln.kind == "decision")
    assert decision.text == "Concentrated load P governs" and "only guard load type" in decision.note


def test_the_lateral_note_and_the_combination_come_from_the_registry():
    res, reg = run(), Registry()
    assert res.reactions.lateral_note == reg.get("ej.reaction.lateral_note").value
    lat = _sets(res)["Lateral"]
    assert any(ln.symbol == "M_u" and "top of concrete" in ln.cite for ln in lat.lines)
    assert any(ln.symbol == "h" for ln in lat.lines)
