"""Standard section properties, read from the derived AISC database files.

Properties are used exactly as published (docs/brief/checks.md, decisions). Each
value is returned as a pint quantity in the units the database states.
"""

import tomllib
from dataclasses import dataclass
from functools import cache

from handrail.errors import InputError
from handrail.shapes_extract import PIPE_TOML
from handrail.stops import Stop
from handrail.units import Q_


class ShapeNotFound(InputError):
    """The designation is not in the shapes database."""


# The citation printed beside every value taken from the database.
DB = "AISC Shapes Database v16.0"


# Section families, as the per-joint tables name them (joints.py; S5-9).
# AISC pipe is the only one a project can enter so far; the others are
# named here so each has its row in those tables, which say which slice
# brings it (S5-1).
PIPE = "AISC pipe"
ROUND_HSS = "round HSS"
ROUND_TUBE = "custom round tube"
RECT_HSS = "rectangular HSS"
RECT_TUBE = "custom rectangular tube"
ROUND_BAR = "solid round bar"
RECT_BAR = "solid rectangular bar"


@dataclass(frozen=True)
class PipeSection:
    label: str   # AISC_Manual_Label, as printed in the calc
    W: Q_        # nominal weight
    A: Q_
    OD: Q_
    tnom: Q_
    tdes: Q_
    D_t: float   # D/t as tabulated
    I: Q_
    S: Q_
    Z: Q_
    r: Q_        # radius of gyration (rx; equal to ry for a pipe)
    family: str = PIPE


@cache
def _pipe_table() -> dict:
    with open(PIPE_TOML, "rb") as f:
        return tomllib.load(f)


def pipe(designation: str) -> PipeSection:
    """Look up an AISC pipe by designation, ignoring case and spaces."""
    table = _pipe_table()
    key = designation.replace(" ", "").upper()
    for label, row in table["shape"].items():
        if label.upper() == key:
            u = table["units"]
            q = lambda name: Q_(row[name], u[name])  # noqa: E731
            return PipeSection(
                label=label,
                W=q("W"), A=q("A"), OD=q("OD"),
                tnom=q("tnom"), tdes=q("tdes"), D_t=row["D/t"],
                I=q("Ix"), S=q("Sx"), Z=q("Zx"), r=q("rx"),
            )
    raise ShapeNotFound(
        f"{designation!r} is not an AISC pipe in {table['source_file']}", stop=Stop.SECTION_NOT_FOUND
    )
