"""Grades by shape: Fy and Fu by grade, shape and wall, and the default
grades (docs/brief/inputs.md, S5-5, S5-7, S5-10).

Machinery tests, same-author (docs/plans/slice-5.md, T4): they hold the
lookup to the brief's rules. They are not test cases, and no value here is
a hand or independent value. Fy and Fu are compared with the registry
entry the lookup should read, never with a typed number.
"""

import dataclasses

import pytest

from handrail import engine, materials, members, project, properties, report, shapes
from handrail.calc import Sheet
from handrail.errors import SectionStop
from handrail.project import ProjectError
from handrail.registry import Registry
from handrail.shapes import PIPE, ROUND_HSS, ROUND_TUBE
from handrail.stops import Stop
from handrail.units import Q_
from test_report import CLEAN


def _raw(**tables) -> dict:
    """A project that runs: Pipe2STD rail and post over 6'-0", no intermediate rail, no grade entered."""
    raw = {
        "project": {"name": "grades"},
        "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
        "top_rail": {"section": "Pipe2STD"}, "post": {"section": "Pipe2STD"},
        "welds": {"rail_to_post": "1/8", "post_to_baseplate": "1/4"},
        "baseplate": {"B": 6, "N": 8}, "intermediate_rail": {"none": True},
    }
    for name, table in tables.items():
        raw[name] = table if name == "intermediate_rail" else {**raw.get(name, {}), **table}
    return raw


def _members(**tables) -> members.Members:
    return members.resolve(project.from_dict(_raw(**tables)), Registry())


def _wall(t_nom: float) -> shapes.Section:
    """A stand-in round HSS with this nominal wall, in inches."""
    return dataclasses.replace(shapes.section("HSS10.000X0.625"), tnom=Q_(t_nom, "inch"), label="FakeHSS")


# -- defaults by shape (S5-5) ---------------------------------------------------

def test_a_grade_left_out_defaults_by_shape():
    m = _members(post={"section": "HSS2.375X0.125"})
    assert (m.project.top_rail.grade, m.project.top_rail.grade_defaulted) == ("A53 Gr B", True)   # AISC pipe
    assert (m.project.post.grade, m.project.post.grade_defaulted) == ("A500 Gr B", True)          # round HSS
    assert materials.DEFAULT_GRADE == {PIPE: "A53 Gr B", ROUND_HSS: "A500 Gr B", ROUND_TUBE: "A500 Gr B"}


def test_a_grade_entered_is_kept_and_not_marked_as_defaulted():
    m = _members(top_rail={"grade": "A500 Gr C"}, post={"grade": "A53 Gr B"})
    assert (m.project.top_rail.grade, m.project.top_rail.grade_defaulted) == ("A500 Gr C", False)
    assert (m.project.post.grade, m.project.post.grade_defaulted) == ("A53 Gr B", False)


def test_filling_in_the_defaults_twice_changes_nothing():
    reg = Registry()
    once = members.resolve(project.from_dict(_raw()), reg).project
    assert members.resolve(once, reg).project == once


# -- the intermediate rail's default grade (S5-10) --------------------------------

OWN_WELD = {"intermediate_rail_to_post": "1/8"}


def _own(section: str, **more) -> dict:
    return {"same_as_top_rail": False, "section": section, **more}


def test_an_hss_intermediate_rail_under_a_pipe_top_rail_defaults_to_a500_gr_b():
    """A53 Gr B is not on the standard list for round HSS, so the
    intermediate rail takes its own shape's default, not the top rail's
    grade with a warning."""
    m = _members(intermediate_rail=_own("HSS1.900X0.120"), welds=OWN_WELD)
    assert m.project.intermediate_member == project.Member("HSS1.900X0.120", "A500 Gr B", grade_defaulted=True)


def test_an_hss_intermediate_rail_under_an_hss_gr_c_top_rail_defaults_to_gr_c():
    m = _members(top_rail={"section": "HSS2.375X0.154", "grade": "A500 Gr C"},
                 intermediate_rail=_own("HSS1.900X0.120"), welds=OWN_WELD)
    assert m.project.intermediate_member == project.Member("HSS1.900X0.120", "A500 Gr C", grade_defaulted=True)


def test_a_pipe_intermediate_rail_under_an_hss_top_rail_defaults_to_a53_gr_b():
    m = _members(top_rail={"section": "HSS2.375X0.154", "grade": "A500 Gr C"},
                 intermediate_rail=_own("Pipe1-1/4STD"), welds=OWN_WELD)
    assert m.project.intermediate_member == project.Member("Pipe1-1/4STD", "A53 Gr B", grade_defaulted=True)


def test_an_intermediate_rail_grade_entered_is_kept():
    m = _members(intermediate_rail=_own("HSS1.900X0.120", grade="A847"), welds=OWN_WELD)
    assert m.project.intermediate_member == project.Member("HSS1.900X0.120", "A847")


def test_the_standard_list_read_for_the_default_is_recorded_for_the_draft_list():
    """S5-10 reads the round HSS list, a drafted entry, so the calc lists it."""
    reg = Registry()
    members.resolve(project.from_dict(_raw(intermediate_rail=_own("HSS1.900X0.120"), welds=OWN_WELD)), reg)
    assert "material.grades.hss_round" in [e.id for e in reg.drafted_used]
    reg = Registry()
    members.resolve(project.from_dict(_raw(intermediate_rail=_own("Pipe1-1/4STD"), welds=OWN_WELD)), reg)
    assert reg.drafted_used == []  # the pipe list is verified, and nothing else is read


# -- Fy and Fu by grade and shape -------------------------------------------------

@pytest.mark.parametrize("family", [PIPE, ROUND_HSS, ROUND_TUBE])
def test_every_round_hollow_family_takes_the_pipe_grade_and_every_round_hss_grade(family):
    reg = Registry()
    hss = reg.get("material.grades.hss_round").value
    assert materials.supported(family) == ["A53 Gr B", *hss]


@pytest.mark.parametrize("grade, name", [("A501 Gr A", "A501_GrA"), ("A501 Gr B", "A501_GrB"), ("A847", "A847"),
                                         ("A500 Gr B", "A500_GrB"), ("A500 Gr C", "A500_GrC"),
                                         ("A1085 Gr A", "A1085_GrA")])
def test_a_plain_round_hss_grade_reads_its_own_fy_and_fu(grade, name):
    reg = Registry()
    sec = shapes.section("HSS2.375X0.154")
    fy, fu = materials.yield_stress(reg, grade, sec), materials.tensile_strength(reg, grade, sec)
    assert (fy.entry, fy.note, fy.range) == (f"material.{name}.hss_round.Fy", f"Yield stress, {grade}", "")
    assert (fu.entry, fu.note, fu.range) == (f"material.{name}.hss_round.Fu", f"Tensile strength, {grade}", "")
    assert fy.quantity(reg) == reg.entries[fy.entry].quantity
    assert fu.quantity(reg) == reg.entries[fu.entry].quantity


def test_an_hss_grade_runs_through_every_check_that_reads_fy_or_fu():
    """A500 Gr C on a pipe rail and post (an unusual pairing, allowed): the
    Fy lines of Checks 1 and 5 and the Fu line of Check 3 cite the grade's
    own entries and carry its values."""
    reg = Registry()
    res = engine.run(project.from_dict(_raw(top_rail={"grade": "A500 Gr C"}, post={"grade": "A500 Gr C"})), reg)
    fy = reg.entries["material.A500_GrC.hss_round.Fy"]
    fu = reg.entries["material.A500_GrC.hss_round.Fu"]

    def line(check, key):
        case = next(c for c in res.check(check).cases if c.lines)
        return next(ln for ln in case.lines if ln.key == key)

    for check in (1, 5):
        assert (line(check, "F_y").value, line(check, "F_y").note) == (fy.quantity, "Yield stress, A500 Gr C")
    assert (line(3, "F_u_BM").value, line(3, "F_u_BM").note) == (fu.quantity, "Tensile strength, A500 Gr C")
    used = [e.id for e in reg.used]
    assert fy.id in used and fu.id in used and "material.A53_GrB.Fy" not in used


# -- A618: Fy and Fu by nominal wall (S5-7) -----------------------------------------

@pytest.mark.parametrize("grade, name", [("A618 Gr Ia", "A618_GrIa"), ("A618 Gr Ib", "A618_GrIb"),
                                         ("A618 Gr II", "A618_GrII")])
@pytest.mark.parametrize("t_nom, wall_range, words", [
    (0.5, materials.THIN, ", wall up to 0.7500 in"),
    (0.75, materials.THIN, ", wall up to 0.7500 in"),              # exactly 3/4 in takes the values up to 3/4 in
    (0.751, materials.THICK, ", wall over 0.7500 in to 1.500 in"),  # just over
    (1.5, materials.THICK, ", wall over 0.7500 in to 1.500 in"),
])
def test_a618_reads_fy_and_fu_by_the_nominal_wall(grade, name, t_nom, wall_range, words):
    reg = Registry()
    sec = _wall(t_nom)
    fy, fu = materials.yield_stress(reg, grade, sec), materials.tensile_strength(reg, grade, sec)
    assert (fy.entry, fy.range, fy.note) == (f"material.{name}.Fy", wall_range, f"Yield stress, {grade}{words}")
    assert (fu.entry, fu.range, fu.note) == (f"material.{name}.Fu", wall_range, f"Tensile strength, {grade}{words}")
    assert fy.quantity(reg) == Q_(reg.entries[fy.entry].value[wall_range], "ksi")
    assert fu.quantity(reg) == Q_(reg.entries[fu.entry].value[wall_range], "ksi")
    # The limits are read from the registry, so a calc in this grade lists them.
    assert {"material.A618.wall.thin_limit", "material.A618.wall.thick_limit"} <= {e.id for e in reg.used}


def test_a618_compares_the_nominal_wall_not_the_design_wall():
    """A database section's design wall is 0.93 of its nominal wall: a
    nominal wall just over 3/4 in has a design wall under it, and still
    takes the thicker range."""
    sec = _wall(0.8)
    assert sec.tdes < Q_(0.75, "inch") < sec.tnom
    assert materials.yield_stress(Registry(), "A618 Gr II", sec).range == materials.THICK


@pytest.mark.parametrize("grade", ["A618 Gr Ia", "A618 Gr Ib", "A618 Gr II"])
def test_an_a618_wall_over_the_thick_limit_stops_naming_member_wall_grade_and_limit(grade):
    with pytest.raises(SectionStop) as stopped:
        materials.yield_stress(Registry(), grade, _wall(1.6), "Post")
    assert stopped.value.stop is Stop.GRADE_WALL_OVER_LIMIT
    assert str(stopped.value) == (
        f"Post FakeHSS, {grade}: nominal wall 1.600 in is over 1.500 in, the thickest wall AISC Manual Table 2-4 "
        f"gives Fy and Fu for in this grade. The tool does not check this section in this grade.")


@pytest.mark.parametrize("t_nom", [0.25, 0.75, 1.0, 1.6])
def test_a618_gr_iii_has_one_fy_and_fu_at_any_wall(t_nom):
    reg = Registry()
    fy = materials.yield_stress(reg, "A618 Gr III", _wall(t_nom))
    assert (fy.entry, fy.range, fy.note) == ("material.A618_GrIII.Fy", "", "Yield stress, A618 Gr III")
    assert "material.A618.wall.thin_limit" not in [e.id for e in reg.used]


def test_a_by_wall_grade_prints_the_value_of_its_range_as_a_calc_line():
    reg = Registry()
    sh = Sheet(reg)
    fy = materials.yield_stress(reg, "A618 Gr II", _wall(1.0)).line(sh, "F_y", "F_y")
    entry = reg.entries["material.A618_GrII.Fy"]
    assert fy.value == Q_(entry.value[materials.THICK], "ksi")
    assert (sh.lines[-1].note, sh.lines[-1].cite) == ("Yield stress, A618 Gr II, wall over 0.7500 in to 1.500 in",
                                                      entry.cite)


# -- an unsupported grade ---------------------------------------------------------

def test_an_unsupported_grade_names_the_grade_and_the_grades_supported_for_that_shape():
    with pytest.raises(ProjectError) as stopped:
        engine.run(project.from_dict(_raw(post={"grade": "A36"})), Registry())
    assert stopped.value.stop is Stop.GRADE_UNSUPPORTED
    assert str(stopped.value) == (
        "post grade 'A36': for AISC pipe this version supports A53 Gr B, A500 Gr B, A500 Gr C, A501 Gr A, "
        "A501 Gr B, A618 Gr Ia, A618 Gr Ib, A618 Gr II, A618 Gr III, A847, A1085 Gr A only")


def test_a1065_is_not_a_round_grade():
    """A1065 moves to slice 6 with rectangular HSS (S5-6)."""
    for family in (PIPE, ROUND_HSS, ROUND_TUBE):
        assert not [g for g in materials.supported(family) if g.startswith("A1065")]


def test_a_blank_grade_entered_is_not_defaulted():
    with pytest.raises(ProjectError, match="post grade '': for AISC pipe this version supports"):
        engine.run(project.from_dict(_raw(post={"grade": ""})), Registry())


# -- the section page: the unusual-pairing warning and the A1085 note (S5-5, S5-6) ---

def _source(**tables) -> str:
    reg = Registry()
    return report.build_source(engine.run(project.from_dict(_raw(**tables)), reg), reg, CLEAN)


def test_an_hss_grade_on_a_pipe_designation_prints_the_unusual_pairing_warning():
    reg = Registry()
    res = engine.run(project.from_dict(_raw(top_rail={"grade": "A500 Gr C"})), reg)
    text = reg.entries["ej.grade.unusual_pairing"].value.format(grade="A500 Gr C", shape="pipe")
    assert res.rail_notes == [f"UNUSUAL PAIRING: {text}"]
    assert text == ("A500 Gr C is not a grade AISC Manual Table 2-4 lists for pipe. The calc uses the Fy and Fu "
                    "of A500 Gr C; confirm the grade.")
    assert res.post_notes == [] and res.inter_notes == []  # the post is A53 Gr B pipe by default
    assert "ej.grade.unusual_pairing" in [e.id for e in reg.drafted_used]


def test_a53_gr_b_on_an_hss_designation_prints_the_unusual_pairing_warning():
    res = engine.run(project.from_dict(_raw(post={"section": "HSS2.375X0.125", "grade": "A53 Gr B"})), Registry())
    warning = ("UNUSUAL PAIRING: A53 Gr B is not a grade AISC Manual Table 2-4 lists for round HSS. "
               "The calc uses the Fy and Fu of A53 Gr B; confirm the grade.")
    assert res.post_notes == [warning]
    assert res.rail_notes == []


def test_a_grade_on_its_shapes_standard_list_prints_no_warning():
    reg = Registry()
    res = engine.run(project.from_dict(_raw(post={"section": "HSS2.375X0.125", "grade": "A500 Gr C"})), reg)
    assert res.rail_notes == res.post_notes == res.inter_notes == []
    assert "ej.grade.unusual_pairing" not in [e.id for e in reg.used]


def test_no_grade_is_unusual_for_a_custom_round_tube():
    """A custom round tube takes every round HSS grade and A53 Gr B, and
    none is an unusual pairing for it. No custom tube can be entered yet, so
    this is a stand-in: a pipe given the custom round tube family."""
    tube = dataclasses.replace(shapes.section("Pipe2STD"), family=ROUND_TUBE)
    for grade in materials.supported(ROUND_TUBE):
        assert properties.grade_notes(Registry(), tube, grade) == []


def test_the_warning_prints_under_its_own_member_on_the_section_page():
    src = _source(intermediate_rail=_own("HSS1.900X0.120", grade="A53 Gr B"), welds=OWN_WELD)
    header = src.index('#text("Intermediate rail: HSS1.900X0.120, A53 Gr B.")')
    flag = src.index('#flag("UNUSUAL PAIRING: A53 Gr B is not a grade AISC Manual Table 2-4 lists for round HSS.')
    assert header < flag < src.index("= Loading")
    assert src.count("UNUSUAL PAIRING") == 1


def test_an_a1085_database_section_prints_the_note_and_runs_on_its_published_properties():
    reg = Registry()
    res = engine.run(project.from_dict(_raw(post={"section": "HSS2.375X0.125", "grade": "A1085 Gr A"})), reg)
    note = reg.entries["ej.grade.A1085_database_note"].value
    assert res.post_notes == [note] and note.startswith("A1085: AISC 360-22 §B4.2 permits")
    published = shapes.section("HSS2.375X0.125")
    assert res.post == published and res.post.tdes < res.post.tnom  # the database's 0.93 wall, as published
    t_des = next(ln for ln in res.post_section_lines if ln.key == "t_des")
    assert t_des.value == published.tdes
    fy = next(ln for ln in next(c for c in res.check(5).cases if c.lines).lines if ln.key == "F_y")
    assert fy.value == reg.entries["material.A1085_GrA.hss_round.Fy"].quantity


def test_a1085_on_a_pipe_designation_prints_both_the_warning_and_the_note():
    res = engine.run(project.from_dict(_raw(top_rail={"grade": "A1085 Gr A"})), Registry())
    assert len(res.rail_notes) == 2
    assert res.rail_notes[0].startswith("UNUSUAL PAIRING: A1085 Gr A is not a grade")
    assert res.rail_notes[1].startswith("A1085: ")


def test_same_as_the_top_rail_prints_the_top_rails_notes_once():
    src = _source(top_rail={"grade": "A500 Gr B"}, intermediate_rail={"same_as_top_rail": True})
    assert src.count("UNUSUAL PAIRING") == 1


def test_an_all_pipe_calc_with_its_grades_entered_prints_no_grade_note():
    src = _source(top_rail={"grade": "A53 Gr B"}, post={"grade": "A53 Gr B"})
    assert "UNUSUAL PAIRING" not in src and "A1085" not in src


# -- a defaulted grade prints as defaulted (S5-10) --------------------------------------

def test_a_defaulted_grade_prints_default_on_the_section_page_and_an_entered_one_does_not():
    src = _source(post={"section": "HSS2.375X0.125"},
                  intermediate_rail=_own("HSS1.900X0.120", grade="A500 Gr C"), welds=OWN_WELD)
    assert '#text("Top rail: Pipe2STD, A53 Gr B (default).")' in src
    assert '#text("Post: HSS2.375X0.125, A500 Gr B (default).")' in src
    assert '#text("Intermediate rail: HSS1.900X0.120, A500 Gr C.")' in src


def test_the_default_grade_entered_by_hand_is_not_marked():
    src = _source(top_rail={"grade": "A53 Gr B"}, post={"grade": "A53 Gr B"})
    assert "(default)" not in src


def test_an_intermediate_rail_grade_left_out_is_marked_whichever_grade_it_takes():
    """S5-10: its own shape's default, or the top rail's grade. Either way
    the engineer did not enter it."""
    own_default = _source(intermediate_rail=_own("HSS1.900X0.120"), welds=OWN_WELD)
    assert '#text("Intermediate rail: HSS1.900X0.120, A500 Gr B (default).")' in own_default
    top_rails = _source(top_rail={"section": "HSS2.375X0.154", "grade": "A500 Gr C"},
                        intermediate_rail=_own("HSS1.900X0.120"), welds=OWN_WELD)
    assert '#text("Intermediate rail: HSS1.900X0.120, A500 Gr C (default).")' in top_rails


def test_the_mark_prints_on_the_section_page_only():
    """Where the grade already prints (Micah, 2026-10-09): not on the calc
    lines that name the grade, and not for the baseplate or the electrode."""
    src = _source()
    assert src.count("(default)") == 2  # the top rail and the post
    assert '#text("Baseplate: A36. Welds: fillet, all around, electrode E70XX.")' in src
    assert '"Yield stress, A53 Gr B"' in src
