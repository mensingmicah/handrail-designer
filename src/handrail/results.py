"""What a calc produces: the cases of each check, the checks, the loading,
and the whole result the report prints.

These types hold results only. The engineering that fills them is in the
check modules (rail.py, intermediate.py, post.py, welds.py), reactions.py
and loading.py; engine.py runs them in order.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from handrail.calc import Comparison, Line, Term, compare, fmt_ratio, term
from handrail.directions import Direction, LoadType
from handrail.project import Project
from handrail.shapes import PipeSection
from handrail.units import Q_

if TYPE_CHECKING:
    from handrail.reactions import Reactions


@dataclass
class Case:
    direction: Direction
    load_type: LoadType | None
    status: str  # "checked", "exempt", "not checked"
    combination: str = ""
    demand: Any = None
    capacity: Any = None
    ratio: float | None = None
    lines: list[Line] = field(default_factory=list)
    remark: str = ""

    @property
    def label(self) -> str:
        return f"{self.direction}, {self.load_type.lower()}" if self.load_type else self.direction


@dataclass
class Check:
    number: int | str    # "4a" and "4b": the intermediate rail's two parts
    title: str
    demand_label: str    # Typst math
    capacity_label: str  # Typst math
    cases: list[Case] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    summary_flag: str = ""  # short flag text printed in the summary row (e.g. Lc/r above 200)
    failures: list[str] = field(default_factory=list)  # NG whatever the ratio (a weld below minimum size)
    bypassed: bool = False
    derived_lengths: list[Line] = field(default_factory=list)  # listed on the Dimensions page
    # A check not computed (Check 4a or 4b): the line printed in place of the
    # envelope, and the summary row's result, with no ratio and no OK or NG
    # of its own ("Controlled by Checks 1 and 2", "None").
    observation: str = ""
    observation_lines: list[Line] = field(default_factory=list)  # printed under it, so its values can be traced
    result: str = ""

    @property
    def checked(self) -> list[Case]:
        return [c for c in self.cases if c.status == "checked"]

    @property
    def controlling(self) -> Case | None:
        # Highest ratio; ties go to the first case in envelope order.
        best = None
        for c in self.checked:
            # A checked case always has its ratio.
            if best is None or cast(float, c.ratio) > cast(float, best.ratio):
                best = c
        return best

    @property
    def computed(self) -> bool:
        return not self.bypassed and not self.result

    @property
    def within_unity(self) -> Comparison:
        """The controlling ratio against 1.00: one comparison gives both the
        verdict and the sign the closing line prints (ADR 0002)."""
        ratio = cast(Case, self.controlling).ratio  # asked only of a computed check, which has one
        return compare(term('"Ratio"', ratio, fmt_ratio), "<=", Term("1.00", 1.0))

    @property
    def ok(self) -> bool:
        # A check not computed defers to the checks it names; it fails nothing itself.
        return not self.computed or (not self.failures and self.within_unity.holds)

    @property
    def verdict(self) -> str:
        if self.bypassed:
            return "Bypassed by engineer"
        if self.result:
            return self.result
        return "OK" if self.ok else "NG"


@dataclass
class Loading:
    P: Any          # concentrated guard load
    w_L: Any        # uniform guard load, or None when exempt
    w_D: Any        # top rail self-weight
    L_post: Any     # post cantilever length, h - t_p
    D_rail: Any     # top rail dead load delivered to the post, w_D times the span
    P_D: Any        # axial dead load at the top of the baseplate (D at the post)
    exempt: bool
    exemption_statement: str
    lines: list[Line]
    derived_lengths: list[Line]  # listed on the Dimensions page
    # The intermediate rail's self-weight and its dead load delivered to the
    # post, w_D,int times the span; None when there is no intermediate rail.
    w_D_int: Q_ | None = None
    D_int: Q_ | None = None
    D_post: Q_ | None = None  # the post's dead load, W over h - t_p (the reaction sets' D breakdown)
    P_c: Q_ | None = None     # the component load on the intermediate rail (S4-3); None without one


@dataclass
class Results:
    project: Project
    rail: PipeSection
    post: PipeSection
    loading: Loading
    section_lines: list[Line]       # top rail
    post_section_lines: list[Line]
    checks: list[Check]
    inter: PipeSection | None = None  # the intermediate rail's section: the top rail's, its own, or None
    inter_section_lines: list[Line] = field(default_factory=list)  # its own section only
    reactions: Reactions | None = None  # the anchor reaction sets

    def check(self, number: int | str) -> Check:
        return next(c for c in self.checks if c.number == number)

    @property
    def derived_lengths(self) -> list[tuple[Line, str]]:
        """Each derived length with where it is computed: the line itself, so the
        Dimensions page prints the formula that computed the value (ADR 0002)."""
        out = [(ln, "Loading") for ln in self.loading.derived_lengths]
        out += [(ln, f"Check {c.number}") for c in self.checks for ln in c.derived_lengths]
        return out
