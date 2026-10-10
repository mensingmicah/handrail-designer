"""The project: every input a calc runs from (slice 2 fields).

A project file is plain TOML that the engineer edits by hand. Reopening the
same file regenerates the same calc. Loading is per ASCE 7-22.

The reader is strict, because a typo must never turn into a plausible calc
for inputs the engineer didn't intend:

- every table accepts only the keys listed in SCHEMA; any other key stops
  with its name (a misspelled override would otherwise fall back silently
  to the code value);
- true/false fields must be real TOML booleans (the text "false" is not);
- loads and the deflection limits must be positive numbers;
- the post is required (every v1 calc checks one post), and the baseplate
  thickness must be less than the post height;
- both weld sizes are required, with no default (docs/brief/inputs.md);
- the baseplate's plan dimensions B and N are required, with no default (S4-6);
- the intermediate rail is in one of three states (S4-1): same as the top
  rail (the default), its own section, or none. Inputs that conflict with
  the state stop the calc, never silently ignored (docs/plans/slice-4.md):
  none = true with a section, grade, intermediate weld size or intermediate
  deflection limit; any of those given while same_as_top_rail is true;
  same_as_top_rail = false with no section. Its own section needs its own
  weld size.

Top-level [hand] and [verification] tables are allowed and ignored: test
cases keep their hand values and their kind in the same file as their
inputs (docs/brief/verification.md).
"""

from __future__ import annotations

import dataclasses
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from handrail import dimensions
from handrail.dimensions import Dimension
from handrail.errors import InputError
from handrail.units import Q_


class ProjectError(InputError):
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
    component: Q_ | None = None     # engineer override (lbf); None = code value (S4-3)
    uniform_exempt: bool = False
    exemption_statement: str = ""


@dataclass(frozen=True)
class Welds:
    """Fillet welds, all around (docs/brief/inputs.md, W12). The sizes are
    required; the electrode defaults to E70XX, the only one v1 accepts
    (checked in validate.py)."""

    rail_to_post: Dimension       # fillet leg size, top rail to post
    post_to_baseplate: Dimension  # fillet leg size, post to baseplate
    electrode: str = "E70XX"
    # Intermediate rail to post: its own section only, where it is required
    # (S4-8). Same as the top rail, the rail to post size applies.
    intermediate_rail_to_post: Dimension | None = None


@dataclass(frozen=True)
class Baseplate:
    """The baseplate's plan dimensions and grade. Its thickness t_p is in
    [geometry]. B is parallel to the rail and N perpendicular to it, both
    required (S4-6). A36 is the default and, for all of v1, the only grade
    accepted (W12)."""

    B: Dimension
    N: Dimension
    grade: str = "A36"


@dataclass(frozen=True)
class DeflectionLimit:
    ratio: float = 120  # limit is L / ratio
    bypass: bool = False


# Input defaults for the deflection limits (docs/brief/inputs.md): L/120 for
# the rail span, L/60 for the post cantilever. Engineering experience, not
# code values. The project reader starts from these, so each default is
# stated once.
RAIL_DEFLECTION = DeflectionLimit()
POST_DEFLECTION = DeflectionLimit(ratio=60)

# The intermediate rail's three input states (S4-1, docs/brief/checks.md).
SAME_AS_TOP, OWN_SECTION, NO_INTERMEDIATE = "same as top rail", "own section", "none"


@dataclass(frozen=True)
class IntermediateRail:
    """Same as the top rail (the default), its own section, or none (S4-1).
    ``member`` and ``deflection`` are its own in the own-section state only;
    same as the top rail, it takes the top rail's section and grade and
    follows Check 2's deflection limit (S4-2)."""

    state: str = SAME_AS_TOP
    member: Member | None = None
    deflection: DeflectionLimit = RAIL_DEFLECTION


@dataclass(frozen=True)
class Project:
    info: ProjectInfo
    span: Dimension
    top_rail: Member
    post: Member
    post_height: Dimension          # h: top of concrete to top rail centerline
    baseplate_thickness: Dimension  # t_p
    welds: Welds
    baseplate: Baseplate
    loads: Loads = field(default_factory=Loads)
    rail_deflection: DeflectionLimit = RAIL_DEFLECTION
    post_deflection: DeflectionLimit = POST_DEFLECTION
    intermediate_rail: IntermediateRail = field(default_factory=IntermediateRail)

    @property
    def intermediate_member(self) -> Member | None:
        """The intermediate rail's section and grade: the top rail's, its own, or None."""
        state = self.intermediate_rail.state
        if state == NO_INTERMEDIATE:
            return None
        return self.top_rail if state == SAME_AS_TOP else self.intermediate_rail.member


# Allowed keys per table. A dict value is a sub-table.
SCHEMA = {
    "project": {"name": None, "phase": None, "description": None, "references": None, "assumptions": None},
    "geometry": {"span": None, "post_height": None, "baseplate_thickness": None},
    "top_rail": {"section": None, "grade": None},
    "post": {"section": None, "grade": None},
    "intermediate_rail": {"same_as_top_rail": None, "none": None, "section": None, "grade": None},
    "baseplate": {"B": None, "N": None, "grade": None},
    "welds": {"rail_to_post": None, "post_to_baseplate": None, "electrode": None,
              "intermediate_rail_to_post": None},
    "loads": {"concentrated_lb": None, "uniform_plf": None, "component_lb": None,
              "uniform_exemption": {"applies": None, "statement": None}},
    "deflection": {"rail": {"limit_L_over": None, "bypass": None},
                   "post": {"limit_L_over": None, "bypass": None},
                   "intermediate_rail": {"limit_L_over": None, "bypass": None}},
    "hand": "ignored",
    "verification": "ignored",
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


def _dimension(table: dict, key: str, where: str) -> Dimension:
    """A required, positive dimension in the forms docs/brief/inputs.md accepts."""
    raw = _need(table, key, where)
    if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
        raise ProjectError(f"project file: '{where}.{key}' must be a dimension, not {raw!r}")
    try:
        dim = dimensions.parse(str(raw))
    except dimensions.DimensionError as e:
        raise ProjectError(f"[{where}] {key}: {e}") from None
    if dim.value.m_as("inch") <= 0:
        raise ProjectError(f"[{where}] {key} must be greater than zero")
    return dim


def _member(raw: dict, where: str) -> Member:
    t = _need(raw, where, "top level")
    return Member(
        section=_str(_need(t, "section", where), f"{where}.section"),
        grade=_str(t.get("grade", "A53 Gr B"), f"{where}.grade"),  # brief: pipe defaults to A53 Gr B
    )


def _given(table: dict, where: str, fields: dict) -> dict:
    """Keyword arguments for the optional keys the file gives.

    ``fields`` maps each file key to (dataclass field, reader). A key the file
    leaves out is left out here too, so the dataclass default applies: each
    default is stated once, on its dataclass (or its default instance).
    """
    return {name: read(table[key], f"{where}.{key}")
            for key, (name, read) in fields.items() if key in table}


def _lbf(value, name: str) -> Q_:
    return Q_(_positive(value, name), "lbf")


def _lbf_per_ft(value, name: str) -> Q_:
    return Q_(_positive(value, name), "lbf/ft")


def _deflection_limit(raw: dict, member: str, default: DeflectionLimit) -> DeflectionLimit:
    d = raw.get("deflection", {}).get(member, {})
    given = _given(d, f"deflection.{member}",
                   {"limit_L_over": ("ratio", _positive), "bypass": ("bypass", _bool)})
    return dataclasses.replace(default, **given)


def _intermediate_rail(raw: dict, top_rail: Member, welds: Welds) -> IntermediateRail:
    """The intermediate rail's state, refusing inputs that conflict with it."""
    t = raw.get("intermediate_rail", {})
    w = "intermediate_rail"
    none = _bool(t["none"], f"{w}.none") if "none" in t else False
    same_given = "same_as_top_rail" in t
    same = _bool(t["same_as_top_rail"], f"{w}.same_as_top_rail") if same_given else True  # the default (S4-1)
    section = _str(t["section"], f"{w}.section") if "section" in t else None
    grade = _str(t["grade"], f"{w}.grade") if "grade" in t else None
    own_inputs = [name for name, given in (
        ("[intermediate_rail] section", section is not None),
        ("[intermediate_rail] grade", grade is not None),
        ("[welds] intermediate_rail_to_post", welds.intermediate_rail_to_post is not None),
        ("[deflection.intermediate_rail]", "intermediate_rail" in raw.get("deflection", {})),
    ) if given]

    if none:
        if same_given and same:
            raise ProjectError("[intermediate_rail] none = true and same_as_top_rail = true contradict each "
                               "other: choose one")
        if own_inputs:
            raise ProjectError(f"[intermediate_rail] none = true, but {', '.join(own_inputs)} is given: there is "
                               f"no intermediate rail to apply it to. Remove it, or set none = false.")
        return IntermediateRail(state=NO_INTERMEDIATE)
    if same:
        if own_inputs:
            raise ProjectError(
                f"[intermediate_rail] same_as_top_rail = true{'' if same_given else ' (the default)'}, but "
                f"{', '.join(own_inputs)} is given. Same as the top rail, the intermediate rail takes the top "
                f"rail's section, grade and rail to post weld size, and follows the top rail's deflection limit. "
                f"Set same_as_top_rail = false to give it its own, or remove the input."
            )
        return IntermediateRail(state=SAME_AS_TOP)
    if section is None:
        raise ProjectError("[intermediate_rail] same_as_top_rail = false needs a section "
                           "(or none = true for no intermediate rail)")
    if welds.intermediate_rail_to_post is None:
        raise ProjectError("[welds] is missing 'intermediate_rail_to_post', required when the intermediate rail "
                           "has its own section (same_as_top_rail = false)")
    return IntermediateRail(
        state=OWN_SECTION,
        member=Member(section=section, grade=grade if grade is not None else top_rail.grade),  # S4-1
        deflection=_deflection_limit(raw, "intermediate_rail", RAIL_DEFLECTION),
    )


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
        **_given(p, "project", {"phase": ("phase", _str), "description": ("description", _str),
                                "references": ("references", _str_list),
                                "assumptions": ("assumptions", _str_list)}),
    )

    g = _need(raw, "geometry", "top level")
    span = _dimension(g, "span", "geometry")
    h = _dimension(g, "post_height", "geometry")
    tp = _dimension(g, "baseplate_thickness", "geometry")
    if not tp.value < h.value:
        raise ProjectError(
            f"[geometry] baseplate_thickness ({tp.entered}) must be less than "
            f"post_height ({h.entered})"
        )

    top_rail = _member(raw, "top_rail")
    post = _member(raw, "post")

    wt = _need(raw, "welds", "top level")
    welds = Welds(
        rail_to_post=_dimension(wt, "rail_to_post", "welds"),
        post_to_baseplate=_dimension(wt, "post_to_baseplate", "welds"),
        **_given(wt, "welds", {"electrode": ("electrode", _str)}),
        **({"intermediate_rail_to_post": _dimension(wt, "intermediate_rail_to_post", "welds")}
           if "intermediate_rail_to_post" in wt else {}),
    )
    bt = _need(raw, "baseplate", "top level")
    baseplate = Baseplate(B=_dimension(bt, "B", "baseplate"), N=_dimension(bt, "N", "baseplate"),
                          **_given(bt, "baseplate", {"grade": ("grade", _str)}))
    intermediate = _intermediate_rail(raw, top_rail, welds)

    ld = raw.get("loads", {})
    ex = ld.get("uniform_exemption", {})
    loads = Loads(
        **_given(ld, "loads", {"concentrated_lb": ("concentrated", _lbf),
                               "uniform_plf": ("uniform", _lbf_per_ft),
                               "component_lb": ("component", _lbf)}),
        **_given(ex, "loads.uniform_exemption", {"applies": ("uniform_exempt", _bool),
                                                 "statement": ("exemption_statement", _str)}),
    )
    if loads.uniform_exempt and not loads.exemption_statement.strip():
        raise ProjectError(
            "[loads.uniform_exemption] applies = true needs a statement of why the "
            "guard is exempt from the uniform load"
        )

    return Project(
        info=info, span=span, top_rail=top_rail, post=post,
        post_height=h, baseplate_thickness=tp, welds=welds, baseplate=baseplate, loads=loads,
        rail_deflection=_deflection_limit(raw, "rail", RAIL_DEFLECTION),
        post_deflection=_deflection_limit(raw, "post", POST_DEFLECTION),
        intermediate_rail=intermediate,
    )
