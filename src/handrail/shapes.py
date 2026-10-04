"""Standard section properties, read from the derived AISC database files.

Properties are used exactly as published (docs/brief/checks.md, decisions). Each
value is returned as a pint quantity in the units the database states.
"""

import tomllib
from dataclasses import dataclass
from functools import cache

from handrail.shapes_extract import PIPE_TOML
from handrail.units import Q_


class ShapeNotFound(KeyError):
    pass


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
        f"{designation!r} is not an AISC pipe in {table['source_file']}"
    )
