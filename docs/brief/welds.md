# Brief: welds

Part of the product brief; index in docs/BRIEF.md. Method for the weld
checks (Checks 3 and 7 in checks.md).

## Weld checks

Weld checks (3 and 7) use the elastic method, treating the weld as a line.
The AISC 360-22 §J2.4 directional strength increase, based on the angle
between the weld force and the weld axis, is not applied unless the
engineer elects it, and only at the post to baseplate weld (decided below,
W2, as revised 2026-10-10); its limits on weld groups loaded at varying
angles, and any Chapter K restrictions for welds to HSS, are registry
entries to verify. Base
metal: per inch of weld, weld shear strength on the throat is compared with
the base metal at the fusion face of each connected part (post wall and
rail, or post wall and baseplate), with the limit state following the
direction of the force there (W5, W6); the lower governs. The minimum
fillet size is a pass/fail line; there is no maximum size check (W11).
The rail to post weld length is the post perimeter, conservative against the true
saddle length. The post to baseplate weld moment arm is h minus the
baseplate thickness.

## Engineering decisions already made

Decided in planning slice 3 (docs/plans/slice-3.md); W numbers are that
plan's decision numbers, kept for the record.

- **Check 3 weld model and eccentricity.** The rail to post weld is
  modeled as a flat ring with the post's perimeter, lying in the plane of
  the rail's underside. The eccentricity is e = half the rail's depth:
  D_rail/2 for round rails, d/2 for rectangular rails when they arrive.
  The horizontal load V at the rail centerline gives M = V·e at the ring.
  This is conservative: the true weld follows the saddle curve of the
  cope, whose centroid for equal diameters is 2R/π below the rail
  centerline (0.637R, against R here). It is a stated assumption, printed
  with the others; its text goes into the "Stated assumptions" list in
  output.md on the slice 3 branch, in the same commit that prints it,
  because a test holds the printed list to that list word for word. (W1,
  Micah 2026-10-04.)
  > Proposed text: "The rail to post weld is modeled as a flat ring of the
  > post's perimeter at the underside of the rail, with eccentricity e =
  > half the rail depth from the rail centerline; this is conservative
  > against the saddle centroid (2R/π for equal round diameters). It is
  > modeled as a fillet of the entered size all around, although at
  > equal diameters the sides of the saddle form a flare-bevel joint."

  The fillet model all around is kept at equal diameters (W9, Micah
  2026-10-08). There the post and rail walls are tangent at the sides of
  the saddle, so 0.707w overstates the throat over a short length. Under
  transverse load those points are at the ring's neutral axis and carry
  shear only, and Check 3 runs far below 1.0, so this cannot flip a
  result. Not chosen: a flare-bevel effective throat (Table J2.2), or
  requiring rail OD > post OD, which would refuse the most common detail.

  Guard loads act through the rail centerline, as in every check. Two
  effects of a load applied at the rail's surface are neglected: torsion
  on the Check 3 ring, and the larger eccentricity to the weld plane.
  Engineering judgement: Check 3 ratios are far below 1.0 for pipe on
  pipe. (Micah, 2026-10-08, ruling on the case 4 independent calc.) To
  revisit for rectangular rails (docs/ROADMAP.md, slices 5 and 6).
- **Directional strength increase: the engineer's election at the post to
  baseplate weld, off by default.** (W2, Micah 2026-10-04; revised by
  Micah 2026-10-10, which replaces the automatic rule.)
  - ~~The AISC 360-22 §J2.4 increase, k_ds = 1.0 + 0.50 sin^1.5 θ, applies
    to fillet welds on round HSS (pipe included), including the post to
    baseplate weld (Check 7).~~ Superseded: the increase is no longer
    automatic anywhere.
  - The post to baseplate weld (Check 7) has an input,
    `directional_increase` under `[welds]`: true or false, false when left
    out (inputs.md).
    - False, the default: k_ds = 1.0. The calc prints that as one line,
      citing AISC 360-22 §J2.4(a)(3), the value for all conditions the
      section does not name.
    - True: k_ds per AISC 360-22 Eq. J2-5, as before the revision, with θ
      computed at the governing point and printed. A line under it states
      that the increase is applied at the engineer's election, and cites
      the 360-22 equation and the Steel Tube Institute's round HSS testing
      as its basis.
    - Either way the input is echoed on the dimensions page, with the weld
      sizes.
  - Test cases (Micah, 2026-10-10). Cases 4, 5 and 7 and the example elect
    the increase and print as before. Cases 1 to 3 and 6 stay at the
    default, k_ds = 1.0, so their Check 7 ratios are 1.5 times what the
    automatic rule gave, and Check 7 reads NG in the printed calcs of
    cases 1 and 2 (0.92 to 1.38). That is accepted: no case records a
    Check 7 value that depends on it, and the key keeps the name
    `directional_increase`.
  - Why it is an election (Micah, 2026-10-10). AISC 360-22 handles strain
    compatibility explicitly only for in-plane eccentric weld groups (the
    instantaneous center method) and for concentric groups mixing
    longitudinal and transverse welds. A round base weld under
    out-of-plane bending has no code procedure, and taking the increase
    rests on HSS research and on the elastic method being a first-failure
    check. That is engineering judgement, so the engineer elects it.
  - Both provisions as read in the 360-22 text (Claude, 2026-10-10;
    paraphrased, page numbers from the PDF):
    - §J2.4(a), page 16.1-130. Fillet weld strength is Eq. J2-4, nominal
      weld stress times effective area times k_ds. k_ds takes Eq. J2-5 for
      fillet welds where strain compatibility of the various weld elements
      is considered (condition 1), 1.0 for fillet welds to the ends of
      rectangular HSS loaded in tension (condition 2), and 1.0 for all
      other conditions (condition 3).
    - The instantaneous center method: a User Note to §J2.4(a), page
      16.1-130, names it as a valid way to find the strength of a weld
      group with elements in various directions, one that considers strain
      compatibility. The Specification's own text does not say "in-plane"
      or "eccentric"; its Commentary (page 16.1-489) sends the reader to
      the AISC Manual for the method, which was not read here.
    - Concentric groups of longitudinal and transverse welds: §J2.4(b),
      page 16.1-132, Eq. J2-6, for a concentrically loaded fillet weld
      group of uniform leg size.
    - One more place, not in the two above: a second User Note to
      §J2.4(a), page 16.1-130, says strain compatibility is satisfied for
      a linear weld group (every element in one line or parallel) of
      uniform leg size, connecting elements of uniform stiffness and
      loaded through its center of gravity, so the increase may be used
      there. A ring is not a linear group, so this does not reach the base
      weld, and the reasoning stands.
    - The Commentary on §J2.4, pages 16.1-489 and 16.1-490, records the
      research behind the round HSS basis: fillet welds joining the end of
      an HSS in axial tension to a rigid plate. Numerical work gave round
      HSS a reliability index of 3.6 against the target of 4.0, and on that
      basis welds to the ends of tension-loaded round HSS were left out of
      the rule that sets k_ds to 1.0 for rectangular HSS.
  - The round-HSS basis is its own entry (`ej.weld.directional_round_hss`),
    drafted, citing a non-primary source: the Steel Tube Institute's
    "Directionality Increase for Fillet Welds to HSS" (Packer et al.
    testing). Its value is the election line the calc prints. Its note
    says that applying the increase under base moment extends that test
    basis, which was axial tension: engineering judgement.
  - The rail to post weld (Check 3; the post end on the rail's underside, a
    branch-to-chord joint) uses k_ds = 1.0 whatever is elected, per the
    Chapter K commentary on branch-to-chord connections, and because W1
    already simplifies the saddle to a flat ring. An ej.* entry, drafted.
    The same holds for the intermediate rail to post weld (Check 4b).
  - Rectangular and square HSS use k_ds = 1.0 (AISC 360-22 §J2.4(a)
    condition 2, for rectangular HSS ends in tension; the wording is
    confirmed when that entry is drafted). Until a later slice drafts that
    rule, the Check 7 weld stops with an error if a section that is not
    round hollow reaches it, whether or not the increase is elected. The
    error names the section and says why: the directional increase rule
    for that section family has not been drafted.
- **Weld force method.** (W3, Micah 2026-10-04.) Weld as a line, elastic.
  For the ring, S_w = πD²/4 (in², a line property, so forces come out per
  inch of weld), with D the post's outside diameter. The shear is V/(πD),
  taken as uniform, and the components combine by vector sum at the
  governing point. No plastic distribution in v1. Micah expects θ = 90°
  at the extreme fiber of the base ring.
- **Effective throat.** (Micah, 2026-10-09.) Every weld check (Checks 3,
  4b and 7) uses t_e = 0.707w for its equal-leg fillets, the form the calc
  prints on its AISC 360-22 §J2.2a line (registry
  `aisc360.J2.2a.throat.coeff`). Independent calcs use the same form, not
  w/√2 or another rounding, so the 0.5% comparison tests the method rather
  than the coefficient's last digit. No values change.
- **Fusion face thickness.** The rail and the post use the published
  design wall t_des (0.135 in for Pipe1-1/2STD, against 0.145 nominal),
  consistent with section properties used as published (checks.md). The
  baseplate uses t_p as entered. (W4, Micah 2026-10-04.)
- **Base metal follows the direction of the force at each fusion face.**
  This refines the single shear-rupture rule in "Weld checks" above.
  (W5, Micah 2026-10-04.)
  - Rail side, in-plane force (the horizontal load along the rail's
    underside): shear rupture only, 0.6·Fu·t/2.00 per §J4.2(b), citing
    the AISC Manual Part 9 convention for base metal at welds (its
    one-sided t_min = 3.09D/Fu comes from shear rupture). Shear yielding,
    §J4.2(a), is a limit state of an element's gross shear area, not of a
    fusion face, and is not checked here. Drafted entry. (W6, Micah
    2026-10-04.) The in-plane demand is V/(πD) only, because the normal
    components go to the chord-wall question (W7).
  - Rail side, force normal to the rail wall (vertical, upward, and the
    V·e moment): a chord-wall limit state (Chapter K, round T-connection,
    β = 1.0), not weld base metal. Not part of Check 3, and not checked
    in v1 (W7, below).
  - Post side of Check 7: the wall carries the weld force as stress along
    the post axis (§J4.1), the same demand as Check 5 at the same section.
    No separate number; a printed line says the post wall at the weld is
    covered by Check 5. The same applies to the post side of Check 3: the
    top of the post sees the same V and much less moment than the base,
    and member shear is not checked (a stated assumption).
  - That coverage holds only while yielding governs over rupture,
    Fu/Ω_t,rupture ≥ Fy/Ω_b, that is Fu/2.00 ≥ Fy/1.67 or Fu/Fy ≥ 1.20
    (the slice 2 tensile-rupture argument). A53 Gr B (1.71), A500 Gr C
    round (1.35) and A1085 (1.30) meet it. A code guard stops the calc,
    naming the grade and the ratio, for a post grade that does not, so
    the printed line cannot become false.
  - The elastic weld-line stress in the post wall at the base can exceed
    Fy/Ω while Check 5 passes (case 7: M/S = 28.1 ksi against Fy/1.67 =
    27.5 ksi, Check 5 = 0.77 on Mp). This is accepted. The wall at the
    base is the member section, and §F8.1 permits Mp for a compact round
    section; Check 5 is the code check for it. The weld is analyzed
    elastically because weld metal is the less ductile element, which does
    not apply to the base metal of a compact section. A noncompact section
    is checked by Eq. F8-2 on S. (Micah, 2026-10-10, ruling on the case 7
    independent calc; no change to the calc.)
  - Baseplate side: shear rupture over t_p, 0.6·Fu·t_p/2.00, against the
    resultant weld force per inch. Accepted by Micah as checked and
    correct.
  - No separate fusion-face (leg area) check on the baseplate. Base metal
    is checked per §J4 on the connected part, and the shear rupture
    through t_p above is that check. (Micah, 2026-10-08, ruling on the case
    4 independent calc.) To confirm at the release review (#18), against
    AISC 360-22 Table J2.5 and its footnotes: under a leg-area check, case
    4's Check 7 would be 1.18, NG.
- **Rail wall chord limit states are not checked.** The force normal to
  the rail wall at the post (the vertical and upward loads and the V·e
  moment) is a chord-wall limit state of a round T-connection (AISC
  360-22 Chapter K, β = 1.0 for equal diameters), not weld base metal,
  and v1 does not check it: connection design is out of scope
  (scope.md). From memory, unverified, the margin for pipe on pipe is
  about 20× (chord plastification ratio about 0.04 for case 2). A stated
  assumption, added to output.md's list on the slice 3 branch with W1:
  > "Local strength of the rail wall at the post (AISC 360-22 Chapter K
  > chord limit states) is not checked."

  The assumption is written for a round hollow rail on a round hollow
  post. Today only AISC pipe can be entered, but that limit lives in the
  shapes lookup and widens in slice 5. So the tool carries its own
  guard, in input validation (`validate()`, which runs before any check):
  if the rail or the post is not a round hollow section, the calc stops
  with an error naming the section and saying the rail-wall assumption
  has not been decided for it. `compute()` skips validation, and exists
  only as the entry point tests use to reach the checks past it (slice
  3 plan, T1). Slices 5 and 6 decide (docs/ROADMAP.md):
  thin-wall custom round rails, and rectangular rails at β = 1, where
  the sidewall limit states can govern. (W7, Micah 2026-10-04.)
  Decided for slice 5, and W7 retired from slice 6: S5-3, "Hollow round
  sections (slice 5)" below.
- **The post may not be wider than the rail.** The coped detail (the post
  end welded to the rail's underside) needs post OD ≤ rail OD; equal ODs
  are allowed. A post wider than the rail stops the calc at input
  validation, before any check runs. The error names both ODs, says the
  coped post to rail underside detail requires post OD ≤ rail OD, and
  says to check the inputs. A rail welded to the side of a wider post,
  or a cap-plate detail, is a different connection and is out of v1
  (docs/ROADMAP.md, slices 5 and 6). (W8, Micah 2026-10-08.) ODs within
  0.01 in are treated as equal (S5-4, below).
- **No bearing credit; the weld carries everything.** This holds at the
  cope (Check 3, as above) and at the baseplate (Check 7). The tool
  evaluates both extreme fibers of the ring and reports the larger,
  naming it. In the horizontal cases dead-load compression adds to
  bending on the compression side, so that side governs; θ = 90° at both
  extreme fibers. (W10, Micah 2026-10-08.) The envelope for both welds:

  | Case | Check 3 (e = D_rail/2) | Check 7 (moment arm h − t_p) |
  | --- | --- | --- |
  | Downward | D + L axial, uniform | D + L axial, uniform |
  | Outward, inward | V = L; M = V·e; D axial | V = L; M = V·(h − t_p); D axial |
  | Longitudinal | as transverse | as transverse |
  | Upward | 1.0L − 0.6D tension | 1.0L − 0.6D tension |

  D in Check 3 is the rail's dead load over the span, w_D,rail·s; D in
  Check 7 is D at the post (loads-and-envelope.md). The combinations are
  those of Check 5: ASCE 7-22 ASD D + L, and 0.6D + 1.0L for upward
  (engineering judgement). Longitudinal equals transverse for the ring
  but is listed, as in Check 5. Upward shows "no net tension;
  compression covered by downward" when 0.6D ≥ L.

  The five orthogonal direction cases stand for both welds; no inclined
  guard load is added. In Check 3 an inclined load raises the ratio by
  under 10%, on a ratio that stays far below 1.0 for pipe on pipe, because
  the demand is V·e with e = D_rail/2. In Check 7 its effect is
  negligible. Engineering judgement (Micah, 2026-10-08, ruling on the case
  4 independent calc). To revisit for rectangular rails (docs/ROADMAP.md,
  slices 5 and 6).
- **Fillet size limits.** (W11, Micah 2026-10-08.) The minimum size is a
  pass/fail line: AISC 360-22 Table J2.4, on the thinner part joined (1/8
  in for every v1 pipe wall, all ≤ 1/4 in). There is no maximum size
  check and no warning for an oversized weld. The §J2.2b(b) maximum
  applies along edges of material, and these are T-joints, so the calc
  prints one line saying it does not apply. Applied anyway it would cap a
  Pipe1-1/2STD post at about 1/8 in, which fails case 2's Check 7 even
  with k_ds = 1.5 (about 1.05 under the concentrated load, about 1.8
  under the distributed load, w·s = 350 lb). Strength stays capped by the weld metal
  line at the size entered, the rail and baseplate base metal lines, and
  Check 5 for the post wall (W5).
  - The Table J2.4 lookup uses the nominal wall thickness t_nom for pipe
    and HSS walls; the baseplate uses t_p as entered. The minimum size is
    a heat-input and cooling-rate rule tied to the physical thickness, not
    a strength provision, so the design wall t_des (W4) stays with the
    fusion-face strength lines only. It is also the stricter choice: a
    wall that straddles a row limit gets the larger minimum (Pipe5STD:
    t_nom = 0.258 in gives 3/16 in, where t_des = 0.241 in would give
    1/8 in). (Micah, 2026-10-08.)
- **Material values used by the welds.** FEXX = 70 ksi (E70XX); Fu for
  A53 Gr B (AISC Manual Table 2-4) for the rail fusion face; Fu for A36
  (Table 2-5) for the baseplate fusion face. The baseplate's Fy is not
  used in v1. D12 excludes baseplate thickness and bending, a different
  limit state from the base metal line at the weld's fusion face, which
  is checked. (W12, Micah 2026-10-08; inputs in inputs.md.)

## Intermediate rail weld to post (Check 4b)

Decided in planning slice 4 (docs/plans/slice-4.md); S4 numbers are that
plan's decision numbers.

- **A weld check for the intermediate rail, treated like Check 3.**
  (S4-8, Micah 2026-10-08.) A scope addition Micah made deliberately:
  until now the intermediate rail's connection to the post was a stated
  assumption, not checked. It prints inside Check 4: Check 4a is the
  member (component-load bending and deflection) and Check 4b is the
  weld, each with its own summary row, so the seven checks and their
  order stay as they are.
  - **Same as the top rail** (S4-1): the intermediate rail uses the top
    rail's section and the top rail's rail to post weld size. Check 4b
    prints "Intermediate rail weld: controlled by Check 3 by observation:
    same section (ring ≥ Check 3's, since post OD ≤ rail OD per W8), same
    weld size, weld reaction R = [value] ≤ P = [value], post wall
    t_des,post = [value] ≥ rail wall t_des,rail = [value]." R is the larger
    of the two cases in S4-9. Guard: if R > P, the full check runs
    instead. (Wording and guard amended by S4-9, Micah 2026-10-09.)
    Second guard (Micah, 2026-10-09, PR #20 review): the observation also
    needs t_des,post ≥ t_des,rail. The base metal line checks the chord's
    wall, the rail in Check 3 and the post in Check 4b; with equal ODs and a
    thinner post wall (a Pipe2XS rail on a Pipe2STD post), Check 4b's
    shear-rupture ratio could exceed Check 3's by about t_rail/t_post, so
    "controlled by Check 3" would not hold. If either guard fails, the full
    check runs, printing which guard failed. The observation sentence
    prints both wall thicknesses beside R ≤ P (Micah, 2026-10-09).
  - **Own section:** a required weld size input for the intermediate rail
    to post weld. The Check 3 method runs on the intermediate rail's ring
    (its perimeter, coped to the side of the post): weld metal with
    k_ds = 1.0 (branch-to-chord, as W2), base metal, the Table J2.4
    minimum size (W11), and the same stated assumptions (the W1/W9 ring
    model and the W7 chord wall).
  - **None:** Check 4b prints "none" with Check 4a.
  - Base metal and the chord wall: S4-12, below.
  - The stated assumption "The intermediate rail's connection to the
    post, and the component load's effect on the post, are not checked."
    (output.md) loses its first half. Proposed text: "The component
    load's effect on the post is not checked." output.md changes on the
    slice 4 branch in the same commit that prints it, because a test
    holds the printed list to output.md word for word.
- **Check 4b load and eccentricity.** (S4-9, Micah 2026-10-09.)
  - The component load is placed adjacent to the post, so the weld at
    that end takes the full P_c. (This is the worst position for the end
    reaction; the slice 4 interview's first proposal, P_c/2 from a
    midspan load, was unconservative by a factor of 2.) The dead-load
    reaction is R_D = w_D,int·L/2. ASD D + L, the component load as L.
  - Two cases (S4-10, checks.md). Horizontal: R = √(P_c² + R_D²), the
    two reactions in the ring's plane at right angles. Downward:
    R = R_D + P_c, same direction.
  - ~~Eccentricity e = D_post/2, from the post centerline (where the
    center-to-center span puts the support) to the post face; M = R·e,
    out of the ring's plane, about the axis perpendicular to R. For the
    round ring f_b = R·e/S_w and f_v = R/(πD_int), combined at the
    governing point (W3, W10).~~ Superseded: Check 4b is a simple shear
    connection, e = 0, no end moment (below, Micah 2026-10-09).
  - The load acts through the intermediate rail's centerline, which
    passes through the ring's centroid: no torsion (the Check 3
    centerline ruling).
- **The intermediate rail may not be wider than the post.** (S4-11,
  Micah 2026-10-09.) The intermediate rail's end is coped to the side of
  the post, and a branch cannot be coped to a narrower chord, so
  D_int ≤ D_post; equal ODs are allowed. With W8 (D_post ≤ D_rail), the
  same-as-top state is buildable only when D_rail = D_post.
  - `validate()` stops the calc, next to the W8 stop, in both the
    same-as-top and own-section states. The message names both ODs and
    says to uncheck `same_as_top_rail` and enter a section no wider than
    the post.
  - At equal ODs the fillet model is kept all around, as W9. It cannot
    flip a result: with the simple shear connection (below) the shear is
    taken as uniform around the ring, and the check runs near 0.01 for
    pipe.
  - A printed stated assumption covers the joint (output.md; text
    revised for the simple shear connection, Micah 2026-10-09): "The
    intermediate rail to post weld is modeled as a flat ring of the
    intermediate rail's perimeter at the post face, a simple shear
    connection consistent with the simple-span intermediate rail: the end
    reaction acts at the weld with no end moment. It is modeled as a
    fillet of the entered size all around, although at equal diameters
    the sides of the saddle form a flare-bevel joint."
- **Base metal at Check 4b: the roles of Check 3 reversed.** (S4-12,
  Micah 2026-10-09; revised the same day by the simple shear connection,
  below.) The intermediate rail is the branch (coped); the post wall is
  the chord. Both Check 4b load cases lie in the ring's plane, tangent
  to the post wall.
  - Chord side (post wall), in-plane force: shear rupture only,
    0.6·Fu·t_des,post/2.00 against f_v = R/(πD_int), as W6.
  - Chord side: the Chapter K chord-wall limit states on the post are
    not checked. The W7 stated assumption is extended, on the slice 4
    branch in the commit that prints it, to: "Local strength of the rail
    wall at the post, and of the post wall at the intermediate rail (AISC
    360-22 Chapter K chord limit states), is not checked." The W7
    non-round stop covers the intermediate rail. (The printed line no
    longer names a normal force from R·e: there is no end moment.)
  - Branch side (intermediate rail wall), in-plane force: shear rupture,
    0.6·Fu·t_des,int/2.00 against the same f_v, Fu of the intermediate
    rail's grade. Check 4b prints both base metal lines, post wall and
    intermediate rail wall, and which governs: the lower allowable, a tie
    going to the post wall, the chord, as Check 3 names its chord (tie
    rule confirmed by Micah, 2026-10-09). The check's base metal ratio is the governing
    wall's. This is the general rule above (the fusion face of each
    connected part, the lower governs) applied to Check 4b. (Micah,
    2026-10-09, ruling on open question 9a of the case 5 independent
    calc: the intermediate rail wall can be the thinner part, as in case
    5, Pipe1-1/4STD t_des = 0.130 in against the Pipe2STD post's 0.143
    in.) It replaces the line "Intermediate rail wall at the weld: shear
    only, member shear not checked (stated assumption).", which had
    itself replaced the argument that the end moment R·e is no more than
    the member check's midspan moment whenever L ≥ 2·D_post; with no end
    moment that argument is moot, and the `validate()` stop for
    L < 2·D_post was removed with it.
  - The same-as-top observation still holds with the branch line added:
    the intermediate rail is then the top rail's section and grade, with
    D_int = D_rail ≥ D_post (W8), so its f_v = R/(πD_rail) ≤ P/(πD_post),
    Check 3's in-plane shear, on the same wall Check 3 checks as its chord.
    The post wall line is the one the t_des,post ≥ t_des,rail guard
    protects.
  - W5's Fu/Fy ≥ 1.20 guard on the intermediate rail's grade is dropped
    (Micah, 2026-10-09): it protected only the removed branch-wall
    argument. The guard on the post grade stays (W5).
- **Check 4b is a simple shear connection.** (Micah, 2026-10-09,
  revising S4-9 and S4-12.) Consistent with Check 4a's simple-span
  member model, the reaction R acts at the weld: e = 0, no end moment.
  Check 4b prints "Simple shear connection consistent with the
  simple-span member assumption; no end moment at the weld." It keeps the
  weld metal line with f_v = R/(πD_int) (the resultant per inch is f_v),
  the base metal lines (post wall and, by the ruling above, intermediate
  rail wall), the Table J2.4 minimum size and the chord-wall stated
  assumption. Rotational restraint of the welded joint is not modeled
  (Micah, 2026-10-09, ruling on open question 9b of the case 5
  independent calc: keep the simple shear connection, no change). R is unchanged (S4-9): the component load
  adjacent to the post with the dead-load end reaction, horizontal by
  vector sum and downward by sum. The same-as-top observation and its
  two guards (R ≤ P; t_des,post ≥ t_des,rail) are unchanged.

## Hollow round sections (slice 5)

Decided in planning slice 5 (docs/plans/slice-5.md); S5 numbers are that
plan's decision numbers.

- **W7 is kept for slice 5, with a stop at chord D/t > 50.** (S5-3, Micah
  2026-10-09.) The stated assumption that the Chapter K chord limit states
  are not checked stays for every round hollow chord slice 5 adds (round
  HSS and custom round tubes), with one new guard. The calc stops when a
  chord's D/t exceeds 50, the AISC 360-22 Chapter K limit of applicability
  for the chord of a round T-connection. The limit is a registry entry,
  drafted, its table number confirmed when it is drafted.
  - The chord is the top rail in Check 3, and the post in Check 4b
    whenever there is an intermediate rail (same as the top rail, or its
    own section). D/t is the value the section's classification uses
    (design wall).
  - The stop is in input validation (`validate()`), beside W7's
    non-round stop, and reads like the slender-section stop: it names the
    member, its D/t, the limit and W7.
  - The supporting argument (Micah, 2026-10-09). The chord wall is not
    what limits a thin rail: at a 6 ft span the rail's own bending ratio
    (Check 1) runs about 3 to 4 times the chord plastification ratio, so
    Check 1 fails long before the chord wall would. The margin narrows on
    a short span with the concentrated load at the post: the rail's
    moment falls with the span while the load delivered to the chord wall
    does not.
  - Planning arithmetic behind it (Claude, 2026-10-09; order of magnitude
    only, from memory of the Chapter K round T-connection equations,
    unverified, not test values): chord plastification strength goes with
    t². With β = 1, Fy = 46 ksi and w·s = 300 lb on a 6 ft span, the
    axial and out-of-plane-moment ratios are each about 0.03 to 0.04 for
    Pipe1-1/2STD (D/t = 14.1), about 0.12 to 0.13 for a 2.375 in tube at
    D/t = 46 (Check 1 about 0.5), and about 0.21 to 0.24 for a 1.900 in
    tube at D/t = 50 (Check 1 about 1.0). At D/t = 100 they would be
    about 0.7 to 0.8, with no code equation applicable.
  - The printed assumption gains a clause. Proposed text, to be accepted
    in the slice 5 pull request and changed in output.md's list in the
    commit that prints it (a test holds the printed list to output.md
    word for word):
    > "Local strength of the rail wall at the post, and of the post wall
    > at the intermediate rail (AISC 360-22 Chapter K chord limit
    > states), is not checked; the chord's D/t is limited to 50, the
    > Chapter K limit of applicability."
  - Cost, accepted: the noncompact test case for Eq. F8-2 (#3) has to sit
    in λp < D/t ≤ 50 (44.1 to 50 at Fy = 46 ksi), and a noncompact A53
    Gr B rail (λp = 58) cannot be run.
- **From slice 6 the Chapter K chord limit states are checked, not
  assumed.** (S5-3, Micah 2026-10-09; a scope addition he made
  deliberately, scope.md.) For round and rectangular chords, built
  together in slice 6: the rail wall in Check 3 and the post wall in Check
  4b. W7, its stated assumption and its non-round stop are retired when
  that lands. Slice 6's plan settles which limit states, the interaction,
  where the lines print, and what becomes of the D/t ≤ 50 stop (a limit
  of applicability still applies to a check made under Chapter K).
- **ODs within 0.01 in are equal in the width comparisons.** (S5-4,
  Micah 2026-10-09.) W8 (post OD ≤ rail OD) and S4-11 (intermediate rail
  OD ≤ post OD) treat two outside diameters within 0.01 in of each other
  as equal, so neither stop fires. The reason is the database's rounding
  of a round HSS's OD (checks.md, S5-4): a pipe and a round HSS of the
  same nominal size are the same physical diameter, but read 2.375 and
  2.38 in, and without the tolerance an HSS2.375 post under a Pipe2STD
  rail would hit a misleading "wider than" stop. Mixed pipe and HSS of
  one size is rare in practice.
  - The tolerance is an engineering-judgement registry entry (source
    "engineer"). It changes only the two comparisons. Every calc line
    still uses each member's own published OD.
  - It applies to every pair of round sections, custom tubes included.
  - Known limit: the rounding is at most 0.005 in for an OD below 10 in,
    which the tolerance covers. From HSS10.750 up the database's rounding
    reaches 0.05 in (10.8 in against Pipe10STD's 10.75 in), so a
    same-size pipe and HSS pair at 10.75 in or larger would still stop.
    No guard member is that large.
- **A post wider than the rail at all runs the full Check 4b.** (S5-11,
  Micah 2026-10-09.) The same-as-top observation for Check 4b (S4-8) says
  the intermediate rail's ring is at least Check 3's "since post OD ≤ rail
  OD per W8". Under the 0.01 in tolerance (S5-4) a post can be wider than
  the rail by up to that much (an HSS2.375 post, 2.38 in, under a Pipe2STD
  rail), and the sentence would be false by 0.2%. So the observation gets
  a third guard beside R ≤ P and t_des,post ≥ t_des,rail: if the post OD
  is greater than the rail OD by any amount, the full Check 4b runs
  instead, printing which guard failed. The tolerance still decides
  whether W8 stops the calc; it no longer decides whether the observation
  may be used.
- **The round weld rulings hold for every round hollow section slice 5
  adds.** (S5-12; Claude's, confirmed by Micah 2026-10-09.)
  - The weld envelope's five orthogonal direction cases and the ruling
    that guard loads act through the rail centerline (above) both rest on
    Check 3 running far below 1.0. Check 3's weld metal demand depends on
    the post OD, the rail OD and the weld size, not on either wall, so a
    thin-wall round rail does not change it. The rail-wall base metal
    line does thin with the wall, but its demand is the in-plane shear
    V/(πD) only (planning arithmetic: about 0.04 for a 0.051 in wall).
    Both rulings stand for round HSS and custom round tubes. Slice 6
    redoes them for rectangular rails.
  - W2's directional increase may be elected at Check 7 for every round
    hollow post, whatever its grade, custom round tubes included. (As
    confirmed on 2026-10-09 it applied automatically; since W2's revision
    of 2026-10-10 it is the engineer's election, off by default.) The
    entry's test basis is cold-formed round HSS; a hot-formed grade (A501,
    A618) extends it by the same engineering judgement the entry already
    records for base moment, and its note says so. Checks 3 and 4b keep
    k_ds = 1.0.
- **Thin material at a weld: a warning, not a stop.** (Micah, 2026-10-10;
  raised by case 6's independent calc, a 1/8 in fillet on a 0.055 in wall.)
  - When either part joined by a fillet weld is thinner than 1/8 in, the
    calc prints a warning at that weld: the joined material is below the
    AWS D1.1 thickness range, and the welding procedure is the engineer's
    responsibility (for example AWS D1.3, sheet steel).
  - The thickness compared is the one the Table J2.4 minimum size line
    reads (W11): the nominal wall t_nom for a rail or post, the baseplate
    thickness t_p as entered. A part at exactly 1/8 in is inside the range
    and prints nothing.
  - It prints at each weld that joins a thin part: Check 3 (top rail and
    post), Check 4b (intermediate rail and post) and Check 7 (post and
    baseplate). In Check 4b it prints in every state with an intermediate
    rail, the same-as-top observation included: the weld is made whether
    or not it is computed.
  - The rule is on the part's thickness, not on how it was entered, so
    three database sections trip it as well as thin custom tubes:
    Pipe1/2STD (0.109 in), Pipe3/4STD (0.113 in) and HSS1.900X0.120.
    (Confirmed by Micah, 2026-10-10: any part under 1/8 in nominal,
    database sections included.)
  - The check is still computed, and its ratio and verdict are unchanged.
    Nothing prints in the summary table.
  - The 1/8 in limit and the AWS D1.1 scope statement are registry
    entries, drafted from memory (`aws.d1_1.thickness_min`,
    `aws.d1_1.scope`); the warning's words are an engineering-judgement
    entry (`ej.weld.thin_material`). The limit is read at every weld, so
    every calc lists it under "Draft code values" while it is drafted.
    (Accepted by Micah, 2026-10-10, as with the chord D/t limit.)
  - Not covered by this warning: local effects of the concentrated guard
    load on a thin tube wall (issue #28, for slice 6).

## Hollow rectangular sections and the chord limit states (slice 6)

Decided in planning slice 6 (docs/plans/slice-6.md); S6 numbers are that
plan's decision numbers. Member rulings of the same slice are in
checks.md and inputs.md.

- **Slice 6 is one slice: rectangular sections and the Chapter K chord
  limit states together.** (S6-1, Micah 2026-10-10.) The roadmap's
  question of a split is answered: no split.
  - Why. The chord limit states will essentially never govern a
    realistic guard: the branch forces at both joints are tens to
    hundreds of pounds, against chord capacities in kips. A split would
    double the fixed cost of a slice (plan, independent calcs, code
    review, pull request, close) for a check that does not decide
    results.
  - Build order. Rectangular members first. Chapter K last, round chords
    before rectangular chords. Each of the three is a clean stopping
    point.
  - The chord checks print compactly. Per joint, one table: limit state,
    ratio, OK or NG. Full calc lines print for the governing limit state
    of the joint, always, whatever its ratio (amended by Micah the same
    day, so his release recompute traces to printed working), and for any
    other limit state whose ratio exceeds a threshold. The rest are table
    rows only. The threshold is 0.5 (Micah's suggestion, Claude's
    proposal; an engineering-judgement registry entry). This follows the
    slice 5 ruling to keep the package lean.
  - Review. Micah's slice review of the chord checks is a cursory read
    of that table. The release recompute rule is unchanged (ADR 0006,
    S5-2): the governing limit state of each case.
- **The post to baseplate weld of a rectangular post: pattern, weld line
  and directional rule.** (S6-6, Micah 2026-10-10.)
  - **Input.** `base_pattern` under `[welds]`: `"all around"`, `"faces
    parallel to rail"` or `"faces perpendicular to rail"`, the words B, N
    and the post's `long_side` use (S4-6, S6-2), so they also serve a
    square post. Required, with no default, for a rectangular or square
    post. A round post is welded all around: the key may be left out, and
    a face pair given for a round post stops. It is echoed on the
    dimensions page with the weld sizes. This settles "by the section's
    width or depth faces" (inputs.md).
  - **Weld line.** The elastic line method stays (W3), the line on the
    post's outside surface.
    - All around: the true rounded rectangle, straight runs on the flats
      and quarter-circle arcs at the corners on the outside radius of
      S6-3, 2·t_des.
    - A face pair: two parallel straight lines, each the flat width of
      its face (the outside dimension less 4·t_des), stopping at the
      tangent points.
    - All five direction cases run on either pattern (W10), the shear
      taken as uniform over the total weld length (W3).
  - **Directional increase.** k_ds = 1.0 for every rectangular post,
    printed citing AISC 360-22 §J2.4(a) condition (2), page 16.1-130, and
    the User Note to §K5, page 16.1-170 (where flexure puts the weld in
    tension, the factor cannot exceed 1.0 in fillet welds to the end of a
    rectangular HSS). `directional_increase = true` with a rectangular
    post stops as a conflicting input; it is never silently ignored.
    This settles W2's last bullet.
  - Why the rounded line. Planning arithmetic (Claude, 2026-10-10; not
    test values), HSS2×2×1/8 all around: S_w = 5.33 in² on a sharp-corner
    rectangle (b·d + d²/3), 4.90 in² on the rounded rectangle, 3.68 in²
    on the flats alone. Sharp corners are 9% unconservative and flats
    alone 25% conservative, on a check that often governs and gets no
    directional increase.
  - Not chosen: flats only for both patterns; sharp corners; a default
    of all around (a post welded on two faces, with the key forgotten,
    would be checked with about twice its weld).
  - Slice 7 reuses the key for a solid rectangular bar post, with sharp
    corners.
- **The post wall at a face-pair base weld is checked on its own lines;
  all around stays "covered by Check 5".** (S6-7, Micah 2026-10-10.)
  - Why. W5's line "post wall covered by Check 5" rests on the weld
    delivering force to the whole post section. With two faces welded
    and no bearing credit (W10), the base moment enters the post through
    two walls alone, and Check 5 on the full section does not describe
    them.
  - For a face pair, per inch of weld at the governing point, following
    the direction of the force as W5 does:
    - force along the post axis, against the wall per AISC 360-22 §J4.1:
      the lower of yielding, Fy·t_des/1.67, and rupture, Fu·t_des/2.00;
    - force along the face, against shear rupture, 0.6·Fu·t_des/2.00
      (§J4.2(b), as W6).
    - Each component has its own ratio; the larger is the post wall's.
      They are not combined.
  - **Compression side.** (Micah's addition.) The yielding limit applies
    to the wall on the compression side only if the welded wall is
    nonslender in compression: b/t ≤ 1.40√(E/Fy), AISC 360-22 Table
    B4.1a Case 6, walls of rectangular HSS, page 16.1-21. A slender
    welded wall stops, naming the post, its b/t and the limit. The limit
    is a drafted registry entry and the stop is tested.
    - Confirmed by Micah (2026-10-10): no separate stop. The post is already classified
      in compression before any check, and a slender wall is a hard stop
      there (`section.slender_in_compression`, stops.md; checks.md, "The
      post"). Slice 6 extends that stop to both walls of a rectangular
      post under the same Case 6 limit. So no post with a slender wall
      reaches Check 7, and this condition is met by the existing stop;
      the slice adds a test that a face-pair weld on such a post stops,
      rather than a second stop.
  - **Not combining the two components is a printed simplification,**
    not only a brief note. (Micah's addition.) Proposed text for the
    "Stated assumptions" list (output.md, changed on the calc branch in
    the commit that prints it): "At a post to baseplate weld on one pair
    of faces, the post wall is checked for the weld force along the post
    axis and for the force along the face separately; the two are not
    combined, the force along the face being small next to the other."
    The list prints word for word in every calc, so this is an intended
    change to every golden snapshot. The same sentence prints at the
    lines in Check 7.
  - All around, on a rectangular post as on a round one: "post wall
    covered by Check 5" (W5), with the Fu/Fy ≥ 1.20 guard on the post
    grade.
  - Planning arithmetic (Claude, 2026-10-10; not test values): an
    HSS2×2×1/8 post, 42 in, 200 lb at the top, welded on the faces
    parallel to the rail with 3/16 in fillets, at the drafted 46 and 58
    ksi. f ≈ 2.70 kip/in; weld metal 2.78 kip/in (0.97); post wall
    yielding 3.20 kip/in (0.84). Against shear rupture on the resultant,
    the alternative not chosen, 2.02 kip/in (1.34).
  - Slice 7 decides the same question for a solid bar post.
- **Rail to post welds at a rectangular chord use AISC 360-22 Table K5.1;
  the round ring model stands.** (S6-8, Micah 2026-10-10.) AISC 360-22
  §K5, page 16.1-168, had not been read into the brief before slice 6:
  the strength of a branch weld "shall be determined considering the
  nonuniformity of load transfer along the line of weld", with effective
  weld properties in Table K5.1 (rectangular HSS, page 16.1-171) and
  Table K5.2 (round HSS, page 16.1-173).
  - **Rectangular chord** (Check 3 with a rectangular rail, Check 4b with
    a rectangular post). The elastic weld-as-a-line method stays (W3),
    on Table K5.1's effective properties for T-connections under branch
    axial load or bending, at θ = 90°:
    - effective length le = 2·Hb + 2·Be (Eq. K5-5);
    - S_ip and S_op per Eqs. K5-6 and K5-7;
    - Be per Eq. K1-1 (page 16.1-159), and Be/2 not over Bb/4 when
      β > 0.85 (Table K5.1);
    - Hb and Bb are the branch's outside dimensions, as the equations are
      written: no rounded-corner correction.
    - Case mapping: the longitudinal case is in-plane bending, the
      transverse cases out-of-plane bending, the vertical cases branch
      axial load. Shear in the chord face is taken as uniform over le.
    - The components combine by vector sum at the governing point,
      against the fillet strength at Ω = 2.00 with k_ds = 1.0 (W2's
      branch rule), as for round.
  - **Equal widths.** The side welds then land on the chord's rounded
    corner and are flare-bevel welds (User Note to §K5, page 16.1-170).
    The fillet model all around is kept, a stated assumption, as W9 does
    for round; the assumption text is proposed on the branch.
  - **Round chord.** The existing ring model (W1, W3) stands as
    engineering judgement. Table K5.2 covers branch axial load only, with
    0.1 ≤ β ≤ 0.5; the tool's round joints are at or near β = 1 and loaded
    in bending, so it gives them no effective length. The ring model's
    registry entry gains a note that §K5 and Table K5.2 were read and do
    not reach this joint. No printed number changes.
  - Planning arithmetic (Claude, 2026-10-10; not test values), an
    HSS2×2×1/8 post under an HSS2×2×1/8 rail: Be = 0.5·Bb, le = 6 in
    against a full perimeter of 8 in, S_op 3% and S_ip 37% below the
    full-perimeter values; the Check 3 ratio stays near 0.02.
  - Not chosen: the full branch perimeter for rectangular chords too
    (it ignores a table that applies directly); sizing the weld to
    develop the branch wall, which §K5 accepts in place of the check.
  - Slice 7 decides this for a solid bar branch or chord.
- **Which families may meet at the rail to post joints, and the width
  rule.** (S6-9, Micah 2026-10-10.) The same table for the Check 3 joint
  (top rail as chord, post as branch) and the Check 4b joint (post as
  chord, intermediate rail as branch). "Round hollow" is AISC pipe, round
  HSS and custom round tube; "rectangular hollow" is rectangular and
  square HSS and custom rectangular tube. Solid bars stay "stop: slice
  7".

  | Chord \ Branch | Round hollow | Rectangular hollow |
  | --- | --- | --- |
  | Round hollow | allowed (slice 5); chord wall checked | allowed, mixed; chord wall not checked |
  | Rectangular hollow | allowed, mixed; chord wall not checked | allowed; chord wall checked |

  - **Mixed pairs are allowed** (a rectangular branch on a round chord, a
    round branch on a rectangular chord), at both joints. Claude had
    recommended stopping them; Micah's ruling: a square post under a pipe
    rail is a common detail and must run in v1.
  - **Weld at a mixed pair:** the W1 convention on the branch's own
    shape. A flat line of the branch's outline at the chord face: the
    rounded rectangle of S6-6 for a rectangular branch, the ring for a
    round branch. e = half the chord's depth in Check 3 (e = 0 in Check
    4b, the simple shear connection). k_ds = 1.0, elastic line method
    (W3). The saddle cope is ignored, conservatively, as in W1, and that
    is printed as a stated assumption. Table K5.1 (S6-8) is for a
    rectangular branch on a rectangular chord and is not used at a mixed
    pair.
  - **Chord wall at a mixed pair: not checked.** The pre-slice-6 stated
    assumption is kept for these pairs ("local strength of the rail wall
    at the post (AISC 360-22 Chapter K) is not checked", and its Check 4b
    counterpart), on the reasoning of S6-1: the branch forces are tens to
    hundreds of pounds against chord capacities in kips. So W7 is retired
    for same-family pairs only. AISC 360-22 has no provision for either
    mixed pair (Commentary to Chapter K, page 16.1-526); the Commentary's
    equivalent square branch of width π·Db/4 (page 16.1-538) is not used.
  - The chord's wall slenderness limit of applicability still applies at
    a mixed pair: D/t ≤ 50 for a round chord (S5-3), and the
    corresponding Chapter K limit for a rectangular chord, B/t and H/t ≤
    35 (AISC 360-22 §K1.3, page 16.1-160; Table K4.2A, page 16.1-170).
  - **Width rule** (W8 and S4-11 carried over): the branch's width across
    the chord face may not exceed the chord's width: Bb ≤ B for a
    rectangular chord, or ≤ D for a round chord; Db in place of Bb for a
    round branch. Equal widths are allowed. In Check 3 the branch width
    is the post's dimension perpendicular to the rail and the chord width
    the rail's horizontal dimension; in Check 4b, the intermediate rail's
    horizontal dimension against the post's dimension perpendicular to
    the rail.
  - The comparison is exact. The 0.01 in tolerance of S5-4 applies only
    where both members are round, as now. The Shapes Database stores Ht
    and B of every rectangular HSS exactly as the designation reads (525
    rows checked, Claude 2026-10-10).
  - The same-as-top state is buildable only when those two widths are
    equal, as for round (S4-11).
  - Proposed assumption texts (the saddle cope at a mixed pair; the chord
    wall at a mixed pair) are Claude's to draft on the branch and Micah's
    to accept in the pull request; output.md changes in the commit that
    prints them.

