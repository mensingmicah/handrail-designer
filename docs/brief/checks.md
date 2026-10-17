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
- **Custom round tube formulas are exact geometry on the §B4.2 design
  wall.** (Micah, 2026-10-10, ruling on the pipe-row report of the
  property-formula test, slice 5 plan T3.) A, I, S, Z, r and D/t come from
  OD and t_des as a hollow circle, and weight from the steel unit weight
  times the area on the nominal wall. They are not forced to match the
  database. The test holds them to the 67 round HSS rows of 10 in OD or
  less in full, and to the pipe rows under 12 in OD on I, S, Z, r and
  weight, with the area never more than 1% above published. Six XS pipe
  rows (14 to 26 in), five pipe areas above published and one pipe D/t
  are accepted database findings, listed in data/README.md, not asserted.
  A custom tube entered with a database shape's dimensions can therefore
  differ from the database shape by those amounts.
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
- **The Fu/Fy ≥ 1.20 guard on the post grade also carries the
  tension-rupture ruling to the new grades.** (S5-13; Claude's, confirmed
  by Micah 2026-10-09.) "The post" above rules out a tensile rupture
  check because yielding governs for A53 Gr B. The same holds for any
  grade with Fu/Fy ≥ 1.20, which the weld decisions' guard on the post
  grade already enforces by stopping the calc (welds.md, W5). Every grade
  slice 5 drafts passes on its drafted values; the lowest is A500 Gr C at
  62/50 = 1.24.
- **Which sections print "designed as round HSS".** (S5-14; Claude's,
  confirmed by Micah 2026-10-09.) The line "Pipe is designed under the
  round HSS provisions" prints for an AISC pipe and for a custom A53
  tube. A round HSS, or a custom tube of an HSS grade, is round HSS and
  prints no such line.

### Hollow rectangular sections (slice 6)

Decided in planning slice 6 (docs/plans/slice-6.md); S6 numbers are that
plan's decision numbers.

- **Slice 6 is not split.** (S6-1, Micah 2026-10-10; welds.md, "Hollow
  rectangular sections and the chord limit states (slice 6)".)
  Rectangular members are built first, then the Chapter K chord limit
  states, round chords before rectangular chords.
- **A custom rectangular tube follows AISC's conventions, with no corner
  radius input.** (S6-3, Micah 2026-10-10.) It settles "Custom
  rectangular tubes use the AISC corner-radius convention" above.
  - Section properties (A, and I, S, Z and r about both axes): exact
    geometry on a rounded rectangle with an outside corner radius of
    2·t_des and an inside radius of t_des, the radius the Shapes
    Database's own properties are built on.
  - Wall slenderness (b/t and h/t for Table B4.1): the outside dimension
    less 3·t_des, AISC 360-22 §B4.1b(d), page 16.1-22, the rule for a
    corner radius that is not known. It implies a 1.5·t outside radius;
    the two conventions differ on purpose, as they do in the database.
  - Weight: the steel unit weight times the area on the nominal wall,
    with a 2·t_nom outside radius (S5-8).
  - The wall is always entered as the nominal wall, t_des per §B4.2 by
    grade (S5-8, inputs.md).
  - Not chosen: an entered corner radius (it could be entered
    unconservatively, a small radius raising every property), or sharp
    corners (3 to 5% high on area at guard sizes).
  - Accepted: a custom tube entered with a database shape's dimensions
    can differ from the database shape by up to about 1%, on the low
    side, as for round tubes. Scratch trial (Claude, 2026-10-10; planning
    arithmetic, not test values) on the 525 rectangular HSS rows: of the
    208 rows with Ht ≤ 8 in, 103 reproduce A, Ix, Iy, Zx, Zy, Sx, Sy, rx
    and ry to the printed digit, the worst miss is 0.93% below published
    and none is above; over all rows 9 come out above, the worst by
    0.22%; weight is within 0.25% on every row.
  - The property-formula test (binding, as slice 5's T3 as ruled): on
    the rows with Ht ≤ 8 in every property reproduces or comes out below
    published, never above, and no more than 1% below; weight within
    0.5%. Larger rows are a reported database finding, not asserted. A
    row above published in the binding set stops the build and goes to
    Micah; the tolerance is never widened.
- **Rectangular HSS flexure: §F7 in full, with Cb from the moment
  diagram.** (S6-4, Micah 2026-10-10.) AISC 360-22 §F7, pages 16.1-62 to
  16.1-65: yielding (Eq. F7-1), flange local buckling (Eq. F7-2 for a
  noncompact flange), web local buckling (Eq. F7-6 for a noncompact web)
  and lateral-torsional buckling (§F7.4, Eqs. F7-8 to F7-11), each about
  the axis being bent. A slender flange or web stops, as for every
  section (above).
  - **Cb is computed now, not taken as 1.0.** Eq. F1-1 (§F1(c), page
    16.1-52) from M_max and the quarter-point moments M_A, M_B and M_C of
    each load case's own moment diagram on the simple-span rail: the
    uniform dead load combined with the concentrated or the uniform guard
    load, as that case combines them. Only for the axis that has an LTB
    limit state. Lb = the span between posts. "Cb from the §F1 moment
    diagram for each load case" (Flexural capacity, above) applies to
    rectangular HSS from this slice.
  - **Rectangular members are biaxial by Chapter H, not SRSS.** A case
    with vertical and horizontal load bends both axes; each axis takes
    its own diagram, its own §F7 strength and its own Cb, and the two
    combine by AISC 360-22 §H1.1 (Eqs. H1-1a and H1-1b, page 16.1-82;
    Eq. H1-1b with Pr = 0 for a rail). This is "All other sections use
    the AISC 360-22 provisions for combined strong- and weak-axis
    bending" (above), now built. Square HSS included; SRSS stays with
    round sections.
  - **Post: Cb = 1.0,** a cantilever with its free end unbraced (§F1(c),
    page 16.1-52), printed with that reason. Lb = h (Flexural capacity,
    above).
  - **Printed:** M_max, M_A, M_B, M_C and Eq. F1-1, then the LTB strength
    with Mn ≤ Mp. AISC 360-22 has no upper limit on Cb itself (the 3.0
    limit of the 2005 edition is gone; read on page 16.1-52, Claude
    2026-10-10); the only cap is Mn ≤ Mp in Eqs. F7-8 and F7-9.
  - **Square sections and weak-axis bending have no LTB.** The calc
    prints that line, citing the User Note to §F7.4 (page 16.1-65).
  - **Cb is one shared function,** so slice 7's flat bar reuses it
    unchanged.
  - **J for a custom rectangular tube:** 4·Ap²·t/p on the wall's midline
    with a midline corner radius of 1.5·t_des (Ap the area enclosed by
    the midline, p its perimeter), the membrane-analogy form of the
    Commentary to §H3 (page 16.1-415). It joins the S6-3 property-formula
    test under the same rule. A database section uses its published J.
  - Planning arithmetic (Claude, 2026-10-10; not test values), HSS2×1×1/8
    on its strong axis at the drafted Fy = 46 ksi: Lp ≈ 33 in and Lr ≈
    950 in, so a 6 ft rail and a 42 in post are both past Lp and Eq. F7-8
    applies; the reduction before Cb is about 2% and 0.4%.
- **Carry-overs for rectangular sections.** (S6-14; Claude's, confirmed
  by Micah 2026-10-10, with his clarification to item 3.) None is
  expected to change which check governs a realistic guard; each extends
  an existing ruling or is a conservative simplification.
  1. **Weld envelope and load at the centerline** (welds.md, W1 and
     W10). Both rulings hold for rectangular rails and for the mixed
     pairs: no inclined guard load case, no torsion on the Check 3 weld,
     no added eccentricity for a load at the rail's surface. Planning
     arithmetic (not test values): an HSS4×2 rail on edge over an
     HSS2×2×1/8 post with a 1/8 in fillet gives Check 3 about 0.05;
     doubling e for a load at the rail's top surface gives about 0.09.
     (Amended by S6-18, Micah 2026-10-17: where the post is rectangular,
     Checks 3 and 7 take a skew horizontal case; welds.md.)
  2. **Check 5 on a rectangular post.** Compression uses the smaller
     radius of gyration with K = 2.1, in every case. Each lateral case
     bends one axis only (the transverse cases one, the longitudinal case
     the other), so §H1.1 takes one moment per case and the post has no
     biaxial case. αPr/Pe and Check 6 use I about the axis that case
     bends. (Amended by S6-18, Micah 2026-10-17: a skew case bends both
     axes, below.)
  3. **Classification.** Flexure is classified for each bent axis by
     AISC 360-22 Table B4.1b (page 16.1-23): the wall in compression is
     the flange (Case 17) and the other wall the web (Case 19; case
     numbers confirmed when drafted). Compression: Table B4.1a Case 6,
     both walls (page 16.1-21). A noncompact wall in flexure takes its
     reduced strength, not only a flag (Micah's clarification): flange
     local buckling per §F7.2(b), Eq. F7-2, and web local buckling per
     §F7.3(b), Eq. F7-6, the rectangular counterpart of the round Eq.
     F8-2 path. A slender wall stops, as now. A test case or a
     same-author test must reach the noncompact flange branch.
  4. **The Fu/Fy ≥ 1.20 guard on the post grade** (S5-13) carries to the
     rectangular grades; the lowest drafted is A500 Gr C at 62/50 = 1.24.
  5. **Same-as-top observations.** Check 4b's "controlled by Check 3"
     (welds.md, S4-8) is used for a round post with a round rail only.
     Any joint with a rectangular member runs the full Check 4b: Table
     K5.1's effective length depends on the chord wall (S6-8), so the
     comparison is no longer true by inspection. Check 4a's "controlled
     by Checks 1 and 2" (S4-2) is kept for rectangular rails: the
     intermediate rail takes the top rail's section, grade and
     orientation.
  6. **Custom rectangular tube input.** `shape = "rectangular tube"`,
     `H`, `B` and `wall_nominal` in place of `section`. H ≥ B is
     required, so `long_side` alone sets the orientation (S6-2). A wall
     too thick to leave a flat (B ≤ 4·t_des) stops. The label reads like
     "Rect. tube 2 × 1 × 0.083 (custom)". Exact wording on the branch.
  7. **Where the round chord table prints.** Inside Check 3, after the
     weld lines (welds.md, S6-1 and S6-10). Check 3 keeps one summary
     row: it reports the largest ratio among its lines (weld metal, base
     metal, chord interaction) and names which governs. No new summary
     row.
  8. **Baseplate size stop.** B must be at least the post's dimension
     parallel to the rail and N at least the one perpendicular to it:
     the existing "smaller than the post OD" stop, per direction.
  9. **Database finding.** HSS1-1/2X1-1/2X3/16 lists t_nom = 0.188 in
     where every other 3/16 in row lists 0.1875 in. It is used as
     published (S5-4) and listed in data/README.md.
  10. **Assumption wording.** The printed assumptions that say "ring",
      "saddle" and "equal round diameters" get rectangular and mixed-pair
      wording, drafted by Claude on the branch for Micah's acceptance in
      the pull request; output.md changes in the commit that prints it.
  - Not chosen, recorded as the fuller alternatives: an inclined-load
    case for rectangular rails (item 1); a rectangular same-as-top
    observation for Check 4b with its own guards (item 5).
- **Found when slice 6's rulings were checked against each other and
  against slice 5's.** (S6-16; Claude's, 2026-10-10; confirmed by Micah,
  2026-10-11.)
  1. **The round chord table gets its own summary row and its own value
     keys.** This amends item 7 of S6-14. Test cases 4 to 7 record
     `check3.ratio` for each direction case as the weld check's ratio. If
     the chord interaction were folded into that ratio, recorded values
     would change wherever the chord ratio exceeds the weld's (case 6:
     about 0.15 against about 0.05), and a recorded value is never edited
     to follow the tool (CLAUDE.md rule 5). So Check 3's ratio keeps its
     meaning, the chord table reports under its own keys, and the summary
     table gains a row, "3 (chord wall)", as Check 4 has 4a and 4b. It
     prints only at a round post on a round rail.
  2. **At Check 4b the S6-11 line prints for every pair, mixed pairs
     included.** The simple shear connection puts no force normal to the
     post wall whatever the two families are. So the "chord wall not
     checked" assumption of S6-9 and S6-12 concerns Check 3 only; S6-9's
     "and its Check 4b counterpart" is dropped.
  3. **S6-4 covers the intermediate rail in Check 4a.** Cb comes from
     each component load case's own diagram (horizontal: the midspan
     point load alone; downward: the point load with the dead load), and
     Lb is the span. Check 4a has no biaxial case: its horizontal case is
     the component load alone (S4-10).
  4. **One sentence replaces W7's in the "Stated assumptions" list.** The
     list prints word for word in every calc, so it cannot depend on the
     sections entered. Proposed, for the pull request: "Local strength of
     the rail wall at the post (AISC 360-22 Chapter K and §J10 chord
     limit states) is checked for a round post on a round rail. It is not
     checked where the rail is rectangular or where a round and a
     rectangular member meet; the rail is then held to the Chapter K
     limits of applicability."
  5. **J in the property-formula test is held at the database's printed
     precision.** Scratch trial (planning arithmetic): the midline
     formula of S6-4 reproduces J to three significant figures on 207 of
     the 208 rows with Ht ≤ 8 in, and on 524 of all 525. The one miss is
     reported to Micah in the build, not asserted and not tuned away.
  6. **The base metal lines of Checks 3 and 4b carry over to rectangular
     walls** (welds.md W5, W6, S4-12): shear rupture on the chord wall,
     and on both walls in Check 4b, with the in-plane shear taken over
     the weld line's length (le of Table K5.1, or the branch's outline at
     a mixed pair); "post wall covered by Check 5" at the Check 3 joint.
  7. **Case 6 runs under the Chapter K limits only by the A500 Gr C
     exception** (S6-13): its rail's drafted Fy/Fu is 50/62 = 0.81. So
     the exception has a test case.
  8. **Slice 5's stop at post D/t > 50 with an intermediate rail goes,**
     with its row in stops.md and its same-author test (S6-13). The rail
     stop stays.

- **Rulings on the slice 6 build report.** (S6-17, Micah, 2026-10-11.) The
  plan (docs/plans/slice-6.md) stays as written; this amends it. Item
  numbers are those of the "Waiting on Micah" list in the Slice status
  issue (#16) at the close of build step 7.
  1. **Item 10: A500 Gr B rectangular Fy/Fu stays drafted at 46/58 ksi**
     (AISC 360-22 Table 2-4). The default grade for a rectangular section
     remains A500 Gr B (S6-5).
  2. **Item 7: case 8's inputs are accepted as proposed.** Case 9's base
     weld is all around, as S6-15 specified, not a face pair; its other
     inputs are accepted as proposed.
  3. **Item 3: at a face-pair base weld the post wall's shear check uses
     one rule in every case.** The full shear per inch of weld is checked
     against wall shear rupture, 0.6·Fu·t_des/2.00, whatever the shear's
     direction relative to the welded faces. This replaces S6-7's "force
     along the face" condition for the shear component; the normal-force
     line of S6-7 is unchanged.
  4. **Item 1: Table K5.1's cap on Be applies when β > 0.85 or θ > 50°,**
     as printed. S6-8's sentence is corrected to match (welds.md).
  5. **Items 2, 4, 5, 6, 9, 11, 12, 14, 15, 18 and 19 are accepted as the
     build report recommended.**
  6. **Item 8: "or rectangular HSS" is added to `section.not_found`.** One
     stop snapshot changes; allowed.
  7. **Item 13: "and §J10" is dropped from the C1 assumption sentence**
     (S6-16 item 4), the round check computing Tables K3.1 and K4.1 only.
  8. **Item 17: the Chapter K registry entries whose notes say the PDF
     text extraction lost symbols are flagged high priority** in the
     slice-close registry review workbook.
  9. **Case 8 carries the face-pair base weld, per S6-15** (the faces
     parallel to the rail), and its Check 7 may print NG in the
     longitudinal case; that is expected. This amends item 2 above for
     case 8, whose inputs were otherwise accepted as proposed. The
     face-pair assumption sentence is reworded: "At a face-pair base
     weld, the post wall's normal force and its shear are each checked
     against their own limit, not combined; the shear is small next to
     the normal force." (Micah, 2026-10-11.)

- **A skew horizontal guard-load case for rectangular posts.** (S6-18,
  Micah, 2026-10-17; prompted by finding 1 of case 8's independent calc,
  tests/cases/independent/case-08.md §16.) This amends S6-14 item 2. The
  weld side is in welds.md, under the same number.
  1. **Why.** ASCE 7-22 §4.5.1 applies the guard load in any direction.
     Where a section or weld line has a point that sees both bending
     components at full value, the transverse and longitudinal cases do
     not envelope a horizontal load between them. Case 8's independent
     calc found Check 5 about 25% higher at the worst angle (0.708 against
     0.5651) and Check 7 about 9% higher (about 2.27 against 2.090).
  2. **A sixth direction case, "skew".** The horizontal guard load, both
     load types, enveloped as in the transverse and longitudinal cases, at
     the plan angle θ from transverse that is worst for the check being
     made. Same Pr = D and the same moment arm as the other lateral cases.
     Each check finds its own θ and prints it. It runs only where a
     rectangular or square member gives a corner (Checks 3, 5 and 7, as
     below).
  3. **Check 5, rectangular and square posts.** Mr,t = Mr·cosθ and Mr,l =
     Mr·sinθ. Eqs. H1-1a and H1-1b are linear in the two, so the worst
     angle is tanθ = Mc,t/Mc,l and the moment term is Mr·√(1/Mc,t² +
     1/Mc,l²), times 8/9 under H1-1a; √2·Mr/Mc for a square post. Mc,t and
     Mc,l are the available flexural strengths the transverse and
     longitudinal cases already compute. This replaces S6-14 item 2's "the
     post has no biaxial case"; the rest of that item stands.
  4. **No skew case for αPr/Pe or Check 6.** Each prints one sentence
     saying why. αPr/Pe: the skew case has the same Pr, and the smallest Pe
     is already computed. Check 6: the skew deflection √(δ_t²·cos²θ +
     δ_l²·sin²θ) never exceeds the larger of the two orthogonal cases.
  5. **Unchanged.** Round posts and ring welds: a circular section or line
     has no corner, and the inclined-load ruling of 2026-10-03
     (loads-and-envelope.md) stands. The reaction sets, already "any
     horizontal direction". The rail checks: S6-14's inclined-load
     alternative for rectangular rails stays not chosen. Check 4b.
  6. **A printed assumption sentence for the skew case** is drafted by
     Claude on the calc branch for Micah's acceptance in the pull request
     (registry entry `ej.skew.case`). As built it prints in the skew
     case's lines in Checks 3, 5 and 7, not in the "Stated assumptions"
     list: that list prints word for word in every calc, round posts
     included, and S6-18 leaves round-post calcs unchanged. Whether it
     also joins the list is Micah's call in the pull request.
