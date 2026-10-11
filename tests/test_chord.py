"""The rail wall at a round post: the Chapter K chord limit states of Check
3 (docs/brief/welds.md, S6-10 and S6-1; docs/brief/checks.md, S6-16 item 1;
docs/plans/slice-6.md, T5).

Machinery tests, same-author: they hold the code to the brief's rules. They
are not test cases, and no value here is a hand or independent value. Where
a number is compared it is worked here in plain arithmetic from the
sections' published dimensions and the registry's entries, not copied from
the tool.
"""

import dataclasses
import math

import pytest

from handrail import engine, project, report
from handrail.chord import IN_PLANE, OUT_OF_PLANE, PLASTIFICATION, PUNCH, ChordCase, ChordCheck
from handrail.registry import Registry
from test_report import CLEAN

P_GUARD, W_GUARD = 200.0, 50.0 / 12  # lb, lb/in: the default guard loads
SPAN = 72.0


def _raw(rail_section="Pipe2STD", post_section="Pipe2STD", **tables) -> dict:
    """A round post on a round rail, 6'-0", no intermediate rail. Each
    keyword replaces or extends one table of the project."""
    raw = {
        "project": {"name": "chord"},
        "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
        "top_rail": {"section": rail_section}, "post": {"section": post_section},
        "welds": {"rail_to_post": "1/8", "post_to_baseplate": "1/4"},
        "baseplate": {"B": 6, "N": 6}, "intermediate_rail": {"none": True},
    }
    for name, table in tables.items():
        raw[name] = {**raw.get(name, {}), **table}
    return raw


def _run(reg=None, **kw):
    reg = reg or Registry()
    return engine.run(project.from_dict(_raw(**kw)), reg), reg


def _chord(res) -> ChordCheck:
    chord = res.check(3).chord
    assert isinstance(chord, ChordCheck)
    return chord


def _case(chord, direction, load_type="Distributed") -> ChordCase:
    return next(c for c in chord.cases if c.direction == direction and c.load_type == load_type)


def _value(lines, key):
    values = [ln.value for ln in lines if ln.key == key and ln.kind == "value"]
    assert values, f"no calc line with key {key!r}"
    return values[0]


def _keys(lines) -> set[str]:
    return {ln.key for ln in lines if ln.kind == "value"}


def _f(q, unit="") -> float:
    return float(q.m_as(unit)) if hasattr(q, "m_as") else float(q)


class Hand:
    """The chord equations in plain arithmetic, from the published sections
    and the registry (kips and inches)."""

    def __init__(self, res, reg):
        rail, post = res.rail, res.post
        self.D, self.t, self.S = _f(rail.OD, "inch"), _f(rail.tdes, "inch"), _f(rail.S, "inch**3")
        self.Db = _f(post.OD, "inch")
        self.Fy = 35.0  # A53 Gr B, the pipe default
        self.beta, self.gamma = self.Db / self.D, self.D / (2 * self.t)
        self.e = self.D / 2
        self.w_D = _f(res.loading.w_D, "lbf/inch")
        self.D_rail = self.w_D * SPAN
        self.M_D = self.w_D * SPAN**2 / 8
        v = lambda entry: reg.entries[entry].value
        self.c = {name: v(f"aisc360.eq.{name}") for name in (
            "K3-1.coeff", "K3-2.coeff_constant", "K3-2.coeff_beta", "K3-2.exponent", "K4-1.coeff", "K4-1.exponent",
            "K4-2.coeff", "K4-3.coeff", "K4-3.coeff_beta", "K4-4.coeff", "K1-3.coeff")}
        self.Om_pl, self.Om_v = v("aisc360.K3.1.omega_plastification"), v("aisc360.K3.1.omega_punching")
        self.Fc = v("aisc360.K1.1.Fc_asd") * self.Fy

    def Qf(self, M_ro_lbin: float) -> float:
        U = M_ro_lbin / 1000 / (self.Fc * self.S)
        return 1 - self.c["K1-3.coeff"] * U * (1 + U)

    def Pc_pl(self, Qf: float) -> float:  # lb
        c = self.c
        Pn = (self.Fy * self.t**2 * (c["K3-2.coeff_constant"] + c["K3-2.coeff_beta"] * self.beta**2)
              * self.gamma ** c["K3-2.exponent"] * Qf)
        return 1000 * Pn / self.Om_pl

    def Mc_op_pl(self, Qf: float) -> float:  # lb-in
        c = self.c
        Mn = self.Fy * self.t**2 * self.Db * c["K4-3.coeff"] / (1 - c["K4-3.coeff_beta"] * self.beta) * Qf
        return 1000 * Mn / self.Om_pl

    def Mc_ip_pl(self, Qf: float) -> float:
        c = self.c
        Mn = c["K4-1.coeff"] * self.Fy * self.t**2 * self.gamma ** c["K4-1.exponent"] * self.beta * self.Db * Qf
        return 1000 * Mn / self.Om_pl

    def Pc_v(self) -> float:
        return 1000 * self.c["K3-1.coeff"] * self.Fy * self.t * math.pi * self.Db / self.Om_v

    def Mc_v(self, name: str) -> float:
        return 1000 * self.c[name] * self.Fy * self.t * self.Db**2 / self.Om_v


# ---------------------------------------------------------------------------
# Where the check is made, and where it reports
# ---------------------------------------------------------------------------


def test_a_round_post_on_a_round_rail_has_the_chord_check_inside_check_3():
    res, _ = _run()
    chord = _chord(res)
    assert chord.number == "3 (chord wall)"
    # No check is added to the seven (plan, Goal).
    assert [c.number for c in res.checks] == [1, 2, 3, "4a", "4b", 5, 6, 7]
    # Every direction case and load type of the weld envelope (W10).
    weld = res.check(3)
    assert [(c.direction, c.load_type) for c in chord.cases] == [(c.direction, c.load_type) for c in weld.cases]


def test_check_3s_own_ratio_and_lines_stay_the_welds():
    """S6-16 item 1: the chord interaction is not folded into Check 3."""
    res, _ = _run()
    weld, chord = res.check(3), _chord(res)
    assert weld.controlling.ratio != chord.controlling.ratio
    assert "Q_f" not in _keys(weld.controlling.lines)
    assert not any(ln.kind == "decision" and "Rail wall" in ln.symbol for ln in weld.controlling.lines)


@pytest.mark.parametrize("members", [
    {"top_rail": {"section": "HSS4X2X1/8", "long_side": "vertical"},
     "post": {"section": "Pipe1-1/2STD"}},                                                  # round post, rectangular rail
    {"post": {"section": "HSS2X2X1/8"}, "welds": {"base_pattern": "all around"}},          # square post, round rail
    {"top_rail": {"section": "HSS4X2X1/8", "long_side": "vertical"},
     "post": {"section": "HSS2X2X1/8"}, "welds": {"base_pattern": "all around"}},          # both rectangular
])
def test_no_chord_check_and_no_summary_row_unless_both_are_round(members):
    res, reg = _run(**members)
    assert res.check(3).chord is None
    src = report.build_source(res, reg, CLEAN)
    assert "3 (chord wall)" not in src and "chord limit states\")" not in src
    # The stated assumption's line stays in Check 3 (S6-9, S6-12).
    assert any(ln.kind == "decision" and "Rail wall, normal force" in ln.symbol
               for ln in res.check(3).controlling.lines)


def test_the_summary_gains_one_row_after_check_3s():
    res, reg = _run()
    src = report.build_source(res, reg, CLEAN)
    summary = src[src.index("= Summary"):]
    assert summary.count('"3 (chord wall). Top rail wall at the post"') == 1
    assert summary.index('"3. Top rail weld to post"') < summary.index('"3 (chord wall).') < summary.index('"4a. ')
    assert "chord limit states" in src[src.index("= Check 3"):src.index("= Check 4a")]


# ---------------------------------------------------------------------------
# The numbers (S6-10)
# ---------------------------------------------------------------------------


def test_the_branch_actions_are_the_weld_envelopes():
    res, reg = _run()
    chord, h = _chord(res), Hand(res, reg)
    down = _case(chord, "Downward")
    assert _f(down.Pr, "lbf") == pytest.approx(h.D_rail + W_GUARD * SPAN)
    assert down.Mr is None and down.plane == "" and down.sense == "compression"
    up = _case(chord, "Upward")
    assert _f(up.Pr, "lbf") == pytest.approx(W_GUARD * SPAN - 0.6 * h.D_rail)
    assert up.sense == "tension" and up.Mr is None
    for direction, plane in (("Outward", OUT_OF_PLANE), ("Inward", OUT_OF_PLANE), ("Longitudinal", IN_PLANE)):
        c = _case(chord, direction, "Concentrated")
        assert _f(c.Pr, "lbf") == pytest.approx(h.D_rail)
        assert _f(c.Mr, "lbf*inch") == pytest.approx(P_GUARD * h.e)
        assert c.plane == plane


def test_qf_uses_the_moment_that_stresses_the_underside():
    res, reg = _run()
    chord, h = _chord(res), Hand(res, reg)
    # Downward: the vertical moment of that case, D and L.
    assert _case(chord, "Downward", "Concentrated").Qf == pytest.approx(h.Qf(h.M_D + P_GUARD * SPAN / 4))
    assert _case(chord, "Downward").Qf == pytest.approx(h.Qf(h.M_D + W_GUARD * SPAN**2 / 8))
    # Horizontal: the dead-load moment only, whatever the guard load.
    for direction in ("Outward", "Inward", "Longitudinal"):
        for lt in ("Concentrated", "Distributed"):
            assert _case(chord, direction, lt).Qf == pytest.approx(h.Qf(h.M_D))
    assert _case(chord, "Downward").Qf < _case(chord, "Outward").Qf < 1.0
    # Upward: the underside is in tension.
    for lt in ("Concentrated", "Distributed"):
        up = _case(chord, "Upward", lt)
        assert up.Qf == 1.0
        assert "U" not in _keys(up.lines) and "M_ro" not in _keys(up.lines)


def test_plastification_strengths_and_the_interaction_at_equal_diameters():
    res, reg = _run()
    chord, h = _chord(res), Hand(res, reg)
    assert not chord.punching and h.Db >= h.D - 2 * h.t

    down = _case(chord, "Downward")
    Pc = h.Pc_pl(h.Qf(h.M_D + W_GUARD * SPAN**2 / 8))
    assert _f(down.Pc, "lbf") == pytest.approx(Pc)
    assert down.ratio == pytest.approx((h.D_rail + W_GUARD * SPAN) / Pc)
    assert down.P_state == PLASTIFICATION and down.Mc is None

    Qf = h.Qf(h.M_D)
    out = _case(chord, "Outward")
    assert _f(out.Mc, "lbf*inch") == pytest.approx(h.Mc_op_pl(Qf))
    # Eq. K4-5: the out-of-plane term is linear,
    assert out.ratio == pytest.approx(h.D_rail / h.Pc_pl(Qf) + W_GUARD * SPAN * h.e / h.Mc_op_pl(Qf))
    assert _case(chord, "Inward").ratio == pytest.approx(out.ratio)
    # and the in-plane term is squared.
    lon = _case(chord, "Longitudinal")
    assert _f(lon.Mc, "lbf*inch") == pytest.approx(h.Mc_ip_pl(Qf))
    assert lon.ratio == pytest.approx(h.D_rail / h.Pc_pl(Qf) + (W_GUARD * SPAN * h.e / h.Mc_ip_pl(Qf)) ** 2)

    up = _case(chord, "Upward")
    assert up.ratio == pytest.approx((W_GUARD * SPAN - 0.6 * h.D_rail) / h.Pc_pl(1.0))
    for c in chord.checked:
        assert "P_c_v" not in _keys(c.lines) and "M_c_v" not in _keys(c.lines)
        assert c.ok


def test_punching_applies_where_the_post_fits_inside_the_rails_wall():
    res, reg = _run(post_section="Pipe1STD")
    chord, h = _chord(res), Hand(res, reg)
    assert chord.punching and h.Db < h.D - 2 * h.t
    Qf = h.Qf(h.M_D)

    out = _case(chord, "Outward")
    assert _f(_value(out.lines, "P_c_v"), "lbf") == pytest.approx(h.Pc_v())
    assert _f(_value(out.lines, "M_c_v"), "lbf*inch") == pytest.approx(h.Mc_v("K4-4.coeff"))
    assert _f(out.Pc, "lbf") == pytest.approx(min(h.Pc_pl(Qf), h.Pc_v()))
    assert _f(out.Mc, "lbf*inch") == pytest.approx(min(h.Mc_op_pl(Qf), h.Mc_v("K4-4.coeff")))
    assert out.M_state == (PLASTIFICATION if h.Mc_op_pl(Qf) <= h.Mc_v("K4-4.coeff") else PUNCH)

    # In this pair punching is the lower in-plane strength: the branch the
    # equal-diameter joints never take.
    lon = _case(chord, "Longitudinal")
    assert h.Mc_v("K4-2.coeff") < h.Mc_ip_pl(Qf)
    assert lon.M_state == PUNCH and lon.P_state == PLASTIFICATION
    assert _f(lon.Mc, "lbf*inch") == pytest.approx(h.Mc_v("K4-2.coeff"))
    assert lon.ratio == pytest.approx(h.D_rail / _f(lon.Pc, "lbf") + (W_GUARD * SPAN * h.e / h.Mc_v("K4-2.coeff")) ** 2)

    # The upward case's tension is held to both limit states too.
    up = _case(chord, "Upward")
    assert _f(up.Pc, "lbf") == pytest.approx(min(h.Pc_pl(1.0), h.Pc_v()))


def test_the_table_says_where_punching_does_not_apply():
    for post, applies in (("Pipe2STD", False), ("Pipe1STD", True)):
        res, reg = _run(post_section=post)
        src = report.build_source(res, reg, CLEAN)
        assert ("Shear yielding (punching) does not apply: the post is not narrower" in src) is not applies
        decisions = [ln.text for ln in _chord(res).controlling.lines if ln.kind == "decision"]
        assert ("Shear yielding (punching) applies" in decisions) is applies
        assert ("Shear yielding (punching) does not apply" in decisions) is not applies


# ---------------------------------------------------------------------------
# What prints in full (S6-1)
# ---------------------------------------------------------------------------


def _with_threshold(value: float) -> Registry:
    reg = Registry()
    entry = reg.entries["ej.weld.chord.print_threshold"]
    reg.entries[entry.id] = dataclasses.replace(entry, value=value)
    return reg


def test_only_the_governing_case_prints_in_full_under_the_threshold():
    res, reg = _run()
    chord = _chord(res)
    assert chord.threshold == 0.5 and chord.controlling.ratio < 0.5
    assert chord.full == [chord.controlling]
    src = report.build_source(res, reg, CLEAN)
    assert src.count("Chord limit states, governing case: ") == 1
    assert "Chord limit states, case over" not in src


def test_a_second_case_over_the_threshold_prints_its_lines():
    res, _ = _run()
    ratios = sorted(c.ratio for c in _chord(res).checked)
    # Between the two highest ratios, a threshold lets exactly the runner-up
    # (and any case tied with it) print beside the governing case.
    threshold = (ratios[-3] + ratios[-2]) / 2 if ratios[-2] > ratios[-3] else ratios[-3] / 2
    reg = _with_threshold(threshold)
    res, reg = _run(reg)
    chord = _chord(res)
    over = [c for c in chord.checked if c.ratio > threshold]
    assert len(over) >= 2
    assert chord.full[0] is chord.controlling
    assert sorted(id(c) for c in chord.full) == sorted(id(c) for c in over)
    src = report.build_source(res, reg, CLEAN)
    assert src.count("Chord limit states, governing case: ") == 1
    assert src.count(f"Chord limit states, case over {threshold:g}: ") == len(over) - 1


def test_every_case_has_a_table_row_with_its_own_verdict():
    res, reg = _run()
    src = report.build_source(res, reg, CLEAN)
    block = src[src.index("Top rail wall at the post: chord limit states"):src.index("Chord limit states, governing case")]
    assert block.count('"OK"') == len(_chord(res).checked) == 10
    assert block.count('"NG"') == 0


# ---------------------------------------------------------------------------
# A rail stressed past Eq. K1-3
# ---------------------------------------------------------------------------


def test_a_chord_stress_that_leaves_no_strength_is_ng_not_a_negative_ratio():
    """Eq. K1-3 goes to zero near U = 1.39. A 14 ft span takes the downward
    distributed case past it (U = 1.42 on a Pipe2STD); the check is NG
    outright and no ratio is divided out."""
    res, reg = _run(geometry={"span": "14'-0\""})
    chord, h = _chord(res), Hand(res, reg)
    M_ro = (h.w_D + W_GUARD) * 168.0**2 / 8
    assert M_ro / 1000 / (h.Fc * h.S) > 1.39
    down = _case(chord, "Downward")
    assert down.no_strength and down.status == "not checked" and down.ratio is None and not down.ok
    assert _f(_value(down.lines, "Q_f")) <= 0
    assert "P_n" not in _keys(down.lines)
    # The concentrated load's moment leaves the wall some strength, and that case is checked as usual.
    assert not _case(chord, "Downward", "Concentrated").no_strength
    assert chord.failures and chord.verdict == "NG" and not chord.ok
    assert all(c.ratio is not None and c.ratio >= 0 for c in chord.checked)
    assert down in chord.full and chord.full[0] is chord.controlling
    src = report.build_source(res, reg, CLEAN)
    assert "NG (no chord strength)" in src[src.index("= Summary"):]
    assert src.count("Chord limit states, case with no available strength: ") == 1


def test_the_exempt_distributed_load_is_listed_and_not_checked():
    res, _ = _run(loads={"uniform_exemption": {"applies": True, "statement": "One- and two-family dwelling."}})
    chord = _chord(res)
    assert [c.status for c in chord.cases if c.load_type == "Distributed"] == ["exempt"] * 5
    assert chord.controlling.load_type == "Concentrated"
