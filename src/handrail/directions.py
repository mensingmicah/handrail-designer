"""Direction cases and load types, each a fixed list of named values.

An enum is a fixed list of named values. Every place that branches on a
direction or a load type names the members it handles and ends by refusing
anything else, so a mistyped or unknown direction stops the calc with a
ValueError instead of computing as another case (issue #21, item 3). That
matters from slice 6 on, when longitudinal stops being identical to
transverse.

The members are also text (StrEnum): a member prints as its value
("Downward") and compares equal to that text, so the printed calc and the
test cases read them exactly as they read the plain strings before.
"""

from __future__ import annotations

from enum import StrEnum
from typing import NoReturn


class Direction(StrEnum):
    """A direction a load is applied in (docs/brief/loads-and-envelope.md)."""

    DOWNWARD = "Downward"
    OUTWARD = "Outward"
    INWARD = "Inward"
    UPWARD = "Upward"
    LONGITUDINAL = "Longitudinal"
    # The component load's horizontal case on the intermediate rail (S4-10).
    HORIZONTAL = "Horizontal"
    # The lateral anchor reaction set: any horizontal direction (S4-4).
    LATERAL = "Lateral"


class LoadType(StrEnum):
    CONCENTRATED = "Concentrated"
    DISTRIBUTED = "Distributed"
    COMPONENT = "Component"  # the intermediate rail's load: Checks 4a and 4b (S4-10)


class Kind(StrEnum):
    """The three kinds of direction case a demand is built for: the guard
    load vertical with the dead load (downward), vertical against it
    (upward), or horizontal with the dead load axial."""

    DOWNWARD = "downward"
    UPWARD = "upward"
    HORIZONTAL = "horizontal"


DOWNWARD, UPWARD, HORIZONTAL, LATERAL = (Direction.DOWNWARD, Direction.UPWARD, Direction.HORIZONTAL,
                                         Direction.LATERAL)
CONCENTRATED, DISTRIBUTED, COMPONENT = LoadType.CONCENTRATED, LoadType.DISTRIBUTED, LoadType.COMPONENT

# The guard load's direction cases, in envelope order (ties go to the first).
DIRECTIONS = (Direction.DOWNWARD, Direction.OUTWARD, Direction.INWARD, Direction.UPWARD, Direction.LONGITUDINAL)
# The guard load types, in envelope order.
LOAD_TYPES = (LoadType.CONCENTRATED, LoadType.DISTRIBUTED)
# The component load's two directions: Checks 4a and 4b (S4-10).
COMPONENT_DIRECTIONS = (Direction.DOWNWARD, Direction.HORIZONTAL)

# Every direction a demand can be built for, with its kind. Outward, inward
# and longitudinal (and the reaction sets' lateral) are the horizontal kind.
# The component load's HORIZONTAL has no entry: it has no demand at the post.
_KIND = {
    Direction.DOWNWARD: Kind.DOWNWARD,
    Direction.UPWARD: Kind.UPWARD,
    Direction.OUTWARD: Kind.HORIZONTAL,
    Direction.INWARD: Kind.HORIZONTAL,
    Direction.LONGITUDINAL: Kind.HORIZONTAL,
    Direction.LATERAL: Kind.HORIZONTAL,
}


def unknown(where: str, what: str, value: object, expected) -> NoReturn:
    """Stop on a direction or load type the code has no branch for. This is a
    bug in the tool, not an input error, so it is a ValueError with its full
    traceback (errors.py)."""
    raise ValueError(f"{where}: no {what} {str(value)!r}; expected one of {', '.join(expected)}")


def kind(direction: Direction) -> Kind:
    """The kind of a direction case. Stops on anything that is not one."""
    try:
        return _KIND[Direction(direction)]
    except (ValueError, KeyError):
        unknown("Demand", "direction case", direction, _KIND)
