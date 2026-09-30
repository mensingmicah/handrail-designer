from handrail import version


def test_stamp_reads_git():
    s = version.stamp()
    assert s.code_commit != "unknown commit"
    assert s.registry_commit != "unknown commit"


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
