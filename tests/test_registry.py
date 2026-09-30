import pytest

from handrail.registry import MissingEntry, Registry, RegistryError


def entry(id, status="drafted", by="", date="", **extra):
    fields = dict(
        id=id, value=1.67, unit="", cite="AISC 360-22 §F1",
        document="AISC 360-22", edition="2022", section="§F1",
        source="memory", status=status, verified_by=by, verified_date=date,
    )
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
