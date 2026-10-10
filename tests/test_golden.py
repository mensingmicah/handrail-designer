"""Golden snapshots of the printed calc (issue #6; docs/plans/slice-5.md, step 1).

A golden snapshot is the full text the tool prints for one calc, saved as a
file in tests/golden/. Each test regenerates that text and fails on any
difference, with a line-by-line diff. The text is the Typst source the PDF
is compiled from, so every printed number, formula, citation, margin note
and table cell is in it.

**A snapshot change is a printed-calc change and needs Micah's review.**
The test cases compare numbers at 0.5%; they cannot see a dropped citation,
a reworded note or a changed decision line. These snapshots can. A pure
refactor must leave every snapshot byte-identical. A change that alters
printed text on purpose updates the snapshots in a commit of its own, one
commit per intended change, so the pull request shows Micah the changed text
as a diff he can read (docs/plans/slice-5.md, "Snapshot rule for every
step"). A difference nobody intended, or one larger than the change it
belongs to, is a stop: find the cause before regenerating anything.

What is snapshotted:

- test cases 1 to 5 (tests/cases/case-NN.toml) and examples/slice-1.toml,
  each as tests/golden/<name>.typ;
- test case 3 stops at validation when run in full (a post wider than its
  rail, W8; slice 3 plan, T1). Its .typ snapshot is the compute step's
  output, the same path its values are tested through, and
  tests/golden/case-03.stop.txt holds the stop message the full run gives.

Every snapshot is generated with the fixed footer stamp CLEAN from
tests/test_report.py, so a new commit or a version bump does not change it.
Snapshots are written and compared as UTF-8 with LF line endings
(.gitattributes keeps them LF on every OS). The generated source holds
nothing that varies by machine or run (no path, no date, no temp file
name), so no placeholder is substituted.

To regenerate on purpose, after Micah has agreed the printed text should
change:

    uv run pytest tests/test_golden.py --update-golden

That rewrites the files in tests/golden/ from the tool's current output and
reports each file it changed. Commit the snapshot change on its own, and
show the diff (git diff tests/golden/) in the report. Never regenerate to
make a failing test pass without knowing why it failed.
"""

import difflib
import tomllib
from pathlib import Path

import pytest

from handrail import engine, project, report
from handrail.errors import InputError
from handrail.registry import Registry
from test_report import CLEAN

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = ROOT / "tests" / "golden"
CASES = sorted((ROOT / "tests" / "cases").glob("case-0[1-5].toml"))
EXAMPLE = ROOT / "examples" / "slice-1.toml"
DIFF_LINES = 200  # the most diff lines a failure prints


def _load(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def _stops_at_validation(path: Path) -> bool:
    return bool(_load(path).get("verification", {}).get("stops_at_validation", ""))


def calc_source(path: Path) -> str:
    """The Typst source of one calc, with the fixed stamp. A case validation
    refuses (test case 3) is taken through the compute step, as its values
    are (slice 3 plan, T1)."""
    proj = project.from_dict(_load(path))
    registry = Registry()
    run = engine.compute if _stops_at_validation(path) else engine.run
    return report.build_source(run(proj, registry), registry, CLEAN)


def stop_message(path: Path) -> str:
    """The message the full run stops with, for a case validation refuses."""
    with pytest.raises(InputError) as stop:
        engine.run(project.from_dict(_load(path)), Registry())
    return f"{stop.value}\n"


def _snapshots() -> dict[str, tuple]:
    """Snapshot file name -> (generator, input file)."""
    out = {f"{p.stem}.typ": (calc_source, p) for p in CASES}
    out["slice-1-example.typ"] = (calc_source, EXAMPLE)
    out.update({f"{p.stem}.stop.txt": (stop_message, p) for p in CASES if _stops_at_validation(p)})
    return out


SNAPSHOTS = _snapshots()


def _diff(name: str, golden: str, current: str) -> str:
    lines = list(difflib.unified_diff(golden.splitlines(), current.splitlines(), f"tests/golden/{name} (committed)",
                                      f"{name} (the tool's output now)", lineterm="", n=2))
    shown = lines[:DIFF_LINES]
    if len(lines) > DIFF_LINES:
        shown.append(f"... {len(lines) - DIFF_LINES} more diff lines not shown")
    return "\n".join(shown)


@pytest.mark.parametrize("name", list(SNAPSHOTS))
def test_printed_calc_matches_its_golden_snapshot(name, request):
    """The tool's printed text for this calc is byte-identical to the
    committed snapshot. A snapshot change is a printed-calc change and needs
    Micah's review: do not regenerate until the cause of a difference is
    known and the change is intended (this file's docstring)."""
    generate, source = SNAPSHOTS[name]
    current = generate(source)
    path = GOLDEN_DIR / name
    if request.config.getoption("--update-golden"):
        before = path.read_bytes() if path.is_file() else None
        GOLDEN_DIR.mkdir(exist_ok=True)
        path.write_bytes(current.encode("utf-8"))
        if before != current.encode("utf-8"):
            print(f"\ngolden snapshot {'created' if before is None else 'CHANGED'}: tests/golden/{name}")
        return
    assert path.is_file(), (
        f"no golden snapshot tests/golden/{name}. Create it on purpose with "
        f"uv run pytest tests/test_golden.py --update-golden"
    )
    golden = path.read_bytes().decode("utf-8")
    assert "\r" not in golden, (
        f"tests/golden/{name} has CRLF line endings; snapshots are LF (.gitattributes). "
        f"Check the checkout, not the tool."
    )
    if current != golden:
        pytest.fail(
            f"The printed calc changed: {source.relative_to(ROOT).as_posix()} no longer matches "
            f"tests/golden/{name}.\n"
            f"A snapshot change is a printed-calc change and needs Micah's review. If this change was not "
            f"intended, it is a stop: find the cause, and do not regenerate the snapshot.\n\n"
            f"{_diff(name, golden, current)}",
            pytrace=False,
        )


def test_every_golden_file_is_a_snapshot_the_test_compares():
    """No stale file in tests/golden/: each one is compared by the test above."""
    stale = sorted(p.name for p in GOLDEN_DIR.iterdir() if p.name not in SNAPSHOTS)
    assert not stale, f"tests/golden/ holds files no test compares: {stale}"


def test_a_changed_line_fails_with_a_readable_diff():
    """The diff a failure prints names the file and shows the old and new line."""
    text = _diff("case-01.typ", "a\nM_n = 1\nc\n", "a\nM_n = 2\nc\n")
    assert "tests/golden/case-01.typ (committed)" in text
    assert "-M_n = 1" in text and "+M_n = 2" in text
