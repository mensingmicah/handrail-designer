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
    assert proj.loads.concentrated_lbf is None and not proj.loads.uniform_exempt
    assert proj.rail_deflection.ratio == 120 and not proj.rail_deflection.bypass
