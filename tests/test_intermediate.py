"""Slice 4: the intermediate rail (Checks 4a and 4b) and its dead load path.

Same-author machinery tests (docs/plans/slice-4.md, T3), like test_post.py
and test_welds.py: every expected value is recomputed here with plain
floats in lb, in and ksi. Test case 5 (an independent calc) is the
independent check.
"""

import pytest

from handrail import checks, dimensions, shapes
from handrail.project import (
    NO_INTERMEDIATE, OWN_SECTION, SAME_AS_TOP, Baseplate, DeflectionLimit, IntermediateRail, Loads, Member, Project,
    ProjectInfo, Welds,
)
from handrail.registry import Registry
from handrail.units import Q_

_LBF = Q_(1, "lbf")
P2, P125 = shapes.pipe("Pipe2STD"), shapes.pipe("Pipe1-1/4STD")


def project(state=OWN_SECTION, section="Pipe1-1/4STD", rail="Pipe2STD", post="Pipe2STD", span="6'-0\"",
            int_weld="1/8", deflection=None, **kw):
    """Case 5's guard by default (plan T1): Pipe2STD rail and post over 6'-0",
    h = 42 in, t_p = 1/2 in, B x N = 6 x 8 in, a Pipe1-1/4STD intermediate rail."""
    member = Member(section, "A53 Gr B") if state == OWN_SECTION else None
    ir = IntermediateRail(state, member, deflection or DeflectionLimit())
    welds = Welds(dimensions.parse("1/8"), dimensions.parse("1/4"),
                  intermediate_rail_to_post=dimensions.parse(int_weld) if state == OWN_SECTION else None)
    return Project(info=ProjectInfo(name="Test"), span=dimensions.parse(span),
                   top_rail=Member(rail, "A53 Gr B"), post=Member(post, "A53 Gr B"),
                   post_height=dimensions.parse("42"), baseplate_thickness=dimensions.parse("1/2"),
                   welds=welds, baseplate=Baseplate(dimensions.parse("6"), dimensions.parse("8")),
                   intermediate_rail=ir, **kw)


def run(**kw):
    return checks.run(project(**kw), Registry())


def _lb(q):
    return q.m_as("lbf")


# ---------------------------------------------------------------------------
# The dead load path (plan, "Where the intermediate rail's dead load goes")
# ---------------------------------------------------------------------------


def test_an_intermediate_rail_adds_its_dead_load_to_d_at_the_post_only():
    L_ft, h, tp = 6.0, 42.0, 0.5
    none, own = run(state=NO_INTERMEDIATE), run()
    w_rail, w_int, w_post = P2.W.m_as("lbf/ft"), P125.W.m_as("lbf/ft"), P2.W.m_as("lbf/ft")
    D_none = w_rail * L_ft + w_post * (h - tp) / 12
    assert _lb(none.loading.P_D) == pytest.approx(D_none, rel=1e-9)
    assert _lb(own.loading.P_D) == pytest.approx(D_none + w_int * L_ft, rel=1e-9)
    assert _lb(own.loading.D_int) == pytest.approx(w_int * L_ft, rel=1e-9)
    assert none.loading.D_int is None and none.loading.w_D_int is None

    # Check 5 (the downward axial load) and Check 7 (its axial dead load) carry it ...
    for number, symbol in ((5, "P_D"), (7, "P_D")):
        for res, D in ((none, D_none), (own, D_none + w_int * L_ft)):
            c = res.check(number).checked[0]
            assert _lb(next(ln.value for ln in c.lines if ln.symbol == symbol)) == pytest.approx(D, rel=1e-9)
    # ... and Check 3's D is the top rail's alone, unchanged.
    for res in (none, own):
        c = res.check(3).checked[0]
        assert _lb(next(ln.value for ln in c.lines if ln.symbol == 'D_"rail"')) == pytest.approx(w_rail * L_ft)


def test_same_as_the_top_rail_adds_the_top_rails_weight():
    res = run(state=SAME_AS_TOP)
    assert res.loading.w_D_int == P2.W
    assert _lb(res.loading.D_int) == pytest.approx(P2.W.m_as("lbf/ft") * 6.0)
    note = next(ln.note for ln in res.loading.lines if ln.symbol == 'w_(D,"int")')
    assert "same section as the top rail" in note


def test_no_intermediate_rail_prints_no_intermediate_dead_load():
    res = run(state=NO_INTERMEDIATE)
    assert not [ln for ln in res.loading.lines if "int" in ln.symbol]


# ---------------------------------------------------------------------------
# Check 4a: the member
# ---------------------------------------------------------------------------

E, FY, OM_B = 29000.0, 35.0, 1.67  # ksi, ksi, - (registry values, restated for the plain calc)


def plain_4a(sec=P125, L=72.0, Pc=50.0, limit=120):
    """Check 4a by hand in plain floats: {(direction, limit state): ratio}."""
    Ma = FY * 1000 * sec.Z.m_as("in^3") / OM_B  # compact Pipe1-1/4STD (D/t well under 0.07E/Fy)
    wD = sec.W.m_as("lbf/inch")
    EI = E * 1000 * sec.I.m_as("in^4")
    ML, MD = Pc * L / 4, wD * L**2 / 8
    DL, DD = Pc * L**3 / (48 * EI), 5 * wD * L**4 / (384 * EI)
    return {("Downward", "Bending"): (MD + ML) / Ma, ("Horizontal", "Bending"): ML / Ma,
            ("Downward", "Deflection"): (DD + DL) / (L / limit), ("Horizontal", "Deflection"): DL / (L / limit)}


def _by_case(chk):
    return {(c.direction, c.limit_state): c for c in chk.checked}


def test_check_4a_matches_plain_calc_and_downward_bending_governs():
    chk = run().check("4a")
    by = _by_case(chk)
    for key, ratio in plain_4a().items():
        assert by[key].ratio == pytest.approx(ratio, rel=1e-9), key
    assert chk.controlling.label == "Downward, bending" and chk.verdict == "OK"
    assert chk.computed and not chk.observation


def test_check_4a_at_the_osha_component_load_runs_the_downward_branch():
    # T3 (Micah, 2026-10-09): 150 lb, own section, so the full check runs at the industrial value.
    res = run(loads=Loads(component=150 * _LBF))
    assert _lb(res.loading.P_c) == 150
    by = _by_case(res.check("4a"))
    for key, ratio in plain_4a(Pc=150.0).items():
        assert by[key].ratio == pytest.approx(ratio, rel=1e-9), key
    assert res.check("4a").controlling.direction == "Downward"
    lines = res.check("4a").controlling.lines
    assert any(ln.symbol == "P_c" and "engineer override" not in ln.note for ln in lines)
    assert any(ln.symbol == "P_c" and "engineer override" in ln.note for ln in res.loading.lines)


def test_check_4a_own_deflection_limit_and_bypass():
    chk = run(deflection=DeflectionLimit(ratio=240)).check("4a")
    assert _by_case(chk)[("Downward", "Deflection")].ratio == pytest.approx(
        plain_4a(limit=240)[("Downward", "Deflection")], rel=1e-9)
    chk = run(deflection=DeflectionLimit(bypass=True)).check("4a")
    assert {c.limit_state for c in chk.checked} == {"Bending"}
    bypassed = [c for c in chk.cases if c.status == "bypassed"]
    assert [c.direction for c in bypassed] == ["Downward", "Horizontal"]
    assert all(c.remark == "Deflection bypassed by engineer" for c in bypassed)


def test_same_as_top_rail_prints_the_observation_with_both_loads():
    chk = run(state=SAME_AS_TOP).check("4a")
    assert not chk.computed and chk.cases == [] and chk.controlling is None
    assert chk.observation == (
        "Controlled by Checks 1 and 2 by observation: same section, grade and span as the top rail; "
        "component load P_c = 50.00 lb ≤ concentrated guard load P = 200.0 lb. See Checks 1 and 2 for the result.")
    assert chk.verdict == chk.result == "Controlled by Checks 1 and 2" and chk.ok


def test_same_as_top_rail_with_check_2_bypassed_says_the_deflection_is_bypassed():
    chk = run(state=SAME_AS_TOP, rail_deflection=DeflectionLimit(bypass=True)).check("4a")
    assert chk.observation.endswith("See Checks 1 and 2 for the result. "
                                    "Deflection follows Check 2, which the engineer bypassed.")


def test_a_component_load_above_p_runs_the_full_check_on_the_top_rail_section():
    # The guard (S4-2): P_c = 250 lb > P = 200 lb, same as the top rail.
    res = run(state=SAME_AS_TOP, loads=Loads(component=250 * _LBF))
    chk = res.check("4a")
    assert chk.computed and not chk.observation
    by = _by_case(chk)
    for key, ratio in plain_4a(sec=P2, Pc=250.0).items():
        assert by[key].ratio == pytest.approx(ratio, rel=1e-9), key
    head = chk.controlling.lines[0]
    assert head.kind == "decision" and head.text == "Computed in full" and "P_c" in head.symbol
    # Same as the top rail, the deflection follows Check 2's limit and bypass.
    res = run(state=SAME_AS_TOP, loads=Loads(component=250 * _LBF), rail_deflection=DeflectionLimit(ratio=240))
    assert _by_case(res.check("4a"))[("Downward", "Deflection")].ratio == pytest.approx(
        plain_4a(sec=P2, Pc=250.0, limit=240)[("Downward", "Deflection")], rel=1e-9)
    res = run(state=SAME_AS_TOP, loads=Loads(component=250 * _LBF), rail_deflection=DeflectionLimit(bypass=True))
    assert {c.limit_state for c in res.check("4a").checked} == {"Bending"}


def test_a_component_load_equal_to_p_is_still_the_observation():
    assert not run(state=SAME_AS_TOP, loads=Loads(component=200 * _LBF)).check("4a").computed


def test_no_intermediate_rail_prints_none():
    res = run(state=NO_INTERMEDIATE)
    chk = res.check("4a")
    assert chk.observation == "None: no intermediate rail." and chk.verdict == "None" and not chk.computed
    assert res.loading.P_c is None
    assert not [ln for ln in res.loading.lines if ln.symbol == "P_c"]


def test_check_4a_cites_the_component_load_model_and_its_direction():
    chk = run().check("4a")
    down = _by_case(chk)[("Downward", "Bending")]
    M_L = next(ln for ln in down.lines if ln.symbol == "M_L")
    assert "AISC Manual Table 3-23, Case 7" in M_L.cite and "point load at midspan" in M_L.cite
    assert "downward component load" in next(ln for ln in down.lines if ln.symbol == "M_a").cite
    assert down.combination.startswith("1.0D + 1.0L, vertical")
    assert _by_case(chk)[("Horizontal", "Bending")].combination.startswith("1.0L horizontal, alone")


# ---------------------------------------------------------------------------
# Check 4b: the intermediate rail weld to the post
# ---------------------------------------------------------------------------

FEXX, FU, OM_W, OM_BM = 70.0, 60.0, 2.00, 2.00  # ksi, ksi, -, - (registry values, restated)


def plain_4b(inter=P125, post=P2, L=72.0, Pc=50.0, w=0.125):
    """Check 4b by hand in plain floats: {direction: (R, f_v, f_b, f_r, ratio)} (S4-9, S4-12)."""
    D, e = inter.OD.m_as("inch"), post.OD.m_as("inch") / 2
    RD = inter.W.m_as("lbf/inch") * L / 2
    Lw, Sw = 3.141592653589793 * D, 3.141592653589793 * D**2 / 4
    weld = 0.6 * FEXX * 1000 * 0.707 * w / OM_W               # k_ds = 1.0
    base = 0.6 * FU * 1000 * post.tdes.m_as("inch") / OM_BM   # post wall, in-plane shear only
    out = {}
    for direction, R in (("Downward", RD + Pc), ("Horizontal", (Pc**2 + RD**2) ** 0.5)):
        f_v, f_b = R / Lw, R * e / Sw
        f_r = (f_v**2 + f_b**2) ** 0.5
        out[direction] = (R, f_v, f_b, f_r, max(f_r / weld, f_v / base))
    return out


def _line(case, symbol):
    return next(ln.value for ln in case.lines if ln.symbol == symbol and ln.kind == "value")


def test_check_4b_matches_plain_calc_and_downward_governs():
    chk = run().check("4b")
    by = {c.direction: c for c in chk.checked}
    for direction, (R, f_v, f_b, f_r, ratio) in plain_4b().items():
        c = by[direction]
        assert _lb(_line(c, "R")) == pytest.approx(R, rel=1e-9)
        assert c.f_v.m_as("lbf/inch") == pytest.approx(f_v, rel=1e-9)
        assert c.f_b.m_as("lbf/inch") == pytest.approx(f_b, rel=1e-9)
        assert c.f_r.m_as("lbf/inch") == pytest.approx(f_r, rel=1e-9)
        assert c.ratio == pytest.approx(ratio, rel=1e-9)
        assert c.f_a is None and c.k_ds == 1.0 and c.theta is None and c.fiber == "extreme fiber"
    assert chk.controlling.direction == "Downward" and chk.verdict == "OK"
    # The 1/8 in weld sits at the Table J2.4 minimum for the thinner part, t_nom = 0.140 in.
    head = chk.controlling.lines
    assert _line(chk.controlling, 't_"min"').m_as("inch") == pytest.approx(0.140)
    assert chk.min_size_ok
    assert _line(chk.controlling, "e").m_as("inch") == pytest.approx(2.375 / 2)
    assert _line(chk.controlling, "L_w").m_as("inch") == pytest.approx(3.141592653589793 * 1.660)
    assert any(ln.symbol == 'D_"int"' for ln in head)


def test_check_4b_prints_the_reversed_base_metal_lines():
    c = run().check("4b").controlling
    decisions = {ln.symbol: ln for ln in c.lines if ln.kind == "decision"}
    assert decisions['"Post wall, normal force"'].text == "Not checked"
    branch = decisions['"Intermediate rail wall at the weld"']
    assert branch.text == "Covered by Check 4a" and "covered by Check 4a" in branch.note
    assert any(ln.kind == "heading" and ln.symbol == "Base metal: post wall fusion face" for ln in c.lines)
    assert _line(c, 't_"post"') == P2.tdes


def test_check_4b_below_minimum_size_is_ng():
    chk = run(int_weld="1/16").check("4b")
    assert not chk.min_size_ok and chk.verdict == "NG" and chk.controlling.ratio < 1.0


def test_same_as_top_rail_check_4b_prints_the_observation_and_how_r_was_found():
    chk = run(state=SAME_AS_TOP).check("4b")
    RD = P2.W.m_as("lbf/inch") * 72 / 2
    R = RD + 50
    assert not chk.computed and chk.result == "Controlled by Check 3"
    assert chk.observation == (
        "Intermediate rail weld: controlled by Check 3 by observation: same section (ring ≥ Check 3's, since post "
        f"OD ≤ rail OD per W8), same weld size, weld reaction R = {R:.2f} lb ≤ P = 200.0 lb.")
    assert _lb(next(ln.value for ln in chk.observation_lines if ln.symbol == "R")) == pytest.approx(R, rel=1e-9)


def test_a_weld_reaction_above_p_runs_the_full_check_4b_on_the_top_rail_ring():
    # The guard (S4-9): P_c = 250 lb, so R = R_D + 250 lb > P = 200 lb.
    chk = run(state=SAME_AS_TOP, loads=Loads(component=250 * _LBF)).check("4b")
    assert chk.computed
    plain = plain_4b(inter=P2, Pc=250.0)
    for c in chk.checked:
        assert c.ratio == pytest.approx(plain[c.direction][4], rel=1e-9)
    head = chk.controlling.lines
    assert head[0].kind == "decision" and head[0].text == "Computed in full"
    branch = next(ln for ln in head if ln.symbol == '"Intermediate rail wall at the weld"')
    assert branch.text == "Covered by Checks 1 and 2"
    # Same as the top rail, the weld is the rail to post size, 1/8 in.
    assert _line(chk.controlling, "w").m_as("inch") == 0.125


def test_no_intermediate_rail_check_4b_prints_none():
    chk = run(state=NO_INTERMEDIATE).check("4b")
    assert chk.observation == "None: no intermediate rail." and chk.verdict == "None"


def test_checks_3_and_7_rings_are_still_the_post_perimeter():
    res = run()
    for number in (3, 7):
        ring_d = next(ln for ln in res.check(number).controlling.lines if ln.symbol == "D")
        assert ring_d.note.endswith("the weld ring is the post perimeter")
