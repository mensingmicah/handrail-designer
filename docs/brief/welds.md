# Brief: welds

Part of the product brief; index in docs/BRIEF.md. Method for the weld
checks (Checks 3 and 7 in checks.md).

## Weld checks

Weld checks (3 and 7) use the elastic method, treating the weld as a line.
The AISC 360-22 §J2.4 directional strength increase is allowed for fillet
welds, based on the angle between the weld force and the weld axis; its
limits on weld groups loaded at varying angles, and any Chapter K
restrictions for welds to HSS, are registry entries to verify, and the
increase is not assumed to apply everywhere (decided below, W2). Base
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
- **Directional strength increase.** (W2, Micah 2026-10-04.)
  - The AISC 360-22 §J2.4 increase, k_ds = 1.0 + 0.50 sin^1.5 θ, applies
    to fillet welds on round HSS (pipe included), including the post to
    baseplate weld (Check 7). θ is computed at the governing point and
    printed.
  - The round-HSS applicability is its own entry, drafted, citing a
    non-primary source: the Steel Tube Institute's "Directionality
    Increase for Fillet Welds to HSS" (Packer et al. testing). Its note
    says that applying the increase under base moment extends that
    test basis, which was axial tension: engineering judgement.
  - Exception: the rail to post weld (Check 3; the post end on the rail's
    underside, a branch-to-chord joint) uses k_ds = 1.0, per the Chapter K
    commentary on branch-to-chord connections, and because W1 already
    simplifies the saddle to a flat ring. An ej.* entry, drafted.
  - Rectangular and square HSS use k_ds = 1.0 (AISC 360-22 excludes the
    increase for rectangular HSS ends in tension; the wording is confirmed
    when that entry is drafted). Until a later slice drafts that rule, the
    weld code applies the increase only to round sections and stops with
    an error if any other section reaches it. The error names the
    section and says why: the directional increase rule for that section
    family has not been drafted.
- **Weld force method.** (W3, Micah 2026-10-04.) Weld as a line, elastic.
  For the ring, S_w = πD²/4 (in², a line property, so forces come out per
  inch of weld), with D the post's outside diameter. The shear is V/(πD),
  taken as uniform, and the components combine by vector sum at the
  governing point. No plastic distribution in v1. Micah expects θ = 90°
  at the extreme fiber of the base ring.
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
  - Baseplate side: shear rupture over t_p, 0.6·Fu·t_p/2.00, against the
    resultant weld force per inch. Accepted by Micah as checked and
    correct.
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
  shapes lookup and widens in slice 5. So Check 3 carries its own guard:
  if the rail or the post is not a round hollow section, the calc stops
  with an error naming the section and saying the rail-wall assumption
  has not been decided for it. Slices 5 and 6 decide (docs/ROADMAP.md):
  thin-wall custom round rails, and rectangular rails at β = 1, where
  the sidewall limit states can govern. (W7, Micah 2026-10-04.)
- **The post may not be wider than the rail.** The coped detail (the post
  end welded to the rail's underside) needs post OD ≤ rail OD; equal ODs
  are allowed. A post wider than the rail stops the calc at input
  validation, before any check runs. The error names both ODs, says the
  coped post to rail underside detail requires post OD ≤ rail OD, and
  says to check the inputs. A rail welded to the side of a wider post,
  or a cap-plate detail, is a different connection and is out of v1
  (docs/ROADMAP.md, slices 5 and 6). (W8, Micah 2026-10-08.)
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
