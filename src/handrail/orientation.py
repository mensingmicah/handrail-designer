"""How a member is built into the guard: which principal axis each load
bends, and its outside dimensions in the guard's directions
(docs/brief/inputs.md, S6-2).

A rectangular section is the same section whichever way round it is built;
the database lists every one with H >= B and x the strong axis. The member's
``long_side`` says which way round, and everything a check needs follows
from it: the axis a vertical or a horizontal load bends in a rail, the axis
a transverse or a longitudinal load bends in a post, the rail's depth and
width, and the post's dimensions across and along the rail.

A round section has one axis and one dimension, and a square one has two
equal axes: each still gets an answer here, so a check asks the same
question of every member.
"""

from __future__ import annotations

from dataclasses import dataclass

from handrail.project import HORIZONTAL, PARALLEL, PERPENDICULAR, VERTICAL
from handrail.shapes import Axis, Section
from handrail.units import Q_

X, Y = "x", "y"  # the strong and the weak principal axis of a rectangular section


@dataclass(frozen=True)
class RailAxes:
    """A rail as built: the axis each load bends, and its depth and width."""

    vertical: str    # the axis a vertical load bends
    horizontal: str  # the axis a horizontal load bends
    depth: Q_        # outside dimension in the vertical direction
    width: Q_        # outside dimension in the horizontal direction


@dataclass(frozen=True)
class PostAxes:
    """A post as built: the axis each lateral load bends, and its plan dimensions."""

    transverse: str     # the axis a load across the guard (outward, inward) bends
    longitudinal: str   # the axis a load along the rail bends
    perpendicular: Q_   # outside dimension perpendicular to the rail
    parallel: Q_        # outside dimension parallel to the rail


def axis(sec: Section, name: str) -> Axis:
    """The section's properties about the axis of this name."""
    if name == X:
        return sec.x
    if name == Y:
        return sec.y
    raise ValueError(f"no principal axis {name!r}; expected one of {X}, {Y}")


def _long_side_is(long_side: str, first: str, second: str, sec: Section) -> bool:
    """Whether the long side lies in the first of the two directions.
    members.resolve requires the word of every member that needs one, so
    anything else here is a bug in the tool, not an input error."""
    if long_side == first:
        return True
    if long_side == second:
        return False
    raise ValueError(f"{sec.label}: long_side {long_side!r}; expected {first!r} or {second!r}")


def rail_axes(sec: Section, long_side: str) -> RailAxes:
    """A top rail or an intermediate rail. Long side vertical: a vertical
    load bends the strong axis, a horizontal load the weak one."""
    if sec.is_round:
        return RailAxes(X, X, sec.OD, sec.OD)
    r = sec.rect
    if r.square:
        return RailAxes(X, Y, r.H, r.B)
    if _long_side_is(long_side, VERTICAL, HORIZONTAL, sec):
        return RailAxes(X, Y, r.H, r.B)
    return RailAxes(Y, X, r.B, r.H)


def post_axes(sec: Section, long_side: str) -> PostAxes:
    """A post. Long side perpendicular to the rail: a load across the guard
    bends the strong axis, a load along the rail the weak one."""
    if sec.is_round:
        return PostAxes(X, X, sec.OD, sec.OD)
    r = sec.rect
    if r.square:
        return PostAxes(X, Y, r.H, r.B)
    if _long_side_is(long_side, PERPENDICULAR, PARALLEL, sec):
        return PostAxes(X, Y, r.H, r.B)
    return PostAxes(Y, X, r.B, r.H)
