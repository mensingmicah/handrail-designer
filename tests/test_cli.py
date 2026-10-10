"""The one command, end to end, and the project file reader."""

import copy
import dataclasses
import tomllib
from pathlib import Path

import pytest

from handrail import cli, project, shapes
from handrail.registry import Registry
from handrail.validate import validate

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "slice-1.toml"


def test_example_project_produces_pdf(tmp_path, capsys):
    out = tmp_path / "calc.pdf"
    assert cli.main(["calc", str(EXAMPLE), "-o", str(out)]) == 0
    assert out.read_bytes()[:4] == b"%PDF"


def test_default_output_sits_beside_the_project_file(tmp_path):
    p = tmp_path / "job.toml"
    p.write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    assert cli.main(["calc", str(p)]) == 0
    assert (tmp_path / "job.pdf").exists()


@pytest.mark.parametrize(
    "edit, message",
    [
        (('span = "6\'-0\\""', 'span = "5 6"'), "not a dimension I can read"),
        (('section = "Pipe2STD"', 'section = "Pipe99STD"'), "Pipe99STD"),
        (('grade = "A53 Gr B"', 'grade = "A36"'), "A53 Gr B only"),
        (("applies = false", "applies = true"), "needs a statement"),
    ],
)
def test_input_errors_are_one_line_messages(tmp_path, capsys, edit, message):
    text = EXAMPLE.read_text(encoding="utf-8")
    assert edit[0] in text
    p = tmp_path / "bad.toml"
    p.write_text(text.replace(edit[0], edit[1]), encoding="utf-8")
    assert cli.main(["calc", str(p)]) == 1
    err = capsys.readouterr().err
    assert err.startswith("error:") and message in err and "Traceback" not in err


def test_project_file_reads_every_field():
    proj = project.load(EXAMPLE)
    assert proj.span.value.m_as("inch") == 72
    assert proj.top_rail.section == "Pipe2STD"
    assert proj.loads.concentrated is None and not proj.loads.uniform_exempt
    assert proj.rail_deflection.ratio == 120 and not proj.rail_deflection.bypass
    assert proj.post.section == "Pipe2STD" and proj.post.grade == "A53 Gr B"
    assert proj.post_height.value.m_as("inch") == 42
    assert proj.baseplate_thickness.value.m_as("inch") == 0.5
    assert proj.post_deflection.ratio == 60 and not proj.post_deflection.bypass


def test_post_deflection_limit_defaults_to_60_when_left_out(tmp_path):
    text = EXAMPLE.read_text(encoding="utf-8")
    block = "[deflection.post]\nlimit_L_over = 60"
    assert block in text
    p = tmp_path / "no-post-limit.toml"
    p.write_text(text.replace(block, "[deflection.post]"), encoding="utf-8")
    assert project.load(p).post_deflection.ratio == 60


# The example's geometry lines, as written in examples/slice-1.toml.
H = 'post_height = "3\'-6\\""'
TP = 'baseplate_thickness = "1/2"'


@pytest.mark.parametrize(
    "old, new, message",
    [
        # t_p must be less than h, so t_p = h is refused as well as t_p > h.
        (TP, 'baseplate_thickness = "3\'-6\\""',
         "baseplate_thickness (3'-6\") must be less than post_height (3'-6\")"),
        (TP, "baseplate_thickness = 48", "baseplate_thickness (48) must be less than post_height"),
        (TP, "baseplate_thickness = 0", "baseplate_thickness must be greater than zero"),
        (H, "post_height = 0", "post_height must be greater than zero"),
        (H, "post_height = true", "'geometry.post_height' must be a dimension"),
        (H, 'post_height = "3 6"', "post_height: '3 6' is not a dimension"),
        # The post is required (D9).
        (H, "", "[geometry] is missing 'post_height'"),
        (TP, "", "[geometry] is missing 'baseplate_thickness'"),
        ("[post]", "[posts]", "unknown table 'posts'"),
        # Post grade uses the rail's grade check, naming the member.
        ('[post]\nsection = "Pipe2STD"      # AISC designation (AISC Shapes Database v16.0)\ngrade = "A53 Gr B"',
         '[post]\nsection = "Pipe2STD"\ngrade = "A500 Gr B"', "post grade 'A500 Gr B'"),
        ("limit_L_over = 60", "limit_L_over = 0", "deflection.post.limit_L_over' must be greater than zero"),
        ("limit_L_over = 60", "limit_over = 60", "unknown key 'deflection.post.limit_over'"),
    ],
)
def test_post_and_geometry_input_errors(tmp_path, capsys, old, new, message):
    code, err = _run_with(tmp_path, capsys, old, new)
    assert code == 1
    assert err.startswith("error:") and message in err, err


def test_missing_post_table_is_refused(tmp_path, capsys):
    text = EXAMPLE.read_text(encoding="utf-8")
    start = text.index("[post]")
    end = text.index("[loads]")
    p = tmp_path / "no-post.toml"
    p.write_text(text[:start] + text[end:], encoding="utf-8")
    assert cli.main(["calc", str(p)]) == 1
    assert "project file: [top level] is missing 'post'" in capsys.readouterr().err


def _run_with(tmp_path, capsys, old, new):
    text = EXAMPLE.read_text(encoding="utf-8")
    assert old in text, old
    p = tmp_path / "edited.toml"
    p.write_text(text.replace(old, new), encoding="utf-8")
    code = cli.main(["calc", str(p)])
    return code, capsys.readouterr().err


@pytest.mark.parametrize(
    "old, new, message",
    [
        # Text is not a boolean: "false" in quotes must not exempt or bypass anything.
        ("applies = false", 'applies = "false"', "loads.uniform_exemption.applies' must be true or false"),
        ("bypass = false", 'bypass = "false"', "deflection.rail.bypass' must be true or false"),
        # Misspelled keys must not fall back silently to the default or code value.
        ("# concentrated_lb = 200", "concentrated_lbs = 250", "unknown key 'loads.concentrated_lbs'"),
        ("limit_L_over = 120", "limit_L_ovr = 240", "unknown key 'deflection.rail.limit_L_ovr'"),
        ('grade = "A53 Gr B"', 'grde = "A53 Gr B"', "unknown key 'top_rail.grde'"),
        ("[top_rail]", "[top_rails]", "unknown table 'top_rails'"),
        # Overrides must be positive numbers.
        ("# concentrated_lb = 200", "concentrated_lb = -200", "must be greater than zero"),
        ("# uniform_plf = 50", "uniform_plf = 0", "must be greater than zero"),
        ("# concentrated_lb = 200", 'concentrated_lb = "250"', "must be a number without quotes"),
        ("# uniform_plf = 50", "uniform_plf = true", "must be a number without quotes"),
        ("limit_L_over = 120", "limit_L_over = 0", "must be greater than zero"),
    ],
)
def test_project_file_typos_stop_with_a_message_naming_the_key(tmp_path, capsys, old, new, message):
    code, err = _run_with(tmp_path, capsys, old, new)
    assert code == 1
    assert err.startswith("error:") and message in err, err


def test_overrides_reach_the_calc_with_units(tmp_path):
    text = EXAMPLE.read_text(encoding="utf-8")
    text = text.replace("# concentrated_lb = 200", "concentrated_lb = 250")
    text = text.replace("# uniform_plf = 50", "uniform_plf = 60")
    p = tmp_path / "over.toml"
    p.write_text(text, encoding="utf-8")
    proj = project.load(p)
    assert proj.loads.concentrated.m_as("lbf") == 250
    assert proj.loads.uniform.m_as("lbf/inch") == pytest.approx(5.0)


@pytest.mark.parametrize("name", ["case-01.toml", "case-02.toml"])
def test_hand_and_verification_tables_are_allowed_in_a_case_file(name):
    case = Path(__file__).resolve().parent / "cases" / name
    assert project.load(case).top_rail.section == "Pipe1-1/2STD"


# ---------------------------------------------------------------------------
# One input-error class, and SCHEMA against the parser (issue #4, items 4 and 6)
# ---------------------------------------------------------------------------


def test_every_input_error_derives_from_the_one_class_the_cli_catches():
    from handrail.errors import SectionStop
    from handrail.dimensions import DimensionError
    from handrail.errors import InputError
    from handrail.registry import MissingEntry, RegistryError
    from handrail.shapes import ShapeNotFound

    for cls in (project.ProjectError, RegistryError, MissingEntry, SectionStop, DimensionError, ShapeNotFound):
        assert issubclass(cls, InputError), cls.__name__


def test_unknown_shape_message_prints_without_quotes(tmp_path, capsys):
    # ShapeNotFound used to be a KeyError, whose message printed inside quotes.
    code, err = _run_with(tmp_path, capsys, 'section = "Pipe2STD"', 'section = "Pipe99STD"')
    assert code == 1
    assert err.startswith("error: 'Pipe99STD' is not an AISC pipe"), err


class _Tracking(dict):
    """A dict that records every key read from it, nested tables included."""

    def __init__(self, raw, where, log):
        super().__init__({k: _Tracking(v, f"{where}{k}.", log) if isinstance(v, dict) else v
                          for k, v in raw.items()})
        self._where, self._log = where, log

    def __getitem__(self, key):
        self._log.add(self._where + key)
        return super().__getitem__(key)

    def get(self, key, default=None):
        self._log.add(self._where + key)
        return super().get(key, default)


def _schema_keys(schema, where=""):
    for key, sub in schema.items():
        if sub == "ignored":
            continue
        if isinstance(sub, dict):
            yield f"{where}{key}"
            yield from _schema_keys(sub, f"{where}{key}.")
        else:
            yield f"{where}{key}"


def _full_project_files():
    """Project files that between them give every key SCHEMA allows. No one
    file can: none = true conflicts with the intermediate rail's own inputs
    (S4-1), so one file has its own section and the other has none."""

    raw = tomllib.loads(EXAMPLE.read_text(encoding="utf-8"))
    raw["loads"].update(concentrated_lb=250, uniform_plf=60, component_lb=150)
    raw["project"].update(references=["Sheet A-501"], assumptions=["Extra."])
    none = copy.deepcopy(raw)
    raw["intermediate_rail"] = {"same_as_top_rail": False, "section": "Pipe1-1/4STD", "grade": "A53 Gr B"}
    raw["welds"]["intermediate_rail_to_post"] = "1/8"
    raw["deflection"]["intermediate_rail"] = {"limit_L_over": 120, "bypass": False}
    none["intermediate_rail"] = {"same_as_top_rail": False, "none": True}
    return raw, none


def test_the_parser_reads_every_key_schema_allows_and_no_other():
    """SCHEMA and from_dict list the same keys separately (issue #4, item 6). A key
    in SCHEMA but never read would be accepted and silently ignored; a key read
    but not in SCHEMA would be refused before it could be read."""
    files = _full_project_files()
    schema = set(_schema_keys(project.SCHEMA))
    given = set().union(*(_schema_keys(raw) for raw in files))
    assert given == schema, f"the test's project files must give every SCHEMA key: {sorted(schema ^ given)}"
    log: set[str] = set()
    for raw in files:
        project.from_dict(_Tracking(raw, "", log))
    assert not schema - log, f"in SCHEMA, never read: {sorted(schema - log)}"
    assert not log - schema, f"read, not in SCHEMA: {sorted(log - schema)}"


def test_left_out_optional_keys_take_the_dataclass_defaults():
    """Issue #4, item 5: each default is stated once, on its dataclass."""

    raw = tomllib.loads(EXAMPLE.read_text(encoding="utf-8"))
    for table in ("loads", "deflection", "intermediate_rail"):
        del raw[table]
    for key in ("phase", "description", "references", "assumptions"):
        del raw["project"][key]
    proj = project.from_dict(raw)
    assert proj.loads == project.Loads()
    assert proj.rail_deflection == project.RAIL_DEFLECTION
    assert proj.post_deflection == project.POST_DEFLECTION
    assert proj.intermediate_rail == project.IntermediateRail()
    assert proj.info == project.ProjectInfo(name=raw["project"]["name"])


def test_a_partial_deflection_table_keeps_the_members_own_default_ratio():
    raw = tomllib.loads(EXAMPLE.read_text(encoding="utf-8"))
    raw["deflection"] = {"rail": {"bypass": True}, "post": {"bypass": True}}
    proj = project.from_dict(raw)
    assert proj.rail_deflection == project.DeflectionLimit(ratio=120, bypass=True)
    assert proj.post_deflection == project.DeflectionLimit(ratio=60, bypass=True)


# ---------------------------------------------------------------------------
# Slice 3: weld and baseplate inputs, and validation (W5, W7, W8, W12)
# ---------------------------------------------------------------------------


def test_weld_sizes_and_defaults_are_read():
    proj = project.load(EXAMPLE)
    assert proj.welds.rail_to_post.value.m_as("inch") == 0.125
    assert proj.welds.post_to_baseplate.value.m_as("inch") == 0.25
    assert proj.welds.post_to_baseplate.normalized == '1/4"'
    assert proj.welds.electrode == "E70XX" and proj.baseplate.grade == "A36"


def test_electrode_and_baseplate_grade_default_when_left_out(tmp_path):
    text = EXAMPLE.read_text(encoding="utf-8")
    for line in ('electrode = "E70XX"', 'grade = "A36"'):
        assert line in text
        text = text.replace(line, "")
    p = tmp_path / "defaults.toml"
    p.write_text(text, encoding="utf-8")
    proj = project.load(p)
    assert proj.welds.electrode == "E70XX" and proj.baseplate.grade == "A36"


WELD = 'post_to_baseplate = "1/4"'


@pytest.mark.parametrize(
    "old, new, message",
    [
        # Sizes are required, with no default (W12).
        (WELD, "", "[welds] is missing 'post_to_baseplate'"),
        ('rail_to_post = "1/8"', "", "[welds] is missing 'rail_to_post'"),
        ("[welds]", "[weld]", "unknown table 'weld'"),
        (WELD, 'post_to_baseplate = "1/4 in fillet"', "post_to_baseplate: '1/4 in fillet' is not a dimension"),
        (WELD, "post_to_baseplate = 0", "post_to_baseplate must be greater than zero"),
        # E70XX and A36 only (W12).
        ('electrode = "E70XX"', 'electrode = "E60XX"', "[welds] electrode 'E60XX': this version supports E70XX only"),
        ('grade = "A36"', 'grade = "A572 Gr 50"', "[baseplate] grade 'A572 Gr 50': this version supports A36 only"),
        ('grade = "A36"', 'thickness = "1/2"', "unknown key 'baseplate.thickness'"),
    ],
)
def test_weld_and_baseplate_input_errors(tmp_path, capsys, old, new, message):
    code, err = _run_with(tmp_path, capsys, old, new)
    assert code == 1
    assert err.startswith("error:") and message in err, err


def test_missing_welds_table_is_refused(tmp_path, capsys):
    text = EXAMPLE.read_text(encoding="utf-8")
    start, end = text.index("[welds]"), text.index("[loads]")
    p = tmp_path / "no-welds.toml"
    p.write_text(text[:start] + text[end:], encoding="utf-8")
    assert cli.main(["calc", str(p)]) == 1
    assert "project file: [top level] is missing 'welds'" in capsys.readouterr().err


def test_post_wider_than_rail_stops_naming_both_ods(tmp_path, capsys):
    # W8: Pipe2STD post (OD 2.375 in) under a Pipe1-1/2STD rail (OD 1.900 in).
    text = EXAMPLE.read_text(encoding="utf-8")
    old = '[top_rail]\nsection = "Pipe2STD"'
    assert old in text
    p = tmp_path / "wide-post.toml"
    p.write_text(text.replace(old, '[top_rail]\nsection = "Pipe1-1/2STD"'), encoding="utf-8")
    assert cli.main(["calc", str(p)]) == 1
    err = capsys.readouterr().err
    assert ("The post (Pipe2STD, OD 2.375 in) is wider than the top rail (Pipe1-1/2STD, OD 1.900 in). "
            "The coped post to rail underside detail requires post OD <= rail OD. Check the inputs.") in err, err


def test_equal_ods_are_allowed():
    proj = project.load(EXAMPLE)  # Pipe2STD rail and post
    validate(proj, Registry())


def _validate_with(monkeypatch, *, family=None, fu=None):
    """validate() on the example with a stand-in: a section of another family,
    or a post grade with a lower Fu. Stand-ins for machinery tests only."""
    real = shapes.section
    if family:
        monkeypatch.setattr(shapes, "section", lambda d: dataclasses.replace(real(d), family=family))
    reg = Registry()
    if fu:
        e = reg.entries["material.A53_GrB.Fu"]
        reg.entries[e.id] = dataclasses.replace(e, value=fu)
    validate(project.load(EXAMPLE), reg)


def test_a_section_that_is_not_round_hollow_stops(monkeypatch):
    # W7, with a stand-in family: only pipe can be entered today.
    with pytest.raises(project.ProjectError,
                       match=r"top rail Pipe2STD \(rectangular HSS\) is not a round hollow section.*"
                             r"rail wall's local strength at the post is not checked"):
        _validate_with(monkeypatch, family="rectangular HSS")


def test_a_post_grade_below_the_fu_fy_limit_stops(monkeypatch):
    # W5, with a stand-in Fu: 40/35 = 1.143 < 1.20.
    with pytest.raises(project.ProjectError,
                       match=r"post grade A53 Gr B: Fu/Fy = 1\.143 is below 1\.2 .*covered by Check 5 only"):
        _validate_with(monkeypatch, fu=40)
    _validate_with(monkeypatch, fu=42)  # 1.20 exactly passes


# ---------------------------------------------------------------------------
# Slice 4: the intermediate rail's states, B x N and the component load, and
# their validation stops (docs/plans/slice-4.md, T3)
# ---------------------------------------------------------------------------


def _example_raw(**tables):
    """The example as a dict, with whole tables replaced or added."""

    raw = tomllib.loads(EXAMPLE.read_text(encoding="utf-8"))
    for name, table in tables.items():
        raw[name] = table
    return raw


OWN = {"same_as_top_rail": False, "section": "Pipe1-1/4STD"}


def _own(**extra):
    """The example with the intermediate rail in its own section."""
    raw = _example_raw(intermediate_rail={**OWN, **extra})
    raw["welds"]["intermediate_rail_to_post"] = "1/8"
    return raw


def test_the_example_is_same_as_top_rail_with_b_and_n():
    proj = project.load(EXAMPLE)
    assert proj.intermediate_rail == project.IntermediateRail(project.SAME_AS_TOP)
    assert proj.intermediate_member == proj.top_rail
    assert proj.baseplate.B.value.m_as("inch") == 6 and proj.baseplate.N.value.m_as("inch") == 8
    assert proj.loads.component is None  # the registry value applies


def test_own_section_reads_its_inputs_and_defaults_its_grade_to_the_top_rails():
    raw = _own()
    raw["deflection"]["intermediate_rail"] = {"limit_L_over": 180, "bypass": True}
    raw["loads"]["component_lb"] = 150
    proj = project.from_dict(raw)
    ir = proj.intermediate_rail
    assert ir.state == project.OWN_SECTION
    assert ir.member == project.Member("Pipe1-1/4STD", "A53 Gr B")
    assert proj.intermediate_member == ir.member
    assert ir.deflection == project.DeflectionLimit(ratio=180, bypass=True)
    assert proj.welds.intermediate_rail_to_post.value.m_as("inch") == 0.125
    assert proj.loads.component.m_as("lbf") == 150


def test_own_section_deflection_limit_defaults_to_l_over_120():
    assert project.from_dict(_own()).intermediate_rail.deflection == project.RAIL_DEFLECTION


def test_none_has_no_intermediate_member():
    proj = project.from_dict(_example_raw(intermediate_rail={"none": True}))
    assert proj.intermediate_rail.state == project.NO_INTERMEDIATE and proj.intermediate_member is None


def _none_with(**inputs):
    raw = _example_raw(intermediate_rail={"none": True, **inputs.pop("table", {})})
    if inputs.pop("weld", False):
        raw["welds"]["intermediate_rail_to_post"] = "1/8"
    if inputs.pop("deflection", False):
        raw["deflection"]["intermediate_rail"] = {"limit_L_over": 120}
    return raw


def _same_with(**inputs):
    raw = _example_raw(intermediate_rail=inputs.pop("table", {}))
    if inputs.pop("weld", False):
        raw["welds"]["intermediate_rail_to_post"] = "1/8"
    if inputs.pop("deflection", False):
        raw["deflection"]["intermediate_rail"] = {"bypass": True}
    return raw


@pytest.mark.parametrize(
    "raw, message",
    [
        # none = true with any of the own-section inputs.
        (_none_with(table={"section": "Pipe1-1/4STD"}), "none = true, but [intermediate_rail] section is given"),
        (_none_with(table={"grade": "A53 Gr B"}), "none = true, but [intermediate_rail] grade is given"),
        (_none_with(weld=True), "none = true, but [welds] intermediate_rail_to_post is given"),
        (_none_with(deflection=True), "none = true, but [deflection.intermediate_rail] is given"),
        (_none_with(table={"same_as_top_rail": True}), "none = true and same_as_top_rail = true contradict"),
        # same_as_top_rail true (given, or by default) with any of them.
        (_same_with(table={"same_as_top_rail": True, "section": "Pipe1-1/4STD"}),
         "same_as_top_rail = true, but [intermediate_rail] section is given"),
        (_same_with(table={"grade": "A53 Gr B"}),
         "same_as_top_rail = true (the default), but [intermediate_rail] grade is given"),
        (_same_with(weld=True), "same_as_top_rail = true (the default), but [welds] intermediate_rail_to_post"),
        (_same_with(deflection=True), "but [deflection.intermediate_rail] is given"),
        # Its own section needs a section and a weld size.
        (_example_raw(intermediate_rail={"same_as_top_rail": False}),
         "same_as_top_rail = false needs a section"),
        (_example_raw(intermediate_rail=OWN), "[welds] is missing 'intermediate_rail_to_post', required when"),
        # B and N are required and positive.
        (_example_raw(baseplate={"N": 8}), "[baseplate] is missing 'B'"),
        (_example_raw(baseplate={"B": 6}), "[baseplate] is missing 'N'"),
        (_example_raw(baseplate={"B": 0, "N": 8}), "[baseplate] B must be greater than zero"),
        (_example_raw(baseplate={"B": 6, "N": -8}), "[baseplate] N: '-8': dimensions cannot be negative"),
        (_example_raw(intermediate_rail={"none": "true"}), "'intermediate_rail.none' must be true or false"),
    ],
)
def test_conflicting_or_missing_intermediate_and_baseplate_inputs_stop(raw, message):
    with pytest.raises(project.ProjectError) as e:
        project.from_dict(raw)
    assert message in str(e.value), str(e.value)


def _validate(raw):
    validate(project.from_dict(raw), Registry())


def test_an_intermediate_rail_wider_than_the_post_stops_in_both_states():
    # S4-11. Same as the top rail: a Pipe2-1/2STD rail on a Pipe2STD post
    # passes W8 (post OD <= rail OD) and stops here.
    raw = _example_raw()
    raw["top_rail"]["section"] = "Pipe2-1/2STD"
    with pytest.raises(project.ProjectError,
                       match=r"The intermediate rail \(Pipe2-1/2STD, OD 2\.875 in\) is wider than the post "
                             r"\(Pipe2STD, OD 2\.375 in\).*requires intermediate rail OD <= post OD\. "
                             r"With same_as_top_rail = true.*uncheck same_as_top_rail"):
        _validate(raw)
    with pytest.raises(project.ProjectError,
                       match=r"The intermediate rail \(Pipe2-1/2STD, OD 2\.875 in\).*Enter a section no wider"):
        _validate(_own(section="Pipe2-1/2STD"))


def test_an_intermediate_rail_as_wide_as_the_post_is_allowed():
    _validate(_own(section="Pipe2STD"))  # equal ODs (S4-11)
    _validate(_own())


def test_a_short_span_no_longer_stops_with_an_intermediate_rail():
    # The L >= 2 D_post stop served only Check 4b's branch-wall argument, which
    # the simple shear connection replaced (Micah, 2026-10-09).
    raw = _own()
    raw["geometry"]["span"] = 4
    _validate(raw)


@pytest.mark.parametrize("name, other", [("B", "N"), ("N", "B")])
def test_a_baseplate_smaller_than_the_post_od_stops(name, other):
    # S4-6: Pipe2STD post, OD 2.375 in.
    raw = _example_raw(baseplate={name: 2, other: 8})
    with pytest.raises(project.ProjectError,
                       match=rf"\[baseplate\] {name} = 2 .* is smaller than the post OD \(Pipe2STD, 2\.375 in\)"):
        _validate(raw)
    _validate(_example_raw(baseplate={name: 2.375, other: 8}))  # equal to the OD passes


def test_a_non_round_intermediate_rail_stops(monkeypatch):
    # W7 extended (S4-12), with a stand-in family on the intermediate section only.
    real = shapes.section
    monkeypatch.setattr(shapes, "section", lambda d: dataclasses.replace(real(d), family="rectangular HSS")
                        if d == "Pipe1-1/4STD" else real(d))
    with pytest.raises(project.ProjectError,
                       match=r"intermediate rail Pipe1-1/4STD \(rectangular HSS\) is not a round hollow section"):
        _validate(_own())


def test_an_intermediate_grade_this_version_does_not_support_stops():
    with pytest.raises(project.ProjectError, match="intermediate rail grade 'A500 Gr B': this version supports"):
        _validate(_own(grade="A500 Gr B"))
