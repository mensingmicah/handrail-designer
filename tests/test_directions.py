"""Directions and load types are fixed lists; an unknown one stops (issue #21, item 3).

Before this, three places computed a mistyped direction as another case:
Check 1's bending ended in a bare ``else`` that took anything as upward,
the shared demand took anything not downward or upward as horizontal, and
the reaction sets relied on that for "Lateral". Same-author machinery
tests: each one calls a function with a direction or load type it has no
branch for and expects a ValueError, never a number.
"""

import pytest

from handrail import checks, intermediate, post
from handrail.calc import Sheet
from handrail.demand import ASD, Given, demand, live_at_post
from handrail.directions import (
    COMPONENT_DIRECTIONS, DIRECTIONS, LOAD_TYPES, Direction, Kind, LoadType, kind,
)
from handrail.registry import Registry
from test_intermediate import run


@pytest.fixture(scope="module")
def res():
    return run()  # case 5's guard: every check computed, an intermediate rail of its own


def test_members_print_and_compare_as_their_text():
    assert f"{Direction.DOWNWARD}" == "Downward" and str(LoadType.CONCENTRATED) == "Concentrated"
    assert Direction.OUTWARD == "Outward" and Direction.OUTWARD.lower() == "outward"
    assert [str(d) for d in DIRECTIONS] == ["Downward", "Outward", "Inward", "Upward", "Longitudinal"]
    assert [str(t) for t in LOAD_TYPES] == ["Concentrated", "Distributed"]
    assert [str(d) for d in COMPONENT_DIRECTIONS] == ["Downward", "Horizontal"]


def test_every_direction_case_has_a_kind():
    assert kind(Direction.DOWNWARD) is Kind.DOWNWARD and kind(Direction.UPWARD) is Kind.UPWARD
    for d in (Direction.OUTWARD, Direction.INWARD, Direction.LONGITUDINAL, Direction.LATERAL):
        assert kind(d) is Kind.HORIZONTAL
    assert kind("Outward") is Kind.HORIZONTAL  # the member's text names it too


@pytest.mark.parametrize("direction", ["Outwrd", "outward", "Sideways", "", Direction.HORIZONTAL])
def test_a_direction_that_is_no_direction_case_has_no_kind(direction):
    # Direction.HORIZONTAL is the component load's direction: it has no demand at the post.
    with pytest.raises(ValueError, match="Demand: no direction case"):
        kind(direction)


@pytest.mark.parametrize("direction", ["Outwrd", "Sideways", Direction.HORIZONTAL])
def test_the_shared_demand_stops_on_an_unknown_direction(res, direction):
    """It used to compute anything not downward or upward as a horizontal case."""
    dead = Given("P_D", "P_D", res.loading.P_D, "D at the post", "Loading")
    arm = Given("L_post", 'L_"post"', res.loading.L_post, "Cantilever length", "Loading")
    with pytest.raises(ValueError, match="no direction case"):
        demand(Registry(), res.project, res.loading, direction, LoadType.CONCENTRATED, ASD, post.WORDING, dead, arm)


@pytest.mark.parametrize("direction", ["Upwrd", "Longitudinal", "Lateral"])
def test_check_1_bending_stops_on_a_direction_it_has_no_branch_for(res, direction):
    """Its last branch was a bare else that computed anything as upward."""
    reg = Registry()
    cap = checks.flexural_capacity(reg, res.rail, "A53 Gr B")
    with pytest.raises(ValueError, match="Check 1: no direction case"):
        checks._bending_case(reg, res.project, res.rail, res.loading, cap, direction, LoadType.CONCENTRATED)


def test_check_2_deflection_stops_on_a_direction_it_has_no_branch_for(res):
    with pytest.raises(ValueError, match="Check 2: no direction case 'Sideways'"):
        checks._deflection_case(Registry(), res.project, res.rail, res.loading, "Sideways", LoadType.CONCENTRATED)


@pytest.mark.parametrize("direction", ["Downward", "Upward", "Horizontal", "Outwrd"])
def test_check_5_moment_case_takes_horizontal_direction_cases_only(res, direction):
    reg = Registry()
    cap = post._capacity(reg, res.project, res.post)
    with pytest.raises(ValueError, match="no (horizontal )?direction case"):
        post._moment_case(reg, res.project, res.post, res.loading, cap, direction, LoadType.CONCENTRATED)


@pytest.mark.parametrize("direction", ["Outward", "Upward", "horizontal"])
def test_check_4a_stops_on_a_direction_the_component_load_does_not_have(res, direction):
    """Its second branch was a bare else that computed anything as horizontal."""
    reg = Registry()
    cap = checks.flexural_capacity(reg, res.inter, "A53 Gr B")
    with pytest.raises(ValueError, match=f"Check 4a: no component load direction '{direction}'"):
        intermediate._bending_case(reg, res.project, res.loading, cap, [], direction)
    with pytest.raises(ValueError, match=f"Check 4a: no component load direction '{direction}'"):
        intermediate._deflection_case(reg, res.project, res.inter, res.loading, res.project.rail_deflection, [],
                                      direction)


@pytest.mark.parametrize("load_type", ["Distributd", "Component", "concentrated"])
def test_an_unknown_guard_load_type_stops(res, load_type):
    """A load type that was not "Concentrated" used to compute as distributed."""
    reg = Registry()
    with pytest.raises(ValueError, match="no guard load type"):
        live_at_post(Sheet(reg), "V_L", "V_L", load_type, res.loading, res.project, "at the top of the post")
    cap = checks.flexural_capacity(reg, res.rail, "A53 Gr B")
    with pytest.raises(ValueError, match="Check 1: no guard load type"):
        checks._bending_case(reg, res.project, res.rail, res.loading, cap, Direction.DOWNWARD, load_type)
    with pytest.raises(ValueError, match="Check 2: no guard load type"):
        checks._deflection_case(reg, res.project, res.rail, res.loading, Direction.DOWNWARD, load_type)
