# Slice 2 plan: the post (Checks 5 and 6), AISC pipe

Status: **in progress on the `slice-2` branch.** Every decision below was
settled by Micah on 2026-09-30 (docs/ROADMAP.md, "Choosing slice 2"; slice
2 planning). The verification steps were revised the same day for the new
verification model (issue #13, ADR 0004): slice 2 is its first user, and
its pull request waits for the harness change. Registry verification
moved out of the slice on 2026-10-03: Micah verifies every drafted entry
in one review in the v1 release slice (docs/ROADMAP.md, slice 9), so this
slice's entries stay drafted and its PDFs print the DRAFT stamp.
Where this plan differs from the brief (docs/BRIEF.md) or CLAUDE.md, those
govern, and the difference is a defect in the plan.

## Goal

Add the post to the calc: Check 5 (combined axial and flexure, cantilever)
and Check 6 (cantilever deflection) for an AISC pipe post in A53 Gr B, run
over the full envelope, printed in a PDF Micah can backcheck by hand. This
slice adds the first load path between two members: the top rail's dead
load, and the guard loads it collects, go into the post. The section layer
stays at pipe, so a mismatch against a hand calc can only come from the new
post engineering. Checks 1 and 2 are unchanged, and test case 1 must pass
exactly as it does today.

## Decisions settled for this slice

**D1. Second-order effects: a ratio and a stop, not an amplifier.** The
tool does not implement Appendix 8 amplification. In each case that has
moment and axial load together (outward, inward, longitudinal), it computes
αPr/Pe and prints one line:

> Second-order effects negligible: αPr/Pe = [value]; amplification taken
> as 1.0.

If αPr/Pe exceeds 0.05 in any of those cases, the calc stops. The stop names
the case, the ratio and the limit, the same way the slender-section stop
does. The gate applies only to cases with lateral design loads (outward,
inward, longitudinal). The downward and upward cases are left out on
purpose: they have no lateral design load, so no moment to amplify.
Notional loads are neglected (D10), so the gravity-only downward case
carries no moment either. Downward axial compression is covered by the
Chapter E check at K = 2.1, and upward is tension. Without that exclusion, a
Pipe1-1/2STD post at h = 42 in with a 7'-0" span would stop on the downward
distributed case (1.6 × 378 lb / 10.78 kip = 0.056), which is an ordinary
guard.

- α = 1.6 (ASD) and the Pe expression, π²EI/Lc², come from AISC 360-22
  Appendix 8. Both are code entries.
- Pe uses Lc = 2.1h, the same effective length as the compression check
  (D3), with EI, not the reduced EI\* of the direct analysis method. This
  departs from Appendix 8 as written: B1 uses K1 = 1, and B2 uses the story
  stiffness. The post is a cantilever, so its second-order effect is sway
  (P-Δ). Pe at K = 1 would be about 4.4 times larger and would understate
  the ratio by that factor. Because the choice of length is Micah's, it is
  recorded in an engineering-judgement entry, and the printed line cites
  that entry as well as Appendix 8.
- Pe stays at K·h (Micah, 2026-10-03, on the case 2 independent calc's
  F-5). The independent calc confirmed it is the conservative choice. The
  Appendix 8 story form, Pe,story = R_M·H·L/Δ_H with R_M = 0.85 and the
  cantilever stiffness 3EI/(h − t_p)², gave 12.58 kip for case 2, against
  10.78 kip at Lc = 2.1h, so the K·h value is about 17% lower and gives a
  higher αPr/Pe.
- The 0.05 limit is its own entry, source "engineer", together with the
  printed sentence. 1/(1 − 0.05) = 1.053, so the amplification neglected is
  at most about 5%.
- Where it shows: αPr/Pe prints in the full calc lines of the controlling
  case, if that case has moment. It also gets its own column in the Check 5
  envelope table, with "—" for downward and upward, so the value is visible
  for every case the stop checks. The column carries only the value; the
  printed sentence goes in the calc lines.

**D2. Post self-weight: full weight at the base, over h − t_p.** The post
dead load is D_post = W × (h − t_p), the tabulated W over the length from
the top of the baseplate to the top rail centerline. That is the same
cantilever length Check 6 and the Check 7 moment arm use. All of it acts as
axial load at the critical section. The axial dead load at the post is
D = w_D,rail × s + D_post, with the span s as the tributary length (locked
assumption).

**D3. Compression effective length: Lc = K·h with K = 2.1.** K is the
recommended design value for a fixed-free column, from AISC 360-22
Commentary Appendix 7, Table C-A-7.1. The table and case are recorded in
the entry. The length is h, not h − t_p. That is Micah's ruling, slightly
conservative, and the same Lc is used for Pe (D1).

**D4. The critical section is at the top of the baseplate.** Horizontal
guard loads applied at the top of the post produce M = V·(h − t_p) in
Check 5. This follows from the locked assumption "the post is fixed at the
top of the baseplate", and it matches the brief's Check 6 length and the
Check 7 moment arm.

**D5. Cb is deferred.** The brief sets post Lb = h under the §F1 cantilever
provision, but round sections have no lateral-torsional buckling limit
state. Cb is drafted in the first slice that brings an LTB-susceptible
section (slice 6 or 7, docs/ROADMAP.md). For the post, Check 5 prints
`aisc360.F8.no_ltb`, just as Check 1 does for the rail.

**D6. Lc/r above 200: a visible flag, not a stop.** Lc/r always prints. When
it exceeds the §E2 User Note's recommended 200, a flag prints beside the
value and in the Check 5 summary row, the way a noncompact section is
flagged, and the calc continues. A Pipe1STD post at h = 42 in reaches about
209.

**D7. Two post test cases, one per Chapter E branch.** Both use test case
1's rail and span (Pipe1-1/2STD top rail, A53 Gr B, 7'-0" span, default
loads), with h = 42 in and t_p = 1/2 in. At h = 42 in, Lc = 88.2 in and
4.71√(E/Fy) = 135.6 for A53 Gr B:

- Test case 2, Pipe1-1/2STD post: Lc/r = 141, Eq. E3-3 (elastic buckling).
- Test case 3, Pipe2STD post: Lc/r = 112, Eq. E3-2.

Both are common guard posts, so neither branch is left tested only against
the machinery, as F8-2 was in slice 1. Case 2 is also the geometry in D1
whose downward distributed case exceeds 0.05. So it checks, against the
independent calc, that the second-order stop covers only the moment cases.

**D8. Axial-only cases use their own chapter, not Chapter H.** Downward has
axial compression with no moment, so its ratio is Pr/Pc (Chapter E).
Using Eq. H1-1b with Mr = 0 would report half of that. Upward is Pr/Pt,
with Pt from §D2 yielding on the gross section. Chapter H applies only in
the cases that have moment. The ratio line carries a margin note: on
downward, "axial only; Chapter E ratio reported", and on upward, the same
wording with Chapter D, "axial only; Chapter D ratio reported", because the
upward case is tension.

**D9. The post is required.** From this slice on, every project file has a
post, post height and baseplate thickness. That matches v1, which always
checks one post. Test case 1 and `examples/slice-1.toml` gain post inputs.
Case 1's recorded hand values are for Checks 1 and 2 only, and they must
pass unchanged. A changed value is a rule 2 stop.

**D10. Notional loads are neglected.** Ruled by Micah on 2026-10-03, on
the case 2 independent calc's F-1. K = 2.1 is the effective length method
(AISC 360-22 App. 7), which as written calls for notional loads in
gravity-only combinations. The tool neglects them, and a new locked
assumption says so (docs/brief/output.md):

> Notional loads (AISC 360-22 App. 7) are neglected. In gravity-only
> combinations they produce a negligible moment, and the reported
> axial-only ratio bounds the H1-1b result.

For case 2's downward distributed case the notional moment would be about
0.002 × 1.6 × 378 lb × 41.5 in ≈ 50 lb-in, and H1-1b with it is below the
reported Pr/Pc (D8). With notional loads neglected, the downward case has
no lateral design load and stays outside the αPr/Pe gate (D1).

**D11. Post loads use tributary length = span.** Ruled by Micah on
2026-10-03, on the case 2 independent calc's F-2: this is his
long-standing practice as engineer of record. The distributed guard load
and the rail dead load reach the post as w·s and w_D,rail·s, with no
increase for rail continuity (a two-span continuous rail would put
1.25·w·s into the interior post). A new locked assumption says so
(docs/brief/output.md):

> Post loads use tributary length = span; rail continuity effects on post
> reactions are neglected (engineering judgement).

The existing assumption that the rail runs continuously over the post
stays, because it describes the connection detail.

## What the slice does

### Input

The project file gains these fields (bare numbers are inches, as
everywhere):

- `[geometry]`: `post_height` (h, from top of concrete to the top rail
  centerline) and `baseplate_thickness` (t_p). The reader rejects
  t_p ≥ h and non-positive values with a clear message.
- `[post]`: `section` (AISC pipe designation) and `grade` (A53 Gr B only,
  enforced by the same check the rail uses).
- `[deflection.post]`: `limit_L_over` (default 60, an input default, not a
  code value) and `bypass`.

The dimensions page echoes h and t_p as entered and normalized, and prints
the derived h − t_p and Lc.

### Engineering

**Section properties** for the post come from the database as published:
D, t_des, A, W, I, S, Z, r, D/t. The pipe section type gains `r` (column
`rx`, already in the extracted file), so no re-extraction is needed.

**Classification** runs before capacity. Flexure uses Table B4.1b round HSS
and the §F8 D/t limit, as slice 1 already does. Compression uses Table
B4.1a round HSS, λr = 0.11E/Fy. Slender in either is a hard stop that names
the element, the ratio and the limit. Compression has no noncompact
category. A noncompact section in flexure computes and is flagged, as in
slice 1.

**Capacities:**
- Compression: Fe per Eq. E3-4, then Fcr per Eq. E3-2 or Eq. E3-3,
  whichever applies at 4.71√(E/Fy). Pn = Fcr·Ag (Eq. E3-1), and Pc = Pn/Ωc
  (§E1).
- Tension: Pn = Fy·Ag (Eq. D2-1), and Pt = Pn/Ωt (§D2). Tensile rupture
  (§D2(b)) is not a v1 check (Micah, 2026-10-03, on the case 2
  independent calc's F-4). It does not govern for these sections: a pipe
  welded all around to the baseplate has U = 1.0 (Table D3.1, Case 1), so
  Ae = Ag, and for A53 Gr B Fu/Ωt = 60/2.00 = 30 ksi exceeds
  Fy/Ωt = 35/1.67 = 21.0 ksi.
- Flexure: Mn per §F8 through the existing flexural-capacity code, with
  Mc = Mn/Ωb.

**Envelope.** Both guard loads apply at the top of the post (brief,
loads-and-envelope.md). The concentrated load is P. The distributed load
reaches the post as w·s. These are separate load types, never concurrent,
and the exemption flag removes the distributed load, as in slice 1.

| Case | Axial Pr at top of baseplate | Moment Mr | Check 5 | Check 6 |
| --- | --- | --- | --- | --- |
| Downward | D + L, compression | 0 | Pr/Pc (D8) | Listed: vertical, no lateral deflection |
| Outward, inward | D, compression | L·(h − t_p) | §H1.1, plus αPr/Pe (D1) | L only |
| Longitudinal | D, compression | L·(h − t_p) | §H1.1, plus αPr/Pe (D1) | L only |
| Upward | 1.0L − 0.6D, tension | 0 | Pr/Pt (D8) | Listed: vertical, no lateral deflection |

- Downward, outward, inward and longitudinal use the ASCE 7-22 ASD D + L
  combination (`asce7.combo.asd.D_plus_L`).
- Upward uses 0.6D + 1.0L, labeled engineering judgement. It reuses
  `ej.combo.bending.upward`. The entry's note is broadened to say the same
  combination applies to the post's axial load. Notes do not print, and the
  printed cite already says "upward case".
- If 0.6D ≥ L, the upward case shows "no net tension; compression covered
  by downward" and is not checked.
- Outward and inward are identical for a round post, and longitudinal
  equals transverse. All are listed so the envelope is explicit, and
  longitudinal is a real, checked case for the post. For the top rail it
  stays "rail carries axially; not checked".
- For round sections the five direction cases cover the ASCE 7-22 "any
  direction" (Micah, 2026-10-03, on the case 2 independent calc's F-3). An
  inclined load trades moment for axial load. In H1-1b the worst
  inclination above horizontal is θ = atan[Mc/(2Pc·(h − t_p))], and the
  ratio rises by the factor √(1 + tan²θ). For case 2 that is θ = 1.07° and
  a 0.018% increase, far inside the 0.5% test tolerance. The increase stays
  that small whenever Mc is much smaller than 2Pc·(h − t_p), which holds for
  guard posts, whose axial capacity far exceeds their lateral load.
- In the moment cases, Pr/Pc selects Eq. H1-1a (Pr/Pc ≥ 0.2) or Eq. H1-1b.

**Deflection (Check 6)**: Δ = V·(h − t_p)³/(3EI), live load only
(`ej.combo.deflection.L_only`), in the three horizontal cases. The limit is
(h − t_p)/60 unless edited, or "Bypassed by engineer" when bypassed. The
limit cites a new entry, `ej.deflection.limit.post`: allowable deflection
is the cantilever length h − t_p divided by the limit ratio the engineer
enters. `ej.deflection.limit` stays as it is and stays with the rail span,
so its verification is not reopened.

### Output (PDF)

The existing layout, extended:

- **Front matter assumptions:** the two locked assumptions added by D10
  and D11 (docs/brief/output.md) print with the others.
- **Dimensions:** h, t_p, h − t_p, Lc.
- **Section properties:** a post block beside the rail block.
- **Loading:** the post dead load line and D at the post.
- **Checks 5 and 6:** they follow Checks 1 and 2, with the same structure:
  an envelope table (Check 5 adds the αPr/Pe column), then the full calc
  lines for the controlling case, ending with the ratio and OK or NG. The
  Check 5 lines name the interaction equation used. In the axial-only
  cases, they carry the D8 margin note instead.
- **Summary table:** rows for Checks 1, 2, 5 and 6.

Checks 3, 4 and 7 and the reactions are not printed.

## Registry entries this slice will draft

Each is drafted with its exact citation and source, and listed in the
review list. Equation numbers and table cases below are from memory, and
the entries record them for verification.

- AISC 360-22 §E1: Ωc
- §E3: Eq. E3-1, Eq. E3-2, Eq. E3-3, Eq. E3-4, and the 4.71√(E/Fy) branch
  limit
- §E2 User Note: Lc/r ≤ 200 recommended (provision text, for the D6 flag)
- Table B4.1a, round HSS in compression: λr
- Commentary Appendix 7, Table C-A-7.1: K = 2.1, the recommended design
  value for a fixed-free column
- §D2: Eq. D2-1 and Ωt
- §H1.1: Eq. H1-1a, Eq. H1-1b, and the Pr/Pc = 0.2 threshold
- Appendix 8: α = 1.6 for ASD, and the Pe expression
- Engineering judgement (source "engineer"): Pe computed at Lc = 2.1h; the
  0.05 limit together with the printed sentence (D1)
- AISC Manual Table 3-23, cantilever with a concentrated load at the free
  end: maximum moment and free-end deflection, with case numbers
- Engineering judgement (source "engineer"): `ej.deflection.limit.post`,
  the post cantilever deflection limit (default L/60, an input default)
- Note broadened (no printed change): `ej.combo.bending.upward`

That is about 20 entries, within the roadmap's estimate of 18–23.

## Tests

- **Test cases 2 and 3 (independent-calc cases, docs/brief/verification.md):**
  case 1's rail and span with h = 42 in and t_p = 1/2 in. Case 2 has a
  Pipe1-1/2STD post, and case 3 a Pipe2STD post (D7). For each case:
  - The independent calc (.claude/skills/independent-calc/SKILL.md) records
    a value for every key. It reads verified entries only, so it works
    every value this slice drafted from its own reading of the code:
    - post section properties used, including r; D_post and D at the post
    - Lc, Lc/r, Fe, Fcr (and which equation), Pn, Pc, Pt, Mn, Mc
    - for each envelope case: Pr, Mr, the equation used and the ratio
    - αPr/Pe for each moment case
    - for each horizontal case: Δ, plus Δ_allow and each ratio
    - the controlling direction for each check
  - Micah recomputes the printed controlling case of Check 5 and of Check 6
    line by line, checking each provision against the code, and records his
    own results in [hand]: at least each governing ratio and which case
    governs (docs/brief/verification.md, changed 2026-10-04).
  - Micah then reviews the independent calc and the slice PDF against the
    checklist in docs/brief/verification.md.

  The Check 1 and 2 values are not recorded in these cases; case 1 covers
  them. Every recorded value must fall within 0.5% relative of the tool's.
  A mismatch, against Micah's value or the independent calc, is a rule 2
  stop.
- **Test case 1:** post inputs added (D9), the same post as case 2
  (Pipe1-1/2STD, h = 42 in, t_p = 1/2 in). Case 1 records no post values.
  Its existing hand values pass unchanged.
- **Hard stops:**
  - slender in compression (B4.1a) stops, naming the ratio and the limit
  - αPr/Pe > 0.05 in a moment case stops, naming the case, the ratio and
    the limit
  - a downward case with αPr/Pe > 0.05 does not stop (test case 2's
    geometry, distributed load), so the D1 scope is held
  - t_p ≥ h is rejected at input
- **Flags and branches:**
  - Lc/r > 200 prints the flag and the calc continues (Pipe1STD at
    h = 42 in)
  - the upward case with no net tension shows the "no net tension" status
  - the downward ratio is Pr/Pc, not the H1-1b value, and the D8 margin
    notes print on both axial-only cases
- **Eq. H1-1a is tested for machinery only.** In the moment cases Pr is
  dead load only, so no realistic guard post reaches Pr/Pc ≥ 0.2, and both
  hand cases will use H1-1b. H1-1a gets a same-author arithmetic test, like
  F8-2 in slice 1. This gap has no realistic trigger in v1 and is recorded
  here rather than as an issue.

## Build order

The branch is `slice-2`. Each step is committed and pushed when its tests
pass.

1. **Issue #4 cleanup** (the `.magnitude` sign test, the stale
   docs/BRIEF.md references, the stale registry note). All existing tests
   pass unchanged.
2. **Project file:** the post, geometry and deflection.post fields, with
   validation. Update test case 1 and `examples/slice-1.toml` (D9).
3. **Registry entries** drafted, and the review list updated.
4. **Post section:** add `r` to the pipe section type; build the post dead
   load and D at the post.
5. **Check 5:** B4.1a classification, Chapter E, §D2, §H1.1, the envelope,
   the αPr/Pe line and stop, and the Lc/r flag.
6. **Check 6:** cantilever deflection over the horizontal cases.
7. **Report:** dimensions, section properties, loading, the Check 5 and 6
   pages, and the summary rows.
8. **Test cases 2 and 3** wired in, values pending. (Done before the
   verification model changed.)
9. **Verification harness:** independent-calc cases, with Micah's
   governing values as a subset; case 1 unchanged as a full-hand case
   (issue #14). (Done; independent templates for cases 2 and 3 created
   by tests/independent_template.py. "No pending at merge" is not a
   test: the calc-code-review skill treats any remaining "pending" in
   tests/cases/ as a must-fix.)
10. **Independent calcs** for cases 2 and 3, each run in a fresh session
    by the independent-calc skill.
11. **Front-matter assumptions:** print the two locked assumptions added
    on 2026-10-03 from the case 2 independent calc's findings, notional
    loads neglected (F-1, D10) and tributary length = span with rail
    continuity neglected (F-2, D11), in the front matter with the others
    (docs/brief/output.md). This changes printed calc text. Locked
    assumptions stay out of the registry (issue #12, closed 2026-10-03).
12. **Micah's governing-case calcs and review** (What Micah does, below).
13. **Pull request** to main, with the calc-code-review skill run on the
    branch first.

## What Micah does

- For test cases 2 and 3 (inputs set in D7), recompute the printed
  controlling cases of Checks 5 and 6 line by line, and record the
  recomputed values in [hand].
- Review each independent calc and the slice PDF against the checklist in
  docs/brief/verification.md, and approve the pull request.

## Done when

- `uv run handrail calc examples/slice-1.toml` produces a PDF with Checks 1,
  2, 5 and 6 as described above.
- All tests pass, including test cases 1, 2 and 3 at 0.5%, with no
  pending value in cases 2 and 3.
- Micah has reviewed the independent calcs and the PDF, and agrees with
  them.

The slice's registry entries are not verified here; they wait for the
release review (slice 9), and the slice 2 PDFs print the DRAFT stamp
until then.

## Not in slice 2

- Checks 3, 4 and 7, welds, and the intermediate rail
- Anchor reaction sets, baseplate B × N, and baseplate grade
- Cb and every LTB provision (D5)
- Appendix 8 amplification (D1)
- Sections other than AISC pipe, and grades other than A53 Gr B
- The input form
