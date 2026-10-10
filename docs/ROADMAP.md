# Roadmap: slices from v0.1.0 to v1

Status: **accepted by Micah, 2026-09-30.** Slice 2 is the post (option A
below). **Current status (2026-10-09):** slices 1–4 are done (v0.1.0 to
v0.4.0, the first complete all-pipe package); slice 5 is next, and its
plan starts with the open decisions on its milestone (regrouping slices
5–7, recompute for new section families). What the tool must do is set by the brief
(docs/BRIEF.md); if this roadmap disagrees with the brief, the brief wins.
Each slice gets its own plan in docs/plans/ before work starts. That plan
settles the slice's open questions, and it can reorder or split the slice.

## Summary

| Slice | Covers | Depends on | Size | New test cases | Issues |
| --- | --- | --- | --- | --- | --- |
| 1 (done, v0.1.0) | Checks 1–2, pipe top rail | — | L | 1 | — |
| 2 (done, v0.2.0) | Checks 5–6: the post (pipe) | 1 | M | 2 | — |
| 3 (done, v0.3.0) | Checks 3 and 7: both welds (pipe rail on pipe post) | 2 | M | 1 | — |
| 4 (done, v0.4.0) | Check 4 (intermediate rail, 4a member and 4b weld) and the anchor reaction sets | 2 (3 for a full package) | M | 1 | #4 (closed) |
| 5 | Round section family: round HSS, custom round tube, solid round bar | 4 | M | 2 | #3 |
| 6 | Rectangular tubes: rectangular HSS, custom rectangular tube | 5 | L | 2 | — |
| 7 | Solid rectangular bar | 6 | M | 1–2 | — |
| 8 | Input form and front-matter image | 7 | L | 0 | — |
| 9 | v1 release | 8 | S code, L review | 0 | — |
| After v1 | Display units, LRFD, slender sections, other mounts | v1 | — | — | #1 |

Sizes are relative to slice 1, which also had to build every layer, so a
later slice of the same size carries more engineering. A slice is marked by
three things: how much check code it adds, how many registry entries it
drafts (slice 1 drafted 35), and how many new test cases it needs.
These are rough guesses. Slice 2, the first check against them, drafted 31
registry entries against an estimate of 18–23 and needed the 2 test cases
planned. Slices 3 and 4 drafted 28 and 15 entries against estimates of
about 15 and 6–8, so the actuals have run 1.5–2 times the estimates. The
estimates for slices 5–9 below have not been revised; read them with that
overrun in mind.

A test case costs Micah less than it did in slice 1. Case 1 was a full
hand calc of every value. From slice 2 on, each test case is an
independent-calc case (docs/brief/verification.md): an agent writes the
full calc, and Micah reviews it and the PDF against the checklist. His
recompute of each new check's governing case (and, from slice 4, each new
reaction set; ADR 0007) waits for one release review in slice 9 (below).
His registry verification happens at each slice close, before the next
slice's build starts (ADR 0008), so Micah's time per slice is the
checklist review plus that slice's drafted entries.

After slice 4 the tool produces the full v1 package for one guard type:
all seven checks, the summary table and the reaction sets, for an all-pipe
guard. That milestone matters for two reasons. It is the first calc that
could stand in for a real hand calc (under the DRAFT stamp). And every
later slice widens that package to new sections, rather than adding
checks and new shapes at the same time.

## How the slices are ordered

Two rules set the order. First, each slice adds one new kind of
engineering to layers that already work (project file, dimension parser,
section data, registry, calc lines, envelope, PDF, test cases).
Second, it reaches a PDF Micah can backcheck before the next slice starts.
When the tool disagrees with a hand calc (rule 2), the question is which
side is wrong. With one new thing per slice, there are few places to look.
Slices 2–4 add members and connections while the section layer stays at
pipe. Slices 5–7 then widen the section layer while the set of checks
stays fixed. Every test case from earlier slices reruns in every later
slice. That rerun is the guard: generalizing a check to new shapes must
leave the old cases unchanged.

The cost of this order is a known refactor. Checks 3–7 will be written
against the pipe section type (`PipeSection` in `src/handrail/shapes.py`),
and slices 5–7 will generalize them. The code term for this is
"premature abstraction", and the choice is between it and a later
refactor. If the section interface is designed now, with only pipe to go
on, it is a guess at what rectangular HSS and bars will need, and a wrong
guess is harder to fix than no guess. Generalizing once the second shape
is actually in hand costs some rework, but the test cases catch any change
to an old result. I think the rework is the cheaper risk. Alternative B
below is the opposite bet.

The input form comes late on purpose. It shows every field in the project
file, and that set of fields will keep changing until the last section
family lands. A form built earlier would be rebuilt with each slice. Until
then Micah edits the TOML project file by hand, as he does now. ADR 0001
already keeps the calc engine independent of the form, so building the
form last changes nothing in the calc.

## Choosing slice 2

The question for slice 2 is which new kind of calc to add next. There are
four realistic answers.

**A. The post: Checks 5 and 6, on a pipe post (recommended).** This slice
adds post height h and baseplate thickness t_p. It adds the post's dead
load and passes the rail's dead load down into the post, which is the
first load path between two members. It covers compression per Chapter E
with the recommended design K for a cantilever, interaction per §H1.1,
tension yielding per §D2 for the upward case, and cantilever deflection
over h − t_p against L/60. The longitudinal case stops being "not checked"
and becomes a real case for the post. The post is usually the member that
governs a baseplate-mounted guard, through flexure at the base under the
concentrated load at 42 in. So this slice gets the most consequential check
backchecked early. Its outputs (shear, moment and axial at the base) are
also what Checks 3 and 7 and the reaction sets consume, so everything after
it builds on it. It stays on pipe, which means a mismatch against the hand
calc can come only from the new post engineering, not from a new section
type. The cost: it is the largest block of new engineering of any
alternative, about 15–20 registry entries, and it raised one question the
brief did not settle (second-order effects, since decided; see slice 2
below).

**B. Section families first: Checks 1–2 for rectangular HSS, bars and
custom sections.** This widens the section layer before more checks are
written against it, so Checks 3–7 would be generic from the first line and
the refactor above goes away. It also brings in the hardest section
engineering early: §F7 and §F11, LTB with Cb from the §F1 moment diagram,
biaxial bending per Chapter H for non-round sections, the axis-orientation
input, and properties computed from dimensions (corner radius, §B4.2 design
thickness). The cost: it adds no new check, and it designs the section
interface for Checks 3–7 before any of those checks exists, so the
interface is still a guess. It is the largest slice on this list (it merges
slices 5–7 below), and it delays the post, which is the check that governs.

**C. Welds first: Check 3, with Check 7 if the post geometry comes
along.** The weld method (elastic line method, §J2.4 directional increase,
base metal per §J4.2, fillet size limits) is the code interpretation I am
least sure of, especially how Chapter K limits the directional increase
for welds to HSS. Doing welds first brings that risk out early. The cost:
Check 7 needs the post's base moment and Check 3 needs the post perimeter,
so this slice either builds half of the post anyway or tests Check 3 alone,
without the member it attaches to. A would build that same post properly.

**D. Everything else for pipe at once: Checks 3–7 and the reactions in
one slice.** This reaches the complete all-pipe package fastest, measured
by calendar time. The cost: one very large PR, a single backcheck covering
five checks, and a hand calc that has to be complete before any of it can
be verified. Slice 1 worked because it was small enough to backcheck
line by line. D gives that up.

I left out a fifth option, building the input form next. It changes no
printed number, and its fields would churn through every later slice.

**Recommendation: A.** It gets the governing check to a backcheckable PDF
soonest. It adds the most new kinds of engineering while keeping the
section layer fixed. And slices 3 and 4 depend on its outputs. B is the
serious alternative, and it is the right choice if you would rather pay
for the section abstraction up front than for a refactor in slices 5–7.

**Decision: A** (Micah, 2026-09-30). The slices below follow from it.

## Slices

### Slice 2: the post (Checks 5 and 6), pipe (done, v0.2.0)

**Covers.** Inputs: post height h, baseplate thickness t_p, post section
(AISC pipe, A53 Gr B), and the post deflection limit (L/60, editable,
bypassable). Dead load of the post, with the top rail's dead load passed to
the post over the span as its tributary length. Check 5: axial and flexure
at the base, over the envelope. Downward puts live axial compression into
the post. Outward and inward put live moment L·(h − t_p) with dead-load axial.
Longitudinal is numerically equal to transverse for a round post but is
listed as its own case. Upward checks tension yielding (§D2) and is shown
even though it will not control. Compression per §E3 with the recommended
design K for a cantilever. Classification per Table B4.1a for round HSS in
compression, with slender as a hard stop. Flexure reuses §F8. Interaction
per Eq. H1-1a/H1-1b. Check 6: cantilever deflection over h − t_p, live
load only, horizontal cases. The dimensions, section properties, loading and
summary pages all grow to cover the post. Folds in issue #4.

**Depends on.** Slice 1 layers, as they are.

**Size.** M. About 18–23 new registry entries (Chapter E equations and
limits, Ωc, Ωt, K, the B4.1a round limit, the H1.1 equations and their
0.2 threshold, Table 3-23 cantilever cases, the L/60 limit as
engineering judgement, and the second-order entries below). Two test cases
(cases 2 and 3): a Pipe1-1/2STD post and a Pipe2STD post, one for each
Chapter E branch (E3-3 and E3-2), both on case 1's rail and span with
h = 42 in and t_p = 1/2 in.

**Decided: second-order effects** (Micah, 2026-09-30). The tool does not
implement Appendix 8 amplification. For the post it computes αPr/Pe and
prints one line: "Second-order effects negligible: αPr/Pe = [value];
amplification taken as 1.0." This covers the cases that have moment and
axial load together (outward, inward, longitudinal). If αPr/Pe exceeds 0.05
in any of them, the calc stops and names the ratio and the limit, in the same way as the
slender-section stop. The supporting provision (α for ASD and the Pe
expression, AISC 360-22 Appendix 8) is drafted into the registry on the
slice 2 branch. The 0.05 limit is its own entry, marked engineering
judgement (source "engineer"): 1/(1 − 0.05) = 1.053, so the amplification
neglected is at most about 5%. Pe is computed with KL = 2.1h, the same
effective length as the compression check. The post is a cantilever, so its
second-order effect is sway (P-Δ). Pe at K = 1 (the Appendix 8 B1 form)
would be about 4.4 times larger and would understate the ratio by that
factor.

**Plan.** docs/plans/slice-2.md, with every decision settled. It also covers
post self-weight (full weight at the base, over h − t_p), Cb (deferred to
the first LTB-susceptible section), and Lc/r above 200 (a visible flag, not
a stop).

### Slice 3: welds (Checks 3 and 7), pipe rail on pipe post (done, v0.3.0)

**Covers.** The weld method in welds.md, built once and used by both
checks. Weld inputs are fillet size and electrode (E70XX by default), with
the weld all around a round post. Check 3 takes the horizontal shear V plus
V·e, with the post perimeter as the weld length and the downward load
passing through the weld. Check 7 takes the base shear and moment, with
moment arm h − t_p. Both use the elastic line method, the §J2.4 directional
increase (where the registry says it applies), and the base metal check on
both connected parts, the lower governing. Minimum and maximum fillet sizes
are pass/fail lines. Adds the baseplate grade (A36 by default; Fy and Fu
per AISC Manual Table 2-5) and Fu for A53 Gr B.

**Depends on.** Slice 2 (post section, base forces, t_p).

**Size.** M. About 15 new registry entries (§J2.4 strength, the
directional-increase equation and its limits, the Chapter K restriction,
J2.2b and Table J2.4 size limits, §J4.2 rupture, Ω for each, FEXX, Fu for
two grades). One test case. (Actual: 28 entries.)

**Settled** (Micah, 2026-10-04 and 2026-10-08): the eccentricity, the
directional increase and the fusion face thickness, with nine further
decisions, W1–W12 in docs/brief/welds.md. **Plan:** docs/plans/slice-3.md,
with test case 4 (case 2's geometry plus welds).

### Slice 4: intermediate rail (Check 4) and anchor reaction sets (done, v0.4.0)

**Covers.** The optional intermediate rail, which defaults to the top rail
section. Check 4: the §4.5.1.2 component load, horizontal at midspan,
acting alone, with no dead load and nothing concurrent. It includes the
component-load deflection check (L/120 default, editable, bypassable) and
shows "none" when there is no intermediate rail. Most of it reuses the
Check 1 and 2 code. The intermediate rail's dead load is added to the post.
Baseplate plan dimensions B × N and the baseplate weight. The two
LRFD reaction sets (lateral, in any horizontal direction, and upward only
when there is net tension; S4-4 in loads-and-envelope.md), each
simultaneous, at the top of concrete, labeled as engineering-judgement
combinations, with the reversal note and B × N printed beside them. The
reaction tables go at the end of the PDF.

**Depends on.** Slice 2 (base forces). Slice 3 is needed for a complete
package, but not for this slice's code.

**Size.** S–M as planned; M as built, with the Check 4b scope addition.
About 6–8 new registry entries planned, 15 drafted (component load, 0.9D + 1.6L
as engineering judgement, the stated assumptions that newly apply). One test
case: the complete all-pipe guard, all seven checks and the
reactions. This case is the milestone.

**Settled** (Micah, 2026-10-08 and 2026-10-09): S4-1 to S4-12 in the
brief, including two additions to the scope above: a weld check for the
intermediate rail (Check 4b, S4-8) and a downward component load case
after OSHA (S4-10). The reaction sets are two, lateral and upward (S4-4).
About 10–12 registry entries. Micah's release recompute now covers the
reaction sets (ADR 0007). **Plan:** docs/plans/slice-4.md, with test
case 5.

### Slice 5: round section family

**Covers.** Round HSS from the database (extraction and row-for-row test
for HSS round rows), custom round tubes defined by dimensions (nominal or
design wall, §B4.2 conversion; weight on the wall as entered, strength on
design), and solid round bar (§F11 flexure; compression with no
local-buckling limit). Section properties computed from dimensions print as
calc lines. Grade lists and the unusual-pairing warning (A500 Gr B/C, A1085
with the "properties as published" note; bars A36). This is also where the
section type is generalized across Checks 1–7. Issue #3 lands here: a
custom thin-wall round tube, or a large round HSS, gives a realistic
noncompact case for Eq. F8-2.

**Depends on.** Slice 4 (all checks exist to be generalized). Its build
starts only after Micah has verified the top 20 entries of the
catch-up (ADR 0008, Notes; gate 1).

**Size.** M. About 12–15 new registry entries. Two test cases: the
noncompact rail (#3) and a solid round bar or custom tube post.

**To settle in the slice plan.** The base metal check for a weld to a
solid bar post: welds.md specifies it over "the thickness on the fusion
face", and a solid bar has no wall.
Also whether the stated assumption that the rail wall's Chapter K chord
limit states are not checked (welds.md, W7) still holds for a thin-wall
custom round rail, or whether Check 3 needs that limit state. Check 3
stops on any rail or post that is not round hollow until this is
decided. A rail welded to the side of a post wider than it, or a
cap-plate detail, is a different connection and is out of v1; the tool
stops when the post is wider than the rail (welds.md, W8). Slices 5 and
6 keep that stop as section families widen, and slice 6 decides which
dimensions it compares for rectangular sections. The weld envelope's
orthogonal-cases ruling and the load-at-the-rail-centerline ruling
(welds.md) are revisited for rectangular rails in slice 6; confirm here
that both still hold for every round rail this slice adds.
Check 4b now checks base metal on both walls, the post and the
intermediate rail (welds.md, Micah 2026-10-09): settle what that line
becomes for a solid bar intermediate rail, which has no wall, with the
solid bar post question above. (The slice 4 plan's flag on the
"branch-wall argument" is moot: that argument was removed with the
simple shear connection.) Whether solid round bar stays in this slice
is open on the Slice 5 milestone (regrouping slices 5–7).

### Slice 6: rectangular tubes

**Covers.** Rectangular HSS from the database and custom rectangular tubes
(AISC corner-radius convention, §B4.2 design thickness). Table B4.1a/B4.1b
limits for rectangular HSS walls, flexure per §F7, and the input for which
axis resists the horizontal guard load, for the top rail and for the
intermediate rail (S4-10: Check 4a's horizontal and downward component
load cases then bend different axes, and the horizontal case can govern
on the weak axis). Biaxial bending per Chapter H for
non-round sections, replacing SRSS for these shapes. The longitudinal case
on the post's other axis. Rectangular post welds: all around, or on one
pair of faces picked by width or depth, with the elastic line properties of
each pattern.

**Depends on.** Slice 5 (the generic section interface). Its build starts
only after Micah has verified every other entry drafted by 2026-10-09
and slice 5's own drafted entries (ADR 0008; gate 2).

**Size.** L, the largest after slice 1. About 20 new registry entries.
Two test cases: a rectangular HSS post where longitudinal governs on the
weak axis, and a rectangular rail.

**To settle in the slice plan.** The rail wall's Chapter K limit states
for a rectangular rail at β = 1, where the sidewall limit states can
govern (welds.md, W7): checked, or a stated assumption with its reason.
Also whether the five orthogonal direction cases still cover the welds
for a rectangular rail. For pipe on pipe an inclined guard load raises
Check 3 by under 10% on a ratio far below 1.0 (demand V·e, e = D_rail/2),
and Check 7 negligibly, so no inclined case is checked (welds.md, the
weld envelope; Micah 2026-10-08). A rectangular rail changes e and the
ring's line properties, so that argument has to be redone. The same goes
for the ruling that guard loads act through the rail centerline: torsion
on the Check 3 weld and the larger eccentricity from a load at the rail's
surface are neglected because Check 3 ratios are far below 1.0 for pipe
on pipe (welds.md, Check 3 weld model; Micah 2026-10-08). Redo that for a
rectangular rail, whose depth and weld pattern differ.

### Slice 7: solid rectangular bar

**Covers.** Flat and rectangular bar, always defined by dimensions: §F11
(yielding and LTB) with Cb from the §F1 moment diagram for each load case
(simple span for the rail, cantilever for the post). This is the first
section where LTB can govern. Includes a flat bar rail loaded about its
weak axis, the case the brief names where a horizontal case may control,
and a flat bar intermediate rail: Check 4a's two component load cases
(horizontal, downward; S4-10) on different axes, with Cb for the
midspan point load. Check 4b's weld ring (S4-8, S4-9) and the cope limit
(S4-11) are round-only until slices 6 and 7 extend them.

**Depends on.** Slice 6 (rectangular axis input, biaxial H provisions,
face-pair welds).

**Size.** M. About 8–10 new registry entries. One or two test cases (a
flat bar rail on its weak axis; a bar post where LTB matters).

It would be reasonable to merge this into slice 6. I've kept it separate so
the one slice that brings in LTB carries nothing else new.

### Slice 8: input form and front-matter image

**Covers.** The browser form per ADR 0001, covering every input in
inputs.md. The normalized dimension shows in gray next to each box. The
exemption checkbox opens its statement box, with an info box drawn from
registry text. Grade warnings. The form writes and reopens the TOML project
file, and reopening regenerates the calc exactly. Image upload for the
front-matter image area.

Also a key sketch, on the input page and in the PDF front matter: a
static PNG that Micah draws, labeled with symbols only (L, h, t_p, B, N,
the member names: top rail, intermediate rail, post, baseplate; and the
weld locations), not to scale and not generated from the inputs. It
shows B parallel and N perpendicular to the rail (S4-6). Placing it is
the whole feature and does not change this slice's size. (Micah,
2026-10-08.) output.md takes the binding text in the slice 8 plan.

**Depends on.** Slice 7, since the input set is only stable once every
section family is in.

**Size.** L in software, zero in engineering: a local web server and form
are a new layer for this codebase. No new test cases. Every existing case
must still pass from a project file that the form saved.

### Slice 9: v1 release

**Covers.** First, a layout pass on the printed package: citation
density and package length, issue #13 questions 5–10, deferred here by
Micah on 2026-10-04. It goes before the release review because that
review recomputes from the printed calc. Then the release review, tracked
as a checklist in issue #18
(label `release-blocker`): the release can't ship while any box is open.
First the registry residual: Micah verifies whatever is still drafted,
which after ADR 0008 is only entries drafted or revised since the last
slice close, so the DRAFT stamp disappears from a normal calc. Then Micah's governing-case recompute of every deferred test case
(cases 2 and 3 so far, and each later slice's cases): he recomputes the
printed controlling case line by line, and each new reaction set, and
replaces each "deferred" [hand] value with his own (ADRs 0006, 0007). Afterwards the full test suite reruns. Any
test case value that depended on a corrected entry is redone from the
corrected entry, independent-calc values by a fresh independent calc and
Micah's values by Micah, never by editing them to the tool's new output
(docs/brief/verification.md, "The release review"). Removing the "DEVELOPMENT —
NOT FOR CONSTRUCTION" watermark, which is Micah's call and his alone. A
whole-tool calc-code review. Stated assumptions and the brief rechecked
against what shipped. CHANGELOG v1.0.0.

**Depends on.** Everything above.

**Size.** Little code, but most of the time is Micah's. The registry
held 109 entries after slice 4 (77 drafted); at the overrun seen so far it
would reach roughly 140–165 entries by this slice. Under ADR 0008 those are
verified at each slice close, so the release review carries only the
residual plus a recompute of each deferred test case (25 deferred [hand]
values in cases 2–5 as of v0.4.0). The architecture review of 2026-10-09
estimated 20–35 hours of Micah's time with all registry verification at
the end, plus any independent calcs redone after a correction; the registry
share of that (8–13 hours) moves to the slice closes, and I'm not sure the
total falls.

## Registry verification at slice close

Decided (Micah, 2026-10-09; ADR 0008), replacing the release-review decision
below: each slice's drafted entries are verified when the slice closes,
before the next slice's build starts, and the 77 entries drafted by then are
caught up in batches, highest fan-out first, under two gates (Micah,
2026-10-09): the 20 entries named in ADR 0008's notes before slice 5's
build starts, and every other entry drafted by 2026-10-09 (57) before
slice 6's build starts. Slice 5's own entries are due before slice 6's build
too. Micah records his verdicts in the registry review workbook; an agent
applies them to the registry on a branch with a pull request
(docs/brief/verification.md, "Applying the verdicts"). The governing-case
recompute stays at slice 9. The rest of this section records the 2026-10-03 decision
it replaced.

### Registry verification at release (replaced)

Decided (Micah, 2026-10-03), replacing the 2026-09-30 decision to verify
each slice's entries within the slice. No slice's "done when" includes
registry verification. Every drafted entry is verified in one review in
slice 9. Entries already verified (32 as of 2026-10-03) stay verified.

The cost of this choice:

- A wrong drafted entry stays in every calc, under the DRAFT stamp,
  until slice 9.
- The independent calcs in slices 2–8 work each drafted value from their
  own reading of the code. A misreading they share with the tool's
  drafted entry passes the test until the review finds it.
- A correction at the review means redoing the affected test case
  values.

Why: Micah will not use the tool on real work until v1 is complete, so
verifying slice by slice protects no real calc before release. One
review is also more efficient once the set of entries has stopped
changing (ADR 0005).

On 2026-10-04 Micah's governing-case recompute moved to the same review,
for the same reason (ADR 0006): from slice 2 on, each test case's [hand]
values are marked "deferred" until slice 9, and within a slice his
checklist review is the only defence against a misreading the tool and
the independent calc share. The verification process is frozen until v1
unless a real problem forces a change (ADR 0006).

## Where the open issues go

Every open issue sits in exactly one GitHub milestone: Slice 5 to Slice 8,
"Slice 9 (v1 release)", or "After v1" (which replaces the old `future`
label). The milestones page is the placement list:
https://github.com/mensingmicah/handrail-designer/milestones. The pinned
"Slice status" issue (#16) has no milestone. Issues that need Micah's
ruling carry the `needs-decision` label and are assigned to him.

## After v1

These come from scope.md's future versions, not from any slice above:
display units (#1), LRFD member checks, slender-section checks, and mounts
the tool checks itself (steel baseplate and anchor to steel, wood,
cold-formed steel), with ACI 318-19, AISI S100 and NDS added as they come.
Baseplate thickness and bending checks are also after v1: in v1 they are
not checked, a stated assumption (slice 2, D12), and the baseplate is
designed by others. Baseplate grades beyond A36 come with those checks;
until then the baseplate grade input accepts A36 only (inputs.md,
slice 3).
End posts, overhangs, sloped runs and infill stay out until the brief says
otherwise.

The single lateral reaction set (S4-4, loads-and-envelope.md) rests on
transverse and longitudinal giving identical reactions in v1. Revisit it
if the longitudinal load is ever modeled differently, for example a
multi-span frame with moment-connected posts. (Micah, 2026-10-08.)

A sketch drawn from the inputs (to the project's dimensions and
sections) is an after-v1 idea; v1 has the static key sketch (slice 8).
(Micah, 2026-10-08.)

An OSHA toggle that sets the component load to OSHA 1910.29(b)(5)'s
150 lb is after v1. In v1 the default stays 50 lb (ASCE 7-22) and the
input info box tells the engineer to enter 150 lb where OSHA applies
(S4-10, checks.md). (Micah, 2026-10-09.)
