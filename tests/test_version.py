import tomllib

from handrail import version


def test_stamp_reads_git():
    s = version.stamp()
    assert s.code_commit != "unknown commit"
    assert s.registry_commit != "unknown commit"


def test_the_footer_prints_the_version_in_pyproject():
    """The footer's tool version is the one pyproject.toml declares, which
    each slice's pull request bumps (CLAUDE.md; issue #24, item 1). The
    golden snapshots use a fixed stamp and cannot see it."""
    with open(version.REPO / "pyproject.toml", "rb") as f:
        declared = tomllib.load(f)["project"]["version"]
    s = version.stamp()
    assert s.tool_version == declared
    assert s.footer_parts()[0].startswith(f"Tool {declared} (")


def test_dirty_when_git_reports_changes(monkeypatch):
    monkeypatch.setattr(version, "_git", lambda *a: " M src/handrail/calc.py")
    assert version._dirty(version.CODE_PATHS)


def test_clean_when_git_reports_nothing(monkeypatch):
    monkeypatch.setattr(version, "_git", lambda *a: "")
    assert not version._dirty(version.CODE_PATHS)


def test_unknown_is_never_reported_clean(monkeypatch):
    # If git is unavailable, the footer must not imply the code is committed.
    monkeypatch.setattr(version, "_git", lambda *a: None)
    assert version._dirty(version.CODE_PATHS)
