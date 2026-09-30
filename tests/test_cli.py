"""The one command, end to end, and the project file reader."""

from pathlib import Path

import pytest

from handrail import cli, project

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


def test_hand_table_is_allowed_in_a_case_file():
    case = Path(__file__).resolve().parent / "cases" / "case-01.toml"
    assert project.load(case).top_rail.section == "Pipe1-1/2STD"
