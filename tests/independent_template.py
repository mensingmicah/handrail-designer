"""Create the independent-calc values template for a test case.

    uv run python tests/independent_template.py case-02

Writes tests/cases/independent/case-02.toml: every value the test compares
for that case, each "pending", and [provenance] unfilled. Key names only:
it runs the tool to learn which values it reports, and never writes or
prints one (CLAUDE.md rule 5). It refuses to overwrite an existing file,
which may hold the independent calc's values.
"""

import sys

from test_hand_cases import (CASES_DIR, INDEPENDENT_CALC, ROOT, expected_keys,
                             independent_path, kind, render_template, run_case)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    case = CASES_DIR / f"{argv[0].removesuffix('.toml')}.toml"
    if not case.is_file():
        print(f"no test case {case.relative_to(ROOT).as_posix()}", file=sys.stderr)
        return 1
    raw, res = run_case(case)
    if kind(raw) != INDEPENDENT_CALC:
        print(f"{case.name}: [verification] kind is {kind(raw)!r}, not {INDEPENDENT_CALC!r}", file=sys.stderr)
        return 1
    out = independent_path(case)
    if out.exists():
        print(f"{out.relative_to(ROOT).as_posix()} already exists and may hold values; "
              f"not overwritten", file=sys.stderr)
        return 1
    keys = expected_keys(raw, res)
    out.parent.mkdir(exist_ok=True)
    out.write_text(render_template(case, keys), encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT).as_posix()}: {len(keys)} keys, all \"pending\"")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
