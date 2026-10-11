"""Command line: ``uv run handrail calc <project.toml> [-o out.pdf]``.

The PDF is written next to the project file with the same name unless -o is
given, so the input file and its calc sit side by side.
"""

import argparse
import sys
from pathlib import Path

from handrail import engine, project, report, version
from handrail.errors import InputError
from handrail.registry import Registry


def calc(project_file: Path, out: Path | None) -> Path:
    proj = project.load(project_file)
    registry = Registry()
    results = engine.run(proj, registry)
    out = out or project_file.with_suffix(".pdf")
    report.render_pdf(results, registry, version.stamp(), out)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="handrail", description="Guard calculation checker")
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("calc", help="run the checks and write the calc PDF")
    c.add_argument("project_file", type=Path, help="project file (.toml)")
    c.add_argument("-o", "--output", type=Path, help="PDF path (default: beside the project file)")
    args = parser.parse_args(argv)

    try:
        out = calc(args.project_file, args.output)
    except InputError as e:
        # One line; anything else is a bug and keeps its full traceback.
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"wrote {out}")
    return 0
