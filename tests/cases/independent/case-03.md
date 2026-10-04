# Independent calc: test case 3 (Pipe2STD post)

| | |
| --- | --- |
| Case | `tests/cases/case-03.toml`, "Test case 3": Pipe2STD post, h = 42 in, t_p = 1/2 in, on case 1's rail and span |
| Covers | post, Check 5 (post combined axial and flexure), Check 6 (post cantilever deflection) |
| Date | 2026-10-04 |
| Model | claude-opus-5-5 |
| Branch / commit | `slice-2` at `65aafa2e2206132edfe9c8f4e9c092591c9e4b08` |
| Written by | the independent-calc skill, in a fresh session |

**Sources read, and nothing else:**

- Case inputs, with the `[hand]` and `[independent]` tables stripped (the skill's command).
- docs/BRIEF.md and every file in docs/brief/ (checks, inputs, loads-and-envelope, output, scope, verification, welds).
- CONTEXT.md.
- docs/plans/slice-2.md (the current plan; its decisions D1–D11 only, none of its computed values). The first lines of docs/plans/slice-1.md, only to confirm it is marked completed.
- Registry entries with status "verified" (the skill's command).
- AISC Shapes Database v16.0 workbook rows for Pipe1-1/2STD and Pipe2STD (the skill's command).
- My own reading of AISC 360-22, the AISC Manual (16th ed.) and ASCE 7-22, from memory, for every value with no verified entry. Each is marked "own reading".
- The values template tests/cases/independent/case-03.toml (its key names and header; every value was "pending").

Not read: src/, any other file in tests/ (including case-02's independent calc), the shapes TOML in data/, drafted registry entries, git history or diffs, and any tool output.

Units: lb, in, ksi, lb-in, as the brief fixes them. Full precision is carried; values are shown to 4 significant figures, ratios to 4 decimals here so the comparison has room.

---

## 1. Inputs

| Symbol | Value | Source |
| --- | --- | --- |
| s, span | 7'-0" = 84 in = 7.000 ft | case `geometry.span` |
| h, post height (top of concrete to top rail centerline) | 42 in | case `geometry.post_height` |
| t_p, baseplate thickness | 1/2 in = 0.5 in | case `geometry.baseplate_thickness` |
| h − t_p, cantilever length (top of baseplate to rail centerline) | 41.5 in | derived |
| Top rail | Pipe1-1/2STD, A53 Gr B | case `top_rail` |
| Post | Pipe2STD, A53 Gr B | case `post` |
| Post deflection limit | L/60, not bypassed | case `deflection.post` |
| Rail deflection limit | L/120, not bypassed (not used here; case 1 covers Check 2) | case `deflection.rail` |
| P, concentrated guard load | 200 lb | `asce7.guard.concentrated` (verified), ASCE 7-22 §4.5.1 |
| w, distributed guard load | 50 lb/ft | `asce7.guard.uniform` (verified), ASCE 7-22 §4.5.1.1 |
| Distributed-load exemption | not claimed | see open question Q1 |
| Intermediate rail | none | case has no intermediate rail |
| Fy (A53 Gr B) | 35 ksi | `material.A53_GrB.Fy` (verified), AISC Manual 16th ed. Table 2-4 |
| E | 29,000 ksi | `material.steel.E` (verified), AISC 360-22 Symbols |

The case file has no `[loads]` table. I take the guard loads at their code defaults and the exemption as not claimed (Q1).

## 2. Limit states considered (step 3)

Listed from the code for each member and connection in this case, not from the plan's check list.

### Post (Pipe2STD), the subject of this case

| Limit state | Provision | Applies? | Why |
| --- | --- | --- | --- |
| Local buckling classification, compression | AISC 360-22 §B4.1a, Table B4.1a (round HSS) | Yes | Needed before Chapter E. Nonslender here (§6.1). |
| Local buckling classification, flexure | §B4.1b, Table B4.1b (round HSS) | Yes | Needed before §F8. Compact here (§6.1). |
| Flexural buckling | §E3 | Yes | Axial compression in downward and horizontal cases. |
| Torsional and flexural-torsional buckling | §E4 | No | Own reading: §E4 is for singly symmetric and unsymmetric members and certain doubly symmetric open or built-up shapes; a closed round section's torsional stiffness keeps torsional buckling from governing, and §E4 is not applied to round HSS in practice. I am not sure of the exact scope wording in 360-22. |
| Slender-element compression | §E7 | No | Section is nonslender in compression; and slender is a hard stop in v1 anyway (brief, checks.md). |
| Tensile yielding, gross section | §D2(a), Eq. D2-1 | Yes | Upward case puts net tension in the post. |
| Tensile rupture, net section | §D2(b), Eq. D2-2 | No (plan) | Excluded from v1 by Micah's ruling in the plan. I re-derived why it cannot govern: a round post welded all around to the baseplate transmits the load to the whole cross-section, so U = 1.0 (own reading: Table D3.1, Case 1), Ae = Ag, and Fu/Ω_t = 60/2.00 = 30 ksi exceeds Fy/Ω_t = 35/1.67 = 20.96 ksi. Fu = 60 ksi and Ω_t = 2.00 (rupture) are own reading. |
| Flexural yielding | §F8.1, Eq. F8-1 | Yes | Horizontal cases put moment at the base. |
| Flexural local buckling | §F8.2 | No | Compact section (`aisc360.F8.nominal_strength`, verified). |
| Lateral-torsional buckling | — | No | Round HSS has no LTB limit state (`aisc360.F8.no_ltb`, verified); plan D5. |
| Combined compression and flexure | §H1.1, Eq. H1-1a/H1-1b | Yes | Horizontal cases: dead-load compression with moment. |
| Combined tension and flexure | §H1.2 | No | The upward case has no moment, and no case has tension with moment. |
| Single-axis flexure and compression, alternate | §H1.3 | No | An optional alternative to §H1.1, not a requirement. |
| Combined forces with torsion, HSS | §H3 | No | No torsion: every load reaches the post on its axis through the rail, which runs continuously over and is welded to the top of the post (locked assumption). |
| Shear | §G5 (round HSS) | No (locked assumption) | "No shear checks in any member" is locked in the output assumptions. For magnitude only: Vn/Ω_v ≈ (0.6Fy·Ag/2)/1.67 = 6.413 kip against V = 350 lb, about 0.055. Own reading of §G5, simplified with Fcr = 0.6Fy. |
| Second-order effects | App. 8 | Ratio and stop, not amplifier (plan D1) | Computed as αPr/Pe for the moment cases (§6.6). |
| Lc/r recommendation | §E2 User Note, 200 | Yes (flag only, plan D6) | Lc/r = 111.5, below 200. |
| Lateral deflection (serviceability) | engineering judgement, L/60 | Yes, Check 6 | Brief, checks.md item 6. |
| Concentrated force on the HSS wall at the rail bearing | Chapter K / Check 3 | Not this case | Rail-to-post weld (Check 3) is out of slice 2. |
| Post-to-baseplate weld and base metal at the weld | §J2.4, §J4.2 / Check 7 | Not this case | Check 7 is out of slice 2. |
| Fatigue | App. 3 | No | Guard loads are not a cyclic design load. |

### Connections and baseplate

| Limit state | Applies? | Why |
| --- | --- | --- |
| Baseplate flexure (plate bending between post and anchors) | **Not in any v1 check. Flagged for Micah, F-2.** | The locked assumption makes the baseplate rigid for analysis, and the seven checks never test its strength. A thin plate could govern the system before the post does. This may be deliberate scope ("the tool stops at the baseplate"); I did not find it stated. |
| Anchors, concrete | No | Out of v1 scope (brief, scope.md); reactions go to anchor software. |

### Top rail

The rail's own checks (Checks 1 and 2) are covered by case 1 and not recorded here. The rail enters this case only as a load source: its dead load and the guard loads it delivers to the post.

## 3. Loads and load path (step 4)

### 3.1 Dead loads

| Line | Equation | Substitution | Result | Citation | Source |
| --- | --- | --- | --- | --- | --- |
| D_rail | W_rail · s | 2.72 lb/ft × 7.000 ft | 19.04 lb | AISC Shapes Database v16.0, W; tributary length = span (brief inputs.md; plan D11) | database; engineer decision |
| D_post | W_post · (h − t_p) | 3.66 lb/ft × 41.5 in / 12 | 12.66 lb (12.6575) | plan D2 | engineer decision |
| P_D | D_rail + D_post | 19.04 + 12.6575 | 31.70 lb (31.6975) | plan D2 | engineer decision |

Direction: downward, on the post axis. Point of application: the rail dead load at the top of the post (rail continuous over the post, welded on its axis); the post's own weight distributed over its length, all taken as axial at the critical section (plan D2). No intermediate rail. The baseplate's weight is below the critical section and does not enter Check 5 or 6.

### 3.2 Guard loads delivered to the top of the post

| Load type | Magnitude at post top | Reasoning |
| --- | --- | --- |
| Concentrated | V = P = 200 lb | ASCE 7-22 §4.5.1 lets the load act at any point on the top rail; the worst point for the post is directly over it, where the whole 200 lb goes into the post. |
| Distributed | V = w · s = 50 × 7.000 = 350 lb | ASCE 7-22 §4.5.1.1 along the rail; tributary length = span, rail continuity neglected (plan D11). |

The two load types are never concurrent (`asce7.guard.uniform`, verified). Each acts in each direction case at the rail centerline over the post, h above top of concrete.

### 3.3 Critical section and how each load reaches it

The post is fixed at the top of the baseplate (locked assumption), so the critical section is there (plan D4). The lever arm from the load to that section is h − t_p = 41.5 in. At that section:

- a vertical load at the top adds to the axial force, with no moment (it is on the post axis);
- a horizontal load V at the top produces shear V and moment V·(h − t_p), with no axial force.

### 3.4 Envelope cases

| Case | Combination | Pr at critical section | Mr | Check 5 equation | Check 6 |
| --- | --- | --- | --- | --- | --- |
| Downward | D + L, `asce7.combo.asd.D_plus_L` (verified) | P_D + V, compression | 0 | Pr/Pc (plan D8) | vertical; no lateral deflection |
| Upward | 0.6D + 1.0L, `ej.combo.bending.upward` (verified) | V − 0.6P_D, tension | 0 | Pr/Pt (plan D8) | vertical; no lateral deflection |
| Outward | D + L | P_D, compression | V·(h − t_p) | §H1.1 | L only, `ej.combo.deflection.L_only` (verified) |
| Inward | D + L | P_D, compression | V·(h − t_p) | §H1.1 | L only |
| Longitudinal | D + L | P_D, compression | V·(h − t_p) | §H1.1 | L only |

Each row is run for both load types, ten cases in all. In the horizontal cases 1.0D is the worst dead load: compression only adds to the H1-1 ratio, so a reduced dead-load factor could not govern. Outward, inward and longitudinal are identical for a round post; they are worked separately below only so that each is shown.

**Inclined loads.** ASCE 7-22 says "any direction". I checked whether a load inclined between horizontal and downward beats the pure horizontal case in Check 5. With the load at angle θ below horizontal, H1-1b becomes (P_D + V sin θ)/(2Pc) + V cos θ·(h − t_p)/Mc. Its maximum is at tan θ = Mc / [2Pc·(h − t_p)] = 14,943 / (2 × 11,313 × 41.5) → θ = 0.9117°. There the distributed-load ratio is 0.97354 against 0.97342 horizontal, an increase of 0.013%. The five direction cases therefore cover "any direction" here to well within the 0.5% test tolerance, as the plan's ruling for round sections says. For Check 6 the horizontal load is already the worst (deflection goes as cos θ).

## 4. Section properties

### Post, Pipe2STD (AISC Shapes Database v16.0, as published)

| Symbol | Value | Database column |
| --- | --- | --- |
| D (outside diameter) | 2.375 in | OD |
| t_des | 0.143 in | tdes |
| A_g | 1.02 in² | A |
| W | 3.66 lb/ft | W |
| I | 0.627 in⁴ | Ix |
| S | 0.528 in³ | Sx |
| Z | 0.713 in³ | Zx |
| r | 0.791 in | rx |
| D/t | 16.6 | D/t (OD/t_des = 2.375/0.143 = 16.61; the tabulated value is used) |

Pipe is designed as round HSS (`aisc360.pipe_as_round_hss`, verified), with the database properties as published (brief, checks.md).

### Top rail, Pipe1-1/2STD (load source only)

W = 2.72 lb/ft (database W). No other rail property is used in this case.

## 5. Load cases: demands (summary)

| Case | Pr (lb) | sense | Mr (lb-in) | V for Check 6 (lb) |
| --- | --- | --- | --- | --- |
| downward, concentrated | 231.7 | compression | 0 | — |
| downward, distributed | 381.7 | compression | 0 | — |
| outward, concentrated | 31.70 | compression | 8,300 | 200 |
| outward, distributed | 31.70 | compression | 14,525 | 350 |
| inward, concentrated | 31.70 | compression | 8,300 | 200 |
| inward, distributed | 31.70 | compression | 14,525 | 350 |
| upward, concentrated | 181.0 | tension | 0 | — |
| upward, distributed | 331.0 | tension | 0 | — |
| longitudinal, concentrated | 31.70 | compression | 8,300 | 200 |
| longitudinal, distributed | 31.70 | compression | 14,525 | 350 |

Each line is worked in §6 and §7.

## 6. Check 5: post combined axial and flexure

### 6.1 Classification (case-independent)

| Line | Equation | Substitution | Result | Citation | Source |
| --- | --- | --- | --- | --- | --- |
| λ (compression and flexure) | D/t | tabulated | 16.6 | Table B4.1a/b, round HSS | database |
| λ_r, compression | 0.11E/Fy | 0.11 × 29,000 / 35 | 91.14 | AISC 360-22 Table B4.1a, round HSS (Case 9 from memory) | own reading |
| Compression class | λ ≤ λ_r | 16.6 ≤ 91.14 | nonslender | §B4.1a | own reading |
| λ_p, flexure | 0.07E/Fy | 0.07 × 29,000 / 35 | 58.00 | Table B4.1b, round HSS | `aisc360.B4.1b.round_hss.lambda_p` |
| λ_r, flexure | 0.31E/Fy | 0.31 × 29,000 / 35 | 256.9 | Table B4.1b, round HSS | `aisc360.B4.1b.round_hss.lambda_r` |
| Flexure class | λ ≤ λ_p | 16.6 ≤ 58.00 | compact | §B4.1b | `aisc360.B4.1b.classification` |
| §F8 scope | D/t < 0.45E/Fy | 16.6 < 372.9 | §F8 applies | §F8 | `aisc360.F8.applicability` |

### 6.2 Compression capacity (case-independent)

| Line | Equation | Substitution | Result | Citation | Source |
| --- | --- | --- | --- | --- | --- |
| K | recommended design value, fixed-free | — | 2.1 | AISC 360-22 Commentary App. 7, Table C-A-7.1, case (e) | own reading; plan D3 |
| L_c | K·h | 2.1 × 42 | 88.20 in | §E2; plan D3 (h, not h − t_p) | own reading; plan D3 |
| L_c/r | L_c/r | 88.20 / 0.791 | 111.5 | §E2 | — |
| L_c/r recommendation | ≤ 200 | 111.5 ≤ 200 | no flag | §E2 User Note | own reading; plan D6 |
| Branch limit | 4.71√(E/Fy) | 4.71 × √(29,000/35) = 4.71 × 28.78 | 135.6 | §E3(a) | own reading |
| Branch | L_c/r ≤ 4.71√(E/Fy) | 111.5 ≤ 135.6 (equivalently Fy/Fe = 1.520 ≤ 2.25) | Eq. E3-2 | §E3(a) | own reading |
| F_e | π²E/(L_c/r)² | 9.870 × 29,000 / 111.5² = 286,219 / 12,433 | 23.02 ksi | Eq. E3-4 | own reading |
| Fy/F_e | | 35 / 23.02 | 1.520 | | |
| F_cr | 0.658^(Fy/Fe) · Fy | 0.658^1.520 × 35 = 0.5292 × 35 | 18.52 ksi | Eq. E3-2 | own reading |
| P_n | F_cr · A_g | 18.52 × 1.02 | 18.89 kip = 18,890 lb (18,893) | Eq. E3-1 | own reading |
| Ω_c | | | 1.67 | §E1 | own reading |
| P_c | P_n/Ω_c | 18,893 / 1.67 | 11,310 lb (11,313) | §E1; Eq. B3-2 | own reading; `aisc360.eq.B3-2` |

### 6.3 Tension capacity (case-independent)

| Line | Equation | Substitution | Result | Citation | Source |
| --- | --- | --- | --- | --- | --- |
| P_n | Fy · A_g | 35 × 1.02 | 35.70 kip = 35,700 lb | Eq. D2-1 | own reading |
| Ω_t | | | 1.67 | §D2(a) | own reading |
| P_t | P_n/Ω_t | 35,700 / 1.67 | 21,380 lb (21,377) | §D2; Eq. B3-2 | own reading; `aisc360.eq.B3-2` |

### 6.4 Flexural capacity (case-independent)

| Line | Equation | Substitution | Result | Citation | Source |
| --- | --- | --- | --- | --- | --- |
| M_n | M_p = Fy · Z | 35 × 0.713 | 24.96 kip-in = 24,955 lb-in | Eq. F8-1 | `aisc360.eq.F8-1` |
| Local buckling | not applicable, compact | | — | §F8.2(a) | `aisc360.F8.nominal_strength` |
| LTB | not a limit state | | — | §F8 | `aisc360.F8.no_ltb` |
| Ω_b | | | 1.67 | §F1(a) | `aisc360.F1.omega_b` |
| M_c | M_n/Ω_b | 24,955 / 1.67 | 14,940 lb-in (14,943) | §F1; Eq. B3-2 | `aisc360.F1.omega_b`; `aisc360.eq.B3-2` |

Biaxial: in every case the moment is about a single axis, so the SRSS resultant (`ej.bending.srss_round`) equals that moment.

### 6.5 Second-order quantity (case-independent part)

| Line | Equation | Substitution | Result | Citation | Source |
| --- | --- | --- | --- | --- | --- |
| P_e | π²EI/L_c² | 9.870 × 29,000 × 0.627 / 88.20² = 179,460 / 7,779 | 23.07 kip = 23,070 lb (23,069) | AISC 360-22 App. 8, Eq. A-8-5 form, with L_c = 2.1h and EI (plan D1) | own reading; plan D1 |
| α | ASD | | 1.6 | App. 8 §8.2.1 (from memory) | own reading |
| Limit | αPr/Pe ≤ 0.05 | | 0.05 | plan D1 (engineer) | plan D1 |

For comparison only (plan D1 already rules K·h): the App. 8 story form P_e,story = R_M · H·L/Δ_H = 0.85 × 3EI/(h − t_p)² = 26,920 lb, so the K·h value is the lower, conservative one.

### 6.6 Envelope cases

**Downward, concentrated** (D + L, axial only; Chapter E ratio, plan D8)

- Pr = P_D + P = 31.6975 + 200 = 231.7 lb, compression
- Mr = 0
- Ratio = Pr/Pc = 231.6975 / 11,313.18 = **0.02048**
- αPr/Pe (not gated, plan D1; for information) = 1.6 × 231.6975 / 23,068.97 = 0.01607

**Downward, distributed** (D + L, axial only; Chapter E ratio)

- Pr = P_D + w·s = 31.6975 + 350 = 381.7 lb, compression
- Mr = 0
- Ratio = Pr/Pc = 381.6975 / 11,313.18 = **0.03374**
- αPr/Pe (not gated; information) = 1.6 × 381.6975 / 23,068.97 = 0.02647, also below 0.05.
- Notional loads neglected (plan D10). Their moment here would be about 0.002 × 1.6 × 381.7 × 41.5 = 50.7 lb-in; H1-1b with it is 0.01687 + 50.7/14,943 = 0.0203, below the reported 0.03374, so the axial-only ratio bounds it as the locked assumption says.

**Outward, concentrated** (D + L; §H1.1)

- Pr = P_D = 31.70 lb, compression
- Mr = P·(h − t_p) = 200 × 41.5 = 8,300 lb-in
- Pr/Pc = 31.6975 / 11,313.18 = 0.002802 < 0.2 → Eq. H1-1b
- Ratio = Pr/(2Pc) + Mr/Mc = 0.001401 + 8,300 / 14,943.11 = 0.001401 + 0.5554 = **0.5568**
- αPr/Pe = 1.6 × 31.6975 / 23,068.97 = **0.002198** ≤ 0.05, OK; amplification taken as 1.0

**Outward, distributed** (D + L; §H1.1)

- Pr = P_D = 31.70 lb, compression
- Mr = w·s·(h − t_p) = 350 × 41.5 = 14,525 lb-in
- Pr/Pc = 0.002802 < 0.2 → Eq. H1-1b
- Ratio = 0.001401 + 14,525 / 14,943.11 = 0.001401 + 0.9720 = **0.9734** (0.97342)
- αPr/Pe = **0.002198** ≤ 0.05, OK

**Inward, concentrated**: identical to outward, concentrated (round section; load reversed). Pr = 31.70 lb, Mr = 8,300 lb-in, Eq. H1-1b, ratio **0.5568**, αPr/Pe **0.002198**.

**Inward, distributed**: identical to outward, distributed. Pr = 31.70 lb, Mr = 14,525 lb-in, Eq. H1-1b, ratio **0.9734**, αPr/Pe **0.002198**.

**Longitudinal, concentrated**: the load acts along the rail at the post top; the round post resists it about the other axis with the same capacity. Pr = 31.70 lb, Mr = 8,300 lb-in, Eq. H1-1b, ratio **0.5568**, αPr/Pe **0.002198**.

**Longitudinal, distributed**: w·s at the post top (engineering judgement, brief loads-and-envelope.md). Pr = 31.70 lb, Mr = 14,525 lb-in, Eq. H1-1b, ratio **0.9734**, αPr/Pe **0.002198**.

**Upward, concentrated** (0.6D + 1.0L, engineering judgement; axial only, Chapter D ratio)

- Net-tension test: 0.6P_D = 0.6 × 31.6975 = 19.02 lb < L = 200 lb → net tension, checked
- Pr = P − 0.6P_D = 200 − 19.0185 = 181.0 lb, tension
- Ratio = Pr/Pt = 180.9815 / 21,377.25 = **0.008466**

**Upward, distributed** (0.6D + 1.0L; Chapter D ratio)

- 0.6P_D = 19.02 lb < 350 lb → net tension
- Pr = 350 − 19.0185 = 331.0 lb, tension
- Ratio = Pr/Pt = 330.9815 / 21,377.25 = **0.01548**

### 6.7 Check 5 envelope

| Case | Pr (lb) | Mr (lb-in) | Equation | αPr/Pe | Ratio |
| --- | --- | --- | --- | --- | --- |
| downward, concentrated | 231.7 C | 0 | Pr/Pc | — | 0.0205 |
| downward, distributed | 381.7 C | 0 | Pr/Pc | — | 0.0337 |
| outward, concentrated | 31.70 C | 8,300 | H1-1b | 0.002198 | 0.5568 |
| **outward, distributed** | 31.70 C | 14,525 | H1-1b | 0.002198 | **0.9734** |
| inward, concentrated | 31.70 C | 8,300 | H1-1b | 0.002198 | 0.5568 |
| inward, distributed | 31.70 C | 14,525 | H1-1b | 0.002198 | 0.9734 |
| upward, concentrated | 181.0 T | 0 | Pr/Pt | — | 0.0085 |
| upward, distributed | 331.0 T | 0 | Pr/Pt | — | 0.0155 |
| longitudinal, concentrated | 31.70 C | 8,300 | H1-1b | 0.002198 | 0.5568 |
| longitudinal, distributed | 31.70 C | 14,525 | H1-1b | 0.002198 | 0.9734 |

Controlling: horizontal distributed load, ratio 0.9734 ≤ 1.0, **OK**. Outward, inward and longitudinal distributed tie exactly; I name "outward, distributed", the first in the values file's key order. The second-order gate passes in every moment case (0.002198 ≤ 0.05).

## 7. Check 6: post cantilever deflection

### 7.1 Case-independent

| Line | Equation | Substitution | Result | Citation | Source |
| --- | --- | --- | --- | --- | --- |
| L | h − t_p | 42 − 0.5 | 41.50 in | brief checks.md item 6 | engineer decision |
| Δ_allow | L/60 | 41.5 / 60 | 0.6917 in | engineering judgement, input default | brief inputs.md; plan (`ej.deflection.limit.post` is drafted, not read) |
| EI | | 29,000,000 psi × 0.627 in⁴ | 1.818 × 10⁷ lb-in² | | `material.steel.E` |
| Formula | Δ = V·L³/(3EI) | cantilever, concentrated load at free end | | AISC Manual 16th ed. Table 3-23, Case 22 (case number from memory; not sure) | own reading |
| L³ | | 41.5³ | 71,470 in³ (71,473.375) | | |

Combination: live load only, `ej.combo.deflection.L_only` (verified). Dead load is axial and causes no lateral deflection.

### 7.2 Envelope cases

**Outward, concentrated**: Δ = 200 × 71,473.375 / (3 × 1.8183 × 10⁷) = 14,294,675 / 54,549,000 = **0.2621 in**; ratio Δ/Δ_allow = 0.26205 / 0.69167 = **0.3789**

**Outward, distributed**: Δ = 350 × 71,473.375 / 54,549,000 = **0.4586 in**; ratio = 0.45859 / 0.69167 = **0.6630**

**Inward, concentrated / distributed**: identical to outward: 0.2621 in, 0.3789; 0.4586 in, 0.6630.

**Longitudinal, concentrated / distributed**: identical (same I about every axis): 0.2621 in, 0.3789; 0.4586 in, 0.6630.

**Downward, upward**: vertical loads, no lateral deflection; listed, not checked (plan).

### 7.3 Check 6 envelope

| Case | Δ (in) | Δ_allow (in) | Ratio |
| --- | --- | --- | --- |
| outward, concentrated | 0.2621 | 0.6917 | 0.3789 |
| **outward, distributed** | 0.4586 | 0.6917 | **0.6630** |
| inward, concentrated | 0.2621 | 0.6917 | 0.3789 |
| inward, distributed | 0.4586 | 0.6917 | 0.6630 |
| longitudinal, concentrated | 0.2621 | 0.6917 | 0.3789 |
| longitudinal, distributed | 0.4586 | 0.6917 | 0.6630 |
| downward, upward | — | — | vertical; no lateral deflection |

Controlling: horizontal distributed load, 0.4586 in ≤ 0.6917 in, ratio 0.6630, **OK**. Ties named "outward, distributed".

## 8. Summary

| Check | Controlling case | Demand | Capacity / limit | Ratio | Result |
| --- | --- | --- | --- | --- | --- |
| 5, post axial + flexure | outward, distributed (ties inward, longitudinal) | Pr = 31.70 lb C, Mr = 14,525 lb-in | Pc = 11,313 lb, Mc = 14,943 lb-in, Eq. H1-1b | 0.9734 | OK |
| 6, post deflection | outward, distributed (ties inward, longitudinal) | Δ = 0.4586 in | Δ_allow = 0.6917 in (L/60) | 0.6630 | OK |

Check 5 is governed almost entirely by flexure: the axial term is 0.0014 of the 0.9734.

## 9. Values from my own reading (no verified entry)

| Value | Used as | Document, section | Source |
| --- | --- | --- | --- |
| λ_r = 0.11E/Fy, round HSS in compression | 91.14 | AISC 360-22 Table B4.1a (Case 9, from memory) | memory |
| K = 2.1, fixed-free recommended design value | L_c | AISC 360-22 Commentary App. 7, Table C-A-7.1, case (e) | memory; also plan D3 |
| L_c/r ≤ 200 recommendation | flag test | AISC 360-22 §E2 User Note | memory; also plan D6 |
| 4.71√(E/Fy) branch limit; Eq. E3-2 and E3-3 | branch, F_cr | AISC 360-22 §E3(a), (b) | memory |
| F_e = π²E/(L_c/r)² | F_e | AISC 360-22 Eq. E3-4 | memory |
| P_n = F_cr·A_g | P_n | AISC 360-22 Eq. E3-1 | memory |
| Ω_c = 1.67 | P_c | AISC 360-22 §E1 | memory |
| P_n = Fy·A_g; Ω_t = 1.67 | P_t | AISC 360-22 Eq. D2-1, §D2(a) | memory |
| Eq. H1-1a, H1-1b, threshold Pr/Pc = 0.2 | interaction | AISC 360-22 §H1.1 | memory |
| α = 1.6 (ASD) | αPr/Pe | AISC 360-22 App. 8 §8.2.1 | memory |
| P_e = π²EI/L_c² form | P_e | AISC 360-22 App. 8 Eq. A-8-5 (with plan D1's L_c and EI) | memory |
| Cantilever free-end load: M = V·L, Δ = V·L³/(3EI) | Mr, Δ | AISC Manual 16th ed. Table 3-23, Case 22 (case number not sure) | memory |
| Δ_allow = L/60, L = h − t_p | Check 6 limit | engineering judgement, brief inputs.md and checks.md; drafted entry `ej.deflection.limit.post` not read | brief |
| Fu = 60 ksi (A53 Gr B), Ω_t = 2.00 rupture, U = 1.0 (Table D3.1 Case 1) | rupture argument only, no recorded value | AISC Manual Table 2-4; AISC 360-22 §D2(b), Table D3.1 | memory |
| §G5 round HSS shear, F_cr ≥ 0.6Fy | magnitude only | AISC 360-22 §G5 | memory |
| §E4 does not apply to round HSS | limit state list | AISC 360-22 §E4 scope | memory; not sure of the 360-22 wording |
| App. 8 story form P_e,story = R_M·H·L/Δ_H, R_M = 0.85 (for a single column, 1 − 0.15 = 0.85) | comparison only | AISC 360-22 App. 8 Eq. A-8-7 | memory |

## 10. Open questions and findings for Micah

- **Q1. Guard loads and exemption are not in the case inputs.** The stripped case file has no `[loads]` table. I used the code defaults (200 lb, 50 lb/ft, verified entries) and took the distributed-load exemption as not claimed. If case 3 means something else, every guard-load value changes.
- **F-1. Check 5 is close to 1.0.** 0.9734 for the horizontal distributed case, OK. The worst inclined direction raises it 0.013% (θ = 0.91°, §3.4); that is within tolerance, but Pipe2STD at this geometry has under 3% reserve, so a modest increase in span or h would fail it.
- **F-2. Baseplate flexure is not a v1 check.** The plate is assumed rigid, and nothing tests that a 1/2 in plate can deliver 14,525 lb-in to the anchors. This may be deliberate scope, but I did not find it stated in the brief or the assumptions. Not in the plan.
- **F-3. Tensile rupture, re-derived.** The plan's argument holds (U = 1.0, 30 ksi > 20.96 ksi); I did not record a value.
- **F-4. Downward αPr/Pe for this case is 0.0265**, below 0.05 anyway, so case 3 does not exercise the D1 scope rule (case 2 is meant to).
- **Q2. Table 3-23 case number** for the cantilever with a free-end load: I believe Case 22 but am not sure.
- **Q3. D/t:** the tabulated 16.6 is used; OD/t_des = 16.61. It changes no result.

## 11. Review checklist (docs/brief/verification.md), run on this calc

1. **Loads complete.** Rail dead load (W·s), post self-weight over h − t_p, both guard load types in every direction. No intermediate rail in this case, so no intermediate rail dead load and no component load (the component load's effect on the post is excluded by locked assumption anyway). Baseplate weight is below the critical section. Complete.
2. **Direction and worst case.** All five directions × two load types are worked (§6.6, §7.2). Concentrated load placed over the post (worst for the post). 1.0D used in the horizontal cases because compression only adds to H1-1. Inclined directions checked (§3.4). The worst case was found by calculation: horizontal distributed in both checks.
3. **Checks complete.** §2 lists every limit state from the code. Not checked and flagged: baseplate flexure (F-2). Excluded by locked assumption or plan: shear, tensile rupture (re-derived, cannot govern), Checks 3 and 7 (out of slice).
4. **Geometry.** h = 42 in for L_c (plan D3); h − t_p = 41.5 in for the moment arm, the deflection length and D_post (plan D2, D4); span 7.000 ft for the tributary length. Checked each use.
5. **Method and equations.** Classification before capacity (nonslender in compression, compact in flexure); §F8 scope met; branch E3-2 checked both as L_c/r ≤ 135.6 and Fy/Fe ≤ 2.25; Pr/Pc = 0.0028 < 0.2 → H1-1b in every moment case; axial-only cases use Chapters E and D (plan D8); net tension confirmed before the upward check.
6. **Assumptions.** Fixed at the top of the baseplate; K = 2.1 with L_c = Kh; tributary length = span, continuity neglected; notional loads neglected (bound shown in §6.6); P_e at L_c = 2.1h with gross EI (plan D1; the story-form comparison shows it is conservative).
7. **Code editions.** AISC 360-22, AISC Manual 16th edition, ASCE 7-22 throughout. Equation and case numbers from memory are marked "not sure" where I am not.
8. **Magnitude sense.** F_cr = 18.52 ksi is about half of Fy at L_c/r = 111.5, as expected; M_c = 14.94 kip-in for a 2 in pipe; Δ = 0.46 in on a 41.5 in cantilever under 350 lb. Units consistent (lb, in, ksi).
9. **Governing case.** Horizontal distributed (w·s = 350 lb > P = 200 lb at a 7 ft span) governs both checks, as expected for a guard post where axial load is small. The tie among outward, inward and longitudinal is expected for a round post.
