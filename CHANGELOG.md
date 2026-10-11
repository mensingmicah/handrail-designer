# Changelog

## v0.5.0 (2026-10-10)

Slice 5: hollow round sections. Plan in docs/plans/slice-5.md.

`uv run handrail calc` now prints the full package for a guard of round
HSS from the Shapes Database and of custom round tubes entered by
dimensions, in every grade AISC Manual Table 2-4 lists for the shape, as
well as AISC pipe. No check is added: the engineering is pipe's (§F8,
Table B4.1, Chapter E, the round weld decisions), and what is new is where
the section and material numbers come from.

### What changed for the engineer

- **Round HSS** from the AISC Shapes Database v16.0, used exactly as
  published, the outside diameter included (2.38 in for HSS2.375; S5-4).
  Outside diameters within 0.01 in are treated as equal in the two width
  stops (post OD ≤ rail OD, intermediate rail OD ≤ post OD), so an
  HSS2.375 post runs under a Pipe2STD rail.
- **Custom round tubes**: `shape = "round tube"`, `OD` and `wall_nominal`
  in place of `section`. The wall entered is always the nominal wall
  (S5-8). t_des per AISC 360-22 §B4.2 by grade; A, I, S, Z, r and D/t from
  OD and t_des; weight from the nominal wall. Each prints as a calc line
  with its citation.
- **Every Table 2-4 grade per shape** (S5-5 to S5-7). Round HSS and custom
  round tubes: A500 Gr B (the default) and Gr C, A501 Gr A and Gr B, A618
  Gr Ia, Ib, II and III, A847, A1085 Gr A; a custom tube also takes A53
  Gr B. Pipe stays A53 Gr B by default. A618 reads Fy and Fu by nominal
  wall (to 3/4 in, over 3/4 to 1-1/2 in, a stop above). A1085: a database
  section runs on its published properties with a printed note; a custom
  tube runs on t_des = t_nom.
- **The "(default)" mark**: a grade the project file leaves out prints as
  "A500 Gr B (default)" on the section page (S5-10). The intermediate rail
  takes the top rail's grade when that grade is listed for its own shape,
  otherwise its own shape's default.
- **Grade warnings**: an HSS grade on a Pipe designation, or A53 Gr B on
  an HSS designation, prints an unusual-pairing warning and still runs. An
  unsupported grade stops, naming the grades supported for that shape.
  "Designed as round HSS" prints for AISC pipe and a custom A53 tube only
  (S5-14).
- **The chord D/t limit** (S5-3): the calc stops when a chord's D/t
  exceeds 50, the AISC 360-22 Chapter K limit of applicability (Tables
  K3.1A and K4.1A): the top rail in Check 3, and the post in Check 4b
  whenever there is an intermediate rail. The Chapter K chord limit states
  themselves are still a stated assumption, checked from slice 6.
- **The directional strength increase is the engineer's election** (W2 as
  revised, Micah 2026-10-10): `[welds] directional_increase`, false when
  left out. False: Check 7 runs on k_ds = 1.0, citing §J2.4(a)(3). True:
  k_ds per Eq. J2-5 as before, with a line saying the increase is applied
  at the engineer's election and its basis. Either way the election is
  echoed under the dimensions table. Checks 3 and 4b stay at k_ds = 1.0.
- **The thin-material warning** (Micah, 2026-10-10): a weld that joins a
  part thinner than 1/8 in (nominal wall, or the baseplate as entered)
  prints "THIN MATERIAL AT WELD" at the top of its check: below the AWS
  D1.1 thickness range, welding procedure the engineer's responsibility.
  A warning, not a stop; it fires on database sections too (Pipe1/2STD,
  Pipe3/4STD, HSS1.900X0.120).
- **The stops register**: docs/brief/stops.md lists every place the tool
  refuses to compute (60 stops), each with its decision and the test that
  triggers it, and one table per joint of which section families may meet
  there. A pair with no cell stops (S5-9). A test holds the code to the
  file.
- Check 4b's same-as-top observation gains a third guard: a post wider
  than the rail by any amount runs the full check (S5-11).

### What it delivers

- The engine made safe to generalize before any of the above (issue #21),
  with no printed calc changed: golden snapshots of the printed text of
  cases 1–5 and the example, and of 104 machinery scenarios; one
  comparison behind each decision line; direction and load type as fixed
  lists; a key on every calc line; checks.py split by check; an id on
  every stop; `ruff check` and pyright in CI.
- One section type for every section, with its family, its source and
  properties about both axes (round shapes set x = y), and every calc line
  citing its own section's source (S5-1).
- The 189 round HSS rows extracted to `data/shapes-hss-round.toml`,
  verified row for row against the original workbook.
- The footer's tool version is now the release's, 0.5.0. It read
  "Tool 0.1.0" on every calc through v0.4.0 (issue #24); the commit hash
  beside it was always right.
- 43 new drafted registry entries (120 drafted, 32 verified in all). Every
  calc still prints the DRAFT stamp.

### Changes to existing calcs

The printed calcs of cases 1–5 and the example differ from v0.4.0 in these
places only; the golden snapshots show each as a diff. The three intended
changes of the plan:

- A defaulted grade gains "(default)": one line, case 5's intermediate
  rail grade (S5-10).
- The stated assumption on the Chapter K chord limit states gains its
  clause: "; the chord's D/t is limited to 50, the Chapter K limit of
  applicability." (S5-3; all six calcs.)
- The chord D/t limit is a drafted entry read for every validated calc, so
  "Draft code values" gains its row (cases 1, 2, 4 and 5 and the example;
  case 3 is computed past validation and does not read it).

And from Micah's rulings of 2026-10-10, after the build:

- The directional increase by election. Every calc gains the echo line
  under the dimensions table. Cases 4 and 5 and the example elect it:
  one more line in Check 7, no number changed. Cases 1 to 3 are left at
  the default (Micah's decision for cases 1 and 2): Check 7 runs on
  k_ds = 1.0, its ratio 1.5 times what it was, and it now reads NG in
  cases 1 and 2 (0.92 to 1.38). None of the three records a Check 7 value.
- The thin-material limit is a drafted entry read at every weld, so
  "Draft code values" gains one row in every calc
  (`aws.d1_1.thickness_min`). None of these six calcs has a part under
  1/8 in. Case 6 does, its 0.055 in rail wall, and prints the warning at
  Check 3.
- The fillet weld strength line cites "AISC 360-22 Eq. J2-4" in place of
  "§J2.4" (read in the 360-22 text, page 16.1-130), in Checks 3, 4b and 7
  and in that entry's row of "Draft code values". No number changed.

### Database findings

Found by the property-formula test, which runs the custom tube's formulas
(exact geometry on the listed OD and the §B4.2 design wall) on database
rows. Full tables in data/README.md. The tool uses every database value as
published, so none of this changes a calc of a database section; it
matters for a custom tube entered with a database shape's dimensions.

- **Reproduces, and binding in the test**: the 67 round HSS rows of 10 in
  or less whose OD column is the designation's OD, on all seven
  properties; the 36 pipe rows under 12 in OD on I, S, Z, r and weight
  (reproduced or below published, never above).
- **Pipe area under 12 in OD**: above published on five rows (Pipe3STD
  +0.64%, Pipe6XS +0.61%, Pipe5STD +0.48%, Pipe3-1/2XS +0.42%, Pipe4STD
  +0.37%). Accepted by Micah; the test holds the formula's area to no more
  than 1% above published. A custom A53 tube with one of these pipes'
  dimensions gets up to 0.64% more area than the database pipe.
- **Pipe D/t**: Pipe2XS is published as 11.7 against 2.375/0.204 = 11.64.
  Accepted; not asserted.
- **Six XS pipe rows, 14 to 26 in**: published A, I, S and Z are 2.9 to
  3.4% below the formulas; they match a wall of 0.90·t_nom, not the listed
  design wall of 0.93·t_nom. Not asserted; no guard member is this size.
- **The other pipe rows 12 in and over** (nine rows): misses in both
  directions (Pipe12XS area +2.6%; Pipe12XXS −2.5 to −2.9% on A, I, S and
  Z). Not asserted.
- **Round HSS over 10 in OD** (84 rows, 34 reproducing in full): the
  misses run mostly above published, the worst +1.9% on I, because the OD
  column is rounded. Not asserted.
- **Round HSS of 10 in or less with a rounded OD column** (38 rows, such
  as HSS2.375 listed as 2.38 in): no row reproduces every property; the
  worst misses are under 0.8%. Not asserted; used as published (S5-4).

### Verification

- Test case 6 (a custom noncompact tube rail, 2.375 × 0.055 in A500 Gr C,
  on a Pipe2STD post) and test case 7 (an HSS2.375X0.125 post at the
  default grade under a Pipe2STD rail) each have an independent calc
  written in a fresh session; every value agrees with the tool within
  0.5%. Case 6 is the noncompact case of issue #3: Eq. F8-2 governs.
- Micah ruled on the open questions of both independent calcs: the post
  wall at the base weld (W5), the directional increase as an election
  (W2), and thin material at a weld. His review of both calcs and both
  PDFs against the checklist is step 11 of the plan, ahead of the pull
  request.
- Cases 1–5: every recorded value is unchanged. Cases 4 and 5 and the
  example gained `directional_increase = true`, an input only.
- The property-formula test (above) checks the custom tube's formulas
  against AISC's published numbers, not against the tool's own.
- At this entry: 2008 tests passed, 33 skipped (the deferred [hand]
  values).

### Deferred to the release review (issue #18)

- Verification of the 43 slice 5 entries. Among them: the A500 Gr B and
  Gr C round Fy and Fu, which the calcs of cases 6 and 7 rest on; and the
  two AWS D1.1 entries, drafted from memory, whose 2020 clause number and
  wording are not confirmed.
- Micah's recompute of case 6's section properties and Check 1; those
  [hand] values read "deferred".

### Known gaps

- The A618 wall ranges and the A1085 wall rule are tested by same-author
  machinery tests only; no test case reaches them.
- Not checked: the Chapter K chord limit states (slice 6), local effects
  of the concentrated guard load on a thin tube wall (issue #28), and
  everything listed under v0.4.0.
- Only round hollow sections. Rectangular HSS and tubes are slice 6; solid
  bars are slice 7.
- A same-size pipe and round HSS pair of 10.75 in or larger still stops at
  the width comparison: the database rounds those ODs by more than the
  0.01 in tolerance.

## v0.4.0 (2026-10-09)

Slice 4: the intermediate rail and the anchor reaction sets. Merged in PR
#20; plan in docs/plans/slice-4.md.

**Milestone: the first complete all-pipe package.** `uv run handrail calc
examples/slice-1.toml` now prints all seven checks (Check 4 in two parts),
the summary table and the two LRFD anchor reaction sets for an AISC pipe
guard on a pipe post in A53 Gr B. It is the first calc that could stand in
for a real hand calc, under the DRAFT stamp.

### Checks covered

- **Check 4a, intermediate rail member**: the component load at midspan
  (M = P_c·L/4, Δ = P_c·L³/48EI), horizontal and downward (downward adds
  the rail's dead load, ASD D + L), with its own deflection limit (L/120
  default, bypassable). Same-as-top-rail prints an observation line
  instead.
- **Check 4b, intermediate rail weld to post**: a simple shear connection
  (e = 0, no end moment) at the post face, weld metal per §J2.4 with
  k_ds = 1.0, base metal on both walls (post wall and intermediate rail
  wall, shear rupture, the lower governing and named), minimum size.
- **Reaction sets**: lateral (any horizontal direction) and upward (only
  when 1.6L > 0.9D), 0.9D + 1.6L at the top of concrete; V, N (signed,
  tension positive) and M to 4 significant figures, with the governing
  load type and the D breakdown including the baseplate weight W_bp.
- Baseplate plan dimensions B × N are inputs. D at the post gains the
  intermediate rail's dead load (Checks 5 and 7 and the reactions; not
  Check 3 or 6).
- Effective throat t_e = 0.707w in every weld check (Micah's ruling).

### What it delivers

- Project file: `[intermediate_rail]` (same as top, own section, or
  none), `[welds] intermediate_rail_to_post`, `[baseplate] B` and `N`,
  `[loads] component_lb`, `[deflection.intermediate_rail]`. Conflicting
  inputs stop the calc.
- One shared per-direction demand function for Checks 5 and 7 and the
  reaction sets (issue #4); printed calcs of the example and cases 1–4 are
  unchanged.
- 15 new drafted registry entries (77 drafted, 32 verified in all). Every
  calc still prints the DRAFT stamp.

### Verification

- Test case 5, the milestone case, has a full independent calc of all
  seven checks and both reaction sets (391 values); every value agrees
  with the tool within 0.5%. Micah reviewed the case 5 PDF against the
  checklist and ruled on the independent calc's open questions (Check 4b as
  a simple shear connection, base metal on both walls, t_e = 0.707w).
- Cases 1–4 gained inputs only; every recorded value is unchanged.
- At release: 1138 tests passed, 25 skipped (the deferred [hand] values).

### Deferred to the release review (issue #18)

- Verification of the 15 slice 4 entries.
- Micah's recompute of case 5's Checks 4a and 4b and of the lateral and
  upward reaction sets (V, N, M each); those [hand] values read
  "deferred".

### Known gaps

- Not checked: the component load's effect on the post, the post wall's
  chord limit states at the intermediate rail, baseplate bending,
  anchorage, maximum fillet size, flare-bevel throats.
- Only round hollow sections, E70XX and A36 baseplate; an intermediate
  rail wider than the post stops the calc.

## v0.3.0 (2026-10-08)

Slice 3: the welds. Merged in PR #19; plan in docs/plans/slice-3.md.

`uv run handrail calc examples/slice-1.toml` now prints Checks 1, 2, 3, 5,
6 and 7 for an AISC pipe top rail on a pipe post in A53 Gr B, both joints
fillet welded all around.

### Checks covered

- **Check 3, top rail weld to post**: a flat ring of the post perimeter
  at the rail's underside, eccentricity e = D_rail/2 (W1, W9). Elastic
  weld-as-a-line, S_w = πD²/4, uniform shear, vector sum at the governing
  extreme fiber with θ printed (W3, W10). Weld metal per AISC 360-22 §J2.4
  with k_ds = 1.0 (W2); rail fusion face in shear rupture per §J4.2(b)
  (W6). Demand and capacity come from the governing line.
- **Check 7, post weld to baseplate**: the same ring at the post OD with
  the arm h − t_p; §J2.4 directional increase for round HSS (W2);
  baseplate base metal through t_p (W5). No separate fusion-face leg
  check on the baseplate (Micah's ruling on the case 4 independent calc).
- Both checks: Table J2.4 minimum size on the thinner part joined, read
  at the nominal wall, pass/fail; a printed line that §J2.2b(b) does not
  apply (W11). The post wall is covered by Check 5 (W5). Every direction
  case for both guard load types, with an envelope table; upward shows
  "no net tension" when 0.6D ≥ L.

### What it delivers

- Project file: `[welds]` (`rail_to_post`, `post_to_baseplate`, required;
  `electrode`, E70XX only) and `[baseplate]` (`grade`, A36 only).
- Validation runs before the calc, as its own step: post OD ≤ rail OD
  (W8), round hollow rail and post (W7), post grade Fu/Fy ≥ 1.20 (W5),
  electrode and baseplate grade (W12). Each stop names what it checked.
- Two new stated assumptions in the front matter: the Check 3 ring model
  with the flare-bevel sentence (W1, W9), and rail wall Chapter K chord
  limit states not checked (W7).
- Dimensions page echoes both weld sizes; Checks 3 and 7 pages; summary
  rows for both.
- 28 new drafted registry entries (62 drafted, 32 verified in all). Every
  calc still prints the DRAFT stamp.

### Verification

- Test case 4 (case 2's inputs with a 1/8" rail weld and a 1/4" post
  weld) is an independent-calc case for Checks 3 and 7; every value
  agrees within 0.5%. Micah reviewed the case 4 PDF against the review
  checklist and ruled on the independent calc's open questions (Q1–Q5).
- Test cases 1–3 gained the weld inputs only; every recorded value is
  unchanged. Case 3 (Pipe2STD post under a Pipe1-1/2STD rail) now stops
  at W8; its values are tested through the compute step.
- At release: 683 tests passed, 14 skipped (the deferred values below).

### Deferred to the release review (issue #18)

- Verification of the 28 slice 3 entries, with the round-HSS directional
  increase (`ej.weld.directional_round_hss`) checked closely: case 4's
  Check 7 passes only with k_ds = 1.5.
- Confirmation against Table J2.5 that no fillet fusion-face check is
  required on the baseplate.
- Micah's recompute of case 4's printed controlling cases of Checks 3
  and 7; those [hand] values read "deferred".

### Known gaps

- Check 4, the intermediate rail, the anchor reaction sets and baseplate
  B × N are not in this release (slice 4).
- Not checked: rail wall chord limit states (W7), baseplate bending,
  maximum fillet size, flare-bevel throats.
- Electrodes other than E70XX, baseplate grades other than A36,
  non-round sections and posts wider than the rail stop the calc.

## v0.2.0 (2026-10-04)

Slice 2: the post. Merged in PR #17; plan in docs/plans/slice-2.md.

`uv run handrail calc examples/slice-1.toml` now prints Checks 1, 2, 5 and
6 for an AISC pipe top rail and pipe post in A53 Gr B.

### Checks covered

- **Check 5, post combined axial and flexure** at the top of the baseplate,
  over the full envelope. Compression per AISC 360-22 Chapter E (Eq. E3-2
  or E3-3, Lc = K·h with K = 2.1 from Commentary Table C-A-7.1); tension
  yielding per §D2 for the upward case; flexure per §F8; interaction per
  Eq. H1-1a/H1-1b in the cases with moment. The downward and upward cases
  have no moment and report the Chapter E or Chapter D ratio instead. The
  longitudinal case is now a real, checked case for the post.
- **Check 6, post deflection**: cantilever deflection over h − t_p, live
  load only, in the horizontal cases, against L/60 (editable, bypassable).

### What it delivers

- Project file: post section, post height h, baseplate thickness t_p and
  the post deflection limit. Every project file now has a post.
- The first load path between members: the top rail's dead load and guard
  loads reach the post over the span as its tributary length, plus the
  post's own weight over h − t_p.
- Hard stops: slender in compression (Table B4.1a), and αPr/Pe above 0.05
  in a moment case (second-order effects; Appendix 8 amplification is not
  implemented). Lc/r above 200 is flagged, not stopped.
- Three new locked assumptions in the front matter: notional loads
  neglected, post loads on tributary length = span with rail continuity
  neglected, and baseplate thickness and bending not checked.
- 31 new drafted registry entries (34 drafted, 32 verified in all). Every
  calc still prints the DRAFT stamp.
- Pre-push hook (.githooks/pre-push) runs the test suite before a push.

### Verification model

From this slice on, checks are verified by an independent calc instead of
Micah's full hand calc (docs/brief/verification.md; ADRs 0004–0006). An
agent in a fresh session, which never reads `src/` or any tool output,
writes a complete calc of each new test case, and the test compares every
one of its values with the tool at 0.5%. Micah reviews that calc and the
printed calc against a written checklist.

- Test cases 2 (Pipe1-1/2STD post, Eq. E3-3) and 3 (Pipe2STD post,
  Eq. E3-2) are independent-calc cases; every value agrees within 0.5%.
- Test case 1 stays a full-hand case with its values unchanged.
- At release: 409 tests passed, 10 skipped (the deferred values below).

### Deferred to the release review (issue #18)

- Verification of every drafted registry entry: the 3 left from slice 1
  and the 31 from slice 2 (ADR 0005).
- Micah's line-by-line recompute of the printed controlling case of
  Checks 5 and 6 in test cases 2 and 3. Until then their [hand] values
  read "deferred" and the test skips them (ADR 0006).
- Any test case value that depends on an entry corrected in that review is
  redone from the corrected entry, never edited to the tool's output.

### Known gaps

- Eq. H1-1a is tested only against a same-author arithmetic test: in the
  moment cases Pr is dead load only, so no realistic guard post reaches
  Pr/Pc ≥ 0.2.
- Checks 3, 4 and 7, the intermediate rail, the anchor reaction sets,
  sections other than AISC pipe and the input form are not in this release.

## v0.1.0 (2026-09-30)

Slice 1: the first end-to-end run from a project file to a printed calc.

`uv run handrail calc examples/slice-1.toml` produces a PDF calc package for
an AISC pipe top rail in A53 Gr B, spanning simple-span between posts.

### Checks covered

- **Check 1, top rail bending**: round HSS classification (AISC 360-22
  Table B4.1b), Mn per §F8, allowable Mn/Ωb, over the full direction envelope.
- **Check 2, top rail deflection**: simple-span midspan deflection against
  L/120 (editable, bypassable by the engineer).

Checks 3-7, reactions, other shapes and the input form are not in this
release.

### What it delivers

- TOML project file, and a dimension parser accepting the forms in the brief
  (5' 6-1/8", 66.125 in, 3 ft 6 in, bare number as inches).
- AISC Shapes Database v16.0 PIPE rows extracted to `data/shapes-pipe.toml`,
  verified row for row against the original workbook.
- Code-value registry with drafted entries, review list, hard stop on a
  missing entry, and the "DRAFT: contains unverified code values" stamp.
  Every entry is still drafted; none is engineer-verified.
- Calc-line machinery with pint units; beam formulas cite AISC Manual
  Table 3-23.
- Envelope of direction cases (downward, outward, inward, upward,
  longitudinal). Every case is computed and listed; the controlling case
  prints in full. Slender sections and D/t beyond the §F8 limit stop the
  calc.
- PDF via Typst: development watermark, DRAFT stamp, version footer with
  uncommitted-changes flag, front matter, dimensions, section properties,
  loading, both checks, summary table.
- Test case 1 (Micah's hand calc) within 0.5% of the tool.

### Known gaps

- The noncompact branch (Eq. F8-2) is tested only against a same-author
  arithmetic rewrite, not a hand calc; a noncompact hand case is tracked in
  GitHub issue #3.
- Display-unit settings: issue #1.
