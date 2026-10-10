# Brief: checks

Part of the product brief; index in docs/BRIEF.md. The seven checks,
flexural and compression capacity, section classification and section
properties. Weld method is in welds.md.

## Checks

1. Top rail bending (simple span)
2. Top rail deflection: downward case D + L on the vertical axis; horizontal
   cases live load only on the horizontal axis; upward case live load only,
   computed and shown though it will not control; run over the full envelope
3. Top rail weld to post: horizontal shear V plus the moment V·e, where e is
   the distance from the rail centerline to the weld plane. Downward load
   passes through the weld; no credit is taken for bearing at the cope.
4. Intermediate rail component check: the component load at midspan of
   the intermediate rail spanning between posts, in two cases (S4-10,
   below). Horizontal: the ASCE 7-22 §4.5.1.2 load, acting alone, not
   combined with dead load. Downward: the same load plus the intermediate
   rail's dead load on the same axis, ASD D + L (engineering judgement,
   after OSHA 1910.29(b)(5)). Neither is concurrent with the top-rail
   loads. Includes a deflection check under each case, default L/120,
   editable and bypassable. When the intermediate rail
   is the same as the top rail, Check 4 is controlled by Checks 1 and 2 by
   observation and not computed, unless the component load exceeds the
   concentrated guard load (S4-1 and S4-2, below). If there is no
   intermediate rail, the check shows "none". Check 4 has two parts: 4a,
   the member (above), and 4b, the intermediate rail weld to the post,
   treated like Check 3 (S4-8, welds.md).
5. Post combined axial and flexure (cantilever)
6. Post deflection (cantilever), horizontal live load only, over the
   cantilever length h − t_p; the L/60 limit uses the same length
7. Post weld to baseplate

Flexural capacity: top rail Lb = span, with Cb from the §F1 moment diagram
for each load case. Post Lb = h using the §F1 cantilever provision. These
Lb and Cb apply only to sections with a lateral-torsional buckling limit
state. Round sections (pipe, round HSS, solid round bar) have none, so Lb
and Cb do not enter their flexural capacity (Slice 2, D5, below). Post
compression uses the recommended design K. In the upward case the post is
checked for axial tension (yielding on the gross section); it is computed
and shown in the envelope summary even though it will not control.

Plus reporting, not pass/fail: factored (LRFD) base reactions for a concrete
substrate, labeled for direct input into anchor software (see
loads-and-envelope.md).

## Engineering decisions already made

- Biaxial bending (dead load about one axis, horizontal guard load about the
  other): round HSS and pipe use the square root of the sum of the squares
  of the two moments against a single capacity, which is exact for a round
  section. All other sections use the AISC 360-22 provisions for combined
  strong- and weak-axis bending.
- Section classification runs before capacity. Compact computes normally.
  Noncompact computes at reduced capacity and is flagged visibly, with the
  width-to-thickness ratio and limits shown. Slender, in either flexure
  (AISC 360-22 Table B4.1b) or compression (Table B4.1a), is a hard stop
  that names the element, its ratio and the limit. Slender-member checks may
  be added later if the need shows up.

- Biaxial SRSS applies to every round section, solid round bar included.
- Standard-section properties are used exactly as published in the
  database, even when the grade (A1085, for example) implies a different
  design wall thickness; the output notes it. Custom rectangular tubes use
  the AISC corner-radius convention, a registry entry. Custom tubes convert
  nominal to design wall thickness per AISC 360-22 §B4.2, a registry entry.
  A1085 is the first grade both rules meet: S5-6, inputs.md.
- Custom tube thickness: the wall entered is always the nominal wall
  (S5-8, inputs.md; Micah 2026-10-09, replacing the nominal/design
  choice). Dead weight uses the nominal wall. Strength and section
  properties use the design wall, converted from nominal per §B4.2. This
  matches AISC's convention (tabulated weight on nominal wall, properties
  on design wall).
- Pipe is designed under the AISC 360-22 round HSS provisions; the
  registry records the basis. (Slice 1.)
- A round section whose D/t is beyond the §F8 applicability limit is a
  hard stop, the same as a slender section: it names the ratio and the
  limit. (Slice 1.)
- Round sections have no lateral-torsional buckling limit state, so Lb and
  Cb do not enter their flexural capacity, and the check prints that
  provision instead. Cb from the §F1 moment diagram is first needed for an
  LTB-susceptible section. (Slice 2, D5.)
- The Check 2 downward case combines D + L as an engineering-judgement
  serviceability combination, labeled as such, not as an ASD strength
  combination. (Slice 1.)

### The post (Checks 5 and 6)

Decided in slice 2; D numbers are that slice plan's decision numbers, kept
for the record.

- **Critical section.** The post is fixed at the top of the baseplate (a
  stated assumption), so that is the critical section. Horizontal guard
  loads at the top of the post produce M = V·(h − t_p), the same length as
  the Check 6 cantilever and the Check 7 moment arm. (D4.)
- **Compression.** Lc = K·h with K = 2.1, the recommended design value for
  a fixed-free column (AISC 360-22 Commentary Appendix 7, Table C-A-7.1).
  The length is h, not h − t_p: my ruling, slightly conservative. Chapter
  E: Fe, then Fcr per Eq. E3-2 or E3-3 at the 4.71√(E/Fy) limit, Pn = Fcr·Ag
  and Pc = Pn/Ωc. (D3.)
- **Classification in compression** uses Table B4.1a for round HSS. Slender
  is a hard stop; compression has no noncompact category. Flexure is
  classified as for the rail.
- **Lc/r above 200** (the §E2 User Note's recommended limit) is a visible
  flag, not a stop. Lc/r always prints; above 200 a flag prints beside it
  and in the Check 5 summary row, the way a noncompact section is flagged,
  and the calc continues. (D6.)
- **Tension** (upward case): yielding on the gross section, Pn = Fy·Ag and
  Pt = Pn/Ωt (§D2). Tensile rupture is not a v1 check: a pipe welded all
  around to the baseplate has U = 1.0 (Table D3.1, Case 1), so Ae = Ag,
  and for A53 Gr B rupture does not govern over yielding. (Ruled
  2026-10-03.)
- **Interaction only where there is moment.** In the outward, inward and
  longitudinal cases Check 5 uses §H1.1, Eq. H1-1a when Pr/Pc ≥ 0.2 and
  Eq. H1-1b otherwise. The axial-only cases use their own chapter:
  downward reports Pr/Pc (Chapter E) and upward reports Pr/Pt (Chapter D),
  because H1-1b with Mr = 0 would report half the axial ratio. Their ratio
  lines carry the margin note "axial only; Chapter E ratio reported" or
  "axial only; Chapter D ratio reported". (D8.)
- **Second-order effects: a ratio and a stop, not an amplifier.** The tool
  does not implement Appendix 8 amplification. In each case with a lateral
  design load (outward, inward, longitudinal) it computes αPr/Pe, with
  α = 1.6 (ASD) and Pe = π²EI/Lc² from Appendix 8, using Lc = K·h (the
  compression length) and EI, not the reduced EI\*. It prints:
  "Second-order effects negligible: αPr/Pe = [value]; amplification taken
  as 1.0." If αPr/Pe exceeds 0.05 in any of those cases, the calc stops,
  naming the case, the ratio and the limit, like the slender-section stop.
  The 0.05 limit is engineering judgement: 1/(1 − 0.05) = 1.053, so the
  amplification neglected is at most about 5%. (D1.)
  - The downward and upward cases are outside the gate: with notional
    loads neglected they have no lateral design load, so no moment to
    amplify. Downward compression is covered by Chapter E at K = 2.1, and
    upward is tension.
  - Using Lc = K·h for Pe departs from Appendix 8 as written (B1 uses
    K1 = 1; B2 uses the story stiffness). The post is a cantilever, so its
    second-order effect is sway (P-Δ); Pe at K = 1 would be 2.1² ≈ 4.4
    times larger and understate the ratio by that factor. Pe at K·h is
    also lower than the Appendix 8 story form, R_M·H·L/Δ_H with R_M = 0.85
    and the cantilever stiffness 3EI/(h − t_p)², so it is the conservative
    choice. The choice of length is recorded as an engineering-judgement
    entry, and the printed line cites it as well as Appendix 8. (D1;
    kept 2026-10-03.)
- **Notional loads are neglected.** K = 2.1 is the effective length method
  (AISC 360-22 Appendix 7), which as written calls for notional loads in
  gravity-only combinations. In those combinations they produce a
  negligible moment, and the reported axial-only ratio bounds the H1-1b
  result. This is a stated assumption (output.md). (D10.)
- **Check 6** is Δ = V·(h − t_p)³/(3EI), live load only, in the three
  horizontal cases; the downward and upward cases are listed as vertical,
  with no lateral deflection. The allowable deflection is (h − t_p)
  divided by the limit ratio, default 60, editable and bypassable. The
  post limit is its own engineering-judgement entry, separate from the
  rail span limit.

### The intermediate rail (Check 4)

Decided in planning slice 4 (docs/plans/slice-4.md); S4 numbers are that
plan's decision numbers, kept for the record.

- **Three input states.** (S4-1, Micah 2026-10-08.) This replaces the
  earlier rule that Check 4 is computed every time, even when the
  intermediate rail matches the top rail.
  - **Same as the top rail** (`same_as_top_rail`, a checkbox, default
    checked): section and grade are the top rail's. Check 4 is not
    computed; it is controlled by Checks 1 and 2 (S4-2, below). The
    intermediate rail's dead load is still added to the post.
  - **Its own section** (checkbox unchecked): the engineer enters the
    section; the grade defaults to the top rail's. The full Check 4 runs:
    component-load bending and deflection, with its own deflection limit
    (S4-2).
  - **None** (`none = true`): no intermediate rail. Check 4 prints "none"
    and no intermediate rail dead load is added.
  - No height input: the Check 4 moment does not depend on it, and the
    component load's effect on the post is not checked (a stated
    assumption, output.md).
  - Because the default state adds dead load to the post, test cases 1–4
    gain `none = true` as an input-only addition, so none of their
    recorded values changes.
- **Check 4 when the intermediate rail is the same as the top rail.**
  (S4-2, Micah 2026-10-08.)
  - Check 4 prints: "Controlled by Checks 1 and 2 by observation: same
    section, grade and span as the top rail; component load P_c = [value]
    ≤ concentrated guard load P = [value]. See Checks 1 and 2 for the
    result." The summary row shows "Controlled by Checks 1 and 2", with
    no ratio and no OK or NG of its own. The wording defers to the top
    rail's result, so a failing Check 1 or 2 needs no separate guard.
  - There is no separate deflection input in this state. The
    intermediate rail follows Check 2, including a bypass.
  - One guard: loads are editable, so if P_c > P the full Check 4 runs
    instead of the observation line.
  - Own-section state: the full Check 4, with its own deflection limit,
    `[deflection.intermediate_rail]`, default L/120, editable and
    bypassable. It cites the existing verified entry `ej.deflection.limit`,
    whose note is broadened to name the intermediate rail (a note edit,
    so the entry stays verified).
- **Component load model.** (S4-3, Micah 2026-10-08.) A point load P_c at
  midspan of the intermediate rail's simple span s: M = P_c·s/4 and
  Δ = P_c·s³/(48EI), the same model as Check 1's concentrated case. The
  1 ft² area of ASCE 7-22 §4.5.1.2 is not modeled; the point load is
  conservative (for a 7'-0" span, spreading 50 lb over a 12 in patch would
  lower M by P_c·b/8 = 75 lb-in, about 7%). P_c is an input,
  `[loads] component_lb`, defaulting to the registry value; the
  §4.5.1.1 exemption does not affect it. This position is for the member
  (Check 4a). For the weld (Check 4b) the load is placed adjacent to the
  post (S4-9, welds.md). Both directions use the same P_c (S4-10).
- **Two directions for the component load.** (S4-10, Micah 2026-10-09.)
  The component load is checked horizontal and downward. ASCE 7-22
  §4.5.1.2 specifies horizontal only; the downward case is engineering
  judgement, after OSHA 1910.29(b)(5), which requires midrails to
  withstand 150 lb in any downward or outward direction.
  - Check 4a, two cases. Horizontal: the component load alone, as before.
    Downward: the component load at midspan plus the intermediate rail's
    dead load, on the same axis, ASD D + L. Deflection under each case,
    with the S4-2 limits, combined as Check 2 does: the horizontal case
    live load only, the downward case D + L (the engineering-judgement
    serviceability combination of Check 2).
  - Check 4b, two cases (welds.md, S4-9).
  - The same-as-top observation for Check 4a still holds when P_c ≤ P:
    Checks 1 and 2 already run the top rail downward and horizontal at P,
    with the same section, span and dead load.
  - The default component load stays 50 lb (ASCE 7-22). The input info
    box adds: "OSHA 1910.29(b)(5) requires intermediate members to
    withstand 150 lb downward or outward; enter 150 lb where OSHA
    applies." Its text is a registry entry, like the exemption info box.
    An OSHA toggle is out of v1 (docs/ROADMAP.md, after v1).

### Section families (slices 5 to 7)

Decided in planning slice 5 (docs/plans/slice-5.md); S5 numbers are that
plan's decision numbers, kept for the record.

- **Section families arrive grouped by engineering.** (S5-1, Micah
  2026-10-09.) Slice 5: hollow round sections, that is round HSS from the
  database and custom round tubes (§B4.2), on the same provisions as pipe
  (§F8, Table B4.1, Chapter E), with a noncompact test case for Eq. F8-2.
  Slice 6: rectangular HSS and custom rectangular tubes. Slice 7: solid
  round bar and solid rectangular bar together (§F11, LTB with Cb, and
  welds to a member with no wall). This replaces the earlier grouping by
  outline, which put solid round bar with the round tubes.
  - Until slice 7 a solid bar cannot be entered. Everything in welds.md
    that is written over a wall (the fusion face thickness W4, the base
    metal lines W5 and W6, "post wall covered by Check 5", Table J2.4's
    thinner part W11, Check 4b's base metal on both walls) is decided for
    solid members once, in slice 7's plan.
  - The section type carries per-axis properties (I, S, Z and r about x
    and about y) from slice 5. A round section has x = y. This fixes the
    data a section holds, not how a check uses it: which axis each check
    reads, the axis input, and Chapter H biaxial bending for non-round
    sections are slice 6's decisions.
- **A round HSS uses the database's values as published, the outside
  diameter included.** (S5-4, Micah 2026-10-09.) The Shapes Database
  stores a round HSS's OD rounded to three significant figures (2.38 in
  for HSS2.375X0.154, 2.88 in for HSS2.875, 6.63 in for HSS6.625; 61 of
  the 189 round HSS rows differ from their designation), and a pipe's OD
  exactly (2.375 in for Pipe2STD). The tool uses the OD column as it
  stands and never reads a diameter out of the designation, so "standard
  section properties are used exactly as published" (above) has no
  exception, and the independent calc reads the same value from the AISC
  workbook.
  - Accepted effect: the weld ring (πD and S_w = πD²/4) and the
    eccentricity e = D_rail/2 use the published OD, which moves Checks 3,
    4b and 7 by about 0.2 to 0.4% against the designation's diameter.
    A, I, S, Z, r and D/t are the published values and do not depend on
    the OD column.
  - The W8 and S4-11 width comparisons treat two ODs within 0.01 in as
    equal (welds.md, S5-4).
