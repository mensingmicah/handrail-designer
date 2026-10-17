"""Hollow rectangular members: orientation, grades, AISC 360-22 F7 with Cb,
and the axis each check reads (docs/brief/inputs.md, S6-2 and S6-5;
docs/brief/checks.md, S6-4 and S6-14; docs/plans/slice-6.md, T5).

Machinery tests, same-author: they hold the code to the brief's rules.
They are not test cases, and no value here is a hand or independent value.
Fy and Fu are compared with the registry entry the lookup should read,
never with a typed number.
"""

import dataclasses
import math

import pytest

from handrail import cb, flexure, materials, members, orientation, project, properties, report, shapes
from handrail.calc import Sheet, Sym
from handrail.errors import SectionStop
from handrail.intermediate import check_4a
from handrail.loading import build_loading
from handrail.post import check_5, check_6, compression_capacity
from handrail.project import ProjectError
from handrail.rail import BiaxialCase, check_1, check_2
from handrail.registry import Registry
from handrail.shapes import RECT_HSS, RECT_TUBE
from handrail.stops import Stop
from handrail.units import Q_
import stand_ins


def _raw(**tables) -> dict:
    """An all-rectangular guard: an HSS4X2X1/8 rail on edge over an
    HSS3X2X1/8 post, 6'-0", no intermediate rail, no grade entered. Each
    keyword replaces or extends one table; a key given as None is removed."""
    raw = {
        "project": {"name": "rectangular"},
        "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
        "top_rail": {"section": "HSS4X2X1/8", "long_side": "vertical"},
        "post": {"section": "HSS3X2X1/8", "long_side": "parallel to rail"},
        "welds": {"rail_to_post": "1/8", "post_to_baseplate": "3/16"},
        "baseplate": {"B": 6, "N": 8}, "intermediate_rail": {"none": True},
    }
    for name, table in tables.items():
        merged = table if name == "intermediate_rail" else {**raw.get(name, {}), **table}
        raw[name] = {key: value for key, value in merged.items() if value is not None}
    return raw


def _members(**tables) -> members.Members:
    return members.resolve(project.from_dict(_raw(**tables)), Registry())


OWN_WELD = {"intermediate_rail_to_post": "1/8"}


def _stops(stop: Stop, **tables) -> str:
    with pytest.raises(ProjectError) as stopped:
        _members(**tables)
    assert stopped.value.stop is stop, str(stopped.value)
    return str(stopped.value)


# -- orientation (S6-2) -------------------------------------------------------

def test_a_rectangular_member_that_is_not_square_keeps_the_orientation_entered():
    m = _members(intermediate_rail={"same_as_top_rail": False, "section": "HSS2X1X1/8", "long_side": "horizontal"},
                 welds=OWN_WELD)
    assert m.project.top_rail.long_side == "vertical"
    assert m.project.post.long_side == "parallel to rail"
    own = m.project.intermediate_rail.member
    assert own is not None and own.long_side == "horizontal"
    assert (m.rail.family, m.post.family) == (RECT_HSS, RECT_HSS)


@pytest.mark.parametrize("table, section, words", [
    ("top_rail", "HSS4X2X1/8", '"vertical" or "horizontal"'),
    ("post", "HSS3X2X1/8", '"perpendicular to rail" or "parallel to rail"'),
])
def test_a_forgotten_orientation_stops_and_names_the_two_words(table, section, words):
    message = _stops(Stop.MEMBER_LONG_SIDE_MISSING, **{table: {"section": section, "long_side": None}})
    assert message.startswith(f"[{table}] is missing 'long_side': {section} is not square")
    assert message.endswith(f"Give long_side = {words}.")


def test_an_intermediate_rail_of_its_own_section_needs_its_own_orientation():
    message = _stops(Stop.MEMBER_LONG_SIDE_MISSING,
                     intermediate_rail={"same_as_top_rail": False, "section": "HSS2X1X1/8"}, welds=OWN_WELD)
    assert message.startswith("[intermediate_rail] is missing 'long_side': HSS2X1X1/8 is not square")


@pytest.mark.parametrize("table, section, what, long_side", [
    ("top_rail", "HSS2X2X1/8", "square", "vertical"),
    ("post", "HSS2X2X1/8", "square", "parallel to rail"),
    ("top_rail", "Pipe2STD", "round", "horizontal"),
    ("post", "HSS2.375X0.125", "round", "perpendicular to rail"),
])
def test_an_orientation_on_a_square_or_a_round_member_stops_as_a_conflicting_input(table, section, what, long_side):
    message = _stops(Stop.MEMBER_LONG_SIDE_NOT_APPLICABLE, **{table: {"section": section, "long_side": long_side}})
    assert f"{section} is a {what} section and has no long side" in message


def test_a_square_member_needs_no_orientation():
    m = _members(top_rail={"section": "HSS2X2X1/8", "long_side": None},
                 post={"section": "HSS2X2X1/8", "long_side": None})
    assert m.project.top_rail.long_side == "" and m.rail.rect.square


@pytest.mark.parametrize("table, word", [
    ("top_rail", "parallel to rail"),        # a post's word on a rail
    ("post", "vertical"),                    # a rail's word on a post
    ("top_rail", "Vertical"),
    ("post", "perpendicular"),
])
def test_an_orientation_takes_only_its_members_two_words(table, word):
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(**{table: {"long_side": word}}))
    assert stopped.value.stop is Stop.MEMBER_LONG_SIDE_INVALID
    assert f"[{table}] long_side {word!r}: give" in str(stopped.value)


def test_an_orientation_must_be_quoted_text():
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(top_rail={"long_side": True}))
    assert stopped.value.stop is Stop.FILE_NOT_TEXT


def test_the_same_as_top_intermediate_rail_takes_no_orientation_of_its_own():
    """Same as the top rail, it takes the top rail's section, grade and
    orientation (S6-14 item 5); one of its own is a conflicting input."""
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(intermediate_rail={"long_side": "vertical"}))
    assert stopped.value.stop is Stop.INTERMEDIATE_SAME_WITH_INPUTS
    assert "[intermediate_rail] long_side is given" in str(stopped.value)
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(intermediate_rail={"none": True, "long_side": "vertical"}))
    assert stopped.value.stop is Stop.INTERMEDIATE_NONE_WITH_INPUTS


# -- grades (S6-5) --------------------------------------------------------------

RECT_GRADES = ["A500 Gr B", "A500 Gr C", "A501 Gr A", "A501 Gr B", "A618 Gr Ia", "A618 Gr Ib", "A618 Gr II",
               "A618 Gr III", "A847", "A1085 Gr A"]


def test_the_rectangular_grades_are_the_table_2_4_list_and_no_other():
    assert materials.supported(RECT_HSS) == RECT_GRADES == materials.supported(RECT_TUBE)
    assert Registry().get(materials.STANDARD_GRADES[RECT_HSS]).value == RECT_GRADES
    assert RECT_TUBE not in materials.STANDARD_GRADES  # a custom tube takes every grade it accepts


def test_a_rectangular_grade_left_out_defaults_to_a500_gr_b():
    m = _members()
    assert (m.project.top_rail.grade, m.project.top_rail.grade_defaulted) == ("A500 Gr B", True)
    assert (m.project.post.grade, m.project.post.grade_defaulted) == ("A500 Gr B", True)
    assert materials.DEFAULT_GRADE[RECT_HSS] == materials.DEFAULT_GRADE[RECT_TUBE] == "A500 Gr B"


@pytest.mark.parametrize("grade, key", [
    ("A500 Gr B", "A500_GrB"), ("A500 Gr C", "A500_GrC"), ("A501 Gr A", "A501_GrA"),
    ("A501 Gr B", "A501_GrB"), ("A847", "A847"), ("A1085 Gr A", "A1085_GrA"),
])
def test_each_plain_rectangular_grade_reads_its_own_rectangular_entries(grade, key):
    reg, sec = Registry(), shapes.section("HSS2X2X1/8")
    Fy, Fu = materials.yield_stress(reg, grade, sec), materials.tensile_strength(reg, grade, sec)
    assert (Fy.entry, Fu.entry) == (f"material.{key}.hss_rect.Fy", f"material.{key}.hss_rect.Fu")
    assert Fy.quantity(reg) == reg.get(Fy.entry).quantity and Fu.quantity(reg) == reg.get(Fu.entry).quantity
    assert (Fy.note, Fu.note) == (f"Yield stress, {grade}", f"Tensile strength, {grade}")


@pytest.mark.parametrize("grade", ["A618 Gr Ia", "A618 Gr Ib", "A618 Gr II"])
def test_rectangular_a618_reads_the_round_shapes_entries_by_nominal_wall(grade):
    """S6-5 reuses slice 5's entries and lookup (S5-7): a wall of exactly
    3/4 in takes the thin range, one just over it the thick range, and one
    over 1-1/2 in stops."""
    reg = Registry()
    base = shapes.section("HSS8X8X5/8")
    round_entry = materials.yield_stress(reg, grade, shapes.section("HSS10.000X0.625")).entry
    for t_nom, wall_range in ((0.75, materials.THIN), (0.7501, materials.THICK), (1.5, materials.THICK)):
        Fy = materials.yield_stress(reg, grade, dataclasses.replace(base, tnom=Q_(t_nom, "inch")))
        assert (Fy.entry, Fy.range) == (round_entry, wall_range)
    with pytest.raises(SectionStop) as stopped:
        materials.yield_stress(reg, grade, dataclasses.replace(base, tnom=Q_(1.6, "inch")), "Post")
    assert stopped.value.stop is Stop.GRADE_WALL_OVER_LIMIT


@pytest.mark.parametrize("grade", ["A53 Gr B", "A1065 Gr 50", "A36"])
def test_a_grade_that_is_not_a_rectangular_hss_grade_is_refused_naming_the_ones_that_are(grade):
    """A53 is a pipe specification and A1065 is not offered in v1 (S6-5)."""
    with pytest.raises(SectionStop) as stopped:
        materials.yield_stress(Registry(), grade, shapes.section("HSS2X2X1/8"), "post")
    assert stopped.value.stop is Stop.GRADE_UNSUPPORTED
    assert str(stopped.value) == (f"post grade {grade!r}: for rectangular HSS this version supports "
                                  f"{', '.join(RECT_GRADES)} only")


def test_every_drafted_rectangular_grade_keeps_the_post_wall_guard_and_the_chapter_k_limits():
    """S6-14 item 4 and S6-13, on the drafted values: Fu/Fy is at least 1.20
    for every grade, the lowest being A500 Gr C; Fy is 52 ksi or less; and
    Fy/Fu is 0.8 or less except for A500 Gr C, the tables' named exception."""
    reg, thin = Registry(), shapes.section("HSS2X2X1/8")
    ratios = {}
    for grade in RECT_GRADES:
        Fy = materials.yield_stress(reg, grade, thin).quantity(reg)
        Fu = materials.tensile_strength(reg, grade, thin).quantity(reg)
        assert Fy <= Q_(52, "ksi"), grade
        ratios[grade] = (Fu / Fy).m_as("dimensionless")
    assert min(ratios, key=ratios.__getitem__) == "A500 Gr C" and min(ratios.values()) >= 1.20
    assert [g for g, r in ratios.items() if 1 / r > 0.8] == ["A500 Gr C"]


def test_no_rectangular_grade_is_an_unusual_pairing_and_a1085_prints_its_note():
    """Every grade a rectangular HSS accepts is on its Table 2-4 list, so
    the unusual-pairing warning never prints for one (S5-5); a database
    section in A1085 prints the published-properties note (S5-6)."""
    reg, sec = Registry(), shapes.section("HSS2X2X1/8")
    for grade in RECT_GRADES:
        notes = properties.grade_notes(reg, sec, grade)
        assert not any(n.startswith("UNUSUAL PAIRING") for n in notes), grade
        assert (notes == [reg.get(properties.A1085_NOTE).value]) == (grade == "A1085 Gr A"), grade


def test_a_rectangular_intermediate_rail_takes_the_top_rails_grade_when_it_is_on_its_own_list():
    """S5-10, carried to rectangular shapes by S6-5."""
    own = {"same_as_top_rail": False, "section": "HSS2X2X1/8"}
    m = _members(top_rail={"grade": "A500 Gr C"}, intermediate_rail=own, welds=OWN_WELD)
    assert m.project.intermediate_rail.member is not None
    assert m.project.intermediate_rail.member.grade == "A500 Gr C"
    # Under a pipe rail in A53 Gr B, which is not a rectangular HSS grade: its own shape's default.
    m = _members(top_rail={"section": "Pipe2STD", "long_side": None, "grade": "A53 Gr B"},
                 intermediate_rail=own, welds=OWN_WELD)
    assert m.project.intermediate_rail.member is not None
    assert m.project.intermediate_rail.member.grade == "A500 Gr B"


# ---------------------------------------------------------------------------
# Step 3: which axis each load bends, Cb, AISC 360-22 F7, and the checks
# ---------------------------------------------------------------------------

def _guard(**tables):
    """The members and loading of the all-rectangular guard, past validation
    (the joint tables stop a rectangular member until the welds step)."""
    reg = Registry()
    m = members.resolve(project.from_dict(_raw(**tables)), reg)
    return reg, m, build_loading(m.project, reg, m.rail, m.post, m.inter)


def _value(lines, key):
    values = [ln.value for ln in lines if ln.key == key and ln.kind == "value"]
    assert values, f"no calc line with key {key!r}"
    return values[0]


def _decisions(lines) -> list[str]:
    return [ln.text for ln in lines if ln.kind == "decision"]


def _case(chk, direction, second="Concentrated"):
    return next(c for c in chk.checked
                if c.direction == direction and (getattr(c, "limit_state", "") or c.load_type) == second)


OWN = {"same_as_top_rail": False, "section": "HSS2X1X1/8", "long_side": "vertical"}


# -- orientation (S6-2) ---------------------------------------------------------

def test_a_rails_long_side_sets_the_axis_each_load_bends_and_its_depth_and_width():
    sec = shapes.section("HSS4X2X1/8")
    on_edge, flat = orientation.rail_axes(sec, "vertical"), orientation.rail_axes(sec, "horizontal")
    assert (on_edge.vertical, on_edge.horizontal) == ("x", "y")
    assert (on_edge.depth.m_as("inch"), on_edge.width.m_as("inch")) == (4, 2)
    assert (flat.vertical, flat.horizontal) == ("y", "x")
    assert (flat.depth.m_as("inch"), flat.width.m_as("inch")) == (2, 4)


def test_a_posts_long_side_sets_the_axis_each_lateral_load_bends_and_its_plan_dimensions():
    sec = shapes.section("HSS3X2X1/8")
    across, along = orientation.post_axes(sec, "perpendicular to rail"), orientation.post_axes(sec, "parallel to rail")
    assert (across.transverse, across.longitudinal) == ("x", "y")
    assert (across.perpendicular.m_as("inch"), across.parallel.m_as("inch")) == (3, 2)
    assert (along.transverse, along.longitudinal) == ("y", "x")
    assert (along.perpendicular.m_as("inch"), along.parallel.m_as("inch")) == (2, 3)


def test_a_square_and_a_round_section_need_no_orientation():
    square, pipe = shapes.section("HSS2X2X1/8"), shapes.section("Pipe2STD")
    assert orientation.rail_axes(square, "") == orientation.RailAxes("x", "y", square.rect.H, square.rect.B)
    assert orientation.post_axes(square, "") == orientation.PostAxes("x", "y", square.rect.H, square.rect.B)
    assert orientation.rail_axes(pipe, "") == orientation.RailAxes("x", "x", pipe.OD, pipe.OD)
    assert orientation.post_axes(pipe, "") == orientation.PostAxes("x", "x", pipe.OD, pipe.OD)


def test_an_orientation_the_reader_would_have_refused_is_a_bug_not_a_default():
    with pytest.raises(ValueError, match="HSS4X2X1/8: long_side ''"):
        orientation.rail_axes(shapes.section("HSS4X2X1/8"), "")
    with pytest.raises(ValueError, match="long_side 'vertical'"):
        orientation.post_axes(shapes.section("HSS3X2X1/8"), "vertical")


def test_the_section_page_prints_both_axes_and_which_axis_each_load_bends():
    reg = Registry()
    lines = properties.section_lines(reg, shapes.section("HSS4X2X1/8"), long_side="vertical")
    keys = [ln.key for ln in lines if ln.kind == "value"]
    assert keys == ["H", "B", "t_nom", "t_des", "A", "W", "I_x", "S_x", "Z_x", "r_x", "I_y", "S_y", "Z_y", "r_y",
                    "J", "b_over_t", "h_over_t"]
    assert all(ln.cite == shapes.DB for ln in lines if ln.kind == "value")
    for long_side, entry in properties.ORIENTATION.items():
        sec = shapes.section("HSS3X2X1/8")
        last = properties.section_lines(reg, sec, long_side=long_side)[-1]
        assert last.kind == "decision" and last.text == reg.get(entry).value
        assert long_side.split()[0] in last.text.lower()
    square = properties.section_lines(reg, shapes.section("HSS2X2X1/8"))[-1]
    assert square.text == reg.get(properties.SQUARE).value


# -- Cb, Eq. F1-1 (S6-4) ------------------------------------------------------------

def _cb(loads, M_mid, span=72.0):
    sh = Sheet(Registry())
    L = Sym("L", Q_(span, "inch"))
    value = cb.simple_span(sh, L, Sym("M_r", Q_(M_mid, "lbf*inch")), loads)
    return value.value, sh.lines


W, P = Sym("w", Q_(5.0, "lbf/inch")), Sym("P", Q_(200.0, "lbf"))


def test_cb_of_a_uniform_load_and_of_a_midspan_point_load():
    """Closed form: with M_A = M_C = 3/4 M_max under a uniform load, Cb =
    12.5/11; with M_A = M_C = 1/2 M_max under a point load, Cb = 12.5/9.5."""
    uniform, _ = _cb([cb.SpanLoad(W, True)], 5.0 * 72**2 / 8)
    point, lines = _cb([cb.SpanLoad(P, False)], 200.0 * 72 / 4)
    assert uniform == pytest.approx(12.5 / 11, rel=1e-12)
    assert point == pytest.approx(12.5 / 9.5, rel=1e-12)
    assert _value(lines, "M_A").m_as("lbf*inch") == pytest.approx(200.0 * 18 / 2)
    assert _value(lines, "M_max") == _value(lines, "M_B")


def test_cb_of_a_uniform_and_a_point_load_together_lies_between_the_two():
    M_w, M_p = 5.0 * 72**2 / 8, 200.0 * 72 / 4
    both, lines = _cb([cb.SpanLoad(W, True), cb.SpanLoad(P, False)], M_w + M_p)
    M_A = 0.75 * M_w + 0.5 * M_p
    assert _value(lines, "M_A").m_as("lbf*inch") == pytest.approx(M_A)
    assert both == pytest.approx(12.5 * (M_w + M_p) / (2.5 * (M_w + M_p) + 6 * M_A + 4 * (M_w + M_p)))
    assert 12.5 / 11 < both < 12.5 / 9.5


def test_cb_with_the_guard_load_opposing_the_dead_load_and_no_reversal():
    """The upward case at guard loads: P far above w L, so the net moment
    keeps one sign and its maximum is at midspan."""
    light = Sym("w", Q_(0.3, "lbf/inch"))
    M_w, M_p = 0.3 * 72**2 / 8, 200.0 * 72 / 4
    value, lines = _cb([cb.SpanLoad(light, True), cb.SpanLoad(P, False, opposes=True)], M_p - M_w)
    M_A = 0.5 * M_p - 0.75 * M_w
    assert "The moment does not reverse: maximum at midspan" in _decisions(lines)
    assert _value(lines, "M_A").m_as("lbf*inch") == pytest.approx(M_A)
    assert value == pytest.approx(12.5 * (M_p - M_w) / (2.5 * (M_p - M_w) + 6 * M_A + 4 * (M_p - M_w)))


def test_cb_finds_the_opposite_peak_when_the_dead_load_outweighs_the_point_load():
    """P below w L: the diagram reverses between the support and midspan,
    and the larger of the two extremes is M_max. Here w = 5 lb/in over 72
    in against P = 200 lb: at midspan M = P L/4 - w L^2/8 = 360 lb-in the
    other way, and at x0 = L/2 - P/(2w) = 16 in the dead load's moment peaks
    at w x0 (L - x0)/2 - P x0/2 = 640 lb-in."""
    value, lines = _cb([cb.SpanLoad(W, True), cb.SpanLoad(P, False, opposes=True)], 360.0)
    assert "The moment reverses between the support and midspan" in _decisions(lines)
    assert _value(lines, "x_0").m_as("inch") == pytest.approx(16.0)
    assert _value(lines, "M_0").m_as("lbf*inch") == pytest.approx(640.0)
    assert _value(lines, "M_max").m_as("lbf*inch") == pytest.approx(640.0)
    M_A = abs(5.0 * 18 * 54 / 2 - 200.0 * 18 / 2)
    assert value == pytest.approx(12.5 * 640 / (2.5 * 640 + 6 * M_A + 4 * 360))


def test_cb_of_two_uniform_loads_opposed_is_that_of_one_uniform_load():
    lighter = Sym("w_D", Q_(1.0, "lbf/inch"))
    value, lines = _cb([cb.SpanLoad(lighter, True), cb.SpanLoad(W, True, opposes=True)], 4.0 * 72**2 / 8)
    assert value == pytest.approx(12.5 / 11, rel=1e-12)
    assert not any("reverse" in text for text in _decisions(lines))


def test_a_cantilevers_cb_is_the_registry_value():
    reg = Registry()
    sh = Sheet(reg)
    assert cb.cantilever(sh).value == reg.get(cb.CANTILEVER).value == 1.0
    assert sh.lines[0].cite == reg.get(cb.CANTILEVER).cite


# -- AISC 360-22 F7 about one axis (S6-4, S6-14 item 3) -----------------------------

def _capacity(sec, axis, Lb=72.0, grade="A500 Gr B", Cb=1.0):
    reg = Registry()
    sh, flags = Sheet(reg), []
    lim = flexure.rect_limits(sh, sec, grade)
    unbraced = flexure.Unbraced(Sym("L", Q_(Lb, "inch")), "Unbraced length", lambda s: s.input("C_b", "C_b", Cb, "Cb"))
    Mc = flexure.rect_axis_capacity(sh, lim, sec, axis, unbraced, flags)
    return Mc.value.m_as("lbf*inch"), sh.lines, flags, reg


def _kip_in(value: float) -> float:
    return value * 1000.0


def test_a_compact_section_about_its_minor_axis_is_the_plastic_moment_with_no_ltb():
    sec = shapes.section("HSS3X2X1/8")
    Mc, lines, flags, reg = _capacity(sec, "y")
    Fy = reg.get("material.A500_GrB.hss_rect.Fy").value
    assert Mc == pytest.approx(_kip_in(Fy * 0.803) / reg.get("aisc360.F1.omega_b").value)
    assert not flags
    assert _decisions(lines) == ["Compact flange: flange local buckling does not apply",
                                 "Compact web: web local buckling does not apply",
                                 "Lateral-torsional buckling does not apply"]
    assert [ln.symbol for ln in lines if ln.kind == "decision"][-1] == '"Bending about the minor axis"'


def test_a_square_section_has_no_ltb_about_either_axis():
    for axis in ("x", "y"):
        _, lines, _, _ = _capacity(shapes.section("HSS2X2X1/8"), axis, Lb=500.0)
        assert [ln.symbol for ln in lines if ln.kind == "decision"][-1] == '"Square section"'
        assert not any(ln.key == "L_p" for ln in lines)


def test_a_noncompact_flange_takes_eq_f7_2_and_is_flagged():
    """S6-14 item 3: a noncompact wall takes its reduced strength, not only a
    flag. HSS4X2X1/8 about y: the 4 in walls are the flanges, h/t = 31.5,
    between 1.12 and 1.40 sqrt(E/Fy)."""
    sec = shapes.section("HSS4X2X1/8")
    Mc, lines, flags, reg = _capacity(sec, "y")
    Fy, E = reg.get("material.A500_GrB.hss_rect.Fy").value, reg.get("material.steel.E").value
    lp, lr = 1.12 * (E / Fy) ** 0.5, 1.40 * (E / Fy) ** 0.5
    Mp, FyS = _kip_in(Fy * 1.02), _kip_in(Fy * 0.898)
    Mn = Mp - (Mp - FyS) * (31.5 - lp) / (lr - lp)
    assert lp < 31.5 < lr and Mn < Mp
    assert _value(lines, "M_n_FLB_y").m_as("lbf*inch") == pytest.approx(Mn)
    assert Mc == pytest.approx(Mn / 1.67)
    assert "NONCOMPACT FLANGE" in _decisions(lines)
    assert len(flags) == 1 and flags[0].startswith("NONCOMPACT: HSS4X2X1/8 flange, h/t = 31.5, exceeds lambda_p")
    assert "AISC 360-22 Eq. F7-2" in flags[0]
    # About x the same section's flanges are the 2 in walls: compact, no flag.
    assert _capacity(sec, "x", Lb=10.0)[2] == []


def test_a_noncompact_web_takes_eq_f7_6_and_is_flagged():
    """No database HSS has a noncompact web: a stand-in h/t of 100, between
    2.42 and 5.70 sqrt(E/Fy), on HSS4X2X1/8 about x."""
    sec = stand_ins.replace(shapes.section("HSS4X2X1/8"), h_t=100.0, label="FakeTube")
    Mc, lines, flags, reg = _capacity(sec, "x", Lb=10.0)
    Fy, E = reg.get("material.A500_GrB.hss_rect.Fy").value, reg.get("material.steel.E").value
    lp, lr = 2.42 * (E / Fy) ** 0.5, 5.70 * (E / Fy) ** 0.5
    Mp, FyS = _kip_in(Fy * 1.66), _kip_in(Fy * 1.32)
    Mn = Mp - (Mp - FyS) * (100.0 - lp) / (lr - lp)
    assert _value(lines, "M_n_WLB_x").m_as("lbf*inch") == pytest.approx(Mn)
    assert Mc == pytest.approx(Mn / 1.67)
    assert "NONCOMPACT WEB" in _decisions(lines) and "AISC 360-22 Eq. F7-6" in flags[0]


@pytest.mark.parametrize("changes, axis, part, name", [
    ({"b_t": 36.0}, "x", "flange", "b/t"),     # over 1.40 sqrt(E/Fy) = 35.15
    ({"h_t": 36.0}, "y", "flange", "h/t"),
    ({"h_t": 150.0}, "x", "web", "h/t"),       # over 5.70 sqrt(E/Fy) = 143.1
    ({"b_t": 150.0}, "y", "web", "b/t"),
])
def test_a_slender_flange_or_web_stops_naming_the_wall_its_ratio_and_the_limit(changes, axis, part, name):
    sec = stand_ins.replace(shapes.section("HSS4X2X1/8"), label="FakeTube", **changes)
    with pytest.raises(SectionStop) as stopped:
        _capacity(sec, axis)
    assert stopped.value.stop is Stop.SECTION_SLENDER_IN_FLEXURE
    ratio = next(iter(changes.values()))
    assert str(stopped.value).startswith(
        f"FakeTube: the {part} is slender in flexure about the {axis} axis, {name} = {ratio:g} > lambda_r = ")
    assert "The tool does not check slender sections." in str(stopped.value)


def _ltb_terms(reg, sec):
    """Lp and Lr from the published properties, in inches (AISC 360-22 Eqs. F7-10 and F7-11)."""
    Fy, E = reg.get("material.A500_GrB.hss_rect.Fy").value, reg.get("material.steel.E").value
    root = (sec.rect.J.m_as("in^4") * sec.A.m_as("in^2")) ** 0.5
    ry, Sx, Mp = sec.y.r.m_as("inch"), sec.x.S.m_as("in^3"), Fy * sec.x.Z.m_as("in^3")
    return Fy, E, root, ry, Sx, Mp, 0.13 * E * ry * root / Mp, 2 * E * ry * root / (0.7 * Fy * Sx)


def test_ltb_does_not_apply_within_lp():
    sec = shapes.section("HSS4X2X1/8")
    Mc, lines, _, reg = _capacity(sec, "x", Lb=60.0)
    _, _, _, _, _, Mp, Lp, _ = _ltb_terms(reg, sec)
    assert 60.0 < Lp and _value(lines, "L_p").m_as("inch") == pytest.approx(Lp)
    assert _decisions(lines)[-1] == "Lateral-torsional buckling does not apply"
    assert not any(ln.key in ("C_b", "L_r", "M_n_LTB") for ln in lines)   # Cb is not asked for
    assert Mc == pytest.approx(_kip_in(Mp) / 1.67)


def test_inelastic_ltb_takes_eq_f7_8_with_cb_and_is_capped_at_mp():
    sec = shapes.section("HSS4X2X1/8")
    Mc, lines, _, reg = _capacity(sec, "x", Lb=72.0, Cb=1.0)
    Fy, _, _, _, Sx, Mp, Lp, Lr = _ltb_terms(reg, sec)
    assert Lp < 72.0 < Lr and _value(lines, "L_r").m_as("inch") == pytest.approx(Lr)
    Mn = Mp - (Mp - 0.7 * Fy * Sx) * (72.0 - Lp) / (Lr - Lp)
    assert Mn < Mp
    assert _value(lines, "M_n_LTB").m_as("lbf*inch") == pytest.approx(_kip_in(Mn))
    assert Mc == pytest.approx(_kip_in(Mn) / 1.67)
    assert "Inelastic lateral-torsional buckling: Eq. F7-8" in _decisions(lines)
    # With the Cb of a uniform load the same equation gives more than Mp, and Mn is Mp (S6-4).
    Mc, lines, _, _ = _capacity(sec, "x", Lb=72.0, Cb=12.5 / 11)
    assert _value(lines, "M_n_LTB").m_as("lbf*inch") == pytest.approx(_kip_in(Mn) * 12.5 / 11)
    assert _value(lines, "M_n_x").m_as("lbf*inch") == pytest.approx(_kip_in(Mp))
    assert Mc == pytest.approx(_kip_in(Mp) / 1.67)


def test_elastic_ltb_takes_eq_f7_9_beyond_lr():
    """No guard member is this long: a stand-in unbraced length past Lr."""
    sec = shapes.section("HSS4X2X1/8")
    _, E, root, ry, _, Mp, _, Lr = _ltb_terms(Registry(), sec)
    Lb = Lr + 500.0
    Mc, lines, _, _ = _capacity(sec, "x", Lb=Lb, Cb=1.0)
    Mn = 2 * E * 1.0 * root / (Lb / ry)
    assert Mn < Mp
    assert _value(lines, "M_n_LTB").m_as("lbf*inch") == pytest.approx(_kip_in(Mn))
    assert Mc == pytest.approx(_kip_in(Mn) / 1.67)
    assert "Elastic lateral-torsional buckling: Eq. F7-9" in _decisions(lines)


def test_only_the_equations_a_section_reaches_are_read_from_the_registry():
    """The DRAFT list names the entries a calc used: a compact section about
    its minor axis reads neither a local buckling equation nor Cb."""
    _, _, _, reg = _capacity(shapes.section("HSS3X2X1/8"), "y")
    used = {e.id for e in reg.used}
    assert "aisc360.eq.F7-1" in used and "aisc360.F7.4.no_ltb_note" in used
    assert not used & {"aisc360.eq.F7-2", "aisc360.eq.F7-6", "aisc360.eq.F7-8", "aisc360.eq.F7-9",
                       "aisc360.eq.F7-10", "aisc360.eq.F1-1"}


# -- Check 1 and Check 2 on a rectangular rail (S6-4) -------------------------------

def test_a_rectangular_rail_combines_its_axes_by_h1_1_in_the_horizontal_cases():
    reg, m, loading = _guard()
    chk = check_1(reg, m.project, m.rail, loading)
    out = _case(chk, "Outward")
    assert isinstance(out, BiaxialCase) and (out.axis_v, out.axis_h) == ("x", "y")
    assert out.ratio == pytest.approx((out.M_v / out.Mc_v + out.M_h / out.Mc_h).m_as("dimensionless"))
    assert out.M_h.m_as("lbf*inch") == pytest.approx(200.0 * 72 / 4)
    assert out.M_v.m_as("lbf*inch") == pytest.approx(loading.w_D.m_as("lbf/inch") * 72**2 / 8)
    assert [ln.symbol for ln in out.lines if ln.kind == "heading"] == [
        "Demand: outward, concentrated load", "Section", "Capacity about the x axis (vertical load)",
        "Capacity about the y axis (horizontal load)", "Interaction"]
    assert out.lines[-1].cite == f"{reg.get('aisc360.eq.H1-1b').cite}; {reg.get('ej.bending.biaxial_rect').cite}"
    # Each axis on its own strength, combined by H1.1: the round sections' SRSS entry is not read.
    assert "each on its own axis" in out.combination
    assert out.combination.endswith(reg.get("ej.bending.biaxial_rect").cite)
    assert "ej.bending.srss_round" not in {e.id for e in reg.used}
    assert _case(chk, "Inward").ratio == out.ratio
    assert chk.controlling is out


def test_the_vertical_cases_of_a_rectangular_rail_bend_one_axis():
    reg, m, loading = _guard()
    chk = check_1(reg, m.project, m.rail, loading)
    M_D = loading.w_D.m_as("lbf/inch") * 72**2 / 8
    down, up = _case(chk, "Downward"), _case(chk, "Upward")
    assert (down.axis_v, down.axis_h, up.axis_h) == ("x", "", "")
    assert down.M_v.m_as("lbf*inch") == pytest.approx(M_D + 3600.0)
    assert up.M_v.m_as("lbf*inch") == pytest.approx(abs(0.6 * M_D - 3600.0))
    assert down.ratio == pytest.approx((down.M_v / down.Mc_v).m_as("dimensionless"))
    assert "Interaction" not in [ln.symbol for ln in down.lines if ln.kind == "heading"]


def test_each_axis_takes_cb_from_its_own_loads_in_the_case():
    """S6-4. The rail on edge is past Lp about x (Lb = 72 in), so each case
    prints Cb for the vertical axis: the dead load alone in the outward
    case, the dead load with the point load in the downward case, and the
    two opposed in the upward case."""
    reg, m, loading = _guard()
    chk = check_1(reg, m.project, m.rail, loading)
    M_D, M_L = loading.w_D.m_as("lbf/inch") * 72**2 / 8, 3600.0

    def eq_f1_1(M_max, M_A):
        return 12.5 * M_max / (2.5 * M_max + 6 * M_A + 4 * M_max)

    assert _value(_case(chk, "Outward").lines, "C_b") == pytest.approx(12.5 / 11)
    assert _value(_case(chk, "Downward").lines, "C_b") == pytest.approx(
        eq_f1_1(M_D + M_L, 0.75 * M_D + 0.5 * M_L))
    assert _value(_case(chk, "Upward").lines, "C_b") == pytest.approx(
        eq_f1_1(M_L - 0.6 * M_D, 0.5 * M_L - 0.6 * 0.75 * M_D))
    assert _value(_case(chk, "Downward", "Distributed").lines, "C_b") == pytest.approx(12.5 / 11)


def test_a_rail_with_its_long_side_horizontal_swaps_the_axes():
    reg, m, loading = _guard(top_rail={"long_side": "horizontal"})
    chk = check_1(reg, m.project, m.rail, loading)
    out, down = _case(chk, "Outward"), _case(chk, "Downward")
    assert (out.axis_v, out.axis_h, down.axis_v) == ("y", "x", "y")
    assert chk.controlling is down   # the vertical load is now on the weak axis, whose flange is noncompact
    assert len(chk.flags) == 1 and "about the y axis" in chk.flags[0]


def test_a_square_rail_is_biaxial_too_and_not_srss():
    reg, m, loading = _guard(top_rail={"section": "HSS2X2X1/8", "long_side": None})
    out = _case(check_1(reg, m.project, m.rail, loading), "Outward")
    assert isinstance(out, BiaxialCase) and (out.axis_v, out.axis_h) == ("x", "y")
    assert out.Mc_v == out.Mc_h
    assert out.ratio == pytest.approx(((out.M_v + out.M_h) / out.Mc_v).m_as("dimensionless"))


def test_check_2_deflects_about_the_axis_the_case_bends():
    reg, m, loading = _guard()
    chk = check_2(reg, m.project, m.rail, loading)
    for direction, I in (("Downward", m.rail.x.I), ("Upward", m.rail.x.I), ("Outward", m.rail.y.I),
                         ("Inward", m.rail.y.I)):
        assert _value(_case(chk, direction).lines, "I") == I, direction
    E = reg.get("material.steel.E").quantity
    out = _case(chk, "Outward")
    assert out.demand.m_as("inch") == pytest.approx((Q_(200, "lbf") * Q_(72, "inch")**3 / (48 * E * m.rail.y.I)).m_as("inch"))


def test_a_round_rail_is_unchanged_by_the_rectangular_path():
    reg, m, loading = _guard(top_rail={"section": "Pipe2STD", "long_side": None})
    chk = check_1(reg, m.project, m.rail, loading)
    assert not any(isinstance(c, BiaxialCase) for c in chk.cases)
    assert "SRSS" in _case(chk, "Outward").combination


# -- Check 4a on a rectangular intermediate rail (S6-16 item 3) ------------------------

def test_check_4a_bends_the_axis_each_direction_of_the_component_load_loads():
    reg, m, loading = _guard(intermediate_rail=OWN, welds=OWN_WELD)
    chk = check_4a(reg, m.project, m.inter, loading)
    down, across = _case(chk, "Downward", "Bending"), _case(chk, "Horizontal", "Bending")
    M_L = 50.0 * 72 / 4
    M_D = loading.w_D_int.m_as("lbf/inch") * 72**2 / 8
    assert _value(down.lines, "M_r_x").m_as("lbf*inch") == pytest.approx(M_D + M_L)
    assert _value(across.lines, "M_r_y").m_as("lbf*inch") == pytest.approx(M_L)
    # HSS2X1X1/8 on edge is past Lp (about 33 in): Cb from the point load with the dead load.
    M_A = 0.75 * M_D + 0.5 * M_L
    assert _value(down.lines, "C_b") == pytest.approx(12.5 * (M_D + M_L) / (6.5 * (M_D + M_L) + 6 * M_A))
    assert not any(ln.key == "C_b" for ln in across.lines)   # the minor axis has no LTB
    assert _value(_case(chk, "Downward", "Deflection").lines, "I_int") == m.inter.x.I
    assert _value(_case(chk, "Horizontal", "Deflection").lines, "I_int") == m.inter.y.I


def test_check_4a_on_a_flat_intermediate_rail_takes_cb_from_the_point_load_alone():
    reg, m, loading = _guard(intermediate_rail={**OWN, "long_side": "horizontal"}, welds=OWN_WELD)
    chk = check_4a(reg, m.project, m.inter, loading)
    across = _case(chk, "Horizontal", "Bending")
    assert _value(across.lines, "M_r_x").m_as("lbf*inch") == pytest.approx(50.0 * 72 / 4)
    assert _value(across.lines, "C_b") == pytest.approx(12.5 / 9.5)
    assert not any(ln.key == "C_b" for ln in _case(chk, "Downward", "Bending").lines)


def test_the_same_as_top_observation_is_kept_for_a_rectangular_rail():
    """S6-14 item 5: the intermediate rail takes the top rail's section,
    grade and orientation, and Checks 1 and 2 cover it."""
    reg, m, loading = _guard(intermediate_rail={})
    chk = check_4a(reg, m.project, m.inter, loading)
    assert chk.result == "Controlled by Checks 1 and 2" and not chk.cases


# -- Checks 5 and 6 on a rectangular post (S6-14 item 2) ------------------------------

def test_each_lateral_case_of_a_rectangular_post_bends_one_axis():
    reg, m, loading = _guard()   # the post's long side is parallel to the rail
    chk = check_5(reg, m.project, m.post, loading)
    out, along = _case(chk, "Outward"), _case(chk, "Longitudinal")
    assert (out.axis, _case(chk, "Inward").axis, along.axis, _case(chk, "Downward").axis) == ("y", "y", "x", "")
    assert _value(out.lines, "M_c_y") == out.M_allow and _value(along.lines, "M_c_x") == along.M_allow
    assert out.M_allow < along.M_allow and out.Mr == along.Mr
    assert _value(out.lines, "I") == m.post.y.I and _value(along.lines, "I") == m.post.x.I
    E, Lc = reg.get("material.steel.E").quantity, _value(out.lines, "L_c")
    assert out.second_order == pytest.approx((1.6 * out.Pr * Lc**2 / (math.pi**2 * E * m.post.y.I)).m_as("dimensionless"))
    orthogonal = max((c for c in chk.checked if c.direction != "Skew"), key=lambda c: c.ratio)
    assert orthogonal.direction == "Outward" and orthogonal.load_type == "Distributed"
    perpendicular = _guard(post={"long_side": "perpendicular to rail"})
    chk = check_5(perpendicular[0], perpendicular[1].project, perpendicular[1].post, perpendicular[2])
    assert (_case(chk, "Outward").axis, _case(chk, "Longitudinal").axis) == ("x", "y")
    # The load along the rail is now on the weak axis; the skew case (S6-18) governs over all.
    assert max((c for c in chk.checked if c.direction != "Skew"), key=lambda c: c.ratio).direction == "Longitudinal"
    assert chk.controlling.direction == "Skew"


@pytest.mark.parametrize("post", [{}, {"long_side": "perpendicular to rail"},
                                  {"section": "HSS2X2X1/8", "long_side": None}])
def test_the_skew_case_of_a_rectangular_post_is_at_the_worst_plan_angle(post):
    """S6-18 item 3: Mr,t = Mr cos theta, Mr,l = Mr sin theta; Eq. H1-1 is
    linear in the two, so tan theta = Mc,t/Mc,l and the moment term is
    Mr sqrt(1/Mc,t^2 + 1/Mc,l^2); sqrt(2) Mr/Mc for a square post. No
    alpha Pr/Pe of its own (item 4)."""
    reg, m, loading = _guard(post=post)
    chk = check_5(reg, m.project, m.post, loading)
    for lt in ("Concentrated", "Distributed"):
        skew, out, along = _case(chk, "Skew", lt), _case(chk, "Outward", lt), _case(chk, "Longitudinal", lt)
        Mct, Mcl, Mr = out.M_allow, along.M_allow, skew.Mr
        assert skew.Mr == out.Mr and skew.Pr == out.Pr and skew.second_order is None
        assert skew.plan_angle.m_as("degree") == pytest.approx(math.degrees(math.atan((Mct / Mcl).m_as(""))))
        term = (Mr * ((1 / Mct**2 + 1 / Mcl**2) ** 0.5)).m_as("")
        assert skew.equation == "Eq. H1-1b"
        assert skew.ratio == pytest.approx((skew.Pr / (2 * skew.P_allow)).m_as("") + term)
        assert skew.ratio > max(out.ratio, along.ratio)
        assert skew.Mc_by == {out.axis: Mct, along.axis: Mcl}
        if m.post.rect.square:
            assert term == pytest.approx(math.sqrt(2) * (Mr / Mct).m_as(""))
            assert skew.plan_angle.m_as("degree") == pytest.approx(45.0)
        assert _decisions(skew.lines)[-3:-1] == ["At the plan angle worst for this check",
                                                 "Not computed for the skew case"]


def test_check_6_has_no_skew_case_and_says_why():
    """S6-18 item 4: the skew deflection never exceeds the larger
    orthogonal case, so Check 6 lists the skew case as not checked; a round
    post has no skew row."""
    reg, m, loading = _guard()
    chk = check_6(reg, m.project, m.post, loading)
    skew = [c for c in chk.cases if c.direction == "Skew"]
    assert len(skew) == 1 and skew[0].status == "not checked"
    assert skew[0].remark == reg.get("ej.skew.deflection").value
    reg, m, loading = _guard(top_rail={"section": "Pipe2STD", "long_side": None},
                             post={"section": "Pipe2STD", "long_side": None})
    assert all(c.direction != "Skew" for c in check_6(reg, m.project, m.post, loading).cases)
    assert all(c.direction != "Skew" for c in check_5(reg, m.project, m.post, loading).cases)


def test_a_rectangular_post_buckles_about_its_weak_axis_in_every_case():
    reg, m, loading = _guard()
    chk = check_5(reg, m.project, m.post, loading)
    for direction in ("Downward", "Outward", "Longitudinal"):
        lines = _case(chk, direction).lines
        assert _value(lines, "r") == m.post.y.r, direction
        assert _value(lines, "L_c_over_r") == pytest.approx(2.1 * 42 / m.post.y.r.m_as("inch"))
    down = _case(chk, "Downward").lines
    assert [ln.key for ln in down if ln.key.startswith("lambda_")] == ["lambda_r_c", "lambda_b", "lambda_h"]
    assert _decisions(down)[:2] == ["Nonslender", "Nonslender"]


def test_the_posts_flexure_takes_cb_of_1_and_lb_of_h():
    """S6-4. HSS2X1X3/16 with its long side perpendicular to the rail is
    past Lp at h = 42 in, so the transverse cases print Eq. F7-8 with the
    cantilever's Cb."""
    reg, m, loading = _guard(post={"section": "HSS2X1X3/16", "long_side": "perpendicular to rail"})
    out = _case(check_5(reg, m.project, m.post, loading), "Outward")
    assert out.axis == "x"
    assert _value(out.lines, "L_b").m_as("inch") == 42 and _value(out.lines, "C_b") == 1.0
    assert _value(out.lines, "M_n_LTB") < _value(out.lines, "M_p_x")
    assert _value(out.lines, "M_n_x") == _value(out.lines, "M_n_LTB")


@pytest.mark.parametrize("changes, wall, name", [({"b_t": 36.0}, "2.000 in", "b/t"), ({"h_t": 36.0}, "3.000 in", "h/t")])
def test_a_slender_wall_of_a_rectangular_post_stops_in_compression(changes, wall, name):
    reg, m, _ = _guard()
    post = stand_ins.replace(m.post, label="FakeTube", **changes)
    with pytest.raises(SectionStop) as stopped:
        compression_capacity(reg, m.project, post)
    assert stopped.value.stop is Stop.SECTION_SLENDER_IN_COMPRESSION
    assert str(stopped.value).startswith(f"FakeTube: the {wall} wall is slender in compression, {name} = 36 > lambda_r = ")


def test_check_6_deflects_about_the_axis_the_case_bends():
    reg, m, loading = _guard()
    chk = check_6(reg, m.project, m.post, loading)
    assert _value(_case(chk, "Outward").lines, "I") == m.post.y.I
    assert _value(_case(chk, "Longitudinal").lines, "I") == m.post.x.I
    assert _case(chk, "Outward").demand > _case(chk, "Longitudinal").demand
    assert chk.controlling.direction == "Outward"


def test_a_square_post_is_the_same_in_every_lateral_case():
    reg, m, loading = _guard(post={"section": "HSS2X2X1/8", "long_side": None})
    chk = check_5(reg, m.project, m.post, loading)
    out, along = _case(chk, "Outward"), _case(chk, "Longitudinal")
    assert (out.axis, along.axis) == ("x", "y") and out.ratio == along.ratio
    assert [ln.key for ln in _case(chk, "Downward").lines if ln.key.startswith("lambda_")] == ["lambda_r_c", "lambda_b"]


# -- the printed envelope and summary of a rectangular rail ------------------------------

def test_the_envelope_and_summary_of_a_rectangular_rail_print_both_axes():
    reg, m, loading = _guard()
    chk = check_1(reg, m.project, m.rail, loading)
    table = report._envelope_biaxial(chk)
    assert "Vertical load" in table and "Horizontal load" in table
    assert "Mrx = 256.5 lb-in\\nMcx = " in table and "Mry = 3,600 lb-in\\nMcy = " in table
    demand, capacity = report._demand_capacity(chk.controlling)
    assert demand == "Mrx = 256.5 lb-in; Mry = 3,600 lb-in"
    assert capacity.startswith("Mcx = ") and "; Mcy = " in capacity
    down = report._demand_capacity(_case(chk, "Downward"))
    assert down[0].startswith("Mrx = ") and ";" not in down[0]
