"""Custom rectangular tubes: the property formulas against AISC's published
values (docs/plans/slice-6.md, T4), and the custom tube's input, design wall
and printed lines (T5; docs/brief/checks.md, S6-3, S6-4 and S6-14 item 6).

**The property-formula test (T4)** runs the custom tube's formulas
(rect_tube.properties) on the rectangular HSS rows of the AISC Shapes
Database, on each row's listed H, B, nominal wall and design wall, and
compares the results with the published values. It is a check against
AISC's numbers, not a same-author one. "Reproduces" means the formula's
value, rounded as the database prints it, is the published value. A row
that fails is reported to Micah; the tolerance is never widened.

Binding (S6-3, S6-16 item 5), on the 208 rows with Ht of 8 in or less:

- A, Ix, Iy, Zx, Zy, Sx, Sy, rx and ry reproduce or come out below
  published, never above, and no more than 1% below.
- The weight is within 0.5% of published.
- J reproduces at the database's printed precision, on every row but one.

Reported, not asserted, and listed in data/README.md as findings:

- J on HSS4X4X3/16, the one row it misses (published 10, formula 9.96).
- The 317 rows over 8 in.

b/t and h/t are not in the ruling's binding set; they reproduce on every
binding row with the three-thickness rule of AISC 360-22 B4.1b(d), and the
test holds that too.

**The machinery tests (T5)** are same-author. They are not test cases, and
no value in them is a hand or independent value.
"""

import pytest

from handrail import materials, members, project, properties, rect_tube, shapes
from handrail.calc import Sheet, Sym
from handrail.errors import SectionStop
from handrail.flexure import rect_axis_capacity, rect_limits, Unbraced
from handrail.project import ProjectError
from handrail.registry import Registry
from handrail.shapes import RECT_HSS, RECT_TUBE
from handrail.stops import Stop
from handrail.units import Q_
from test_tube import _decimals, _rows, _sig3, reproduces
from handrail.shapes_extract import RECT_HSS_TOML

# ---------------------------------------------------------------------------
# T4: the formulas on database rows
# ---------------------------------------------------------------------------

# Database column -> (the formula's value, the unit the column is in).
SECTION = {"A": ("A", "in^2"), "Ix": ("Ix", "in^4"), "Iy": ("Iy", "in^4"), "Zx": ("Zx", "in^3"),
           "Zy": ("Zy", "in^3"), "Sx": ("Sx", "in^3"), "Sy": ("Sy", "in^3"), "rx": ("rx", "inch"),
           "ry": ("ry", "inch")}
OTHER = {"J": ("J", "in^4"), "W": ("W", "lbf/ft"), "b/tdes": ("b_t", ""), "h/tdes": ("h_t", "")}
COLUMNS = {**SECTION, **OTHER}

ALL_ROWS = _rows(RECT_HSS_TOML)
BINDING = {label: row for label, row in ALL_ROWS.items() if row["Ht"] <= 8}
J_MISS = "HSS4X4X3/16"


def _computed(row: dict) -> dict[str, float]:
    """The formulas' values for one database row, by database column."""
    sh = Sheet(Registry())
    p = rect_tube.properties(sh, Sym("H", Q_(row["Ht"], "inch")), Sym("B", Q_(row["B"], "inch")),
                             Sym("t_nom", Q_(row["tnom"], "inch")), Sym("t_des", Q_(row["tdes"], "inch")))
    out = {}
    for column, (name, unit) in COLUMNS.items():
        value = getattr(p, name).value
        out[column] = value.m_as(unit) if unit else value
    return out


@pytest.fixture(scope="module")
def computed() -> dict[str, dict[str, float]]:
    return {label: _computed(row) for label, row in BINDING.items()}


def above(published: float, value: float) -> bool:
    """Whether the formula's value, rounded as the database prints it, is above the published one."""
    if reproduces(published, value):
        return False
    return _sig3(value) > published and round(value, _decimals(published)) > published


def test_the_binding_group_is_the_rows_the_ruling_names():
    """208 of the 525 rectangular HSS rows have Ht of 8 in or less (S6-3). A
    filter that lost rows would pass the tests below on fewer shapes."""
    assert len(ALL_ROWS) == 525 and len(BINDING) == 208
    assert max(row["Ht"] for row in BINDING.values()) == 8


@pytest.mark.parametrize("column", list(SECTION))
def test_a_section_property_reproduces_or_comes_out_below_published_never_above(computed, column):
    """Binding (S6-3). A row above published would make a custom tube
    unconservative against the database shape of the same dimensions: it
    stops the build and goes to Micah. Nothing here is tuned."""
    over = [f"{label}: published {row[column]:g}, formula {computed[label][column]:.5g}"
            for label, row in BINDING.items() if above(row[column], computed[label][column])]
    assert not over, f"{column} comes out ABOVE published on {len(over)} row(s); report to Micah:\n" + "\n".join(over)
    low = [f"{label}: published {row[column]:g}, formula {computed[label][column]:.5g} "
           f"({(computed[label][column] - row[column]) / row[column]:+.2%})"
           for label, row in BINDING.items() if computed[label][column] < 0.99 * row[column]]
    assert not low, f"{column} is more than 1% below published on {len(low)} row(s):\n" + "\n".join(low)


@pytest.mark.parametrize("column", ["A", "Zx", "Zy"])
def test_the_area_and_both_plastic_moduli_reproduce_on_every_binding_row(computed, column):
    """Stronger than the ruling asks, and true: these three reproduce to the
    printed digit on all 208 rows, which fixes the corner radii (2 t outside,
    t inside) as the ones the database's own properties are built on."""
    assert not [label for label, row in BINDING.items() if not reproduces(row[column], computed[label][column])]


def test_the_weight_is_within_half_a_percent_of_published(computed):
    off = {label: (computed[label]["W"] - row["W"]) / row["W"] for label, row in BINDING.items()}
    assert max(abs(d) for d in off.values()) < 0.005, max(off.items(), key=lambda kv: abs(kv[1]))


def test_j_reproduces_at_the_printed_precision_on_every_binding_row_but_one(computed):
    """S6-16 item 5. The one miss is reported to Micah, not asserted away and
    not tuned: HSS4X4X3/16, published 10, where the midline formula gives
    9.96. It is below published, so a custom tube's Lp and Lr are not helped
    by it."""
    misses = [label for label, row in BINDING.items() if not reproduces(row["J"], computed[label]["J"])]
    assert misses == [J_MISS]
    assert computed[J_MISS]["J"] < BINDING[J_MISS]["J"]
    assert not [label for label, row in BINDING.items() if above(row["J"], computed[label]["J"])]


@pytest.mark.parametrize("column", ["b/tdes", "h/tdes"])
def test_the_three_thickness_rule_reproduces_the_published_wall_ratios(computed, column):
    """AISC 360-22 B4.1b(d): the outside dimension less three times the
    design wall. It reproduces the database's own b/t and h/t on every
    binding row, so a custom tube classifies as the database shape of the
    same dimensions does."""
    assert not [label for label, row in BINDING.items() if not reproduces(row[column], computed[label][column])]


def test_the_larger_rows_are_a_finding_not_asserted():
    """Reported in data/README.md: over 8 in a few rows come out above
    published by up to about a quarter of a percent. Counted here so the
    README's figures cannot go stale silently; nothing is asserted of the
    values themselves."""
    large = {label: row for label, row in ALL_ROWS.items() if row["Ht"] > 8}
    over = {column: sum(above(row[column], _computed(row)[column]) for row in large.values())
            for column in ("Sx", "rx")}
    assert len(large) == 317
    assert all(count <= 5 for count in over.values()), over


# ---------------------------------------------------------------------------
# T5: input, design wall and the section a custom tube resolves to
# ---------------------------------------------------------------------------

TUBE = {"shape": "rectangular tube", "H": 4, "B": 2, "wall_nominal": "1/8", "long_side": "vertical"}


def _raw(**tables) -> dict:
    """A custom rectangular tube rail over a database HSS post, 6'-0". Each
    keyword replaces or extends one table; a key given as None is removed."""
    raw = {
        "project": {"name": "rect tube"},
        "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
        "top_rail": dict(TUBE),
        "post": {"section": "HSS2X2X1/8"},
        "welds": {"rail_to_post": "1/8", "post_to_baseplate": "3/16"},
        "baseplate": {"B": 6, "N": 8}, "intermediate_rail": {"none": True},
    }
    for name, table in tables.items():
        merged = table if name == "intermediate_rail" else {**raw.get(name, {}), **table}
        raw[name] = {key: value for key, value in merged.items() if value is not None}
    return raw


def _resolve(**tables) -> members.Members:
    return members.resolve(project.from_dict(_raw(**tables)), Registry())


def _stops(stop: Stop, resolve: bool = False, **tables) -> str:
    with pytest.raises(ProjectError) as stopped:
        if resolve:
            _resolve(**tables)
        else:
            project.from_dict(_raw(**tables))
    assert stopped.value.stop is stop, str(stopped.value)
    return str(stopped.value)


def test_a_custom_rectangular_tube_resolves_to_a_computed_section_of_its_own_family():
    m = _resolve()
    sec = m.rail
    assert sec.family == RECT_TUBE and sec.custom and sec.source == shapes.CUSTOM
    assert sec.label == "Rect. tube 4 × 2 × 0.125 (custom)"
    assert (sec.rect.H.m_as("inch"), sec.rect.B.m_as("inch")) == (4, 2)
    assert sec.tnom.m_as("inch") == 0.125
    assert sec.tdes.m_as("inch") == pytest.approx(Registry().get("aisc360.B4.2.coeff").value * 0.125)
    assert m.project.top_rail.grade == "A500 Gr B" and m.project.top_rail.grade_defaulted


def test_a_custom_tube_on_a_database_shapes_dimensions_matches_it_to_within_one_percent_from_below():
    """S6-3, accepted: a custom tube entered with a database shape's
    dimensions can differ from it by up to about 1%, on the low side. Its
    design wall is 0.93 x 0.125 = 0.11625 in against the published 0.116."""
    custom, published = _resolve().rail, shapes.section("HSS4X2X1/8")
    for name in ("x", "y"):
        mine, theirs = getattr(custom, name), getattr(published, name)
        for prop in ("I", "S", "Z", "r"):
            ratio = (getattr(mine, prop) / getattr(theirs, prop)).m_as("dimensionless")
            assert 0.99 < ratio < 1.01, (name, prop, ratio)
    assert (custom.rect.b_t, custom.rect.h_t) == pytest.approx((14.2, 31.4), abs=0.1)
    assert custom.rect.J.m_as("in^4") == pytest.approx(published.rect.J.m_as("in^4"), rel=0.01)


def test_the_weight_is_on_the_nominal_wall_and_the_properties_on_the_design_wall():
    """S5-8, S6-3. A1085 takes the nominal wall as its design wall (S5-6), so
    the same dimensions weigh the same and are stronger."""
    a500, a1085 = _resolve().rail, _resolve(top_rail={"grade": "A1085 Gr A"}).rail
    assert a1085.tdes == a1085.tnom == a500.tnom and a500.tdes < a500.tnom
    assert a1085.W == a500.W and a1085.A > a500.A and a1085.x.I > a500.x.I
    lines = {ln.key: ln for ln in a1085.computed}
    assert lines["t_des"].cite == Registry().get("aisc360.B4.2.nominal_wall").cite


def test_every_property_is_a_calc_line_with_its_citation():
    sec = _resolve().rail
    keys = [ln.key for ln in sec.computed]
    assert keys[:4] == ["H", "B", "t_nom", "t_des"]
    for key in ("R_o", "R_i", "A", "W", "I_x", "S_x", "Z_x", "r_x", "I_y", "S_y", "Z_y", "r_y", "J", "b_over_t",
                "h_over_t"):
        assert keys.count(key) == 1, key
    assert all(ln.cite for ln in sec.computed), [ln.key for ln in sec.computed if not ln.cite]
    reg = Registry()
    lines = {ln.key: ln for ln in sec.computed}
    assert lines["b_over_t"].cite == reg.get("aisc360.B4.1b.d.width").cite
    assert reg.get("ej.section.rect_tube.J").cite in lines["J"].cite
    assert reg.get("aisc360.CH3.midline_area").cite in lines["A_m"].cite
    # The section page prints those lines, then the orientation sentence.
    page = properties.section_lines(reg, sec, long_side="vertical")
    assert [ln.key for ln in page[:-1]] == keys and page[-1].kind == "decision"


def test_a_square_custom_tube_needs_no_orientation_and_has_equal_axes():
    m = _resolve(top_rail={"H": 2, "B": 2, "long_side": None})
    assert m.rail.rect.square and m.rail.x == m.rail.y
    assert "long_side = " in _stops(Stop.MEMBER_LONG_SIDE_NOT_APPLICABLE, resolve=True, top_rail={"H": 2, "B": 2})


def test_a_custom_tube_that_is_not_square_needs_its_orientation():
    message = _stops(Stop.MEMBER_LONG_SIDE_MISSING, resolve=True, top_rail={"long_side": None})
    assert message.startswith("[top_rail] is missing 'long_side': Rect. tube 4 × 2 × 0.125 (custom) is not square")


def test_h_is_the_longer_side():
    message = _stops(Stop.MEMBER_RECT_H_LESS_THAN_B, top_rail={"H": 2, "B": 4})
    assert message.startswith("[top_rail] H (2) is less than B (4).")


def test_a_wall_that_leaves_no_flat_stops():
    """B = 1 in against four design walls: 4 x 0.93 x 0.25 = 0.93 in leaves
    a flat; a 0.27 in wall (1.0044 in) does not; neither does exactly four."""
    assert _resolve(top_rail={"B": 1, "wall_nominal": 0.25}).rail.rect.B.m_as("inch") == 1
    message = _stops(Stop.MEMBER_RECT_WALL_LEAVES_NO_FLAT, resolve=True, top_rail={"B": 1, "wall_nominal": 0.27})
    assert message.startswith("Rect. tube 4 × 1 × 0.27 (custom): B = 1.000 in <= 4 t_des = 1.004 in")
    # A1085's design wall is the nominal wall: 4 x 0.25 = 1.0 in, exactly B.
    _stops(Stop.MEMBER_RECT_WALL_LEAVES_NO_FLAT, resolve=True,
           top_rail={"B": 1, "wall_nominal": 0.25, "grade": "A1085 Gr A"})


@pytest.mark.parametrize("table, expected", [
    ({"OD": 2.375}, "[top_rail] OD is given for shape = \"rectangular tube\", which takes H, B and wall_nominal."),
    ({"shape": "round tube", "OD": 2.375, "long_side": None},
     "[top_rail] H, B is given for shape = \"round tube\", which takes OD and wall_nominal."),
])
def test_a_dimension_of_the_other_shape_is_a_conflicting_input(table, expected):
    assert _stops(Stop.MEMBER_CUSTOM_KEYS_OF_ANOTHER_SHAPE, top_rail=table).startswith(expected)


@pytest.mark.parametrize("key", ["H", "B", "wall_nominal", "shape"])
def test_each_key_of_a_custom_rectangular_tube_is_required(key):
    assert f"[top_rail] is missing '{key}'" in _stops(Stop.FILE_MISSING_KEY, top_rail={key: None})


def test_a_designation_with_a_rectangular_tubes_dimensions_names_the_rectangular_tube():
    message = _stops(Stop.MEMBER_SECTION_WITH_CUSTOM_DIMENSIONS, top_rail={"section": "HSS4X2X1/8"})
    assert "or a custom rectangular tube (shape = \"rectangular tube\", H, B and wall_nominal), not both" in message


def test_a_custom_rectangular_tube_takes_the_rectangular_grades_and_not_a53():
    """S6-5: A53 is a pipe specification. Validation refuses the grade for
    the member's family, as it does for a database section."""
    reg = Registry()
    assert _resolve(top_rail={"grade": "A500 Gr C"}).project.top_rail.grade == "A500 Gr C"
    sec = _resolve(top_rail={"grade": "A53 Gr B"}).rail
    assert "A53 Gr B" not in materials.supported(sec.family)
    with pytest.raises(SectionStop) as stopped:
        materials.yield_stress(reg, "A53 Gr B", sec, "top rail")
    assert stopped.value.stop is Stop.GRADE_UNSUPPORTED
    assert str(stopped.value).startswith("top rail grade 'A53 Gr B': for custom rectangular tube this version supports")


def test_an_intermediate_rail_can_be_a_custom_rectangular_tube():
    own = {"same_as_top_rail": False, "shape": "rectangular tube", "H": 2, "B": 1, "wall_nominal": 0.083,
           "long_side": "horizontal"}
    m = _resolve(intermediate_rail=own, welds={"intermediate_rail_to_post": "1/8"})
    assert m.own is not None and m.own.label == "Rect. tube 2 × 1 × 0.083 (custom)"
    with pytest.raises(ProjectError) as stopped:
        project.from_dict(_raw(intermediate_rail={"H": 2, "B": 1}))
    assert stopped.value.stop is Stop.INTERMEDIATE_SAME_WITH_INPUTS


def test_a_custom_tube_classifies_and_bends_on_its_computed_values():
    """The flexure block reads the custom tube's computed ratios and prints
    them as computed, to four significant figures."""
    reg = Registry()
    sec = members.resolve(project.from_dict(_raw()), reg).rail
    sh, flags = Sheet(reg), []
    lim = rect_limits(sh, sec, "A500 Gr B")
    rect_axis_capacity(sh, lim, sec, "y", Unbraced(Sym("L", Q_(72, "inch")), "", lambda s: s.input("C_b", "C_b", 1.0, "")),
                       flags)
    flange = next(ln for ln in sh.lines if ln.key == "lambda_f_y")
    assert flange.value == sec.rect.h_t and "computed (design wall)" in flange.note
    assert flange.cite == shapes.CUSTOM
    assert len(flags) == 1 and f"h/t = {sec.rect.h_t:.4g}" in flags[0]


def test_the_reader_keeps_a_custom_rectangular_tubes_dimensions_as_entered():
    """The dimensions page echoes them as entered and as read (S6-14 item 6)."""
    rail = project.from_dict(_raw()).top_rail
    assert rail.H is not None and rail.B is not None and rail.wall_nominal is not None
    assert (rail.H.entered, rail.B.entered, rail.wall_nominal.entered) == ("4", "2", "1/8")
    assert rail.custom and rail.OD is None and rail.section == ""


def test_a_database_rectangular_hss_is_not_a_custom_tube():
    assert not shapes.section("HSS4X2X1/8").custom and shapes.section("HSS4X2X1/8").family == RECT_HSS
