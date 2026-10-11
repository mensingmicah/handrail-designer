"""Welds at rectangular and mixed joints (docs/brief/welds.md, S6-6 to S6-9,
S6-11 to S6-13; docs/brief/checks.md, S6-14 and S6-16; docs/plans/slice-6.md,
T5).

Machinery tests, same-author: they hold the code to the brief's rules. They
are not test cases, and no value here is a hand or independent value. Where
a number is compared it is worked here from the section's published
dimensions by a closed form, or by summing the weld line numerically, not
copied from the tool.
"""

import dataclasses
import math

import pytest

from handrail import engine, project, report, shapes, weld_lines
from handrail.dimensions import parse
from handrail.errors import InputError, SectionStop
from handrail.orientation import post_axes
from handrail.project import ProjectError
from handrail.registry import Registry
from handrail.stops import Stop
from handrail.units import Q_
from handrail.weld_lines import LONGITUDINAL, TRANSVERSE, Side
from handrail.welds import WeldCase
import stand_ins

T_DES = 0.116  # the published design wall of every 1/8 in HSS used here


def _raw(**tables) -> dict:
    """An all-rectangular guard that runs: an HSS4X2X1/8 rail on edge over
    an HSS3X2X1/8 post with its long side along the rail, welded all
    around, 6'-0", no intermediate rail. Each keyword replaces or extends
    one table; a key given as None is removed."""
    raw = {
        "project": {"name": "rect welds"},
        "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
        "top_rail": {"section": "HSS4X2X1/8", "long_side": "vertical"},
        "post": {"section": "HSS3X2X1/8", "long_side": "parallel to rail"},
        "welds": {"rail_to_post": "1/8", "post_to_baseplate": "3/16", "base_pattern": "all around"},
        "baseplate": {"B": 6, "N": 8}, "intermediate_rail": {"none": True},
    }
    for name, table in tables.items():
        merged = table if name == "intermediate_rail" else {**raw.get(name, {}), **table}
        raw[name] = {key: value for key, value in merged.items() if value is not None}
    return raw


def _run(**tables):
    return engine.run(project.from_dict(_raw(**tables)), Registry())


def _stops(stop: Stop, **tables) -> str:
    with pytest.raises(InputError) as stopped:
        _run(**tables)
    assert stopped.value.stop is stop, str(stopped.value)
    return str(stopped.value)


def _value(lines, key):
    values = [ln.value for ln in lines if ln.key == key and ln.kind == "value"]
    assert values, f"no calc line with key {key!r}"
    return values[0]


def _decisions(lines) -> dict[str, str]:
    return {ln.symbol: ln.text for ln in lines if ln.kind == "decision"}


def _case(chk, direction, load_type="Distributed") -> WeldCase:
    return next(c for c in chk.checked if c.direction == direction and c.load_type == load_type)


SQUARE = {"section": "HSS2X2X1/8", "long_side": None}
PIPE_RAIL = {"section": "Pipe2STD", "long_side": None}
PIPE_POST = {"section": "Pipe2STD", "long_side": None}
OWN_WELD = {"intermediate_rail_to_post": "1/8"}


# ---------------------------------------------------------------------------
# The weld lines (S6-6, S6-8)
# ---------------------------------------------------------------------------

def _summed_line(a: float, b: float, R: float, n: int = 20000) -> tuple[float, float]:
    """Length and moment of inertia about the axis parallel to side a of a
    rounded rectangle a by b as a line, by summing short pieces of it: an
    independent check on the closed form the tool prints."""
    length = inertia = 0.0
    for sign in (1, -1):                       # the two flats parallel to the axis
        length += a - 2 * R
        inertia += (a - 2 * R) * (sign * b / 2) ** 2
    half = b / 2 - R
    for _ in range(2):                         # the two flats across it
        length += 2 * half
        inertia += (2 * half) ** 3 / 12
    for i in range(n):                         # the four corner arcs
        t = (i + 0.5) * (math.pi / 2) / n
        y = half + R * math.sin(t)
        d = R * (math.pi / 2) / n
        length += 4 * d
        inertia += 4 * d * y * y
    return length, inertia


@pytest.mark.parametrize("label, long_side", [("HSS2X2X1/8", ""), ("HSS3X2X1/8", "parallel to rail"),
                                               ("HSS3X2X1/8", "perpendicular to rail")])
def test_the_rounded_rectangle_is_the_true_outline_as_a_line(label, long_side):
    """S6-6: straight runs on the flats and quarter-circle arcs on the
    outside radius, 2 t_des. A load across the guard bends the line over
    the post's dimension perpendicular to the rail."""
    sec = shapes.section(label)
    ax = post_axes(sec, long_side)
    par, perp = ax.parallel.m_as("inch"), ax.perpendicular.m_as("inch")
    rg = weld_lines.rounded_rectangle(
        Registry(), sec, parse("3/16"), "post",
        along=Side("a_par", 'a_"par"', ax.parallel, "parallel"), across=Side("a_perp", 'a_"perp"', ax.perpendicular, "perp"))
    R = 2 * T_DES
    assert _value(rg.lines, "R_o").m_as("inch") == pytest.approx(R)
    L, I_t = _summed_line(par, perp, R)
    _, I_l = _summed_line(perp, par, R)
    assert rg.L_w.value.m_as("inch") == pytest.approx(L, rel=1e-6)
    assert rg.L_w.value.m_as("inch") == pytest.approx(2 * (par - 2 * R) + 2 * (perp - 2 * R) + 2 * math.pi * R)
    assert rg.S_by[TRANSVERSE].value.m_as("in^2") == pytest.approx(I_t / (perp / 2), rel=1e-6)
    assert rg.S_by[LONGITUDINAL].value.m_as("in^2") == pytest.approx(I_l / (par / 2), rel=1e-6)
    assert rg.S_w is None and rg.uniform == "uniform along the weld line"


def test_the_rounded_line_sits_between_sharp_corners_and_flats_alone():
    """The brief's planning figures for HSS2X2X1/8 (S6-6): 5.33 in^2 on a
    sharp-cornered rectangle, about 4.90 on the rounded one, 3.68 on the
    flats alone."""
    sec = shapes.section("HSS2X2X1/8")
    side = Side("a", "a", sec.rect.H, "side")
    rg = weld_lines.rounded_rectangle(Registry(), sec, parse("3/16"), "post", along=side,
                                      across=dataclasses.replace(side, key="b", symbol="b"))
    S = rg.S_by[TRANSVERSE].value.m_as("in^2")
    sharp, flats = 2 * 2 + 2**2 / 3, (2 * 1.536 * 1 + 2 * 1.536**3 / 12) / 1
    assert flats < S < sharp
    assert S == pytest.approx(4.906, abs=0.001)


@pytest.mark.parametrize("pattern, strong, weak", [("faces parallel to rail", TRANSVERSE, LONGITUDINAL),
                                                    ("faces perpendicular to rail", LONGITUDINAL, TRANSVERSE)])
def test_a_face_pair_is_two_flat_lines_between_the_tangent_points(pattern, strong, weak):
    """S6-6. HSS3X2X1/8 with its long side along the rail: the faces
    parallel to the rail are the 3 in ones, 2 in apart; the faces
    perpendicular to it the 2 in ones, 3 in apart. Each line is its face
    less four design walls. The lines are the extreme fibers for a load
    across them, and bend about their own middle for a load along them."""
    sec = shapes.section("HSS3X2X1/8")
    ax = post_axes(sec, "parallel to rail")
    face, apart = (3.0, 2.0) if pattern == "faces parallel to rail" else (2.0, 3.0)
    rg = weld_lines.face_pair(Registry(), sec, parse("3/16"), pattern, ax)
    line = face - 4 * T_DES
    assert _value(rg.lines, "l_w").m_as("inch") == pytest.approx(line)
    assert rg.L_w.value.m_as("inch") == pytest.approx(2 * line)
    assert rg.S_by[strong].value.m_as("in^2") == pytest.approx(line * apart)
    assert rg.S_by[weak].value.m_as("in^2") == pytest.approx(line**2 / 3)
    assert "each welded face" in next(ln.note for ln in rg.lines if ln.key == "w")


def test_a_face_pair_takes_only_its_two_phrases():
    with pytest.raises(ValueError, match="base_pattern 'all around'"):
        weld_lines.face_pair(Registry(), shapes.section("HSS2X2X1/8"), parse("3/16"), "all around",
                             post_axes(shapes.section("HSS2X2X1/8"), ""))


def _k5(chord: str, face: float, branch: str, depth: float, width: float, bending: bool = True):
    c, b = shapes.section(chord), shapes.section(branch)
    return weld_lines.table_k5_1(
        Registry(), parse("1/8"), c, "A500 Gr B", "Top rail", Side("B_chord", "B", Q_(face, "inch"), "chord face"),
        b, "A500 Gr B", "Post", Side("H_b", "H_b", Q_(depth, "inch"), "branch depth"),
        Side("B_b", "B_b", Q_(width, "inch"), "branch width"), bending=bending)


def test_table_k5_1_with_the_effective_width_uncapped():
    """A slender chord face: HSS4X4X1/8, B/t = 34.5, under a 2 x 2 branch
    of the same wall and grade. Eq. K1-1 gives Be = (10/34.5) Bb = 0.58 in,
    under the cap of Bb/2 = 1 in. Then le, Sip and Sop by Eqs. K5-5 to
    K5-7 per unit throat."""
    rg = _k5("HSS4X4X1/8", 4.0, "HSS2X2X1/8", 2.0, 2.0)
    Be = 10 / (4.0 / T_DES) * 2.0
    assert Be < 1.0
    assert _value(rg.lines, "B_e_K1").m_as("inch") == pytest.approx(Be)
    assert _value(rg.lines, "B_e").m_as("inch") == pytest.approx(Be)
    assert rg.L_w.value.m_as("inch") == pytest.approx(2 * 2.0 + 2 * Be)
    assert rg.S_by[LONGITUDINAL].value.m_as("in^2") == pytest.approx(2.0**2 / 3 + Be * 2.0)
    assert rg.S_by[TRANSVERSE].value.m_as("in^2") == pytest.approx(2.0 * 2.0 + 2.0**2 / 3 - (2.0 - Be) ** 3 / (3 * 2.0))


def test_table_k5_1_with_the_effective_width_capped_at_equal_widths():
    """The brief's planning figures (S6-8): an HSS2X2X1/8 post under an
    HSS2X2X1/8 rail. Eq. K1-1 gives 0.58 Bb, and the cap holds Be to Bb/2:
    le = 6 in against a perimeter of 8, Sop 3% and Sip 37% below the
    full-perimeter values (exactly 31/32 and 5/8 of them)."""
    rg = _k5("HSS2X2X1/8", 2.0, "HSS2X2X1/8", 2.0, 2.0)
    assert _value(rg.lines, "B_e_K1").m_as("inch") == pytest.approx(10 / (2.0 / T_DES) * 2.0)
    assert _value(rg.lines, "B_e").m_as("inch") == pytest.approx(1.0)
    assert rg.L_w.value.m_as("inch") == pytest.approx(6.0)
    full = 2.0 * 2.0 + 2.0**2 / 3
    assert rg.S_by[TRANSVERSE].value.m_as("in^2") / full == pytest.approx(31 / 32)
    assert rg.S_by[LONGITUDINAL].value.m_as("in^2") / full == pytest.approx(5 / 8)


def test_table_k5_1_scales_the_effective_width_by_the_two_walls_and_grades():
    """Eq. K1-1's second factor, Fy t / (Fyb tb): a 3/16 in chord under a
    1/8 in branch."""
    rg = _k5("HSS4X4X3/16", 4.0, "HSS2X2X1/8", 2.0, 2.0)
    t = shapes.section("HSS4X4X3/16").tdes.m_as("inch")
    assert _value(rg.lines, "B_e_K1").m_as("inch") == pytest.approx(10 / (4.0 / t) * (t / T_DES) * 2.0)


def test_the_cap_applies_below_beta_0_85_as_the_table_prints_it():
    """WAITING ON MICAH (docs/plans/slice-6.md, open item 1). Table K5.1
    reads 'when beta > 0.85 or theta > 50 degrees, Be/2 shall not exceed
    Bb/4'; S6-8 paraphrases it as 'when beta > 0.85'. Every branch here is
    at 90 degrees, so as printed the cap always applies, and the tool
    applies it as printed. This is the one kind of joint where the two
    readings differ: beta = 0.5 on a stocky chord face (HSS2X2X1/8, B/t =
    17.2), where Eq. K1-1 gives 0.58 Bb. The tool gives Be = Bb/2; the
    paraphrase would give 0.58 Bb. If Micah rules for the paraphrase, this
    test and weld_lines.table_k5_1 change together."""
    rg = _k5("HSS2X2X1/8", 2.0, "HSS2X1X1/8", 2.0, 1.0)
    uncapped = 10 / (2.0 / T_DES) * 1.0
    assert uncapped > 0.5
    assert _value(rg.lines, "B_e_K1").m_as("inch") == pytest.approx(uncapped)
    assert _value(rg.lines, "B_e").m_as("inch") == pytest.approx(0.5)


def test_without_bending_a_line_prints_its_length_only():
    rg = _k5("HSS2X2X1/8", 2.0, "HSS2X1X1/8", 1.0, 2.0, bending=False)
    assert rg.S_by == {} and not any(ln.key.startswith("S_w") for ln in rg.lines)
    assert rg.L_w.value.m_as("inch") == pytest.approx(2 * 1.0 + 2 * 1.0)


# ---------------------------------------------------------------------------
# Check 7 on a rectangular post (S6-6, S6-7)
# ---------------------------------------------------------------------------

def test_a_rectangular_post_welded_all_around_runs_on_its_rounded_rectangle():
    res = _run()
    chk = res.check(7)
    out, along = _case(chk, "Outward"), _case(chk, "Longitudinal")
    lines = out.lines
    # The post is 2 in across the rail and 3 in along it.
    assert (_value(lines, "a_par").m_as("inch"), _value(lines, "a_perp").m_as("inch")) == (3, 2)
    M = 300.0 * 41.5
    assert out.f_b.m_as("lbf/inch") == pytest.approx(M / _value(lines, "S_w_t").m_as("in^2"))
    assert along.f_b.m_as("lbf/inch") == pytest.approx(M / _value(lines, "S_w_l").m_as("in^2"))
    assert out.f_b > along.f_b                      # the transverse load bends the line over its 2 in depth
    assert out.f_v.m_as("lbf/inch") == pytest.approx(300.0 / _value(lines, "L_w").m_as("inch"))
    assert chk.controlling.direction in ("Outward", "Inward")
    assert _decisions(lines)['"Post wall at the weld"'] == "Covered by Check 5"
    assert out.wall_ratio is None and out.governs == "weld metal"
    assert [c.status for c in chk.cases] == ["checked"] * 10        # all five direction cases, both load types


def test_k_ds_is_1_for_every_rectangular_post_and_says_why():
    reg = Registry()
    res = engine.run(project.from_dict(_raw()), reg)
    lines = res.check(7).controlling.lines
    k_ds = next(ln for ln in lines if ln.key == "k_ds")
    assert k_ds.value == reg.get("aisc360.J2.4.kds_rect_hss").value == 1.0
    assert k_ds.cite == "AISC 360-22 §J2.4(a)(2)"
    note = next(ln for ln in lines if ln.kind == "decision" and ln.text == "No directional increase")
    assert note.cite == "AISC 360-22 §K5, User Note" and note.note == reg.get("aisc360.K5.user_note.rect_hss_kds").value
    assert all(c.theta is None and c.k_ds == 1.0 for c in res.check(7).checked)
    assert "aisc360.J2.4.kds_other" not in {e.id for e in reg.used}


@pytest.mark.parametrize("post, pattern, strong", [
    (SQUARE, "faces parallel to rail", "Outward"),
    (SQUARE, "faces perpendicular to rail", "Longitudinal"),
    ({"section": "HSS3X2X1/8", "long_side": "parallel to rail"}, "faces parallel to rail", "Outward"),
    ({"section": "HSS3X2X1/8", "long_side": "perpendicular to rail"}, "faces perpendicular to rail", "Longitudinal"),
])
def test_a_face_pair_runs_all_five_cases_and_is_weak_across_its_own_lines(post, pattern, strong):
    """S6-6: all five direction cases run on either pattern. The case that
    bends the two lines about their own length governs by a wide margin
    (plan, open item 7)."""
    wide_rail = {"section": "HSS4X3X1/8", "long_side": "horizontal"}   # 4 in wide: wide enough for either post
    chk = _run(top_rail=wide_rail, post=post, welds={"base_pattern": pattern}).check(7)
    weak = "Longitudinal" if strong == "Outward" else "Outward"
    assert [c.status for c in chk.cases] == ["checked"] * 10
    assert chk.controlling.direction in (weak, "Inward") and chk.controlling.direction != strong
    assert _case(chk, weak).ratio > 2 * _case(chk, strong).ratio
    assert _case(chk, weak).f_b > _case(chk, strong).f_b


def test_the_post_wall_at_a_face_pair_is_checked_on_its_own_lines_not_combined():
    """S6-7. The brief's planning figures: HSS2X2X1/8, 42 in, 200 lb at the
    top, faces parallel to the rail, 3/16 in fillets, at 46 and 58 ksi:
    f about 2.70 kip/in; weld metal 2.78 (0.97); post wall yielding 3.20
    (0.84)."""
    reg = Registry()
    res = engine.run(project.from_dict(_raw(top_rail=PIPE_RAIL, post=SQUARE,
                                             welds={"base_pattern": "faces parallel to rail"})), reg)
    chk = res.check(7)
    out = _case(chk, "Outward", "Concentrated")
    Fy, Fu = reg.get("material.A500_GrB.hss_rect.Fy").value, reg.get("material.A500_GrB.hss_rect.Fu").value
    yielding, rupture = Fy * T_DES / 1.67 * 1000, Fu * T_DES / 2.00 * 1000
    assert out.wall_allow.m_as("lbf/inch") == pytest.approx(min(yielding, rupture)) == pytest.approx(yielding)
    assert out.wall_allow.m_as("kip/inch") == pytest.approx(3.20, abs=0.01)
    assert out.f_b.m_as("kip/inch") == pytest.approx(2.70, abs=0.01)     # the bending force; the dead load adds 0.01
    assert out.weld_ratio == pytest.approx(0.97, abs=0.01)
    assert out.wall_ratio == pytest.approx(out.f_n.m_as("lbf/inch") / yielding) == pytest.approx(0.85, abs=0.01)
    assert out.ratio == max(out.weld_ratio, out.base_ratio, out.wall_ratio)
    words = _decisions(out.lines)
    assert words['"Post wall at the weld"'] == "Checked on its own lines"
    assert "Covered by Check 5" not in words.values()
    rule = next(ln for ln in out.lines if ln.kind == "decision" and ln.text == "Checked on its own lines")
    assert rule.note == reg.get("ej.weld.post_wall.face_pair").value


def test_the_face_pair_assumption_is_printed_with_the_others_word_for_word():
    """S6-7, Micah's addition: not combining the two components is a printed
    simplification. The sentence in the "Stated assumptions" list is the
    one Check 7 prints at the post wall lines, from the same registry entry."""
    assert Registry().get("ej.weld.post_wall.face_pair").value in report.LOCKED_ASSUMPTIONS


def test_the_post_walls_shear_check_takes_the_full_shear_whatever_its_direction():
    """S6-17 item 3 (Micah, 2026-10-11), settling S6-7's open item. At a
    face-pair weld the post wall's shear check is the full shear per inch of
    weld against shear rupture, 0.6 Fu t / 2.00, whether the load is along
    the welded faces or across them. A case with no horizontal force has no
    shear line."""
    reg = Registry()
    Fu = reg.get("material.A500_GrB.hss_rect.Fu").value
    for pattern, cases in (("faces parallel to rail", ("Longitudinal", "Outward")),
                           ("faces perpendicular to rail", ("Outward", "Longitudinal"))):
        chk = _run(top_rail=PIPE_RAIL, post=SQUARE, welds={"base_pattern": pattern}).check(7)
        for name in cases:
            case = _case(chk, name)
            face = _value(case.lines, "R_wall_face").m_as("lbf/inch")
            assert face == pytest.approx(0.6 * Fu * T_DES / 2.00 * 1000)
            assert _value(case.lines, "Ratio_wall_face") == pytest.approx(case.f_v.m_as("lbf/inch") / face)
            assert _value(case.lines, "Ratio_wall") == max(_value(case.lines, "Ratio_wall_axial"),
                                                           _value(case.lines, "Ratio_wall_face"))
    down = _case(chk, "Downward")
    assert not any(ln.key == "Ratio_wall_face" for ln in down.lines)
    assert "no horizontal force in this case" in next(ln.note for ln in down.lines if ln.key == "Ratio_wall")
    assert _value(down.lines, "Ratio_wall") == _value(down.lines, "Ratio_wall_axial")


def test_the_post_wall_can_govern_a_face_pair_weld():
    """With a weld large enough that the weld metal is not the limit, the
    wall's yielding along the post axis is: demand, capacity and ratio come
    from that line, and the envelope names it."""
    chk = _run(top_rail=PIPE_RAIL, post=SQUARE,
               welds={"base_pattern": "faces parallel to rail", "post_to_baseplate": "3/8"}).check(7)
    out = _case(chk, "Outward")
    assert out.wall_ratio > out.weld_ratio and out.governs == "post wall"
    assert (out.demand, out.capacity) == (out.f_n, out.wall_allow)
    assert out.ratio == out.wall_ratio


def test_the_base_pattern_is_required_for_a_rectangular_post_and_never_assumed():
    message = _stops(Stop.WELD_BASE_PATTERN_MISSING, welds={"base_pattern": None})
    assert message.startswith("[welds] is missing 'base_pattern': the post HSS3X2X1/8 is rectangular")
    assert message.endswith('Give base_pattern = "all around", "faces parallel to rail" or '
                            '"faces perpendicular to rail".')
    assert "the post HSS2X2X1/8 is rectangular" in _stops(Stop.WELD_BASE_PATTERN_MISSING, top_rail=PIPE_RAIL,
                                                           post=SQUARE, welds={"base_pattern": None})


def test_a_round_post_is_welded_all_around_and_a_face_pair_for_it_stops():
    round_post = {"top_rail": PIPE_RAIL, "post": PIPE_POST}
    for welds_table in ({"base_pattern": None}, {"base_pattern": "all around"}):
        assert _run(**round_post, welds={**welds_table, "post_to_baseplate": "1/4"}).check(7).ok is not None
    message = _stops(Stop.WELD_BASE_PATTERN_ON_ROUND_POST, **round_post,
                     welds={"base_pattern": "faces perpendicular to rail"})
    assert "the post Pipe2STD is round and is welded all around" in message


def test_electing_the_directional_increase_with_a_rectangular_post_stops():
    message = _stops(Stop.WELD_DIRECTIONAL_INCREASE_ON_RECTANGULAR_POST, welds={"directional_increase": True})
    assert message.startswith("[welds] directional_increase = true, but the post HSS3X2X1/8 is rectangular")
    assert "AISC 360-22 §J2.4(a)(2); AISC 360-22 §K5, User Note" in message


def test_the_base_pattern_stops_hold_when_a_calc_skips_validation():
    """Check 7 makes the same tests itself, as it does for its joint table."""
    reg = Registry()
    with pytest.raises(SectionStop) as stopped:
        engine.compute(project.from_dict(_raw(welds={"base_pattern": None})), reg)
    assert stopped.value.stop is Stop.WELD_BASE_PATTERN_MISSING


def test_a_face_pair_on_a_post_with_a_slender_wall_stops_at_the_compression_stop(monkeypatch):
    """S6-7, as confirmed by Micah: no separate stop. A post with a slender
    wall is stopped in compression before Check 7, so the yielding line of
    a face-pair weld never stands on a slender wall."""
    real = shapes.section

    def slender(designation):
        sec = real(designation)
        return stand_ins.replace(sec, b_t=36.0) if sec.label == "HSS2X2X1/8" else sec

    monkeypatch.setattr(shapes, "section", slender)
    with pytest.raises(SectionStop) as stopped:
        _run(top_rail=PIPE_RAIL, post=SQUARE, welds={"base_pattern": "faces parallel to rail"})
    assert stopped.value.stop is Stop.SECTION_SLENDER_IN_COMPRESSION


# ---------------------------------------------------------------------------
# Check 3: the rail to post weld at rectangular and mixed joints (S6-8, S6-9)
# ---------------------------------------------------------------------------

def test_check_3_at_a_rectangular_rail_and_post_uses_table_k5_1():
    """The post's dimension along the rail is the branch depth Hb, its
    dimension across the rail the branch width Bb, and the rail's
    horizontal dimension the chord face. The longitudinal case is in-plane
    bending, the transverse cases out-of-plane, at e = half the rail depth."""
    reg = Registry()
    res = engine.run(project.from_dict(_raw()), reg)
    chk = res.check(3)
    out, along, down = _case(chk, "Outward"), _case(chk, "Longitudinal"), _case(chk, "Downward")
    lines = out.lines
    assert (_value(lines, "B_chord").m_as("inch"), _value(lines, "H_b").m_as("inch"),
            _value(lines, "B_b").m_as("inch")) == (2, 3, 2)
    assert _value(lines, "e").m_as("inch") == 2.0                    # half the 4 in rail depth
    assert _value(lines, "B_e").m_as("inch") == pytest.approx(1.0)   # capped at Bb/2
    le = _value(lines, "L_w").m_as("inch")
    assert le == pytest.approx(2 * 3 + 2 * 1.0)
    M = 300.0 * 2.0
    assert out.f_b.m_as("lbf/inch") == pytest.approx(M / _value(lines, "S_w_t").m_as("in^2"))
    assert along.f_b.m_as("lbf/inch") == pytest.approx(M / _value(lines, "S_w_l").m_as("in^2"))
    assert out.f_v.m_as("lbf/inch") == pytest.approx(300.0 / le)
    assert down.f_a.m_as("lbf/inch") == pytest.approx((res.loading.D_rail.m_as("lbf") + 300.0) / le)
    assert out.k_ds == 1.0 and out.theta is None
    words = _decisions(lines)
    assert words['"Rail wall, normal force"'] == "Not checked"
    assert reg.get("ej.weld.chord_wall.rect").value in {ln.note for ln in lines if ln.kind == "decision"}
    assert "Fillet model kept" in words.values()                    # post and rail are both 2 in wide
    assert words['"Post wall at the weld"'] == "Covered by Check 5"
    # The rail fusion face takes the in-plane shear over the effective length (S6-16 item 6).
    assert out.base_demand == out.f_v
    assert "ej.weld.ring_model" not in {e.id for e in reg.used}


def test_check_3_with_a_rectangular_post_on_a_round_rail_uses_the_posts_outline():
    """S6-9, a mixed pair: the post's rounded rectangle, flat at the rail's
    underside, e = half the rail's diameter; Table K5.1 is not used."""
    reg = Registry()
    res = engine.run(project.from_dict(_raw(top_rail=PIPE_RAIL, post=SQUARE)), reg)
    out = _case(res.check(3), "Outward")
    assert _value(out.lines, "e").m_as("inch") == pytest.approx(2.375 / 2)
    L, I = _summed_line(2.0, 2.0, 2 * T_DES)
    assert _value(out.lines, "L_w").m_as("inch") == pytest.approx(L, rel=1e-6)
    assert out.f_b.m_as("lbf/inch") == pytest.approx(300.0 * 2.375 / 2 / I, rel=1e-6)   # c = 1 in
    used = {e.id for e in reg.used}
    assert "ej.weld.line.outline_model" in used and "aisc360.eq.K5-5" not in used
    assert reg.get("ej.weld.chord_wall.mixed").value in {ln.note for ln in out.lines if ln.kind == "decision"}


def test_check_3_with_a_round_post_on_a_rectangular_rail_uses_the_posts_ring():
    """S6-9, the other mixed pair: the ring of the post, as for round on
    round, at e = half the rail's depth."""
    reg = Registry()
    res = engine.run(project.from_dict(_raw(top_rail={"section": "HSS4X3X1/8", "long_side": "horizontal"},
                                             post=PIPE_POST, welds={"base_pattern": None,
                                                                    "post_to_baseplate": "1/4"})), reg)
    out = _case(res.check(3), "Outward")
    assert _value(out.lines, "e").m_as("inch") == 1.5                # the rail lies flat: 3 in deep
    assert _value(out.lines, "L_w").m_as("inch") == pytest.approx(math.pi * 2.375)
    assert _value(out.lines, "S_w").m_as("in^2") == pytest.approx(math.pi * 2.375**2 / 4)
    assert reg.get("ej.weld.chord_wall.mixed").value in {ln.note for ln in out.lines if ln.kind == "decision"}
    assert "ej.weld.rail_wall_normal" not in {e.id for e in reg.used}


# ---------------------------------------------------------------------------
# Check 4b at rectangular and mixed joints (S6-8, S6-9, S6-11, S6-14 item 5)
# ---------------------------------------------------------------------------

RECT_INT = {"same_as_top_rail": False, "section": "HSS2X1X1/8", "long_side": "horizontal"}


def _line_4b(**tables):
    reg = Registry()
    res = engine.run(project.from_dict(_raw(**tables)), reg)
    chk = res.check("4b")
    return reg, res, chk, chk.controlling.lines


def test_check_4b_with_both_rectangular_uses_table_k5_1_with_the_post_as_the_chord():
    """The post's axis is vertical, so the branch depth Hb is the
    intermediate rail's vertical dimension and its width Bb the horizontal
    one, on the post face across the rail. A simple shear connection: only
    the effective length is used."""
    reg, res, chk, lines = _line_4b(intermediate_rail=RECT_INT, welds=OWN_WELD)
    assert (_value(lines, "B_chord").m_as("inch"), _value(lines, "H_b").m_as("inch"),
            _value(lines, "B_b").m_as("inch")) == (2, 1, 2)
    le = _value(lines, "L_w").m_as("inch")
    assert le == pytest.approx(2 * 1 + 2 * 1.0)
    assert not any(ln.key.startswith("S_w") for ln in lines)
    R = 50.0 + res.loading.w_D_int.m_as("lbf/inch") * 72 / 2
    assert chk.controlling.direction == "Downward"
    assert chk.controlling.f_v.m_as("lbf/inch") == pytest.approx(R / le)
    assert "Fillet model kept" in _decisions(lines).values()
    assert "ej.weld.intermediate_line_model" in {e.id for e in reg.used}


def test_check_4b_with_a_rectangular_rail_on_a_round_post_uses_the_rails_outline():
    reg, _, _, lines = _line_4b(top_rail=PIPE_RAIL, post=PIPE_POST, intermediate_rail=RECT_INT,
                                welds={**OWN_WELD, "base_pattern": None, "post_to_baseplate": "1/4"})
    L, _ = _summed_line(2.0, 1.0, 2 * T_DES)
    assert _value(lines, "L_w").m_as("inch") == pytest.approx(L, rel=1e-6)
    assert (_value(lines, "a_h").m_as("inch"), _value(lines, "a_v").m_as("inch")) == (2, 1)
    assert "aisc360.eq.K5-5" not in {e.id for e in reg.used}


def test_check_4b_with_a_round_rail_on_a_rectangular_post_uses_the_rails_ring():
    reg, _, _, lines = _line_4b(top_rail=PIPE_RAIL, post=SQUARE,
                                intermediate_rail={"same_as_top_rail": False, "section": "Pipe1-1/4STD"},
                                welds=OWN_WELD)
    assert _value(lines, "L_w").m_as("inch") == pytest.approx(math.pi * 1.66)
    assert "ej.weld.intermediate_ring_model" in {e.id for e in reg.used}


@pytest.mark.parametrize("tables", [
    {"intermediate_rail": RECT_INT, "welds": OWN_WELD},
    {"top_rail": PIPE_RAIL, "post": PIPE_POST, "intermediate_rail": RECT_INT,
     "welds": {**OWN_WELD, "base_pattern": None, "post_to_baseplate": "1/4"}},
    {"top_rail": PIPE_RAIL, "post": SQUARE,
     "intermediate_rail": {"same_as_top_rail": False, "section": "Pipe1-1/4STD"}, "welds": OWN_WELD},
    {"top_rail": PIPE_RAIL, "post": PIPE_POST,
     "intermediate_rail": {"same_as_top_rail": False, "section": "Pipe1-1/4STD"},
     "welds": {**OWN_WELD, "base_pattern": None, "post_to_baseplate": "1/4"}},
])
def test_check_4b_says_the_chord_limit_states_have_no_demand_for_each_of_the_four_pairs(tables):
    """S6-11, for every pair, mixed pairs included (S6-16 item 2): one
    line, no table. The base metal lines on both walls stay (S6-16 item 6)."""
    reg, _, chk, lines = _line_4b(**tables)
    line = next(ln for ln in lines if ln.kind == "decision" and ln.symbol == '"Post wall, chord limit states"')
    assert line.text == "No demand" and line.note == reg.get("ej.weld.check4b.no_chord_demand").value
    assert getattr(chk, "chord", None) is None  # the chord check is Check 3's alone (S6-10)
    assert {"R_n_BM_post", "R_n_BM_int"} <= {ln.key for ln in lines}
    assert chk.base_governs in ("post wall", "intermediate rail wall")


def test_a_rectangular_same_as_top_intermediate_rail_runs_check_4b_in_full():
    """S6-14 item 5: the observation is for a round post with a round rail
    only. Check 4a keeps its own observation."""
    reg = Registry()
    square = {"section": "HSS2X2X1/8", "long_side": None}
    res = engine.run(project.from_dict(_raw(top_rail=square, post=square, intermediate_rail={})), reg)
    chk = res.check("4b")
    assert not chk.observation and chk.computed and chk.controlling is not None
    first = chk.controlling.lines[0]
    assert first.text == "Computed in full" and first.note == reg.get("ej.weld.intermediate.rect_full").value
    assert res.check("4a").result == "Controlled by Checks 1 and 2"


# ---------------------------------------------------------------------------
# The width rule (S6-9) and the baseplate (S6-14 item 8)
# ---------------------------------------------------------------------------

def test_a_post_as_wide_as_the_rail_is_allowed_and_a_wider_one_stops():
    assert _run().check(3).computed                                   # 2 in post on a 2 in rail
    message = _stops(Stop.SECTION_POST_WIDER_THAN_RAIL, post={"long_side": "perpendicular to rail"})
    assert message.startswith("The post (HSS3X2X1/8, 3.000 in perpendicular to the rail) is wider than the top rail "
                              "(HSS4X2X1/8, 2.000 in wide).")


def test_the_width_rule_is_exact_where_either_member_is_rectangular():
    """S6-9: the 0.01 in tolerance of S5-4 is for two round members only.
    A 2.375 in pipe post on a 2 in rail stops; a 2 in square post under a
    1.9 in pipe rail stops; under a 2.375 in pipe rail it runs."""
    _stops(Stop.SECTION_POST_WIDER_THAN_RAIL, post=PIPE_POST, welds={"base_pattern": None})
    _stops(Stop.SECTION_POST_WIDER_THAN_RAIL, top_rail={"section": "Pipe1-1/2STD", "long_side": None}, post=SQUARE)
    assert _run(top_rail=PIPE_RAIL, post=SQUARE).check(3).computed


def test_the_intermediate_rail_may_not_be_wider_than_the_post_face_it_lands_on():
    wide = {"same_as_top_rail": False, "section": "HSS3X2X1/8", "long_side": "horizontal"}    # 3 in wide
    message = _stops(Stop.SECTION_INTERMEDIATE_WIDER_THAN_POST, intermediate_rail=wide, welds=OWN_WELD)
    assert message.startswith("The intermediate rail (HSS3X2X1/8, 3.000 in wide) is wider than the post "
                              "(HSS3X2X1/8, 2.000 in perpendicular to the rail).")
    on_edge = {**wide, "long_side": "vertical"}                                                # 2 in wide
    assert _run(intermediate_rail=on_edge, welds=OWN_WELD).check("4b").computed
    # Same as the top rail, it is the rail's width that must fit: here 2 in on a 2 in post face.
    assert _run(intermediate_rail={}).check("4b").computed


def test_the_baseplate_must_cover_a_rectangular_post_in_each_direction():
    """B is parallel to the rail and N perpendicular to it (S4-6): the post
    is 3 in along the rail and 2 in across it."""
    message = _stops(Stop.BASEPLATE_SMALLER_THAN_POST, baseplate={"B": 2.5, "N": 8})
    assert message == ("[baseplate] B = 2.5 (parallel to the rail) is smaller than the post dimension parallel to "
                       "the rail (HSS3X2X1/8, 3.000 in). Check the inputs.")
    assert _run(baseplate={"B": 3, "N": 2}).check(7).computed
    message = _stops(Stop.BASEPLATE_SMALLER_THAN_POST, baseplate={"B": 6, "N": 1.5})
    assert "N = 1.5 (perpendicular to the rail) is smaller than the post dimension perpendicular to the rail" in message


# ---------------------------------------------------------------------------
# The chord's own Chapter K limits (S6-13)
# ---------------------------------------------------------------------------

def test_a_rectangular_rail_over_the_wall_limit_stops_on_either_wall():
    message = _stops(Stop.SECTION_CHORD_WALL_OVER_LIMIT, top_rail={"section": "HSS5X2X1/8"})
    assert message.startswith("top rail HSS5X2X1/8: H/t = 43.10 > 35")
    flat = {"section": "HSS5X2X1/8", "long_side": "horizontal"}
    assert "H/t = 43.10 > 35" in _stops(Stop.SECTION_CHORD_WALL_OVER_LIMIT, top_rail=flat)
    assert _run().check(3).computed            # HSS4X2X1/8: H/t = 34.5, inside the limit


def _with_stress(entry: str, value: float, **tables):
    reg = Registry()
    e = reg.entries[entry]
    reg.entries[e.id] = dataclasses.replace(e, value=value)
    return engine.run(project.from_dict(_raw(**tables)), reg)


def test_the_chords_material_limits_apply_where_its_wall_is_a_stated_assumption():
    """Fy over 52 ksi and Fy/Fu over 0.8 stop, for the top rail, at a
    rectangular chord and at a mixed pair. No offered grade is outside the
    limits on the drafted values, so each is reached with a stand-in value."""
    other = {"grade": "A500 Gr C"}       # the post on another grade, so the stand-in touches the rail alone
    with pytest.raises(ProjectError) as stopped:
        _with_stress("material.A500_GrB.hss_rect.Fy", 55, post=other)
    assert stopped.value.stop is Stop.JOINT_CHECK3_FY_OVER_LIMIT
    assert str(stopped.value).startswith("top rail HSS4X2X1/8, A500 Gr B: Fy = 55.00 ksi > 52.00 ksi")
    with pytest.raises(ProjectError) as stopped:
        _with_stress("material.A500_GrB.hss_rect.Fu", 50, post=other)
    assert stopped.value.stop is Stop.JOINT_CHECK3_FY_FU_OVER_LIMIT
    assert "Fy/Fu = 0.9200 > 0.8" in str(stopped.value)
    # A mixed pair: a pipe rail over a square post, the rail's A53 Fu lowered to 40 (35/40 = 0.875).
    with pytest.raises(ProjectError) as stopped:
        _with_stress("material.A53_GrB.Fu", 40, top_rail=PIPE_RAIL, post=SQUARE)
    assert stopped.value.stop is Stop.JOINT_CHECK3_FY_FU_OVER_LIMIT


def test_a500_gr_c_is_the_named_exception_to_the_ductility_limit():
    """S6-13: 50/62 = 0.81 is over 0.8 and passes, by the tables' note."""
    reg = Registry()
    res = engine.run(project.from_dict(_raw(top_rail={"grade": "A500 Gr C"})), reg)
    assert res.check(3).computed
    assert "aisc360.K1.3.A500_GrC_note" in {e.id for e in reg.used}
    plain = Registry()
    engine.run(project.from_dict(_raw()), plain)
    assert "aisc360.K1.3.A500_GrC_note" not in {e.id for e in plain.used}    # read only when a ratio is over


def test_the_branch_is_not_held_to_the_chords_limits_at_a_rectangular_or_mixed_joint():
    """S6-13: the chord's own limits only. A post grade over the ductility
    limit runs (A500 Gr C aside, with a stand-in Fu on the post's grade
    that keeps the Fu/Fy guard), and Table K4.2A's aspect limit is not
    applied: HSS4X2 is H/B = 2, and a 3 x 1 rail would be outside it."""
    rail_c = {"grade": "A500 Gr C"}       # the rail on Gr C, so the stand-in below touches the post alone
    assert _with_stress("material.A500_GrB.hss_rect.Fy", 48.3, top_rail=rail_c).check(3).computed   # 48.3/58 = 0.83
    narrow = {"section": "HSS3X1X1/8", "long_side": "horizontal"}             # H/B = 3: outside 0.5 to 2.0
    assert _run(top_rail=narrow, post={"section": "Pipe2STD", "long_side": None},
                welds={"base_pattern": None, "post_to_baseplate": "1/4"}).check(3).computed
