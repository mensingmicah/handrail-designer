"""Create the independent-calc values template for a test case.

    uv run python tests/independent_template.py case-02
    uv run python tests/independent_template.py case-06 --add

Writes tests/cases/independent/case-02.toml: every value the test compares
for that case, each "pending", and [provenance] unfilled. Key names only:
it runs the tool to learn which values it reports, and never writes or
prints one (CLAUDE.md rule 5). It refuses to overwrite an existing file,
which may hold the independent calc's values.

With --add, the file exists and the case has come to cover a new group
(test case 6 gained the chord check in slice 6): the keys the file lacks
are appended at its end, each "pending". Nothing already in the file is
changed, and none of its values is read out or printed; only its key
names are compared. It refuses if a missing key belongs to a table the
file already has, since a TOML table cannot be opened twice.
"""

import sys
import tomllib

from test_hand_cases import (CASES_DIR, INDEPENDENT_CALC, PENDING, ROOT, _flatten, _is_text, expected_keys,
                             independent_path, kind, render_template, run_case)

USAGE = "\n".join(line.strip() for line in __doc__.strip().splitlines()[2:4])


def _rel(path) -> str:
    """A path as the messages print it: from the repo root where it is under it."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def render_added(keys) -> str:
    """The tables appended for keys a file lacks, each "pending". Names only."""
    tables: dict[str, list[str]] = {}
    for key in keys:
        parent, leaf = key.rsplit(".", 1)
        tables.setdefault(parent, []).append(leaf)
    out = ["", "# Added by tests/independent_template.py --add: values the case has come to",
           "# cover since this file was written, each \"pending\" until an independent",
           "# calc fills it. Nothing above this line was changed."]
    for parent, leaves in tables.items():
        out += ["", f"[independent.{parent}]"]
        for leaf in leaves:
            hint = "  # text, in quotes" if _is_text(f"{parent}.{leaf}") else ""
            out.append(f'{leaf} = "{PENDING}"{hint}')
    return "\n".join(out) + "\n"


def add(out, keys) -> int:
    """Append the keys the file lacks, each "pending". Compares key names
    only; no value of the file is printed or rewritten."""
    with open(out, "rb") as f:
        have = dict(_flatten(tomllib.load(f).get("independent", {})))
    missing = [k for k in keys if k not in have]
    if not missing:
        print(f"{_rel(out)}: no key to add")
        return 0
    # Every table the file has, at any depth: a parent of any key it holds.
    tables = set()
    for k in have:
        parts = k.split(".")[:-1]
        tables.update(".".join(parts[:i]) for i in range(1, len(parts) + 1))
    clash = sorted({k.rsplit(".", 1)[0] for k in missing} & tables)
    if clash:
        print(f"{_rel(out)}: keys are missing from tables the file already has "
              f"({', '.join(clash)}); add them by hand, in those tables", file=sys.stderr)
        return 1
    text = render_added(missing)
    with open(out, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(size - 1, 0))
        ends_clean = size == 0 or f.read(1) == b"\n"
    with open(out, "a", encoding="utf-8", newline="\n") as f:
        f.write(text if ends_clean else "\n" + text)
    print(f"{_rel(out)}: {len(missing)} keys added, all \"pending\"; "
          f"groups {sorted({k.split('.')[0] for k in missing})}")
    return 0


def main(argv: list[str]) -> int:
    adding = "--add" in argv
    argv = [a for a in argv if a != "--add"]
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
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
    keys = expected_keys(raw, res)
    if adding:
        if not out.exists():
            print(f"no {out.relative_to(ROOT).as_posix()} to add to; run without --add", file=sys.stderr)
            return 1
        return add(out, keys)
    if out.exists():
        print(f"{out.relative_to(ROOT).as_posix()} already exists and may hold values; "
              f"not overwritten", file=sys.stderr)
        return 1
    out.parent.mkdir(exist_ok=True)
    out.write_text(render_template(case, keys), encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT).as_posix()}: {len(keys)} keys, all \"pending\"")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
