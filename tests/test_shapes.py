"""The section type (S5-1; docs/plans/slice-5.md, step 2).

One type for every section: its family, the source of its values, and its
properties about both principal axes. Same-author machinery tests.
"""

import dataclasses

import pytest

from handrail import engine, report, shapes
from handrail.registry import Registry
from handrail.shapes import DB, PIPE, Axis, Section
from handrail.units import Q_
from test_intermediate import project
from test_line_keys import _blocks
from test_report import CLEAN


def _pipes():
    return [shapes.section(label) for label in shapes.labels(PIPE)]


def test_a_pipe_is_a_database_section_of_the_pipe_family():
    sec = shapes.section("Pipe2STD")
    assert isinstance(sec, Section)
    assert sec.family == PIPE and sec.source == DB == "AISC Shapes Database v16.0"


def test_a_round_section_has_the_same_properties_about_both_axes():
    """S5-1: the type carries I, S, Z and r about x and about y, and a round
    section has x = y. The database publishes both columns for a pipe; they
    are read as published and are equal on every row."""
    pipes = _pipes()
    assert len(pipes) > 30
    for sec in pipes:
        assert sec.x == sec.y, sec.label


def test_the_single_value_properties_read_the_x_axis():
    """Every check reads sec.I, sec.S, sec.Z and sec.r, as it did before the
    type had two axes. Which axis a check reads for a section that is not
    round is slice 6's decision; until then these are the x axis."""
    base = shapes.section("Pipe2STD")
    y = Axis(I=Q_(9, "in^4"), S=Q_(9, "in^3"), Z=Q_(9, "in^3"), r=Q_(9, "inch"))
    sec = dataclasses.replace(base, y=y)
    assert (sec.I, sec.S, sec.Z, sec.r) == (base.x.I, base.x.S, base.x.Z, base.x.r)
    assert sec.I != sec.y.I


# Which member each cited section value belongs to, by block and line key.
RAIL, POST, INT = "Source of the rail", "Source of the post", "Source of the intermediate rail"
EXPECTED = {
    "loading": {"w_D": RAIL, "W_post": POST, "w_D_int": INT},
    "Check 1": {"lambda": RAIL, "Z": RAIL},
    "Check 2": {"I": RAIL},
    "Check 3": {"D": POST, "d_rail": RAIL, "t_rail_nom": RAIL, "t_post_nom": POST, "t_rail": RAIL},
    "Check 4a": {"lambda": INT, "Z": INT, "I_int": INT},
    "Check 4b": {"D": INT, "t_int_nom": INT, "t_post_nom": POST, "t_post": POST, "t_int": INT},
    "Check 5": {"lambda": POST, "Z": POST, "r": POST, "A_g": POST, "I": POST},
    "Check 6": {"I": POST},
    "Check 7": {"D": POST, "t_post_nom": POST},
}


@pytest.fixture
def cited(monkeypatch):
    """Case 5's guard with three different sections, each given a source of
    its own, so a line citing the wrong member's source shows."""
    sources = {"Pipe2-1/2STD": RAIL, "Pipe2STD": POST, "Pipe1-1/4STD": INT}
    real = shapes.section
    monkeypatch.setattr(shapes, "section", lambda d: dataclasses.replace(real(d), source=sources[real(d).label]))
    reg = Registry()
    res = engine.run(project(rail="Pipe2-1/2STD"), reg)
    return res, reg


def test_every_line_cites_the_source_of_the_section_it_reads(cited):
    """F10 item 8: one constant used to cite every section value. Now each
    line cites its own section's source, so a custom tube beside a database
    post is cited correctly on every line."""
    res, _ = cited
    seen = {name: set() for name in EXPECTED}
    for block, lines in _blocks(res):
        name = block.split(",")[0].replace(" observation", "")
        for ln in lines:
            if ln.kind != "value" or ln.key not in EXPECTED.get(name, {}):
                continue
            assert ln.cite == EXPECTED[name][ln.key], f"{block}: {ln.key} cites {ln.cite!r}"
            seen[name].add(ln.key)
    for name, keys in EXPECTED.items():
        assert seen[name] == set(keys), f"{name}: lines not found: {sorted(set(keys) - seen[name])}"
    for lines, source in ((res.section_lines, RAIL), (res.post_section_lines, POST), (res.inter_section_lines, INT)):
        assert lines and {ln.cite for ln in lines} == {source}


def test_no_line_falls_back_to_the_database_citation(cited):
    """With every section given another source, the database is named only
    where the report itself names it: the references list and the sentence
    on the section properties page (F10 item 2, which step 8 makes per member)."""
    res, reg = cited
    src = report.build_source(res, reg, CLEAN)
    assert src.count(DB) == 2
    for source in (RAIL, POST, INT):
        assert source in src
