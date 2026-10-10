"""Parse dimensions in the forms engineers type, and echo them back.

Accepted forms (docs/brief/inputs.md), with a bare number meaning inches:

    5' 6-1/8"    5'-6 1/8"    66.125 in    3 ft 6 in    42    1/2    7'

Anything ambiguous is rejected with a message rather than guessed at: a
misread dimension gives a plausible wrong number, which a checker would not
catch.
"""

import math
import re
from dataclasses import dataclass
from fractions import Fraction

from handrail.errors import InputError
from handrail.stops import Stop
from handrail.units import Q_


class DimensionError(InputError):
    """Raised when a dimension string cannot be read unambiguously."""


_DEC = r"(?:\d+(?:\.\d*)?|\.\d+)"
_FEET = rf"(?P<ft>{_DEC})\s*(?:'|′|’|ft\.?|feet|foot)"
# Inch value: whole and fraction ("6-1/8" or "6 1/8"), fraction alone, or decimal.
_INCH_VAL = (
    rf"(?:(?P<iw>\d+)(?:\s*-\s*|\s+)(?P<ifr>\d+/\d+)"
    rf"|(?P<ifr_only>\d+/\d+)"
    rf"|(?P<idec>{_DEC}))"
)
_INCH_UNIT = r"(?:\"|''|″|”|in\.?|inch|inches)"
_PATTERN = re.compile(
    rf"^\s*(?:{_FEET})?\s*-?\s*(?:{_INCH_VAL}\s*(?P<iu>{_INCH_UNIT})?)?\s*$",
    re.IGNORECASE,
)


def _fraction(text: str, entered: str) -> Fraction:
    num, den = text.split("/")
    if int(den) == 0:
        raise DimensionError(f"{entered!r}: fraction has a zero denominator", stop=Stop.DIMENSION_ZERO_DENOMINATOR)
    return Fraction(int(num), int(den))


def parse_inches(entered: str) -> float:
    """Return the dimension in inches as a float. Raises DimensionError."""
    if not isinstance(entered, str):
        entered = str(entered)
    text = entered.strip()
    if not text:
        raise DimensionError("empty dimension", stop=Stop.DIMENSION_EMPTY)
    if text.startswith("-"):
        raise DimensionError(f"{entered!r}: dimensions cannot be negative", stop=Stop.DIMENSION_NEGATIVE)

    m = _PATTERN.match(text)
    if m is None or (m["ft"] is None and not _has_inches(m)):
        raise DimensionError(
            f"{entered!r} is not a dimension I can read. Use forms like "
            "5' 6-1/8\", 66.125 in, 3 ft 6 in, or 42 (bare number = inches).", stop=Stop.DIMENSION_UNREADABLE
        )

    feet = float(m["ft"]) if m["ft"] is not None else 0.0
    if m["iw"] is not None:
        inches = int(m["iw"]) + float(_fraction(m["ifr"], entered))
    elif m["ifr_only"] is not None:
        inches = float(_fraction(m["ifr_only"], entered))
    elif m["idec"] is not None:
        inches = float(m["idec"])
    else:
        inches = 0.0

    if m["ft"] is not None and inches >= 12:
        raise DimensionError(
            f"{entered!r}: the inches part ({inches:g}) must be less than 12 "
            "when feet are given", stop=Stop.DIMENSION_INCHES_12_OR_MORE
        )
    return 12.0 * feet + inches


def _has_inches(m: re.Match) -> bool:
    return any(m[g] is not None for g in ("iw", "ifr_only", "idec"))


def format_ft_in(inches: float) -> str:
    """Architectural echo of a length: 42 -> 3'-6", 66.125 -> 5'-6 1/8".

    Fractions are shown to the nearest 1/16 only when the value is exactly a
    sixteenth; otherwise the inches are shown as a decimal so nothing is
    silently rounded. Lengths under 12 in are shown in inches alone.
    """
    if inches < 0:
        raise ValueError("negative length")
    sixteenths = inches * 16
    exact = math.isclose(sixteenths, round(sixteenths), abs_tol=1e-9)
    if exact:
        total16 = round(sixteenths)
        feet, rem16 = divmod(total16, 12 * 16)
        whole, frac16 = divmod(rem16, 16)
        frac = Fraction(frac16, 16)
        if frac == 0:
            in_text = f"{whole}"
        elif whole == 0 and feet == 0:
            in_text = f"{frac.numerator}/{frac.denominator}"
        else:
            in_text = f"{whole} {frac.numerator}/{frac.denominator}"
    else:
        feet = int(inches // 12)
        in_text = f"{inches - 12 * feet:.3f}".rstrip("0").rstrip(".")
    if feet == 0:
        return f'{in_text}"'
    return f"{feet}'-{in_text}\""


@dataclass(frozen=True)
class Dimension:
    """A dimension as entered, with its value and normalized echo."""

    entered: str
    value: Q_  # pint Quantity in inches

    @property
    def normalized(self) -> str:
        return format_ft_in(self.value.m_as("inch"))


def parse(entered: str) -> Dimension:
    """Parse a dimension string into a Dimension carrying a pint length."""
    return Dimension(entered=str(entered), value=Q_(parse_inches(entered), "inch"))
