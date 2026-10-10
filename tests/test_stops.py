"""Every stop has an id, a row in docs/brief/stops.md and a test (S5-9).

A stop is any place the tool refuses to compute and says why
(docs/brief/inputs.md, "Stops and supported combinations"). This file:

- triggers every stop: TRIGGERS holds one function per stop id, and
  test_stop_is_triggered runs each and checks the error carries that id;
- holds the code to docs/brief/stops.md, as tests/test_report.py holds the
  printed assumptions to output.md: every stop id in the code is in
  stops.md, every id in stops.md is in the code, and each row names the
  test that triggers it;
- holds the per-joint tables of section families in stops.md to the tables
  in joints.py, and gives each joint a stand-in family with no row.

So stops.md changes only on a calc branch, in the same commit as the code
it describes (CLAUDE.md, Git).
"""

import ast
import dataclasses
import re
from pathlib import Path

import pytest

from handrail import dimensions, engine, flexure, joints, post, project, shapes
from handrail.errors import InputError, SectionStop
from handrail.joints import ALLOWED, CHECK_3, CHECK_4B, CHECK_7, GROUPS, JOINTS
from handrail.project import ProjectError
from handrail.registry import Registry
from handrail.shapes import PIPE, RECT_HSS
from handrail.stops import Stop
from handrail.validate import validate
from test_registry import entry, write

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "handrail"
STOPS_MD = ROOT / "docs" / "brief" / "stops.md"
STAND_IN = "stand-in family"  # a family with no row in any joint's table

# ---------------------------------------------------------------------------
# One trigger per stop
# ---------------------------------------------------------------------------

TRIGGERS = {}


def trigger(stop: Stop):
    def register(fn):
        assert stop not in TRIGGERS, f"two triggers for {stop}"
        TRIGGERS[stop] = fn
        return fn
    return register


def _raw(**tables) -> dict:
    """A project that runs: Pipe2STD rail and post over 6'-0", no intermediate
    rail. Each keyword replaces or extends one table; None removes it."""
    raw = {
        "project": {"name": "stops"},
        "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
        "top_rail": {"section": "Pipe2STD"}, "post": {"section": "Pipe2STD"},
        "welds": {"rail_to_post": "1/8", "post_to_baseplate": "1/4"},
        "baseplate": {"B": 6, "N": 8}, "intermediate_rail": {"none": True},
    }
    for name, table in tables.items():
        if table is None:
            del raw[name]
        elif name == "intermediate_rail":
            raw[name] = table
        else:
            raw[name] = {**raw.get(name, {}), **table}
    return raw


def _load(**tables):
    return project.from_dict(_raw(**tables))


def _run(**tables):
    return engine.run(_load(**tables), Registry())


OWN = {"same_as_top_rail": False, "section": "Pipe1-1/4STD"}
OWN_WELD = {"intermediate_rail_to_post": "1/8"}


def _stand_in(monkeypatch, family, only=None):
    """Sections of another family: every section, or only the one labelled
    ``only``. Stand-ins for machinery tests; no project can enter one."""
    real = shapes.pipe

    def pipe(designation):
        sec = real(designation)
        return dataclasses.replace(sec, family=family) if only in (None, sec.label) else sec

    monkeypatch.setattr(shapes, "pipe", pipe)


def _fake(D_t):
    return dataclasses.replace(shapes.pipe("Pipe2STD"), D_t=D_t, label="FakePipe")


# -- the project file -------------------------------------------------------

@trigger(Stop.FILE_NOT_FOUND)
def _(tmp_path, monkeypatch):
    project.load(tmp_path / "no-such-project.toml")


@trigger(Stop.FILE_INVALID_TOML)
def _(tmp_path, monkeypatch):
    bad = tmp_path / "bad.toml"
    bad.write_text("[project\nname = ", encoding="utf-8")
    project.load(bad)


@trigger(Stop.FILE_UNKNOWN_KEY)
def _(tmp_path, monkeypatch):
    _load(top_rail={"sektion": "Pipe2STD"})


@trigger(Stop.FILE_NOT_A_TABLE)
def _(tmp_path, monkeypatch):
    _load(deflection={"rail": 5})


@trigger(Stop.FILE_MISSING_KEY)
def _(tmp_path, monkeypatch):
    _load(post=None)


@trigger(Stop.FILE_NOT_TEXT)
def _(tmp_path, monkeypatch):
    _load(project={"name": 5})


@trigger(Stop.FILE_NOT_A_TEXT_LIST)
def _(tmp_path, monkeypatch):
    _load(project={"references": "one"})


@trigger(Stop.FILE_NOT_A_BOOLEAN)
def _(tmp_path, monkeypatch):
    _load(intermediate_rail={"none": "true"})


@trigger(Stop.FILE_NOT_A_NUMBER)
def _(tmp_path, monkeypatch):
    _load(loads={"concentrated_lb": "200"})


@trigger(Stop.FILE_NOT_POSITIVE)
def _(tmp_path, monkeypatch):
    _load(loads={"uniform_plf": 0})


@trigger(Stop.FILE_NOT_A_DIMENSION)
def _(tmp_path, monkeypatch):
    _load(geometry={"span": True})


@trigger(Stop.FILE_DIMENSION_NOT_POSITIVE)
def _(tmp_path, monkeypatch):
    _load(geometry={"span": 0})


@trigger(Stop.GEOMETRY_BASEPLATE_NOT_BELOW_POST_HEIGHT)
def _(tmp_path, monkeypatch):
    _load(geometry={"baseplate_thickness": 42})


@trigger(Stop.LOADS_EXEMPTION_NEEDS_STATEMENT)
def _(tmp_path, monkeypatch):
    _load(loads={"uniform_exemption": {"applies": True}})


@trigger(Stop.INTERMEDIATE_NONE_AND_SAME)
def _(tmp_path, monkeypatch):
    _load(intermediate_rail={"none": True, "same_as_top_rail": True})


@trigger(Stop.INTERMEDIATE_NONE_WITH_INPUTS)
def _(tmp_path, monkeypatch):
    _load(intermediate_rail={"none": True, "section": "Pipe1-1/4STD"})


@trigger(Stop.INTERMEDIATE_SAME_WITH_INPUTS)
def _(tmp_path, monkeypatch):
    _load(intermediate_rail={"section": "Pipe1-1/4STD"})


@trigger(Stop.INTERMEDIATE_OWN_NEEDS_SECTION)
def _(tmp_path, monkeypatch):
    _load(intermediate_rail={"same_as_top_rail": False})


@trigger(Stop.INTERMEDIATE_OWN_NEEDS_WELD_SIZE)
def _(tmp_path, monkeypatch):
    _load(intermediate_rail=OWN)


# -- a dimension as typed: each reaches the engineer through the project file --

@trigger(Stop.DIMENSION_EMPTY)
def _(tmp_path, monkeypatch):
    _load(geometry={"span": "  "})


@trigger(Stop.DIMENSION_NEGATIVE)
def _(tmp_path, monkeypatch):
    _load(geometry={"span": "-6'"})


@trigger(Stop.DIMENSION_UNREADABLE)
def _(tmp_path, monkeypatch):
    _load(geometry={"span": "six feet"})


@trigger(Stop.DIMENSION_ZERO_DENOMINATOR)
def _(tmp_path, monkeypatch):
    _load(welds={"rail_to_post": "1/0"})


@trigger(Stop.DIMENSION_INCHES_12_OR_MORE)
def _(tmp_path, monkeypatch):
    _load(geometry={"span": "5' 13\""})


# -- sections, grades and the baseplate --------------------------------------

@trigger(Stop.SECTION_NOT_FOUND)
def _(tmp_path, monkeypatch):
    _run(top_rail={"section": "Pipe99STD"})


@trigger(Stop.GRADE_UNSUPPORTED)
def _(tmp_path, monkeypatch):
    _run(post={"grade": "A36"})


@trigger(Stop.GRADE_POST_FU_FY_BELOW_LIMIT)
def _(tmp_path, monkeypatch):
    reg = Registry()
    fu = reg.entries["material.A53_GrB.Fu"]
    reg.entries[fu.id] = dataclasses.replace(fu, value=40)  # a stand-in Fu: 40/35 is below 1.20
    validate(_load(), reg)


@trigger(Stop.WELD_ELECTRODE_UNSUPPORTED)
def _(tmp_path, monkeypatch):
    _run(welds={"electrode": "E60XX"})


@trigger(Stop.BASEPLATE_GRADE_UNSUPPORTED)
def _(tmp_path, monkeypatch):
    _run(baseplate={"grade": "A572 Gr 50"})


@trigger(Stop.BASEPLATE_SMALLER_THAN_POST)
def _(tmp_path, monkeypatch):
    _run(baseplate={"B": 2})


@trigger(Stop.SECTION_POST_WIDER_THAN_RAIL)
def _(tmp_path, monkeypatch):
    _run(top_rail={"section": "Pipe1-1/2STD"})


@trigger(Stop.SECTION_INTERMEDIATE_WIDER_THAN_POST)
def _(tmp_path, monkeypatch):
    _run(intermediate_rail={"same_as_top_rail": False, "section": "Pipe2-1/2STD"}, welds=OWN_WELD)


# -- the per-joint tables ----------------------------------------------------

@trigger(Stop.JOINT_CHECK3_NOT_SUPPORTED)
def _(tmp_path, monkeypatch):
    _stand_in(monkeypatch, RECT_HSS)
    _run()


@trigger(Stop.JOINT_CHECK3_NO_CELL)
def _(tmp_path, monkeypatch):
    _stand_in(monkeypatch, STAND_IN)
    _run()


@trigger(Stop.JOINT_CHECK4B_NOT_SUPPORTED)
def _(tmp_path, monkeypatch):
    _stand_in(monkeypatch, RECT_HSS, only="Pipe1-1/4STD")
    _run(intermediate_rail=OWN, welds=OWN_WELD)


@trigger(Stop.JOINT_CHECK4B_NO_CELL)
def _(tmp_path, monkeypatch):
    _stand_in(monkeypatch, STAND_IN, only="Pipe1-1/4STD")
    _run(intermediate_rail=OWN, welds=OWN_WELD)


@trigger(Stop.JOINT_CHECK7_NOT_SUPPORTED)
def _(tmp_path, monkeypatch):
    # Inside the weld code, when a calc is computed without validation.
    _stand_in(monkeypatch, RECT_HSS)
    engine.compute(_load(), Registry())


@trigger(Stop.JOINT_CHECK7_NO_CELL)
def _(tmp_path, monkeypatch):
    _stand_in(monkeypatch, STAND_IN)
    engine.compute(_load(), Registry())


# -- a section the checks will not check ---------------------------------------

@trigger(Stop.SECTION_BEYOND_F8_LIMIT)
def _(tmp_path, monkeypatch):
    flexure.flexural_capacity(Registry(), _fake(400), "A53 Gr B")


@trigger(Stop.SECTION_SLENDER_IN_FLEXURE)
def _(tmp_path, monkeypatch):
    flexure.flexural_capacity(Registry(), _fake(300), "A53 Gr B")


@trigger(Stop.SECTION_SLENDER_IN_COMPRESSION)
def _(tmp_path, monkeypatch):
    post.compression_capacity(Registry(), _load(), _fake(100))


@trigger(Stop.CHECK5_SECOND_ORDER_NOT_NEGLIGIBLE)
def _(tmp_path, monkeypatch):
    # A 103 lb/ft rail over 12'-0" on a Pipe2STD post: alpha Pr/Pe is about 0.087.
    _run(top_rail={"section": "Pipe26STD"}, geometry={"span": "12'-0\""})


# -- the code-value registry -------------------------------------------------

@trigger(Stop.REGISTRY_FILE_NOT_FOUND)
def _(tmp_path, monkeypatch):
    Registry(tmp_path / "no-such-registry.toml")


@trigger(Stop.REGISTRY_INVALID_TOML)
def _(tmp_path, monkeypatch):
    bad = tmp_path / "reg.toml"
    bad.write_text("review = [", encoding="utf-8")
    Registry(bad)


@trigger(Stop.REGISTRY_MISSING_FIELD)
def _(tmp_path, monkeypatch):
    Registry(write(tmp_path, ["a"], entry("a").replace('cite = "AISC 360-22 §F1"\n', "")))


@trigger(Stop.REGISTRY_BAD_STATUS)
def _(tmp_path, monkeypatch):
    Registry(write(tmp_path, ["a"], entry("a", status="checked")))


@trigger(Stop.REGISTRY_VERIFIED_WITHOUT_SIGNOFF)
def _(tmp_path, monkeypatch):
    Registry(write(tmp_path, [], entry("a", status="verified")))


@trigger(Stop.REGISTRY_DRAFTED_WITH_SIGNOFF)
def _(tmp_path, monkeypatch):
    Registry(write(tmp_path, ["a"], entry("a", by="MM")))


@trigger(Stop.REGISTRY_DUPLICATE_ID)
def _(tmp_path, monkeypatch):
    Registry(write(tmp_path, ["a"], entry("a"), entry("a")))


@trigger(Stop.REGISTRY_NO_REVIEW_LIST)
def _(tmp_path, monkeypatch):
    p = tmp_path / "reg.toml"
    p.write_text(entry("a"), encoding="utf-8")
    Registry(p)


@trigger(Stop.REGISTRY_DUPLICATE_REVIEW_ID)
def _(tmp_path, monkeypatch):
    Registry(write(tmp_path, ["a", "a"], entry("a")))


@trigger(Stop.REGISTRY_REVIEW_LIST_MISMATCH)
def _(tmp_path, monkeypatch):
    Registry(write(tmp_path, ["a"], entry("a"), entry("b")))


@trigger(Stop.REGISTRY_MISSING_ENTRY)
def _(tmp_path, monkeypatch):
    Registry().get("aisc360.nonexistent")


@trigger(Stop.REGISTRY_NOT_A_QUANTITY)
def _(tmp_path, monkeypatch):
    Registry().get("material.grades.pipe").quantity  # a list of grade names, not a number


@trigger(Stop.REGISTRY_CITE_NAMES_NO_EQUATION)
def _(tmp_path, monkeypatch):
    Registry().get("material.steel.E").equation_number  # its cite names a section, not an equation


@pytest.mark.parametrize("stop", list(Stop), ids=lambda s: s.value)
def test_stop_is_triggered(stop, tmp_path, monkeypatch):
    """The stop's trigger refuses to compute, and the error carries its id."""
    assert stop in TRIGGERS, f"no test triggers the stop {stop.value!r}; add one above (S5-9)"
    with pytest.raises(InputError) as stopped:
        TRIGGERS[stop](tmp_path, monkeypatch)
    assert stopped.value.stop is stop, f"triggered {stopped.value.stop.value!r}: {stopped.value}"
    assert str(stopped.value).strip(), "a stop says why"


# ---------------------------------------------------------------------------
# The code is held to docs/brief/stops.md
# ---------------------------------------------------------------------------

ROW = re.compile(r"^\| `([a-zA-Z0-9_.]+)` \|(.*)\|\s*$")


def _stops_md() -> str:
    return STOPS_MD.read_text(encoding="utf-8")


def _rows() -> dict[str, list[str]]:
    """stop id -> the row's other cells (condition, decision, test)."""
    rows = {}
    for line in _stops_md().splitlines():
        m = ROW.match(line)
        if m:
            assert m.group(1) not in rows, f"stops.md lists {m.group(1)!r} twice"
            rows[m.group(1)] = [cell.strip() for cell in m.group(2).split("|")]
    return rows


def test_every_stop_in_the_code_is_in_stops_md_and_every_stop_there_is_in_the_code():
    in_code, in_doc = {s.value for s in Stop}, set(_rows())
    assert not in_code - in_doc, f"stops in the code with no row in docs/brief/stops.md: {sorted(in_code - in_doc)}"
    assert not in_doc - in_code, f"stops in docs/brief/stops.md that the code does not have: {sorted(in_doc - in_code)}"


def test_every_row_of_stops_md_gives_its_condition_its_decision_and_the_test_that_triggers_it():
    triggered = {s.value for s in TRIGGERS}
    for stop_id, cells in _rows().items():
        assert len(cells) == 3 and all(cells), f"stops.md {stop_id}: a row is id, condition, decision, test"
        assert stop_id in triggered, f"stops.md lists {stop_id!r}, which no test triggers"
        assert cells[2] == f"`test_stop_is_triggered[{stop_id}]`", (
            f"stops.md {stop_id}: the test column must name the test that triggers it, "
            f"`test_stop_is_triggered[{stop_id}]` in tests/test_stops.py"
        )


def test_every_trigger_is_for_a_stop_the_code_has():
    assert set(TRIGGERS) == set(Stop)


ERROR_CLASSES = {"InputError", "ProjectError", "DimensionError", "RegistryError", "MissingEntry", "ShapeNotFound",
                 "SectionStop", "error"}  # "error": the class a joint is told to raise (joints.py)


def test_every_error_that_stops_a_calc_is_raised_with_a_stop_id():
    """No stop without an id: every raise of an input error in src/ passes
    ``stop=``. (InputError also requires it when the error is built.)"""
    missing = []
    for path in sorted(SRC.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not (isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call)):
                continue
            f = node.exc.func
            name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
            if name in ERROR_CLASSES and not any(k.arg == "stop" for k in node.exc.keywords):
                missing.append(f"{path.name}:{node.lineno}")
    assert not missing, f"stops raised with no id: {missing}"


def test_every_stop_id_is_used_by_the_code():
    """No id without a stop: each member of Stop is named somewhere in src/
    outside its own definition."""
    used = set()
    for path in sorted(SRC.glob("*.py")):
        if path.name == "stops.py":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "Stop":
                used.add(node.attr)
    unused = sorted(s.name for s in Stop if s.name not in used)
    assert not unused, f"stop ids no code raises: {unused}"


# ---------------------------------------------------------------------------
# The per-joint tables of section families
# ---------------------------------------------------------------------------

def _section_of(heading: str) -> str:
    text = _stops_md()
    assert heading in text, f"docs/brief/stops.md has no heading {heading!r}"
    return text.split(heading, 1)[1].split("\n#", 1)[0]


@pytest.mark.parametrize("joint", JOINTS, ids=lambda j: j.name.split(" (")[0])
def test_the_joint_table_in_stops_md_is_the_table_in_the_code(joint):
    """Cell for cell: stops.md prints each joint's table under a heading
    that is the joint's name, exactly as joints.markdown_table renders the
    data the code decides by."""
    assert joints.markdown_table(joint) in _section_of(f"### {joint.name}"), (
        f"docs/brief/stops.md, {joint.name}: the table does not match joints.py. It should read:\n\n"
        f"{joints.markdown_table(joint)}"
    )


def test_families_printed_in_one_group_share_every_cell():
    """The tables print one row per group of families (rectangular HSS with
    custom rectangular tube; the two solid bars), which is only right while
    every family in a group has the same cells."""
    families = [f for g in GROUPS for f in g]
    for group in GROUPS:
        first = group[0]
        for other in group[1:]:
            for f in families:
                assert CHECK_3.table[(first, f)] == CHECK_3.table[(other, f)]
                assert CHECK_3.table[(f, first)] == CHECK_3.table[(f, other)]
            assert CHECK_7.table[first] == CHECK_7.table[other]
    assert set(CHECK_3.table) == {(c, b) for c in families for b in families}
    assert set(CHECK_7.table) == set(families)


def test_the_only_allowed_pair_is_pipe_on_pipe():
    """Step 1 of slice 5: the tables allow what the tool computed before
    they existed, and nothing else. Step 5 sets the round HSS and custom
    round tube cells to allowed, here and in stops.md, in the same commit."""
    for joint in (CHECK_3, CHECK_4B):
        assert {pair for pair, cell in joint.table.items() if cell.allowed} == {(PIPE, PIPE)}
        assert joint.cell(PIPE, PIPE) is ALLOWED
    assert {family for family, cell in CHECK_7.table.items() if cell.allowed} == {PIPE}


def test_a_stop_cell_names_the_member_whose_family_brings_the_stop(monkeypatch):
    """The messages W7 and S4-12 have given since slices 3 and 4, word for
    word, followed by the joint, both families and the slice (S5-1)."""
    w7 = ("is not a round hollow section. The stated assumption that the rail wall's local strength at the post "
          "is not checked has been decided only for a round hollow rail on a round hollow post, not for this "
          "section.")
    cases = [  # (the section given the stand-in family, the project, the message)
        ("Pipe2STD", {"post": {"section": "Pipe1-1/2STD"}},
         f"top rail Pipe2STD (rectangular HSS) {w7} Check 3 joint (top rail as chord, post as branch): rectangular "
         f"HSS as the chord with AISC pipe as the branch is not supported until slice 6 (S5-1)."),
        ("Pipe1-1/2STD", {"post": {"section": "Pipe1-1/2STD"}},
         f"post Pipe1-1/2STD (rectangular HSS) {w7} Check 3 joint (top rail as chord, post as branch): AISC pipe as "
         f"the chord with rectangular HSS as the branch is not supported until slice 6 (S5-1)."),
        ("Pipe1-1/4STD", {"intermediate_rail": OWN, "welds": OWN_WELD},
         f"intermediate rail Pipe1-1/4STD (rectangular HSS) {w7} Check 4b joint (post as chord, intermediate rail "
         f"as branch): AISC pipe as the chord with rectangular HSS as the branch is not supported until slice 6 "
         f"(S5-1)."),
    ]
    for label, tables, message in cases:
        with monkeypatch.context() as m:
            _stand_in(m, RECT_HSS, only=label)
            with pytest.raises(ProjectError) as stopped:
                _run(**tables)
        assert str(stopped.value) == message


def test_a_stand_in_family_with_no_row_stops_at_each_of_the_three_joints(monkeypatch):
    """Binding (S5-9; Micah, 2026-10-09): a pair of families with no cell in
    a joint's table stops, with a message naming the joint and both
    families. Allowed means listed as allowed; nothing unlisted is computed.

    Each joint is reached through validate(), with the stand-in family on
    one member only. For the Check 7 joint the stand-in is first given
    cells at the other two joints, so the post reaches the baseplate table,
    where it has no row."""
    listed = "The tool computes only the combinations listed as allowed (S5-9)."

    # Check 3 joint: a stand-in post under a pipe rail.
    with monkeypatch.context() as m:
        _stand_in(m, STAND_IN, only="Pipe1-1/2STD")
        with pytest.raises(ProjectError) as stopped:
            _run(post={"section": "Pipe1-1/2STD"})
    assert stopped.value.stop is Stop.JOINT_CHECK3_NO_CELL
    assert str(stopped.value) == (
        "Check 3 joint (top rail as chord, post as branch): there is no decision for AISC pipe as the chord "
        f"(top rail Pipe2STD) with stand-in family as the branch (post Pipe1-1/2STD). {listed}")

    # Check 4b joint: a stand-in intermediate rail on a pipe post.
    with monkeypatch.context() as m:
        _stand_in(m, STAND_IN, only="Pipe1-1/4STD")
        with pytest.raises(ProjectError) as stopped:
            _run(intermediate_rail=OWN, welds=OWN_WELD)
    assert stopped.value.stop is Stop.JOINT_CHECK4B_NO_CELL
    assert str(stopped.value) == (
        "Check 4b joint (post as chord, intermediate rail as branch): there is no decision for AISC pipe as the "
        f"chord (post Pipe2STD) with stand-in family as the branch (intermediate rail Pipe1-1/4STD). {listed}")

    # Check 7 joint: a stand-in post that the other two joints allow.
    with monkeypatch.context() as m:
        _stand_in(m, STAND_IN, only="Pipe1-1/2STD")
        for pair in ((PIPE, STAND_IN), (STAND_IN, PIPE), (STAND_IN, STAND_IN)):
            m.setitem(joints.CHORD_AND_BRANCH, pair, ALLOWED)
        with pytest.raises(ProjectError) as stopped:
            _run(post={"section": "Pipe1-1/2STD"}, intermediate_rail=OWN, welds=OWN_WELD)
    assert stopped.value.stop is Stop.JOINT_CHECK7_NO_CELL
    assert str(stopped.value) == (
        "Check 7 joint (post on the baseplate): there is no decision for a stand-in family post (Pipe1-1/2STD) "
        f"on an A36 plate baseplate. {listed}")
    assert (PIPE, STAND_IN) not in joints.CHORD_AND_BRANCH  # the stand-in cells are gone again


def test_the_weld_code_stops_at_the_check_7_joint_when_a_calc_skips_validation(monkeypatch):
    """compute() without validate(): the Check 7 weld asks the same table,
    so an unlisted post is still never computed."""
    _stand_in(monkeypatch, STAND_IN)
    with pytest.raises(SectionStop) as stopped:
        engine.compute(_load(), Registry())
    assert stopped.value.stop is Stop.JOINT_CHECK7_NO_CELL
    assert "Check 7 joint (post on the baseplate)" in str(stopped.value) and STAND_IN in str(stopped.value)


def test_a_dimension_stop_keeps_its_own_id_through_the_project_file():
    """The project reader adds where the dimension was typed; the stop is still the dimension's."""
    with pytest.raises(dimensions.DimensionError) as direct:
        dimensions.parse("six feet")
    with pytest.raises(ProjectError) as through_file:
        _load(geometry={"span": "six feet"})
    assert direct.value.stop is through_file.value.stop is Stop.DIMENSION_UNREADABLE
    assert str(through_file.value) == f"[geometry] span: {direct.value}"
