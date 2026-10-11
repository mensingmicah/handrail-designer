# Independent calc: test case 6

Custom noncompact round tube rail (2.375 OD × 0.055 nominal wall, A500
Gr C) on a Pipe2STD post (A53 Gr B). No intermediate rail.

| | |
| --- | --- |
| Case | tests/cases/case-06.toml (inputs only; value tables stripped) |
| Date | 2026-10-10 |
| Model | Claude (Anthropic). The model id is given in the session report to Micah and is not recorded in the repo. |
| Branch, commit | `slice-5`, f0f148213da84a5e2d6e653ac4e73aa791e3222d |
| Coverage | section, Check 1, Check 2, Check 3, and the post group (D at the post). Checks 5 to 7 and the reactions are not covered by this case. |

Sources read: the case inputs (the skill's command); docs/BRIEF.md and
every file in docs/brief/; CONTEXT.md; docs/plans/slice-5.md (decisions
only; its "rough figures" for case 6 were not used); the verified registry
entries (the skill's command); the Pipe2STD row of
data/aisc-shapes-database-v16.0.xlsx (the skill's command);
out/aisc-360-22.pdf, the Specification's own text, cited below by section
and printed page; the key names and comment header of
tests/cases/independent/case-06.toml (step 7, after the calc was worked).
Not read: src/, any other file under tests/, tests/golden/, any drafted
registry entry, anything else in out/, any tool output. No test was run.

Notation: "360-22" is AISC 360-22 (ANSI/AISC 360-22, August 1, 2022), page
numbers as printed (16.1-nn). "Manual" is the AISC Steel Construction
Manual, 16th Edition. "Verified" names a verified registry entry by id.
"Own reading" is my reading, with "PDF" (out/aisc-360-22.pdf) or "memory".
Full precision is carried; values are shown to four significant figures
(more where a later line needs them).

## 1. Inputs

| Symbol | Value | Source |
| --- | --- | --- |
| L = s (span, post to post) | 6'-0" = 72 in | case input |
| h (top of concrete to rail centerline) | 42 in | case input |
| t_p (baseplate) | 1/2 in | case input |
| Top rail | custom round tube, D = 2.375 in, t_nom = 0.055 in, A500 Gr C | case input |
| Post | Pipe2STD, A53 Gr B | case input |
| Intermediate rail | none | case input |
| Baseplate | B = 6 in, N = 8 in, A36 | case input (not used by the covered groups) |
| Rail to post weld | w = 1/8 in fillet, E70XX | case input |
| Post to baseplate weld | 1/4 in fillet | case input (Check 7, not covered) |
| Deflection limits | rail L/120, post L/60, not bypassed | case input |
| P (concentrated guard load) | 200 lb | ASCE 7-22 §4.5.1; verified `asce7.guard.concentrated` |
| w (distributed guard load) | 50 lb/ft = 4.1667 lb/in | ASCE 7-22 §4.5.1.1; verified `asce7.guard.uniform`. No exemption entered. |
| E | 29,000 ksi | 360-22 Symbols; verified `material.steel.E` |
| F_y, rail (A500 Gr C, round) | 50 ksi | Manual Table 2-4, 16th Ed.; **own reading, memory, not certain** (section 10, open question 1) |
| F_u, rail (A500 Gr C, round) | 62 ksi | Manual Table 2-4, 16th Ed.; own reading, memory |
| F_y, post (A53 Gr B) | 35 ksi | Manual Table 2-4; verified `material.A53_GrB.Fy` (not used by the covered groups) |
| F_EXX (E70XX) | 70 ksi | electrode classification strength; own reading, memory |
| Steel density ρ | 490 lb/ft³ | Manual, 16th Ed. (basis of tabulated weights); own reading, memory |

## 2. Limit states considered

From the Specification, not from the tool's list of checks.

### Top rail (member)

| Limit state | Provision | Applies? |
| --- | --- | --- |
| Flexural yielding, M_p | 360-22 §F8.1, Eq. F8-1 (p. 16.1-65) | Yes. Computed in Check 1. |
| Flexural local buckling | 360-22 §F8.2 (p. 16.1-65) | Yes. D/t = 46.43 > λ_p = 40.6, so the wall is noncompact and Eq. F8-2 applies. It governs over M_p. |
| §F8 applicability, D/t < 0.45E/F_y | 360-22 §F8 (p. 16.1-65) | Checked: 46.43 < 261. |
| Slender wall, D/t > λ_r | Table B4.1b Case 20 (p. 16.1-23) | Checked: 46.43 < 179.8, not slender. No stop. |
| Lateral-torsional buckling | 360-22 §F8 lists yielding and local buckling only | No. Round section; verified `aisc360.F8.no_ltb`. L_b and C_b do not enter. |
| Shear | 360-22 §G5 (p. 16.1-80) | Not checked: stated assumption "No shear checks in any member" (output.md, scope.md). For information: F_cr = min(0.78E/(D/t)^1.5 = 71.5, 0.6F_y = 30) = 30 ksi, V_n/Ω = 30 × 0.3734/2/1.67 = 3.35 kip against V = wL/2 = 150 lb (0.04), or 200 lb with P beside the post (0.06). Not a test value. |
| Axial force from the longitudinal load | Chapters D, E | Not checked: "The top rail carries it axially and is not checked for it" (loads-and-envelope.md). 300 lb on A = 0.3734 in² is 0.8 ksi. |
| Torsion | 360-22 §H3 | None: guard loads act through the rail centerline (welds.md, W1). |
| Deflection | 360-22 Chapter L; limit is engineering judgement | Yes. Check 2; verified `ej.deflection.limit`. |
| Local effect of P on the thin wall (dent, ovalization at the point of load) | No 360-22 provision for a hand load on an HSS wall | Not checked, and the plan does not mention it. Flagged, open question 5. |

### Rail to post joint (Check 3)

| Limit state | Provision | Applies? |
| --- | --- | --- |
| Weld metal rupture | 360-22 §J2.4(a), Eq. J2-4; Table J2.5 (pp. 16.1-130, 16.1-132) | Yes. k_ds = 1.0 at this branch-to-chord weld (welds.md, W2). |
| Base metal at the rail fusion face, in-plane shear | 360-22 §J4.2(b), Eq. J4-4 (p. 16.1-146) | Yes, shear rupture only, demand V/(πD) (welds.md, W5, W6). |
| Base metal, shear yielding | 360-22 §J4.2(a), Eq. J4-3 | Not checked: a limit state of an element's gross shear area, not of a fusion face (W6). |
| Force normal to the rail wall (vertical load, V·e moment): chord plastification, and punching when D_b < D − 2t | 360-22 Tables K3.1 and K4.1 (pp. 16.1-163, 16.1-167 to 168) | Not checked in v1: stated assumption (W7), kept for slice 5 by S5-3. Punching does not apply at β = 1 (D_b is not less than D − 2t). For information only, section 7.6. |
| Chord D/t limit of applicability | 360-22 Table K3.1A (p. 16.1-164) and Table K4.1A (p. 16.1-168): D/t ≤ 50 for T-connections | Checked: 46.43 ≤ 50. No stop (S5-3). |
| Post wall at the weld | 360-22 §J4.1 | Covered by Check 5 (W5); Check 5 is not in this case's coverage. The W5 guard F_u/F_y ≥ 1.20 on the post grade: A53 Gr B, 60/35 = 1.71 (F_u = 60 ksi, own reading, memory). |
| Minimum fillet size | 360-22 §J2.2b(a), Table J2.4 (pp. 16.1-127, 16.1-128) | Yes, pass/fail (W11). |
| Maximum fillet size | 360-22 §J2.2b(b) (p. 16.1-127) | Does not apply: it governs welds along edges of material, and this is a T-joint (W11). |
| Fillet weld to material 0.055 in thick | 360-22 §J2 adopts AWS D1.1 | Flagged, open question 4: outside what the plan discusses. |

### Post (for D at the post only)

Checks 5, 6 and 7 are not in this case's coverage. The post group here
records the post's published properties and the dead load D at the
critical section, the cross-member quantity the custom rail changes
(verification.md, S5-2).

## 3. Loads and load path

**Dead load.** The rail's self-weight, w_D, acts downward along the span
(section 4.3). At each post the rail delivers w_D·s, the span being the
tributary length with no increase for continuity (stated assumption). The
post's own weight over h − t_p acts along the post. There is no
intermediate rail. The baseplate weight is below the critical section and
enters the reaction sets only (not covered).

**Guard loads.** Two load types, never concurrent: P = 200 lb, and w = 50
lb/ft. Each is run in every direction case. No exemption is entered, so
both act.

**On the rail (Checks 1 and 2).** Simple span L = 72 in between posts
(stated assumption). P acts at midspan, w along the whole span, both
through the rail centerline.

| Direction | Rail bending axis | Combination |
| --- | --- | --- |
| Downward | L on the vertical axis with D | Strength: D + L (ASCE 7-22 §2.4.1 Comb. 2; verified `asce7.combo.asd.D_plus_L`). Deflection: D + L, engineering judgement (verified `ej.combo.deflection.D_plus_L`). |
| Outward, inward | L on the horizontal axis, D on the vertical axis | Strength: SRSS of the two moments against one capacity (verified `ej.bending.srss_round`), D + L. Deflection: L only (verified `ej.combo.deflection.L_only`). |
| Upward | L opposes D on the vertical axis | Strength: 0.6D + 1.0L, net (verified `ej.combo.bending.upward`). Deflection: L only. |
| Longitudinal | Axial in the rail | Not checked for the rail (loads-and-envelope.md). |

**Through the rail to post weld (Check 3).** The rail runs over the post;
the post end is coped and welded to the rail's underside. The weld is
modeled as a flat ring of the post's perimeter in the plane of the rail's
underside (W1). At the post both guard load types act at the top of the
post: P, or w·s = 300 lb. A horizontal load V at the rail centerline
reaches the ring as a shear V and a moment V·e, e = D_rail/2. A vertical
load passes through the ring as a uniform normal force; no bearing is
credited (W10). D in Check 3 is the rail's dead load over the span,
w_D·s.

| Direction | On the ring | Combination |
| --- | --- | --- |
| Downward | D + L, uniform compression | D + L |
| Outward, inward | V = L; M = V·e; D uniform compression | D + L |
| Longitudinal | as transverse (the ring is round) | D + L |
| Upward | 1.0L − 0.6D, uniform tension | 0.6D + 1.0L, engineering judgement |

**To the base of the post.** All of D acts as axial load at the top of the
baseplate, the critical section (loads-and-envelope.md, D2 and D11).

Envelope cases: 2 load types × {downward, outward, inward, upward} = 8 for
Checks 1 and 2; 2 × {downward, outward, inward, upward, longitudinal} = 10
for Check 3. All are worked below; the worst of each check is found by
calculation.

## 4. Section properties

### 4.1 Top rail: design wall

360-22 §B4.2 (p. 16.1-24), own reading, PDF: the design wall thickness "shall
be taken equal to the nominal thickness for box sections and HSS produced
according to ASTM A1065/A1065M or ASTM A1085/A1085M. For HSS produced
according to other standards approved for use under this Specification,
the design wall thickness, t, shall be taken equal to 0.93 times the
nominal wall thickness." A500 is neither A1065 nor A1085, so 0.93 applies.
The 2022 text keys on the ASTM standard, not on ERW against SAW.

| Symbol | Equation | Substituted | Result | Citation; source |
| --- | --- | --- | --- | --- |
| t_des | 0.93·t_nom | 0.93 × 0.055 | 0.05115 in | 360-22 §B4.2; own reading, PDF |
| d_i | D − 2·t_des | 2.375 − 2 × 0.05115 | 2.2727 in | geometry |
| D/t | D/t_des | 2.375/0.05115 | 46.43 (46.4321) | 360-22 §B4.1b(g), p. 16.1-22: D outside diameter, t design wall; own reading, PDF |

### 4.2 Top rail: properties from dimensions (D and t_des)

Exact geometry of a circular ring (the formulas of the Manual's Part 17
table of properties of geometric sections; own reading, memory).

| Symbol | Equation | Substituted | Result |
| --- | --- | --- | --- |
| A | π(D² − d_i²)/4 | π(5.640625 − 5.165165)/4 = π × 0.4754597/4 | 0.3734 in² (0.373425) |
| I | π(D⁴ − d_i⁴)/64 | π(31.816650 − 26.678932)/64 = π × 5.137718/64 | 0.2522 in⁴ (0.252197) |
| S | I/(D/2) | 0.252197/1.1875 | 0.2124 in³ (0.212377) |
| Z | (D³ − d_i³)/6 | (13.396484 − 11.738871)/6 = 1.657613/6 | 0.2763 in³ (0.276269) |
| r | √(I/A) | √(0.252197/0.373425) = √0.675362 | 0.8218 in (0.821804) |

Round section: the properties are the same about every axis.

### 4.3 Top rail: weight on the nominal wall

A custom tube's dead weight uses the nominal wall (checks.md, S5-8).

| Symbol | Equation | Substituted | Result | Citation; source |
| --- | --- | --- | --- | --- |
| d_i,nom | D − 2·t_nom | 2.375 − 0.110 | 2.265 in | geometry |
| A_nom | π(D² − d_i,nom²)/4 | π(5.640625 − 5.130225)/4 = π × 0.5104/4 | 0.4009 in² (0.400867) | geometry |
| w_D | ρ·A_nom | 490 lb/ft³ × 0.400867 in² / 144 in²/ft² | 1.364 lb/ft (1.364062) | ρ: own reading, memory |
| w_D | | 1.364062/12 | 0.1137 lb/in (0.113672) | |

### 4.4 Top rail: classification in flexure

| Symbol | Equation | Substituted | Result | Citation; source |
| --- | --- | --- | --- | --- |
| λ_p | 0.07E/F_y | 0.07 × 29,000/50 | 40.60 | 360-22 Table B4.1b Case 20 (p. 16.1-23); verified `aisc360.B4.1b.round_hss.lambda_p` |
| λ_r | 0.31E/F_y | 0.31 × 29,000/50 | 179.8 | same; verified `aisc360.B4.1b.round_hss.lambda_r` |
| §F8 limit | 0.45E/F_y | 0.45 × 29,000/50 | 261.0 | 360-22 §F8; verified `aisc360.F8.applicability` |

λ_p = 40.60 < D/t = 46.43 ≤ λ_r = 179.8: **noncompact** (360-22 §B4.1b;
verified `aisc360.B4.1b.classification`). D/t = 46.43 < 261: §F8 applies.
D/t = 46.43 ≤ 50: no chord D/t stop (S5-3).

### 4.5 Post: Pipe2STD, as published

AISC Shapes Database v16.0, row Pipe2STD, read from AISC's workbook with
the skill's command. Used exactly as published (checks.md).

| W | A | OD | t_nom | t_des | D/t | I | S | Z | r |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3.66 lb/ft | 1.02 in² | 2.375 in | 0.154 in | 0.143 in | 16.6 | 0.627 in⁴ | 0.528 in³ | 0.713 in³ | 0.791 in |

## 5. Check 1: top rail bending

### 5.1 Capacity (the same for every case)

| Symbol | Equation | Substituted | Result | Citation; source |
| --- | --- | --- | --- | --- |
| M_p | F_y·Z | 50 × 0.276269 | 13.81 kip-in (13.8134) | 360-22 Eq. F8-1; verified `aisc360.eq.F8-1` |
| 0.021E/(D/t) | | 0.021 × 29,000/46.4321 = 609/46.4321 | 13.12 ksi (13.1159) | 360-22 Eq. F8-2; verified `aisc360.eq.F8-2.coeff` |
| M_n, local buckling | [0.021E/(D/t) + F_y]·S | (13.1159 + 50) × 0.212377 = 63.1159 × 0.212377 | 13.40 kip-in (13.4043) | 360-22 Eq. F8-2, §F8.2(b), noncompact; verified `aisc360.eq.F8-2` |
| M_n | min(M_p, M_n,LB) | min(13.8134, 13.4043) | 13.40 kip-in = 13,404 lb-in | 360-22 §F8; verified `aisc360.F8.nominal_strength`. **Eq. F8-2 governs.** |
| Ω_b | | | 1.67 | 360-22 §F1(a) (p. 16.1-52); verified `aisc360.F1.omega_b` |
| M_n/Ω_b | M_n/Ω_b | 13,404.34/1.67 | 8,027 lb-in (8,026.55) | 360-22 Eq. B3-2; verified `aisc360.eq.B3-2` |

### 5.2 Moments

| Symbol | Equation | Substituted | Result | Citation; source |
| --- | --- | --- | --- | --- |
| M_D | w_D·L²/8 | 0.113672 × 72²/8 | 73.66 lb-in (73.6594) | Manual Table 3-23 Case 1; verified `aisc_manual.t3-23.case1.M` |
| M_L, concentrated | P·L/4 | 200 × 72/4 | 3,600 lb-in | Manual Table 3-23 Case 7; verified `aisc_manual.t3-23.case7.M` |
| M_L, distributed | w·L²/8 | 4.16667 × 72²/8 | 2,700 lb-in | Manual Table 3-23 Case 1; verified |

Both maxima are at midspan, so they add directly.

### 5.3 Envelope

Downward: M = M_D + M_L. Outward and inward: M = √(M_D² + M_L²).
Upward: M = M_L − 0.6·M_D, with 0.6 × 73.6594 = 44.196 lb-in.
Ratio = M/(M_n/Ω_b) = M/8,026.55.

| Case | Equation, substituted | M (lb-in) | Ratio |
| --- | --- | --- | --- |
| Downward, concentrated | 73.66 + 3,600 | 3,674 (3,673.66) | **0.4577** |
| Downward, distributed | 73.66 + 2,700 | 2,774 (2,773.66) | 0.3456 |
| Outward, concentrated | √(73.66² + 3,600²) | 3,601 (3,600.75) | 0.4486 |
| Outward, distributed | √(73.66² + 2,700²) | 2,701 (2,701.00) | 0.3365 |
| Inward, concentrated | as outward | 3,601 | 0.4486 |
| Inward, distributed | as outward | 2,701 | 0.3365 |
| Upward, concentrated | 3,600 − 44.196 | 3,556 (3,555.80) | 0.4430 |
| Upward, distributed | 2,700 − 44.196 | 2,656 (2,655.80) | 0.3309 |

**Check 1: downward, concentrated controls. 3,674/8,027 = 0.4577 ≤ 1.0,
OK.** Noncompact section, capacity from Eq. F8-2.

## 6. Check 2: top rail deflection

### 6.1 Stiffness and limit

| Symbol | Equation | Substituted | Result | Citation; source |
| --- | --- | --- | --- | --- |
| EI | E·I | 29,000,000 psi × 0.252197 in⁴ | 7.314 × 10⁶ lb-in² (7,313,717) | |
| Δ_allow | L/120 | 72/120 | 0.6000 in | engineering judgement; verified `ej.deflection.limit` |

### 6.2 Components

| Symbol | Equation | Substituted | Result | Citation; source |
| --- | --- | --- | --- | --- |
| Δ_D | 5·w_D·L⁴/(384EI) | 5 × 0.113672 × 26,873,856/(384 × 7,313,717) | 0.005439 in | Manual Table 3-23 Case 1; verified `aisc_manual.t3-23.case1.delta` |
| Δ_L, concentrated | P·L³/(48EI) | 200 × 373,248/(48 × 7,313,717) | 0.2126 in (0.212642) | Manual Table 3-23 Case 7; verified `aisc_manual.t3-23.case7.delta` |
| Δ_L, distributed | 5·w·L⁴/(384EI) | 5 × 4.16667 × 26,873,856/(384 × 7,313,717) | 0.1994 in (0.199351) | Manual Table 3-23 Case 1; verified |

### 6.3 Envelope

Downward: Δ = Δ_D + Δ_L (D + L, engineering-judgement serviceability
combination). Outward, inward and upward: Δ = Δ_L (live load only; dead
load is on the other axis, or is not credited). Ratio = Δ/0.6.

| Case | Δ (in) | Ratio |
| --- | --- | --- |
| Downward, concentrated | 0.005439 + 0.212642 = 0.2181 | **0.3635** |
| Downward, distributed | 0.005439 + 0.199351 = 0.2048 | 0.3413 |
| Outward, concentrated | 0.2126 | 0.3544 |
| Outward, distributed | 0.1994 | 0.3323 |
| Inward, concentrated | 0.2126 | 0.3544 |
| Inward, distributed | 0.1994 | 0.3323 |
| Upward, concentrated | 0.2126 | 0.3544 |
| Upward, distributed | 0.1994 | 0.3323 |

**Check 2: downward, concentrated controls. 0.2181/0.6000 = 0.3635 ≤ 1.0,
OK.**

## 7. Check 3: top rail weld to post

### 7.1 Weld geometry

The ring has the post's perimeter (W1, W3); the post OD is the published
value (S5-4).

| Symbol | Equation | Substituted | Result | Citation; source |
| --- | --- | --- | --- | --- |
| D_post | | | 2.375 in | Shapes Database, Pipe2STD |
| L_w | π·D_post | π × 2.375 | 7.461 in (7.46128) | weld as a line (W3) |
| S_w | π·D_post²/4 | π × 5.640625/4 | 4.430 in² (4.43014) | weld as a line (W3); Manual Part 8, elastic method, own reading, memory |
| e | D_rail/2 | 2.375/2 | 1.1875 in | W1 |
| t_e | 0.707·w | 0.707 × 0.125 | 0.08838 in (0.088375) | 360-22 §J2.2a (p. 16.1-126), in the form the brief fixes (welds.md, "Effective throat"); own reading, PDF |

### 7.2 Allowables per inch of weld

| Symbol | Equation | Substituted | Result | Citation; source |
| --- | --- | --- | --- | --- |
| F_nw | 0.60·F_EXX | 0.60 × 70 | 42.00 ksi | 360-22 Table J2.5, fillet welds, shear (p. 16.1-132); own reading, PDF |
| k_ds | | | 1.0 | branch-to-chord weld (welds.md, W2); 360-22 §J2.4(a)(3) (p. 16.1-130); own reading, PDF |
| Ω | | | 2.00 | 360-22 Table J2.5; own reading, PDF |
| R_n/Ω, weld metal | F_nw·t_e·k_ds/Ω | 42.00 × 0.088375 × 1.0/2.00 | 1.856 kip/in = 1,856 lb/in (1,855.875) | 360-22 Eq. J2-4 (p. 16.1-130); own reading, PDF |
| R_n/Ω, rail wall | 0.60·F_u·t_des,rail/Ω | 0.60 × 62 × 0.05115/2.00 | 0.9514 kip/in = 951.4 lb/in (951.39) | 360-22 §J4.2(b), Eq. J4-4, Ω = 2.00 (p. 16.1-146); own reading, PDF. Shear rupture only, on the design wall (W4, W5, W6). |

Minimum fillet size (W11): thinner part joined, by nominal wall, is the
rail, t_nom = 0.055 in (post t_nom = 0.154 in). 0.055 in is "to 1/4
inclusive", so w_min = 1/8 in (360-22 Table J2.4, p. 16.1-128; own
reading, PDF). w = 1/8 in ≥ 1/8 in: **OK**. The §J2.2b(b) maximum size
does not apply to a T-joint (W11).

### 7.3 Loads at the ring

| Symbol | Equation | Substituted | Result |
| --- | --- | --- | --- |
| D | w_D·s | 1.364062 lb/ft × 6 ft | 8.184 lb (8.18437) |
| L, concentrated | P | | 200 lb |
| L, distributed | w·s | 50 × 6 | 300 lb |

D here is the top rail's dead load only (welds.md, W10).

### 7.4 Forces per inch and ratios

Definitions, as positive magnitudes:

- f_a: the axial (vertical) force per inch, uniform around the ring.
  Downward (D + L)/L_w; horizontal cases D/L_w; upward (L − 0.6D)/L_w,
  with 0.6D = 4.9106 lb.
- f_v = V/L_w: the horizontal shear per inch, taken as uniform (W3).
- f_b = V·e/S_w: the bending force per inch at the extreme fiber.
- f_n: the total force per inch normal to the ring's plane at the
  governing point. Horizontal cases: f_b + f_a on the compression side of
  bending, f_b − f_a on the tension side; the compression side is larger,
  so it governs (W10). Vertical cases: f_n = f_a, uniform.
- f_r = √(f_v² + f_n²): the resultant per inch at the governing point.
- Weld ratio = f_r/1,855.875. Base metal ratio = f_v/951.39 (the in-plane
  force only; the normal components go to the chord wall, W5 and W7). The
  vertical cases have no in-plane force, so no base metal ratio.
- Case ratio = the larger of the two.

**Concentrated, L = V = 200 lb.** V·e = 200 × 1.1875 = 237.5 lb-in.

| Case | f_a | f_v | f_b | f_n | f_r | Fiber | Weld ratio | Base ratio | Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Downward | 208.184/7.46128 = 27.90 | — | — | 27.90 | 27.90 | uniform | 0.01503 | — | 0.01503 |
| Outward | 8.184/7.46128 = 1.097 | 200/7.46128 = 26.81 | 237.5/4.43014 = 53.61 | 54.71 | √(26.81² + 54.71²) = 60.92 | compression side | 0.03283 | 0.02817 | 0.03283 |
| Inward | 1.097 | 26.81 | 53.61 | 54.71 | 60.92 | compression side | 0.03283 | 0.02817 | 0.03283 |
| Upward | (200 − 4.911)/7.46128 = 26.15 | — | — | 26.15 | 26.15 | uniform | 0.01409 | — | 0.01409 |
| Longitudinal | 1.097 | 26.81 | 53.61 | 54.71 | 60.92 | compression side | 0.03283 | 0.02817 | 0.03283 |

**Distributed, L = V = w·s = 300 lb.** V·e = 300 × 1.1875 = 356.25 lb-in.

| Case | f_a | f_v | f_b | f_n | f_r | Fiber | Weld ratio | Base ratio | Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Downward | 308.184/7.46128 = 41.30 | — | — | 41.30 | 41.30 | uniform | 0.02226 | — | 0.02226 |
| Outward | 1.097 | 300/7.46128 = 40.21 | 356.25/4.43014 = 80.42 | 81.51 | √(40.21² + 81.51²) = 90.89 | compression side | **0.04897** | 0.04226 | **0.04897** |
| Inward | 1.097 | 40.21 | 80.42 | 81.51 | 90.89 | compression side | 0.04897 | 0.04226 | 0.04897 |
| Upward | (300 − 4.911)/7.46128 = 39.55 | — | — | 39.55 | 39.55 | uniform | 0.02131 | — | 0.02131 |
| Longitudinal | 1.097 | 40.21 | 80.42 | 81.51 | 90.89 | compression side | 0.04897 | 0.04226 | 0.04897 |

All forces in lb per inch of weld. Tension side of the horizontal cases,
for the record: f_n = f_b − f_a = 52.51 (concentrated) and 79.32
(distributed); f_r = 58.96 and 88.93 lb/in. Both are below the
compression side.

Upward: 0.6D = 4.91 lb is less than L in both load types, so there is net
tension and the case is checked.

### 7.5 Result

**Check 3: outward, distributed controls (inward and longitudinal tie
exactly). Weld metal: 90.89/1,856 = 0.04897. Rail wall base metal:
40.21/951.4 = 0.04226. Ratio 0.04897 ≤ 1.0, OK; weld metal governs.**
Minimum size OK.

### 7.6 For information: the rail wall as a chord (not checked in v1)

Not a test value, and not part of Check 3 (W7; the chord limit states
become a check in slice 6). Recorded because this case is where W7 is
weakest.

Limits of applicability, 360-22 Tables K3.1A and K4.1A (pp. 16.1-164,
16.1-168; own reading, PDF): chord D/t = 46.43 ≤ 50; branch D_b/t_b = 16.6
≤ 50 and ≤ 0.05E/F_yb = 41.4; width ratio D_b/D = 1.0; F_y = 50 ksi ≤ 52
ksi; F_y/F_u = 50/62 = 0.806, over the 0.8 limit, but the table's note
accepts A500 Gr C by name.

Strengths with β = 1.0, γ = D/(2t) = 23.22, Q_f = 1.0 (the simple-span
rail has no moment at the post), Ω = 1.67. The PDF's text layer drops the
Greek letters of these equations, so their β and γ terms are from my
memory of the equations and are **not confirmed against the page**:

| Limit state | Equation | Allowable | Demand (distributed) | Ratio |
| --- | --- | --- | --- | --- |
| Chord plastification, branch axial (K3-2) | F_y·t²(3.1 + 15.6β²)γ^0.2 | 4.588/1.67 = 2.748 kip | 300 + 8.2 = 308 lb (downward) | 0.11 |
| Chord plastification, out-of-plane moment (K4-3) | F_y·t²·D_b·3.0/(1 − 0.81β) | 4.906/1.67 = 2.937 kip-in | 356 lb-in (transverse) | 0.12 |
| Chord plastification, in-plane moment (K4-1) | 5.39·F_y·t²·γ^0.5·β·D_b | 8.069/1.67 = 4.832 kip-in | 356 lb-in (longitudinal) | 0.07 |

These run at about 2.3 to 2.5 times Check 3's reported ratio, and still
far below 1.0.

## 8. Post group: D at the post

Post properties are the published row in section 4.5.

| Symbol | Equation | Substituted | Result | Citation; source |
| --- | --- | --- | --- | --- |
| h − t_p | | 42 − 0.5 | 41.5 in | top of baseplate to rail centerline |
| D_post | W·(h − t_p) | 3.66 lb/ft × 41.5 in/12 | 12.66 lb (12.6575) | tabulated weight (loads-and-envelope.md, D2) |
| D, rail | w_D·s | 1.364062 × 6 | 8.184 lb (8.18437) | section 4.3 |
| D, intermediate rail | | none | 0 | case input |
| D at the post | w_D·s + D_post | 8.18437 + 12.6575 | 20.84 lb (20.8419) | loads-and-envelope.md |

## 9. Summary

| Check | Controlling case | Demand | Capacity | Ratio | |
| --- | --- | --- | --- | --- | --- |
| Section | noncompact in flexure, D/t = 46.43 against λ_p = 40.60 | | | | flag |
| 1. Top rail bending | downward, concentrated | 3,674 lb-in | 8,027 lb-in (Eq. F8-2) | 0.4577 | OK |
| 2. Top rail deflection | downward, concentrated | 0.2181 in | 0.6000 in | 0.3635 | OK |
| 3. Top rail weld to post | outward, distributed (ties with inward and longitudinal) | 90.89 lb/in | 1,856 lb/in (weld metal) | 0.04897 | OK |
| 3, rail wall base metal | same case | 40.21 lb/in | 951.4 lb/in | 0.04226 | OK |
| 3, minimum fillet size | | 1/8 in | 1/8 in minimum | | OK |
| Post group | D at the post | 20.84 lb | | | |

## 10. Values from my own reading

None of these has a verified registry entry.

| Value | Used | Document, edition, section | Source and confidence |
| --- | --- | --- | --- |
| F_y = 50 ksi, A500 Gr C round | Classification, Check 1 | Manual, 16th Ed., Table 2-4 | Memory. **Not certain.** I believe the 16th Edition prints 50 ksi for round as well as rectangular A500 Gr C, following ASTM A500-21; the 15th Edition printed 46 ksi for round. Open question 1. |
| F_u = 62 ksi, A500 Gr C round | Check 3 rail wall | Manual, 16th Ed., Table 2-4 | Memory. Confident: 62 ksi in both editions. |
| F_u = 60 ksi, A53 Gr B | W5 guard, noted only | Manual, 16th Ed., Table 2-4 | Memory. Confident. |
| t_des = 0.93·t_nom | Section | 360-22 §B4.2, p. 16.1-24 | PDF, read directly. |
| D outside diameter, t design wall, for D/t | Section | 360-22 §B4.1b(g), p. 16.1-22 | PDF, read directly. |
| A, I, S, Z, r of a circular ring | Section | Manual, 16th Ed., Part 17, properties of geometric sections | Memory for the reference; the formulas are exact geometry. |
| ρ = 490 lb/ft³ | Rail weight | Manual, 16th Ed. (basis of tabulated weights) | Memory. Confident of the value; not sure of the table number. |
| F_EXX = 70 ksi | Check 3 | E70XX classification (AWS A5.1); 360-22 Table J2.5 | Memory. Confident. |
| F_nw = 0.60·F_EXX, Ω = 2.00 | Check 3 | 360-22 Table J2.5, p. 16.1-132 | PDF, read directly. |
| R_n = F_nw·A_we·k_ds | Check 3 | 360-22 Eq. J2-4, p. 16.1-130 | PDF, read directly. k_ds = 1.0 is the brief's decision (W2). |
| t_e = 0.707·w | Check 3 | 360-22 §J2.2a, p. 16.1-126 | The PDF gives the definition (shortest distance from root to face); 0.707 is the equal-leg geometry in the form the brief fixes. |
| Minimum fillet 1/8 in to 1/4 in thickness | Check 3 | 360-22 Table J2.4, p. 16.1-128 | PDF, read directly. |
| R_n = 0.60·F_u·A_nv, Ω = 2.00 | Check 3 rail wall | 360-22 Eq. J4-4, p. 16.1-146 | PDF, read directly. |
| S_w = πD²/4, weld as a line | Check 3 | Manual, 16th Ed., Part 8, elastic method | Memory; the brief fixes the form (W3). |
| Chord D/t ≤ 50 | Section, stop | 360-22 Table K3.1A, p. 16.1-164; Table K4.1A, p. 16.1-168 | PDF, read directly. |
| Table K3.1 and K4.1 strengths | Section 7.6, information only | 360-22 pp. 16.1-163, 16.1-167 | Memory for β and γ; the PDF's text layer drops them. Not test values. |
| Pipe2STD row | Post group, Check 3 ring | AISC Shapes Database v16.0 | AISC's workbook, the skill's command. |

## 11. Open questions

1. **F_y for round A500 Gr C.** The slice plan has Micah verifying the
   A500 Gr B and Gr C round F_y and F_u before this calc runs (S5-5). No
   such entry was among the verified entries at this commit, so F_y = 50
   ksi and F_u = 62 ksi here are my own reading, and I am not certain of
   the 50. Sensitivity, if Table 2-4 reads 46 ksi: λ_p = 44.13, still
   noncompact; M_p = 12.71 kip-in; Eq. F8-2 gives M_n = 12.55 kip-in and
   still governs; M_n/Ω_b = 7,518 lb-in; Check 1 = 0.4887 (downward,
   concentrated). Section properties, Check 2, Check 3 and D at the post
   do not change (F_u is 62 ksi either way).
2. **The chord wall carries most of Check 3's force and is not checked.**
   Of the governing 90.89 lb/in, 81.51 lb/in is normal to the rail wall
   and goes to the W7 assumption; the base metal line sees only the 40.21
   lb/in in-plane shear. Section 7.6 puts the chord plastification ratios
   near 0.11 to 0.12, from equations I could not confirm against the page.
   No change asked for; this is the plan's own reason for extending case 6
   in slice 6.
3. **The weld leg is 2.4 times the rail's design wall** (0.125 in against
   0.05115 in). The rail wall allowable, 951 lb/in, is 51% of the weld
   metal's, so the weld can never develop its strength on this wall; the
   check handles that through the base metal line. Stated so the reader
   is not surprised by a 1/8 in fillet passing Table J2.4 on a 0.055 in
   wall.
4. **Welding a 0.055 in wall.** 360-22 §J2 adopts AWS D1.1, which from
   memory does not cover steel under 1/8 in thick (AWS D1.3 covers sheet
   steel). Table J2.4's first row, "to 1/4 inclusive", has no lower
   bound, so the tool's pass/fail line reads OK. The plan notes this is
   not a stocked size and the case exists to reach Eq. F8-2; I flag it
   only because a real custom tube this thin would raise it. I am not
   sure of the D1.1 thickness limit.
5. **Local effect of the 200 lb load on a 0.051 in wall** (denting or
   ovalization at the point of load). No 360-22 provision covers it and
   the brief does not mention it. Not checked.
6. **Key mapping I assumed** (section 13): `post.P_D_lb` is D at the
   post, 20.84 lb; `check3.t_min_in` is the nominal thickness of the
   thinner part joined that enters Table J2.4, 0.055 in; `check3.f_a` in
   the upward case is the net tension (L − 0.6D)/L_w; `check3.ratio` is
   the larger of the weld metal and base metal ratios.

## 12. Review checklist (docs/brief/verification.md)

1. **Loads complete.** Rail dead load on the nominal wall, carried into
   Checks 1, 2 and 3 and to the post. Post dead load over h − t_p. No
   intermediate rail, so no component load and no intermediate dead load.
   Both guard load types in every check. Baseplate weight belongs to the
   reactions only (not covered).
2. **Direction and worst case.** Checks 1 and 2: downward, outward,
   inward and upward for both load types, 8 cases each; longitudinal is
   axial in the rail and not checked. Check 3: all five directions, 10
   cases, both extreme fibers evaluated in the horizontal cases. Each
   worst case is found by calculation: downward concentrated for Checks 1
   and 2, a horizontal distributed case for Check 3.
3. **Checks complete.** Section 2 lists each limit state and why it is or
   is not checked. Not checked, by the brief: shear, rail axial force, the
   chord wall (W7). Not in the brief: the local effect of P on the thin
   wall, and the welding-code thickness limit (open questions 4 and 5).
4. **Geometry.** Rail span L = 72 in for Checks 1 and 2. Weld ring on the
   post's published OD, 2.375 in; e = D_rail/2 = 1.1875 in. Tributary
   length s = 72 in. D_post over h − t_p = 41.5 in. Properties on t_des =
   0.05115 in; weight and Table J2.4 on t_nom = 0.055 in; rail fusion face
   on t_des.
5. **Method and equations.** §B4.2 at 0.93 (A500 is not A1065 or A1085).
   Classification before capacity: noncompact, so Eq. F8-2, compared with
   M_p; the §F8 limit and λ_r checked. SRSS for the horizontal cases.
   Weld: Eq. J2-4 with k_ds = 1.0, t_e = 0.707w; base metal Eq. J4-4 on
   the in-plane shear only. Chord D/t ≤ 50 checked.
6. **Assumptions.** Simple-span rail; loads through the rail centerline;
   flat ring of the post's perimeter at the rail's underside, no bearing
   credit; shear taken as uniform around the ring; span as tributary
   length; chord wall not checked. All are the brief's.
7. **Code editions.** AISC 360-22 throughout, read from the 2022 text,
   pages cited. Manual, 16th Edition. ASCE 7-22. Shapes Database v16.0.
8. **Magnitude sense.** A = 0.373 in² is 37% of Pipe2STD's 1.02 in² on
   36% of its wall, as expected for the same OD. w_D = 1.36 lb/ft against
   3.66 lb/ft. M_n from Eq. F8-2 is 3% below M_p, as expected just past
   λ_p. Rail deflection 0.22 in on 6 ft. Weld forces under 100 lb/in
   against allowables near 1,000 to 1,900 lb/in. Units: lb, in, lb-in,
   ksi; kip-in converted to lb-in before each ratio.
9. **Governing case.** Checks 1 and 2: downward, concentrated, the only
   case where live and dead load share an axis, and P·L/4 exceeds w·L²/8
   at a 6 ft span (3,600 against 2,700 lb-in). Check 3: horizontal,
   distributed, since w·s = 300 lb exceeds P = 200 lb at the post and the
   V·e moment dominates. Both as expected.

## 13. Values file mapping

Every key in tests/cases/independent/case-06.toml is filled. The inward
cases equal the outward cases, and Check 3's longitudinal cases equal its
transverse cases, because the section and the ring are round.

Values computed here that have no key (a check or value one side has and
the other may not):

- The classification itself: λ_p = 40.60, λ_r = 179.8, the §F8 limit
  261.0, and the result "noncompact".
- M_p = 13,813 lb-in, and which equation governs M_n (Eq. F8-2).
- The rail's nominal wall and nominal-wall area, A_nom = 0.4009 in².
- The component moments and deflections: M_D = 73.66 lb-in, Δ_D =
  0.005439 in.
- Check 3's dead load at the ring, D = w_D·s = 8.184 lb, and the
  tension-side forces in the horizontal cases.
- The chord D/t limit check, 46.43 ≤ 50.
