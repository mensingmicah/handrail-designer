"""Which section families may meet at each joint (docs/brief/inputs.md, S5-9).

One table per joint. A cell is either allowed or a stop, and a pair of
families with no cell stops too: nothing unlisted is ever computed
(binding; Micah, 2026-10-09). The tables are data, printed in
docs/brief/stops.md, and tests/test_stops.py holds this module and that
file to each other.

The joints:

- Check 3 joint: the top rail is the chord and the post the branch.
- Check 4b joint: the post is the chord and the intermediate rail the
  branch. Same table as the Check 3 joint.
- Check 7 joint: the post on the baseplate (A36 plate, the only baseplate).

An allowed chord and branch pair rests on W2's branch rule (k_ds = 1.0) and
on the weld line of its pair (W1 for round on round, Table K5.1 for
rectangular on rectangular, the branch's outline where the two are mixed;
S6-8, S6-9). An allowed post on the baseplate is welded all around, or, a
rectangular post, on the pattern entered (S6-6); the engineer may elect
W2's directional increase for a round post only. A stop cell names the
slice that brings its family (S5-1).

Slice 6 allows every pair of the hollow families, round and rectangular,
at the chord and branch joints, a round member with a rectangular one
included (S6-9), and each of them as a post on the baseplate. Rules about
dimensions and grades, not families, are ordinary stops in validate.py:
the width rule and the Chapter K limits of applicability.
"""

from __future__ import annotations

from dataclasses import dataclass

from handrail.errors import InputError
from handrail.shapes import PIPE, RECT_BAR, RECT_HSS, RECT_TUBE, ROUND_BAR, ROUND_HSS, ROUND_TUBE, Section
from handrail.stops import Stop

# The families in table order, grouped as the tables print them: families
# in one group share every cell.
GROUPS: tuple[tuple[str, ...], ...] = ((PIPE,), (ROUND_HSS,), (ROUND_TUBE,), (RECT_HSS, RECT_TUBE),
                                       (ROUND_BAR, RECT_BAR))
BROUGHT_BY = "S5-1"  # the decision that says which slice brings each family


@dataclass(frozen=True)
class Cell:
    """One cell of a joint's table: allowed, or a stop naming the slice
    that brings the family and the message the stop gives."""

    allowed: bool
    slice: int | None = None   # a stop cell: the slice that brings the family
    message: str = ""          # a stop cell: the message, with {member}, {label} and {family} of the section it names

    @property
    def text(self) -> str:
        """The cell as docs/brief/stops.md prints it."""
        return "allowed" if self.allowed else f"stop: slice {self.slice}"


ALLOWED = Cell(True)

# The rail to post joints are decided for hollow members, round and
# rectangular and the two mixed (W1 to W10, S6-8, S6-9); a member with no
# wall is slice 7's.
_NOT_HOLLOW = ("{member} {label} ({family}) is not a hollow section. The rail to post welds and the wall they land on "
               "have been decided only for round and rectangular hollow members, not for this section.")
# The post to baseplate weld likewise (W2, S6-6).
_NO_BASE_WELD_RULE = ("{label} ({family}): the post to baseplate weld of this section family has not been decided. "
                      "The tool checks it only for round and rectangular hollow posts.")


def _stop(slice: int, message: str) -> Cell:
    return Cell(False, slice, message)


def _by_family(rows: dict[str, list[Cell]]) -> dict[tuple[str, str], Cell]:
    """A chord and branch table written by group, as a cell for every pair of families."""
    table = {}
    for chord_group, cells in zip(GROUPS, rows.values(), strict=True):
        for branch_group, cell in zip(GROUPS, cells, strict=True):
            for chord in chord_group:
                for branch in branch_group:
                    table[(chord, branch)] = cell
    return table


_S7 = _stop(7, _NOT_HOLLOW)

# Chord (row) and branch (column), in GROUPS order: AISC pipe; round HSS;
# custom round tube; rectangular HSS and custom rectangular tube; solid
# round bar and solid rectangular bar. Every pair of hollow families may
# meet, a round member with a rectangular one included (S6-9).
CHORD_AND_BRANCH = _by_family({
    "AISC pipe":         [ALLOWED, ALLOWED, ALLOWED, ALLOWED, _S7],
    "round HSS":         [ALLOWED, ALLOWED, ALLOWED, ALLOWED, _S7],
    "custom round tube": [ALLOWED, ALLOWED, ALLOWED, ALLOWED, _S7],
    "rectangular":       [ALLOWED, ALLOWED, ALLOWED, ALLOWED, _S7],
    "solid bar":         [_S7,     _S7,     _S7,     _S7,     _S7],
})

POST_ON_BASEPLATE: dict[str, Cell] = {
    PIPE: ALLOWED,
    ROUND_HSS: ALLOWED,
    ROUND_TUBE: ALLOWED,
    RECT_HSS: ALLOWED,
    RECT_TUBE: ALLOWED,
    ROUND_BAR: _stop(7, _NO_BASE_WELD_RULE),
    RECT_BAR: _stop(7, _NO_BASE_WELD_RULE),
}

LISTED_ONLY = "The tool computes only the combinations listed as allowed (S5-9)."


@dataclass(frozen=True)
class JointMember:
    """A member at a joint: what the message calls it, and its section."""

    name: str            # "top rail", "post", "intermediate rail"
    section: Section


@dataclass(frozen=True)
class ChordBranchJoint:
    """A joint where a branch member is welded to the wall of a chord."""

    name: str
    table: dict[tuple[str, str], Cell]
    not_supported: Stop   # the id of a stop cell
    no_cell: Stop         # the id of a pair with no cell

    def cell(self, chord_family: str, branch_family: str) -> Cell | None:
        return self.table.get((chord_family, branch_family))

    def require(self, chord: JointMember, branch: JointMember, error: type[InputError]) -> None:
        """Stop unless this joint's table lists the pair as allowed."""
        c, b = chord.section.family, branch.section.family
        cell = self.cell(c, b)
        if cell is None:
            raise error(
                f"{self.name}: there is no decision for {c} as the chord ({chord.name} {chord.section.label}) "
                f"with {b} as the branch ({branch.name} {branch.section.label}). {LISTED_ONLY}",
                stop=self.no_cell)
        if not cell.allowed:
            named = self._named(chord, branch)
            raise error(
                cell.message.format(member=named.name, label=named.section.label, family=named.section.family)
                + f" {self.name}: {c} as the chord with {b} as the branch is not supported until slice "
                  f"{cell.slice} ({BROUGHT_BY}).",
                stop=self.not_supported)

    def _named(self, chord: JointMember, branch: JointMember) -> JointMember:
        """The member a stop cell's message names: the one whose family
        brings the stop. That is the chord when a joint of the chord's
        family alone stops for the same slice, and the branch otherwise."""
        c, b = chord.section.family, branch.section.family
        own = self.cell(c, c)
        return chord if own is not None and own.slice == self.table[(c, b)].slice else branch


@dataclass(frozen=True)
class BaseplateJoint:
    """The post on the baseplate."""

    name: str
    table: dict[str, Cell]
    not_supported: Stop
    no_cell: Stop

    def cell(self, post_family: str) -> Cell | None:
        return self.table.get(post_family)

    def require(self, post: JointMember, error: type[InputError]) -> None:
        """Stop unless this joint's table lists the post's family as allowed."""
        family = post.section.family
        cell = self.cell(family)
        if cell is None:
            raise error(
                f"{self.name}: there is no decision for a {family} post ({post.section.label}) on an A36 plate "
                f"baseplate. {LISTED_ONLY}",
                stop=self.no_cell)
        if not cell.allowed:
            raise error(
                cell.message.format(member=post.name, label=post.section.label, family=family)
                + f" {self.name}: a {family} post is not supported until slice {cell.slice} ({BROUGHT_BY}).",
                stop=self.not_supported)


CHECK_3 = ChordBranchJoint("Check 3 joint (top rail as chord, post as branch)", CHORD_AND_BRANCH,
                           Stop.JOINT_CHECK3_NOT_SUPPORTED, Stop.JOINT_CHECK3_NO_CELL)
CHECK_4B = ChordBranchJoint("Check 4b joint (post as chord, intermediate rail as branch)", CHORD_AND_BRANCH,
                            Stop.JOINT_CHECK4B_NOT_SUPPORTED, Stop.JOINT_CHECK4B_NO_CELL)
CHECK_7 = BaseplateJoint("Check 7 joint (post on the baseplate)", POST_ON_BASEPLATE,
                         Stop.JOINT_CHECK7_NOT_SUPPORTED, Stop.JOINT_CHECK7_NO_CELL)
JOINTS = (CHECK_3, CHECK_4B, CHECK_7)


def group_label(group: tuple[str, ...]) -> str:
    return ", ".join(group)


def markdown_table(joint: ChordBranchJoint | BaseplateJoint) -> str:
    """The joint's table as docs/brief/stops.md prints it, one row and column
    per group of families."""
    if isinstance(joint, BaseplateJoint):
        rows = ["| Post | Cell |", "| --- | --- |"]
        rows += [f"| {group_label(g)} | {joint.table[g[0]].text} |" for g in GROUPS]
        return "\n".join(rows)
    rows = ["| Chord \\ Branch | " + " | ".join(group_label(g) for g in GROUPS) + " |",
            "| --- |" + " --- |" * len(GROUPS)]
    for chord in GROUPS:
        cells = " | ".join(joint.table[(chord[0], branch[0])].text for branch in GROUPS)
        rows.append(f"| {group_label(chord)} | {cells} |")
    return "\n".join(rows)
