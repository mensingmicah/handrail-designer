"""Custom round tubes: the property formulas against AISC's published
values (docs/plans/slice-5.md, T3), and the custom tube's input, design
wall and printed lines (T4; docs/brief/inputs.md, S5-8).

**The property-formula test (T3)** runs the custom tube's formulas
(tube.properties) on rows of the AISC Shapes Database, on each row's listed
outside diameter, nominal wall and design wall, and compares the results
with the published values. It is a check against AISC's numbers, not a
same-author one. "Reproduces" means the formula's value, rounded as the
database prints it, is the published value. A row that fails to reproduce
is reported to Micah; the tolerance is never widened.

Binding (Micah, 2026-10-10):

- The 67 round HSS rows whose OD column is the designation's OD and is 10 in
  or less: A, I, S, Z, r and D/t reproduce; the weight is within 0.5%.
- The 36 pipe rows under 12 in OD: I, S, Z and r reproduce or come out
  below published, never above.

Not asserted, and listed in data/README.md as findings:

- Pipe area under 12 in OD. It comes out ABOVE published on five rows, which
  Micah's ruling says to park and report: it waits on him (slice status
  issue). Pipe D/t, which misses on one row (below published).
- The six XS pipe rows 14 to 26 in, whose published A, I, S and Z match a
  wall of 0.90 t_nom, not the listed design wall; the other pipe rows 12 in
  and over; round HSS rows over 10 in, and those whose OD column is rounded
  away from the designation.

**The machinery tests (T4)** are same-author. They are not test cases, and
no value in them is a hand or independent value.
"""

import math
import re
import tomllib

import pytest

from handrail import engine, flexure, project, properties, report, shapes, tube
from handrail.calc import Sheet, Sym
from handrail.errors import SectionStop
from handrail.project import ProjectError
from handrail.registry import Registry
from handrail.shapes import PIPE, ROUND_HSS, ROUND_TUBE
from handrail.shapes_extract import PIPE_TOML, ROUND_HSS_TOML
from handrail.stops import Stop
from handrail.units import Q_
from test_report import CLEAN

# ---------------------------------------------------------------------------
# T3: the formulas on database rows
# ---------------------------------------------------------------------------

# Database column -> (the formula's value, the unit the column is in).
COLUMNS = {"A": ("A", "in^2"), "Ix": ("I", "in^4"), "Sx": ("S", "in^3"), "Zx": ("Z", "in^3"), "rx": ("r", "inch"),
           "D/t": ("D_t", ""), "W": ("W", "lbf/ft")}


def _rows(path) -> dict[str, dict]:
    with open(path, "rb") as f:
        return tomllib.load(f)["shape"]


def _designation_od(label: str) -> float:
    found = re.match(r"HSS([0-9.]+)X", label)
    assert found, label
    return float(found.group(1))


HSS_ROWS = {label: row for label, row in _rows(ROUND_HSS_TOML).items()
            if row["OD"] == _designation_od(label) and row["OD"] <= 10}
PIPE_ROWS = {label: row for label, row in _rows(PIPE_TOML).items() if row["OD"] < 12}


def _computed(row: dict) -> dict[str, float]:
    """The formulas' values for one database row, by database column."""
    sh = Sheet(Registry())
    p = tube.properties(sh, Sym("D", Q_(row["OD"], "inch")), Sym("t_nom", Q_(row["tnom"], "inch")),
                        Sym("t_des", Q_(row["tdes"], "inch")))
    out = {}
    for column, (name, unit) in COLUMNS.items():
        value = getattr(p, name).value
        out[column] = value.m_as(unit) if unit else value
    return out


def _decimals(published: float) -> int:
    text = repr(float(published))
    return 0 if text.endswith(".0") else len(text.split(".")[1])


def _sig3(x: float) -> float:
    return round(x, 2 - math.floor(math.log10(abs(x))))


def reproduces(published: float, computed: float) -> bool:
    """Whether the computed value, rounded as the database prints it, is the
    published value: to three significant figures, or to the published
    number of decimals where the database prints fewer figures (0.016)."""
    if math.isclose(_sig3(computed), published, rel_tol=1e-9):
        return True
    decimals = _decimals(published)
    return decimals > 0 and math.isclose(round(computed, decimals), published, rel_tol=1e-9)


def _misses(rows: dict[str, dict], column: str, accept) -> list[str]:
    out = []
    for label, row in rows.items():
        computed = _computed(row)[column]
        if not accept(row[column], computed):
            out.append(f"{label}: published {row[column]:g}, formula {computed:.5g} "
                       f"({(computed - row[column]) / row[column]:+.2%})")
    return out


def test_the_binding_groups_are_the_rows_the_ruling_names():
    """67 round HSS rows (OD column equal to the designation's OD, 10 in or
    less) and 36 pipe rows under 12 in OD. A filter that lost rows would
    pass the tests below on fewer of them."""
    assert (len(HSS_ROWS), len(PIPE_ROWS)) == (67, 36)
    assert max(row["OD"] for row in HSS_ROWS.values()) == 10 and max(row["OD"] for row in PIPE_ROWS.values()) < 12


@pytest.mark.parametrize("column", ["A", "Ix", "Sx", "Zx", "rx", "D/t"])
def test_the_formulas_reproduce_every_binding_round_hss_row(column):
    misses = _misses(HSS_ROWS, column, reproduces)
    assert not misses, (f"{column} does not reproduce on {len(misses)} of {len(HSS_ROWS)} round HSS rows. Report it "
                        f"to Micah; do not widen the comparison (T3):\n" + "\n".join(misses))


def test_the_weight_formula_is_within_half_a_percent_on_every_binding_round_hss_row():
    """The weight is the steel unit weight times the area on the nominal wall (S5-8)."""
    misses = _misses(HSS_ROWS, "W", lambda published, computed: abs(computed - published) <= 0.005 * published)
    assert not misses, "weight over 0.5% from published (T3):\n" + "\n".join(misses)


@pytest.mark.parametrize("column", ["Ix", "Sx", "Zx", "rx"])
def test_the_formulas_reproduce_or_come_out_below_every_pipe_row_under_12_in(column):
    """Never above published beyond the database's rounding: a custom tube
    in the pipe grade must not be given more than the database pipe of the
    same dimensions. Above is the stop-and-ask of T3: park it and tell
    Micah, do not loosen this."""
    above = _misses(PIPE_ROWS, column, lambda published, computed: reproduces(published, computed)
                    or computed < published)
    assert not above, (f"{column} comes out ABOVE published on {len(above)} pipe rows under 12 in. Park it and report "
                       f"to Micah (T3):\n" + "\n".join(above))


# ---------------------------------------------------------------------------
# T4: the custom tube's input
# ---------------------------------------------------------------------------

TUBE = {"shape": "round tube", "OD": 2.375, "wall_nominal": 0.065}


def _raw(**tables) -> dict:
    """A project that runs: Pipe2STD rail and post over 6'-0", no intermediate rail.
    A table given replaces the base one whole, so a member can be a tube."""
    raw = {
        "project": {"name": "tube"},
        "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
        "top_rail": {"section": "Pipe2STD"}, "post": {"section": "Pipe2STD"},
        "welds": {"rail_to_post": "1/8", "post_to_baseplate": "1/4"},
        "baseplate": {"B": 6, "N": 8}, "intermediate_rail": {"none": True},
    }
    return {**raw, **tables}


def _run(registry: Registry | None = None, **tables):
    return engine.run(project.from_dict(_raw(**tables)), registry or Registry())


def _source(**tables) -> str:
    reg = Registry()
    return report.build_source(engine.run(project.from_dict(_raw(**tables)), reg), reg, CLEAN)


OWN_WELDS = {"rail_to_post": "1/8", "post_to_baseplate": "1/4", "intermediate_rail_to_post": "1/8"}


def test_a_custom_round_tube_is_read_with_its_od_and_nominal_wall():
    proj = project.from_dict(_raw(top_rail={**TUBE, "grade": "A500 Gr C"}))
    rail = proj.top_rail
    assert rail.custom and rail.section == "" and rail.grade == "A500 Gr C"
    assert rail.OD is not None and rail.wall_nominal is not None
    assert (rail.OD.value, rail.wall_nominal.value) == (Q_(2.375, "inch"), Q_(0.065, "inch"))
    assert not proj.post.custom and proj.post.OD is None


@pytest.mark.parametrize("missing", ["shape", "OD", "wall_nominal"])
def test_a_custom_tube_needs_its_shape_its_od_and_its_nominal_wall(missing):
    """wall_nominal is required, with no default (S5-8)."""
    table = {key: value for key, value in TUBE.items() if key != missing}
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(post=table))
    assert stopped.value.stop is Stop.FILE_MISSING_KEY
    assert str(stopped.value) == f"project file: [post] is missing '{missing}'"


@pytest.mark.parametrize("extra", [{"shape": "round tube"}, {"OD": 2.375}, {"wall_nominal": 0.065}, TUBE])
def test_a_section_given_with_custom_dimensions_stops_as_conflicting_inputs(extra):
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(top_rail={"section": "Pipe2STD", **extra}))
    assert stopped.value.stop is Stop.MEMBER_SECTION_WITH_CUSTOM_DIMENSIONS
    assert str(stopped.value) == (
        f"[top_rail] section is given together with {', '.join(extra)}. A member is either a standard section "
        f"(section) or a custom round tube (shape = \"round tube\", OD and wall_nominal), not both. Remove one.")


@pytest.mark.parametrize("wall", [1.1875, 1.5])
def test_a_wall_of_half_the_od_or_more_stops(wall):
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(post={**TUBE, "wall_nominal": wall}))
    assert stopped.value.stop is Stop.MEMBER_WALL_HALF_OD_OR_MORE
    assert "is half the OD (2.375) or more, which is not a tube" in str(stopped.value)


def test_a_custom_shape_other_than_a_round_tube_stops():
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(post={**TUBE, "shape": "rectangular tube"}))
    assert stopped.value.stop is Stop.MEMBER_SHAPE_UNSUPPORTED
    assert str(stopped.value) == "[post] shape 'rectangular tube': this version supports \"round tube\" only"


def test_an_intermediate_rail_can_be_a_custom_tube_and_its_dimensions_conflict_with_the_other_states():
    own = {"same_as_top_rail": False, "shape": "round tube", "OD": 1.66, "wall_nominal": 0.109}
    res = _run(intermediate_rail=own, welds=OWN_WELDS)
    assert res.inter is not None and res.inter.family == ROUND_TUBE and res.inter.OD == Q_(1.66, "inch")
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(intermediate_rail={"none": True, "OD": 1.66}))
    assert stopped.value.stop is Stop.INTERMEDIATE_NONE_WITH_INPUTS and "[intermediate_rail] OD" in str(stopped.value)
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(intermediate_rail={"shape": "round tube", "OD": 1.66, "wall_nominal": 0.109}))
    assert stopped.value.stop is Stop.INTERMEDIATE_SAME_WITH_INPUTS


# ---------------------------------------------------------------------------
# T4: the design wall, the properties and the grade
# ---------------------------------------------------------------------------

def _tube(grade: str = "A500 Gr B", od: float = 2.375, wall: float = 0.065, registry: Registry | None = None):
    proj = project.from_dict(_raw(post={"shape": "round tube", "OD": od, "wall_nominal": wall, "grade": grade}))
    assert proj.post.OD is not None and proj.post.wall_nominal is not None
    return tube.round_tube(registry or Registry(), proj.post.OD, proj.post.wall_nominal, grade)


def test_the_design_wall_is_the_registry_coefficient_times_the_nominal_wall():
    reg = Registry()
    sec = _tube(registry=reg)
    coeff = reg.entries["aisc360.B4.2.coeff"].value
    assert sec.tnom == Q_(0.065, "inch")
    assert sec.tdes.m_as("inch") == pytest.approx(coeff * 0.065, rel=1e-12)
    line = next(ln for ln in sec.computed if ln.key == "t_des")
    assert line.cite == reg.entries["aisc360.B4.2.design_wall"].cite and '"0.93" t_"nom"' in (line.symbolic or "")


def test_a_custom_a1085_tube_runs_on_the_nominal_wall():
    """S5-6: AISC 360-22 B4.2 gives A1085 the nominal wall as its design wall."""
    reg = Registry()
    a1085, a500 = _tube("A1085 Gr A", registry=reg), _tube("A500 Gr B")
    assert a1085.tdes == a1085.tnom == Q_(0.065, "inch")
    assert a1085.A > a500.A and a1085.I > a500.I and a1085.D_t < a500.D_t
    assert a1085.W == a500.W  # the weight is on the nominal wall for both
    line = next(ln for ln in a1085.computed if ln.key == "t_des")
    assert line.symbolic == 't_"nom"' and line.cite == reg.entries["aisc360.B4.2.nominal_wall"].cite
    assert "aisc360.B4.2.coeff" not in [e.id for e in reg.used]


@pytest.mark.parametrize("grade", ["A53 Gr B", "A500 Gr C", "A501 Gr A", "A618 Gr II", "A847"])
def test_every_other_grade_takes_the_reduced_design_wall(grade):
    """The rule is by ASTM standard, not by how the tube is made: hot-formed
    A501 and A618 take the same coefficient as A500 (S5-6)."""
    assert _tube(grade).tdes == _tube("A500 Gr B").tdes < Q_(0.065, "inch")


def test_the_properties_are_exact_geometry_on_the_design_wall_and_the_weight_on_the_nominal_wall():
    reg = Registry()
    sec = _tube(registry=reg)
    D, t, tn = 2.375, sec.tdes.m_as("inch"), 0.065
    d = D - 2 * t
    A, I = math.pi / 4 * (D**2 - d**2), math.pi / 64 * (D**4 - d**4)
    rho = reg.entries["material.steel.density"].quantity
    assert sec.A.m_as("in^2") == pytest.approx(A, rel=1e-12)
    assert sec.I.m_as("in^4") == pytest.approx(I, rel=1e-12)
    assert sec.S.m_as("in^3") == pytest.approx(I / (D / 2), rel=1e-12)
    assert sec.Z.m_as("in^3") == pytest.approx((D**3 - d**3) / 6, rel=1e-12)
    assert sec.r.m_as("inch") == pytest.approx(math.sqrt(I / A), rel=1e-12)
    assert sec.D_t == pytest.approx(D / t, rel=1e-12)
    nominal_area = Q_(math.pi / 4 * (D**2 - (D - 2 * tn) ** 2), "in^2")
    assert sec.W.m_as("lbf/ft") == pytest.approx((rho * nominal_area).m_as("lbf/ft"), rel=1e-12)


def test_a_custom_tube_is_a_round_section_named_by_its_dimensions():
    sec = _tube(od=2.375, wall=0.055)
    assert (sec.label, sec.family, sec.source, sec.custom) == ("Round tube 2.375 × 0.055 (custom)", ROUND_TUBE,
                                                              shapes.CUSTOM, True)
    assert sec.x == sec.y and sec.I == sec.x.I
    assert [ln.key for ln in sec.computed] == ["D", "t_nom", "t_des", "D_i", "A", "D_i_nom", "A_nom", "rho", "W",
                                               "I", "S", "Z", "r", "D_over_t"]


def test_a_custom_tubes_grade_defaults_to_a500_gr_b_and_an_intermediate_tube_takes_the_top_rails():
    res = _run(post=TUBE)
    assert (res.project.post.grade, res.project.post.grade_defaulted) == ("A500 Gr B", True)
    own = {"same_as_top_rail": False, "shape": "round tube", "OD": 1.66, "wall_nominal": 0.109}
    for top_grade in ("A53 Gr B", "A847"):  # any grade a custom tube accepts (S5-10)
        res = _run(top_rail={"section": "Pipe2STD", "grade": top_grade}, intermediate_rail=own, welds=OWN_WELDS)
        member = res.project.intermediate_member
        assert member is not None and (member.grade, member.grade_defaulted) == (top_grade, True)


def test_no_grade_is_an_unusual_pairing_for_a_custom_tube():
    for grade in ("A53 Gr B", "A500 Gr C", "A1085 Gr A"):
        res = _run(post={**TUBE, "grade": grade})
        assert res.post_notes == [] and properties.grade_notes(Registry(), res.post, grade) == []


def test_a_custom_tube_in_the_pipe_grade_prints_designed_as_round_hss_and_one_in_an_hss_grade_does_not():
    def says(res) -> bool:
        # Check 5's moment cases print the flexure block; its axial-only cases do not.
        return any(ln.kind == "decision" and ln.text == "Designed as round HSS"
                   for case in res.check(5).cases for ln in case.lines)

    assert says(_run(post={**TUBE, "wall_nominal": 0.154, "grade": "A53 Gr B"}))
    assert not says(_run(post={**TUBE, "wall_nominal": 0.154, "grade": "A500 Gr B"}))
    assert flexure.designed_as_round_hss(_tube("A53 Gr B"), "A53 Gr B")


def test_a_custom_post_within_the_od_tolerance_of_a_pipe_rail_runs():
    res = _run(post={**TUBE, "OD": 2.38, "wall_nominal": 0.154})
    assert res.post.OD == Q_(2.38, "inch") and res.rail.OD == Q_(2.375, "inch")


# ---------------------------------------------------------------------------
# T4: the existing stops, on a computed D/t
# ---------------------------------------------------------------------------

def _post(od: float, wall: float, grade: str = "A500 Gr B") -> dict:
    """A custom post under a rail of the same diameter, with no intermediate
    rail, so the post is not a chord."""
    return {"top_rail": {"shape": "round tube", "OD": od, "wall_nominal": 0.25},
            "post": {"shape": "round tube", "OD": od, "wall_nominal": wall, "grade": grade},
            "baseplate": {"B": 8, "N": 8}}


def test_a_custom_tube_slender_in_compression_stops_on_its_computed_ratio():
    with pytest.raises(SectionStop) as stopped:
        _run(**_post(6.0, 0.065))  # D/t = 6 / (0.93 x 0.065) = 99.3, over 0.11E/Fy
    assert stopped.value.stop is Stop.SECTION_SLENDER_IN_COMPRESSION
    assert str(stopped.value).startswith("Round tube 6 × 0.065 (custom): wall is slender in compression, D/t = 99.26 > ")


def test_a_custom_tube_slender_in_flexure_stops_on_its_computed_ratio():
    with pytest.raises(SectionStop) as stopped:
        _run(**_post(6.0, 0.026))  # D/t = 248, over 0.31E/Fy and under 0.45E/Fy
    assert stopped.value.stop is Stop.SECTION_SLENDER_IN_FLEXURE
    assert "wall is slender in flexure, D/t = 248.1 > lambda_r" in str(stopped.value)


def test_a_custom_tube_beyond_the_f8_limit_stops_on_its_computed_ratio():
    with pytest.raises(SectionStop) as stopped:
        _run(**_post(6.0, 0.02))  # D/t = 323, not less than 0.45E/Fy
    assert stopped.value.stop is Stop.SECTION_BEYOND_F8_LIMIT
    assert "Round tube 6 × 0.02 (custom): D/t = 322.6 is not less than" in str(stopped.value)


def test_an_a618_custom_tube_over_the_thick_wall_limit_stops_naming_the_member():
    """S5-7's stop, which no database section reaches: a 1.6 in wall."""
    with pytest.raises(SectionStop) as stopped:
        _run(**_post(8.0, 1.6, "A618 Gr II"))
    assert stopped.value.stop is Stop.GRADE_WALL_OVER_LIMIT
    assert str(stopped.value).startswith("Post Round tube 8 × 1.6 (custom), A618 Gr II: nominal wall 1.600 in is over")


def test_an_a618_custom_tube_reads_the_range_of_its_nominal_wall():
    res = _run(**_post(8.0, 0.8, "A618 Gr II"))  # nominal 0.8 in, design 0.744 in: the thicker range
    fy = next(ln for ln in next(c for c in res.check(5).cases if c.lines).lines if ln.key == "F_y")
    assert fy.note == "Yield stress, A618 Gr II, wall over 0.7500 in to 1.500 in"


# ---------------------------------------------------------------------------
# T4: what a custom tube prints (F10 items 2 and 4 to 7)
# ---------------------------------------------------------------------------

def test_the_section_page_prints_a_custom_tubes_properties_as_calc_lines():
    src = _source(top_rail={**TUBE, "grade": "A500 Gr C"})
    assert ('#text("Top rail: Round tube 2.375 × 0.065 (custom), A500 Gr C.") Properties are computed below from the '
            'dimensions entered, on the design wall thickness of AISC 360-22 §B4.2; the weight is on the nominal '
            'wall.') in src
    # The database sentence still prints once, after the first database section: the post.
    assert src.count("Properties are used exactly as published in the AISC Shapes Database v16.0.") == 1
    assert ('#text("Post: Pipe2STD, A53 Gr B (default).") Properties are used exactly as published in the AISC '
            'Shapes Database v16.0.') in src
    assert '"Nominal wall thickness (0.065 as entered)"' in src
    assert '"Diameter-to-thickness ratio, computed (design wall)"' in src
    assert '"lambda = D/t, computed (design wall)", "Section properties (custom section)"' in src
    assert '"Top rail self-weight: computed W = 1.605 lb/ft", "Section properties (custom section)"' in src


def test_an_all_database_calc_prints_the_database_sentence_once_after_the_top_rail():
    src = _source(intermediate_rail={"same_as_top_rail": False, "section": "Pipe1-1/4STD"}, welds=OWN_WELDS)
    assert src.count("Properties are used exactly as published in the AISC Shapes Database v16.0.") == 1
    assert '#text("Top rail: Pipe2STD, A53 Gr B (default).") Properties are used exactly as published' in src
    assert "Properties are computed below" not in src and "computed (design wall)" not in src


def test_the_rail_block_leaves_out_r_and_the_post_block_prints_it():
    res = _run(top_rail=TUBE, post={**TUBE, "wall_nominal": 0.154})
    assert "r" not in [ln.key for ln in res.section_lines]
    assert "r" in [ln.key for ln in res.post_section_lines]
    assert res.rail.r is not None  # computed either way


def test_the_dimensions_page_echoes_a_custom_tubes_od_and_nominal_wall():
    src = _source(post={"shape": "round tube", "OD": "2-3/8", "wall_nominal": "1/8"})
    assert '"Post, custom round tube: outside diameter", "2-3/8", "2 3/8\\"", "2.375 in"' in src
    assert '"Post, custom round tube: nominal wall", "1/8", "1/8\\"", "0.1250 in"' in src
    assert "Top rail, custom round tube" not in src


def test_the_weld_checks_cite_a_custom_tubes_own_source():
    res = _run(post={**TUBE, "wall_nominal": 0.154})
    ring = next(ln for ln in res.check(7).controlling.lines if ln.key == "D")
    assert ring.cite == shapes.CUSTOM and ring.note.startswith("Round tube 2.375 × 0.154 (custom): outside diameter")
    assert PIPE != ROUND_HSS  # the families stay distinct names
