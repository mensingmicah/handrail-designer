# Slice 4 plan: the intermediate rail (Check 4) and the anchor reaction sets

Status: **planned** (Micah, 2026-10-09). Not started; no branch yet.

> This plan is a record of what slice 4 sets out to build and why. The
> binding engineering decisions (S4-1 to S4-12) were recorded in the brief
> as they were made, during the planning interview of 2026-10-08 and
> 2026-10-09: docs/brief/checks.md ("The intermediate rail (Check 4)"),
> docs/brief/welds.md ("Intermediate rail weld to post (Check 4b)"),
> docs/brief/loads-and-envelope.md (base reactions), docs/brief/inputs.md
> and docs/brief/output.md. The verification change is ADR 0007. Where
> this plan differs from docs/BRIEF.md, CLAUDE.md or a later plan, those
> govern. T1 to T3 below are test decisions, not tool behavior, and stay
> here.

## Goal

Add Check 4 for the intermediate rail, in two parts: 4a, the member
(component load bending and deflection), and 4b, its weld to the post.
Add the baseplate's plan dimensions B × N and the two LRFD anchor
reaction sets. After this slice the tool prints the full v1 package for
an all-pipe guard: all seven checks, the summary table and the reaction
tables. It is the first calc that could stand in for a real hand calc,
under the DRAFT stamp. The section layer stays at pipe. Checks 1, 2, 3,
5, 6 and 7 are unchanged for a guard with no intermediate rail, and test
cases 1–4 must pass exactly as they do today.

## Decisions settled for this slice

> **Revision, 2026-10-09 (Micah, PR #20 review):** Check 4b is a simple
> shear connection, consistent with Check 4a's simple-span member: the
> reaction R acts at the weld, e = 0, no end moment. This supersedes the
> e = D_post/2 and M = R·e of S4-9, the branch-wall argument and the
> L ≥ 2·D_post stop of S4-12, and every later mention of them in this plan
> (the Engineering, Input, T3 and figures sections). docs/brief/welds.md
> holds the decision.

S4-1 to S4-12 are in the brief, with Micah's name and date on each. In
short:

| No. | Decision | Brief |
| --- | --- | --- |
| S4-1 | Intermediate rail input, three states: same as the top rail (`same_as_top_rail`, default checked), its own section (grade defaults to the top rail's), or none (`none = true`). No height input. Replaces "computed every time". | checks.md, inputs.md |
| S4-2 | Same as top: Check 4a prints "Controlled by Checks 1 and 2 by observation…", summary row with no ratio and no OK/NG of its own; no separate deflection input (follows Check 2, bypass included); one guard, P_c > P runs the full check. Own section: `[deflection.intermediate_rail]`, default L/120, bypassable, citing `ej.deflection.limit`. | checks.md |
| S4-3 | Component load for Check 4a: a point load at midspan, M = P_c·L/4, Δ = P_c·L³/(48EI); the 1 ft² area not modeled. `[loads] component_lb`, default from the registry; the exemption does not affect it. | checks.md |
| S4-4 | Two reaction sets: lateral (the horizontal guard load in any horizontal direction; transverse and longitudinal give identical reactions in v1) and upward (only when 1.6L > 0.9D). Replaces the three sets. | loads-and-envelope.md |
| S4-5 | Each set uses the larger of P and w·s at the top of the post and names it; exemption on, P only; a tie gives one set naming both. | loads-and-envelope.md |
| S4-6 | B parallel to the rail, N perpendicular; required, no default; stop if ≤ 0 or smaller than the post OD. W_bp = ρ·B·N·t_p in the reaction sets' D only. | inputs.md, loads-and-envelope.md |
| S4-7 | Reaction tables: V, N, M at 4 significant figures; N signed, tension positive, with the word; the convention note under each table; "V and M act in the same vertical plane; M = V·h"; combination label, governing load type, D breakdown and total. | output.md |
| S4-8 | Check 4b, the intermediate rail weld to the post, treated like Check 3 (a deliberate scope addition). Same as top: "controlled by Check 3 by observation", guard R > P. Own section: a required weld size; the Check 3 method on the intermediate rail's ring, k_ds = 1.0, base metal, minimum size. | welds.md |
| S4-9 | Check 4b load: P_c adjacent to the post (full P_c to that end), R_D = w_D,int·L/2, ASD D + L; horizontal R = √(P_c² + R_D²), downward R = R_D + P_c; ~~e = D_post/2, M = R·e~~ **revised 2026-10-09 (Micah): a simple shear connection, e = 0, no end moment**; no torsion. | welds.md |
| S4-10 | The component load runs horizontal and downward (downward is engineering judgement, after OSHA 1910.29(b)(5)). 4a downward adds the intermediate rail's dead load, ASD D + L; deflection as Check 2 combines it (horizontal L only, downward D + L). Default stays 50 lb; the info box tells the engineer to enter 150 lb where OSHA applies. | checks.md |
| S4-11 | Validation stop when D_int > D_post (the cope), both states; equal ODs allowed, fillet model kept; a printed assumption for the joint. | welds.md |
| S4-12 | Check 4b base metal with branch and chord reversed: post wall shear rupture (W6); chord-wall normal force not checked (W7 assumption extended); branch wall "covered by Check 4a" (own section) or "by Checks 1 and 2" (same as top); Fu/Fy ≥ 1.20 guard on the intermediate grade; stop if L < 2·D_post. **Revised 2026-10-09 (Micah): the branch wall is "shear only, member shear not checked"; the L ≥ 2·D_post stop is removed; the chord-wall line names no R·e normal force.** | welds.md |
| ADR 0007 | Micah's release-review recompute covers each new reaction set (V, N, M) as well as each new check. | verification.md |

Three decisions were Claude's, confirmed by Micah on 2026-10-09:

- **Conflicting inputs stop the calc**, never silently ignored: `none =
  true` with a section, a grade or an intermediate weld size; a section,
  grade or intermediate weld size given while `same_as_top_rail` is true;
  `same_as_top_rail = false` with no section.
- **One shared per-direction demand function** (issue #4, item 1). It takes
  the load combination as data (its D and L factors and its printed
  label) and the moment arm as an input, and returns P, V and M for each
  direction case. Checks 5 and 7 call it with the ASD combinations and
  h − t_p (the top of the baseplate); the reaction sets call it with
  0.9D + 1.6L and h (the top of concrete). The arm used prints in each
  calc, as Checks 5 and 7 print it today.
- **About 10–12 new registry entries** (below), against the roadmap's 6–8.

### Where the intermediate rail's dead load goes

Stated explicitly, because it is the one new load path in this slice (Micah,
2026-10-09). The intermediate rail's dead load over the span,
w_D,int·L, is added to D at the post. It reaches:

- **Check 5** (post axial load, every case) and **Check 7** (the axial
  term at the base weld), through D at the post;
- **the reaction sets**, through their D (with the top rail, the post and
  the baseplate);
- **Check 4a's downward case and Check 4b**, as the intermediate rail's own
  dead load (S4-9, S4-10).

It does **not** reach Check 3: Check 3's D is the top rail's dead load,
w_D,rail·L, carried through the rail to post weld. The intermediate rail
frames into the side of the post below that weld. Nor does it reach Check
6 (live load only). The state is "none" for cases 1–4, so none of their
values moves.

### Test decisions

**T1. Test case 5, the milestone.** A fresh guard that passes every check,
with one full independent calc of all seven checks (4a and 4b included)
and both reaction sets. Not an extension of case 4: this is the first case
where the intermediate rail's dead load flows into Checks 5 and 7 and the
baseplate weight into the reactions, and only a calc that runs the whole
guard top to bottom catches an integration error there; case 4 also fails
Check 5. (Micah, 2026-10-08.)

- Pipe2STD top rail and post, A53 Gr B; L = 6'-0", h = 42 in, t_p = 1/2 in;
  B = 6 in (parallel to rail) × N = 8 in (perpendicular to rail).
- Intermediate rail: its own section, Pipe1-1/4STD (OD 1.660 in ≤ post OD
  2.375 in), grade defaulted (A53 Gr B), so the full Checks 4a and 4b run.
- Welds: rail to post 1/8 in, post to baseplate 1/4 in, intermediate rail
  to post 1/8 in; E70XX; A36 baseplate.
- Default loads (P = 200 lb, w = 50 plf, P_c = 50 lb), no exemption;
  default deflection limits.
- Micah's [hand] values, deferred to the release review (ADRs 0006,
  0007): the governing ratio and controlling case of Check 4a (bending and
  deflection) and Check 4b; the lateral and upward reaction sets, V, N
  and M each. Already on #18.

Rough figures for case 5, from planning arithmetic (Claude, not test
values; rule 5). D at the post = 21.96 (top rail, 3.66 plf × 6 ft) +
13.62 (intermediate, 2.27 × 6) + 12.66 (post, 3.66 × 41.5/12) = 48.2 lb.
The distributed load governs the post and the reactions: w·L = 300 lb >
P = 200 lb.

- Check 1: P governs, downward, M ≈ 3,600 + 198 = 3,800 lb-in against
  Ma = 35·0.713/1.67 = 14.94 kip-in, about 0.25.
- Check 3: about 0.05. Check 7: M = 300 × 41.5 = 12,450 lb-in, S_w = 4.430
  in², f ≈ 2.82 kip/in against 5.57 kip/in (k_ds = 1.5), about 0.51.
- Check 5: Lc/r = 2.1·42/0.791 = 111.5, Fcr ≈ 18.5 ksi, Pr/Pc ≈ 0.004,
  H1-1b ≈ 0.002 + 12.45/14.94 ≈ 0.84. Check 6: Δ ≈ 0.393 in against
  41.5/60 = 0.692 in, about 0.57.
- Check 4a, downward governs: M = 900 + 123 = 1,023 lb-in against Ma =
  35·0.305/1.67 = 6.39 kip-in, about 0.16; Δ ≈ 0.073 + 0.012 = 0.085 in
  against 72/120 = 0.60 in, about 0.14.
- Check 4b, downward governs: R = 6.8 + 50 = 56.8 lb, M = 56.8 × 1.1875 =
  67.5 lb-in, S_w = π(1.660)²/4 = 2.164 in², f_r ≈ 33 lb/in against 1.86
  kip/in, about 0.02. The 1/8 in weld sits at the Table J2.4 minimum
  (thinner part, t_nom = 0.140 in).
- Reactions: W_bp = (490/1728)·6·8·0.5 = 6.8 lb; ΣD = 55.0 lb. Lateral
  (distributed): V = 1.6 × 300 = 480 lb, N = −0.9 × 55.0 = −49.5 lb
  (compression), M = 480 × 42 = 20,160 lb-in. Upward (distributed):
  N = 480 − 49.5 = +430.5 lb (tension), V = 0, M = 0.

Branches case 5 reaches: Check 4a and 4b in full, the downward case
governing each; the upward reaction set present; the distributed load
type named in both sets; a weld at the minimum size in Check 4b.

**T2. Cases 1–4 and the example.** Cases 1–4 gain `none = true` (S4-1)
and B × N as input-only additions; they record no Check 4 or reaction
values, and every existing value stays as it is. A changed value is a
rule 2 stop. The example (examples/slice-1.toml, Pipe2STD rail and post)
takes the default same-as-top state, so its PDF shows both observation
lines, and gains B × N.

**T3. Machinery tests** (same-author, like F8-2 in slice 1), for the
branches case 5 does not reach:

- Same as top: Check 4a's and 4b's observation lines print both values;
  the summary rows read "Controlled by Checks 1 and 2" and "Controlled by
  Check 3" with no ratio; with Check 2 bypassed, 4a's deflection reads
  bypassed.
- The guards: P_c > P runs the full Check 4a; R > P runs the full Check 4b.
- None: Check 4a and 4b print "none"; no intermediate dead load anywhere.
- **The component load at 150 lb (OSHA)**, own-section state, so the
  downward branch of Checks 4a and 4b runs at the industrial value
  (Micah, 2026-10-09). (In the same-as-top state 150 ≤ 200 lb, so the
  observation lines would print instead.)
- Every validation stop: each conflicting-input combination; D_int >
  D_post; L < 2·D_post; B or N ≤ 0 or smaller than the post OD; the
  Fu/Fy ≥ 1.20 guard on the intermediate grade (stand-in grade); a
  non-round intermediate rail (stand-in section).
- Reactions: no net uplift (no upward set, with the status printed);
  P = w·s (one set naming both types); exemption on (P only).
- **The moment arm** (Micah, 2026-10-09): the shared demand function
  returns the lateral reaction set's M with h and Check 5's with h − t_p,
  for the same load; the test asserts both.
- The dead load path: an intermediate rail adds w_D,int·L to D in Checks
  5 and 7 and the reactions, and leaves Check 3's D unchanged.

## What the slice does

### Input

The project file gains (bare numbers are inches):

- `[intermediate_rail]`: `same_as_top_rail` (default true), `none`
  (default false), `section` and `grade` (own-section state only; grade
  defaults to the top rail's).
- `[welds]`: `intermediate_rail_to_post`, a required dimension in the
  own-section state, an input error in the other two.
- `[baseplate]`: `B` and `N`, required dimensions.
- `[loads]`: `component_lb`, default from the registry.
- `[deflection.intermediate_rail]`: `limit_L_over` (default 120) and
  `bypass`, own-section state only.
- Validation (`validate()`): the conflicting-input stops; S4-6 (B, N);
  S4-11 (D_int ≤ D_post); S4-12 (L ≥ 2·D_post; the Fu/Fy guard on the
  intermediate grade); W7's non-round stop extended to the intermediate
  rail. Each stop names what it checked and why.

The dimensions page echoes B, N (with their orientation) and the
intermediate weld size, as entered and normalized.

### Engineering

- **Check 4a** reuses the Check 1 and 2 code on the intermediate rail
  section: classification, §F8, the slender and D/t stops; the point load
  at midspan (S4-3); horizontal (P_c alone) and downward (D + L) cases
  (S4-10); deflection under each, combined as Check 2 does. For a round
  section the downward case always governs; the horizontal case is listed
  so the envelope is explicit.
- **Check 4b** reuses the weld ring code (welds.py) on a ring of the
  intermediate rail's perimeter, D = D_int, with the roles of Check 3
  reversed (S4-12): R in the ring's plane gives f_v = R/(πD_int), M = R·e
  with e = D_post/2 gives f_b = R·e/S_w, combined at the governing point;
  k_ds = 1.0; weld metal; post wall shear rupture over t_des,post;
  the branch wall covered by the member check (printed line); minimum
  size on the thinner part's t_nom; the §J2.2b(b) not-applicable line.
  The ring function takes the member whose perimeter it is, instead of
  always the post.
- **D at the post** gains w_D,int·L (above).
- **Reaction sets** from the shared demand function: 0.9D + 1.6L, arm h,
  the larger load type, D including W_bp. Lateral: V, N (compression),
  M = V·h. Upward when 1.6L > 0.9D: N (tension), V = 0, M = 0.

### Output (PDF)

- Check 4 pages between Checks 3 and 5: Check 4a (member) and 4b (weld),
  each with its envelope table and the full calc for the controlling
  case, or its observation line, or "none".
- Summary table: separate rows for 4a and 4b.
- Reaction tables at the end, after the summary table (S4-7), with B × N
  and its orientation beside them.
- Stated assumptions (output.md, changed on the branch in the commit
  that prints them, since a test holds the printed list to output.md word
  for word):
  - "The intermediate rail's connection to the post, and the component
    load's effect on the post, are not checked." becomes "The component
    load's effect on the post is not checked." (S4-8)
  - The W7 assumption is extended to the post wall at the intermediate
    rail (S4-12).
  - New: the intermediate rail to post weld ring model, with the
    flare-bevel note (S4-11).
- The input info text for the component load (the OSHA note, S4-10) is a
  registry entry; until the slice 8 form, the example project file's
  comment carries it.

Layout details (column order, line wording beyond the decisions) are
Claude's to propose on the branch and Micah's to accept in the PR review.

## Registry entries this slice will draft

About 10–12. Citations from memory, to be verified at the release review
(#18):

- ASCE 7-22 §4.5.1.2: the component load, 50 lb; its area (not to exceed
  1 ft²) and that it is not superimposed with the §4.5.1.1 loads
  (provision text)
- OSHA 29 CFR 1910.29(b)(5): 150 lb, any downward or outward direction
  (provision text for the info box; source the web or memory)
- Engineering judgement (source "engineer"): the downward component load
  case after OSHA (S4-10); the point load at midspan (S4-3); 0.9D + 1.6L
  for the reaction sets, and its 0.9 and 1.6 factors; reactions at the
  top of concrete with arm h, one lateral set in any horizontal direction
  (S4-4); the Check 4b ring model, eccentricity and load position (S4-9);
  the branch wall covered by the member check when L ≥ 2·D_post (S4-12)
- Note edits only, so verified entries stay verified: `ej.deflection.limit`
  (names the intermediate rail), `ej.combo.deflection.D_plus_L` and
  `ej.combo.deflection.L_only` (Check 4a); drafted entries whose notes
  broaden: `ej.weld.branch_kds`, `ej.weld.rail_wall_normal`,
  `ej.weld.post_wall.fu_fy_min`, `material.steel.density` (baseplate
  weight)

## Tests

- **Test case 5** (independent-calc case, T1): every value the tool prints
  for all seven checks and both reaction sets. Micah's [hand] values are
  "deferred" to the release review (ADRs 0006, 0007).
- **Cases 1–4** (T2): inputs added, no new values recorded, every existing
  value unchanged.
- **Machinery tests** (T3).

## Build order

Each step is committed and pushed when its tests pass.

1. **Issue #4 "do first"**, with no change to any printed number or calc
   text:
   - one per-direction demand function shared by post.py and welds.py,
     taking the load combination as data and the moment arm as an input
     (above), replacing `post._downward`, `_moment_case`, `_upward` and
     `welds._weld_case`'s own demand code;
   - rename `post._live_at_post` to `live_at_post`;
   - the #4 small items: `welds.Ring.D` unused; `_weld_values` finding the
     minimum-size line by its `"w ="` prefix; `checks.validate()` not
     confirming the rail grade has an `FU_ENTRY`.

   Confirmed unchanged two ways: all tests pass unchanged, and the Typst
   source of the example and of cases 1–4, generated on main before the
   step and on the branch after it, is identical apart from the footer's
   commit hashes.
2. **Project file:** the new inputs and validation; cases 1–4 and the
   example updated (T2); the validation machinery tests.
3. **Registry entries** drafted; review list updated.
4. **D at the post** gains the intermediate rail; the dead-load path test.
5. **Check 4a.**
6. **Check 4b** (the ring generalized to the member whose perimeter it is).
7. **Reaction sets**, from the shared demand function; the moment arm test.
8. **Report:** the assumptions into output.md and the front matter, the
   dimensions page, the Check 4 pages, summary rows, the reaction tables.
9. **Test case 5** wired in, values pending; independent template created.
10. **Independent calc for case 5,** in a fresh session by the
    independent-calc skill. This planning session has read src/, so it
    must not write it (rule 6).
11. **Micah's review** of the independent calc and the PDF against the
    checklist. His recompute is deferred (#18).
12. **Pull request** to main, with the calc-code-review skill run first.

## What Micah does

- Review the case 5 independent calc and the slice PDF against the
  checklist in docs/brief/verification.md, and approve the pull request.
  It is the first full package: worth reading as he would a junior
  engineer's complete calc.
- At the release review: verify this slice's drafted entries; recompute
  case 5's Checks 4a and 4b and its lateral and upward reaction sets.

## Done when

- `uv run handrail calc examples/slice-1.toml` prints all seven checks
  (Check 4 as its observation lines), the summary table and the reaction
  tables.
- All tests pass, cases 1–5 at 0.5%, with no pending value in case 5.
- Micah has reviewed the case 5 independent calc and the PDF.

## Flags for later slices

- **Slice 5:** the D_int ≤ D_post stop (S4-11) and the branch-wall
  argument (S4-12) must hold for every round family it adds; a solid bar
  intermediate rail has no wall, the same question slice 5 already has
  for a solid bar post.
- **Slice 6:** the shared demand function needs two moment axes for
  biaxial bending on rectangular posts; Check 4b's ring needs a
  rectangular pattern; the axis input covers the intermediate rail
  (roadmap). One lateral reaction set still holds: V, M and D at the base
  do not depend on which post axis takes the load.
- **Slice 7:** a flat bar intermediate rail, with Check 4a's two cases on
  different axes and Cb for the midspan point load (roadmap).
- **After v1:** the OSHA toggle; revisiting the single lateral set if the
  longitudinal load is modeled differently; an input-driven sketch
  (roadmap).

## Not in slice 4

- The component load's effect on the post (a stated assumption)
- The post wall's Chapter K chord limit states at the intermediate rail
  (S4-12), and the rail wall's (W7)
- An intermediate rail wider than the post, or any detail other than the
  coped end welded all around (S4-11)
- Baseplate thickness and bending (D12); anchorage
- Service-level reactions; a downward reaction set
- The OSHA toggle; non-round sections
