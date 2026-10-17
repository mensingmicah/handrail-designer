"""Create the independent-calc values template for a test case.

    uv run python tests/independent_template.py case-02
    uv run python tests/independent_template.py case-06 --add

Writes tests/cases/independent/case-02.toml: every value the test compares
for that case, each "pending", and [provenance] unfilled. Key names only:
it runs the tool to learn which values it reports, and never writes or
prints one (CLAUDE.md rule 5). It refuses to overwrite an existing file,
which may hold the independent calc's values.

With --add, the file exists and the case has come to cover new values
(test case 6 gained the chord check in slice 6; cases 8 and 9 the skew
case of S6-18): the keys the file lacks are added, each "pending". A key
whose table the file already has is inserted at the end of that table,
since a TOML table cannot be opened twice; the rest are appended at the
file's end in tables of their own. Nothing already in the file is changed
or reordered: lines are only inserted. None of its values is read out or
printed; only its key names are compared.
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
        out += [_pending(parent, leaf) for leaf in leaves]
    return "\n".join(out) + "\n"


INSERTED = "# Added by tests/independent_template.py --add, each \"pending\":"


def _pending(parent: str, leaf: str) -> str:
    hint = "  # text, in quotes" if _is_text(f"{parent}.{leaf}") else ""
    return f'{leaf} = "{PENDING}"{hint}'


def add(out, keys) -> int:
    """Add the keys the file lacks, each "pending": into the table the file
    already has for a key, or appended in a new table. Compares key names
    only; no value of the file is printed, rewritten or moved."""
    with open(out, "rb") as f:
        have = dict(_flatten(tomllib.load(f).get("independent", {})))
    missing = [k for k in keys if k not in have]
    if not missing:
        print(f"{_rel(out)}: no key to add")
        return 0
    with open(out, encoding="utf-8", newline="") as f:
        lines = f.read().split("\n")
    headers = {line.strip()[len("[independent."):-1]: i for i, line in enumerate(lines)
               if line.strip().startswith("[independent.") and line.strip().endswith("]")}
    into: dict[str, list[str]] = {}
    appended = []
    for key in missing:
        parent, leaf = key.rsplit(".", 1)
        if parent in headers:
            into.setdefault(parent, []).append(leaf)
        else:
            appended.append(key)
    # Insert from the bottom of the file up, so each header's index holds.
    for parent in sorted(into, key=lambda p: headers[p], reverse=True):
        end = next((i for i in range(headers[parent] + 1, len(lines)) if lines[i].lstrip().startswith("[")),
                   len(lines))
        while end - 1 > headers[parent] and (not lines[end - 1].strip() or lines[end - 1].lstrip().startswith("#")):
            end -= 1  # after the table's last key, before the blank and comment lines that close it
        lines[end:end] = [INSERTED] + [_pending(parent, leaf) for leaf in into[parent]]
    text = "\n".join(lines)
    if appended:
        text = (text if text.endswith("\n") or not text else text + "\n") + render_added(appended)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text if text.endswith("\n") else text + "\n")
    print(f"{_rel(out)}: {len(missing)} keys added, all \"pending\" "
          f"({sum(map(len, into.values()))} into tables the file had, {len(appended)} in new tables); "
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
