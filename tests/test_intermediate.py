"""Slice 4: the intermediate rail (Checks 4a and 4b) and its dead load path.

Same-author machinery tests (docs/plans/slice-4.md, T3), like test_post.py
and test_welds.py: every expected value is recomputed here with plain
floats in lb, in and ksi. Test case 5 (an independent calc) is the
independent check.
"""

import dataclasses

import pytest

from handrail import checks, dimensions, shapes
from handrail.project import (
    NO_INTERMEDIATE, OWN_SECTION, SAME_AS_TOP, Baseplate, DeflectionLimit, IntermediateRail, Loads, Member, Project,
    ProjectInfo, Welds,
)
from handrail.registry import Registry

P2, P125 = shapes.pipe("Pipe2STD"), shapes.pipe("Pipe1-1/4STD")


def project(state=OWN_SECTION, section="Pipe1-1/4STD", rail="Pipe2STD", post="Pipe2STD", span="6'-0\"",
            int_weld="1/8", deflection=None, **kw):
    """Case 5's guard by default (plan T1): Pipe2STD rail and post over 6'-0",
    h = 42 in, t_p = 1/2 in, B x N = 6 x 8 in, a Pipe1-1/4STD intermediate rail."""
    member = Member(section, "A53 Gr B") if state == OWN_SECTION else None
    ir = IntermediateRail(state, member, deflection or DeflectionLimit())
    welds = Welds(dimensions.parse("1/8"), dimensions.parse("1/4"),
                  intermediate_rail_to_post=dimensions.parse(int_weld) if state == OWN_SECTION else None)
    return Project(info=ProjectInfo(name="Test"), span=dimensions.parse(span),
                   top_rail=Member(rail, "A53 Gr B"), post=Member(post, "A53 Gr B"),
                   post_height=dimensions.parse("42"), baseplate_thickness=dimensions.parse("1/2"),
                   welds=welds, baseplate=Baseplate(dimensions.parse("6"), dimensions.parse("8")),
                   intermediate_rail=ir, **kw)


def run(**kw):
    return checks.run(project(**kw), Registry())


def _lb(q):
    return q.m_as("lbf")


# ---------------------------------------------------------------------------
# The dead load path (plan, "Where the intermediate rail's dead load goes")
# ---------------------------------------------------------------------------


def test_an_intermediate_rail_adds_its_dead_load_to_d_at_the_post_only():
    L_ft, h, tp = 6.0, 42.0, 0.5
    none, own = run(state=NO_INTERMEDIATE), run()
    w_rail, w_int, w_post = P2.W.m_as("lbf/ft"), P125.W.m_as("lbf/ft"), P2.W.m_as("lbf/ft")
    D_none = w_rail * L_ft + w_post * (h - tp) / 12
    assert _lb(none.loading.P_D) == pytest.approx(D_none, rel=1e-9)
    assert _lb(own.loading.P_D) == pytest.approx(D_none + w_int * L_ft, rel=1e-9)
    assert _lb(own.loading.D_int) == pytest.approx(w_int * L_ft, rel=1e-9)
    assert none.loading.D_int is None and none.loading.w_D_int is None

    # Check 5 (the downward axial load) and Check 7 (its axial dead load) carry it ...
    for number, symbol in ((5, "P_D"), (7, "P_D")):
        for res, D in ((none, D_none), (own, D_none + w_int * L_ft)):
            c = res.check(number).checked[0]
            assert _lb(next(ln.value for ln in c.lines if ln.symbol == symbol)) == pytest.approx(D, rel=1e-9)
    # ... and Check 3's D is the top rail's alone, unchanged.
    for res in (none, own):
        c = res.check(3).checked[0]
        assert _lb(next(ln.value for ln in c.lines if ln.symbol == 'D_"rail"')) == pytest.approx(w_rail * L_ft)


def test_same_as_the_top_rail_adds_the_top_rails_weight():
    res = run(state=SAME_AS_TOP)
    assert res.loading.w_D_int == P2.W
    assert _lb(res.loading.D_int) == pytest.approx(P2.W.m_as("lbf/ft") * 6.0)
    note = next(ln.note for ln in res.loading.lines if ln.symbol == 'w_(D,"int")')
    assert "same section as the top rail" in note


def test_no_intermediate_rail_prints_no_intermediate_dead_load():
    res = run(state=NO_INTERMEDIATE)
    assert not [ln for ln in res.loading.lines if "int" in ln.symbol]
