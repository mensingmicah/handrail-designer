# Independent calc: test case 7

Round HSS post (HSS2.375X0.125, default grade) under a Pipe2STD rail.
Coverage per the slice 5 plan (T2): post, Check 3, Check 5, Check 6,
Check 7, reactions. Checks 1, 2 and 4 and the section group are not covered.

## Header

- **Case:** tests/cases/case-07.toml (inputs only; value tables stripped).
- **Date:** 2026-10-10.
- **Model:** Claude. The model id is not written into the repo (session
  policy); it is in the session report to Micah.
- **Branch and commit:** `slice-5`. Sources were read at `bdeb282`. A build
  session committed to the branch while this calc was being written (head
  `b3df5ff` when this file was saved); those commits were not read.
- **Independence:** this session read no src/, no tool output, no golden
  snapshot, no test file other than the two named below, no other case's
  independent files, no registry entry (verified or drafted, by Micah's
  instruction for this calc), and no git history or diff. No test was run.
  One file arrived unasked: the harness attached
  .claude/rules/engine-layout.md (module names and conventions, no values).
- **Sources read:**
  - Case inputs: tests/cases/case-07.toml through the skill's stripping
    command; the key names and header comments of
    tests/cases/independent/case-07.toml.
  - docs/BRIEF.md and every file in docs/brief/; CONTEXT.md;
    docs/plans/slice-5.md (decisions only; its "rough figures" for case 7
    were not used, and every number below is derived here).
  - AISC Shapes Database v16.0 workbook
    (data/aisc-shapes-database-v16.0.xlsx), rows Pipe2STD and
    HSS2.375X0.125. Cited below as **DB**.
  - AISC 360-22 (out/aisc-360-22.pdf), read this session. Cited below by
    section and printed page, as **360-22 p. 16.1-n**.
  - From memory, each listed in section 11: AISC Steel Construction Manual,
    16th Edition, Tables 2-4 and 2-5 (Fy, Fu) and the steel density;
    ASCE 7-22 §4.5.1 and §2.4.1; the E70XX classification strength.

**Conventions.** ASD throughout (360-22 §B3.2, Eq. B3-2, p. 16.1-16).
E = 29,000 ksi (360-22 p. 16.1-21). Full precision is carried; results are
shown to four significant figures. A value that is exact in six digits or
fewer (110.25, 1.1875, 0.088375) is written in full.

## 1. Inputs

| Item | Value | Source |
| --- | --- | --- |
| Span s (= L, tributary length for the post) | 6'-0" = 72 in | case file |
| Post height h (top of concrete to rail centerline) | 42 in | case file |
| Baseplate thickness t_p | 1/2 in | case file |
| Top rail | Pipe2STD, A53 Gr B | case file |
| Post | HSS2.375X0.125; grade not entered, so A500 Gr B | case file; S5-5 default (inputs.md) |
| Intermediate rail | none | case file |
| Baseplate | B = 6 in (parallel to rail) × N = 8 in, A36 | case file |
| Weld, rail to post | 1/8 in fillet, E70XX | case file |
| Weld, post to baseplate | 3/16 in fillet all around, E70XX | case file |
| Guard loads | not entered, so defaults: P = 200 lb, w = 50 lb/ft; no exemption | ASCE 7-22 §4.5.1, §4.5.1.1 (memory) |
| Post deflection limit | (h − t_p)/60, not bypassed | case file |

Derived lengths:

| Symbol | Equation | Result | Source |
| --- | --- | --- | --- |
| h − t_p | 42 − 0.5 | 41.5 in | critical section at top of baseplate, D4 (checks.md) |
| w·s | 50 lb/ft × 72 in / 12 | 300 lb | distributed load on the post, tributary length = span (loads-and-envelope.md) |

## 2. Limit states considered

Listed from AISC 360-22, member by member, not from the tool's list of
checks.

**Post, HSS2.375X0.125 (cantilever, fixed at top of baseplate).**

| Limit state | Provision | Applies? |
| --- | --- | --- |
| Wall local buckling, axial compression | Table B4.1a Case 9 | Classified in section 5.1: nonslender. A slender wall would stop the calc. |
| Wall local buckling, flexure | Table B4.1b Case 20; §F8.2 | Classified in section 5.1: compact, so §F8.2 does not apply. |
| §F8 applicability, D/t < 0.45E/Fy | §F8 | Checked in section 5.1. |
| Flexural yielding (plastic moment) | §F8.1, Eq. F8-1 | Yes. Governs Mn. |
| Lateral-torsional buckling | Chapter F | No. Round HSS has no LTB limit state; §F8 lists yielding and local buckling only. |
| Flexural buckling | §E3 | Yes, Lc = K·h, K = 2.1 (D3). |
| Torsional, flexural-torsional buckling | §E4 | No. Round HSS: flexural buckling only (Table User Note E1.1, p. 16.1-39). |
| Tensile yielding | §D2(a), Eq. D2-1 | Yes, upward case. |
| Tensile rupture | §D2(b), Eq. D2-2 | Not a v1 check (checks.md, S5-13). Confirmed in section 5.1 that yielding governs. |
| Combined compression and flexure | §H1.1 | Yes, the three horizontal cases. |
| Combined tension and flexure | §H1.2 | No case has both: the upward case has no moment. |
| Second-order effects | Appendix 8 | Gate only: αPr/Pe ≤ 0.05, or stop (D1). |
| Shear | §G5 | Not checked: stated assumption (output.md). For information, section 12 item 5. |
| Torsion | §H3 | None. Loads act through the member centerlines (welds.md, W1). |
| Lateral deflection | serviceability | Yes, Check 6, engineering-judgement limit. |
| Lc/r > 200 | §E2 User Note | Flag only (D6). Lc/r = 110.25: no flag. |

**Rail to post weld (Check 3): post end coped to the rail underside, 1/8 in fillet.**

| Limit state | Provision | Applies? |
| --- | --- | --- |
| Weld metal rupture | §J2.4, Eq. J2-4, Table J2.5 | Yes, k_ds = 1.0 (W2, branch to chord). |
| Base metal, rail wall, in-plane shear rupture | §J4.2(b), Eq. J4-4 | Yes, horizontal cases, demand V/(πD) (W5, W6). |
| Base metal, rail wall, shear yielding | §J4.2(a) | Not checked (W6): a limit state of a gross shear area, not of a fusion face. |
| Rail wall, force normal to the wall (chord plastification and the other chord limit states) | Chapter K, Tables K3.1 and K4.1 | Not checked in slice 5: stated assumption (W7, kept by S5-3). The guard is chord D/t ≤ 50 (Tables K3.1A and K4.1A, pp. 16.1-164 and 16.1-168): rail D/t = 16.6 (DB), passes. |
| Base metal, post wall | §J4.1 | Covered by Check 5 (W5); needs Fu/Fy ≥ 1.20, section 5.1. |
| Minimum fillet size | Table J2.4 | Yes, pass/fail line (W11). |
| Maximum fillet size | §J2.2b(b) | Does not apply: T-joint, not along an edge (W11). |

One observation under Chapter K, not a new check: Tables K3.1A and K4.1A
limit the width ratio to D_b/D ≤ 1.0. With published ODs the branch (post,
2.38 in) is 0.005 in wider than the chord (rail, 2.375 in). That is the
database's rounding of the same physical 2.375 in diameter, which S5-4
already rules on (ODs within 0.01 in are equal), so W8 does not stop this
case.

**Post to baseplate weld (Check 7): 3/16 in fillet all around.**

| Limit state | Provision | Applies? |
| --- | --- | --- |
| Weld metal rupture | §J2.4, Eq. J2-4 and J2-5, Table J2.5 | Yes, with k_ds per W2 and S5-12. |
| Base metal, baseplate, shear rupture through t_p | §J4.2(b), Eq. J4-4 | Yes, against the resultant per inch (W5). |
| Base metal, post wall, tension along the post axis | §J4.1 | Covered by Check 5 (W5). Quantified in section 12 item 2, for Micah. |
| Minimum fillet size | Table J2.4 | Yes. |
| Maximum fillet size | §J2.2b(b) | Does not apply (W11). |
| Baseplate bending, anchors | — | Out of scope (scope.md); stated assumption. |

Nothing that could govern is missing from the plan's scope, with one item
raised for Micah: the post wall at the base weld (section 12 item 2).

## 3. Loads and load path

**Dead load.**

| Symbol | Equation | Result | Source |
| --- | --- | --- | --- |
| W_rail | tabulated | 3.66 lb/ft | DB, Pipe2STD |
| W_post | tabulated | 3.01 lb/ft | DB, HSS2.375X0.125 |
| D_rail | W_rail·s = 3.66 × 72/12 | 21.96 lb | loads-and-envelope.md (D2, D11) |
| D_post | W_post·(h − t_p) = 3.01 × 41.5/12 | 10.41 lb | same |
| D_int | no intermediate rail | 0 | S4-1 |
| D (at the post's critical section) | D_rail + D_post = 21.96 + 10.41 | 32.37 lb | same |
| W_bp | ρ·B·N·t_p = (490/1728) × 6 × 8 × 0.5 | 6.806 lb | S4-6; ρ = 490 lb/ft³ (memory) |
| D (reaction sets) | D_rail + D_post + W_bp = 32.37 + 6.806 | 39.18 lb | S4-6 |

The rail's dead load reaches the post through the rail to post weld
(Check 3 carries D_rail only), then travels down the post with the post's
own weight to the top of the baseplate (Checks 5 and 7 carry D), and the
baseplate's weight joins below that section (reaction sets only).

**Guard loads.** Two load types, never concurrent, each run through every
direction (loads-and-envelope.md):

| Load type | On the post | Magnitude |
| --- | --- | --- |
| Concentrated | P at the top of the post (rail centerline) | 200 lb |
| Distributed | w·s at the top of the post | 300 lb |

The load acts at the rail centerline, height h above concrete. It enters
the post through the Check 3 weld ring at the rail underside (eccentricity
e = D_rail/2 from the rail centerline, W1) and is carried by cantilever
bending to the top of the baseplate, lever arm h − t_p = 41.5 in (Checks 5,
6 and 7), and to the top of concrete, lever arm h = 42 in (reactions).

**Direction cases and combinations** (loads-and-envelope.md; welds.md W10):

| Case | At the post base (Checks 5, 7) | At the rail weld (Check 3) | Combination |
| --- | --- | --- | --- |
| Downward | Pr = D + L, compression; M = 0 | (D_rail + L), uniform | ASCE 7-22 ASD D + L |
| Outward, inward | Pr = D; M = L·(h − t_p) | V = L; M = L·e; D_rail axial | ASCE 7-22 ASD D + L |
| Longitudinal | as transverse | as transverse | ASCE 7-22 ASD D + L |
| Upward | Pr = L − 0.6D, tension; M = 0 | L − 0.6·D_rail, tension | 0.6D + 1.0L, engineering judgement |

Five directions × two load types = ten envelope cases per check. The post
is round, so outward, inward and longitudinal give identical numbers; all
are listed. Upward net tension exists in every upward case (0.6D = 19.42
lb at most, against L ≥ 200 lb).

**Reactions** (LRFD, 0.9D + 1.6L, engineering judgement; S4-4 to S4-6):
the larger load type, w·s = 300 lb > P = 200 lb, so "distributed".

## 4. Section properties

Used exactly as published (checks.md; S5-4: the OD column as it stands).

| Property | Post, HSS2.375X0.125 | Rail, Pipe2STD | Source |
| --- | --- | --- | --- |
| OD, D | 2.38 in | 2.375 in | DB |
| t_nom | 0.125 in | 0.154 in | DB |
| t_des | 0.116 in | 0.143 in | DB |
| D/t | 20.5 | 16.6 | DB |
| W | 3.01 lb/ft | 3.66 lb/ft | DB |
| A | 0.823 in² | — | DB |
| I | 0.527 in⁴ | — | DB |
| S | 0.443 in³ | — | DB |
| Z | 0.592 in³ | — | DB |
| r | 0.800 in | — | DB |

Rail properties not listed are not used by the covered checks.

Materials (all from memory; section 11):

| Member | Grade | Fy | Fu |
| --- | --- | --- | --- |
| Post | A500 Gr B, round | 46 ksi | 58 ksi |
| Rail | A53 Gr B | 35 ksi | 60 ksi |
| Baseplate | A36 | 36 ksi (not used) | 58 ksi |
| Weld | E70XX | — | F_EXX = 70 ksi |

**I am not sure of the post's Fy.** See section 12 item 1.

## 5. Check 5: post, combined axial and flexure

### 5.1 Capacities (case-independent)

Classification:

| Symbol | Equation | Result | Citation |
| --- | --- | --- | --- |
| D/t | tabulated | 20.5 | DB; t is the design wall, §B4.1(g), p. 16.1-22 |
| λr, compression | 0.11E/Fy = 0.11 × 29,000/46 | 69.35 | Table B4.1a Case 9, p. 16.1-21 |
| | 20.5 ≤ 69.35 | nonslender | |
| λp, flexure | 0.07E/Fy = 0.07 × 29,000/46 | 44.13 | Table B4.1b Case 20, p. 16.1-23 |
| λr, flexure | 0.31E/Fy = 0.31 × 29,000/46 | 195.4 | same |
| | 20.5 ≤ 44.13 | compact | |
| §F8 limit | 0.45E/Fy = 0.45 × 29,000/46 | 283.7 | §F8, p. 16.1-65 |
| | 20.5 < 283.7 | §F8 applies | |
| Fu/Fy | 58/46 | 1.261 ≥ 1.20 | W5 and S5-13 guard: passes |

Flexure:

| Symbol | Equation | Result | Citation |
| --- | --- | --- | --- |
| Mn | Fy·Z = 46 × 0.592 | 27.23 kip-in = 27,232 lb-in | Eq. F8-1, p. 16.1-65 |
| Mc | Mn/Ωb = 27.232/1.67 | 16.31 kip-in = 16,310 lb-in | §F1(a), Ωb = 1.67, p. 16.1-52 |

Lb and Cb do not enter (round section, no LTB; checks.md D5).

Compression:

| Symbol | Equation | Result | Citation |
| --- | --- | --- | --- |
| K | fixed-free, recommended design value | 2.1 | Commentary Table C-A-7.1 case (e), p. 16.1-650; D3 |
| Lc | K·h = 2.1 × 42 | 88.2 in | §E2, p. 16.1-40; length h, not h − t_p (D3) |
| Lc/r | 88.2/0.800 | 110.25 | below 200: no flag (§E2 User Note) |
| 4.71√(E/Fy) | 4.71 × √(29,000/46) | 118.3 | §E3, p. 16.1-40 |
| | 110.25 ≤ 118.3 | Eq. E3-2 | |
| Fe | π²E/(Lc/r)² = π² × 29,000/110.25² | 23.55 ksi | Eq. E3-4, p. 16.1-41 |
| Fy/Fe | 46/23.55 | 1.954 (≤ 2.25, same branch) | §E3(a) |
| Fn (the brief's Fcr) | 0.658^(Fy/Fe)·Fy = 0.658^1.954 × 46 | 20.31 ksi | Eq. E3-2, p. 16.1-40 |
| Pn | Fn·Ag = 20.31 × 0.823 | 16.71 kips = 16,710 lb | Eq. E3-1 |
| Pc | Pn/Ωc = 16.71/1.67 | 10.01 kips = 10,010 lb | §E1, Ωc = 1.67, p. 16.1-38 |

360-22 names the E3 stress Fn; the brief and the values file call it Fcr.

Tension:

| Symbol | Equation | Result | Citation |
| --- | --- | --- | --- |
| Pn | Fy·Ag = 46 × 0.823 | 37.86 kips | Eq. D2-1, p. 16.1-32 |
| Pt | Pn/Ωt = 37.858/1.67 | 22.67 kips = 22,670 lb | Ωt = 1.67, p. 16.1-32 |
| Rupture, for the record | Fu·Ae/Ωt = 58 × 0.823/2.00, U = 1.0 | 23.87 kips > 22.67 | Eq. D2-2, p. 16.1-33; Table D3.1 Case 1, p. 16.1-34. Yielding governs. |

Second-order gate:

| Symbol | Equation | Result | Citation |
| --- | --- | --- | --- |
| Pe | π²EI/Lc² = π² × 29,000 × 0.527/88.2² | 19.39 kips | App. 8, Eq. A-8-5 form, p. 16.1-284, with Lc = K·h and EI (D1, engineering judgement) |
| αPr/Pe | 1.6 × 32.37/19,390 | 0.002671 | α = 1.6 (ASD), p. 16.1-284 |
| | 0.002671 ≤ 0.05 | negligible; amplification 1.0 | D1 |

Pr = D in all three moment cases and both load types, so αPr/Pe is the
same in all six.

### 5.2 Envelope

Downward (axial only, Chapter E ratio; D8):

| Load type | Pr = D + L | Pr/Pc |
| --- | --- | --- |
| Concentrated | 32.37 + 200 = 232.4 lb | 232.4/10,008 = 0.02322 |
| Distributed | 32.37 + 300 = 332.4 lb | 332.4/10,008 = 0.03321 |

Outward, inward, longitudinal (identical; §H1.1, p. 16.1-82):

| Line | Concentrated | Distributed |
| --- | --- | --- |
| Pr = D | 32.37 lb | 32.37 lb |
| Mr = L·(h − t_p) | 200 × 41.5 = 8,300 lb-in | 300 × 41.5 = 12,450 lb-in |
| Pr/Pc | 32.37/10,008 = 0.003234 | 0.003234 |
| Threshold | < 0.2: Eq. H1-1b | < 0.2: Eq. H1-1b |
| Pr/(2Pc) | 0.001617 | 0.001617 |
| Mr/Mc | 8,300/16,307 = 0.5090 | 12,450/16,307 = 0.7635 |
| Ratio, Eq. H1-1b | 0.001617 + 0.5090 = 0.5106 | 0.001617 + 0.7635 = **0.7651** |

Biaxial bending does not arise: dead load is axial at the post, and the
moment is about one axis in each case.

Upward (axial only, Chapter D ratio; D8), 0.6D + 1.0L:

| Load type | Pr = L − 0.6D | Pr/Pt |
| --- | --- | --- |
| Concentrated | 200 − 0.6 × 32.37 = 180.6 lb, tension | 180.6/22,669 = 0.007966 |
| Distributed | 300 − 0.6 × 32.37 = 280.6 lb, tension | 280.6/22,669 = 0.01238 |

**Controlling:** outward (= inward = longitudinal), distributed, Eq.
H1-1b, ratio 0.7651 ≤ 1.0, OK.

## 6. Check 6: post deflection

Live load only, cantilever length h − t_p (checks.md, Check 6).

| Symbol | Equation | Result | Source |
| --- | --- | --- | --- |
| Δ_allow | (h − t_p)/60 = 41.5/60 | 0.6917 in | case file limit; engineering judgement |
| Δ, concentrated | P·(h − t_p)³/(3EI) = 200 × 41.5³/(3 × 29,000,000 × 0.527) | 0.3118 in | cantilever, end load |
| Ratio | 0.3118/0.6917 | 0.4508 | |
| Δ, distributed | 300 × 41.5³/(3 × 29,000,000 × 0.527) | 0.4677 in | |
| Ratio | 0.4677/0.6917 | **0.6761** | |

The same in outward, inward and longitudinal. Downward and upward are
vertical: no lateral deflection.

**Controlling:** outward (= inward = longitudinal), distributed, 0.4677 in
against 0.6917 in, ratio 0.6761, OK.

## 7. Check 3: rail to post weld

### 7.1 Case-independent

| Symbol | Equation | Result | Citation |
| --- | --- | --- | --- |
| D | post OD, as published | 2.38 in | DB; ring = post perimeter (W1); S5-4 |
| L_w | πD = π × 2.38 | 7.477 in | W3 |
| S_w | πD²/4 = π × 2.38²/4 | 4.449 in² | W3 |
| e | D_rail/2 = 2.375/2 | 1.1875 in | W1 |
| w | fillet size | 0.125 in | case file |
| t_e | 0.707w = 0.707 × 0.125 | 0.088375 in | §J2.2a, p. 16.1-126; the 0.707 form per welds.md |
| Fnw | 0.60·F_EXX = 0.60 × 70 | 42 ksi | Table J2.5, p. 16.1-132 |
| k_ds | branch to chord | 1.0 | W2; §J2.4(3), p. 16.1-130 |
| Weld allowable | Fnw·t_e·k_ds/Ω = 42 × 0.088375 × 1.0/2.00 | 1.856 kip/in = 1,856 lb/in | Eq. J2-4, p. 16.1-130; Ω = 2.00, Table J2.5 |
| Base metal allowable, rail wall | 0.60·Fu·t_des/Ω = 0.60 × 60 × 0.143/2.00 | 2.574 kip/in = 2,574 lb/in | Eq. J4-4, p. 16.1-146; W5, W6; t_des per W4 |
| Thinner part joined | min(post t_nom 0.125, rail t_nom 0.154) | 0.125 in | W11: nominal walls |
| Minimum fillet | to 1/4 in inclusive | 1/8 in | Table J2.4, p. 16.1-128 |
| | 0.125 ≥ 0.125 | OK | |

D in Check 3 is the rail's dead load only: D_rail = 21.96 lb (W10).

### 7.2 Envelope

Forces per inch of weld. f_a is the axial component, f_b the bending
component at the extreme fiber, f_v the uniform shear, f_n the normal
component at the governing fiber, f_r the resultant.

Downward, uniform: f = (D_rail + L)/L_w.

| Load type | f_a = f_n = f_r | Weld ratio |
| --- | --- | --- |
| Concentrated | (21.96 + 200)/7.477 = 29.69 lb/in | 29.69/1,856 = 0.01600 |
| Distributed | (21.96 + 300)/7.477 = 43.06 lb/in | 43.06/1,856 = 0.02320 |

Outward, inward, longitudinal (identical):

| Line | Concentrated | Distributed |
| --- | --- | --- |
| V = L | 200 lb | 300 lb |
| M = V·e | 200 × 1.1875 = 237.5 lb-in | 300 × 1.1875 = 356.25 lb-in |
| f_v = V/L_w | 200/7.477 = 26.75 lb/in | 300/7.477 = 40.12 lb/in |
| f_b = M/S_w | 237.5/4.449 = 53.39 lb/in | 356.25/4.449 = 80.08 lb/in |
| f_a = D_rail/L_w | 21.96/7.477 = 2.937 lb/in | 2.937 lb/in |
| f_n, compression side = f_b + f_a | 56.32 lb/in | 83.01 lb/in |
| f_r, compression side = √(f_n² + f_v²) | √(56.32² + 26.75²) = 62.35 lb/in | √(83.01² + 40.12²) = 92.20 lb/in |
| f_r, tension side = √((f_b − f_a)² + f_v²) | 57.10 lb/in | 86.95 lb/in |
| Governing fiber | compression side | compression side |
| Weld ratio = f_r/1,856 | 0.03360 | **0.04968** |
| Base metal ratio = f_v/2,574 | 0.01039 | 0.01559 |

No bearing credit is taken (W10), so dead-load compression adds to bending
on the compression side. The base metal line takes the in-plane demand f_v
only (W6); the normal components go to the chord wall (W7).

Upward, uniform tension: f = (L − 0.6·D_rail)/L_w.

| Load type | T | f_a = f_n = f_r | Weld ratio |
| --- | --- | --- | --- |
| Concentrated | 200 − 0.6 × 21.96 = 186.8 lb | 186.8/7.477 = 24.99 lb/in | 0.01346 |
| Distributed | 300 − 0.6 × 21.96 = 286.8 lb | 286.8/7.477 = 38.36 lb/in | 0.02067 |

**Controlling:** outward (= inward = longitudinal), distributed, weld
metal, compression side, ratio 0.04968, OK. Rail wall base metal 0.01559.

## 8. Check 7: post to baseplate weld

### 8.1 Case-independent

| Symbol | Equation | Result | Citation |
| --- | --- | --- | --- |
| L_w | πD = π × 2.38 | 7.477 in | W3; DB OD (S5-4) |
| S_w | πD²/4 | 4.449 in² | W3 |
| Arm | h − t_p | 41.5 in | welds.md |
| w | fillet size | 0.1875 in | case file |
| t_e | 0.707w = 0.707 × 0.1875 | 0.1326 in | §J2.2a; welds.md |
| Fnw | 0.60 × 70 | 42 ksi | Table J2.5, p. 16.1-132 |
| θ | at either extreme fiber, and all around in the uniform cases | 90° | see below |
| k_ds | 1.0 + 0.50 sin^1.5 θ = 1.0 + 0.50 × 1 | 1.5 | Eq. J2-5, p. 16.1-130; applied to a round post by W2 and S5-12 (engineering judgement) |
| Weld allowable | Fnw·t_e·k_ds/Ω = 42 × 0.1325625 × 1.5/2.00 | 4.176 kip/in = 4,176 lb/in | Eq. J2-4; Ω = 2.00 |
| Base metal allowable, baseplate | 0.60·Fu·t_p/Ω = 0.60 × 58 × 0.5/2.00 | 8.700 kip/in = 8,700 lb/in | Eq. J4-4, p. 16.1-146; W5 |
| Thinner part joined | min(post t_nom 0.125, t_p 0.5) | 0.125 in | W11 |
| Minimum fillet | to 1/4 in inclusive | 1/8 in | Table J2.4, p. 16.1-128 |
| | 0.1875 ≥ 0.125 | OK | |

θ at the extreme fiber: the weld axis there is tangent to the ring,
perpendicular to the direction of V. The bending and axial components act
along the post axis and the uniform shear V/(πD) acts in the direction of
V; both are perpendicular to the weld axis, so the resultant is too:
θ = 90°. In the downward and upward cases the force is along the post
axis all around the ring: θ = 90°.

D in Check 7 is D at the post, 32.37 lb.

### 8.2 Envelope

Downward, uniform: f = (D + L)/L_w.

| Load type | f_a = f_n = f_r | Weld ratio (/4,176) | Base ratio (/8,700) |
| --- | --- | --- | --- |
| Concentrated | 232.4/7.477 = 31.08 lb/in | 0.007443 | 0.003572 |
| Distributed | 332.4/7.477 = 44.45 lb/in | 0.01065 | 0.005109 |

Outward, inward, longitudinal (identical):

| Line | Concentrated | Distributed |
| --- | --- | --- |
| V = L | 200 lb | 300 lb |
| M = V·(h − t_p) | 8,300 lb-in | 12,450 lb-in |
| f_v = V/L_w | 26.75 lb/in | 40.12 lb/in |
| f_b = M/S_w | 8,300/4.449 = 1,866 lb/in | 12,450/4.449 = 2,799 lb/in |
| f_a = D/L_w | 32.37/7.477 = 4.329 lb/in | 4.329 lb/in |
| f_n, compression side = f_b + f_a | 1,870 lb/in | 2,803 lb/in |
| f_r, compression side = √(f_n² + f_v²) | 1,870 lb/in | 2,803 lb/in |
| f_r, tension side | 1,862 lb/in | 2,794 lb/in |
| Governing fiber | compression side | compression side |
| θ, k_ds | 90°, 1.5 | 90°, 1.5 |
| Weld ratio = f_r/4,176 | 0.4479 | **0.6713** |
| Base ratio = f_r/8,700 | 0.2150 | 0.3222 |

(Unrounded: f_n = 1,869.997 and 2,802.831 lb/in; f_r = 1,870.188 and
2,803.118 lb/in. The shear moves the resultant by 0.01%.)

The points on the neutral axis were also tried, because k_ds is lower
there (the shear is parallel to the weld axis): distributed load,
f = √(4.329² + 40.12²) = 40.36 lb/in at θ = 6.16°, ratio 0.014. The
extreme fiber governs.

Upward, uniform tension: f = (L − 0.6D)/L_w.

| Load type | T | f_a = f_n = f_r | Weld ratio | Base ratio |
| --- | --- | --- | --- | --- |
| Concentrated | 180.6 lb | 180.6/7.477 = 24.15 lb/in | 0.005784 | 0.002776 |
| Distributed | 280.6 lb | 280.6/7.477 = 37.53 lb/in | 0.008987 | 0.004313 |

**Controlling:** outward (= inward = longitudinal), distributed, weld
metal, compression side, ratio 0.6713, OK. Baseplate base metal 0.3222.
Post wall: covered by Check 5 (W5); see section 12 item 2.

## 9. Anchor reaction sets

LRFD, 0.9D + 1.6L (engineering judgement), at the top of concrete, moment
arm h = 42 in. Governing load type: distributed (w·s = 300 lb > P = 200
lb). N positive = tension.

| Symbol | Equation | Result |
| --- | --- | --- |
| D | 21.96 (top rail) + 0 (intermediate rail) + 10.41 (post) + 6.806 (baseplate) | 39.18 lb |
| 0.9D | 0.9 × 39.18 | 35.26 lb |
| **Lateral set** | | |
| V | 1.6 × 300 | 480 lb |
| M | V·h = 480 × 42 | 20,160 lb-in |
| N | −0.9D | −35.26 lb (compression) |
| **Upward set** | 1.6L = 480 lb > 0.9D = 35.26 lb: net tension, so the set is reported | |
| V | — | 0 |
| M | — | 0 |
| N | 1.6 × 300 − 0.9 × 39.18 | +444.7 lb (tension) |

## 10. Summary

| Check | Controlling case | Demand | Capacity | Ratio |
| --- | --- | --- | --- | --- |
| 3, rail to post weld | outward, distributed; compression side | 92.20 lb/in | 1,856 lb/in | 0.04968 |
| 5, post | outward, distributed; Eq. H1-1b | Mr = 12,450 lb-in, Pr = 32.37 lb | Mc = 16,310 lb-in, Pc = 10,010 lb | 0.7651 |
| 6, post deflection | outward, distributed | 0.4677 in | 0.6917 in | 0.6761 |
| 7, post to baseplate weld | outward, distributed; compression side | 2,803 lb/in | 4,176 lb/in | 0.6713 |

Outward, inward and longitudinal tie exactly in every check; "outward" is
named because it comes first in the values file's key order.

## 11. Values from my own reading

No registry entry was read for this calc, so every code value is my own
reading. Those read from the AISC 360-22 text this session carry their
page above. Those from memory:

| Value | Used | Document | Confidence |
| --- | --- | --- | --- |
| A500 Gr B, round: Fy = 46 ksi, Fu = 58 ksi | post | AISC Manual, 16th Edition, Table 2-4 | **Not sure of Fy.** Section 12 item 1. |
| A53 Gr B: Fy = 35 ksi, Fu = 60 ksi | rail wall, Check 3 | AISC Manual, 16th Edition, Table 2-4 | Confident. |
| A36: Fu = 58 ksi | baseplate, Check 7 | AISC Manual, 16th Edition, Table 2-5 | Confident. |
| F_EXX = 70 ksi | both welds | AWS A5.1 E70XX classification; AISC Manual Part 8 | Confident. |
| Steel density 490 lb/ft³ | baseplate weight | AISC Manual, 16th Edition (weights of materials, Part 17) | Confident of the value, not of the table number. |
| P = 200 lb; w = 50 lb/ft | guard loads | ASCE 7-22 §4.5.1 and §4.5.1.1 | Confident. |
| D + L | ASD combination | ASCE 7-22 §2.4.1 | Confident. |
| Δ = PL³/(3EI) | Check 6 | elastic beam theory (AISC Manual Table 3-23, cantilever with end load) | Confident. |

Read from the 360-22 text, with one remark each where the text and the
brief differ in wording:

- t_e = 0.707w: §J2.2a defines the throat as the shortest distance from
  the root to the face of the diagrammatic weld; 0.707 is the brief's
  stated form of that for an equal-leg fillet.
- Table J2.5 gives Fnw = 0.60·F_EXX and Ω = 2.00 for fillet welds; §J4.2(b)
  gives 0.60·Fu·Anv and Ω = 2.00.
- K = 2.1 is in the Commentary (Table C-A-7.1), not the Specification.

## 12. Open questions for Micah

1. **A500 Gr B round, Fy.** I used Fy = 46 ksi and Fu = 58 ksi as the 16th
   Edition Manual's Table 2-4 values, from memory. My recollection is that
   the 16th Edition follows ASTM A500-21, which gives round and shaped HSS
   the same strengths (Gr B 46/58, Gr C 50/62). The 15th Edition and
   earlier list 42/58 for round Gr B. I could not check the table, and the
   plan says you verify this value yourself. If the verified value is 42
   ksi, this calc's post values are wrong and must be redone in a fresh
   session, not edited. For sizing the difference only: at 42 ksi the wall
   is still compact and nonslender, the branch is still Eq. E3-2, and the
   controlling Check 5 ratio would be about 0.84 in place of 0.7651.
   Checks 3, 6 and 7 and the reactions do not use the post's Fy.
2. **Post wall at the base weld is the weakest element of that joint, and
   Check 5 is what covers it.** By the same elastic line model as Check 7,
   the post wall at the extreme fiber carries 2,803 lb/in. The wall's
   allowable in tension yielding is Fy·t_des/1.67 = 46 × 0.116/1.67 =
   3,195 lb/in (ratio 0.877), and in rupture Fu·t_des/2.00 = 3,364 lb/in
   (0.833). Both are below the weld's 4,176 lb/in, so the weld metal ratio
   of 0.6713 is not the joint's critical number. W5 rules that the wall is
   covered by Check 5, which gives 0.7651 because the member check uses
   the plastic modulus (Z/S = 1.336). On first yield the wall is at
   M/S = 12,450/0.443 = 28.10 ksi against Fy/1.67 = 27.54 ksi, 1.02. I
   have followed W5 and recorded no value for this. I raise it because
   this wall (0.116 in) is thinner than any pipe wall the ruling was made
   on.
3. **Check 7 passes only with the directional increase.** With k_ds = 1.0
   the weld allowable is 2,784 lb/in and the ratio 1.007, NG. W2 and S5-12
   apply k_ds = 1.5 here as engineering judgement. For the record, the
   360-22 text (§J2.4, p. 16.1-130) gives Eq. J2-5 "where strain
   compatibility of the various weld elements is considered" and k_ds =
   1.0 "for all other conditions"; its User Note describes a linear weld
   group loaded through its center of gravity. No change made; this is
   already a decision of yours and a drafted entry for the release review.
4. **Keys read by interpretation.** The values file does not define a few
   keys; section 13 says how I read each. If the tool means something
   else by one of them, that mismatch is a naming difference, not a calc
   difference.
5. **Member shear, for information.** Not checked (stated assumption).
   §G5 (pp. 16.1-80 and 16.1-81): Vn = Fcr·Ag/2 with Fcr = 0.6Fy =
   27.6 ksi gives Vn = 11.36 kips, Vn/1.67 = 6.80 kips, against V = 0.300
   kips: 0.044.

## 13. Values file mapping

Every key in tests/cases/independent/case-07.toml is filled. How I read
the keys the file does not define:

| Key | Read as |
| --- | --- |
| `post.D_post_lb` | the post's own dead load, W_post·(h − t_p) |
| `post.P_D_lb` | D at the post's critical section, D_rail + D_post |
| `check5.Fcr_ksi` | the Chapter E stress, Fn in 360-22's notation |
| `check3.t_min_in`, `check7.t_min_in` | thickness of the thinner part joined, for Table J2.4 (nominal walls, W11) |
| `check3.w_min_in`, `check7.w_min_in` | the Table J2.4 minimum fillet size |
| `check3.base_allow_lbpin` | rail wall, shear rupture, per inch |
| `check7.base_allow_lbpin` | baseplate, shear rupture through t_p, per inch |
| `f_a_lbpin` | the axial component per inch: (D + L)/L_w downward, D/L_w in the moment cases, (L − 0.6D)/L_w upward |
| `f_n_lbpin` | the normal component at the governing fiber: f_b + f_a in the moment cases, f_a in the uniform cases |
| `f_r_lbpin` | the resultant at the governing fiber |
| `check3.ratio_base` | f_v over the rail wall allowable (moment cases only, as the file's keys have it) |
| `check7.ratio_base` | f_r over the baseplate allowable, all ten cases |
| `ratio` (Checks 3 and 7) | the larger of the weld and base metal ratios; the weld governs in every case here |
| `check7.weld_allow_lbpin` | the allowable with k_ds included |
| `reactions.D_lb` | the reaction sets' D, baseplate included |

Computed here with no key in the file (a finding only if the tool prints
them differently): Fy and Fu of each part; the classification limits (λr
in compression, λp and λr in flexure, the §F8 limit) and Fu/Fy; D_rail;
Pe; the tension Pn; Pr/Pc and the H1-1b terms; the tension-side resultants
in Checks 3 and 7; the moments M = V·e and M = V·(h − t_p) at the weld
rings; Check 3's k_ds (1.0) and unfactored weld strengths; the
neutral-axis point in Check 7; 0.9D in the reaction sets.

Keys I could not fill: none.

## 14. Review checklist (docs/brief/verification.md)

1. **Loads complete.** Rail dead load over the span and post dead load
   over h − t_p are carried to the post base; the baseplate weight enters
   the reactions only; there is no intermediate rail. Both guard load
   types are run. The component load does not apply (no intermediate
   rail).
2. **Direction and worst case.** All five directions and both load types
   are worked for every check, ten cases each (six for Check 6, which has
   no vertical cases). The worst case is found by calculation: outward,
   distributed, in all four checks.
3. **Checks complete.** Section 2 lists every limit state from the code.
   Those not checked are each tied to a decision in the brief. One is
   raised for Micah: the post wall at the base weld (section 12 item 2).
4. **Geometry.** h = 42 in for Lc and the reaction arm; h − t_p = 41.5 in
   for the post moment, the deflection length and its limit, the Check 7
   arm and the post weight; e = D_rail/2 = 1.1875 in for Check 3; the
   post's published OD of 2.38 in for both weld rings; span 72 in as
   tributary length.
5. **Method and equations.** Classification before capacity (nonslender,
   compact). Eq. E3-2 by Lc/r = 110.25 ≤ 118.3. Pr/Pc = 0.0032 < 0.2, so
   Eq. H1-1b; axial-only cases on their own chapters. αPr/Pe = 0.0027 ≤
   0.05. k_ds = 1.0 at Check 3 and 1.5 at Check 7, per W2.
6. **Assumptions.** Post fixed at the top of the baseplate; K = 2.1 on h;
   tributary length = span; flat-ring weld model at the rail underside;
   no bearing credit; chord wall not checked (rail D/t = 16.6 ≤ 50).
7. **Code editions.** AISC 360-22 throughout, pages from the 2022 text;
   AISC Manual 16th Edition; ASCE 7-22; Shapes Database v16.0.
8. **Magnitude sense.** A 2-3/8 in thin-wall HSS post at 42 in under 300
   lb is near 3/4 of its bending capacity and deflects under 1/2 in; the
   base weld force of 2.8 kip/in is M/S_w with a negligible shear; the
   rail weld is lightly loaded because its lever arm is only 1.19 in.
   Units: lb, in, lb-in, lb/in, ksi.
9. **Governing case.** The distributed load (300 lb at the post) governs
   over the concentrated load (200 lb) in every check, as expected for a
   6 ft span, in a horizontal direction.
