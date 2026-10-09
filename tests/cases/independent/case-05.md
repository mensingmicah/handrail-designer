# Independent calc: test case 5

| | |
| --- | --- |
| Case | `tests/cases/case-05.toml`, "Test case 5": full guard, Pipe2STD rail and post, Pipe1-1/4STD intermediate rail, both reaction sets |
| Date | 2026-10-09 |
| Model | claude-opus-5-5 |
| Branch, commit | `slice-4` at `5fa154a51b93157fc01406702cff5a0926c46394` |
| Method | independent-calc skill (`.claude/skills/independent-calc/SKILL.md`) |

**Sources read, and nothing else:** the case inputs with `[hand]` and
`[independent]` stripped (the skill's command); docs/BRIEF.md and every
file in docs/brief/ (scope, inputs, loads-and-envelope, checks, welds,
output, verification); CONTEXT.md; docs/plans/slice-4.md (the newest plan
not marked completed); the registry entries with status "verified" (the
skill's command); the rows for Pipe2STD and Pipe1-1/4STD from
`data/aisc-shapes-database-v16.0.xlsx` (the skill's command); the key names
and header comments of `tests/cases/independent/case-05.toml` (the
template, all "pending", read only at step 7). Everything else comes from my
own reading of AISC 360-22, the AISC Manual (16th Ed.) and ASCE 7-22,
recorded line by line.

Two disclosures. The slice 4 plan carries planning arithmetic for this case
("Rough figures for case 5"). I read it as part of the plan, and I did not
use it: every number below comes from the inputs. The session context
also showed the last five commit subjects of the branch (for example
"Check 4b observation prints the wall comparison"). They contain no
values. No src/, tests/ value, tool output, drafted entry or diff was
read.

Arithmetic: Python standard library, full precision, reported to 4
significant figures. Units are lb, in, lb-in and ksi, and weld forces are
in lb per inch of weld (lb/in).

---

## 1. Inputs

| Item | Value | Note |
| --- | --- | --- |
| Span s = L | 6'-0" = 72.00 in | tributary length for the post |
| Post height h | 42.00 in | top of concrete to top rail centerline |
| Baseplate t_p | 1/2 in = 0.5000 in | |
| Cantilever h − t_p | 41.50 in | top of baseplate to top rail CL |
| Baseplate B × N | 6 in (parallel to rail) × 8 in (perpendicular), A36 | |
| Top rail | Pipe2STD, A53 Gr B | |
| Post | Pipe2STD, A53 Gr B | |
| Intermediate rail | Pipe1-1/4STD, own section (`same_as_top_rail = false`), grade defaults to A53 Gr B | |
| Welds | rail to post 1/8 in; post to baseplate 1/4 in; intermediate rail to post 1/8 in; E70XX | |
| Deflection limits | rail L/120; post (h − t_p)/60; intermediate rail L/120; none bypassed | |
| Guard loads | no `[loads]` table, so defaults: P = 200 lb, w = 50 plf, P_c = 50 lb; no exemption | |

Loads and material values:

| Symbol | Value | Citation | Source |
| --- | --- | --- | --- |
| P | 200 lb | ASCE 7-22 §4.5.1 | verified `asce7.guard.concentrated` |
| w | 50 plf = 4.167 lb/in | ASCE 7-22 §4.5.1.1 | verified `asce7.guard.uniform` |
| P_c | 50 lb | ASCE 7-22 §4.5.1.2 | own reading (memory) |
| E | 29,000 ksi | AISC 360-22, Symbols | verified `material.steel.E` |
| F_y (A53 Gr B) | 35 ksi | AISC Manual 16th Ed. Table 2-4 | verified `material.A53_GrB.Fy` |
| F_u (A53 Gr B) | 60 ksi | AISC Manual 16th Ed. Table 2-4 | own reading (memory) |
| F_u (A36 plate) | 58 ksi | AISC Manual 16th Ed. Table 2-5 (58–80 ksi; minimum used) | own reading (memory) |
| F_EXX (E70XX) | 70 ksi | AISC 360-22 Table J2.5 / AWS D1.1 | own reading (memory) |
| ρ steel | 490 lb/ft³ = 0.2836 lb/in³ | AISC Manual 16th Ed. Part 17 (weight of steel) | own reading (memory) |

Input validation conditions (brief), confirmed by me: post OD 2.375 ≤ rail
OD 2.375 (W8, equal allowed); D_int 1.660 ≤ D_post 2.375 (S4-11);
L = 72 ≥ 2·D_post = 4.750 (S4-12); F_u/F_y = 60/35 = 1.714 ≥ 1.20 for post
and intermediate grade (W5, S4-12); B = 6, N = 8 > post OD 2.375 (S4-6);
0 < t_p = 0.5 < h (D9). All pass, so the full calc runs.

## 2. Limit states considered

Worked from AISC 360-22 by member and connection, not from the plan's list.

**Top rail (round HSS in flexure, AISC 360-22 §F8 via Manual Table 2-4,
verified `aisc360.pipe_as_round_hss`).**

- Flexural yielding, §F8.1: applies, checked (Check 1).
- Flexural local buckling, §F8.2: applies only to noncompact or slender
  walls; D/t = 16.61 < λ_p = 58.00, compact, so not applicable.
- Lateral-torsional buckling: not a limit state for round HSS (verified
  `aisc360.F8.no_ltb`).
- Shear, §G5: excluded from v1 by decision (scope.md). Magnitude for the
  record (own reading of §G5): V ≤ 300 lb against V_n/Ω_v ≈
  (0.6·35·1.02/2)/1.67 = 6.41 kips, about 0.05. Cannot govern.
- Axial compression from the longitudinal guard load: the rail carries it
  axially and is not checked, by decision (loads-and-envelope.md).
  Magnitude for the record: 300 lb against P_c ≈ 13 kips at L_c = 72 in
  (L_c/r = 91.0), about 0.02, and not concurrent with transverse bending.
  Cannot govern.
- Torsion, §H3: the guard load acts through the rail centerline by ruling
  (welds.md, case 4 ruling), so there is no torsion.
- Deflection (serviceability): checked (Check 2).
- Rail wall local strength at the post, Chapter K chord limit states: not
  checked, stated assumption (W7).

**Intermediate rail (round HSS flexure).** Same list as the top rail:
yielding (Check 4a), local buckling not applicable (compact, D/t = 12.77),
no LTB, no shear (scope), no axial load in any case, no torsion. Deflection
checked (Check 4a).

**Post (round HSS, combined axial and flexure).**

- Compression flexural buckling, §E3: applies (Check 5). Torsional or
  flexural-torsional buckling, §E4: not applicable to round HSS (closed,
  doubly symmetric, torsionally stiff). Slender-element compression, §E7:
  not applicable, D/t = 16.61 < 0.11E/F_y = 91.14 (Table B4.1a).
- Flexure, §F8: yielding governs (compact).
- Combined, §H1.1: Eq. H1-1a or H1-1b in the moment cases (Check 5).
- Tension yielding, §D2(a): upward case (Check 5). Tension rupture,
  §D2(b): ruled out in the brief (U = 1.0, F_u/F_y = 1.71).
- Second-order effects: the Appendix 8 gate αP_r/P_e ≤ 0.05 (brief D1).
- Shear, §G5: excluded by decision; magnitude as for the rail, about 0.05.
- Torsion: no eccentric load in any case (the rails frame on the post
  centerline).
- Lateral deflection: Check 6.
- Post wall local strength at the intermediate rail (Chapter K): not
  checked, stated assumption (S4-12).
- Component load's effect on the post: not checked, stated assumption
  (output.md). Magnitude for the record: 50 lb horizontal at some height
  below h gives under 50·41.5 = 2,075 lb-in at the base, against
  12,450 lb-in from w·s. Not concurrent with the guard load, so it cannot
  govern.

**Welds (Checks 3, 4b, 7).**

- Weld metal shear on the effective throat, §J2.4 (Table J2.5): checked.
- Base metal, §J4: shear rupture on the chord wall in-plane (Checks 3, 4b)
  and on the baseplate through t_p (Check 7). Shear yielding §J4.2(a) is
  not a fusion-face limit state (W6). The post side of Check 7 and the
  branch sides of Checks 3 and 4b are covered by the member checks (W5,
  S4-12). I confirmed the S4-12 condition: the Check 4b end moment
  R·e = 67.46 lb-in is no more than Check 4a's downward midspan moment of
  1,023 lb-in.
- Minimum fillet size, Table J2.4: checked. Maximum size, §J2.2b(b): not
  applicable at T-joints (W11).
- Minimum effective length, §J2.2b (4w): ring lengths of 5.2 to 7.5 in are
  far above 4w ≤ 1.0 in, so this does not govern.
- Chapter K chord-wall normal force: not checked (W7, S4-12).

**Baseplate and anchorage.** Plate bending and thickness: not checked (D12,
out of scope). Anchorage: out of scope. Reactions are reported only.

Nothing is flagged as missing from the plan. Every limit state that could
govern is either checked or excluded by a recorded decision, and the
excluded ones are at 0.05 or below here.

## 3. Loads and load path

Dead loads (weights from the AISC database W column):

| Load | Expression | Value |
| --- | --- | --- |
| Top rail w_D,rail | 3.66 plf / 12 | 0.3050 lb/in |
| Intermediate rail w_D,int | 2.27 plf / 12 | 0.1892 lb/in |
| Top rail over span | 0.3050 × 72.00 | 21.96 lb |
| Intermediate rail over span | 0.1892 × 72.00 | 13.62 lb |
| Post, D_post = W·(h − t_p) | (3.66/12) × 41.50 | 12.66 lb |
| **D at the post** (Checks 5, 7) | 21.96 + 13.62 + 12.66 | **48.24 lb** |
| Baseplate W_bp = ρ·B·N·t_p | 0.2836 × 6 × 8 × 0.5 | 6.806 lb |
| **ΣD for reactions** | 48.24 + 6.806 | **55.04 lb** |

Source: brief, loads-and-envelope.md ("Dead load at the post", base
reactions S4-6) and the slice 4 plan ("Where the intermediate rail's dead
load goes"). ρ is my own reading.

Where each load goes:

- **Top rail, Check 1 and 2.** Simple span L = 72 in. Dead load w_D,rail
  is vertical, downward, uniform. P is at midspan; w is uniform over the
  span. The direction cases are downward (D + L on the vertical axis),
  outward and inward (L horizontal, D vertical, resultant by SRSS, verified
  `ej.bending.srss_round`), and upward (L − 0.6D, verified
  `ej.combo.bending.upward`). The longitudinal case is carried axially by
  the rail and not checked.
- **Rail to post weld, Check 3.** The guard load reaches the post top as
  P (placed adjacent to the post, so the full P) or w·s = 300 lb. Dead
  load at the ring is w_D,rail·s = 21.96 lb (not the intermediate rail's;
  the plan's load path). Horizontal cases: V = L at the rail centerline,
  M = V·e at the ring with e = D_rail/2, D axial compression. Downward:
  D + L axial. Upward: L − 0.6D axial tension.
- **Intermediate rail, Check 4a.** Simple span 72 in, P_c at midspan.
  Horizontal: P_c alone (verified `ej.combo.deflection.L_only` for
  deflection). Downward: P_c + w_D,int on the vertical axis, ASD D + L
  (verified `asce7.combo.asd.D_plus_L`; deflection
  `ej.combo.deflection.D_plus_L`). Not concurrent with the top rail loads.
- **Intermediate rail weld, Check 4b.** P_c adjacent to the post, so the
  full P_c reaches the weld, plus R_D = w_D,int·L/2. Horizontal: R =
  √(P_c² + R_D²). Downward: R = R_D + P_c. M = R·e, with e = D_post/2.
- **Post, Checks 5, 6, 7.** Both guard load types act at the post top (P,
  or w·s = 300 lb). Fixed at the top of the baseplate; arm h − t_p =
  41.50 in. D at the post (48.24 lb) is axial compression at the critical
  section in every case. The envelope follows the brief's table: downward
  D + L axial; outward, inward and longitudinal D axial plus M =
  L·(h − t_p); upward 1.0L − 0.6D tension. L = 300 > 0.6D = 28.94, so the
  upward case is a real net-tension case.
- **Reactions.** At the top of concrete, arm h = 42 in, 0.9D + 1.6L
  (engineering judgement), using the larger of P = 200 and w·s = 300:
  **distributed**. D includes the baseplate.

Envelope cases worked: Checks 1 and 2, 4 directions × 2 load types = 8.
Checks 3, 5 and 7, 5 directions × 2 = 10 each. Check 6, 3 horizontal
directions × 2 = 6 (downward and upward produce no lateral deflection).
Check 4a, 2 directions × (bending, deflection). Check 4b, 2 directions.
Reactions, 2 sets.

## 4. Section properties

AISC Shapes Database v16.0 (`data/aisc-shapes-database-v16.0.xlsx`),
used as published (checks.md).

| Property | Pipe2STD (rail, post) | Pipe1-1/4STD (intermediate) |
| --- | --- | --- |
| OD | 2.375 in | 1.660 in |
| t_nom | 0.154 in | 0.140 in |
| t_des | 0.143 in | 0.130 in |
| A | 1.020 in² | 0.625 in² |
| I | 0.627 in⁴ | 0.184 in⁴ |
| S | 0.528 in³ | 0.222 in³ |
| Z | 0.713 in³ | 0.305 in³ |
| r | 0.791 in | 0.543 in |
| W | 3.66 plf | 2.27 plf |
| D/t = OD/t_des | 2.375/0.143 = 16.61 (database 16.6) | 1.660/0.130 = 12.77 (database 12.8) |

D/t is computed from OD and t_des at full precision (AISC 360-22 §B4.2:
t is the design wall thickness). The database's rounded column differs by
0.05% (Pipe2STD) and 0.24% (Pipe1-1/4STD). See open question 2.

Classification, flexure (Table B4.1b, round HSS):
λ_p = 0.07E/F_y = 0.07 × 29,000/35 = 58.00 (verified
`aisc360.B4.1b.round_hss.lambda_p`); λ_r = 0.31E/F_y = 256.9 (verified
`aisc360.B4.1b.round_hss.lambda_r`). Both sections are compact (16.61 and
12.77 < 58.00), per verified `aisc360.B4.1b.classification`. §F8
applicability: D/t < 0.45E/F_y = 372.9 (verified
`aisc360.F8.applicability`). OK for both.

Classification, compression (Table B4.1a, round HSS, own reading):
λ_r = 0.11E/F_y = 91.14. Post 16.61 < 91.14, nonslender.

---

## 5. Check 1: top rail bending

**Capacity (case-independent).**

| Line | Value | Citation, source |
| --- | --- | --- |
| M_n = M_p = F_y·Z = 35 × 0.713 | 24.96 kip-in = 24,955 lb-in | AISC 360-22 Eq. F8-1, verified `aisc360.eq.F8-1`; compact so F8.2 n/a, verified `aisc360.F8.nominal_strength` |
| Ω_b | 1.67 | §F1(a), verified `aisc360.F1.omega_b` |
| M_a = M_n/Ω_b = 24,955/1.67 | 14,943 lb-in | Eq. B3-2, verified `aisc360.eq.B3-2` |

Lb and Cb do not enter (round section, verified `aisc360.F8.no_ltb`).

**Moments.** M_D = w_D·L²/8 = 0.3050 × 72²/8 = 197.6 lb-in (Manual Table
3-23 Case 1, verified `aisc_manual.t3-23.case1.M`).
Concentrated: M_L = P·L/4 = 200 × 72/4 = 3,600 lb-in (Table 3-23 Case 7,
verified `aisc_manual.t3-23.case7.M`).
Distributed: M_L = w·L²/8 = 4.167 × 72²/8 = 2,700 lb-in (Case 1).

| Case | Combination | M_r expression | M_r (lb-in) | Ratio M_r/M_a |
| --- | --- | --- | --- | --- |
| Downward, concentrated | D + L | 197.6 + 3,600 | 3,798 | **0.2541** |
| Downward, distributed | D + L | 197.6 + 2,700 | 2,898 | 0.1939 |
| Outward / inward, concentrated | D + L, SRSS | √(3,600² + 197.6²) | 3,605 | 0.2413 |
| Outward / inward, distributed | D + L, SRSS | √(2,700² + 197.6²) | 2,707 | 0.1812 |
| Upward, concentrated | 0.6D + 1.0L | 3,600 − 0.6 × 197.6 | 3,481 | 0.2330 |
| Upward, distributed | 0.6D + 1.0L | 2,700 − 0.6 × 197.6 | 2,581 | 0.1728 |
| Longitudinal | rail carries axially; not checked (brief) | — | — | — |

**Controlling: downward, concentrated, 0.2541 → 0.25 OK.**

## 6. Check 2: top rail deflection

EI = 29,000,000 × 0.627 = 1.818 × 10⁷ lb-in². Δ_allow = L/120 = 72/120 =
0.6000 in (verified `ej.deflection.limit`).

Δ_D = 5w_D·L⁴/(384EI) = 5 × 0.3050 × 72⁴/(384 × 1.818 × 10⁷) = 0.005870 in
(Table 3-23 Case 1, verified `aisc_manual.t3-23.case1.delta`).
Δ_L,conc = P·L³/(48EI) = 200 × 72³/(48 × 1.818 × 10⁷) = 0.08553 in
(Case 7, verified `aisc_manual.t3-23.case7.delta`).
Δ_L,dist = 5w·L⁴/(384EI) = 5 × 4.167 × 72⁴/(384 × 1.818 × 10⁷) = 0.08018 in.

| Case | Combination (verified entry) | Δ (in) | Ratio Δ/0.6000 |
| --- | --- | --- | --- |
| Downward, concentrated | D + L (`ej.combo.deflection.D_plus_L`) | 0.005870 + 0.08553 = 0.09140 | **0.1523** |
| Downward, distributed | D + L | 0.005870 + 0.08018 = 0.08605 | 0.1434 |
| Outward / inward, concentrated | L only (`ej.combo.deflection.L_only`) | 0.08553 | 0.1426 |
| Outward / inward, distributed | L only | 0.08018 | 0.1336 |
| Upward, concentrated | L only | 0.08553 | 0.1426 |
| Upward, distributed | L only | 0.08018 | 0.1336 |

**Controlling: downward, concentrated, 0.1523 → 0.15 OK.**

## 7. Check 3: top rail weld to post

**Ring and capacities (case-independent).** Model W1 and W3: a flat ring
of the post perimeter at the rail underside.

| Line | Value | Citation, source |
| --- | --- | --- |
| D (post OD) | 2.375 in | W3 |
| L_w = πD | 7.461 in | W3 |
| S_w = πD²/4 | 4.430 in² | W3 (line property) |
| e = D_rail/2 | 1.1875 in | W1 |
| Weld w = 1/8 in; throat t_e = 0.707w | 0.08839 in | AISC 360-22 §J2.2a; own reading |
| F_nw = 0.60F_EXX = 0.60 × 70 | 42.00 ksi | §J2.4, Table J2.5; own reading |
| k_ds | 1.0 (branch-to-chord, W2) | brief W2; §J2.4 own reading |
| Ω (weld) | 2.00 | Table J2.5; own reading |
| Weld allowable = F_nw·t_e·k_ds/Ω = 42.00 × 0.08839 × 1.0/2.00 | 1.856 kip/in = 1,856 lb/in | §J2.4 |
| Base metal (rail wall, chord), shear rupture 0.6F_u·t_des/Ω = 0.6 × 60 × 0.143/2.00 | 2.574 kip/in = 2,574 lb/in | §J4.2(b), Ω = 2.00; own reading; W5, W6 (t_des per W4) |
| Minimum size, Table J2.4: thinner part t_nom = min(0.154, 0.154) = 0.154 in ≤ 1/4 in | w_min = 1/8 in; 1/8 ≥ 1/8 **OK** | Table J2.4, own reading; t_nom per W11 |

**Demands.** D = w_D,rail·s = 21.96 lb; f_a = D/L_w = 21.96/7.461 = 2.943
lb/in (compression) in the horizontal cases. In those cases f_b = V·e/S_w
and f_v = V/L_w (uniform, W3). The governing point is the compression-side
extreme fiber, where f_n = f_b + f_a. The in-plane f_v there is radial,
perpendicular to the weld axis, so f_r = √(f_n² + f_v²) (W10). The base
metal line takes f_v only (W5).

| Case | V or axial | f_a | f_b | f_n | f_v | f_r | Ratio weld | Ratio base | Fiber |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Downward, conc | D + L = 221.96 lb | 29.75 | — | 29.75 | — | 29.75 | 0.01603 | — | uniform |
| Downward, dist | 21.96 + 300 = 321.96 lb | 43.15 | — | 43.15 | — | 43.15 | 0.02325 | — | uniform |
| Out/in/long, conc | V = 200 lb | 2.943 | 200 × 1.1875/4.430 = 53.61 | 56.55 | 26.81 | 62.58 | 0.03372 | 26.81/2,574 = 0.01041 | compression side |
| Out/in/long, dist | V = 300 lb | 2.943 | 80.42 | 83.36 | 40.21 | 92.55 | **0.04986** | 0.01562 | compression side |
| Upward, conc | 200 − 0.6 × 21.96 = 186.8 lb tension | 25.04 | — | 25.04 | — | 25.04 | 0.01349 | — | uniform |
| Upward, dist | 300 − 13.18 = 286.8 lb tension | 38.44 | — | 38.44 | — | 38.44 | 0.02071 | — | uniform |

(Forces in lb/in. The check ratio is the larger of weld and base metal.
In every case it is the weld.)

**Controlling: outward, distributed (inward and longitudinal tie), 0.04986
→ 0.05 OK.**

## 8. Check 4a: intermediate rail member

Pipe1-1/4STD, compact, D/t = 12.77. L = 72 in.

| Line | Value | Citation, source |
| --- | --- | --- |
| M_n = M_p = 35 × 0.305 | 10.68 kip-in = 10,675 lb-in | Eq. F8-1, verified |
| M_a = 10,675/1.67 | 6,392 lb-in | §F1(a), Eq. B3-2, verified |
| EI = 29 × 10⁶ × 0.184 | 5.336 × 10⁶ lb-in² | |
| Δ_allow = 72/120 | 0.6000 in | verified `ej.deflection.limit` |
| M_D = w_D,int·L²/8 = 0.1892 × 72²/8 | 122.6 lb-in | Table 3-23 Case 1, verified |
| M_L = P_c·L/4 = 50 × 72/4 | 900.0 lb-in | Case 7, verified; P_c point load at midspan, S4-3 |
| Δ_D = 5 × 0.1892 × 72⁴/(384EI) | 0.01241 in | Case 1, verified |
| Δ_L = 50 × 72³/(48EI) | 0.07286 in | Case 7, verified |

| Case | M_r (lb-in) | Bending ratio | Δ (in) | Deflection ratio |
| --- | --- | --- | --- | --- |
| Horizontal (P_c alone; Δ L only) | 900.0 | 900.0/6,392 = 0.1408 | 0.07286 | 0.1214 |
| Downward (D + L) | 122.6 + 900.0 = 1,023 | **0.1600** | 0.01241 + 0.07286 = 0.08527 | 0.1421 |

**Controlling: downward, bending, 0.1600 → 0.16 OK.** Deflection
controlling: downward, 0.1421 → 0.14 OK.

## 9. Check 4b: intermediate rail weld to post

Ring of the intermediate rail's perimeter at the post face (S4-8, S4-11),
k_ds = 1.0 (branch-to-chord), base metal on the post wall (chord, S4-12).

| Line | Value | Citation, source |
| --- | --- | --- |
| D_int | 1.660 in | |
| L_w = πD_int | 5.215 in | W3 |
| S_w = πD_int²/4 | 2.164 in² | W3 |
| e = D_post/2 | 1.1875 in | S4-9 |
| R_D = w_D,int·L/2 = 0.1892 × 36 | 6.810 lb | S4-9 |
| t_e = 0.707 × 0.125 | 0.08839 in | §J2.2a, own reading |
| F_nw | 42.00 ksi | §J2.4, own reading |
| Weld allowable (k_ds = 1.0) | 1,856 lb/in | §J2.4, Ω = 2.00, own reading |
| Base metal, post wall shear rupture 0.6 × 60 × 0.143/2.00 | 2,574 lb/in | §J4.2(b), own reading; S4-12, t_des,post |
| Minimum size: thinner part t_nom = min(0.140, 0.154) = 0.140 in ≤ 1/4 | w_min = 1/8; 1/8 ≥ 1/8 **OK** (at the minimum) | Table J2.4, own reading |

| Case | R (lb) | M = R·e (lb-in) | f_b = M/S_w | f_v = R/L_w | f_r = √(f_b² + f_v²) | Ratio weld | Ratio base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Horizontal | √(50² + 6.810²) = 50.46 | 59.92 | 27.69 | 9.676 | 29.33 | 0.01580 | 0.003759 |
| Downward | 6.810 + 50 = 56.81 | 67.46 | 31.17 | 10.89 | 33.02 | **0.01779** | 0.004232 |

(Forces in lb/in.) No axial force on this ring, so no f_a term. The R·e
moment is normal to the ring's plane, so the extreme-fiber f_b and the
in-plane f_v are perpendicular and combine by SRSS.

**Controlling: downward, component, 0.01779 → 0.02 OK.**

## 10. Check 5: post combined axial and flexure

**Capacities (case-independent).**

| Line | Value | Citation, source |
| --- | --- | --- |
| K | 2.1 | AISC 360-22 Commentary App. 7, Table C-A-7.1 (fixed-free, recommended); own reading; brief D3 |
| L_c = K·h = 2.1 × 42 | 88.20 in | brief D3 (h, not h − t_p) |
| L_c/r = 88.20/0.791 | 111.5 (≤ 200, no flag) | §E2 User Note; own reading |
| F_e = π²E/(L_c/r)² = π² × 29,000/111.5² | 23.02 ksi | Eq. E3-4; own reading |
| 4.71√(E/F_y) = 4.71√(29,000/35) | 135.6 | §E3; own reading |
| L_c/r = 111.5 ≤ 135.6, so **Eq. E3-2** | | |
| F_y/F_e = 35/23.02 | 1.520 | |
| F_cr = 0.658^(F_y/F_e)·F_y = 0.658^1.520 × 35 | 18.52 ksi | Eq. E3-2; own reading |
| P_n = F_cr·A_g = 18.52 × 1.02 | 18.89 kips = 18,893 lb | Eq. E3-1; own reading |
| Ω_c | 1.67 | §E1; own reading |
| P_c = P_n/Ω_c | 11,313 lb | |
| M_n = M_p = 35 × 0.713 | 24,955 lb-in | Eq. F8-1, verified |
| M_c = M_n/Ω_b | 14,943 lb-in | §F1(a), verified |
| P_t = F_y·A_g/Ω_t = 35 × 1.02/1.67 | 21.38 kips = 21,377 lb | §D2(a), Eq. D2-1, Ω_t = 1.67; own reading |
| P_e = π²EI/L_c² = π² × 29,000 × 0.627/88.20² | 23.07 kips = 23,069 lb | App. 8 form at L_c = K·h (brief D1); own reading |

**Envelope.** D = 48.24 lb (Section 3). Arm h − t_p = 41.50 in.

| Case | P_r (lb) | M_r (lb-in) | Equation | Ratio | αP_r/P_e |
| --- | --- | --- | --- | --- | --- |
| Downward, conc | 48.24 + 200 = 248.2 C | 0 | P_r/P_c (Ch. E, axial only) | 0.02194 | — |
| Downward, dist | 48.24 + 300 = 348.2 C | 0 | P_r/P_c | 0.03078 | — |
| Out/in/long, conc | 48.24 C | 200 × 41.50 = 8,300 | H1-1b (P_r/P_c = 0.004264 < 0.2) | 48.24/(2 × 11,313) + 8,300/14,943 = 0.002132 + 0.5554 = 0.5576 | 1.6 × 48.24/23,069 = 0.003346 |
| Out/in/long, dist | 48.24 C | 300 × 41.50 = 12,450 | H1-1b | 0.002132 + 0.8332 = **0.8353** | 0.003346 |
| Upward, conc | 200 − 0.6 × 48.24 = 171.1 T | 0 | P_r/P_t (Ch. D, axial only) | 0.008002 | — |
| Upward, dist | 300 − 28.94 = 271.1 T | 0 | P_r/P_t | 0.01268 | — |

H1-1b per AISC 360-22 §H1.1(b), own reading: P_r/(2P_c) + M_r/M_c ≤ 1.0
for P_r/P_c < 0.2. α = 1.6 (ASD), App. 8, own reading. Every αP_r/P_e =
0.003346 ≤ 0.05, so second-order effects are negligible and amplification
is taken as 1.0 (brief D1). Upward net tension exists: L > 0.6D in both
types.

**Controlling: outward, distributed (inward and longitudinal tie), 0.8353
→ 0.84 OK.**

## 11. Check 6: post deflection

Δ = V·(h − t_p)³/(3EI), live load only (brief). (h − t_p)³ = 41.50³ =
71,473 in³. 3EI = 3 × 1.818 × 10⁷ = 5.455 × 10⁷ lb-in².
Δ_allow = (h − t_p)/60 = 41.50/60 = 0.6917 in (post limit, engineering
judgement, brief).

| Case | V (lb) | Δ (in) | Ratio |
| --- | --- | --- | --- |
| Outward / inward / longitudinal, conc | 200 | 0.2621 | 0.3789 |
| Outward / inward / longitudinal, dist | 300 | 0.3931 | **0.5683** |
| Downward, upward | vertical, no lateral deflection | — | — |

**Controlling: outward, distributed, 0.5683 → 0.57 OK.**

## 12. Check 7: post weld to baseplate

**Ring and capacities (case-independent).**

| Line | Value | Citation, source |
| --- | --- | --- |
| D (post OD), L_w = πD, S_w = πD²/4 | 2.375 in, 7.461 in, 4.430 in² | W3 |
| Arm h − t_p | 41.50 in | welds.md |
| w = 1/4 in; t_e = 0.707w | 0.1768 in | §J2.2a, own reading |
| F_nw = 0.60F_EXX | 42.00 ksi | §J2.4, own reading |
| θ at the governing point | 90° (see below) | W2, W3 |
| k_ds = 1.0 + 0.50 sin^1.5(90°) | 1.500 | §J2.4; own reading; W2 (round-HSS applicability is a drafted entry I did not read) |
| Weld allowable = 42.00 × 0.1768 × 1.5/2.00 | 5.568 kip/in = 5,568 lb/in | §J2.4, Ω = 2.00 |
| Base metal, baseplate shear rupture 0.6F_u·t_p/Ω = 0.6 × 58 × 0.5/2.00 | 8.700 kip/in = 8,700 lb/in | §J4.2(b); own reading; W5 |
| Post side | covered by Check 5 (W5); F_u/F_y = 1.71 ≥ 1.20 | |
| Minimum size: thinner part = min(t_nom,post 0.154, t_p 0.500) = 0.154 in | w_min = 1/8; 1/4 ≥ 1/8 **OK** | Table J2.4, own reading |

θ: at the extreme fiber, the normal component (vertical) and the radial
shear component (horizontal, in the plane of the ring, pointing across
the weld) are both perpendicular to the weld's tangential axis. So their
resultant is too, and θ = 90°. In the downward and upward cases the force
is vertical everywhere, so θ = 90° all around. k_ds = 1.5 in every case.

**Demands.** f_a = D/L_w = 48.24/7.461 = 6.465 lb/in (compression) in the
horizontal cases. f_b = M/S_w, f_v = V/L_w. Compression-side fiber governs.

| Case | Axial or V | f_a | f_b | f_n | f_v | f_r | Ratio weld | Ratio base | Fiber |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Downward, conc | 248.2 lb C | 33.27 | — | 33.27 | — | 33.27 | 0.005975 | 0.003824 | uniform |
| Downward, dist | 348.2 lb C | 46.67 | — | 46.67 | — | 46.67 | 0.008382 | 0.005365 | uniform |
| Out/in/long, conc | V = 200, M = 8,300 | 6.465 | 1,874 | 1,880 | 26.81 | 1,880 | 0.3376 | 0.2161 | compression side |
| Out/in/long, dist | V = 300, M = 12,450 | 6.465 | 2,810 | 2,817 | 40.21 | 2,817 | **0.5059** | 0.3238 | compression side |
| Upward, conc | 171.1 lb T | 22.93 | — | 22.93 | — | 22.93 | 0.004117 | 0.002635 | uniform |
| Upward, dist | 271.1 lb T | 36.33 | — | 36.33 | — | 36.33 | 0.006524 | 0.004176 | uniform |

(Forces in lb/in. On the tension side, f_r = √((2,810 − 6.465)² + 40.21²)
= 2,804 lb/in in the distributed case, so the compression side governs, as
W10 expects.)

**Controlling: outward, distributed (inward and longitudinal tie), 0.5059
→ 0.51 OK.**

## 13. Anchor reaction sets (LRFD, at the top of concrete)

Combination 0.9D + 1.6L, engineering judgement (brief S4-4); factors from
the brief, not ASCE (own reading: ASCE 7-22 §2.3.1 has no such
combination). Load type: max(P = 200, w·s = 300) = **distributed**,
300 lb. Arm h = 42.00 in.

D breakdown: top rail 21.96 + intermediate rail 13.62 + post 12.66 +
baseplate 6.806 = **55.04 lb**.

| Set | V (lb) | N (lb), tension + | M (lb-in) |
| --- | --- | --- | --- |
| Lateral | 1.6 × 300 = **480.0** | −0.9 × 55.04 = **−49.54** (compression) | 480.0 × 42.00 = **20,160** |
| Upward (1.6L = 480 > 0.9D = 49.54, so present) | **0** | 480.0 − 49.54 = **+430.5** (tension) | **0** |

## 14. Summary

| Check | Controlling case | Ratio | Result |
| --- | --- | --- | --- |
| 1 Top rail bending | downward, concentrated | 0.2541 | OK |
| 2 Top rail deflection | downward, concentrated | 0.1523 | OK |
| 3 Rail to post weld | outward, distributed (weld metal) | 0.04986 | OK |
| 4a Intermediate rail | downward, bending | 0.1600 | OK |
| 4b Intermediate rail weld | downward, component (weld metal) | 0.01779 | OK |
| 5 Post combined | outward, distributed, H1-1b | 0.8353 | OK |
| 6 Post deflection | outward, distributed | 0.5683 | OK |
| 7 Post to baseplate weld | outward, distributed (weld metal) | 0.5059 | OK |
| Reactions | lateral: V 480.0, N −49.54, M 20,160; upward: N +430.5 | — | reported |

## 15. Values from my own reading (no verified entry)

| Value | Citation | Source |
| --- | --- | --- |
| P_c = 50 lb | ASCE 7-22 §4.5.1.2 | memory |
| F_u = 60 ksi, A53 Gr B | AISC Manual 16th Ed. Table 2-4 | memory |
| F_u = 58 ksi, A36 plate | AISC Manual 16th Ed. Table 2-5 | memory |
| F_EXX = 70 ksi | AISC 360-22 Table J2.5 (E70 electrode) | memory |
| ρ = 490 lb/ft³ | AISC Manual 16th Ed. Part 17 | memory |
| λ_r = 0.11E/F_y, round HSS compression | AISC 360-22 Table B4.1a | memory |
| K = 2.1, fixed-free | AISC 360-22 Commentary App. 7, Table C-A-7.1 | memory; also brief D3 |
| L_c/r ≤ 200 recommendation | AISC 360-22 §E2 User Note | memory |
| F_e = π²E/(L_c/r)² | AISC 360-22 Eq. E3-4 | memory |
| E3-2 branch limit 4.71√(E/F_y); F_cr = 0.658^(F_y/F_e)F_y | AISC 360-22 §E3, Eq. E3-2 | memory |
| P_n = F_cr·A_g; Ω_c = 1.67 | AISC 360-22 Eq. E3-1, §E1 | memory |
| P_n = F_y·A_g; Ω_t = 1.67 | AISC 360-22 §D2(a), Eq. D2-1 | memory |
| H1-1a/H1-1b and the 0.2 threshold | AISC 360-22 §H1.1 | memory |
| α = 1.6 (ASD); P_e = π²EI/L_c² | AISC 360-22 Appendix 8 | memory; length per brief D1 |
| t_e = 0.707w (equal-leg fillet) | AISC 360-22 §J2.2a | memory |
| F_nw = 0.60F_EXX; Ω = 2.00 | AISC 360-22 §J2.4, Table J2.5 | memory |
| k_ds = 1.0 + 0.50 sin^1.5 θ | AISC 360-22 §J2.4 | memory; brief W2 |
| Base metal shear rupture 0.60F_u·A_nv, Ω = 2.00 | AISC 360-22 §J4.2(b), Eq. J4-4 | memory |
| Minimum fillet 1/8 in for thinner part ≤ 1/4 in | AISC 360-22 Table J2.4 | memory |
| 0.9D + 1.6L reaction factors | brief S4-4 (engineering judgement) | brief |

## 16. Open questions

1. **k_ds on a round-HSS-to-plate fillet weld (Check 7).** The brief
   applies k_ds = 1.5 (W2), citing a drafted entry and an STI source that I
   may not read. From my own memory I'm not sure whether AISC 360-22
   Chapter K (§K5 or its commentary) restricts the §J2.4 directional
   increase for welds of HSS ends to plates. My recollection is that the
   explicit exclusion is for rectangular HSS. I applied 1.5 as the brief
   decides. If 1.0 were required, Check 7 would rise to 0.5059 × 1.5 =
   0.7589, still OK. This is already on the release review list through
   the drafted entry, so it is not a new decision.
2. **D/t: computed or tabulated.** I used OD/t_des at full precision
   (16.61, 12.77). The database column reads 16.6 and 12.8. That moves
   only the classification line, never a ratio. Pipe1-1/4STD differs by
   0.24%, inside the 0.5% tolerance, so the test passes either way. Noted
   in case the tool prints the tabulated value.
3. **Uniform shear in the ring (W3).** The true elastic shear flow in a
   ring under lateral V is zero at the extreme fiber and 2V/(πD) at the
   neutral axis. The decided model, uniform V/(πD) added at the extreme
   fiber, is conservative at the governing point. At the neutral axis
   (f_n = f_a only, shear along the weld axis, θ = 0, k_ds = 1.0 in
   Check 7) the demand is about 2 × 40.21 = 80.4 lb/in against
   1.0 × 3,712 = 3,712 lb/in, negligible. I followed the brief.
4. **Plan status line.** docs/plans/slice-4.md still reads "Status:
   planned … Not started; no branch yet", although the branch is at step
   9 or later. Doc wording only; it changes no value.

No key in the values file was left unfilled, and every value I computed
for a check has a key. Some values have no key, but none is a check
result: Δ_D and Δ_L separately, P_r/P_c in the moment cases, F_y/F_e,
P_e, the classification limits, and the tension-side f_r of Check 7.

## 17. Review checklist (docs/brief/verification.md)

1. **Loads complete.** Top rail, intermediate rail and post dead loads are
   carried to the post (48.24 lb), and the baseplate goes into the
   reactions only (55.04 lb). Both guard load types run in every check. The
   component load runs in 4a and 4b. The intermediate rail's dead load
   enters Checks 4a (downward), 4b, 5, 7 and the reactions. It stays out
   of Check 3, which has only the top rail's 21.96 lb, and out of Check 6.
   Yes.
2. **Direction and worst case.** Every check lists all five directions or
   says why one is not worked (Check 1/2 longitudinal is axial in the
   rail; Check 6 has no vertical deflection). Every controlling case was
   found by computing all cases. Upward uses 0.6D + 1.0L; reactions use
   0.9D + 1.6L. Yes.
3. **Checks complete.** Section 2 lists every limit state; the ones not
   checked are excluded by recorded decisions and are at 0.05 or below.
   Nothing new to flag.
4. **Geometry.** h − t_p = 41.50 in for Checks 5, 6 and 7 (moment, Δ, weld
   arm); h = 42 in for L_c (D3) and the reaction arm; e = D_rail/2 =
   1.1875 in (Check 3); e = D_post/2 = 1.1875 in (Check 4b; equal to Check
   3's only because rail and post OD are equal); span 72 in; Check 4b
   ring D_int = 1.660 in; Check 3 and 7 ring D_post = 2.375 in. Yes.
5. **Method and equations.** Both sections are compact and inside §F8
   scope; the post is nonslender in compression; L_c/r = 111.5 < 135.6, so
   E3-2; P_r/P_c = 0.004264 < 0.2, so H1-1b; axial-only cases use Chapters
   E and D (D8); the second-order gate passes (0.003346). Yes.
6. **Assumptions.** Fixed at the top of the baseplate; K = 2.1 on h;
   tributary length = span; the P_c point load at midspan for 4a and
   adjacent to the post for 4b; the rigid baseplate; the ring models. All
   follow the brief.
7. **Code editions.** AISC 360-22, AISC Manual 16th Ed., ASCE 7-22 and
   Shapes Database v16.0 throughout. Equation numbers are from memory of
   360-16 and assumed unchanged in 360-22 (Section 15).
8. **Magnitude sense.** The Check 5 ratio of 0.84 is dominated by
   flexure, as expected for a 42 in Pipe2STD post under 300 lb; the post
   axial is tiny. Check 7 at about 0.5 for a 1/4 in weld matches a
   12.45 kip-in base moment. Welds at the rail are 0.02–0.05. The Check 6
   deflection of 0.39 in at 41.5 in is plausible for Pipe2STD. Units are
   consistent (lb, in).
9. **Governing case.** As expected: the distributed load governs the post
   (w·s = 300 > P = 200), and the post's horizontal case controls Checks
   5, 6 and 7. The concentrated load governs the rail (P·L/4 = 3,600 >
   w·L²/8 = 2,700), with downward controlling Checks 1 and 2 (D adds to
   L). Downward controls Checks 4a and 4b (D adds to P_c). Overall Check 5
   governs the guard at 0.84.
