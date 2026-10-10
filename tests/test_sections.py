"""Hollow round sections at the joints: the width comparisons' OD
tolerance (S5-4), the third guard on Check 4b's observation (S5-11), the
chord D/t limit (S5-3) and the round HSS cells of the per-joint tables
(docs/brief/welds.md, "Hollow round sections (slice 5)").

Machinery tests, same-author (docs/plans/slice-5.md, T4). They are not
test cases, and no value here is a hand or independent value. Where no
database section has the dimension a rule turns on, the section is a
stand-in: a database section with one value replaced.
"""

import dataclasses

import pytest

from handrail import engine, project, shapes
from handrail.project import ProjectError
from handrail.registry import Registry
from handrail.stops import Stop
from handrail.units import Q_

OD_TOLERANCE = "ej.section.od_tolerance"
OWN_WELD = {"intermediate_rail_to_post": "1/8"}


def _raw(**tables) -> dict:
    """A project that runs: Pipe2STD rail and post over 6'-0", no intermediate rail."""
    raw = {
        "project": {"name": "sections"},
        "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
        "top_rail": {"section": "Pipe2STD"}, "post": {"section": "Pipe2STD"},
        "welds": {"rail_to_post": "1/8", "post_to_baseplate": "1/4"},
        "baseplate": {"B": 6, "N": 8}, "intermediate_rail": {"none": True},
    }
    for name, table in tables.items():
        raw[name] = table if name == "intermediate_rail" else {**raw.get(name, {}), **table}
    return raw


def _run(registry: Registry | None = None, **tables):
    return engine.run(project.from_dict(_raw(**tables)), registry or Registry())


def _with(monkeypatch, label: str, **changes) -> None:
    """Give the database section of this label other values: a stand-in."""
    real = shapes.section

    def section(designation: str) -> shapes.Section:
        sec = real(designation)
        return dataclasses.replace(sec, **changes) if sec.label == label else sec

    monkeypatch.setattr(shapes, "section", section)


def _od(inches: float):
    return Q_(inches, "inch")


# -- the OD tolerance in W8 and S4-11 (S5-4) -----------------------------------------

def test_a_post_wider_than_the_rail_by_less_than_the_tolerance_runs(monkeypatch):
    """W8: ODs 0.005 in apart are equal, so the stop does not fire. The
    tolerance decided, so the calc lists its entry."""
    _with(monkeypatch, "Pipe1-1/2STD", OD=_od(2.380))  # the post, under a 2.375 in rail
    reg = Registry()
    res = _run(reg, post={"section": "Pipe1-1/2STD"})
    assert res.post.OD == _od(2.380) and res.rail.OD == _od(2.375)
    assert OD_TOLERANCE in [e.id for e in reg.used]


def test_a_post_wider_than_the_rail_by_more_than_the_tolerance_stops(monkeypatch):
    _with(monkeypatch, "Pipe1-1/2STD", OD=_od(2.395))  # 0.02 in wider
    with pytest.raises(ProjectError) as stopped:
        _run(post={"section": "Pipe1-1/2STD"})
    assert stopped.value.stop is Stop.SECTION_POST_WIDER_THAN_RAIL
    assert "OD 2.395 in) is wider than the top rail (Pipe2STD, OD 2.375 in)" in str(stopped.value)


def test_an_intermediate_rail_wider_than_the_post_by_less_than_the_tolerance_runs(monkeypatch):
    """S4-11, with the same tolerance."""
    _with(monkeypatch, "Pipe1-1/4STD", OD=_od(2.380))  # the intermediate rail, on a 2.375 in post
    reg = Registry()
    res = _run(reg, intermediate_rail={"same_as_top_rail": False, "section": "Pipe1-1/4STD"}, welds=OWN_WELD)
    assert res.inter.OD == _od(2.380) and res.post.OD == _od(2.375)
    assert OD_TOLERANCE in [e.id for e in reg.used]


def test_an_intermediate_rail_wider_than_the_post_by_more_than_the_tolerance_stops(monkeypatch):
    _with(monkeypatch, "Pipe1-1/4STD", OD=_od(2.395))
    with pytest.raises(ProjectError) as stopped:
        _run(intermediate_rail={"same_as_top_rail": False, "section": "Pipe1-1/4STD"}, welds=OWN_WELD)
    assert stopped.value.stop is Stop.SECTION_INTERMEDIATE_WIDER_THAN_POST
    assert "OD 2.395 in) is wider than the post (Pipe2STD, OD 2.375 in)" in str(stopped.value)


@pytest.mark.parametrize("tables", [
    {},                                                                   # equal ODs
    {"post": {"section": "Pipe1-1/2STD"}},                                # a narrower post
    {"intermediate_rail": {"same_as_top_rail": False, "section": "Pipe1-1/4STD"}, "welds": OWN_WELD},
    {"intermediate_rail": {"same_as_top_rail": True}},
], ids=["equal", "narrower post", "narrower intermediate rail", "same as top"])
def test_the_tolerance_is_not_read_when_no_member_is_wider_than_it_may_be(tables):
    """The tolerance is read only when it decides (as the checks fetch an
    equation only on its own branch), so a calc it did not decide does not
    list its drafted entry."""
    reg = Registry()
    _run(reg, **tables)
    assert OD_TOLERANCE not in [e.id for e in reg.used]


def test_the_tolerance_changes_only_the_comparison_every_line_uses_each_members_own_od(monkeypatch):
    _with(monkeypatch, "Pipe1-1/2STD", OD=_od(2.380))
    res = _run(post={"section": "Pipe1-1/2STD"})
    ring = next(ln for ln in res.check(3).controlling.lines if ln.key == "D")
    depth = next(ln for ln in res.check(3).controlling.lines if ln.key == "d_rail")
    assert ring.value == _od(2.380) and depth.value == _od(2.375)


# -- Check 4b's observation: a post wider than the rail at all (S5-11) ---------------

def _guards(chk) -> list:
    return [ln for ln in chk.controlling.lines if ln.kind == "decision" and ln.text == "Computed in full"]


def test_a_post_wider_than_the_rail_within_the_tolerance_runs_the_full_check_4b(monkeypatch):
    """Same as the top rail, R <= P and equal walls, but the post is 0.005
    in wider than the rail: the observation's "ring at least Check 3's"
    would be false, so the full check runs and prints the guard that failed."""
    _with(monkeypatch, "Pipe2XS", OD=_od(2.380), tdes=shapes.section("Pipe2STD").tdes)
    res = _run(post={"section": "Pipe2XS"}, intermediate_rail={"same_as_top_rail": True})
    chk = res.check("4b")
    assert chk.observation == "" and chk.cases
    guards = _guards(chk)
    assert len(guards) == 1
    assert guards[0].symbol == 'D_"post" = "2.380 in" > D_"rail" = "2.375 in"'
    assert "the post is wider than the rail" in guards[0].note


def test_equal_ods_keep_the_observation():
    chk = _run(intermediate_rail={"same_as_top_rail": True}).check("4b")
    assert chk.result == "Controlled by Check 3" and chk.observation and not chk.cases


def test_a_rail_wider_than_the_post_within_the_tolerance_keeps_the_observation(monkeypatch):
    """The other way round, the rail 0.005 in wider than the post: this
    weld's ring, the rail's perimeter, is still at least Check 3's."""
    _with(monkeypatch, "Pipe2STD", OD=_od(2.380))  # rail and intermediate rail
    _with(monkeypatch, "Pipe2XS", tdes=shapes.section("Pipe2STD").tdes)
    reg = Registry()
    chk = _run(reg, post={"section": "Pipe2XS"}, intermediate_rail={"same_as_top_rail": True}).check("4b")
    assert chk.result == "Controlled by Check 3"
    assert OD_TOLERANCE in [e.id for e in reg.used]  # S4-11: the intermediate rail is 0.005 in wider than the post


# -- round HSS at the joints (S5-9, S5-12), by real inputs ----------------------------

def test_a_round_hss_post_under_a_pipe_rail_of_the_same_size_runs():
    """HSS2.375 reads 2.38 in and Pipe2STD 2.375 in: the same physical
    diameter, equal within the tolerance (S5-4). The post takes the round
    HSS default grade, and each weld ring uses the post's own published OD."""
    reg = Registry()
    res = _run(reg, post={"section": "HSS2.375X0.125"})
    assert (res.post.family, res.post.OD, res.rail.OD) == (shapes.ROUND_HSS, _od(2.38), _od(2.375))
    assert res.project.post == project.Member("HSS2.375X0.125", "A500 Gr B", grade_defaulted=True)
    assert OD_TOLERANCE in [e.id for e in reg.used]
    for check in (3, 7):
        ring = next(ln for ln in res.check(check).controlling.lines if ln.key == "D")
        assert ring.value == _od(2.38)


def test_the_directional_increase_applies_to_a_round_hss_post_at_check_7_only():
    """W2 as S5-12 confirms it: k_ds from theta at the post to baseplate
    weld, k_ds = 1.0 at the branch-to-chord welds."""
    res = _run(post={"section": "HSS2.375X0.125"}, top_rail={"section": "HSS2.375X0.154"},
               intermediate_rail={"same_as_top_rail": False, "section": "HSS1.900X0.120"}, welds=OWN_WELD)
    assert res.check(7).controlling.k_ds > 1.0
    assert res.check(3).controlling.k_ds == 1.0 and res.check("4b").controlling.k_ds == 1.0


@pytest.mark.parametrize("rail, post, inter", [
    ("HSS2.375X0.154", "HSS2.375X0.125", "HSS1.900X0.120"),
    ("HSS2.375X0.154", "Pipe2STD", "Pipe1-1/4STD"),
    ("Pipe2STD", "Pipe2STD", "HSS1.900X0.120"),
    ("Pipe2STD", "HSS1.900X0.120", "Pipe1-1/4STD"),
])
def test_pipe_and_round_hss_meet_at_every_joint(rail, post, inter):
    res = _run(top_rail={"section": rail}, post={"section": post},
               intermediate_rail={"same_as_top_rail": False, "section": inter}, welds=OWN_WELD)
    assert [c.number for c in res.checks] == [1, 2, 3, "4a", "4b", 5, 6, 7]
    assert all(c.computed and c.controlling is not None for c in res.checks)
