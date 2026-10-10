"""Standard section properties, read from the derived AISC database files.

Properties are used exactly as published (docs/brief/checks.md, decisions). Each
value is returned as a pint quantity in the units the database states.
"""

import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from handrail.calc import Line, fmt_g, fmt_sig
from handrail.errors import InputError
from handrail.shapes_extract import PIPE_TOML, ROUND_HSS_TOML
from handrail.stops import Stop
from handrail.units import Q_


class ShapeNotFound(InputError):
    """The designation is not in the shapes database."""


# The source of a standard section: the citation printed beside every value
# taken from the database (Section.source).
DB = "AISC Shapes Database v16.0"
# The source of a custom section: its values are computed on the section
# properties page from the dimensions entered (tube.py).
CUSTOM = "Section properties (custom section)"


# Section families, as the per-joint tables name them (joints.py; S5-9).
# AISC pipe and round HSS are the ones the database lookup returns; the
# others are named here so each has its row in those tables, which say
# which slice brings it (S5-1).
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
    section: the shapes database for a standard section, the section
    properties page for a custom one, whose values are computed there from
    the dimensions entered (``computed`` holds those lines). A round section
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
    D_t: float   # D/t: as tabulated, or as computed for a custom section
    x: Axis
    y: Axis
    custom: bool = False               # computed from the dimensions entered, not looked up
    computed: tuple[Line, ...] = ()    # a custom section: the calc lines that computed its values

    @property
    def how(self) -> str:
        """How the section's values were arrived at, as a calc line's note says it."""
        return "computed" if self.custom else "tabulated"

    def ratio_text(self, ratio: float) -> str:
        """D/t as printed: a tabulated ratio as published, a computed one to four significant figures."""
        return fmt_sig(ratio) if self.custom else fmt_g(ratio)

    @property
    def W_text(self) -> str:
        """The weight in lb/ft as a note prints it: as published, or to four significant figures."""
        W = self.W.m_as("lbf/ft")
        return fmt_sig(W) if self.custom else f"{W:g}"

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
def _table(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


# The derived database files a designation is looked up in, in this order,
# with the family of the sections each one holds.
_DATABASE = ((PIPE_TOML, PIPE), (ROUND_HSS_TOML, ROUND_HSS))


def labels(family: str) -> list[str]:
    """Every designation of one family, in database order."""
    return [label for path, fam in _DATABASE if fam == family for label in _table(path)["shape"]]


def section(designation: str) -> Section:
    """Look up a standard section by its AISC designation (the database's
    AISC_Manual_Label), ignoring case and spaces: an AISC pipe or a round
    HSS. Every value is the published one, the outside diameter included
    (S5-4): nothing is read out of the designation."""
    key = designation.replace(" ", "").upper()
    for path, family in _DATABASE:
        table = _table(path)
        for label, row in table["shape"].items():
            if label.upper() == key:
                u = table["units"]
                q = lambda name, row=row, u=u: Q_(row[name], u[name])
                return Section(
                    label=label, family=family, source=DB,
                    W=q("W"), A=q("A"), OD=q("OD"),
                    tnom=q("tnom"), tdes=q("tdes"), D_t=row["D/t"],
                    x=Axis(I=q("Ix"), S=q("Sx"), Z=q("Zx"), r=q("rx")),
                    y=Axis(I=q("Iy"), S=q("Sy"), Z=q("Zy"), r=q("ry")),
                )
    raise ShapeNotFound(
        f"{designation!r} is not an AISC pipe or round HSS in {_table(PIPE_TOML)['source_file']}",
        stop=Stop.SECTION_NOT_FOUND,
    )
