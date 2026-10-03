# Independent calc: test case 2 (post, Checks 5 and 6)

| | |
| --- | --- |
| Case | tests/cases/case-02.toml, "Test case 2": Pipe1-1/2STD post, h = 42 in, t_p = 1/2 in, on case 1's rail and span |
| Date | 2026-10-03 |
| Model | claude-opus-5-5 (Claude Opus 5.5), fresh session, independent-calc skill |
| Branch, commit | slice-2 at 45c8ab72df70becf359ef448b522c3717be2a8ef |
| Covers | post properties, Check 5 (post axial + flexure), Check 6 (post deflection) |

**Sources read.** The case inputs with the `hand` and `independent` tables
stripped (skill command); docs/BRIEF.md and every file in docs/brief/
(scope, inputs, loads-and-envelope, checks, welds, output, verification);
CONTEXT.md; the slice 2 plan's decisions (docs/plans/slice-2.md, D1–D9 and
"What the slice does"), its computed values ignored; the first lines of
docs/plans/slice-1.md, only to confirm it is marked completed; the
registry entries with status "verified" (skill command); the Pipe1-1/2STD
row of data/aisc-shapes-database-v16.0.xlsx (skill command; rail and post
are the same section, so one row); the template
tests/cases/independent/case-02.toml. Code provisions with no verified entry
are from my own reading (memory) of AISC 360-22, the AISC Manual 16th Ed.
and ASCE 7-22, recorded in "Values from my own reading" below. Nothing in
src/, no tool output, no drafted registry entry and no git history was read.

**Citation tags.** `[V: id]` is a verified registry entry. `[own]` is my
own reading, from memory, listed with its citation in the "own reading"
section. `[brief]`, `[plan Dn]` and `[input]` are the brief, a slice 2 plan
decision and the case file.

Units: lb, in, ksi, lb-in, kip only where noted (1 kip = 1000 lb).
Values shown to 4 significant figures; carried at full precision.

---

## 1. Inputs

| Symbol | Value | Source |
| --- | --- | --- |
| s, span (post to post, c/c) | 7'-0" = 84.00 in = 7.000 ft | [input] geometry.span |
| h, post height (top of concrete to rail centerline) | 42.00 in | [input] geometry.post_height |
| t_p, baseplate thickness | 1/2 in = 0.5000 in | [input] geometry.baseplate_thickness |
| Top rail | Pipe1-1/2STD, A53 Gr B | [input] top_rail |
| Post | Pipe1-1/2STD, A53 Gr B | [input] post |
| Intermediate rail | none | [input] (no section given) |
| Post deflection limit | L/60, not bypassed | [input] deflection.post |
| P, concentrated guard load | 200 lb, any direction | [V: asce7.guard.concentrated], ASCE 7-22 §4.5.1 |
| w, distributed guard load | 50 lb/ft, any direction, not concurrent with P | [V: asce7.guard.uniform], ASCE 7-22 §4.5.1.1 |
| Distributed-load exemption | not claimed (no input), so w applies | [input], [brief] inputs.md |
| E | 29,000 ksi | [V: material.steel.E], AISC 360-22 Symbols |
| F_y, A53 Gr B | 35 ksi | [V: material.A53_GrB.Fy], AISC Manual Table 2-4 |
| F_u, A53 Gr B | 60 ksi (used only in the information-only rupture line) | [own] O-15 |
| Pipe designed as round HSS | yes | [V: aisc360.pipe_as_round_hss] |

Derived geometry:

| Symbol | Equation | Substituted | Result | Cite |
| --- | --- | --- | --- | --- |
| L_p, cantilever length | h − t_p | 42.00 − 0.5000 | 41.50 in | [plan D4], [brief] checks.md Check 6 |
| L_c, effective length | K·h | 2.1 × 42.00 | 88.20 in | [plan D3], K [own] O-6 |

## 2. Limit states considered

Worked from AISC 360-22 by chapter for the post (the member in this case's
scope), not from the plan's list. The rail is in the model only as a load
source; Checks 1 and 2 are covered by case 1 and not recorded here.

| Limit state | AISC 360-22 | Applies? | Why |
| --- | --- | --- | --- |
| Local buckling classification, compression | Table B4.1a, round HSS | Yes, as a gate | Slender walls would reduce Pn (§E7); computed in §4 |
| Local buckling classification, flexure | Table B4.1b, round HSS | Yes, as a gate | Selects F8.1 vs F8.2; computed in §4 |
| Flexural buckling | §E3 | Yes | Cantilever column under D (and D + L downward) |
| Torsional / flexural-torsional buckling | §E4 | No | Closed round section, doubly symmetric with very large GJ; §E4 is for open singly-symmetric, unsymmetric and certain doubly symmetric (cruciform, built-up) shapes |
| Slender-element compression | §E7 | No | Nonslender (§4) |
| Tensile yielding, gross section | §D2(a) | Yes | Upward case puts net tension in the post |
| Tensile rupture, net section | §D2(b) with §D3 | Applies; does not govern | Welded all around to the baseplate, so U = 1.0 and A_e = A_g; F_u/Ω_t = 60/2.00 = 30 ksi > F_y/Ω_t = 35/1.67 = 20.96 ksi. Not in the plan; shown for information in §7. Flag F-4 |
| Flexural yielding | §F8.1 | Yes | Compact section, M_n = M_p |
| Flexural local buckling | §F8.2 | No | Compact (§4) |
| Lateral-torsional buckling | — | No | Round HSS has no LTB limit state [V: aisc360.F8.no_ltb]; L_b and C_b do not enter [plan D5] |
| Combined axial + flexure | §H1.1 | Yes, moment cases | Outward, inward, longitudinal: D axial with live moment |
| Combined tension + flexure | §H1.2 | No | No case has tension and moment together (upward has no moment) |
| §H1.3 (single-axis, out-of-plane) | §H1.3 | No | Permissive alternative for compact rolled shapes; §H1.1 is used |
| Torsion, combined torsion | §H3 | No | Guard loads act at the rail centerline over the post axis; no eccentricity to the post axis in any case |
| Shear | §G5 | Excluded by the brief | "No shear checks in any member" [brief] output.md. For information only: §7 gives ratio 0.07 |
| Second-order effects | Ch. C, App. 7, App. 8 | Yes, as a gate | [plan D1]: αPr/Pe ≤ 0.05 in moment cases, amplification taken as 1.0. Notional loads in the gravity-only case are not in the plan: flag F-1 |
| Slenderness recommendation | §E2 User Note | Yes, as a flag | L_c/r ≤ 200 recommended [plan D6] |
| Concentrated forces on the HSS wall at the coped top (rail bearing / weld) | Ch. K, §J2 | Not in this slice | Check 3 territory (rail-to-post weld), not built in slice 2 |
| Post-to-baseplate weld; baseplate; anchorage | §J2, Ch. K | Not in this slice / out of v1 | Check 7 is not in slice 2; anchorage is out of v1 scope |
| Serviceability: cantilever drift | — (not code) | Yes | Check 6, L/60 over h − t_p [brief] |

## 3. Loads and load path

### 3.1 Dead load

| Symbol | Equation | Substituted | Result | Cite |
| --- | --- | --- | --- | --- |
| W_rail | tabulated | — | 2.720 lb/ft | AISC Shapes DB v16.0, Pipe1-1/2STD, W |
| W_post | tabulated | — | 2.720 lb/ft | same row |
| D_rail, rail dead load to the post | W_rail · s | 2.720 lb/ft × 7.000 ft | 19.04 lb | tributary = span [brief] inputs.md, output.md |
| D_post | W_post · (h − t_p) | 2.720 lb/ft × 41.50/12 ft | 9.407 lb | [plan D2] |
| D, axial dead load at the critical section | D_rail + D_post | 19.04 + 9.407 | 28.45 lb (compression) | [plan D2] |

Path: rail weight bears on the coped post top concentrically (rail
continuous over the post, post welded to its underside [brief]
output.md), so it enters the post as pure axial load with no moment. The
post's own weight is distributed down its length; all of it is taken at
the critical section (top of baseplate) [plan D2, D4]. No intermediate
rail. The baseplate weight is below the critical section and does not
enter Checks 5 or 6.

### 3.2 Guard loads at the post

Both load types are applied at the top of the post, on the rail
centerline (height h above concrete, L_p = 41.50 in above the critical
section) [brief] loads-and-envelope.md; [plan] envelope.

| Load type | Force at post top | Equation | Result | Cite |
| --- | --- | --- | --- | --- |
| Concentrated | V_c = P | — | 200.0 lb | [V: asce7.guard.concentrated] |
| Distributed | V_w = w · s | 50 lb/ft × 7.000 ft | 350.0 lb | [V: asce7.guard.uniform]; tributary = span |

Worst point of application for the post: P directly over the post puts
all of P into this post; any other position on the rail shares it with the
adjacent post. The horizontal force produces the largest base moment when
applied at the highest point, the rail centerline at h. Never concurrent
with each other [V: asce7.guard.uniform].

### 3.3 Combinations and envelope cases

| Case | Axial at critical section | Moment at critical section | Combination | Cite |
| --- | --- | --- | --- | --- |
| Downward | D + L, compression | 0 | D + L | [V: asce7.combo.asd.D_plus_L] |
| Outward | D, compression | L · L_p | D + L (D, L on different actions) | [V: asce7.combo.asd.D_plus_L] |
| Inward | D, compression | L · L_p (opposite sign) | D + L | same |
| Longitudinal | D, compression | L · L_p about the other axis | D + L | same; [brief] loads-and-envelope.md |
| Upward | 1.0L − 0.6D, tension if > 0 | 0 | 0.6D + 1.0L, engineering judgement | [V: ej.combo.bending.upward] |
| Deflection (horizontal cases) | — | — | L only | [V: ej.combo.deflection.L_only] |

Each of the five directions is run with each of the two load types: ten
strength cases, six deflection cases (downward and upward give no lateral
deflection). For a round post, outward, inward and longitudinal are
identical in magnitude; all are computed and listed.

Upward net-tension test: 0.6D = 0.6 × 28.45 = 17.07 lb, less than both
200.0 lb and 350.0 lb, so both upward cases have net tension and are
checked (the plan's "no net tension" status does not arise).

Inclined directions: ASCE 7-22 says "any direction". A load inclined at θ
above the horizontal adds axial and loses moment. With the H1-1b
coefficients of §5, the worst θ is atan[(1/2Pc)/(L_p/Mc)] = 1.074°, and
the ratio rises by a factor of 1.000175 (0.018%) over θ = 0 for both
load types. So the orthogonal cases envelope the inclined ones to well
within the 0.5% test tolerance. Flag F-3.

## 4. Section properties and classification (post)

From the AISC Shapes Database v16.0 row for Pipe1-1/2STD, used as
published [brief] checks.md. The rail is the same row (W used in §3.1).

| Symbol | Column | Value |
| --- | --- | --- |
| D (OD) | OD | 1.900 in |
| t_des | tdes | 0.1350 in |
| A_g | A | 0.7490 in² |
| W | W | 2.720 lb/ft |
| I | Ix (= Iy) | 0.2930 in⁴ |
| S | Sx | 0.3090 in³ |
| Z | Zx | 0.4210 in³ |
| r | rx (= ry) | 0.6260 in |
| D/t | D/t | 14.10 (check: 1.900/0.1350 = 14.07, the database rounds to 14.1) |

Classification (D/t = 14.10 as published):

| Test | Limit equation | Substituted | Limit | Result | Cite |
| --- | --- | --- | --- | --- | --- |
| Compression, slender? | λ_r = 0.11E/F_y | 0.11 × 29,000/35 | 91.14 | 14.10 ≤ 91.14: nonslender | Table B4.1a, round HSS [own] O-3 |
| Flexure, compact? | λ_p = 0.07E/F_y | 0.07 × 29,000/35 | 58.00 | 14.10 ≤ 58.00: compact | [V: aisc360.B4.1b.round_hss.lambda_p] |
| Flexure, slender? | λ_r = 0.31E/F_y | 0.31 × 29,000/35 | 256.9 | not slender | [V: aisc360.B4.1b.round_hss.lambda_r] |
| §F8 applicability | D/t < 0.45E/F_y | 0.45 × 29,000/35 | 372.9 | 14.10 < 372.9: §F8 applies | [V: aisc360.F8.applicability] |

## 5. Check 5: post combined axial and flexure

### 5.1 Case-independent capacities

**Compression (Chapter E).**

| Symbol | Equation | Substituted | Result | Cite |
| --- | --- | --- | --- | --- |
| K | recommended design value, fixed-free | — | 2.1 | AISC 360-22 Comm. App. 7, Table C-A-7.1 [own] O-6; [plan D3] |
| L_c | K·h | 2.1 × 42.00 | 88.20 in | [plan D3] |
| L_c/r | | 88.20/0.6260 | 140.9 | §E2 |
| §E2 flag | L_c/r ≤ 200? | 140.9 ≤ 200 | no flag | §E2 User Note [own] O-7; [plan D6] |
| Branch limit | 4.71√(E/F_y) | 4.71 × √(29,000/35) = 4.71 × 28.78 | 135.6 | §E3 [own] O-5 |
| Branch | L_c/r vs limit | 140.9 > 135.6 | Eq. E3-3 | §E3(b) [own] O-5 |
| (equivalent test) | F_y/F_e vs 2.25 | 35/14.42 = 2.427 > 2.25 | Eq. E3-3, consistent | §E3 [own] O-5 |
| F_e | π²E/(L_c/r)² | π² × 29,000/140.9² | 14.42 ksi | Eq. E3-4 [own] O-4 |
| F_cr | 0.877F_e | 0.877 × 14.42 | 12.64 ksi | Eq. E3-3 [own] O-4 |
| P_n | F_cr·A_g | 12.64 × 0.7490 | 9.471 kip = 9471 lb | Eq. E3-1 [own] O-4 |
| Ω_c | | | 1.67 | §E1 [own] O-1 |
| P_c | P_n/Ω_c | 9471/1.67 | 5671 lb | §E1; Eq. B3-2 [V: aisc360.eq.B3-2] |

For reference only, Eq. E3-2 at this slenderness would give F_cr =
0.658^2.427 × 35 = 12.67 ksi, 0.2% above E3-3: the two branches nearly
meet here, so a branch error would barely move P_c. The branch itself is
still a test value (Fcr_equation).

**Tension (Chapter D).**

| Symbol | Equation | Substituted | Result | Cite |
| --- | --- | --- | --- | --- |
| P_n (yielding) | F_y·A_g | 35 × 0.7490 | 26.22 kip = 26,215 lb | Eq. D2-1 [own] O-8 |
| Ω_t | | | 1.67 | §D2(a) [own] O-8 |
| P_t | P_n/Ω_t | 26,215/1.67 | 15,698 lb | §D2(a) [own] O-8 |

**Flexure (Chapter F).**

| Symbol | Equation | Substituted | Result | Cite |
| --- | --- | --- | --- | --- |
| Classification | compact | §4 | F8.1 only | [V: aisc360.F8.nominal_strength] |
| LTB | not a limit state | — | L_b, C_b do not enter | [V: aisc360.F8.no_ltb] |
| M_n = M_p | F_y·Z | 35 × 0.4210 | 14.74 kip-in = 14,735 lb-in | Eq. F8-1 [V: aisc360.eq.F8-1] |
| Ω_b | | | 1.67 | [V: aisc360.F1.omega_b] |
| M_c | M_n/Ω_b | 14,735/1.67 | 8823 lb-in | Eq. B3-2 [V: aisc360.eq.B3-2] |

Sanity: M_p/M_y = Z/S = 0.4210/0.3090 = 1.362, the usual shape factor for a
thick pipe; no 1.6M_y cap exists in §F8 and it would not bind anyway.

**Second-order gate (plan D1).**

| Symbol | Equation | Substituted | Result | Cite |
| --- | --- | --- | --- | --- |
| P_e | π²EI/L_c² | π² × 29,000 × 0.2930/88.20² | 10.78 kip = 10,780 lb | App. 8 P_e form [own] O-10; L_c = 2.1h [plan D1] |
| α | ASD | | 1.6 | App. 8 [own] O-10 |
| Limit | | | 0.05 | [plan D1] (engineer) |

**Interaction selection (§H1.1).** In every moment case P_r = D = 28.45 lb,
so P_r/P_c = 28.45/5671 = 0.005016 < 0.2: Eq. H1-1b,
P_r/(2P_c) + (M_rx/M_cx + M_ry/M_cy) ≤ 1.0 [own] O-9. Each moment case has
a single moment (the post carries no dead-load moment), so the round-section
SRSS [V: ej.bending.srss_round] reduces to that one moment.

### 5.2 Envelope cases

**Downward, concentrated** (axial only, [plan D8]):
P_r = D + P = 28.45 + 200.0 = 228.4 lb compression [V: asce7.combo.asd.D_plus_L].
M_r = 0. Ratio = P_r/P_c = 228.4/5671 = **0.04028**. Equation: Chapter E
(P_r/P_c). For information, αP_r/P_e = 1.6 × 228.4/10,780 = 0.03391 (not
gated, [plan D1]).

**Downward, distributed** (axial only):
P_r = D + w·s = 28.45 + 350.0 = 378.4 lb compression.
M_r = 0. Ratio = 378.4/5671 = **0.06673**. Equation: Chapter E.
For information, αP_r/P_e = 1.6 × 378.4/10,780 = 0.05617, above 0.05;
by [plan D1] the downward case is not gated, so this does not stop the
calc. This is the D1 scope test the plan names. See flag F-1: this is not
clean if notional loads apply.

**Outward, concentrated:**
P_r = D = 28.45 lb compression.
M_r = P·L_p = 200.0 × 41.50 = 8300 lb-in.
αP_r/P_e = 1.6 × 28.45/10,780 = 0.004222 ≤ 0.05: amplification taken as 1.0 [plan D1].
P_r/P_c = 0.005016 < 0.2: Eq. H1-1b.
Ratio = 28.45/(2 × 5671) + 8300/8823 = 0.002508 + 0.9407 = **0.9432**.

**Outward, distributed:**
P_r = 28.45 lb compression.
M_r = w·s·L_p = 350.0 × 41.50 = 14,525 lb-in.
αP_r/P_e = 0.004222 ≤ 0.05.
P_r/P_c = 0.005016 < 0.2: Eq. H1-1b.
Ratio = 0.002508 + 14,525/8823 = 0.002508 + 1.646 = **1.649 > 1.0, NG**.

**Inward, concentrated:** identical to outward with the moment reversed:
P_r = 28.45 lb, M_r = 8300 lb-in, αP_r/P_e = 0.004222, Eq. H1-1b, ratio **0.9432**.

**Inward, distributed:** P_r = 28.45 lb, M_r = 14,525 lb-in,
αP_r/P_e = 0.004222, Eq. H1-1b, ratio **1.649, NG**.

**Longitudinal, concentrated:** the load is applied at the post top
parallel to the rail [brief]; the moment is about the other axis, but the
section is round, so: P_r = 28.45 lb, M_r = 8300 lb-in,
αP_r/P_e = 0.004222, Eq. H1-1b, ratio **0.9432**.

**Longitudinal, distributed:** P_r = 28.45 lb, M_r = 350.0 × 41.50 =
14,525 lb-in, αP_r/P_e = 0.004222, Eq. H1-1b, ratio **1.649, NG**.

**Upward, concentrated** (axial only, tension, [plan D8]):
T_r = 1.0P − 0.6D = 200.0 − 0.6 × 28.45 = 200.0 − 17.07 = 182.9 lb tension
[V: ej.combo.bending.upward]. Ratio = T_r/P_t = 182.9/15,698 = **0.01165**.
Equation: Chapter D (P_r/P_t, §D2).

**Upward, distributed:** T_r = 350.0 − 17.07 = 332.9 lb tension.
Ratio = 332.9/15,698 = **0.02121**. Equation: Chapter D.

## 6. Check 6: post deflection

Cantilever fixed at the top of the baseplate (rigid baseplate [brief]
output.md), load at the free end, L = L_p = 41.50 in, live load only
[V: ej.combo.deflection.L_only].

| Symbol | Equation | Substituted | Result | Cite |
| --- | --- | --- | --- | --- |
| Δ form | V·L_p³/(3EI) | — | — | AISC Manual Table 3-23, cantilever with concentrated load at free end [own] O-11 |
| L_p³ | | 41.50³ | 71,473 in³ | |
| 3EI | | 3 × 29,000,000 psi × 0.2930 | 25,491,000 lb-in² | |
| Δ_allow | L_p/60 | 41.50/60 | 0.6917 in | [brief] checks.md Check 6; [input] limit_L_over = 60 |

| Case | V (lb) | Δ = V·L_p³/(3EI) | Δ (in) | Ratio Δ/Δ_allow |
| --- | --- | --- | --- | --- |
| Outward, concentrated | 200.0 | 200.0 × 71,473/25,491,000 | 0.5608 | 0.8108 |
| Outward, distributed | 350.0 | 350.0 × 71,473/25,491,000 | 0.9814 | **1.419, NG** |
| Inward, concentrated | 200.0 | same as outward | 0.5608 | 0.8108 |
| Inward, distributed | 350.0 | same as outward | 0.9814 | **1.419, NG** |
| Longitudinal, concentrated | 200.0 | same (round section) | 0.5608 | 0.8108 |
| Longitudinal, distributed | 350.0 | same | 0.9814 | **1.419, NG** |
| Downward, upward | — | vertical load, no lateral deflection | — | listed, not checked |

## 7. Information only (not checks in the plan's scope)

| Item | Equation | Result | Cite |
| --- | --- | --- | --- |
| Tensile rupture capacity | F_u·A_e/Ω_t, A_e = U·A_n, U = 1.0, A_n = A_g | 60 × 0.7490/2.00 = 22.47 kip | §D2(b), Table D3.1 Case 1 [own] O-15 |
| Rupture ratio, upward distributed | 332.9/22,470 | 0.01482 (yield governs, 0.02121) | |
| Shear capacity, round HSS | V_c = F_cr·A_g/2/Ω_v, F_cr = 0.6F_y (short, stocky) | 0.6 × 35 × 0.7490/2/1.67 = 4.709 kip | §G5 [own] O-16 |
| Shear ratio, distributed | 350.0/4709 | 0.07432 | excluded by the brief |
| Notional load, downward distributed (if applied) | N = 0.002αY = 0.002 × 1.6 × 378.4 | 1.211 lb; M = 50.26 lb-in | §C2.2b, App. 7.2 [own] O-12; flag F-1 |
| H1-1b with that notional moment | 378.4/(2 × 5671) + 50.26/8823 | 0.03906 (< P_r/P_c = 0.06673) | flag F-1 |
| App. 8 story P_e for comparison | R_M·3EI/L_p², R_M = 0.85 | 12.58 kip; αP_r/P_e,story = 0.003618 (moment cases), 0.04813 (downward distributed) | App. 8 Eq. for P_e,story [own] O-10; flag F-5 |
| Continuous-rail reaction, 2 equal spans | 1.25·w·s | 437.5 lb; Check 5 ratio 2.060, Check 6 ratio 1.774 | flag F-2 |

## 8. Summary

| Check | Controlling case | Demand | Capacity / limit | Ratio | Result |
| --- | --- | --- | --- | --- | --- |
| 5, post axial + flexure | Outward distributed (ties exactly with inward and longitudinal distributed) | P_r = 28.45 lb, M_r = 14,525 lb-in | P_c = 5671 lb, M_c = 8823 lb-in, Eq. H1-1b | 1.649 | NG |
| 6, post deflection | Outward distributed (ties with inward and longitudinal distributed) | Δ = 0.9814 in | Δ_allow = 0.6917 in | 1.419 | NG |

Check 5 envelope: downward 0.04028 / 0.06673; outward, inward and
longitudinal 0.9432 / 1.649; upward 0.01165 / 0.02121 (concentrated /
distributed). Check 6 envelope: 0.8108 / 1.419 in each horizontal case.

The distributed load governs both checks because w·s = 350 lb exceeds
P = 200 lb at a 7'-0" span; the concentrated cases pass (0.94, 0.81). A
Pipe1-1/2STD post at 7'-0" spacing failing the 50 plf case is in line
with practice. The Chapter E term in the governing H1-1b ratio is
0.002508 of 1.649 (0.15%); P_r/P_c itself is 0.30% of it.

## 9. Values from my own reading (no verified entry)

All from memory; no web source was opened in this session. Each should be
confirmed against the 360-22 text; equation numbers are my memory of
360-16, assumed unchanged.

| Id | Value or provision | Document, section |
| --- | --- | --- |
| O-1 | Ω_c = 1.67 | AISC 360-22 §E1 |
| O-2 | Compression members: nonslender sections use §E3 (and §E4 where applicable); slender use §E7 | AISC 360-22 §E1, Table User Note E1.1 |
| O-3 | Round HSS in axial compression, λ_r = 0.11E/F_y on D/t | AISC 360-22 Table B4.1a (round HSS row; I believe Case 9, not sure) |
| O-4 | P_n = F_cr·A_g (E3-1); F_cr = 0.658^(F_y/F_e)·F_y (E3-2); F_cr = 0.877F_e (E3-3); F_e = π²E/(L_c/r)² (E3-4) | AISC 360-22 §E3 |
| O-5 | Branch: E3-2 when L_c/r ≤ 4.71√(E/F_y) (equivalently F_y/F_e ≤ 2.25), else E3-3 | AISC 360-22 §E3(a), (b) |
| O-6 | K = 2.1 recommended design value, fixed base, free top (theoretical 2.0) | AISC 360-22 Commentary Appendix 7, Table C-A-7.1, case (e) |
| O-7 | L_c/r preferably not over 200 | AISC 360-22 §E2 User Note |
| O-8 | P_n = F_y·A_g (D2-1), Ω_t = 1.67, tensile yielding on the gross section | AISC 360-22 §D2(a) |
| O-9 | H1-1a: P_r/P_c + 8/9(M_rx/M_cx + M_ry/M_cy) ≤ 1.0 for P_r/P_c ≥ 0.2; H1-1b: P_r/(2P_c) + (M_rx/M_cx + M_ry/M_cy) ≤ 1.0 for P_r/P_c < 0.2 | AISC 360-22 §H1.1 |
| O-10 | α = 1.6 (ASD); P_e1 = π²EI*/(L_c1)² (here with EI and L_c = 2.1h per plan D1); P_e,story = R_M·HL/Δ_H, R_M = 1 − 0.15(P_mf/P_story) | AISC 360-22 Appendix 8, §8.2.1 and §8.2.2 |
| O-11 | Cantilever, concentrated load at free end: M_max = P·l at the fixed end; Δ_max = P·l³/(3EI) at the free end | AISC Manual 16th Ed. Table 3-23 (I believe Case 22; not sure) |
| O-12 | Notional loads N_i = 0.002αY_i; under the effective length method they need be applied only in gravity-only combinations | AISC 360-22 §C2.2b and Appendix 7, §7.2 |
| O-13 | Torsional buckling (§E4) does not govern closed round sections | AISC 360-22 §E4 scope, from memory |
| O-14 | M_p = F_y·Z as the explicit form of the verified F8-1 text | AISC 360-22 Eq. F8-1 |
| O-15 | F_u = 60 ksi for A53 Gr B; Ω_t = 2.00 for rupture; U = 1.0 when the load is transmitted to all elements by welds | AISC Manual Table 2-4; AISC 360-22 §D2(b), Table D3.1 Case 1 |
| O-16 | Round HSS shear: V_n = F_cr·A_g/2, F_cr ≤ 0.6F_y; Ω_v = 1.67 | AISC 360-22 §G5 |

## 10. Open questions and flags for Micah

**F-1. Notional loads in the downward (gravity-only) case.** The plan uses
K = 2.1, which is the effective length method (AISC 360-22 App. 7.2). As I
read it, that method still requires notional loads N = 0.002αY_i in
gravity-only combinations (§C2.2b via App. 7.2), and the downward case is
gravity only. The plan doesn't mention it. Two consequences: (a) the
moment is tiny here (50.26 lb-in), and H1-1b with it gives 0.03906, *less*
than the reported P_r/P_c of 0.06673, so D8's P_r/P_c is the conservative
value either way; (b) the downward case would then have a moment, so D1's
reason for leaving it out of the αP_r/P_e gate ("no moment to amplify")
no longer holds, and the downward distributed case at 0.05617 would stop
the calc. I followed the plan (no notional load, no gate on downward).
This is a decision, not an arithmetic point.

**F-2. Post reaction from a rail continuous over the post.** The brief's
locked assumptions say the rail runs continuously over the post and the
tributary length is the span. A two-span continuous rail puts 1.25·w·s
into the interior post (437.5 lb here, Check 5 ratio 2.060, Check 6 1.774);
a long continuous run gives about 1.10–1.14·w·s. I used w·s as the brief
directs. Simple-span tributary for the post is unconservative by up to 25%
when the rail is genuinely continuous. Both checks fail here regardless, but
on a passing post this could be the difference. The concentrated load is
unaffected (P directly over the post is the worst reaction either way).

**F-3. Inclined guard loads.** "Any direction" includes inclined loads.
I showed in §3.3 that the worst inclination (1.07° above horizontal) raises
the H1-1b ratio by only 0.018%, so the five orthogonal cases are a sound
envelope for this section. That's worth an assumption line rather than a
check, if you want it stated.

**F-4. Tensile rupture (§D2(b)) is not in the plan.** It doesn't govern for
an all-around welded pipe (U = 1.0, F_u/2.00 > F_y/1.67 for A53 Gr B), §7.
It would only matter for a connection with shear lag (U < 1), such as a
slotted pipe on a gusset, which v1 doesn't have.

**F-5. P_e at L_c = 2.1h vs App. 8's story P_e.** For information: the
App. 8 story form with R_M = 0.85 and the cantilever's lateral stiffness
3EI/L_p² gives 12.58 kip, against the plan's 10.78 kip. The plan's
value is the more conservative one (17% lower P_e), and under the story
form the downward distributed case would be 0.04813, below 0.05.
No action is needed unless you want the D1 entry's note to record the
comparison.

**F-6. Sign and text formats in the values file.** I recorded the upward
P_r values as positive magnitudes (182.9 and 332.9 lb) with tension stated
in the comment; the key doesn't say what sign convention it uses. The text keys
(Fcr_equation, check5.equation.*, controlling) have no format I could
see; I used "E3-3", "H1-1b", "Chapter E" (downward), "Chapter D"
(upward), and the key-suffix form "outward_distributed". A mismatch on
these may be format, not engineering.

**F-7. Controlling-case tie.** Outward, inward and longitudinal distributed
give identical ratios in both checks. I named outward_distributed as
controlling; the tie-break rule isn't stated anywhere I read.

**F-8. Brief wording (minor).** docs/brief/verification.md says the
Chapter E term is "about 0.3%" of the controlling H1-1b ratio in this case.
The H1-1b axial term P_r/(2P_c) is 0.15% of it; P_r/P_c is 0.30%. The point
the brief makes stands either way.

**Mapping gaps (step 7).** Every key in the template has a value. Values I
computed with no key: the classification ratios and limits (λ_r = 91.14
compression, λ_p = 58.00 flexure); the 4.71√(E/F_y) branch limit (135.6);
P_e (10,780 lb); αP_r/P_e for the downward cases (information only, per
D1); the upward net-tension test (0.6D = 17.07 lb); Δ for downward and upward
(not applicable); the §7 information-only items. The tool may not print
all of these, but P_e, the branch limit and the classification limits are
hidden values whose error would show only through the ratios.

## 11. Review checklist (docs/brief/verification.md)

1. **Loads complete.** Rail dead load (W·s), post dead load (W·(h − t_p)),
   both guard load types (P and w·s), each applied in all five directions.
   No intermediate rail, so no component load and no intermediate-rail
   dead load. Baseplate weight correctly excluded (below the critical
   section). Notional loads not included (F-1).
2. **Direction and worst case.** P and w·s act at the post top on the rail
   centerline, the worst position for the post. All five directions × two
   load types are computed; inclined directions shown not to govern (F-3).
   Upward uses 0.6D against L. Worst case found by calculation:
   distributed horizontal, 1.649 and 1.419.
3. **Checks complete.** §2 lists every Chapter B, D, E, F, G, H limit state
   and the second-order gate. Rupture (F-4) and shear (excluded by the brief)
   are computed for information. Notional loads (F-1) are the one
   requirement I believe applies and the plan leaves out.
4. **Geometry.** Moment arm and deflection length L_p = h − t_p = 41.50 in
   (plan D4, brief Check 6). L_c = 2.1h with h = 42.00 in, not h − t_p
   (plan D3). D_post over h − t_p (plan D2). Span 84.00 in = 7.000 ft for
   tributary.
5. **Method and equations.** Compression nonslender (14.10 ≤ 91.14),
   flexure compact (14.10 ≤ 58.00), §F8 applies (14.10 < 372.9).
   E3 branch by both tests (140.9 > 135.6; 2.427 > 2.25) gives E3-3. H1-1b by
   P_r/P_c = 0.005016 < 0.2. Axial-only cases use Chapter E / Chapter D
   (plan D8). αP_r/P_e = 0.004222 ≤ 0.05 in every moment case.
6. **Assumptions.** Fixed at top of baseplate, rigid baseplate; K = 2.1;
   L_c uses h; no LTB for round; no amplification (gate passed); rail
   weight concentric. Continuity (F-2) and notional loads (F-1) are the
   two I'd question.
7. **Code editions.** AISC 360-22, AISC Manual 16th Ed., ASCE 7-22
   throughout. Equation numbers from memory of 360-16 and flagged so.
   Table B4.1a and Table 3-23 case numbers stated as uncertain.
8. **Magnitude sense.** D = 28 lb for 7 ft of 2.72 plf rail plus 3.5 ft of
   post: right. P_c = 5.7 kip for a 1-1/2" pipe at KL/r = 141: right order.
   M_c = 8.8 kip-in vs 14.5 kip-in demand: a 1-1/2" pipe post at 7 ft
   failing the 50 plf case is expected. Δ ≈ 1 in at 350 lb on a 41.5 in
   cantilever with I = 0.293 in⁴: consistent with the stiffness. Units
   checked line by line (lb, in, psi for 3EI).
9. **Governing case.** Horizontal distributed load at the top producing
   moment at the base, as expected for a post (the governing case named in
   verification.md). Downward and upward are far from governing (0.067,
   0.021).
