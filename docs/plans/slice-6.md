# Slice 6 plan: hollow rectangular sections and the round chord check

Status: **planned** 2026-10-11, from Micah's rulings S6-1 to S6-16 in the
planning interview of 2026-10-10 (S6-16 confirmed 2026-10-11). Frozen once
pushed: the build does not edit this plan. Anything the build finds wrong
or missing here is reported to Micah, not written in.

> This plan is a record of what slice 6 sets out to build and why. The
> binding engineering decisions (S6-1 to S6-16) are in the brief:
> docs/brief/checks.md ("Hollow rectangular sections (slice 6)"),
> docs/brief/welds.md ("Hollow rectangular sections and the chord limit
> states (slice 6)"), docs/brief/inputs.md ("Rectangular sections (slice
> 6)"), docs/brief/verification.md and docs/brief/scope.md. Where this
> plan differs from docs/BRIEF.md, CLAUDE.md or a later plan, those
> govern. T1 to T5 below are test decisions, not tool behavior, and stay
> here.

## Goal

Widen the section layer to hollow rectangular sections: rectangular and
square HSS from the Shapes Database and custom rectangular tubes, as top
rail, intermediate rail and post, alone or mixed with round members. Then
turn the rail-wall assumption (W7) into a check where the code gives one:
the AISC 360-22 Chapter K chord limit states of a round rail at a round
post, inside Check 3. No check is added to the seven. Test cases 1 to 7
must pass exactly as they do today, and their printed calcs must not
change except in the places listed under "Intended changes to existing
printed calcs".

Slice 6 is one slice, not two (S6-1). Solid bars are slice 7.

## Decisions settled for this slice

S6-1 to S6-16 are in the brief, with Micah's name and date on each. In
short:

| No. | Decision | Brief |
| --- | --- | --- |
| S6-1 | One slice. Build order: rectangular members, then welds, then the chord limit states. The chord check prints as one compact table per joint, with full calc lines for the governing limit state always and for any other over 0.5. | checks.md, welds.md |
| S6-2 | Orientation is a geometric input, `long_side`: vertical or horizontal for a rail, perpendicular or parallel to the rail for a post. Required for a non-square rectangle, a stop on a square or round member. The axes are derived and printed. | inputs.md |
| S6-3 | A custom rectangular tube has no corner radius input: properties on a 2·t_des outside radius, b/t and h/t on the outside dimension less 3·t_des (§B4.1b(d)), weight on the nominal wall. The property-formula test binds on rows with Ht ≤ 8 in. | checks.md |
| S6-4 | Flexure by §F7 in full: yielding, flange and web local buckling, LTB with Cb from each case's own moment diagram (Eq. F1-1), Lb = span. Rectangular members combine axes by §H1.1, not SRSS. Post Cb = 1.0. J for a custom tube from the midline formula. | checks.md |
| S6-5 | Every Table 2-4 grade for rectangular HSS, default A500 Gr B; A618 reuses slice 5's wall ranges; A1085 as S5-6; no A53 for a rectangular tube; A1065 not offered in v1. | inputs.md |
| S6-6 | Rectangular post base weld: `base_pattern`, all around or one face pair, required with no default. All around is the true rounded rectangle; a face pair is two flat lines. k_ds = 1.0; electing the increase with a rectangular post stops. | welds.md |
| S6-7 | At a face-pair base weld the post wall is checked on its own lines (axial against §J4.1, along the face against §J4.2), not combined, and that is a printed assumption. All around stays "covered by Check 5". A slender welded wall is caught by the existing compression stop. | welds.md |
| S6-8 | The weld at a rectangular chord uses Table K5.1's effective properties (Eqs. K5-5 to K5-7, Be per Eq. K1-1). The round ring model stands; Table K5.2 does not reach it. | welds.md |
| S6-9 | Every pair of round hollow and rectangular hollow may meet at both rail to post joints, mixed pairs included. At a mixed pair the weld is the branch's own outline, flat. The width rule (branch no wider than the chord) is exact. | welds.md |
| S6-10 | The round chord check, Check 3 only: chord plastification and punching by Tables K3.1 and K4.1 for each direction case, combined by Eq. K4-5, with Qf from the rail's Check 1 moment as a bound on the continuity moment. | welds.md |
| S6-11 | At Check 4b the chord limit states have no demand (simple shear connection): one printed line, no table. | welds.md |
| S6-12 | A rectangular chord's limit states are not computed in v1: a stated assumption inside the Chapter K limits. | welds.md, scope.md |
| S6-13 | The Chapter K limits of applicability are stops, at Check 3 only: the full round set for round on round; the chord's own limits for a rectangular chord or a mixed pair; none at Check 4b. A500 Gr C is a named exception to Fy/Fu. | welds.md |
| S6-14 | Ten carry-overs: the weld envelope and centerline rulings; Check 5 on a rectangular post; classification with reduced strength for a noncompact wall; the Fu/Fy guard; the same-as-top observations; custom tube input; the baseplate size stop per direction; a database finding; assumption wording. | checks.md |
| S6-15 | Test cases: case 6 extended with the chord table; case 8 all rectangular; case 9 a square post under a pipe rail with a rectangular intermediate rail. Recompute: case 6 the governing chord limit state; case 8 Checks 1, 3, 7; case 9 Checks 5, 7. | verification.md |
| S6-16 | Eight findings from cross-checking the rulings, confirmed by Micah 2026-10-11: the chord table has its own summary row and keys; the S6-11 line prints for every pair; S6-4 covers Check 4a; one assumption sentence replaces W7's; J held at printed precision; base metal lines carry over; case 6 runs by the A500 Gr C exception; the post D/t stop goes. | checks.md |

Decided outside the interview and applied here:

- **ADR 0008 as amended.** Nothing in this slice waits on registry
  verification.
- **Micah's standing rule for this slice's planning** (2026-10-10,
  welds.md): where a refinement is unlikely ever to govern a realistic
  guard, lead with the leanest compliant option.
- **Two brief files are calc code** (CLAUDE.md, Git): docs/brief/stops.md
  and the "Stated assumptions" list in docs/brief/output.md change on the
  branch, in the commit of the code they describe. No other brief text
  changes during the build.

## Open for Micah

Points the rulings leave unsettled, or where the 360-22 text reads
differently from a ruling's paraphrase. None is decided here. Each says
what the build does until he rules; in every case that is the option that
leaves existing calcs unchanged, or the one that follows the code text as
printed.

1. **Table K5.1's cap on Be.** S6-8 says "Be/2 not over Bb/4 when
   β > 0.85". The table (page 16.1-171) reads "when β > 0.85 or θ > 50°".
   Every joint in this tool is θ = 90°, so as printed the cap applies at
   every joint, not only above β = 0.85. The two readings differ only
   where β ≤ 0.85 and Be would exceed Bb/2, which needs a stocky chord
   (B/t under about 20 at equal walls and grades; HSS2×2×1/8 is 17.2).
   Until ruled: the build applies the table as printed, which never gives
   a longer weld than the other reading. Cases 8 and 9 have β = 1 at
   every rectangular joint, so no recorded value depends on the answer.
   Recommendation: confirm the table as printed, and correct S6-8's
   sentence.
2. **The width ratio's upper bound and the 0.01 in OD tolerance.** S6-13
   makes 0.2 < Db/D ≤ 1.0 a stop for round on round. Test case 7 (an
   HSS2.375 post, published OD 2.38 in, under a Pipe2STD rail, 2.375 in)
   has Db/D = 1.002, and S5-4's tolerance was ruled for W8 and S4-11
   only. Applied without it, the new stop would refuse case 7 and two
   second-tier calcs. Until ruled: W8, with its tolerance, stays the only
   test of the upper bound, the new stop tests the lower bound alone, and
   the chord equations use each member's published OD (β = 1.002 for
   that pair). Recommendation: rule exactly that.
3. **S6-7's "force along the face" when the shear is normal to the
   welded faces.** With the faces parallel to the rail welded, a
   transverse load's shear is normal to those faces, neither along the
   post axis nor along the face. Until ruled: the build follows the
   ruling's words, resolving the weld force along the post axis and along
   the face; a shear normal to the welded faces enters the weld metal
   line (as now) and neither post wall line, and the calc says so.
   Alternative: take the whole shear V/L against shear rupture in every
   case, which is conservative and prints a slightly larger
   non-governing ratio (about 0.05 in planning arithmetic).
   Recommendation: the alternative, if Micah prefers one rule for every
   case. To settle before the case 9 independent calc.
4. **The `base_pattern` echo on a round post.** S6-6 echoes the pattern
   on the dimensions page and lets a round post leave the key out. It
   does not say whether a round post's calc prints "all around" there.
   Until ruled: the echo prints for a rectangular post only, so no
   existing calc changes. Recommendation: keep that.
5. **Issue #28, second question: the concentrated guard load's local
   effect on a thin wall away from a joint.** S6-13 answers #28's
   applicability questions; no S6 ruling answers this one. Nothing is
   built for it. Recommendation: no check in v1 (Chapter K is written for
   forces delivered through a branch or plate; the chord limits D/t ≤ 50
   and B/t ≤ 35 already bound the wall), stated in one assumption
   sentence if Micah wants it printed.
6. **Two existing stop scenarios reach a new stop first.**
   `stop-second-order` (a Pipe20XS rail on a Pipe2STD post, Db/D = 0.12)
   and `stop-tube-slender` (a 6 × 0.065 in tube post, Db/tb = 99) are
   refused by S6-13's new limits before they reach the stop they were
   written for. Their stop messages change (intended change C8). Until
   ruled: the files keep their inputs and record the new message; the
   stops they were written for stay held by `stop-second-order-tall` and
   by new triggers in tests/test_stops.py. Recommendation: re-point both
   (a rectangular rail over the same post is held to the chord's own
   limits only), as Micah did for `stop-second-order` in slice 5.
7. **The inputs of cases 8 and 9** (T2 and T3) are Claude's proposal:
   S6-15 fixes what each case is, not its sections, weld sizes or
   pattern. One consequence to confirm with them: under S6-6 a face pair
   is run in all five direction cases, and in the direction that bends
   the two weld lines about their own length it reads NG by a factor of
   3 to 6 at guard loads (planning arithmetic under T3). S6-7's planning
   arithmetic looked at the favourable direction only. Case 9 as
   proposed therefore prints Check 7 NG. To confirm, or change, before
   the independent calcs run.

## Test decisions

**T1. Test case 6, extended with the round chord table** (S6-15, S5-3).
No input changes. The chord table reports under its own group,
`check3_chord`, so `check3.ratio` keeps its meaning in cases 4 to 7
(S6-16 item 1) and no other case gains a key.

- `covers` gains `check3_chord`; `recompute` gains `check3_chord`.
  Micah's [hand] value, deferred to the release review: the governing
  chord limit state (its direction case and ratio).
- The independent-calc file gains the new keys as "pending". No existing
  value in either of case 6's files is touched. A fresh independent-calc
  session fills the new keys only.
- Case 6 runs under the Chapter K limits only by the A500 Gr C exception
  (S6-16 item 7): the rail's drafted Fy/Fu is 50/62 = 0.81.

Rough figures (planning arithmetic from welds.md S6-10; not test
values): Pn of Eq. K3-2 ≈ 4.6 kips (2.75 allowable); Mn-op of Eq. K4-3 ≈
4.9 kip-in (2.9 allowable); the outward case interacts at about 0.12 with
Qf = 1, a little more with Qf; punching does not apply (Db ≥ D − 2t).

**T2. Test case 8, all rectangular** (S6-15). Claude's proposal for the
inputs, from the sections the rulings' own planning arithmetic used; open
item 7.

- Top rail: HSS4X2X1/8, `long_side = "vertical"`. Post: HSS3X2X1/8,
  `long_side = "parallel to rail"`. Intermediate rail: its own section,
  HSS2X1-1/2X1/8, `long_side = "horizontal"`. Every grade left out (the
  A500 Gr B default).
- L = 6'-0", h = 42 in, t_p = 1/2 in; B = 6 in × N = 8 in; A36 baseplate.
  Welds: rail to post 1/8 in, intermediate rail to post 1/8 in, post to
  baseplate 3/16 in, `base_pattern = "all around"`; E70XX.
- Default loads, no exemption; default deflection limits.
- `covers`: every group (section, Checks 1 to 7 and the reactions).
- `recompute`: check1, check3, check7.
- Why these. The rail on edge puts the horizontal guard load on the weak
  axis, where the 4 in wall is a noncompact flange (h/t = 31.5 against
  λp = 28.1), so the governing case of Check 1 reaches Eq. F7-2, the
  dead load's strong-axis LTB with Cb (Lb = 72 in against Lp ≈ 69 in) and
  the §H1.1 combination together. The post is not square, so its
  `long_side` and the per-axis reads of Checks 5 and 6 have a case: the
  transverse cases bend its weak axis. Post and rail are both 2 in wide
  at the Check 3 joint, and the intermediate rail is 2 in wide on the
  post's 2 in face, so β = 1 at both rectangular joints (open item 1).
  The rail's H/t is 34.5, inside the limit of 35.

Rough figures for case 8 (planning arithmetic, not test values), at the
drafted Fy = 46 ksi. Check 1, outward concentrated: Mn,y by Eq. F7-2 ≈
44.2 kip-in, Mr,y = 3,600 lb-in, with the dead load's 257 lb-in on the
strong axis: about 0.14. Check 2 about 0.10. Check 3 by Table K5.1: Be =
1.0 in, le = 8 in, about 0.05 to 0.06. Check 5, transverse, weak axis:
Mr = 12,450 lb-in against Mc ≈ 22.1 kip-in, about 0.57; Lc/r ≈ 110, Eq.
E3-2. Check 6 about 0.51. Check 7 on the rounded rectangle: about 0.65.

**T3. Test case 9, a mixed pair with a rectangular intermediate rail**
(S6-15). Claude's proposal for the inputs; open item 7.

- Top rail: Pipe2STD. Post: HSS2X2X1/8. Intermediate rail: its own
  section, HSS2X1X1/8, `long_side = "horizontal"`. Every grade left out
  (A53 Gr B for the pipe, A500 Gr B for the HSS).
- Geometry, baseplate and loads as case 8. Welds: rail to post 1/8 in,
  intermediate rail to post 1/8 in, post to baseplate 3/16 in,
  `base_pattern = "faces parallel to rail"`; E70XX.
- `covers`: post, check3, check4a, check4b, check5, check6, check7,
  reactions. The section group and Checks 1 and 2 are not covered: the
  pipe rail is cases 1 to 5's.
- `recompute`: check5, check7.
- Why these. The square post under a pipe rail is the detail Micah ruled
  must run (S6-9), and S6-7's planning arithmetic is this post with this
  weld. Check 3 is the mixed pair (the post's rounded rectangle on the
  pipe, e = D_rail/2). Check 4b is a rectangular branch on a rectangular
  chord (Table K5.1, β = 1). Check 7 is the face pair with S6-7's post
  wall lines.

Rough figures for case 9 (planning arithmetic, not test values). Check
5: Lc/r ≈ 116, Eq. E3-2; H1-1b ≈ 0.78. Check 6 ≈ 0.73. Check 3 ≈ 0.05.
Check 4b ≈ 0.01. Check 7, faces parallel to the rail, flats of 1.536 in
at ±1.0 in: transverse, S_w = 3.07 in², f ≈ 4.05 kip/in against 2.78,
about 1.46 under the distributed load (0.97 under the concentrated
load, S6-7's figure); longitudinal, S_w = 0.79 in², f ≈ 15.8 kip/in,
about 5.7. So Check 7 prints NG, governed by the longitudinal case (open
item 7). All around on the same post would be about 0.91.

**T4. The property-formula test for custom rectangular tubes** (S6-3,
S6-4, S6-16 item 5). The custom tube's formulas are run on the
rectangular HSS rows of the Shapes Database.

- **Binding:** the rows with Ht ≤ 8 in (208 in the scratch trial). A,
  Ix, Iy, Zx, Zy, Sx, Sy, rx and ry reproduce or come out below
  published, never above, and no more than 1% below. Weight within 0.5%.
  J reproduces at the database's printed precision.
- **Reported, not asserted:** the larger rows; the one row where the
  trial missed J.
- **A row above published in the binding set stops the build and goes to
  Micah.** The tolerance is never widened.

**T5. Machinery tests** (same-author), for what cases 8 and 9 do not
reach:

- `long_side`: missing on a non-square rail and post; given on a square
  and on a round member; each of the four orientations maps to the
  printed axes.
- Custom rectangular tube: H < B; a wall leaving no flat (B ≤ 4·t_des);
  `section` given with H or B; a square custom tube; the label; A1085 on
  t_des = t_nom.
- Classification: a noncompact flange (Eq. F7-2) and a noncompact web
  (Eq. F7-6) on stand-in sections; a slender flange, a slender web and a
  slender wall in compression each stop.
- LTB: Lb ≤ Lp, Lp < Lb ≤ Lr and Lb > Lr; a square section and weak-axis
  bending print the no-LTB line; Mn capped at Mp.
- Cb: the uniform load, the midspan point load, each combined with the
  dead load, against closed-form values; the cantilever's 1.0.
- Grades: each rectangular grade's Fy and Fu; A618 by wall; A53 Gr B and
  A1065 refused on a rectangular member.
- Check 7: each `base_pattern` on a square and a non-square post, in all
  five cases; the key missing on a rectangular post; a face pair on a
  round post; `directional_increase = true` on a rectangular post; a
  face pair on a post with a slender wall stops at the existing
  compression stop (S6-7).
- Table K5.1: Be uncapped; Be capped; the β ≤ 0.85 stocky-chord joint of
  open item 1, marked as waiting on Micah.
- Mixed pairs, both ways round, at both joints; the width rule at each
  (equal widths allowed, wider stops), exact for a rectangular member and
  with the 0.01 in tolerance where both are round.
- Chapter K limits (S6-13): each limit, on the member it applies to, and
  no stop from the branch limits at a rectangular chord or a mixed pair;
  the A500 Gr C exception; no stop at Check 4b for a post over D/t = 50
  with an intermediate rail under a rectangular rail.
- The round chord table: punching applies (Db < D − 2t) and does not;
  Qf below 1.0 and Qf = 1.0 (upward); a second limit state over the 0.5
  threshold prints its lines; the summary row prints only for round on
  round.
- Check 4b: the S6-11 line for each of the four pairs; a rectangular
  member forces the full check (S6-14 item 5).
- The baseplate size stop in each direction for a non-square post.
- Every new stop id is in stops.md and has a trigger (the existing test).

## Supported combinations

The per-joint tables as slice 6 leaves them (S6-9). The code holds them
as data; docs/brief/stops.md prints them. "Allowed" is subject to the
width rule and the Chapter K limits listed after the tables.

Check 3 joint (top rail = chord, post = branch) and Check 4b joint (post =
chord, intermediate rail = branch): the same table for both. "Round
hollow" is AISC pipe, round HSS and custom round tube; "rectangular
hollow" is rectangular and square HSS and custom rectangular tube.

| Chord \ Branch | Round hollow | Rectangular hollow | Solid bars |
| --- | --- | --- | --- |
| Round hollow | allowed; at Check 3 the chord wall is checked (S6-10) | allowed, mixed; chord wall not checked | stop: slice 7 |
| Rectangular hollow | allowed, mixed; chord wall not checked | allowed; chord wall not checked (S6-12) | stop: slice 7 |
| Solid bars | stop: slice 7 | stop: slice 7 | stop: slice 7 |

Check 7 joint (post on the baseplate; A36 plate is the only baseplate):

| Post | Cell |
| --- | --- |
| Round hollow | allowed: welded all around; W2's directional increase may be elected |
| Rectangular hollow | allowed: `base_pattern` required; k_ds = 1.0 (S6-6) |
| Solid bars | stop: slice 7 |

Stops this slice adds to the list in stops.md, each with its id, row and
trigger in the commit that adds it: `long_side` missing or not applicable
(S6-2); the custom rectangular tube input stops (S6-14 item 6);
`base_pattern` missing, or a face pair on a round post, or the increase
elected on a rectangular post (S6-6); a slender flange, web or wall on a
rectangular section (the existing stops, on b/t and h/t); the width rule
for rectangular and mixed pairs (W8 and S4-11 extended, S6-9); the
Chapter K limits (S6-13): rail B/t or H/t over 35, rail Fy over 52 ksi,
rail Fy/Fu over 0.8, and for round on round the post's Db/tb, the width
ratio's lower bound, and the post's Fy and Fy/Fu; the baseplate size stop
per direction (S6-14 item 8). One stop goes: the post's D/t over 50 with
an intermediate rail (S6-16 item 8).

## What the slice does

### Input

The project file gains (bare numbers are inches):

- A member takes a rectangular or square HSS designation in `section`,
  or a custom rectangular tube: `shape = "rectangular tube"`, `H`, `B`
  and `wall_nominal`, with H ≥ B.
- `long_side` on a non-square rectangular member: `"vertical"` or
  `"horizontal"` for a rail, `"perpendicular to rail"` or `"parallel to
  rail"` for a post (S6-2).
- `[welds] base_pattern`: `"all around"`, `"faces parallel to rail"` or
  `"faces perpendicular to rail"`, required for a rectangular post
  (S6-6).
- `grade`: the rectangular HSS grades (S6-5); the defaults of S5-5 and
  S5-10.

The dimensions page echoes a custom tube's H, B and nominal wall, and
the base pattern for a rectangular post (open item 4 for a round one).
The section page prints each rectangular member's orientation and which
axis each load bends (S6-2).

### Engineering

- **Sections.** Rectangular HSS rows extracted from the workbook like
  the pipe and round HSS rows, values as published, with the row-for-row
  test. A database section classifies on its published b/t and h/t; a
  custom tube on the outside dimension less 3·t_des (S6-3).
- **Flexure** (S6-4, S6-14 item 3): §F7 about the axis bent, the lowest
  of yielding, flange local buckling, web local buckling and LTB; Cb by
  one shared function from the case's moment diagram.
- **Check 1** on a rectangular rail: each direction case puts its
  vertical moment on one axis and its horizontal moment on the other,
  by `long_side`, and combines them by Eq. H1-1b with Pr = 0. Round
  rails keep SRSS.
- **Check 2**: each case deflects about the axis it bends, on that
  axis's I (S6-2). Nothing else changes.
- **Check 4a** as Check 1 for the intermediate rail's own orientation
  (S6-16 item 3); the same-as-top observation is kept (S6-14 item 5).
- **Checks 5 and 6** on a rectangular post (S6-14 item 2): the smaller r
  in compression; one moment per lateral case on the axis that case
  bends; αPr/Pe and the deflection on that axis's I; Cb = 1.0, Lb = h.
- **Check 7** on a rectangular post (S6-6, S6-7): the weld line of the
  chosen pattern, the elastic line method in all five cases, k_ds = 1.0,
  and for a face pair the post wall lines.
- **Checks 3 and 4b** (S6-8, S6-9, S6-16 item 6): the ring for round on
  round, as now; Table K5.1 at a rectangular branch on a rectangular
  chord; the branch's own outline at a mixed pair; base metal on the
  walls as now, the in-plane shear over the weld line's length. Check 4b
  runs in full at any joint with a rectangular member.
- **The round chord table** in Check 3 (S6-10): for each direction case
  the branch actions, the available strengths by plastification and,
  where it applies, punching, Qf, and the Eq. K4-5 interaction. The
  chord wall's ratio is the largest interaction over the cases.
- **Check 4b's chord line** (S6-11), for every pair.

### Output (PDF)

- The chord table prints after Check 3's weld lines: one row per limit
  state with its ratio and OK or NG; full calc lines for the governing
  limit state, and for any other over the 0.5 threshold (S6-1). The
  summary table gains the row "3 (chord wall)" (S6-16 item 1), at a
  round post on a round rail only.
- A rectangular or mixed joint keeps the line "rail wall, normal force:
  not checked", reworded for its pair.
- Printed wording beyond the rulings (line notes, the reworded
  assumptions of S6-14 item 10, S6-8 and S6-9, the S6-11 line, the
  orientation sentence) is Claude's to propose on the branch and Micah's
  to accept in the pull request.

## Intended changes to existing printed calcs

Every golden snapshot of both tiers stays byte-identical except for the
changes listed here. There are 47 snapshotted calcs today (cases 1 to 7
and the example in the first tier, 39 in the second) and 66 stop and
direct snapshots (65 in the second tier and case 3's); every one of the 47 calcs is a round post on a round
rail. Each change below is one commit, reported as "same change in N
files" with one example.

| No. | Change | Expected diff | Step |
| --- | --- | --- | --- |
| C1 | **One assumption sentence replaces W7's** (S6-16 item 4), in output.md's list and the front matter together. | 47 calcs: the line beginning "Local strength of the rail wall at the post, and of the post wall at the intermediate rail" becomes the S6-16 item 4 sentence. One line each. | 6 |
| C2 | **The round chord table in Check 3, and its summary row** (S6-10, S6-16 item 1). | 47 calcs: in Check 3 the line "Rail wall, normal force → Not checked" is replaced by the chord table and its calc lines; the summary table gains one row, "3 (chord wall)", after Check 3's. Check 3's own lines, ratio and summary row do not change. | 6 |
| C3 | **Check 4b's chord line** (S6-11). | The 15 calcs that print Check 4b in full: the line "Post wall, chord limit states → Not checked" becomes the S6-11 line. The calcs in the same-as-top observation state do not change. | 6 |
| C4 | **"Draft code values" rows.** The list follows the entries a calc reads, so its rows change in the commit of the change that causes them, and are counted in that commit's summary. | 47 calcs. Added: the Chapter K limit entries read in validation (with C8's stops); the chord equations, Ω values, Qf entries and the 0.5 threshold (with C2); the S6-11 entry (with C3, in 15 calcs). Removed: `ej.weld.rail_wall_normal` (with C2) and `ej.weld.post_wall_chord_intermediate` (with C3). A revised citation on an entry already listed changes that row. | 5, 6 |
| C5 | **The face-pair assumption sentence** (S6-7), added to output.md's list. | 47 calcs: one sentence added to "Stated assumptions". | 5 |
| C6 | **The weld-model assumptions reworded for rectangular and mixed pairs** (S6-14 item 10, S6-8, S6-9). | 47 calcs: the two sentences that begin "The rail to post weld is modeled as a flat ring" and "The intermediate rail to post weld is modeled as a flat ring". The words are proposed on the branch. | 5 |
| C7 | **The post D/t stop at Check 4b is removed** (S6-16 item 8). | `stop-chord-post` (.toml and .stop.txt) is deleted, with its row in stops.md and its test. A round post over D/t = 50 under a round rail now stops as a branch (S6-13), which gets its own new scenario. | 6 |
| C8 | **Stop messages.** | `stop-chord-rail`: the message loses "a stated assumption, not a check (W7)". `stop-tube-shape`: "rectangular tube" is now a shape, so the scenario moves to a shape that is not, and the message names both custom shapes. `direct-w7-rail`, `direct-w7-post`, `direct-w7-inter`, `direct-dir-increase-stop`: the stand-in family becomes a solid bar, and the message says slice 7. `stop-second-order`, `stop-tube-slender`: a new S6-13 stop is reached first (open item 6). | 5, 6 |

Not expected to change, and a stop if they do: any number, ratio,
verdict or controlling case in the 47 calcs; Check 3's and Check 7's
weld lines; the dimensions and section pages of a calc with no
rectangular member; `stop-B-small` and `stop-N-small` (a round post's
message keeps its words under the per-direction stop); the recorded
values of cases 1 to 7.

New snapshot files are expected and are not changes: cases 8 and 9 in
the first tier; second-tier calcs and stops for the rectangular
branches.

## Registry entries this slice will draft

About 85 to 110, well above the roadmap's 35 to 50. I am not sure of the
count: this registry stores each coefficient and each Ω as its own
entry, and §F7 and Chapter K are dense with them. Every entry is drafted
from the 360-22 text (out/aisc-360-22.pdf) with its section and page, or
from memory where the source is the Manual; none is marked verified.

- **Fy and Fu, rectangular HSS** (AISC Manual Table 2-4): A500 Gr B,
  A500 Gr C, A501 Gr A, A501 Gr B, A847, A1085 Gr A: 12 entries, from
  memory. A618 reuses slice 5's.
- **Classification:** Table B4.1a Case 6; Table B4.1b Cases 17 and 19
  (numbers confirmed when drafted); §B4.1b(d)'s 3·t rule: about 8.
- **§F7:** Eqs. F7-1, F7-2, F7-6, F7-8 to F7-11 with their
  coefficients, and the User Note to §F7.4: about 12.
- **§F1:** Eq. F1-1 and the cantilever's Cb = 1.0: 2 to 6.
- **Custom rectangular tube:** the corner radius conventions, the
  property formulas, the weight rule, the J formula (Commentary to §H3),
  the no-flat stop: about 10.
- **Check 7 on a rectangular post:** §J2.4(a) condition (2) and the User
  Note to §K5; the rounded-rectangle and face-pair line properties;
  §J4.1 yielding and rupture with their Ω; the face-pair engineering
  judgement and its assumption words: about 10.
- **§K5:** the provision, Eqs. K5-5 to K5-7, Eq. K1-1, the cap on Be,
  the case mapping, the equal-width User Note and its fillet-model
  judgement: about 9.
- **Mixed pairs and rectangular chords:** the weld model, the cope
  ignored, the chord wall not checked (two entries), the width rule: 4
  or 5.
- **Chapter K limits** (§K1.3, Tables K3.1A, K4.1A, K4.2A): B/t and H/t;
  Fy; Fy/Fu and the A500 Gr C note; Db/tb, 0.05·E/Fyb, the width ratio;
  the stop's engineering judgement: about 9.
- **The round chord check:** Eqs. K3-1, K3-2, K4-1 to K4-5 with their
  coefficients; the two Ω; Eq. K1-3, U and Fc; the punching condition;
  the Mro bound and the 0.5 threshold (engineering judgement); the S6-11
  line: about 22.
- **Printed text:** the orientation sentences; the base pattern echo;
  the reworded lines for rectangular and mixed joints: about 5.
- **Revised drafted entries:** `material.grades.hss_rect` (A1065 out,
  A618's names corrected, S6-5); `ej.weld.ring_model` (the §K5 note,
  S6-8); `ej.weld.chord_D_over_t_stop` and
  `aisc360.K.round_chord.D_over_t_max` (W7's words, the limit kept);
  `ej.weld.branch_kds`, `ej.weld.line_method` and `ej.weld.no_bearing`
  where a note names round sections only.

## Tests

- **Golden snapshots:** both tiers byte-identical through every step
  except C1 to C8.
- **Test cases 8 and 9**, and case 6's new group, each with a fresh
  independent calc (T1 to T3). [hand] values "deferred" to the release
  review.
- **Cases 1 to 7:** no input change, no new value outside case 6's new
  group, every existing value unchanged. A changed value is a rule 2
  stop.
- **The property-formula test** (T4), the **machinery tests** (T5) and
  the **extraction test** for the rectangular rows.

## Build order

Each step is committed and pushed when the full suite passes. Each of
the first three blocks (members, steps 1 to 4; welds, step 5; the chord
limit states, step 6) is a clean stopping point (S6-1).

**Snapshot rule for every step** (as slice 5's; Micah, 2026-10-09). A
step that changes printed text on purpose updates the golden snapshots
in a commit of its own, one commit per intended change, and that step's
report gives the diff as "same change in N files" with one example. A
snapshot difference that is not in the table above, or is larger than
its row says, is a stop: the snapshot is not regenerated until the cause
is known, the change is backed out, and it goes to Micah.

1. **Shapes data.** The rectangular HSS rows extracted to a derived
   file, with the row-for-row test; the section type's rectangular
   fields (H, B, b/t, h/t, J) and families; lookup by designation; the
   database finding of S6-14 item 9 in data/README.md. No printed calc
   changes.
2. **Members: registry and input.** The member entries drafted and the
   review list updated. `long_side`; the custom rectangular tube input;
   grades and defaults by shape; their stops, with stops.md. The joint
   tables still stop a rectangular member, so no project with one runs
   in full yet; the tests work at function level.
3. **Members: engineering.** The shared Cb function; §F7 with
   classification; Check 1 by §H1.1 and Check 2 by axis; Check 4a;
   Checks 5 and 6 on a rectangular post; the section page. Round calcs
   byte-identical.
4. **Custom rectangular tube properties** as calc lines, and the
   property-formula test (T4). The row report goes to Micah here; the
   work on custom tubes stops if a binding row comes out above
   published.
5. **Welds.** The weld entries drafted. Check 7 on a rectangular post
   (S6-6, S6-7); Checks 3 and 4b at rectangular and mixed joints (S6-8,
   S6-9); the joint tables opened; the width rule; the chord's own
   Chapter K limits for a rectangular chord and a mixed pair (S6-13);
   the baseplate stop per direction. Second-tier scenarios for the new
   branches. Then the intended changes, one commit each: C5, C6, and
   the parts of C8 and C4 that belong here.
6. **The chord limit states.** The round-on-round limits of S6-13 and
   the removal of the post D/t stop (C7, C8, C4); the round chord table
   and its summary row (C2); Check 4b's line (C3); the assumption
   sentence (C1). One commit each.
7. **Test cases.** Case 6's new group, pending; cases 8 and 9 wired
   with inputs and every value pending; the independent templates; the
   snapshots of cases 8 and 9.
8. **Independent calcs** for case 6's new group and for cases 8 and 9,
   each in a fresh session by the independent-calc skill, after Micah
   has answered open items 3 and 7. The build session has read src/, so
   it must not write any of them (rule 6).
9. **Micah's review** of the three independent calcs and the PDFs
   against the checklist. His recompute is deferred (#18).
10. **Version 0.6.0** in pyproject.toml, CHANGELOG, the calc-code-review
    skill, then the **pull request** to main.

At the close: #18 gains case 6's chord limit state, case 8 (Checks 1, 3
and 7) and case 9 (Checks 5 and 7), and the known gaps below; #28
closes, or stays open for open item 5; the registry review workbook for
the slice's drafted entries is produced; the roadmap and #16 are
updated; this plan is marked completed.

## Which cases need a fresh independent calc

Case 6 (the new group only), case 8 and case 9: one fresh session each.
Cases 1 to 5 and 7 change no input and no value.

## Known gaps for the release-review issue (#18)

Tested only by same-author tests unless a case reaches them first:

- A custom rectangular tube in a calc (S6-15): covered by the
  property-formula test against the Shapes Database.
- Eq. F7-6 (a noncompact web) and Eq. F7-9 (Lb > Lr): no guard section
  reaches either.
- LTB that governs: at guard spans Cb restores Mp, so Eq. F7-8 prints
  but never controls.
- A rectangular post with its long side perpendicular to the rail; a
  rail with its long side horizontal as the top rail.
- `base_pattern = "faces perpendicular to rail"`; a face pair on a
  non-square post.
- A round post on a rectangular rail (the other mixed pair).
- Table K5.1 below β = 0.85, and Be uncapped (open item 1).
- Each Chapter K limit as a stop; the A500 Gr C exception is reached by
  case 6.
- Punching in the round chord table (Db < D − 2t): case 6 is at equal
  diameters.
- The rectangular grades other than A500 Gr B.

## What Micah does

- Answer the seven open items; items 3 and 7 before the independent
  calcs run.
- During the build: read the property-formula report (T4), and rule if
  it stops.
- Review the three independent calcs and the PDFs of cases 6, 8 and 9
  against the checklist in docs/brief/verification.md.
- In the pull request: read the snapshot diffs C1 to C8, accept or
  reword the proposed printed text, and approve.
- At the release review: verify this slice's drafted entries; recompute
  case 6's governing chord limit state, case 8's Checks 1, 3 and 7 and
  case 9's Checks 5 and 7.

## Done when

- `uv run handrail calc` prints a full package for a guard of
  rectangular HSS, of custom rectangular tubes, and of round and
  rectangular members mixed, and for the unchanged example.
- All tests pass: cases 1 to 9 at 0.5%, with no pending value.
- The golden snapshots of the 47 existing calcs differ from main only by
  C1 to C8.
- Micah has reviewed the three independent calcs and the PDFs.

## Flags for later slices

- **Slice 7:** `long_side` for flat bar and `base_pattern` with sharp
  corners for a solid bar post (S6-2, S6-6); the shared Cb function
  (S6-4); S6-7's post wall question and S6-8's weld for a solid member;
  the solid bar cells of the joint tables.
- **Slice 8:** `long_side` and `base_pattern` as pickers in the form.
- **Release review:** the drafted count would be about 205 to 230 (121
  as of 2026-10-11 plus this slice's).
- **After v1:** a rectangular chord's limit states computed (S6-12
  records the full set); the continuity moment for Qf (#29).

## Not in slice 6

- Solid round bar, solid rectangular bar, flat bar (slice 7)
- A rectangular chord's limit states as a check; chord limit states at a
  mixed pair (S6-9, S6-12)
- A chord check at Check 4b (S6-11)
- An inclined guard load case for rectangular rails; a rectangular
  same-as-top observation for Check 4b (S6-14, not chosen)
- An entered corner radius (S6-3); A1065 (S6-5)
- `ruff format`; the input form; any new check
