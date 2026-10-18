# Independent calc: test case 9

Mixed pair: HSS2X2X1/8 post under a Pipe2STD top rail, HSS2X1X1/8
intermediate rail (long side horizontal), base weld all around.

- **Case:** tests/cases/case-09.toml (`covers`: post, check3, intermediate,
  check4a, check4b, check5, check6, check7, reactions; `recompute`: check5,
  check7)
- **Date:** 2026-10-17
- **Model:** claude-opus-5-5
- **Branch / commit:** slice-6 at 67a072a06601b4a6acdf216dca46df0565e6ffd7
  (equal to origin/slice-6, clean working tree, confirmed before reading)
- **Sources read, and nothing else:**
  - the case inputs, value tables stripped, by the skill's command;
  - docs/BRIEF.md and all of docs/brief/ (scope, inputs,
    loads-and-envelope, checks, welds, stops, output, verification);
  - CONTEXT.md;
  - docs/plans/slice-6.md, the current slice plan (decisions only; its
    planning arithmetic was not used as a value);
  - the verified registry entries, by the skill's command;
  - the AISC Shapes Database v16.0 workbook rows for Pipe2STD, HSS2X2X1/8
    and HSS2X1X1/8, by the skill's command;
  - out/aisc-360-22.pdf (the Specification's text, extracted to plain text
    and searched) for §§E3, F1, F7, H1, J2.4 (Table J2.4), J4.2, K1
    (Eq. K1-1), K5, Tables K4.2A and K5.1, Tables B4.1a and B4.1b;
  - in step 7 only: the comment header and key names of
    tests/cases/independent/case-09.toml.

Source tags used on each line: **[V: id]** a verified registry entry;
**[own: memory]** my own reading from memory; **[own: PDF]** my own
reading of the 360-22 text in out/aisc-360-22.pdf; **[brief: id]** an
engineering decision of the brief or plan. Units: lb, in, ksi, lb-in,
lb/in of weld. Values are carried at full precision and printed to 4
significant figures.

## 1. Inputs

| Item | Value | Note |
| --- | --- | --- |
| Span L = s | 6'-0" = 72 in | tributary length for the post (stated assumption) |
| Post height h | 42 in | top of concrete to top rail centerline |
| Baseplate t_p | 1/2 in = 0.5 in | |
| h − t_p | 41.5 in | cantilever length, Check 6 length, Check 5 and 7 arm [brief: D4] |
| Baseplate B × N | 6 in (parallel to rail) × 8 in (perpendicular), A36 | |
| Top rail | Pipe2STD, A53 Gr B (default) | round chord at Check 3 |
| Post | HSS2X2X1/8, A500 Gr B (default) | square, no `long_side` (correct: square) |
| Intermediate rail | HSS2X1X1/8, own section, `long_side = "horizontal"`, A500 Gr B (default per S5-10: A53 Gr B is not on the rectangular HSS list) | |
| Welds | rail to post 1/8 in; intermediate rail to post 1/8 in; post to baseplate 3/16 in, all around; E70XX | `directional_increase` not given → false; a rectangular post takes k_ds = 1.0 regardless [brief: S6-6] |
| Guard loads | P = 200 lb [V: asce7.guard.concentrated]; w = 50 lb/ft [V: asce7.guard.uniform]; no exemption | defaults |
| Component load | P_c = 50 lb | ASCE 7-22 §4.5.1.2 [own: memory] |
| Deflection limits | rail L/120, post (h − t_p)/60, intermediate rail L/120; none bypassed | [V: ej.deflection.limit] |

Note on the inputs against the plan: slice-6.md T3 proposed `base_pattern =
"faces parallel to rail"` for this case and predicted Check 7 NG. The case
file has `"all around"`. The case inputs govern; S6-7's face-pair post
wall lines and plan open item 3 do not arise here.

**Materials** (all [own: memory] unless tagged):

| Member | Grade | Fy (ksi) | Fu (ksi) | Citation |
| --- | --- | --- | --- | --- |
| Top rail | A53 Gr B | 35 [V: material.A53_GrB.Fy] | 60 | AISC Manual 16th Ed. Table 2-4 |
| Post, intermediate rail | A500 Gr B, rectangular | 46 | 58 | AISC Manual 16th Ed. Table 2-4; ASTM A500/A500M-21 shaped (rectangular) values |
| Baseplate | A36 plate | (not used) | 58 | AISC Manual 16th Ed. Table 2-5 |
| Weld | E70XX | | F_EXX = 70 | AWS A5.1; AISC 360-22 Table J2.5 |

E = 29,000 ksi [V: material.steel.E].

Post-grade guard (W5, S5-13, S6-14 item 4): Fu/Fy = 58/46 = 1.261 ≥ 1.20,
so the post wall at both welds is covered by Check 5.

## 2. Limit states considered (step 3)

Listed from the code for every member and connection, not from the plan's
list.

**Post, HSS2X2X1/8, a cantilever fixed at the top of the baseplate.**

| Limit state | Code | Applies? |
| --- | --- | --- |
| Flexural buckling in compression | AISC 360-22 §E3 | Yes: Check 5, Lc = 2.1h [brief: D3] |
| Torsional / flexural-torsional buckling | §E4 | No: doubly symmetric closed section; torsional buckling of HSS does not govern over flexural buckling (J = 0.796 in⁴, same order as I) [own: memory] |
| Local buckling in compression | Table B4.1a Case 6, §E7 | Classified: nonslender, so §E7 not needed |
| Tensile yielding | §D2(a) | Yes, upward case [brief: "The post"] |
| Tensile rupture | §D2(b) | Not checked: all-around weld, U = 1.0, and Fu/Fy ≥ 1.20 [brief: S5-13] |
| Flexural yielding | §F7.1, Eq. F7-1 | Yes |
| Flange / web local buckling | §F7.2, §F7.3 | Classified compact; do not apply |
| Lateral-torsional buckling | §F7.4 | No: square section (User Note to §F7.4) [own: PDF] |
| Shear | §G4 | Not checked: stated assumption (output.md). Magnitude for the record: A_w = 2(Ht − 3t)t = 2(1.652)(0.116) = 0.3833 in²; V_n ≈ 0.6·46·0.3833 = 10.58 kips against V = 300 lb; negligible [own: memory] |
| Torsion | §H3 | No: every load acts through the rail and post centerlines [brief: W1, S6-14 item 1] |
| Combined axial and flexure | §H1.1, Eqs. H1-1a/b | Yes: one axis in the five orthogonal cases; **both axes in the skew case** (section 4, open question 1) |
| Second-order effects | Appendix 8 ratio αPr/Pe ≤ 0.05 | Yes, as a gate [brief: D1] |
| Lateral deflection | serviceability | Yes: Check 6 |
| Wall local strength at the base | §J10 | No: no concentrated transverse force on a flange; the weld delivers the force to the wall, covered by Check 5 [brief: W5] |

**Intermediate rail, HSS2X1X1/8, simple span L.** Flexure by §F7 about
each bent axis: yielding (F7-1), FLB and WLB (compact, do not apply), LTB
on the strong axis only (§F7.4; the horizontal case bends the strong axis
here), none on the weak axis (User Note). Shear not checked (assumption;
negligible at 56.6 lb). Deflection: yes. Torsion: none (load through the
centerline). **Not in the plan:** an inclined component load in the
downward-outward quadrant (OSHA 1910.29(b)(5)'s "any downward or outward
direction" reads as including it) would bend both axes; S6-16 item 3 says
Check 4a has no biaxial case. My estimate by H1-1b is 0.191 against the
downward case's 0.166; deflection (0.282) still governs Check 4a. Flagged
for Micah (open question 6); not computed as a case.

**Top rail, Pipe2STD.** Checks 1 and 2 are outside this case's `covers`
(the pipe rail is cases 1 to 5's). At the Check 3 joint it is the chord.

**Check 3 joint: post (rectangular branch) coped to the underside of the
round rail (chord), a mixed pair [brief: S6-9].**

| Limit state | Code | Applies? |
| --- | --- | --- |
| Fillet weld metal shear | §J2.4(a), Eq. J2-4, k_ds = 1.0 | Yes [brief: W2 branch rule] |
| Base metal, rail wall, in-plane force | §J4.2(b), Eq. J4-4 | Yes, horizontal cases only (in-plane V/L_w) [brief: W5, W6] |
| Base metal, post wall | §J4.1 | Covered by Check 5 [brief: W5, S6-16 item 6] |
| Minimum fillet size | Table J2.4 | Yes |
| Maximum fillet size | §J2.2b(b) | No: T-joint, not along an edge [brief: W11] |
| Chord wall local strength (plastification, punching) | Chapter K | Not checked at a mixed pair: stated assumption [brief: S6-9]; the chord's own limits of applicability are checked instead (below) |
| Chapter K limits, chord's own | §K1.3; Tables K3.1A/K4.1A for a round chord | Checked: D/t = 16.6 ≤ 50; Fy = 35 ≤ 52 ksi; Fy/Fu = 35/60 = 0.583 ≤ 0.8 [brief: S6-13]. All pass |
| Width rule | W8 extended | Post width across the rail 2.000 in ≤ rail OD 2.375 in: passes (exact comparison) [brief: S6-9] |
| Thin material warning | AWS D1.1 scope | Thinnest part t_nom = 0.125 in = 1/8 in: inside the range, no warning |

**Check 4b joint: intermediate rail (rectangular branch) coped to the post
side (rectangular chord).**

| Limit state | Code | Applies? |
| --- | --- | --- |
| Fillet weld metal on the effective length | §K5, Eq. K5-1; Table K5.1, Eq. K5-5 | Yes [brief: S6-8] |
| Base metal, post wall and intermediate rail wall | §J4.2(b) | Yes, both; the lower governs, a tie to the post wall [brief: S4-12] |
| Minimum fillet size | Table J2.4 | Yes |
| Chord limit states | Chapter K | No demand: simple shear connection, no axial force or moment into the post wall [brief: S6-11] |
| Chapter K applicability limits | | None at Check 4b [brief: S6-13] |
| Width rule | S4-11 extended | Intermediate rail horizontal dimension 2 in ≤ post dimension perpendicular to the rail 2 in: equal, allowed |
| Flare-bevel at equal widths | User Note to §K5 | β = 1: the side welds land on the post's corner radius; the fillet model is kept as a stated assumption [brief: S6-8] |

**Check 7 joint: post on the baseplate, all around.** Weld metal
(§J2.4(a), k_ds = 1.0 by §J2.4(a)(2) and the User Note to §K5, which I read
on page 16.1-170); base metal on the baseplate, shear rupture through t_p
against the resultant (§J4.2(b)) [brief: W5]; post wall covered by Check 5
(all around, Fu/Fy ≥ 1.20); Table J2.4 minimum size; baseplate bending and
anchorage out of scope. Table K5.1's "transverse plate" row is a plate
welded across an HSS face, not an HSS end on a plate: not applicable.

**Reactions:** reported, not checked (LRFD, 0.9D + 1.6L).

## 3. Loads and load path (step 4)

### Dead loads

| Symbol | Equation | Substituted | Result | Citation, source |
| --- | --- | --- | --- | --- |
| w_D,rail | tabulated W | Pipe2STD | 3.66 lb/ft | AISC Shapes Database v16.0 |
| D_rail | w_D,rail·s | 3.66 × 72/12 | 21.96 lb | [brief: D2] |
| w_D,int | tabulated W | HSS2X1X1/8 | 2.20 lb/ft | Shapes Database |
| D_int | w_D,int·L | 2.20 × 72/12 | 13.20 lb | [brief: loads-and-envelope, slice 4] |
| W_post | tabulated W | HSS2X2X1/8 | 3.05 lb/ft | Shapes Database |
| D_post | W·(h − t_p) | 3.05 × 41.5/12 | 10.55 lb | [brief: D2, D11] |
| P_D | D_rail + D_int + D_post | 21.96 + 13.20 + 10.548 | 45.71 lb | dead load at the post's critical section |
| ρ | steel density | 490/1728 | 0.2836 lb/in³ | AISC Manual (490 pcf) [own: memory] |
| W_bp | ρ·B·N·t_p | 0.28356 × 6 × 8 × 0.5 | 6.806 lb | [brief: S4-6]; reactions only |
| D (reactions) | P_D + W_bp | 45.708 + 6.806 | 52.51 lb | |

### Guard loads and where they act

- **Concentrated** P = 200 lb, at the top rail centerline, applied in each
  direction case. At the post it acts at the top: V = P (horizontal), or
  axial P (vertical), worst position at the post.
- **Distributed** w·s = 50 × 6 = 300 lb at the top of the post (the span
  is the tributary length). The two types are not concurrent; both run
  through every envelope. The distributed load exceeds P, so it governs
  every load-proportional ratio.
- **Component load** P_c = 50 lb on the intermediate rail only, not
  concurrent with the guard loads: at midspan for Check 4a, adjacent to the
  post for Check 4b, horizontal and downward [brief: S4-3, S4-9, S4-10].

### Direction cases and how each reaches the critical sections

| Case | Post (Checks 5, 7, at the top of the baseplate) | Check 3 weld (rail underside) | Combination |
| --- | --- | --- | --- |
| Downward | axial P_D + L, compression; M = 0 | axial D_rail + L, uniform | ASCE 7-22 §2.4.1 Comb. 2, D + L [V: asce7.combo.asd.D_plus_L] |
| Outward, inward | V = L at h − t_p: M = L·41.5 about the post axis parallel to the rail; axial P_D | V = L; M = L·e, e = D_rail/2; axial D_rail | D + L |
| Longitudinal | V = L along the rail: M = L·41.5 about the other post axis; axial P_D | V = L along the rail; M = L·e; axial D_rail | D + L |
| Upward | tension L − 0.6·P_D; M = 0 | tension L − 0.6·D_rail | 0.6D + 1.0L, engineering judgement [V: ej.combo.bending.upward] |
| Skew (S6-18, see open question 1) | horizontal L at plan angle φ from transverse: M_x = L·41.5·cos φ, M_y = L·41.5·sin φ; axial P_D | V = L at angle φ; M components L·e·cos φ and L·e·sin φ; axial D_rail | D + L |

Outward and inward are mirror images on a square post and a symmetric weld
line; longitudinal equals transverse because the post is square (I_x =
I_y, S_w,t = S_w,l). They are all listed so the envelope is explicit.
Upward: 0.6·P_D = 27.42 lb < L, and 0.6·D_rail = 13.18 lb < L, so net
tension exists in every upward case and each is checked.

Check 3's D is the top rail's own dead load; the intermediate rail frames
in below that weld [brief: loads-and-envelope, slice 4]. Check 6 is live
load only.

**Skew angle, by calculation, not assumed.** For the square post the
H1-1b moment term is (M cos φ)/M_cx + (M sin φ)/M_cy with M_cx = M_cy,
maximum at φ = 45° (d/dφ = 0 at tan φ = M_cx/M_cy = 1), factor √2. For
the weld line, the bending force at a point (x, y) is
M(y cos φ + x sin φ)/I_w; its maximum over the rounded rectangle is the
support function h(φ) = 0.768(|cos φ| + |sin φ|) + 0.232, which I also
scanned numerically on the line (0° to 90°): 1.000 at 0°, 1.173 at 15°,
1.281 at 30°, 1.314 at 40°, **1.318 at 45°**, symmetric beyond. So φ =
45° governs Checks 3, 5 and 7, at the midpoint of a corner arc.

### Envelope cases listed

Checks 3, 5, 7: {downward, outward, inward, upward, longitudinal, skew} ×
{concentrated, distributed} = 12 each. Check 6: {outward, inward,
longitudinal} × 2 = 6 (downward and upward have no lateral deflection;
the template defines no skew case for Check 6, and for this square post a
skew load deflects by the same resultant as a transverse one). Check 4a:
horizontal and downward. Check 4b: horizontal and downward. Reactions:
lateral and upward sets.

## 4. Section properties (AISC Shapes Database v16.0, as published)

| Property | Post HSS2X2X1/8 | Intermediate HSS2X1X1/8 | Top rail Pipe2STD |
| --- | --- | --- | --- |
| Ht × B (in) | 2 × 2 | 2 × 1 | OD = 2.375 |
| t_nom / t_des (in) | 0.125 / 0.116 | 0.125 / 0.116 | 0.154 / 0.143 |
| A (in²) | 0.840 | 0.608 | 1.02 |
| b/t, h/t | 14.2, 14.2 | 5.62, 14.2 | D/t = 16.6 |
| I_x, S_x, Z_x, r_x | 0.486, 0.486, 0.584, 0.761 | 0.280, 0.280, 0.366, 0.679 | |
| I_y, S_y, Z_y, r_y | 0.486, 0.486, 0.584, 0.761 | 0.0922, 0.184, 0.223, 0.390 | |
| J (in⁴) | 0.796 | 0.238 | |
| W (lb/ft) | 3.05 | 2.20 | 3.66 |

Intermediate rail orientation: long side horizontal, so the horizontal
component load bends the strong axis (x, I_x = 0.280) and the vertical
loads bend the weak axis (y, I_y = 0.0922) [brief: S6-2].

**Classification, A500 Gr B (Fy = 46 ksi)** [own: PDF, Tables B4.1a,
B4.1b]: √(E/Fy) = √(29000/46) = 25.11.

| Element | Ratio | Limit | Result |
| --- | --- | --- | --- |
| Post walls, compression (B4.1a Case 6) | 14.2 | λr = 1.40√(E/Fy) = 35.15 | nonslender |
| Post flange, flexure (B4.1b Case 17) | 14.2 | λp = 1.12√(E/Fy) = 28.12; λr = 35.15 | compact |
| Post web, flexure (B4.1b Case 19) | 14.2 | λp = 2.42√(E/Fy) = 60.76; λr = 5.70√(E/Fy) = 143.1 | compact |
| Intermediate, strong-axis bending: flange (1 in wall) / web (2 in wall) | 5.62 / 14.2 | 28.12 / 60.76 | compact |
| Intermediate, weak-axis bending: flange (2 in wall) / web (1 in wall) | 14.2 / 5.62 | 28.12 / 60.76 | compact |

## 5. Check 3: top rail to post weld (mixed pair)

### Case-independent quantities

**Weld line:** the post's rounded rectangle on its outside surface
[brief: S6-9, S6-6], outside corner radius R = 2·t_des.

| Symbol | Equation | Substituted | Result | Source |
| --- | --- | --- | --- | --- |
| R | 2·t_des | 2 × 0.116 | 0.232 in | [brief: S6-3, S6-6] |
| a | flat length, H − 2R | 2 − 0.464 | 1.536 in | |
| c | extreme fiber, H/2 | | 1.000 in | |
| L_w | 4a + 2πR | 6.144 + 1.4577 | 7.602 in | |
| I_w, flats ⊥ to bending plane | 2·a·c² | 2 × 1.536 × 1² | 3.072 in³ | line property |
| I_w, flats ∥ | 2·a³/12 | 2 × 1.536³/12 | 0.6040 in³ | |
| I_w, four arcs | 4R[y_c²·π/2 + 2y_cR + R²·π/4], y_c = c − R = 0.768 | 4(0.232)[0.9265 + 0.3564 + 0.04227] | 1.230 in³ | integration, checked numerically |
| I_w | sum | | 4.906 in³ | |
| S_w,t = S_w,l | I_w/c | | 4.906 in² | square post |
| e | D_rail/2 | 2.375/2 | 1.1875 in | [brief: W1, S6-9] |
| w, t_e | 0.707w | 0.707 × 0.125 | 0.08838 in | [brief: effective throat] |
| F_nw | 0.60·F_EXX·k_ds, k_ds = 1.0 | 0.60 × 70 × 1.0 | 42 ksi | 360-22 Table J2.5, §J2.4(a) [own: memory]; [brief: W2] |
| R_w/Ω | F_nw·t_e/2.00 | 42 × 0.088375/2.00 | 1856 lb/in | Ω = 2.00, Table J2.5 [own: memory] |
| Rail base metal | 0.60·Fu·t_des,rail/2.00 | 0.6 × 60 × 0.143/2.00 | 2574 lb/in | §J4.2(b), Eq. J4-4 [own: PDF]; [brief: W6] |
| Thinner part | min(t_nom,post, t_nom,rail) | min(0.125, 0.154) | 0.125 in | [brief: W11] |
| w_min | Table J2.4, to 1/4 in | | 1/8 in | [own: PDF] |
| Min size | w = 1/8 ≥ 1/8 | | **OK** | |

Forces per inch of weld (W3, W10): f_a = axial/L_w; f_v = V/L_w,
uniform; f_b = M/S_w (orthogonal cases) or the corner value (skew);
f_n = f_a + f_b on the compression side, which governs in every moment
case (dead-load compression adds to bending there); f_r = √(f_n² + f_v²).
Base metal ratio = f_v / 2574 (in-plane force only).

### Every envelope case

| Case | f_a | f_b | f_v | f_n | f_r | Fiber | Weld ratio | Base ratio | Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Downward, conc (21.96 + 200) | 29.20 | — | — | 29.20 | 29.20 | uniform | 0.01573 | — | 0.01573 |
| Downward, dist (21.96 + 300) | 42.35 | — | — | 42.35 | 42.35 | uniform | 0.02282 | — | 0.02282 |
| Outward, conc (M = 237.5) | 2.889 | 48.41 | 26.31 | 51.30 | 57.66 | compression | 0.03107 | 0.01022 | 0.03107 |
| Outward, dist (M = 356.3) | 2.889 | 72.62 | 39.46 | 75.51 | 85.20 | compression | 0.04591 | 0.01533 | 0.04591 |
| Inward, conc / dist | as outward | | | | | | | | 0.03107 / 0.04591 |
| Upward, conc (200 − 13.18) | 24.58 | — | — | 24.58 | 24.58 | uniform | 0.01324 | — | 0.01324 |
| Upward, dist (300 − 13.18) | 37.73 | — | — | 37.73 | 37.73 | uniform | 0.02033 | — | 0.02033 |
| Longitudinal, conc / dist | as outward (S_w,l = S_w,t) | | | | | | | | 0.03107 / 0.04591 |
| Skew 45°, conc | 2.889 | 63.81 | 26.31 | 66.70 | 71.70 | compression | 0.03864 | 0.01022 | 0.03864 |
| Skew 45°, dist | 2.889 | 95.72 | 39.46 | 98.61 | 106.2 | compression | **0.05723** | 0.01533 | **0.05723** |

Tension side, outward distributed, for the record:
√(39.46² + (72.62 − 2.889)²) = 80.12 lb/in < 85.20.

**Skew, full lines (distributed):** M = 300 × 1.1875 = 356.25 lb-in;
M_t = M_l = 356.25 cos 45° = 251.9 lb-in. Governing point: midpoint of
a corner arc, x = y = 0.768 + 0.232 cos 45° = 0.9320 in.
f_b,t = 251.9 × 0.9320/4.906 = 47.86 lb/in; f_b,l = 47.86 lb/in;
f_b = 95.72; f_n = 95.72 + 2.889 = 98.61; f_v = 300/7.602 = 39.46;
f_r = √(98.61² + 39.46²) = 106.2 lb/in; ratio 106.2/1856 = 0.0572.

**Check 3 controlling: skew, distributed, 0.0572 (OK).** Without the
skew case: outward (or inward or longitudinal), distributed, 0.0459.

## 6. Check 4a: intermediate rail member, HSS2X1X1/8

### Case-independent capacities

| Symbol | Equation | Substituted | Result | Citation, source |
| --- | --- | --- | --- | --- |
| M_px | Fy·Z_x | 46 × 0.366 | 16,840 lb-in (16.836 kip-in) | Eq. F7-1 [own: PDF] |
| M_py | Fy·Z_y | 46 × 0.223 | 10,260 lb-in | Eq. F7-1 |
| √(J·A_g) | | √(0.238 × 0.608) | 0.3804 in² | |
| L_p | 0.13·E·r_y·√(JA_g)/M_p | 0.13 × 29000 × 0.39 × 0.3804/16.836 | 33.22 in | Eq. F7-10 [own: PDF] |
| L_r | 2·E·r_y·√(JA_g)/(0.7·Fy·S_x) | 2 × 29000 × 0.39 × 0.3804/(0.7 × 46 × 0.28) | 954.4 in | Eq. F7-11 [own: PDF] |
| L_b | span | | 72 in: L_p < L_b ≤ L_r → Eq. F7-8 | [brief: S6-4, S6-16 item 3] |
| Δ_allow | L/120 | 72/120 | 0.600 in | [V: ej.deflection.limit] |

### Horizontal case (component load alone, strong axis x)

| Symbol | Equation | Substituted | Result | Source |
| --- | --- | --- | --- | --- |
| M_r | P_c·L/4 | 50 × 72/4 | 900 lb-in | [V: aisc_manual.t3-23.case7.M] |
| M_A, M_B, M_C | quarter, center, three-quarter | 450, 900, 450 | lb-in | |
| C_b | 12.5M_max/(2.5M_max + 3M_A + 4M_B + 3M_C) | 12.5/(2.5 + 1.5 + 4 + 1.5) | 1.316 | Eq. F1-1 [own: PDF] |
| M_n (F7-8) | C_b[M_p − (M_p − 0.7FyS_x)(L_b − L_p)/(L_r − L_p)] | 1.316[16.836 − 7.820 × 0.04210] | 21.72 kip-in > M_p | Eq. F7-8 |
| M_n | min(F7-8, M_p) | | 16,840 lb-in = M_p | |
| M_c | M_n/Ω_b | 16836/1.67 | 10,080 lb-in | [V: aisc360.F1.omega_b], [V: aisc360.eq.B3-2] |
| Ratio | M_r/M_c | 900/10081 | 0.08927 | |
| Δ | P_c·L³/(48EI_x) | 50 × 72³/(48 × 29×10⁶ × 0.280) | 0.04788 in | [V: aisc_manual.t3-23.case7.delta]; L only [V: ej.combo.deflection.L_only] |
| Ratio | Δ/Δ_allow | 0.04788/0.600 | 0.07980 | |

### Downward case (P_c + dead load, weak axis y)

| Symbol | Equation | Substituted | Result | Source |
| --- | --- | --- | --- | --- |
| w_D | 2.20/12 | | 0.1833 lb/in | |
| M_r | P_c·L/4 + w_D·L²/8 | 900 + 0.1833 × 72²/8 | 1019 lb-in (1018.8) | [V: aisc_manual.t3-23.case1.M], case 7; D + L [V: ej.combo.deflection.D_plus_L] for the combination on one axis (ASD D + L for strength, [V: asce7.combo.asd.D_plus_L]) |
| M_n | M_py (no LTB on the weak axis; compact) | | 10,260 lb-in | User Note to §F7.4 [own: PDF] |
| M_c | M_n/1.67 | 10258/1.67 | 6143 lb-in | |
| Ratio | 1018.8/6142.5 | | 0.1659 | |
| Δ | P_c·L³/(48EI_y) + 5w_D·L⁴/(384EI_y) | 0.1454 + 0.02399 | 0.1694 in | Table 3-23 cases 7 and 1 [V] |
| Ratio | 0.1694/0.600 | | **0.2823** | |

**Check 4a controlling: downward, deflection, 0.282 (OK).** Bending:
downward 0.166.

## 7. Check 4b: intermediate rail to post weld (rectangular on rectangular)

Simple shear connection, e = 0, no end moment [brief: Check 4b, S4-12].
Component load adjacent to the post [brief: S4-9]. Chapter K chord limit
states: no demand; the intermediate rail delivers no axial force or moment
to the post wall [brief: S6-11]. Table K5.1 effective length [brief: S6-8].

| Symbol | Equation | Substituted | Result | Source |
| --- | --- | --- | --- | --- |
| H_b | branch dimension in the plane of the connection (vertical) | | 1.0 in | Table K5.1 notation [own: memory] |
| B_b | branch dimension across the chord face (horizontal) | | 2.0 in | [brief: S6-9 width rule] |
| B, t | chord (post) face width, design wall | | 2.0, 0.116 in | |
| β | B_b/B | 2/2 | 1.000 | |
| B_e | (10/(B/t))·(Fy·t/(Fy_b·t_b))·B_b ≤ B_b | (10/17.24)(1.0)(2.0) | 1.160 in | Eq. K1-1 [own: PDF] |
| Cap | β > 0.85 or θ > 50°: B_e/2 ≤ B_b/4 | B_e ≤ 1.0 | B_e = 1.000 in | Table K5.1 [own: PDF, page 16.1-171]; θ = 90° |
| l_e | 2H_b/sin θ + 2B_e | 2(1.0) + 2(1.0) | 4.000 in | Eq. K5-5 [own: PDF] |
| R_D | w_D,int·L/2 | 13.20/2 | 6.600 lb | [brief: S4-9] |
| t_e | 0.707 × 0.125 | | 0.08838 in | |
| F_nw | 0.60 × 70 × 1.0 | | 42 ksi | Eq. K5-1, k_ds = 1.0 |
| Weld allowable | F_nw·t_e/2.00 | | 1856 lb/in | §K5(a), Ω = 2.00 [own: PDF] |
| Post wall base metal | 0.6·Fu·t_des,post/2.00 | 0.6 × 58 × 0.116/2 | 2018 lb/in | §J4.2(b) |
| Intermediate wall base metal | 0.6·Fu·t_des,int/2.00 | 0.6 × 58 × 0.116/2 | 2018 lb/in | tie → **post wall** governs [brief: S4-12] |
| Thinner part, w_min | t_nom 0.125 both; Table J2.4 | | 1/8 in; **OK** | |

| Case | R | f_v = f_r = R/l_e | Weld ratio | Base ratio (post wall) | Ratio |
| --- | --- | --- | --- | --- | --- |
| Horizontal: √(P_c² + R_D²) | √(50² + 6.6²) = 50.43 lb | 12.61 lb/in | 0.006794 | 0.006247 | 0.006794 |
| Downward: P_c + R_D | 56.60 lb | 14.15 lb/in | **0.007624** | 0.007011 | **0.007624** |

**Check 4b controlling: downward, component, 0.00762 (OK).**

## 8. Check 5: post combined axial and flexure

### Case-independent capacities

| Symbol | Equation | Substituted | Result | Citation, source |
| --- | --- | --- | --- | --- |
| K | fixed-free, recommended | | 2.1 | Commentary App. 7, Table C-A-7.1 [brief: D3] |
| L_c | K·h | 2.1 × 42 | 88.20 in | [brief: D3: h, not h − t_p] |
| r | smaller r (square: r_x = r_y) | | 0.761 in | [brief: S6-14 item 2] |
| L_c/r | | 88.2/0.761 | 115.9 (< 200, no flag) | [brief: D6] |
| Limit | 4.71√(E/Fy) | 4.71 × 25.11 | 118.3 → L_c/r ≤ limit: **Eq. E3-2** | §E3(a) [own: PDF] |
| F_e | π²E/(L_c/r)² | π² × 29000/115.9² | 21.31 ksi | Eq. E3-4 [own: PDF] |
| F_cr | 0.658^(Fy/Fe)·Fy | 0.658^(46/21.307) × 46 = 0.658^2.159 × 46 | 18.64 ksi | Eq. E3-2 |
| P_n | F_cr·A_g | 18.635 × 0.840 | 15,650 lb | Eq. E3-1 |
| P_c | P_n/Ω_c | 15653/1.67 | 9373 lb | §E1, Ω_c = 1.67 [own: memory] |
| M_nx = M_ny | M_p = Fy·Z (compact; square, no LTB; C_b = 1.0, L_b = h noted, not used) | 46 × 0.584 | 26,860 lb-in | Eq. F7-1; User Note §F7.4 [own: PDF]; [brief: S6-4] |
| M_cx = M_cy | M_n/1.67 | 26864/1.67 | 16,090 lb-in | [V: aisc360.F1.omega_b] |
| P_t | Fy·A_g/Ω_t | 46 × 0.840/1.67 | 23,140 lb | §D2(a), Eq. D2-1, Ω_t = 1.67 [own: memory] |
| P_e | π²EI/L_c² | π² × 29000 × 0.486/88.2² | 17,880 lb | App. 8 with L_c = K·h and EI [brief: D1] |

### Every envelope case

Interaction: P_r/P_c = 45.71/9373 = 0.004876 < 0.2 in every moment case
→ Eq. H1-1b, P_r/(2P_c) + M_rx/M_cx + M_ry/M_cy ≤ 1.0 [own: PDF]. Axial
only cases report their own chapter's ratio [brief: D8].

| Case | P_r (lb) | M_r (lb-in) | Equation | Ratio | αP_r/P_e |
| --- | --- | --- | --- | --- | --- |
| Downward, conc | 245.7 C | 0 | Pr/Pc | 0.02621 | — |
| Downward, dist | 345.7 C | 0 | Pr/Pc | 0.03688 | — |
| Outward, conc | 45.71 C | 8300 | H1-1b | 0.002438 + 0.5160 = 0.5184 | 0.004090 |
| Outward, dist | 45.71 C | 12,450 | H1-1b | 0.002438 + 0.7740 = 0.7764 | 0.004090 |
| Inward, conc / dist | as outward | | H1-1b | 0.5184 / 0.7764 | 0.004090 |
| Upward, conc | 200 − 27.42 = 172.6 T | 0 | Pr/Pt | 0.007459 | — |
| Upward, dist | 300 − 27.42 = 272.6 T | 0 | Pr/Pt | 0.01178 | — |
| Longitudinal, conc / dist | 45.71 C | 8300 / 12,450 (other axis) | H1-1b | 0.5184 / 0.7764 | 0.004090 |
| Skew 45°, conc | 45.71 C | 8300; M_rx = M_ry = 5869 | H1-1b | 0.002438 + 2(0.3649) = 0.7321 | 0.004090 (no key) |
| Skew 45°, dist | 45.71 C | 12,450; M_rx = M_ry = 8803 | H1-1b | 0.002438 + 2(0.5473) = **1.097** | 0.004090 (no key) |

αP_r/P_e = 1.6 × 45.71/17881 = 0.00409 ≤ 0.05 in every lateral case:
second-order effects negligible, amplification taken as 1.0.

**Full lines, controlling case (skew, distributed):** V = 300 lb at
φ = 45° from transverse; M = 300 × 41.5 = 12,450 lb-in;
M_rx = M_ry = 12,450 × cos 45° = 8803 lb-in;
H1-1b = 45.71/(2 × 9373) + 8803/16,086 + 8803/16,086
= 0.002438 + 0.5473 + 0.5473 = **1.097 > 1.0, NG**.

**Check 5 controlling: skew, distributed, 1.097, NG.** Without the skew
case: outward (inward, longitudinal), distributed, 0.776, OK. See open
question 1: whether the skew case is binding, and whether the linear
H1-1b sum is what Micah wants for a square tube bent about its diagonal.

## 9. Check 6: post deflection

| Symbol | Equation | Substituted | Result | Source |
| --- | --- | --- | --- | --- |
| Δ_allow | (h − t_p)/60 | 41.5/60 | 0.6917 in | [brief: Check 6] |
| Δ, conc | V(h − t_p)³/(3EI) | 200 × 41.5³/(3 × 29×10⁶ × 0.486) | 0.3381 in | cantilever tip load [own: memory] |
| Δ, dist | | 300 × 71,473/(42.28×10⁶) | 0.5071 in | |

| Case | Δ (in) | Ratio |
| --- | --- | --- |
| Outward / inward / longitudinal, conc | 0.3381 | 0.4888 |
| Outward / inward / longitudinal, dist | 0.5071 | **0.7332** |

**Check 6 controlling: outward, distributed, 0.733 (OK);** inward and
longitudinal tie with it.

## 10. Check 7: post to baseplate weld, all around

### Case-independent quantities

| Symbol | Equation | Substituted | Result | Source |
| --- | --- | --- | --- | --- |
| L_w, S_w,t = S_w,l | rounded rectangle, as Check 3 | | 7.602 in; 4.906 in² | [brief: S6-6] |
| Arm | h − t_p | | 41.5 in | [brief: W, D4] |
| t_e | 0.707 × 0.1875 | | 0.1326 in | |
| F_nw | 0.60 × 70 × k_ds, k_ds = 1.0 | | 42 ksi | §J2.4(a)(2); User Note to §K5 [own: PDF]; [brief: S6-6] |
| Weld allowable | 42 × 0.13256/2.00 | | 2784 lb/in | Table J2.5, Ω = 2.00 |
| Baseplate base metal | 0.6·Fu·t_p/2.00 | 0.6 × 58 × 0.5/2.00 | 8700 lb/in | §J4.2(b), against f_r [brief: W5] |
| Post wall | covered by Check 5 (all around; Fu/Fy = 1.261 ≥ 1.20) | | | [brief: W5, S6-7] |
| Thinner part, w_min | min(0.125, 0.5) = 0.125 in → 1/8 in; w = 3/16 | | **OK** | Table J2.4 |

### Every envelope case

| Case | f_a | f_b | f_v | f_n | f_r | Fiber | Weld ratio | Base ratio | Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Downward, conc (45.71 + 200) | 32.32 | — | — | 32.32 | 32.32 | uniform | 0.01161 | 0.003715 | 0.01161 |
| Downward, dist (45.71 + 300) | 45.48 | — | — | 45.48 | 45.48 | uniform | 0.01634 | 0.005227 | 0.01634 |
| Outward, conc (M = 8300) | 6.013 | 1692 | 26.31 | 1698 | 1698 | compression | 0.6100 | 0.1952 | 0.6100 |
| Outward, dist (M = 12,450) | 6.013 | 2538 | 39.46 | 2544 | 2544 | compression | 0.9139 | 0.2924 | 0.9139 |
| Inward, conc / dist | as outward | | | | | | | | 0.6100 / 0.9139 |
| Upward, conc (200 − 27.42) | 22.70 | — | — | 22.70 | 22.70 | uniform | 0.008155 | 0.002609 | 0.008155 |
| Upward, dist (300 − 27.42) | 35.86 | — | — | 35.86 | 35.86 | uniform | 0.01288 | 0.004122 | 0.01288 |
| Longitudinal, conc / dist | as outward | | | | | | | | 0.6100 / 0.9139 |
| Skew 45°, conc | 6.013 | 2230 | 26.31 | 2236 | 2236 | compression | 0.8033 | 0.2570 | 0.8033 |
| Skew 45°, dist | 6.013 | 3345 | 39.46 | 3351 | 3351 | compression | **1.204** | 0.3852 | **1.204** |

Outward distributed, tension side for the record: √(39.46² + (2538 −
6.01)²) = 2532 lb/in < 2544.

**Full lines, controlling case (skew, distributed):** M = 300 × 41.5 =
12,450 lb-in; M_t = M_l = 8803 lb-in; governing point at the corner-arc
midpoint (0.9320, 0.9320) in;
f_b,t = 8803 × 0.9320/4.906 = 1673 lb/in; f_b,l = 1673 lb/in;
f_b = 3345 lb/in; f_a = 45.71/7.602 = 6.013 lb/in (compression side);
f_n = 3351 lb/in; f_v = 300/7.602 = 39.46 lb/in;
f_r = √(3351² + 39.46²) = 3351 lb/in;
weld ratio 3351/2784 = **1.204 > 1.0, NG**; baseplate base metal
3351/8700 = 0.385.

**Check 7 controlling: skew, distributed, 1.204, NG.** Without the skew
case: outward (inward, longitudinal), distributed, 0.914, OK.

## 11. Reaction sets (LRFD, 0.9D + 1.6L, arm h = 42 in)

Engineering-judgement combinations [brief: loads-and-envelope]. Larger
load type: w·s = 300 lb > P = 200 lb → **distributed** [brief: S4-5].
D = 21.96 (top rail) + 13.20 (intermediate) + 10.55 (post) + 6.806
(baseplate) = 52.51 lb.

| Set | V (lb) | N (lb), tension + | M (lb-in) |
| --- | --- | --- | --- |
| Lateral | 1.6 × 300 = 480.0 | −0.9 × 52.51 = −47.26 (compression) | 480 × 42 = 20,160 |
| Upward (1.6L = 480 > 0.9D = 47.26) | 0 | 480 − 47.26 = +432.7 (tension) | 0 |

## 12. Summary

| Check | Controlling case | Ratio | Result | Without skew |
| --- | --- | --- | --- | --- |
| 3 | skew, distributed | 0.0572 | OK | outward, distributed, 0.0459 |
| 4a | downward, deflection | 0.282 | OK | |
| 4b | downward, component | 0.00762 | OK | |
| 5 | skew, distributed | 1.097 | **NG** | outward, distributed, 0.776 |
| 6 | outward, distributed | 0.733 | OK | |
| 7 | skew, distributed | 1.204 | **NG** | outward, distributed, 0.914 |
| Reactions | lateral: V = 480, N = −47.26, M = 20,160; upward: N = +432.7 | | | |

## 13. Values from my own reading (no verified entry)

| Value | Used as | Document, section | Source |
| --- | --- | --- | --- |
| A500 Gr B rectangular Fy = 46, Fu = 58 ksi | post, intermediate rail | AISC Manual 16th Ed. Table 2-4; ASTM A500/A500M-21 | memory |
| A53 Gr B Fu = 60 ksi | rail base metal, Fy/Fu limit | AISC Manual 16th Ed. Table 2-4 | memory |
| A36 Fu = 58 ksi | baseplate base metal | AISC Manual 16th Ed. Table 2-5 | memory |
| F_EXX = 70 ksi; F_nw = 0.60F_EXX; Ω = 2.00 | all welds | AISC 360-22 Table J2.5, §J2.4(a); §K5(a) | memory; §K5(a) Ω read in the PDF |
| k_ds = 1.0 at Checks 3, 4b and 7 | | §J2.4(a)(2) and (3); User Note to §K5 (p. 16.1-170) | PDF (User Note); brief W2, S6-6 |
| t_e = 0.707w | | §J2.2a | brief ruling |
| Shear rupture 0.60Fu·A_nv, Ω = 2.00 | base metal | §J4.2(b), Eq. J4-4 | PDF |
| Table J2.4 minimum fillet sizes | | Table J2.4 | PDF |
| P_c = 50 lb | component load | ASCE 7-22 §4.5.1.2 | memory |
| ρ = 490 lb/ft³ | baseplate weight | AISC Manual (steel unit weight) | memory |
| Ω_c = 1.67, Ω_t = 1.67 | Checks 5 | §E1, §D2 | memory |
| Eqs. E3-2, E3-4 and the 4.71√(E/Fy) limit | Check 5 | §E3 | PDF |
| Eq. H1-1b and the 0.2 threshold | Check 5 | §H1.1 | PDF |
| Eqs. F7-1, F7-8, F7-10, F7-11; User Note to §F7.4 | Checks 4a, 5 | §F7 | PDF |
| Eq. F1-1; C_b = 1.0 for a cantilever with the free end unbraced | Check 4a; post | §F1(c) | PDF |
| Table B4.1a Case 6 (1.40); Table B4.1b Case 17 (1.12, 1.40), Case 19 (2.42, 5.70) | classification | Tables B4.1a, B4.1b | PDF |
| Eq. K1-1; Table K5.1 Eq. K5-5 and the B_e/2 ≤ B_b/4 cap (β > 0.85 or θ > 50°) | Check 4b | §K1, Table K5.1 (p. 16.1-171) | PDF |
| Round chord D/t ≤ 50, Fy ≤ 52 ksi, Fy/Fu ≤ 0.8 | Check 3 applicability | Tables K3.1A, K4.1A (round tables not opened; the 52 ksi and 0.8 limits read in Table K4.2A) | memory and PDF; brief S6-13 |
| Cantilever tip deflection VL³/(3EI) | Check 6 | AISC Manual Table 3-23 (cantilever, load at free end) | memory |
| 0.9D + 1.6L | reactions | engineering judgement | brief |

## 14. Open questions

1. **The skew case (S6-18) is not in any document I may read.** The
   values template's header defines it ("the horizontal guard load at the
   plan angle from transverse worst for the check", Checks 3, 5 and 7) and
   the branch's last commits name S6-18, but docs/brief/, docs/plans/,
   docs/adr/ and CONTEXT.md have no S6-17 or S6-18, and the brief's S6-14
   item 2 says the opposite: "Each lateral case bends one axis only ... and
   the post has no biaxial case." I worked the skew case from my own
   reading of ASCE 7-22 §4.5.1 (the load "in any direction") because the
   test compares its keys. **With it, case 9 fails Check 5 (1.097) and
   Check 7 (1.204)**; without it both pass (0.776, 0.914). Micah: confirm
   S6-18 and move it into the brief (CLAUDE.md asks that binding
   decisions be in the brief before the plan is marked completed).
   - Check 5 uses the linear H1-1b sum, M_rx/M_cx + M_ry/M_cy, which is
     what §H1.1 prints. It is conservative for a square tube about its
     diagonal: my estimate, thin-wall, Z_diag ≈ (√2/1.5)·Z_x ≈ 0.94Z_x, so
     the true diagonal demand is about 1.06·M/M_p, against √2·M/M_p from
     H1-1b. The skew ratio would then be about 0.82, not 1.10. I did not
     use this: §H1.1 is the code text, and §H2 (the stress alternative) is
     not in the plan. Micah's call whether the tool should take the
     diagonal's own capacity.
   - The distributed load at skew: the full w·s = 300 lb at the plan
     angle, its longitudinal component taken as the brief takes the
     longitudinal distributed load (engineering judgement).
2. **How the skew weld stress is combined.** I evaluated the elastic
   line stress at the actual governing point of the rounded rectangle,
   the corner-arc midpoint, so f_b,t and f_b,l are each component's
   contribution at that point (c = 0.9320 in each axis). Adding each
   component's own maximum, M_t/S_w,t + M_l/S_w,l, places both maxima at
   a sharp corner (1, 1) that is not on the weld line, and gives f_b
   7.3% higher: Check 7 skew 1.292 instead of 1.204, Check 3 0.0607
   instead of 0.0572. The two readings differ by more than the 0.5%
   tolerance, so if the tool sums the maxima the comparison fails here,
   and that is a method question, not an arithmetic one.
3. **Table K5.1's B_e cap (plan open item 1).** The 360-22 page reads
   "When β > 0.85 or θ > 50°, B_e/2 shall not exceed B_b/4". I applied it
   as printed. Here β = 1 and θ = 90°, so both readings cap B_e at
   1.000 in (Eq. K1-1 alone gives 1.160 in). I recorded `B_e_in` as the
   capped value used in l_e.
4. **H_b and B_b at Check 4b.** I took H_b = 1 in (the intermediate
   rail's vertical dimension, in the plane of the post and rail axes) and
   B_b = 2 in (across the post face, the width the S6-9 width rule
   compares). Swapped, l_e would be 2(2) + 2(min(…, B_b/2 = 0.5)) = 5 in,
   and the ratios would fall by 20%. It does not change any verdict.
5. **Check 3's base metal in the vertical cases.** The downward and
   upward cases put no in-plane force on the rail wall; their normal
   force is the chord-wall question, a stated assumption at a mixed pair
   (S6-9). So they have weld ratios only, and the template has no
   `ratio_base` key for them, which agrees.
6. **An inclined component load on the intermediate rail** (section 2):
   not in the plan (S6-16 item 3); my estimate is 0.191 against 0.166.
   It does not govern Check 4a; listed so Micah can rule.
7. **D_post in the reaction sets.** I used W·(h − t_p), the definition
   in loads-and-envelope.md. Over h it would add 0.127 lb to D: below
   the tolerance.

**Mapping gaps (step 7).** Every key in the template has a value. Values I
computed with no key: Check 7's weld allowable (2784 lb/in; Check 3 and
Check 4b have `weld_allow_lbpin`, Check 7 does not); αP_r/P_e in the skew
cases (0.004090; the template has the key for the orthogonal lateral
cases only); the Check 4a L_b-to-L_p comparison and the uncapped B_e
(1.160 in). No check is on one side only, as far as the keys show.

## 15. Review checklist (docs/brief/verification.md, items 1–9)

1. **Loads complete.** Top rail, intermediate rail and post dead loads
   carried to the post (45.71 lb at the critical section); baseplate
   added to the reaction sets only. Both guard load types in every case.
   Component load on Check 4a and 4b only, not concurrent with the guard
   loads. Check 3 uses the top rail's dead load only. Yes.
2. **Direction and worst case.** All five orthogonal cases plus skew,
   each with both load types; the skew angle found by calculation (45°,
   scanned 0° to 90° on the weld line); the governing fiber evaluated on
   both sides (compression governs). Upward checked for net tension in
   every case. Yes.
3. **Checks complete.** Every limit state in section 2 is either checked
   or given a reason. Two not in the plan are flagged (the skew case's
   standing, open question 1; the inclined component load, question 6).
4. **Geometry.** Moment arm h − t_p = 41.5 in for Checks 5 to 7; L_c =
   2.1h on h, not h − t_p (D3); e = D_rail/2 = 1.1875 in at Check 3 and
   e = 0 at Check 4b; reactions on h = 42 in; L_b = 72 in for the
   intermediate rail. Yes.
5. **Method and equations.** Classification before capacity (all
   compact, nonslender). E3-2 by L_c/r = 115.9 ≤ 118.3. H1-1b by P_r/P_c =
   0.0049 < 0.2. F7-8 branch by L_p < L_b ≤ L_r, capped at M_p. No LTB on
   the square post or the weak axis. Table K5.1 at β = 1 with the cap.
   k_ds = 1.0 everywhere. Yes.
6. **Assumptions.** Post fixed at the top of the baseplate; K = 2.1;
   tributary length = span; weld as an elastic line with uniform shear;
   no bearing credit; fillet model kept at the equal-width sides of the
   Check 4b joint; chord wall not checked at the mixed pair (inside its
   Chapter K limits). Stated, and as the brief rules.
7. **Code editions.** AISC 360-22, AISC Manual 16th Ed., ASCE 7-22
   throughout; the 360-22 text read where noted. Yes.
8. **Magnitude sense.** Check 3 ≈ 0.05 and Check 4b ≈ 0.008 are joint
   checks at tens to hundreds of pounds, as S6-1 expects; Check 5 0.78
   and Check 6 0.73 for a 2 in square post under 300 lb at 41.5 in are
   plausible; Check 7 at 0.91 for a 3/16 in fillet on a 2 in tube with no
   directional increase is plausible. Units: lb, in, lb-in, lb/in; kip
   values converted. Yes.
9. **Governing case.** Expected: the distributed load (300 lb > 200 lb)
   in the horizontal cases, and that holds for the orthogonal envelope.
   The skew case takes over Checks 3, 5 and 7 by √2 (Check 5) and 1.318
   (the welds), and turns Checks 5 and 7 NG. That is the finding to
   resolve first (open question 1).

## 16. S6-18 item 4 correction

Recomputed after comparison, 2026-10-17, slice-6 at e8b4247 (equal to
origin/slice-6, clean tree). Source of the ruling: docs/brief/welds.md,
S6-18 (Micah, 2026-10-17), "The skew horizontal case at a rectangular
post's welds", items on Check 7 and Check 3 [brief: S6-18]. This session
read only welds.md's S6-18 text and my own case-09.md and case-09.toml;
no tool output. It supersedes the skew lines of sections 5 and 10, the
skew rows of the summary (section 12), and resolves open question 2:
the two bending components are taken at full value at one point (the
corner of the all-around line), not as the elastic stress at the
corner-arc midpoint I used first.

**Method [brief: S6-18].** f_b,t = M_r·cos θ / S_w,t; f_b,l = M_r·sin θ /
S_w,l; f_b = f_b,t + f_b,l, maximum M_r·√(1/S_w,t² + 1/S_w,l²) at
tan θ = S_w,t/S_w,l. Moduli: the rounded-line values already used for
the transverse and longitudinal cases (S6-6), S_w,t = S_w,l = 4.906 in²,
so θ = 45° (unchanged) and f_b = √2·M_r/4.906. Axial term as in the other
lateral cases (compression side governs, f_n = f_a + f_b). Shear per
inch: the larger of the transverse and longitudinal values, equal here
(V/L_w). The sum is 1.0729 times my arc-point value (√2/4.906 against
2·cos 45°·0.9320/4.906), as open question 2 estimated.

Check 3 note: the rail here is round (Pipe2STD), so the moduli are the
post's rounded rectangle of section 5 (S6-9), not Table K5.1's S_ip and
S_op; S6-18's "same treatment" is applied with those moduli. Check 3's
base metal ratio is f_v/2574 (in-plane force only) and does not change.

**Check 3, skew (e = 1.1875 in; f_a = 21.96/7.602 = 2.889 lb/in;
allowable 1856 lb/in).**

| Quantity | Conc (M = 237.5 lb-in) | Dist (M = 356.25 lb-in) | Arc-point values (first calc), conc / dist |
| --- | --- | --- | --- |
| f_b,t = M cos 45°/4.906 | 34.23 lb/in | 51.35 lb/in | 31.91 / 47.86 |
| f_b,l = M sin 45°/4.906 | 34.23 lb/in | 51.35 lb/in | 31.91 / 47.86 |
| f_b | 68.47 lb/in | 102.7 lb/in | 63.81 / 95.72 |
| f_v = V/7.602 (unchanged) | 26.31 lb/in | 39.46 lb/in | 26.31 / 39.46 |
| f_n = f_a + f_b | 71.36 lb/in | 105.6 lb/in | 66.70 / 98.61 |
| f_r = √(f_n² + f_v²) | 76.05 lb/in | 112.7 lb/in | 71.70 / 106.2 |
| Weld ratio = f_r/1856 | 0.04098 | **0.06074** | 0.03864 / 0.05723 |
| Base ratio = f_v/2574 (unchanged) | 0.01022 | 0.01533 | 0.01022 / 0.01533 |
| Ratio | 0.04098 | **0.06074** | 0.03864 / 0.05723 |

**Check 3 controlling: skew, distributed, 0.0607 (OK)** (was 0.0572;
controlling case unchanged).

**Check 7, skew (arm 41.5 in; f_a = 45.71/7.602 = 6.013 lb/in; weld
allowable 2784 lb/in; baseplate base metal 8700 lb/in).**

| Quantity | Conc (M = 8300 lb-in) | Dist (M = 12,450 lb-in) | Arc-point values (first calc), conc / dist |
| --- | --- | --- | --- |
| f_b,t = M cos 45°/4.906 | 1196 lb/in | 1795 lb/in | 1115 / 1673 |
| f_b,l = M sin 45°/4.906 | 1196 lb/in | 1795 lb/in | 1115 / 1673 |
| f_b | 2393 lb/in | 3589 lb/in | 2230 / 3345 |
| f_v (unchanged) | 26.31 lb/in | 39.46 lb/in | 26.31 / 39.46 |
| f_n = f_a + f_b | 2399 lb/in | 3595 lb/in | 2236 / 3351 |
| f_r | 2399 lb/in | 3595 lb/in | 2236 / 3351 |
| Weld ratio = f_r/2784 | 0.8617 | **1.292** | 0.8033 / 1.204 |
| Base ratio = f_r/8700 | 0.2757 | 0.4133 | 0.2570 / 0.3852 |
| Ratio | 0.8617 | **1.292 NG** | 0.8033 / 1.204 |

**Check 7 controlling: skew, distributed, 1.292, NG** (was 1.204;
controlling case unchanged). Without the skew case: outward,
distributed, 0.914, OK (unchanged).

**Unchanged:** plan_angle_deg (45° in both checks), f_a, f_v, fiber
("compression side"), Check 3's ratio_base, every orthogonal case, the
controlling-case text of Checks 3, 5 and 7, and Check 5 (not a weld
check; S6-18 item 4 does not reach it).

Values file: 30 lines of tests/cases/independent/case-09.toml replaced,
each carrying the note "recomputed after comparison under S6-18 item 4
(sum of component maxima); first value used the stress at the arc point".
