import tomllib

import pytest

from handrail.registry import REGISTRY_PATH, MissingEntry, Registry, RegistryError


def entry(id, status="drafted", by="", date="", **extra):
    fields = {
        "id": id, "value": 1.67, "unit": "", "cite": "AISC 360-22 §F1",
        "document": "AISC 360-22", "edition": "2022", "section": "§F1",
        "source": "memory", "status": status, "verified_by": by, "verified_date": date,
    }
    fields.update(extra)
    lines = ["[[entry]]"] + [f"{k} = {v!r}".replace("'", '"') for k, v in fields.items()]
    lines.append("drafted_on = 2026-09-30")
    return "\n".join(lines) + "\n"


def write(tmp_path, review, *entries):
    p = tmp_path / "reg.toml"
    body = f"review = {list(review)!r}\n".replace("'", '"') + "\n".join(entries)
    p.write_text(body, encoding="utf-8")
    return p


def test_real_registry_loads():
    # The committed registry must satisfy every rule-1 check.
    Registry()


def test_review_list_matches_drafted_entries(tmp_path):
    p = write(tmp_path, ["a"], entry("a"), entry("b", status="verified", by="MM", date="2026-10-01"))
    reg = Registry(p)
    assert reg.review == ["a"]


def test_drafted_entry_missing_from_review_list_is_refused(tmp_path):
    p = write(tmp_path, ["a"], entry("a"), entry("b"))
    with pytest.raises(RegistryError, match="Drafted but not in review list: b"):
        Registry(p)


def test_review_list_naming_a_verified_entry_is_refused(tmp_path):
    p = write(tmp_path, ["a", "b"], entry("a"), entry("b", status="verified", by="MM", date="2026-10-01"))
    with pytest.raises(RegistryError, match="not a drafted entry: b"):
        Registry(p)


def test_verified_without_name_and_date_is_refused(tmp_path):
    p = write(tmp_path, [], entry("a", status="verified"))
    with pytest.raises(RegistryError, match="verified without"):
        Registry(p)


def test_missing_field_is_refused(tmp_path):
    bad = entry("a").replace('cite = "AISC 360-22 §F1"\n', "")
    p = write(tmp_path, ["a"], bad)
    with pytest.raises(RegistryError, match="a: missing field.*cite"):
        Registry(p)


def test_missing_entry_is_a_hard_stop_naming_the_entry(tmp_path):
    reg = Registry(write(tmp_path, ["a"], entry("a")))
    with pytest.raises(MissingEntry, match="aisc360.nonexistent"):
        reg.get("aisc360.nonexistent")


def test_usage_tracks_only_drafted_entries_used(tmp_path):
    p = write(
        tmp_path, ["a", "c"],
        entry("a"), entry("b", status="verified", by="MM", date="2026-10-01"), entry("c"),
    )
    reg = Registry(p)
    reg.get("b")
    reg.get("a")
    reg.get("a")
    assert [e.id for e in reg.used] == ["b", "a"]
    assert [e.id for e in reg.drafted_used] == ["a"]  # c was never used


def test_quantity_carries_units():
    reg = Registry()
    assert reg.get("material.steel.E").quantity.m_as("ksi") == 29000
    assert reg.get("asce7.guard.uniform").quantity.m_as("lbf/inch") == pytest.approx(50 / 12)


# ---------------------------------------------------------------------------
# Registry lint (.claude/rules/code-values.md, "Editing the file itself").
#
# Shell edits have rewritten backslashes and line endings in the registry
# (slice 4: d72e4aa wrote literal \r escapes into a note; 5fa154a repaired
# it). TOML accepts those escapes, so the registry loads and nothing else
# notices. This lint fails on them instead.
# ---------------------------------------------------------------------------

BACKSLASH = "\\"


def lint(text: str) -> list[str]:
    """Problems in registry text: every backslash escape other than \\" and
    a line continuation (a backslash as the last character on its line),
    and every control character inside a parsed string (a stray \\r, \\t,
    or a newline left by a broken continuation). The working copy may
    have CRLF line endings, so they are read as LF first."""
    text = text.replace("\r\n", "\n")
    problems = []
    for number, line in enumerate(text.split("\n"), 1):
        body = line.rstrip(" \t")
        i = 0
        while i < len(body):
            if body[i] != BACKSLASH:
                i += 1
                continue
            if i == len(body) - 1:
                break  # line continuation
            if body[i + 1] != '"':
                problems.append(f"line {number}: escape {body[i:i + 2]!r} in {line.strip()[:70]!r}")
            i += 2
    try:
        parsed = tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        return problems + [f"not valid TOML: {e}"]

    def strings(node, where):
        if isinstance(node, dict):
            for k, v in node.items():
                yield from strings(v, f"{where}.{k}" if where else k)
        elif isinstance(node, list):
            for n, v in enumerate(node):
                yield from strings(v, f"{where}[{n}]")
        elif isinstance(node, str):
            yield where, node

    for where, s in strings(parsed, ""):
        bad = sorted({repr(c) for c in s if ord(c) < 32 or ord(c) == 127})
        if bad:
            problems.append(f"{where}: control character(s) {', '.join(bad)} in {s[:70]!r}")
    return problems


def test_registry_has_no_stray_escapes_or_control_characters():
    with open(REGISTRY_PATH, encoding="utf-8", newline="") as f:
        problems = lint(f.read())
    assert not problems, (
        "registry/code-values.toml has text a shell edit may have mangled. Fix it with the file-edit "
        "tool (.claude/rules/code-values.md):\n" + "\n".join(problems)
    )


GOOD = (
    'review = []\n'
    '[[entry]]\n'
    'id = "a"\n'
    'value = "Text with a \\"quoted\\" word."\n'
    'note = """\n'
    'First line, continued \\\n'
    'on the next."""\n'
)


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_lint_accepts_quotes_and_line_continuations(newline):
    assert lint(GOOD.replace("\n", newline)) == []


@pytest.mark.parametrize("bad, found", [
    # The slice 4 failure: a continuation written as a \r escape.
    (GOOD.replace("continued \\\n", "continued \\r\n"), "'\\\\r'"),
    (GOOD.replace("with a", "with\\ta"), "'\\\\t'"),
    # A doubled backslash: the continuation is lost and a newline lands in the text.
    (GOOD.replace("continued \\\n", "continued \\\\\n"), "'\\n'"),
])
def test_lint_finds_mangled_escapes(bad, found):
    problems = lint(bad)
    assert problems and any(found in p for p in problems), problems
