"""The project: every input a calc runs from (slice 1 fields only).

A project file is plain TOML that the engineer edits by hand. Reopening the
same file regenerates the same calc. Loading is per ASCE 7-22.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from handrail import dimensions
from handrail.dimensions import Dimension


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
    concentrated_lbf: float | None = None  # None = code value from the registry
    uniform_plf: float | None = None
    uniform_exempt: bool = False
    exemption_statement: str = ""


@dataclass(frozen=True)
class DeflectionLimit:
    ratio: float = 120.0  # limit is L / ratio
    bypass: bool = False


@dataclass(frozen=True)
class Project:
    info: ProjectInfo
    span: Dimension
    top_rail: Member
    loads: Loads = field(default_factory=Loads)
    rail_deflection: DeflectionLimit = field(default_factory=DeflectionLimit)


def _need(table: dict, key: str, where: str):
    if key not in table:
        raise ProjectError(f"project file: [{where}] is missing '{key}'")
    return table[key]


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
    p = _need(raw, "project", "top level")
    info = ProjectInfo(
        name=_need(p, "name", "project"),
        phase=p.get("phase", ""),
        description=p.get("description", ""),
        references=tuple(p.get("references", ())),
        assumptions=tuple(p.get("assumptions", ())),
    )
    g = _need(raw, "geometry", "top level")
    try:
        span = dimensions.parse(_need(g, "span", "geometry"))
    except dimensions.DimensionError as e:
        raise ProjectError(f"[geometry] span: {e}") from None
    if span.value.m_as("inch") <= 0:
        raise ProjectError("[geometry] span must be greater than zero")

    r = _need(raw, "top_rail", "top level")
    top_rail = Member(section=_need(r, "section", "top_rail"), grade=r.get("grade", "A53 Gr B"))

    ld = raw.get("loads", {})
    ex = ld.get("uniform_exemption", {})
    loads = Loads(
        concentrated_lbf=ld.get("concentrated_lb"),
        uniform_plf=ld.get("uniform_plf"),
        uniform_exempt=bool(ex.get("applies", False)),
        exemption_statement=ex.get("statement", ""),
    )
    if loads.uniform_exempt and not loads.exemption_statement.strip():
        raise ProjectError(
            "[loads.uniform_exemption] applies = true needs a statement of why the "
            "guard falls under the ASCE 7-22 §4.5.1.1 exemption"
        )

    d = raw.get("deflection", {}).get("rail", {})
    defl = DeflectionLimit(ratio=float(d.get("limit_L_over", 120)), bypass=bool(d.get("bypass", False)))
    if defl.ratio <= 0:
        raise ProjectError("[deflection.rail] limit_L_over must be greater than zero")
    return Project(info=info, span=span, top_rail=top_rail, loads=loads, rail_deflection=defl)
