# Slice 5 plan: hollow round sections (round HSS and custom round tubes)

Status: **planned** 2026-10-09, from Micah's rulings S5-1 to S5-14 in the
planning interview of that date. Nothing is open. The build starts on the
`slice-5` branch with step 1.

> This plan is a record of what slice 5 sets out to build and why. The
> binding engineering decisions (S5-1 to S5-14) were recorded in the brief
> as they were made: docs/brief/checks.md ("Section families"),
> docs/brief/verification.md, docs/brief/welds.md ("Hollow round sections
> (slice 5)"), docs/brief/inputs.md (grades, custom round tube input,
> stops) and docs/brief/scope.md. Where this plan differs from
> docs/BRIEF.md, CLAUDE.md or a later plan, those govern. T1 to T4 below
> are test decisions, not tool behavior, and stay here.

## Goal

Widen the section layer from AISC pipe to every hollow round section:
round HSS from the Shapes Database and custom round tubes defined by
dimensions, in every grade AISC Manual Table 2-4 lists for them. The
engineering is pipe's (§F8, Table B4.1, Chapter E, the round weld
decisions); what is new is where the numbers come from. Before any of
that, make the calc engine safe to generalize (issue #21), proven by
golden snapshots to change no printed calc. No check is added. Test cases
1–5 must pass exactly as they do today, and their printed calcs must not
change except in the places listed under "Output".

Solid round bar is not in this slice: it moved to slice 7 with solid
rectangular bar (S5-1).

## Decisions settled for this slice

S5-1 to S5-14 are in the brief, with Micah's name and date on each. In
short:

| No. | Decision | Brief |
| --- | --- | --- |
| S5-1 | Slices 5–7 regrouped by engineering: 5 hollow round, 6 hollow rectangular, 7 every solid bar. The section type carries per-axis properties (x and y) from slice 5; round shapes set x = y; which checks read which axis is slice 6's decision. (#22, F1) | checks.md |
| S5-2 | Micah's release recompute covers a check in a family's first case when the case reaches a provision, equation branch or computed property none of his arithmetic has touched; a new section name alone does not. A family case covers only the groups its family changes, and still records every cross-member quantity it changes. (#23) | verification.md |
| S5-3 | W7 (Chapter K chord limit states not checked) kept for slice 5, with a stop when a chord's D/t exceeds 50: the top rail in Check 3, the post in Check 4b. Scope addition: from slice 6 the chord limit states are checked for round and rectangular chords, and W7 is retired. | welds.md, scope.md |
| S5-4 | A round HSS uses the database values as published, OD included (2.38 in for HSS2.375); no reading of the designation. The 0.2–0.4% effect on Checks 3, 4b and 7 is accepted. W8 and S4-11 treat ODs within 0.01 in as equal. | checks.md, welds.md |
| S5-5 | Every shape can use every grade the Manual lists for it. Default for round HSS and custom round tube: A500 Gr B; pipe stays A53 Gr B. Slice 5 drafts Fy and Fu for every plain grade. Custom round tubes take the round HSS grades plus A53 Gr B. Unusual pairings on database sections warn. Micah verifies the A500 Gr B and Gr C round Fy and Fu before the independent calcs run. | inputs.md |
| S5-6 | A1085 Gr A offered: a database section on its published 0.93·t_nom properties, with a note saying a custom section gets the nominal wall; a custom tube on t_des = t_nom. A1065 moves to slice 6. The §B4.2 wall rule is drafted from the 360-22 text; if it still keys on ERW against SAW, stop and ask. | inputs.md |
| S5-7 | A618 offered with Fy and Fu by wall range (Gr Ia, Ib, II: 50/70 to 3/4 in, 46/67 over 3/4 to 1-1/2 in, stop above; Gr III 50/65). The nominal wall is compared. Entries stored by wall range for slice 6 to reuse. Machinery tests only. | inputs.md |
| S5-8 | A custom tube's wall is always the nominal wall: key `wall_nominal`, required, no nominal/design flag. t_des per §B4.2 by grade. t_nom feeds Table J2.4, the A618 ranges and weight; t_des feeds properties and strength. | inputs.md, checks.md, scope.md |
| S5-9 | One table per joint says which section families may meet; a pair with no cell stops. docs/brief/stops.md lists every stop with its decision and its test, and a test holds the code to it. Built in the #21 step. (#22, F9) | inputs.md, CLAUDE.md |
| S5-10 | The intermediate rail takes the top rail's grade when that grade is on the standard list for its own shape, otherwise its own shape's default (refines S4-1). A defaulted grade prints as "A500 Gr B (default)", for every member. | inputs.md |
| S5-11 | A third guard on Check 4b's same-as-top observation: a post OD greater than the rail OD by any amount runs the full Check 4b. | welds.md |
| S5-12 | The weld envelope and load-at-centerline rulings hold for every round hollow rail; W2's directional increase applies at Check 7 to every round hollow post, custom tubes and hot-formed grades included. (Claude's, confirmed.) | welds.md |
| S5-13 | The Fu/Fy ≥ 1.20 post-grade guard carries the no-tension-rupture ruling to the new grades. (Claude's, confirmed.) | checks.md |
| S5-14 | "Designed as round HSS" prints for AISC pipe and a custom A53 tube only. (Claude's, confirmed.) | checks.md |

Decided outside the interview and applied here:

- **#11: option A** (Micah, 2026-10-09, in his brief for this plan). The
  DRAFT list is filled last, after the whole body is built, with a
  regression test that adds a late registry read and asserts the entry is
  still listed.
- **#24 item 1** (approved in the architecture review of 2026-10-09): the
  footer's tool version. The slice 5 pull request bumps `pyproject.toml`
  to 0.5.0; CLAUDE.md's slice-close routine now says so.
- **ADR 0008 as amended** (Micah, 2026-10-09): nothing in this slice
  waits on registry verification, apart from the four A500 values Micah
  chose to verify first (S5-5).

### How S5-10 to S5-14 came about

S5-10 and S5-11 were found when the decisions were checked against each
other: S4-1 against S5-5 (the intermediate rail's default grade), and
S4-8 against S5-4 (the observation sentence inside the OD tolerance).
S5-12 to S5-14 were Claude's, following from the rulings above or from
the roadmap's "confirm here" list; Micah confirmed all of them on
2026-10-09. One more was Claude's and is a build decision, not
engineering:

- **Step 1 adds `ruff check` (the linter) but not `ruff format`.** A
  linter flags likely mistakes; a formatter rewrites layout. Reformatting
  the whole codebase would bury the refactor's diff, so it stays on #7.
  If `ruff check` flags existing code, those fixes go in their own
  commit, separate from the #21 refactor. (Confirmed by Micah,
  2026-10-09.)

### Test decisions

**T1. Test case 6, the rail case (#3).** A custom noncompact tube rail on
a pipe post. (Micah, 2026-10-09.)

- Top rail: custom round tube, OD 2.375 in, `wall_nominal` 0.055 in,
  A500 Gr C. Post: Pipe2STD, A53 Gr B. No intermediate rail.
- L = 6'-0", h = 42 in, t_p = 1/2 in; B = 6 in × N = 8 in; A36 baseplate.
  Welds: rail to post 1/8 in, post to baseplate 1/4 in; E70XX.
- Default loads, no exemption; default deflection limits.
- `covers`: section, check1, check2, check3, and the post group, which
  holds D at the post (S5-2's cross-member quantity: the rail's computed
  weight flowing into the post's dead load). Checks 5–7 and the reactions
  are not covered.
- `recompute`: section and check1. Micah's [hand] values, deferred to the
  release review: the custom tube's section properties (t_des, A, I, S,
  Z, r) and Check 1's governing ratio and controlling case.
- Not a stocked A500 size. Noncompact A500 tube does not exist at guard
  diameters; the case exists to reach Eq. F8-2 inside the D/t ≤ 50 stop.
- Slice 6's round chord check (S5-3) extends this case rather than adding
  one: its D/t of 46.4 is where the W7 assumption is weakest. (Micah,
  2026-10-09.)

Rough figures for case 6, from planning arithmetic (Claude, not test
values; rule 5), at the drafted Fy = 50 ksi. t_des = 0.93 × 0.055 =
0.05115 in; D/t = 46.4; λp = 0.07E/Fy = 40.6 (44.1 if Fy verifies as 46
ksi), so the wall is noncompact either way. A ≈ 0.373 in², I ≈ 0.252 in⁴,
S ≈ 0.212 in³, Z ≈ 0.276 in³, r ≈ 0.822 in; weight on the nominal wall ≈
1.36 plf. Mp ≈ 13.8 kip-in; Eq. F8-2 gives Mn ≈ 13.4 kip-in, which
governs; Ma ≈ 8.0 kip-in. Check 1, concentrated, downward: M ≈ 3,600 + 74
= 3,674 lb-in, about 0.46. Check 2 about 0.36. Check 3 about 0.05, rail
wall base metal about 0.04. D at the post ≈ 8.2 + 12.7 = 20.8 lb.

Branches case 6 reaches: the custom-tube path (§B4.2 at 0.93, properties
from dimensions, weight from the nominal wall); Eq. F8-2 governing over
Mp; the noncompact flag; Check 3's rail-wall base metal on a computed
t_des and an A500 Fu.

**T2. Test case 7, the post case.** A database round HSS post under a
pipe rail. (Micah, 2026-10-09.)

- Top rail: Pipe2STD, A53 Gr B. Post: HSS2.375X0.125, grade left out of
  the file so the A500 Gr B default applies. No intermediate rail.
- Geometry, baseplate and loads as case 6. Welds: rail to post 1/8 in,
  post to baseplate 3/16 in; E70XX.
- `covers`: post, check3, check5, check6, check7, reactions. Check 3 is
  covered because its weld ring is the post's perimeter, a cross-member
  quantity (S5-2). The section group and Checks 1 and 2 are not covered.
- `recompute`: none (an empty list, which the harness already accepts).
  Every provision and branch the case uses is one Micah recomputes in
  cases 2–5; only registry values and published properties differ.

Rough figures for case 7 (planning arithmetic, not test values), at the
drafted Fy = 46 ksi and Fu = 58 ksi, with S, Z and r approximated from
the published A = 0.823 in² and I = 0.527 in⁴. D at the post ≈ 22.0 +
10.4 = 32.4 lb. The distributed load governs the post: w·L = 300 lb.
Check 5: Lc/r ≈ 110, below 4.71√(E/Fy) = 118, so Eq. E3-2; H1-1b ≈ 0.77
(about 0.84 if Fy verifies as 42 ksi). Check 6 ≈ 0.468 in against 0.692
in, about 0.68. Check 7: S_w = π(2.38)²/4 = 4.449 in², f ≈ 2.80 kip/in
against 4.18 kip/in (k_ds = 1.5), about 0.67. Reactions: V = 480 lb, M =
20,160 lb-in, N ≈ −35 lb lateral and ≈ +445 lb upward.

Branches case 7 reaches: the round HSS extraction, on a section no pipe
row matches; the published OD of 2.38 in in the rings of Checks 3 and 7;
the 0.01 in tolerance (a 2.38 in post under a 2.375 in rail runs); an
A500 Fy in Chapter E; the default grade.

**T3. The property-formula test.** The custom tube's formulas (A, I, S,
Z, r, D/t, and weight on the nominal wall) are run on database rows and
compared with the published values, a check against AISC's numbers rather
than a same-author one. A row that fails to reproduce within the
database's rounding is reported to Micah; the tolerance is never widened.
(Micah, 2026-10-09.)

- **Binding:** the round HSS rows whose OD column equals the
  designation's OD and is 10 in or less. All six properties must
  reproduce to the last published digit on every one. A scratch trial
  (planning arithmetic, 2026-10-09) found 67 such rows, all reproducing.
- **Round HSS rows over 10 in:** not asserted. The trial missed the last
  digit on 23 of 61 (worst 0.5%). The build lists them in the pull
  request as a finding.
- **Pipe rows:** before the pull request, the build reports to Micah, for
  each property (A, I, S, Z, r, weight): how many rows reproduce, and for
  the misses, the direction (formula above or below published) and the
  worst percentage. The trial reproduced 11 of 51 rows in full; the
  published pipe areas run above the computed ones (Pipe2STD: 1.02 in²
  published, 1.003 computed, 1.7%; up to 3.4% for large XS pipe).
  - **Stop and ask Micah if the formula comes out above the published I,
    S or Z for any pipe row.** That would make a custom A53 tube
    unconservative against the database shape of the same dimensions.
  - If every miss is below published, it is listed as a finding, and the
    properties that reproduce on every pipe row become binding for pipe
    too.

**T3 as ruled during the build** (Micah, 2026-10-10, on the pipe-row
report). The formula did come out above the published I, S and Z, on six
pipe rows: XS pipe 14 to 26 in, whose published A, I, S and Z match a wall
of 0.90·t_nom, not the listed design wall. His ruling: the custom tube
formulas are accepted as exact geometry on the listed OD and the design
wall of §B4.2. The binding tests became:

- the 67 round HSS rows: A, I, S, Z, r and D/t reproduce at the database's
  printed precision; weight within 0.5%;
- pipe rows under 12 in OD: A, I, S, Z and r reproduce or come out below
  published, never above; D/t reproduces. A row above on any of them is
  parked and reported;
- the six XS rows and the large-HSS misses are a database finding, listed
  in data/README.md and the pull request, not asserted.

As built (tests/test_tube.py): the round HSS rows pass in full, and the
pipe rows pass on I, S, Z and r. Pipe area comes out above published on
five rows under 12 in (Pipe3STD +0.64%, Pipe6XS +0.61%, Pipe5STD +0.48%,
Pipe3-1/2XS +0.42%, Pipe4STD +0.37%) and pipe D/t misses on one (Pipe2XS:
published 11.7, 2.375/0.204 = 11.64, below).

Micah's second ruling (2026-10-10): both are accepted as database
findings, listed in data/README.md with the others. The binding pipe test
gains a guard in place of "reproduces or below" for the area: on pipe rows
under 12 in, the formula's area is never more than 1% above published.
Pipe D/t is not asserted.

More changes to the snapshot rule were ruled the same day: the chord D/t
draft row is a third intended change to existing calcs; stop-second-order's
rail moved to Pipe20XS; and full-noncompact and full-noncompact-same, whose
Pipe26STD rail the chord D/t limit refuses, were retired, with
full-tube-noncompact-rail holding the noncompact branch and Eq. F8-2.

**T4. Machinery tests** (same-author), for what cases 6 and 7 do not
reach:

- A1085: a database section prints the note and runs on published
  properties; a custom tube runs on t_des = t_nom.
- A618 (S5-7): a wall at exactly 3/4 in, one just over, and one over
  1-1/2 in that stops; Gr III at any wall.
- A501 Gr A and Gr B, A847: accepted, with their own Fy and Fu.
- The chord D/t > 50 stop: on the top rail; on the post with an
  intermediate rail; no stop on a post over 50 with no intermediate rail.
- The OD tolerance: ODs 0.005 in apart run; ODs 0.02 in apart stop, in
  both W8 and S4-11.
- The unusual-pairing warning: an HSS grade on a Pipe designation, A53
  Gr B on an HSS designation, and no warning for either on a custom tube.
- Custom tube input: `wall_nominal` missing; `section` given with custom
  dimensions; a wall of half the OD or more; a slender custom tube and one
  beyond the §F8 limit (the existing stops, on computed D/t).
- An unsupported grade names the grade and the grades supported for that
  shape.
- S5-9: a stand-in family with no row stops at each of the three joints,
  naming the joint and both families; every stop id in the code is in
  stops.md and every id there has a test.
- S5-10: an HSS intermediate rail under a pipe top rail defaults to A500
  Gr B; under an HSS Gr C top rail, to Gr C; a defaulted grade prints
  "(default)" and an entered one does not.
- S5-11: a post 0.005 in wider than the rail, same-as-top state, runs the
  full Check 4b and prints which guard failed; equal ODs keep the
  observation.

## Supported combinations (F9)

The per-joint tables as slice 5 leaves them. The code holds them as data
(step 1); docs/brief/stops.md prints them. "Allowed" is subject to the
dimension stops listed after the tables.

Check 3 joint (top rail = chord, post = branch) and Check 4b joint (post =
chord, intermediate rail = branch): the same table for both.

| Chord \ Branch | AISC pipe | Round HSS | Custom round tube | Rectangular HSS, custom rectangular tube | Solid round bar, solid rectangular bar |
| --- | --- | --- | --- | --- | --- |
| AISC pipe | allowed | allowed | allowed | stop: slice 6 | stop: slice 7 |
| Round HSS | allowed | allowed | allowed | stop: slice 6 | stop: slice 7 |
| Custom round tube | allowed | allowed | allowed | stop: slice 6 | stop: slice 7 |
| Rectangular HSS, custom rectangular tube | stop: slice 6 | stop: slice 6 | stop: slice 6 | stop: slice 6 | stop: slice 7 |
| Solid round bar, solid rectangular bar | stop: slice 7 | stop: slice 7 | stop: slice 7 | stop: slice 7 | stop: slice 7 |

Each "allowed" cell cites W7 as kept by S5-3 (the chord wall is a stated
assumption) and W2's branch rule (k_ds = 1.0). Each stop cell says the
family is not supported until that slice and cites S5-1. Until step 5
sets the round HSS and custom round tube cells to allowed, only pipe on
pipe is allowed, which is today's behavior.

Check 7 joint (post on the baseplate; A36 plate is the only baseplate):

| Post | Cell |
| --- | --- |
| AISC pipe, round HSS, custom round tube | allowed: welded all around; W2's directional increase applies |
| Rectangular HSS, custom rectangular tube | stop: slice 6 (the weld pattern and the directional rule for rectangular HSS) |
| Solid round bar, solid rectangular bar | stop: slice 7 |

Dimension and grade stops this slice adds to the list in stops.md: the
chord D/t limit (S5-3); the OD tolerance inside W8 and S4-11 (S5-4, a
change to two existing stops); the A618 wall over 1-1/2 in (S5-7); the
custom tube input stops (S5-8); a grade with no Fy or Fu entry for the
shape (existing, now per shape).

## Pipe-specific printed text (F10)

Every place the code prints, or assumes, something true only of AISC
pipe. File and line as of main at 17ca67f; step 1 moves most of them.

| No. | Where | What it says today | What slice 5 does |
| --- | --- | --- | --- |
| 1 | checks.py:336–338 | "Designed as round HSS: Pipe is designed under the round HSS provisions" (`aisc360.pipe_as_round_hss`), printed for any section through §F8 | Prints for AISC pipe and a custom A53 tube only. A round HSS, or a custom tube of an HSS grade, is round HSS and prints no such line. |
| 2 | report.py:487 | "Properties are used exactly as published in the AISC Shapes Database v16.0.", once, after the top rail | Per member. Database section: the sentence as it stands. Custom section: properties computed from the dimensions entered, t_des per §B4.2. |
| 3 | project.py:242 | Every member defaults to A53 Gr B | Default by shape (S5-5); the intermediate rail per S5-10; a defaulted grade prints "(default)". |
| 4 | checks.py:306, 342; post.py:77 | D/t "tabulated" | "tabulated" for a database section; a computed calc line for a custom tube. |
| 5 | checks.py:253, 266, 281, 300 | Self-weight "tabulated W = …", cited to the database | For a custom tube, the weight is a calc line: density × area on the nominal wall. |
| 6 | checks.py:296–298 | D, t_nom, t_des as givens cited to the database | For a custom tube: D and t_nom "as entered"; t_des a calc line citing §B4.2 (S5-8). A, I, S, Z, r as calc lines. |
| 7 | welds.py:99, 125, 445, 455, 620–621 | Outside diameter and wall thicknesses in the weld checks, cited to the database | Cited to the member's own source (database, or as entered and computed). |
| 8 | checks.py:45 | One citation constant, "AISC Shapes Database v16.0", used for every section value | A section carries its own source, and each line cites it. |
| 9 | checks.py:49–52 | Fy and Fu entries keyed by grade name only | Keyed by grade and shape, and by wall range for A618 (S5-7). |
| 10 | The unsupported-grade stop | Names "the grades supported", one list | Names the grades supported for that shape. |
| 11 | checks.py:579–581; welds.py:287–290 | The W7 non-round stop and the directional-increase family stop, each its own `if` | Cells of the per-joint tables (S5-9). |
| 12 | shapes.py | `PipeSection`, `pipe()`, `ROUND_HOLLOW = (PIPE,)`, r "equal to ry for a pipe" | The generic section type with per-axis properties (S5-1). Code only. |
| 13 | version.py, pyproject.toml | Footer "Tool 0.1.0" | 0.5.0 (#24). |

Correct for every hollow round section, wrong for a solid bar, so flagged
for slice 7 and left alone here: "round HSS in flexure" and "round HSS in
compression" on the classification lines (checks.py:344–345, post.py:82);
"Round HSS: lateral-torsional buckling does not apply" (checks.py:363);
"design wall" and "wall thickness" throughout welds.py; the stated
assumptions' "saddle centroid (2R/π for equal round diameters)" and
"flare-bevel joint" (also slice 6, for rectangular rails).

## What the slice does

### Input

The project file gains (bare numbers are inches):

- A member (`[top_rail]`, `[post]`, `[intermediate_rail]`) takes either
  `section` (a Pipe or round HSS designation) or a custom round tube:
  `shape = "round tube"`, `OD` and `wall_nominal`. Both together stop.
- `grade`: any grade with Fy and Fu entries for the member's shape. Left
  out, it defaults by shape (S5-5; S5-10 for the intermediate rail).
- No new keys for loads, welds, deflection or the baseplate.
- Validation (`validate()`): the per-joint tables (S5-9); the chord D/t
  limit (S5-3); W8 and S4-11 with the OD tolerance (S5-4); the A618 wall
  limit (S5-7); the custom tube stops (S5-8). The existing slender, §F8
  applicability and Fu/Fy stops run on the new sections unchanged.

The dimensions page echoes a custom tube's OD and nominal wall, as
entered and normalized.

### Engineering

- **The section type** (S5-1): one type for every section, with its
  family, its source (database or custom), OD, t_nom, t_des, weight, A,
  and I, S, Z and r about x and about y. A round section sets x = y, and
  every check keeps reading the single value it reads today.
- **Round HSS from the database** (S5-4): the round HSS rows extracted to
  a derived file like the pipe rows, with the same row-for-row test.
  Values as published, OD included.
- **Custom round tube** (S5-8): t_des from t_nom per §B4.2 by grade; A,
  I, S, Z and r from OD and t_des; D/t = OD/t_des; weight = density ×
  area on the nominal wall. Each prints as a calc line with its citation.
- **Grades** (S5-5 to S5-7): Fy and Fu by grade and shape, and by nominal
  wall for A618. Classification, §F8, Chapter E, §H1, §D2 and the weld
  base metal lines read them where they read A53's today.
- **Checks 1–7** are otherwise unchanged. Check 7 applies W2's
  directional increase to every round hollow post; Check 3 and Check 4b
  keep k_ds = 1.0.

### Output (PDF)

- Section pages: per-member source sentence; custom tubes as calc lines
  (F10 items 2, 4, 5, 6); the A1085 note (S5-6); the unusual-pairing
  warning (S5-5); the grade used.
- The printed calcs of cases 1–5 and the example change in these places
  only:
  - the W7 stated assumption gains its clause (S5-3), changed in
    output.md's list in the same commit that prints it. It shows in the
    golden snapshots for Micah's review;
  - a defaulted grade gains "(default)" (S5-10). Case 5 leaves its
    intermediate rail's grade out, so that line of its snapshot changes;
    every other rail and post grade in cases 1–5 and the example is
    entered. "Every member" means the top rail, the post and the
    intermediate rail, not the baseplate grade or the electrode, and the
    mark prints on the section properties page, where the grade already
    prints (both confirmed by Micah, 2026-10-09);
  - the footer's tool version, 0.1.0 to 0.5.0 (#24). The snapshots are
    generated with a fixed stamp, so they do not show this one; the
    version test covers it.
- Proposed assumption text (S5-3, welds.md), for Micah to accept in the
  pull request: "Local strength of the rail wall at the post, and of the
  post wall at the intermediate rail (AISC 360-22 Chapter K chord limit
  states), is not checked; the chord's D/t is limited to 50, the Chapter
  K limit of applicability."

Layout details (line wording beyond the decisions, where the warning
sits) are Claude's to propose on the branch and Micah's to accept in the
pull request review.

## Registry entries this slice will draft

About 35–40, well above the roadmap's 12–15: the grade rulings (S5-5 to
S5-7) roughly doubled the count. Citations from memory unless noted; all
drafted, verified by Micah at the release review, or earlier from the
slice-close workbook if he chooses.

- **Fy and Fu, round HSS** (AISC Manual Table 2-4): A500 Gr B, A500 Gr C,
  A501 Gr A, A501 Gr B, A847, A1085 Gr A: 12 entries. **The four A500
  values are verified by Micah before the independent calcs run** (S5-5):
  drafted as Gr C 50/62 (one secondary source) and Gr B 46/58, with 42/58
  the pre-A500-21 value; I am not sure which the 16th Edition prints.
- **A618** (S5-7): Fy and Fu by wall range for Gr Ia, Ib and II; Fy and
  Fu for Gr III; the 3/4 in and 1-1/2 in limits: 8 to 10 entries,
  depending on how a range is stored.
- **§B4.2** (from the 360-22 text, S5-6): the provision, the 0.93
  coefficient, and the nominal-wall rule for A1085: 3 entries.
- **Round tube property formulas**: A, I, S, Z, r and D/t from OD and
  t_des, and weight from the nominal wall and the steel density: 6 or 7
  entries. I believe the reference is the Manual's Part 17 table of
  properties of geometric sections; I am not sure of its number.
- **Chapter K**: the chord D/t ≤ 50 limit of applicability, table number
  confirmed when drafted; and the engineering-judgement entry for the
  stop (S5-3): 2 entries.
- **Engineering judgement** (source "engineer"): the 0.01 in OD tolerance
  (S5-4); a custom tube's wall taken as nominal (S5-8): 2 entries.
- **Printed text**: the A1085 note; the unusual-pairing warning: 2
  entries.
- **Revised drafted entries**: `material.grades.hss_round` (A618's grade
  names corrected, A1065 removed); `ej.weld.directional_round_hss` (note
  broadened to custom tubes and hot-formed grades); `ej.weld.rail_wall_normal`
  (the D/t limit); `aisc360.pipe_as_round_hss` (note names custom A53
  tubes). `material.grades.pipe` is verified and is not touched.

## Tests

- **Golden snapshots** (step 1): the Typst source of cases 1–5 and the
  example, byte-identical through every refactor step.
- **Test cases 6 and 7** (independent-calc cases, T1 and T2), each with a
  fresh independent calc. Case 6's [hand] values are "deferred" to the
  release review; case 7 has none.
- **Cases 1–5**: no input change, no new values, every existing value
  unchanged. A changed value is a rule 2 stop.
- **The property-formula test** (T3) and the **machinery tests** (T4).
- **The extraction test** for the round HSS rows, as for pipe.

## Build order

Each step is committed and pushed when its tests pass. Steps 1 and 2
change no printed calc, and the snapshots prove it.

**Snapshot rule for every step** (Micah, 2026-10-09). A step that changes
printed text on purpose updates the golden snapshots in a commit of its
own, one commit per intended change, and that step's report shows Micah
the snapshot diff. A snapshot diff nobody intended, or one larger than
the change it belongs to, is a stop: the snapshot is not regenerated
until the cause is known. This slice has two intended changes to the
existing calcs, both in step 8 and neither in step 1: the W7 assumption
clause (S5-3) and "(default)" on case 5's intermediate rail grade
(S5-10).

1. **Issue #21: make the engine safe to generalize.** In this order:
   - **Golden snapshot test first** (#6): the Typst source of cases 1–5
     and `examples/slice-1.toml`, generated with a fixed stamp, committed
     under tests/golden/; a readable diff on any difference; a documented
     way to regenerate on purpose. A snapshot is the full printed text of
     a calc saved as a file, so any change to calc text shows up in the
     pull request as text Micah can read.
   - **The comparison helper**: one definition per decision line (ADR
     0002 applied to decisions), so the printed relation and the `if`
     that acts on it cannot drift apart.
   - **Direction enums**, with no catch-all branch: an enum is a fixed
     list of named values, so a mistyped direction stops instead of
     computing as another case.
   - **Stable line keys**: the test harness finds values by a key on
     each calc line, not by the printed symbol. This changes how the
     harness extracts values, not its rules (frozen, ADR 0006).
   - **Split checks.py**: result types, Checks 1–2, `validate` and the
     `compute` orchestration in separate modules.
   - **#11 option A**: the DRAFT list filled last, with its regression
     test.
   - **Stops** (S5-9): an id on every stop, the per-joint tables as
     data, docs/brief/stops.md, the test that holds the code to it, and
     the stand-in family test. The tables start with pipe on pipe as the
     only allowed pair.
   - **pyright and `ruff check`** in the dev group and CI (#7). Any fix
     `ruff check` asks of existing code goes in its own commit, separate
     from the refactor (Micah, 2026-10-09).
   - **#24 items 2 and 3**: the welds.py docstring; the case 5 header.
   - `.claude/rules/` and the calc-code-review skill updated where they
     name moved files.

   Confirmed unchanged: the snapshots are byte-identical before and after
   every item after the first, and all tests pass with case values
   unchanged.
2. **The section type** (S5-1): the generic type replaces `PipeSection`
   under all seven checks, each line citing its section's own source (F10
   items 8 and 12). Snapshots still byte-identical.
3. **Shapes data**: the round HSS rows extracted, with the row-for-row
   test; lookup by designation across pipe and round HSS.
4. **Registry entries** drafted; review list updated; §B4.2 from the
   360-22 text, stopping to ask Micah if it keys on ERW against SAW. Then
   a review workbook of this step's entries, so Micah can give his
   verdict on the four A500 values; a separate agent session applies it
   on the branch ("Applying the verdicts", verification.md).
5. **Project file and validation**: custom tube input; grades and
   defaults by shape; the table cells for round HSS and custom round tube
   set to allowed; the D/t stop; the OD tolerance; the A618 wall lookup
   and stop; their machinery tests.
6. **Custom tube properties** as calc lines; the property-formula test
   (T3). The pipe-row report goes to Micah here, well before the pull
   request, and the work stops if the formula exceeds a published I, S
   or Z.
7. **Grades through the checks**: Fy and Fu by grade, shape and wall;
   the unusual-pairing warning; the A1085 note; the grade machinery
   tests.
8. **Report**: the section pages (F10 items 1 to 7 and 10), which print
   nothing new for an all-pipe calc with its grades entered. Then the two
   intended changes to existing calcs, each in its own commit with its
   snapshot update, and each diff shown in the step's report:
   - the "(default)" mark on a defaulted grade (S5-10). The diff should
     be one line, in case 5: its intermediate rail's grade;
   - the W7 assumption clause (S5-3), in output.md and the front matter
     in the same commit. The diff should be that one assumption, in each
     of the six snapshots.
9. **Test cases 6 and 7** wired in, values pending; independent
   templates created.
10. **Independent calcs for cases 6 and 7**, each in a fresh session by
    the independent-calc skill, after Micah's verdict on the A500 values
    is applied. This planning session has read src/, so it must not write
    either (rule 6).
11. **Micah's review** of both independent calcs and both PDFs against
    the checklist. His recompute of case 6 is deferred (#18).
12. **Version 0.5.0** in pyproject.toml (#24), CHANGELOG, the
    calc-code-review skill, then the **pull request** to main.

At the close: #18 gains case 6 (section properties and Check 1), ticks
the Eq. F8-2 gap, and lists the A618 thick-wall and A1085 wall branches
as known gaps; #3 closes; the registry review workbook for the slice's
drafted entries is produced; #16 is updated.

## Which cases need a fresh independent calc

Cases 6 and 7, one fresh session each. No existing case does: cases 1–5
change no input and no value. If a registry correction changes a value an
earlier case recorded, "Registry corrections" in verification.md applies.

## What Micah does

- During the build: read the pipe-row report from the property-formula
  test (T3), and rule if it stops.
- Also during the build: give his verdict on the A500 Gr B and Gr C round Fy
  and Fu against Table 2-4, before step 10. Answer if §B4.2 turns out to
  key on ERW against SAW.
- Review the case 6 and case 7 independent calcs and PDFs against the
  checklist in docs/brief/verification.md. Each is about half a full
  seven-check calc.
- In the pull request: read the snapshot diff (the assumption clause),
  accept or reword the proposed printed text, and approve.
- At the release review: verify this slice's drafted entries; recompute
  case 6's section properties and Check 1.

## Done when

- `uv run handrail calc` prints a full package for a guard of round HSS
  and custom round tubes, and for the unchanged example.
- All tests pass: cases 1–7 at 0.5%, no pending value in cases 6 and 7.
- The golden snapshots of cases 1–5 and the example differ from main only
  in the places listed under "Output".
- Micah has reviewed both independent calcs and both PDFs.

## Flags for later slices

- **Slice 6:** which checks read the y-axis, the axis input and Chapter
  H biaxial bending (S5-1). The Chapter K chord limit states, checked for
  round and rectangular chords, retiring W7, its assumption text and its
  table row; case 6 is extended for the round chord check; decide what
  becomes of the D/t ≤ 50 stop (S5-3). The rectangular rows of the
  per-joint tables, and the weld pattern as part of the Check 7 joint
  (S5-9). A1065, and rectangular A500, A618 and A1085 values, reusing the
  A618 wall-range lookup (S5-6, S5-7). `wall_nominal` for custom
  rectangular tubes, where the wall also sets the corner radius (S5-8).
  Confirm the rectangular Ht and B columns are stored exactly (S5-4). Its
  plan should decide first whether to split the slice.
- **Slice 7:** every question a member with no wall raises (roadmap,
  slice 7). The classification and LTB lines that say "round HSS" (F10).
  Bar grades from Table 2-5.
- **Slice 8:** the grade dropdown with preferred grades grouped at the
  top (S5-5); `wall_nominal` in the form.
- **Release review:** the A618 and A1085 branches as known gaps; the
  drafted count would be about 112 to 117 (77 as of 2026-10-09 plus
  this slice's).

## Not in slice 5

- Solid round bar, rectangular HSS, rectangular tube, flat bar (S5-1)
- The Chapter K chord limit states as a check (slice 6, S5-3)
- A1065; grades outside Table 2-4 (A513 mechanical tubing, for example)
- A nominal/design choice for a custom tube's wall (S5-8)
- `ruff format`; the input form; any new check
