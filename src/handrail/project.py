"""The project: every input a calc runs from (slice 1 fields only).

A project file is plain TOML that the engineer edits by hand. Reopening the
same file regenerates the same calc. Loading is per ASCE 7-22.

The reader is strict, because a typo must never turn into a plausible calc
for inputs the engineer didn't intend:

- every table accepts only the keys listed in SCHEMA; any other key stops
  with its name (a misspelled override would otherwise fall back silently
  to the code value);
- true/false fields must be real TOML booleans (the text "false" is not);
- loads and the deflection limit must be positive numbers.

A top-level [hand] table is allowed and ignored: hand-calc test cases keep
their hand values in the same file as their inputs.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from handrail import dimensions
from handrail.dimensions import Dimension
from handrail.units import Q_


class ProjectError(ValueError):
    """The project file is missing a field or has a value the tool can't use."""


@dataclass(frozen=True)
class ProjectInfo:
    name: str
    phase: str = ""
    description: str = ""
    references: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()  # added by the engineer; the tool's own are locked


@dataclass(frozen=True)
class Member:
    section: str  # AISC designation, e.g. "Pipe1-1/2STD"
    grade: str


@dataclass(frozen=True)
class Loads:
    concentrated: Q_ | None = None  # engineer override (lbf); None = code value from the registry
    uniform: Q_ | None = None       # engineer override (lbf/ft); None = code value
    uniform_exempt: bool = False
    exemption_statement: str = ""


@dataclass(frozen=True)
class DeflectionLimit:
    ratio: float = 120  # limit is L / ratio
    bypass: bool = False


@dataclass(frozen=True)
class Project:
    info: ProjectInfo
    span: Dimension
    top_rail: Member
    loads: Loads = field(default_factory=Loads)
    rail_deflection: DeflectionLimit = field(default_factory=DeflectionLimit)


# Allowed keys per table. A dict value is a sub-table.
SCHEMA = {
    "project": {"name": None, "phase": None, "description": None, "references": None, "assumptions": None},
    "geometry": {"span": None},
    "top_rail": {"section": None, "grade": None},
    "loads": {"concentrated_lb": None, "uniform_plf": None,
              "uniform_exemption": {"applies": None, "statement": None}},
    "deflection": {"rail": {"limit_L_over": None, "bypass": None}},
    "hand": "ignored",
}


def _check_keys(table: dict, schema: dict, where: str) -> None:
    for key, value in table.items():
        name = f"{where}.{key}" if where else key
        if key not in schema:
            allowed = ", ".join(schema)
            what = "table" if isinstance(value, dict) else "key"
            raise ProjectError(
                f"project file: unknown {what} '{name}'. "
                f"Allowed {'here' if where else 'at top level'}: {allowed}"
            )
        sub = schema[key]
        if isinstance(sub, dict):
            if not isinstance(value, dict):
                raise ProjectError(f"project file: '{name}' must be a table [{name}]")
            _check_keys(value, sub, name)


def _need(table: dict, key: str, where: str):
    if key not in table:
        raise ProjectError(f"project file: [{where}] is missing '{key}'")
    return table[key]


def _str(value, name: str) -> str:
    if not isinstance(value, str):
        raise ProjectError(f"project file: '{name}' must be text in quotes, not {value!r}")
    return value


def _str_list(value, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ProjectError(f"project file: '{name}' must be a list of quoted text, e.g. [\"...\"]")
    return tuple(value)


def _bool(value, name: str) -> bool:
    # bool("false") is True in Python, so text must never be read as a boolean.
    if not isinstance(value, bool):
        raise ProjectError(
            f"project file: '{name}' must be true or false without quotes, not {value!r}"
        )
    return value


def _positive(value, name: str) -> float:
    # bool is a subclass of int in Python; exclude it explicitly.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProjectError(f"project file: '{name}' must be a number without quotes, not {value!r}")
    if not value > 0:
        raise ProjectError(f"project file: '{name}' must be greater than zero, not {value!r}")
    return value


def load(path: str | Path) -> Project:
    path = Path(path)
    try:
        with open(path, "rb") as f:
            raw = tomllib.load(f)
    except FileNotFoundError:
        raise ProjectError(f"project file not found: {path}") from None
    except tomllib.TOMLDecodeError as e:
        raise ProjectError(f"project file {path} is not valid TOML: {e}") from None
    return from_dict(raw)


def from_dict(raw: dict) -> Project:
    _check_keys(raw, SCHEMA, "")

    p = _need(raw, "project", "top level")
    info = ProjectInfo(
        name=_str(_need(p, "name", "project"), "project.name"),
        phase=_str(p.get("phase", ""), "project.phase"),
        description=_str(p.get("description", ""), "project.description"),
        references=_str_list(p.get("references", []), "project.references"),
        assumptions=_str_list(p.get("assumptions", []), "project.assumptions"),
    )

    g = _need(raw, "geometry", "top level")
    span_raw = _need(g, "span", "geometry")
    if isinstance(span_raw, bool) or not isinstance(span_raw, (str, int, float)):
        raise ProjectError(f"project file: 'geometry.span' must be a dimension, not {span_raw!r}")
    try:
        span = dimensions.parse(str(span_raw))
    except dimensions.DimensionError as e:
        raise ProjectError(f"[geometry] span: {e}") from None
    if span.value.m_as("inch") <= 0:
        raise ProjectError("[geometry] span must be greater than zero")

    r = _need(raw, "top_rail", "top level")
    top_rail = Member(
        section=_str(_need(r, "section", "top_rail"), "top_rail.section"),
        grade=_str(r.get("grade", "A53 Gr B"), "top_rail.grade"),  # brief: pipe defaults to A53 Gr B
    )

    ld = raw.get("loads", {})
    ex = ld.get("uniform_exemption", {})
    P = ld.get("concentrated_lb")
    w = ld.get("uniform_plf")
    loads = Loads(
        concentrated=None if P is None else Q_(_positive(P, "loads.concentrated_lb"), "lbf"),
        uniform=None if w is None else Q_(_positive(w, "loads.uniform_plf"), "lbf/ft"),
        uniform_exempt=_bool(ex.get("applies", False), "loads.uniform_exemption.applies"),
        exemption_statement=_str(ex.get("statement", ""), "loads.uniform_exemption.statement"),
    )
    if loads.uniform_exempt and not loads.exemption_statement.strip():
        raise ProjectError(
            "[loads.uniform_exemption] applies = true needs a statement of why the "
            "guard is exempt from the uniform load"
        )

    d = raw.get("deflection", {}).get("rail", {})
    defl = DeflectionLimit(
        ratio=_positive(d.get("limit_L_over", 120), "deflection.rail.limit_L_over"),
        bypass=_bool(d.get("bypass", False), "deflection.rail.bypass"),
    )
    return Project(info=info, span=span, top_rail=top_rail, loads=loads, rail_deflection=defl)
