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


# The source of a standard section: the citation printed beside every value
# taken from the database (Section.source).
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
class Axis:
    """A section's properties about one principal axis."""

    I: Q_   # moment of inertia
    S: Q_   # elastic section modulus
    Z: Q_   # plastic section modulus
    r: Q_   # radius of gyration


@dataclass(frozen=True)
class Section:
    """One type for every section (S5-1): its family, where its values come
    from, and its properties about both principal axes.

    ``source`` is the citation printed beside every value taken from the
    section: the shapes database for a standard section. A round section
    has x = y. I, S, Z and r below read the x axis, the single value every
    check reads today; which axis each check reads for a section that is
    not round is slice 6's decision.
    """

    label: str   # AISC_Manual_Label, as printed in the calc
    family: str  # one of the families the per-joint tables name (joints.py)
    source: str  # the citation printed beside each of its values
    W: Q_        # nominal weight
    A: Q_
    OD: Q_
    tnom: Q_
    tdes: Q_
    D_t: float   # D/t as tabulated
    x: Axis
    y: Axis

    @property
    def I(self) -> Q_:
        return self.x.I

    @property
    def S(self) -> Q_:
        return self.x.S

    @property
    def Z(self) -> Q_:
        return self.x.Z

    @property
    def r(self) -> Q_:
        return self.x.r


@cache
def _pipe_table() -> dict:
    with open(PIPE_TOML, "rb") as f:
        return tomllib.load(f)


def pipe(designation: str) -> Section:
    """Look up an AISC pipe by designation, ignoring case and spaces."""
    table = _pipe_table()
    key = designation.replace(" ", "").upper()
    for label, row in table["shape"].items():
        if label.upper() == key:
            u = table["units"]
            q = lambda name, row=row, u=u: Q_(row[name], u[name])
            return Section(
                label=label, family=PIPE, source=DB,
                W=q("W"), A=q("A"), OD=q("OD"),
                tnom=q("tnom"), tdes=q("tdes"), D_t=row["D/t"],
                x=Axis(I=q("Ix"), S=q("Sx"), Z=q("Zx"), r=q("rx")),
                y=Axis(I=q("Iy"), S=q("Sy"), Z=q("Zy"), r=q("ry")),
            )
    raise ShapeNotFound(
        f"{designation!r} is not an AISC pipe in {table['source_file']}", stop=Stop.SECTION_NOT_FOUND
    )
