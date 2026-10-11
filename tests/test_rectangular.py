"""Hollow rectangular members: orientation, grades and the section they
resolve to (docs/brief/inputs.md, S6-2 and S6-5; docs/plans/slice-6.md, T5).

Machinery tests, same-author: they hold the code to the brief's rules.
They are not test cases, and no value here is a hand or independent value.
Fy and Fu are compared with the registry entry the lookup should read,
never with a typed number.
"""

import dataclasses

import pytest

from handrail import materials, members, project, properties, shapes
from handrail.errors import SectionStop
from handrail.project import ProjectError
from handrail.registry import Registry
from handrail.shapes import RECT_HSS, RECT_TUBE
from handrail.stops import Stop
from handrail.units import Q_


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
