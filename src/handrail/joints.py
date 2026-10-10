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

An allowed chord and branch pair rests on W7, kept for slice 5 by S5-3 (the
chord wall's local strength is a stated assumption, not a check), and on
W2's branch rule (k_ds = 1.0). An allowed post on the baseplate is welded
all around, with W2's directional increase. A stop cell names the slice
that brings its family (S5-1).

As built in step 1 of slice 5, the only allowed pair is AISC pipe on AISC
pipe, which is what the tool computed before the tables existed. Step 5
sets the round HSS and custom round tube cells to allowed.
"""

from __future__ import annotations

from dataclasses import dataclass

from handrail.errors import InputError
from handrail.shapes import PIPE, RECT_BAR, RECT_HSS, RECT_TUBE, ROUND_BAR, ROUND_HSS, ROUND_TUBE, PipeSection
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

# W7 (extended to the intermediate rail by S4-12): the wording the stop has
# had since slice 3.
_NOT_ROUND_HOLLOW = ("{member} {label} ({family}) is not a round hollow section. The stated assumption that the rail "
                     "wall's local strength at the post is not checked has been decided only for a round hollow "
                     "rail on a round hollow post, not for this section.")
# W2 at the post to baseplate weld: the wording the stop has had since slice 3.
_NO_DIRECTIONAL_RULE = ("{label} ({family}): the directional strength increase rule for this section family has not "
                        "been drafted. The tool applies the increase only to round hollow sections.")
# A round hollow family the tool does not have yet (until step 5 of slice 5).
_NOT_BUILT = "{member} {label} ({family}): this version does not have this section family yet."


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


_S5, _S6, _S7 = _stop(5, _NOT_BUILT), _stop(6, _NOT_ROUND_HOLLOW), _stop(7, _NOT_ROUND_HOLLOW)

# Chord (row) and branch (column), in GROUPS order: AISC pipe; round HSS;
# custom round tube; rectangular HSS and custom rectangular tube; solid
# round bar and solid rectangular bar.
CHORD_AND_BRANCH = _by_family({
    "AISC pipe":         [ALLOWED, _S5, _S5, _S6, _S7],
    "round HSS":         [_S5,     _S5, _S5, _S6, _S7],
    "custom round tube": [_S5,     _S5, _S5, _S6, _S7],
    "rectangular":       [_S6,     _S6, _S6, _S6, _S7],
    "solid bar":         [_S7,     _S7, _S7, _S7, _S7],
})

POST_ON_BASEPLATE: dict[str, Cell] = {
    PIPE: ALLOWED,
    ROUND_HSS: _stop(5, _NOT_BUILT),
    ROUND_TUBE: _stop(5, _NOT_BUILT),
    RECT_HSS: _stop(6, _NO_DIRECTIONAL_RULE),
    RECT_TUBE: _stop(6, _NO_DIRECTIONAL_RULE),
    ROUND_BAR: _stop(7, _NO_DIRECTIONAL_RULE),
    RECT_BAR: _stop(7, _NO_DIRECTIONAL_RULE),
}

LISTED_ONLY = "The tool computes only the combinations listed as allowed (S5-9)."


@dataclass(frozen=True)
class JointMember:
    """A member at a joint: what the message calls it, and its section."""

    name: str            # "top rail", "post", "intermediate rail"
    section: PipeSection


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
