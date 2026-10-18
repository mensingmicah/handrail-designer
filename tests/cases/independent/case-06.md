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

## Check 3 chord wall (slice 6)

Independent calc of the `check3_chord` group only: the AISC 360-22 Chapter K
chord limit states of the round rail wall at the round post (S6-10). Every
other group in this file was worked by an earlier session; this section
reads none of it and derives what it needs (rail weight, Check 1 moments)
afresh.

- Case: tests/cases/case-06.toml (inputs read with the `hand` and
  `independent` tables stripped).
- Date: 2026-10-17. Model: Claude (Anthropic); model id given in the
  session report, not recorded in the repo.
- Branch slice-6, commit 75c2813d1d37cb314f1f5a9fff7de13141d05b10 (equal to
  origin/slice-6, clean tree, checked before starting).
- Sources read: docs/BRIEF.md and every file in docs/brief/; CONTEXT.md;
  docs/plans/slice-6.md (decisions only; its planning figures were not
  used); the verified registry entries (command in the skill); the
  Pipe2STD row of data/aisc-shapes-database-v16.0.xlsx; out/aisc-360-22.pdf
  (§K1 pp. 16.1-157 to 16.1-160, §K3 Tables K3.1 and K3.1A pp. 16.1-163 to
  16.1-164, §K4 Tables K4.1 and K4.1A pp. 16.1-167 to 16.1-168), read
  through `pdftotext`; the pending key names and the comment header of
  tests/cases/independent/case-06.toml (step 7). Nothing else.
- Arithmetic: Python standard library, full precision; values below are
  rounded to 4 significant figures for reporting only.

### C1. Inputs

| Symbol | Value | Source |
| --- | --- | --- |
| Rail (chord) | custom round tube, OD 2.375 in, t_nom = 0.055 in, A500 Gr C | case input |
| Post (branch) | Pipe2STD, A53 Gr B | case input |
| Span L | 6'-0" = 72 in | case input |
| Intermediate rail | none | case input |
| Guard loads | P = 200 lb; w = 50 lb/ft = 4.1667 lb/in; no exemption | case has no `[loads]`: defaults, verified `asce7.guard.concentrated`, `asce7.guard.uniform` |
| Combinations | D + L (1.0, 1.0); upward 0.6D + 1.0L | verified `asce7.combo.asd.D_plus_L`, `ej.combo.bending.upward` |
| E | 29,000 ksi | verified `material.steel.E` |
| Rail Fy / Fu | 50 / 62 ksi | own reading: AISC Manual 16th Ed. Table 2-4, ASTM A500/A500M-21 Gr C (round and shaped now equal), from memory |
| Post Fyb | 35 ksi | verified `material.A53_GrB.Fy` |
| Post Fub | 60 ksi | own reading: AISC Manual 16th Ed. Table 2-4, A53 Gr B, from memory (used only in the Fyb/Fub limit) |
| Pipe2STD | OD = Db = 2.375 in, t_des = tb = 0.143 in, D/t = 16.6 | AISC Shapes Database v16.0 row |
| θ | 90° (post perpendicular to rail) | geometry; T-connection per §K3(a) and §K4(a) |

### C2. Limit states considered (from the code)

The joint is a single round branch (post) welded perpendicular to the
underside of a continuous round chord (rail): a T-connection, AISC 360-22
§K3(a) for axial branch load and §K4(a) for branch moment. Every limit
state Chapter K could apply:

| Limit state | Provision | Applies? Why |
| --- | --- | --- |
| Chord plastification, branch axial | Table K3.1, Eq. K3-2 (T- and Y-) | Yes: downward and upward cases (and the axial D in the lateral cases) |
| Chord plastification, cross-connection | Eq. K3-3 | No: one branch only, punching load equilibrated by chord beam shear (§K3(a)) |
| K-connection plastification | Eqs. K3-4, K3-5 | No: one branch |
| Shear yielding (punching), axial | Eq. K3-1 | Only when Db < D − 2t. Here Db = 2.375 in, D − 2t = 2.273 in: does not apply |
| Chord plastification, in-plane moment | Table K4.1, Eq. K4-1 | Yes: longitudinal case (moment in the plane of rail and post) |
| Punching, in-plane moment | Eq. K4-2 | Same condition as K3-1: does not apply |
| Chord plastification, out-of-plane moment | Eq. K4-3 | Yes: outward and inward cases |
| Punching, out-of-plane moment | Eq. K4-4 | Does not apply (as above) |
| Combined axial and moments | Eq. K4-5 | Yes: every case |
| Chord-stress interaction Qf | §K1.3, Eqs. K1-3 and K1-6 | Yes: in K3-2, K4-1, K4-3 (plan S6-10 sets Mro) |
| End distance | §K1.4, Eq. K1-8 | No: interior post (stated assumption, output.md); S6-13 adds nothing |
| Plate-to-round HSS | Table K2.1 | No: no plate; the branch is an HSS. Not used for the guard load's own local effect either (see Q4) |
| Branch local yielding from uneven load | Table K3.2 (K3-9) | No: rectangular branches only |
| Rectangular chord limit states, §J10 | Table K4.2, §J10 | No: round chord |
| Weld of branch to chord | §K5, Table K5.2 | Not in this group: Check 3's weld lines (Table K5.2 is axial only, 0.1 ≤ β ≤ 0.5, so S6-8 keeps the ring model) |
| Branch and chord as members | Chapters E, F, H | Not in this group: Checks 1 and 5 |

Limits of applicability (Tables K3.1A and K4.1A, T-connections; §K1.3):

| Limit | Value | Result |
| --- | --- | --- |
| D/t ≤ 50 | 2.375/0.05115 = 46.43 | OK |
| Db/tb ≤ 50 | 16.6 (published) | OK |
| Db/tb ≤ 0.05E/Fyb (compression branch) | 0.05(29,000)/35 = 41.43 | OK |
| 0.2 < Db/D ≤ 1.0 | 2.375/2.375 = 1.000 | OK (at the upper bound) |
| Fy, Fyb ≤ 52 ksi | 50, 35 | OK |
| Fy/Fu ≤ 0.8 | 50/62 = 0.8065 | Over 0.8; passes only by the tables' note "ASTM A500/A500M Grade C is acceptable" (S6-13, S6-16 item 7) |
| Fyb/Fub ≤ 0.8 | 35/60 = 0.5833 | OK |

### C3. Loads and load path

All guard loads act through the rail centerline (brief, Check 3 weld
model). The branch actions at the chord wall are the weld envelope's (W10),
by S6-10: the load reaches the post through the rail wall at the post.

- **Rail dead load.** Custom tube weight on the nominal wall (checks.md;
  S5-8): A_nom = π·t_nom·(OD − t_nom) = π(0.055)(2.320) = 0.4009 in²;
  steel 490 lb/ft³ = 0.28356 lb/in³ (own reading: AISC Manual, steel unit
  weight 490 pcf, memory); w_D = 0.4009 × 0.28356 = 0.11367 lb/in = 1.364
  lb/ft.
- **D in Check 3** = w_D·L = 0.11367 × 72 = 8.184 lb (welds.md W10: the
  top rail's dead load over the span; no intermediate rail).
- **Guard load reaching the post (L).** Concentrated: P = 200 lb applied at
  the post. Distributed: w·s = 4.1667 × 72 = 300.0 lb, the tributary span
  of an interior post. Both load types are run in every case.
- **Eccentricity.** e = D_rail/2 = 2.375/2 = 1.1875 in (S6-10, W1).

| Case | Branch action on the rail wall | Combination | Qf basis (S6-10) |
| --- | --- | --- | --- |
| Downward | Pr = D + L, branch compression | D + L | Check 1 downward vertical moment; underside in compression, Eq. K1-3 |
| Upward | Pr = L − 0.6D, branch tension | 0.6D + 1.0L | underside in tension, Qf = 1.0 |
| Outward, inward | Mr-op = L·e; Pr = D | D + L | Check 1 dead-load vertical moment only, Eq. K1-3 |
| Longitudinal | Mr-ip = L·e; Pr = D | D + L | dead-load vertical moment only, Eq. K1-3 |

Outward and inward are identical (round chord, round branch, no sign
dependence in K4-3 or Qf); both are listed.

Check 1 moments for Mro (simple span, L = 72 in; verified
`aisc_manual.t3-23.case1.M` and `aisc_manual.t3-23.case7.M`):

- M_D = w_D·L²/8 = 0.11367 × 5184/8 = 73.66 lb-in
- Concentrated, midspan: P·L/4 = 200 × 72/4 = 3,600 lb-in
- Distributed: w·L²/8 = 4.1667 × 5184/8 = 2,700 lb-in
- Downward Mro: concentrated 3,600 + 73.66 = 3,674 lb-in; distributed
  2,700 + 73.66 = 2,774 lb-in.
- Lateral cases Mro = M_D = 73.66 lb-in. Pro = 0 in every case (S6-10).

### C4. Section properties of the chord (rail)

- t = t_des = 0.93·t_nom = 0.93 × 0.055 = 0.05115 in. AISC 360-22 §B4.2
  (HSS other than A1065 and A1085: 0.93 of nominal); own reading, memory.
- Di = D − 2t = 2.375 − 0.1023 = 2.273 in
- Ag = π/4·(D² − Di²) = 0.3734 in² (not used: Pro = 0)
- I = π/64·(D⁴ − Di⁴) = 0.2522 in⁴; S = I/(D/2) = 0.2124 in³ (exact hollow
  circle on the design wall, checks.md custom round tube ruling)
- β = Db/D = 2.375/2.375 = 1.000 (§K1.1)
- γ = D/(2t) = 2.375/(2 × 0.05115) = 23.22 (§K1.1)
- γ^0.2 = 1.876; γ^0.5 = 4.818; 3.0/(1 − 0.81β) = 3.0/0.19 = 15.79

### C5. Case-independent capacities (Qf = 1, θ = 90°, sin θ = 1)

All AISC 360-22, read from out/aisc-360-22.pdf (equation forms
reconstructed where the text extraction lost symbols; they match my
memory of the 360-16 tables, renumbered).

- **Eq. K3-2** (Table K3.1, chord plastification, T-connection):
  Pn·sinθ = Fy·t²·(3.1 + 15.6β²)·γ^0.2·Qf
  = 50 × 0.05115² × (3.1 + 15.6) × 1.876 × Qf = 4.588·Qf kips.
  Ω = 1.67 (Table K3.1). Pc = 4,588/1.67 = 2,748·Qf lb.
- **Eq. K4-1** (Table K4.1, in-plane, chord plastification):
  Mn-ip = 5.39·Fy·t²·γ^0.5·β·Db·sinθ·Qf
  = 5.39 × 50 × 0.05115² × 4.818 × 1.0 × 2.375 × Qf = 8.069·Qf kip-in.
  Ω = 1.67. Mc-ip = 4,832·Qf lb-in.
- **Eq. K4-3** (Table K4.1, out-of-plane, chord plastification):
  Mn-op = Fy·t²·Db·[3.0/(1 − 0.81β)]·Qf/sinθ
  = 50 × 0.05115² × 2.375 × 15.79 × Qf = 4.906·Qf kip-in.
  Ω = 1.67. Mc-op = 2,937·Qf lb-in.
- Punching (Eqs. K3-1, K4-2, K4-4, Ω = 1.58): not computed, Db = 2.375 in
  is not < D − 2t = 2.273 in.
- **Qf** (§K1.3(b), Eq. K1-3): Qf = 1 − 0.3U(1 + U) ≤ 1.0, with
  U = |Pro/(Fc·Ag) + Mro/(Fc·S)| ≤ 1.0 (Eq. K1-6) and Fc = 0.60Fy for ASD
  (§K1.1 definitions) = 30 ksi. Fc·S = 30 × 0.2124 = 6.371 kip-in.
- **Eq. K4-5**: Pr/Pc + (Mr-ip/Mc-ip)² + Mr-op/Mc-op ≤ 1.0, with Pc from
  Table K3.1 at the case's Qf.

### C6. Every case

Downward (D + L), branch compression, Mr = 0:

| Load type | Mro (lb-in) | U = Mro/(Fc S) | Qf | Pr = D + L (lb) | Pc = 2,748·Qf (lb) | Ratio Pr/Pc |
| --- | --- | --- | --- | --- | --- | --- |
| concentrated | 3,674 | 0.5766 | 0.7273 | 8.184 + 200 = 208.2 | 1,998 | 0.1042 |
| distributed | 2,774 | 0.4353 | 0.8125 | 8.184 + 300 = 308.2 | 2,233 | **0.1380** |

Qf, concentrated: 1 − 0.3(0.5766)(1.5766) = 0.7273. Distributed:
1 − 0.3(0.4353)(1.4353) = 0.8125.

Upward (0.6D + 1.0L), branch tension, Qf = 1.0 (connecting surface in
tension, §K1.3(a)), Mr = 0:

| Load type | Pr = L − 0.6D (lb) | Pc (lb) | Ratio |
| --- | --- | --- | --- |
| concentrated | 200 − 4.911 = 195.1 | 2,748 | 0.07101 |
| distributed | 300 − 4.911 = 295.1 | 2,748 | 0.1074 |

Net tension in both (L > 0.6D), so the case is checked.

Outward and inward (identical), Mro = M_D = 73.66 lb-in:
U = 73.66/6,371 = 0.01156; Qf = 1 − 0.3(0.01156)(1.01156) = 0.9965.
Pr = D = 8.184 lb; Pc = 2,748 × 0.9965 = 2,738 lb; Pr/Pc = 0.002989.
Mc-op = 2,937 × 0.9965 = 2,927 lb-in.

| Load type | Mr-op = L·e (lb-in) | Mr-op/Mc-op | Ratio (K4-5) |
| --- | --- | --- | --- |
| concentrated | 200 × 1.1875 = 237.5 | 0.08114 | 0.08413 |
| distributed | 300 × 1.1875 = 356.3 | 0.1217 | 0.1247 |

Longitudinal, same Qf = 0.9965, Pr/Pc = 0.002989;
Mc-ip = 4,832 × 0.9965 = 4,815 lb-in:

| Load type | Mr-ip = L·e (lb-in) | (Mr-ip/Mc-ip)² | Ratio (K4-5) |
| --- | --- | --- | --- |
| concentrated | 237.5 | 0.002433 | 0.005423 |
| distributed | 356.3 | 0.005475 | 0.008464 |

### C7. Summary

| Case | Concentrated | Distributed |
| --- | --- | --- |
| Downward | 0.1042 | **0.1380** |
| Upward | 0.07101 | 0.1074 |
| Outward | 0.08413 | 0.1247 |
| Inward | 0.08413 | 0.1247 |
| Longitudinal | 0.005423 | 0.008464 |

Controlling: **downward, distributed**, chord plastification (Eq. K3-2)
in the Eq. K4-5 interaction, ratio 0.138 ≤ 1.0, OK. Qf decides the order:
at Qf = 1 the downward distributed case would be 308.2/2,748 = 0.112,
below the outward distributed case's 0.125; the downward case's own rail
moment lowers its Qf to 0.81.

### C8. Values from my own reading (no verified entry)

| Value | Used | Source |
| --- | --- | --- |
| A500 Gr C Fy = 50, Fu = 62 ksi | chord Fy, limits | AISC Manual 16th Ed. Table 2-4 and ASTM A500-21, memory |
| A53 Gr B Fu = 60 ksi | Fyb/Fub limit only | AISC Manual 16th Ed. Table 2-4, memory |
| t_des = 0.93·t_nom | chord t | AISC 360-22 §B4.2, memory |
| Steel 490 lb/ft³ | rail weight, D | AISC Manual, memory |
| Eqs. K3-1, K3-2, K4-1 to K4-5; Ω = 1.67 and 1.58 | capacities | AISC 360-22 Tables K3.1 and K4.1, pp. 16.1-163 and 16.1-167 (PDF, symbols reconstructed) |
| Eqs. K1-3, K1-6; Fc = 0.60Fy (ASD) | Qf | AISC 360-22 §K1.1 and §K1.3, pp. 16.1-158 to 16.1-160 (PDF) |
| β, γ definitions | parameters | AISC 360-22 §K1.1 (PDF) |
| Punching condition Db < D − 2t | punching not checked | Tables K3.1 and K4.1 (PDF) |
| Limits of applicability, A500 Gr C note | C2 | Tables K3.1A and K4.1A, §K1.3 (PDF) |

### C9. Open questions and findings for Micah

- **Q1. An inclined guard load raises the chord interaction by about
  38%.** Eq. K4-5 is linear in Pr and Mr-op, so a load in the
  transverse-vertical plane, inclined downward and outward, adds the two
  ratios about as a root-sum-square. Scanning the angle (with Qf following
  the inclined case's vertical moment), the distributed load gives 0.190 at
  51° below horizontal, against 0.138 for the worst orthogonal case; the
  concentrated load 0.138 at 56°; upward-and-outward 0.162. W10's reason
  for no inclined case (under 10% on the weld, because the weld demand is
  V·e) does not carry over to this interaction, though S6-10 reuses W10's
  envelope. Not recorded in the values file (the plan's five cases are);
  no result changes at these magnitudes. A ruling or a sentence in the
  brief would close it.
- **Q2. Concentrated load in two places at once.** The branch actions put
  P at the post, while Qf takes Check 1's moment with P at midspan. They
  cannot occur together; S6-10 chooses this as a bound, so it is
  conservative and I applied it as written.
- **Q3. Pro = 0 in the longitudinal case.** The rail carries the
  longitudinal load axially (up to 300 lb). §K1.3 takes Pro on the side of
  the joint with lower compression stress for round HSS, which here is
  the side in tension or unloaded, so Pro = 0 is at or above the code's
  Qf penalty. No issue; noted because the plan does not say why.
- **Q4. Local effect of the guard load on the thin rail wall away from the
  post** (plan open item 5, issue #28): no Chapter K provision is written
  for a hand load; not computed.
- **Q5. Brief inconsistency on A500 Gr C round Fy.** welds.md W5 lists
  "A500 Gr C round (1.35)" for Fu/Fy, which is 62/46, the pre-2021 round
  value; checks.md S5-13 and the plan use 50/62. I used 50 ksi. At 46 ksi
  every chord capacity here scales by 0.92 and Fc changes too.
- **Q6. Key `check3_chord.punching` has no listed words** in the values
  file's header. I recorded `false` (punching does not apply, Db not <
  D − 2t). The test may expect another form.

### C10. Review checklist (docs/brief/verification.md, items 1 to 9)

1. **Loads complete.** Rail dead load over the span (the only D at this
   joint; no intermediate rail, and the post's own weight is below the
   joint); both guard load types in every case. The component load does
   not reach Check 3.
2. **Direction and worst case.** Five orthogonal cases, both load types,
   each worked; downward distributed governs by calculation. Inward is
   computed equal to outward. The inclined load (Q1) is outside the plan's
   envelope and flagged.
3. **Checks complete.** Every Chapter K limit state for a round
   T-connection listed in C2; punching excluded by its own condition;
   applicability limits all checked.
4. **Geometry.** e = D_rail/2 = 1.1875 in; span 72 in for Check 1 moments
   and tributary length; θ = 90°; β = 1.000; γ on the design wall.
5. **Method and equations.** T-connection equations (not cross); Ω = 1.67
   for plastification; Qf by Eq. K1-3 with Fc = 0.6Fy (ASD) and the
   S6-10 moment per case; Qf = 1 for the upward case; K4-5 with the
   in-plane term squared.
6. **Assumptions.** Interior post (no end-distance reduction); Mro as
   S6-10's bound; Pro = 0 (Q3); loads at the rail centerline.
7. **Code editions.** AISC 360-22 throughout for Chapter K, §B4.2 and
   §K1; AISC Manual 16th Ed. for Table 2-4 and steel weight; ASCE 7-22 for
   loads and combinations.
8. **Magnitude sense.** Pc ≈ 2.7 kips and Mc-op ≈ 2.9 kip-in against
   branch forces of 0.2 to 0.3 kips: ratios 0.01 to 0.14, consistent with
   S6-1's "tens to hundreds of pounds against capacities in kips" and the
   S5-3 order-of-magnitude estimate for a 2.375 in tube near D/t = 46.
9. **Governing case.** Downward, distributed. I expected an outward case
   from the brief's planning description; it is not, because the downward
   case's own vertical moment cuts Qf to 0.81 while the lateral cases keep
   Qf ≈ 1.0. That is S6-10's Qf rule doing what it says.
