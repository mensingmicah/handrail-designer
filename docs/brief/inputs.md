# Brief: inputs

Part of the product brief; index in docs/BRIEF.md. What the engineer enters
and how it is entered.

## Inputs

- Project info: name, phase, one-line description, reference documents,
  and additional assumptions. The tool's own stated assumptions are locked
  and always printed; the engineer can add to them but not edit or remove
  them.
- A note on the input page states that loading is per ASCE 7-22. The PDF
  covers this through its code references.
- Distributed-load exemption: a checkbox. Ticking it opens a short text box
  where the engineer states that the guard falls under the ASCE 7-22
  §4.5.1.1 exemption; that text prints on the loading page. An info box next
  to the checkbox explains the exemption's requirements; its text comes from
  registry entries.
- Post height h, from top of concrete to the top rail centerline; span (post
  to post, center to center); baseplate thickness t_p and plan dimensions
  B × N. B and N give the baseplate weight and print beside the anchor
  reaction sets. (S4-6, Micah 2026-10-08.) B is the plate dimension
  parallel to the rail and N the one perpendicular to it, and they print
  labeled that way ("B = 6 in (parallel to rail) × N = 8 in
  (perpendicular to rail)"). Both are required under `[baseplate]`, with
  no default, entered like any dimension. Input validation stops the calc
  if B or N is ≤ 0 or smaller than the post OD. The front-matter key
  sketch (a static PNG, slice 8) shows the same orientation.
- The span is the tributary length for the post, a stated assumption
  (output.md)
- Every project has a post, post height and baseplate thickness: v1 always
  checks one post. A baseplate thickness of zero or less, or not less than
  h, is rejected at input. (Slice 2, D9.)
- Top rail and post sections: pick an AISC designation, or define a custom
  section by dimensions. For a custom tube, the wall entered is always the
  nominal wall; there is no nominal/design choice (S5-8, below). For rectangular sections, the engineer sets
  which axis resists the horizontal guard load.
- Intermediate rail: one of three states (S4-1, checks.md). Same as the
  top rail (a checkbox, `same_as_top_rail`, default checked): section and
  grade are the top rail's. Unchecked: the engineer enters the section,
  and the grade defaults to the top rail's. Or none (`none = true`): no
  intermediate rail. There is no intermediate rail height input; nothing
  in v1 uses it. (Micah, 2026-10-08.)
  - Conflicting inputs stop the calc and are never silently ignored
    (Claude's decision, confirmed by Micah 2026-10-09): `none = true` with
    a section, a grade or an intermediate weld size; a section, grade or
    intermediate weld size given while `same_as_top_rail` is true;
    `same_as_top_rail = false` with no section. The intermediate rail to
    post weld size is required in the own-section state only.
- Material grade for rail, post and baseplate. The standard grade lists for
  pipe, round HSS and rectangular HSS are registry entries
  (material.grades.pipe, material.grades.hss_round, material.grades.hss_rect;
  AISC Manual Table 2-4). Two different cases:
  - A grade with no Fy or Fu registry entry for the member's shape stops
    the calc with a message naming the grade and the grades supported for
    that shape. Since slice 5 the rail and post grades are those under
    "Grades for pipe, round HSS and custom round tubes" below; A36 is
    still the only baseplate grade (W12).
  - A grade that has its entries but is outside the standard list for the
    shape is an unusual pairing, and gets a warning, not a block. Built in
    slice 5: it prints on the section properties page, under the member.

  The grade list for solid bars and baseplate is not yet in the registry.
  A500 (Gr B, Gr C) is never offered for solid bars, and the defaults
  are bars A36, pipe A53 Gr B, round HSS and custom round tube A500 Gr B
  (S5-5, below), baseplate A36: these are my engineering
  decisions, not registry entries. Every Fy and Fu is a registry entry
  citing the AISC Manual: Table 2-4 for shapes (pipe, HSS), Table 2-5 for
  plates and bars (for example, A36 Fy per Table 2-5).
- Welds at the rail to post and post to baseplate connections: fillet welds,
  size entered, E70XX electrode by default. Round posts are welded all
  around. Rectangular posts (HSS or bar) are welded all around or on one
  pair of faces, which the engineer picks by the section's width or depth
  faces.
  The two weld sizes (rail to post, post to baseplate) are required
  inputs with no default, entered like any dimension ("3/16"). The
  electrode is an input defaulting to E70XX, and E70XX is the only one
  accepted; any other stops with a message. The baseplate grade is an
  input defaulting to A36, and A36 is the only one accepted; any other
  stops with a message. More baseplate grades come with baseplate checks
  (after v1, docs/ROADMAP.md); more rail and post grades come with the
  section families. (Slice 3, W12.)
- Guard loads (concentrated, distributed, component), defaulting to code
  values, editable
- Deflection limits: L/120 for the rail span and L/60 for the post
  cantilever by default. These are engineering experience, not code. Each is editable
  and each can be bypassed by checkbox.
- Dimensions must accept the forms engineers actually type: 5' 6-1/8",
  66.125 in, 3 ft 6 in, 42. A bare number is inches in every field. The
  normalized value is echoed in gray next to the box (42 → 3'-6") and again
  on the calc's dimensions page.

## Grades for pipe, round HSS and custom round tubes (slice 5)

Decided in planning slice 5 (docs/plans/slice-5.md); S5 numbers are that
plan's decision numbers. (S5-5, Micah 2026-10-09.)

- **Where this is going.** Every shape can use every grade the AISC
  Manual lists for it: Table 2-4 for pipe and HSS. This replaces "A500
  Gr B and Gr C only" as the limit for HSS.
- **In the form (slice 8).** The grade dropdown shows the preferred and
  common grades in a separate group at the top, and the rest of the
  shape's Table 2-4 grades below. The TOML project file just takes the
  grade name.
- **Defaults.** Round HSS and custom round tube: A500 Gr B (conservative,
  and commonly specified). Pipe: A53 Gr B, as before.
- **The intermediate rail's default grade.** (S5-10, Micah 2026-10-09;
  it refines S4-1, "the grade defaults to the top rail's".) An
  intermediate rail of its own section takes the top rail's grade when
  that grade is on the standard list for the intermediate rail's own
  shape (any grade a custom tube accepts, for a custom tube). Otherwise
  it takes its own shape's default. So an HSS intermediate rail under a
  pipe top rail defaults to A500 Gr B, not to A53 Gr B with a warning.
- **A defaulted grade prints as defaulted,** for every member, not only
  the intermediate rail: "A500 Gr B (default)". (S5-10, Micah
  2026-10-09.) It prints on the section properties page, where each
  member's grade already prints. "Every member" is the top rail, the post
  and the intermediate rail; the baseplate grade and the electrode, which
  accept one value each, are not marked.
- **Slice 5 splits the Table 2-4 grades for pipe and round HSS in two.**
  A plain grade differs from the others only in Fy and Fu; slice 5 drafts
  the Fy and Fu entries for every plain grade. A grade with a rule of its
  own (A1085's design wall under §B4.2, for example) is decided one grade
  at a time, each as its own numbered decision below. Until a grade has
  its Fy and Fu entries it stops the calc, naming the grade and the
  grades supported, as before.
- **Custom round tube** accepts every grade round HSS does, plus A53
  Gr B. None of them is an unusual pairing for a custom tube.
- **Unusual pairings on database sections** (an HSS grade on a Pipe
  designation, A53 Gr B on an HSS designation) are allowed, with the
  printed warning this file already calls for. Slice 5 builds the
  warning.
- **Verify before the independent calcs.** I verify the A500 Gr B and
  Gr C round Fy and Fu entries against Table 2-4 before slice 5's
  independent calcs run: ASTM A500-21 changed the round values, and both
  new test cases turn on them. This is my choice for these four values,
  not a gate on the slice (ADR 0008 as amended).

### The plain grades and the grades with a rule of their own

The split of S5-5, as drafted for slice 5 (Claude, 2026-10-09, from memory
of AISC Manual Table 2-4 and one secondary article; every Fy and Fu is a
drafted registry entry until I verify it).

- **Plain** (only Fy and Fu differ): A53 Gr B (pipe); for round HSS, A500
  Gr B, A500 Gr C, A501 Gr A, A501 Gr B and A847. A501 is plain only if
  the §B4.2 wall rule is by ASTM standard (below).
- **A1065** is not a round HSS grade. It moves to slice 6 with
  rectangular HSS, and the registry's drafted round HSS list
  (`material.grades.hss_round`) is corrected in slice 5. (Micah,
  2026-10-09.)
- **A1085 Gr A is offered in slice 5.** (S5-6, Micah 2026-10-09.) It
  follows the two rules already in checks.md.
  - A database section runs on its published properties, on
    t_des = 0.93·t_nom, and prints a note that also says how to get the
    credit. Roughly: "A1085: AISC 360-22 §B4.2 permits the nominal wall;
    database properties are used as published, on t_des = 0.93·t_nom. To
    use the nominal wall, enter the tube as a custom section." Claude
    proposes the final wording on the slice 5 branch.
  - A custom A1085 tube uses t_des = t_nom (§B4.2). Its wall, like every
    custom tube's, is entered as the nominal wall (S5-8).
  - Accepted: the same tube gives two answers, about 7% apart on wall
    thickness, by the route it is entered. The database route is the
    conservative one.
- **The §B4.2 wall rule is drafted from the 360-22 text, not from
  memory.** (Micah, 2026-10-09.) His recollection is that since 360-16 it
  reads: nominal wall for A1065 and A1085, 0.93·t_nom for HSS to other
  approved standards, which makes A501 plain. If the 360-22 text still
  keys on ERW against SAW, the work stops and Claude asks him, because
  seamless A501 would then need a ruling.
- **A618 is offered in slice 5, with its Fy and Fu by wall thickness.**
  (S5-7, Micah 2026-10-09.) Values as drafted, from memory of AISC Manual
  Table 2-4, to be verified like every other entry:

  | Grade | Wall | Fy / Fu (ksi) |
  | --- | --- | --- |
  | A618 Gr Ia, Ib, II | up to 3/4 in | 50 / 70 |
  | A618 Gr Ia, Ib, II | over 3/4 in to 1-1/2 in | 46 / 67 |
  | A618 Gr III | all walls | 50 / 65 |

  - Each grade name (Ia, Ib, II, III) has its own entries. The registry's
    drafted list, which names them "I, II, III", is corrected.
  - The wall compared with the limits is the nominal one: t_nom for a
    database section, the nominal wall entered for a custom tube (S5-8). The limit is
    on the product's thickness, the reasoning of W11 (welds.md) for Table
    J2.4. A wall of exactly 3/4 in takes the "up to 3/4 in" values.
  - A Gr Ia, Ib or II wall over 1-1/2 in stops the calc: Table 2-4 gives
    no values there. The stop names the member, its wall, the grade and
    the limit.
  - Fy and Fu are stored in the registry by wall range, and the two
    limits (3/4 in and 1-1/2 in) are entries too, so slice 6's
    rectangular A618 reuses the same entries and the same lookup.
  - Testing: same-author machinery tests only (a wall at exactly 3/4 in,
    one just over it, and one over 1-1/2 in that stops). No test case
    reaches the branch, and I do not review it by hand; the
    calc-code-review session covers the code. It is listed with the
    known test gaps on the release-review issue (#18) when slice 5
    closes.
  - The entries are drafted like all the others, go in slice 5's
    registry review workbook, and I verify them at the release review.

## Custom round tube input (slice 5)

(S5-8, Micah 2026-10-09.) This supersedes two earlier lines of the brief:
"the engineer says whether the entered wall thickness is nominal or
design", and "a custom tube's weight uses the wall thickness as entered".

- **A custom tube's wall is always the nominal wall.** There is no
  nominal/design flag. The key is `wall_nominal`, so the project file says
  what the number is. It is required, with no default.
- **The design wall follows §B4.2 by grade:** t_des = 0.93·t_nom, or
  t_des = t_nom for A1085 (S5-6).
- **What each wall feeds.** t_nom: Table J2.4's minimum fillet (W11), the
  A618 wall ranges (S5-7) and the weight. t_des: section properties and
  strength, including the fusion face thickness (W4).
- **The section page prints both**, roughly: "t_nom = 0.120 in (as
  entered); t_des = 0.93·t_nom = 0.112 in, AISC 360-22 §B4.2".
- **Why no flag.** Every grade allowed for a custom tube is specified by
  its nominal wall. The only error this rule allows is entering a wall
  that has already been reduced, which is then reduced again: that is
  conservative. A nominal/design flag would allow the unconservative
  error, a nominal wall marked "design", with no sign of it in the
  output.
- **Project file.** A custom round tube is entered with
  `shape = "round tube"`, `OD` and `wall_nominal` in place of `section`.
  Giving `section` together with any of those stops the calc as
  conflicting inputs, like the intermediate rail's stops. A wall of half
  the OD or more stops. The printed label reads like "Round tube 2.375 ×
  0.055 (custom)". (Claude's proposals, accepted by Micah 2026-10-09;
  exact wording on the branch.)
- Slice 6 applies the same rule to custom rectangular tubes.

## Stops and supported combinations (slice 5)

(S5-9, Micah 2026-10-09; from the architecture review of 2026-10-09, F9.)
A stop is any place the tool refuses to compute and says why: a bad or
conflicting input, a section it will not check, a combination of sections
it has no decision for.

- **One table per joint says which section families may meet there.** The
  joints are the Check 3 joint (top rail as chord, post as branch), the
  Check 4b joint (post as chord, intermediate rail as branch) and the
  Check 7 joint (post on the baseplate). Each cell is either "allowed" or
  a stop message citing the decision behind it. A family not built yet
  has a row that says which slice brings it.
- **Allowed means listed as allowed.** A pair of families with no cell in
  a joint's table stops the calc, with a message naming the joint and both
  families. Nothing unlisted is ever computed. (Binding; Micah,
  2026-10-09.) A test gives each of the three joints a stand-in family
  with no row and confirms the stop.
- **docs/brief/stops.md lists every stop:** an id, the condition, the
  decision it comes from, and the test that triggers it. The per-joint
  tables print there too. Rules about dimensions, not families, stay
  ordinary stops and are on the same list: W8, S4-11, the chord D/t limit
  (S5-3), the A618 wall limit (S5-7), B and N against the post OD.
- **A test holds the code to that file,** as a test holds the printed
  assumptions to output.md: every stop in the code has an id that is in
  stops.md, and every id in stops.md has a test that triggers it. So
  stops.md, like the assumptions list, changes only on a calc branch, in
  the same commit as the code it describes (CLAUDE.md, Git). It is
  created on the slice 5 branch, in the refactor step (issue #21), with
  the golden snapshots proving no printed calc changes.
