# Independent calc: test case 4 (welds, Checks 3 and 7)

- **Case:** tests/cases/case-04.toml, "Test case 4": case 2 with a 1/8 in
  rail to post fillet and a 1/4 in post to baseplate fillet. Covers Checks
  3 and 7 only.
- **Date:** 2026-10-08
- **Model:** claude-opus-5-5
- **Branch / commit:** slice-3 at 04f38c5a8e62af79aa19458c6cb112ed4f5e846c
- **Written by:** the independent-calc skill, in a session that had not read
  src/, tests/ (beyond the commands the skill gives), any tool output, the
  shapes TOML or any drafted registry entry. The session context did carry
  the one-line subjects of the five most recent commits (attached
  automatically at session start); no diff or file content from them was
  read.

**Sources read**

1. Case inputs: tests/cases/case-04.toml with `[hand]` and `[independent]`
   stripped, by the skill's command.
2. The brief: docs/BRIEF.md; docs/brief/scope.md, inputs.md,
   loads-and-envelope.md, checks.md, welds.md, output.md, verification.md.
3. CONTEXT.md.
4. The current slice plan, docs/plans/slice-3.md: its decisions W1–W12
   (as recorded in docs/brief/welds.md, which governs) and T2. Its "rough
   figures for case 4" were not used; every number below is derived here.
5. Verified registry entries (status "verified"), by the skill's command.
6. AISC Shapes Database v16.0 workbook, row Pipe1-1/2STD (rail and post are
   the same section), by the skill's command.
7. My own reading of AISC 360-22, the AISC Manual (16th ed.) and ASCE 7-22,
   from memory, for every value with no verified entry (listed in
   "Values from my own reading").

Units: lb, in, ksi; weld forces per inch of weld (lb/in). Values carried at
full precision; reported to 4 significant figures.

---

## 1. Inputs

| Symbol | Value | Source |
| --- | --- | --- |
| s, span | 7'-0" = 84 in = 7.0 ft | case input `geometry.span` |
| h, post height (top of concrete to rail CL) | 42 in | case input |
| t_p, baseplate thickness | 1/2 in = 0.5 in | case input |
| Top rail | Pipe1-1/2STD, A53 Gr B | case input |
| Post | Pipe1-1/2STD, A53 Gr B | case input |
| Baseplate grade | A36 | case input |
| w_3, rail to post fillet | 1/8 in = 0.125 in | case input `welds.rail_to_post` |
| w_7, post to baseplate fillet | 1/4 in = 0.25 in | case input `welds.post_to_baseplate` |
| Electrode | E70XX | case input |
| Guard loads | defaults, no exemption | case file has no `[loads]` table and no exemption; inputs.md: "defaulting to code values" |
| Intermediate rail | none | case file has none |

Derived lengths:

- h − t_p = 42 − 0.5 = **41.50 in** (Check 7 moment arm; welds.md "The post
  to baseplate weld moment arm is h minus the baseplate thickness").
- e = D_rail/2 = 1.900/2 = **0.9500 in** (Check 3 eccentricity, W1).

## 2. Limit states considered

Members and connections in scope for this case: the rail to post fillet
weld ring (Check 3), the post to baseplate fillet weld ring (Check 7), and
the parts each joins. For each I list every limit state AISC 360-22 could
apply, and why it does or does not apply here.

### Check 3, rail to post weld (post end coped to the rail's underside)

| Limit state | Provision (own reading) | Applies? |
| --- | --- | --- |
| Fillet weld metal shear on the effective throat | AISC 360-22 §J2.4, Table J2.5, Eq. J2-3/J2-4 | **Checked.** k_ds = 1.0 by W2 (branch-to-chord weld). |
| Directional strength increase | §J2.4, k_ds = 1.0 + 0.50 sin^1.5 θ | **Not used** (W2 exception). Would be 1.5 at θ = 90°; omitting it is conservative. |
| Base metal, rail side, in-plane force | §J4.2(b) shear rupture, 0.6·Fu·t | **Checked** against f_v (W5, W6). |
| Base metal, rail side, force normal to rail wall | Chapter K, round T-connection chord plastification / punching shear, β = 1.0 | **Not checked** (W7, stated assumption; connection design out of scope). See open question Q4. |
| Base metal, post side | §J4.1/§J4.2 on the post wall | **Not separately checked:** covered by Check 5 (W5); the top of the post sees the same V and far less moment than the base. Grade guard Fu/Fy = 60/35 = 1.714 ≥ 1.20, so the coverage argument holds. |
| Shear yielding of the rail wall | §J4.2(a) | Not a fusion-face limit state (W6); member shear not checked (scope.md). |
| Minimum fillet size | §J2.2b, Table J2.4 | **Checked** (W11), on t_nom of the thinner part. |
| Maximum fillet size along edges | §J2.2b(b) | **Does not apply:** T-joint, not along an edge (W11). |
| Minimum fillet length (4w) | §J2.2b(c) (own reading of the number) | Not in the decided checks. L_w = 5.969 in ≫ 4·0.125 = 0.5 in; cannot govern. Flagged for completeness. |
| Flare-bevel throat at the saddle sides (equal ODs) | §J2.1, Table J2.2 | **Not used** (W9): fillet model all around kept. |
| Torsion on the ring (load applied off the rail CL) | elastic weld group | Not in the envelope; see open question Q2. |

### Check 7, post to baseplate weld

| Limit state | Provision (own reading) | Applies? |
| --- | --- | --- |
| Fillet weld metal shear on the effective throat | §J2.4, Table J2.5 | **Checked**, with k_ds (W2). |
| Directional strength increase on round HSS | §J2.4, k_ds | **Used** per W2 (non-primary STI basis; extension to base moment is engineering judgement). θ = 90° at the governing fiber. |
| Base metal, baseplate | 0.6·Fu·t_p/Ω (W5: shear rupture over t_p, i.e. a punching-type rupture of the plate around the ring) | **Checked** against f_r. |
| Base metal, baseplate fusion face (leg on the plate surface) | §J2.4 / Table J2.5 note to §J4 (own reading, uncertain) | **Not in the decided method.** See open question Q3; I am not sure 360-22 requires it. |
| Base metal, post side | §J4.1 tension/compression in the wall | Covered by Check 5 (W5); Fu/Fy = 1.714 ≥ 1.20. |
| Baseplate bending / thickness | Manual Part 14 style | **Not checked** (D12, stated assumption). |
| Minimum fillet size | Table J2.4 | **Checked**, on t_nom of the post wall (thinner part). |
| Maximum fillet size | §J2.2b(b) | Does not apply (T-joint). |
| Minimum length | §J2.2b(c) | 5.969 in ≫ 1.0 in; cannot govern; not in the decided checks. |
| Effective weld length for welds to HSS | Chapter K (§K5, rectangular HSS) | Rectangular-HSS provisions; do not apply to a round post. No reduction taken. |
| Anchorage, concrete | — | Out of scope (scope.md). |

Nothing that could govern is missing from the plan's list, apart from the
open questions Q1–Q4 (inclined load, torsion, fusion-face leg, chord wall),
none of which can change a result in this case by my arithmetic.

## 3. Loads and load path

### Load magnitudes

| Load | Value | Citation | Source |
| --- | --- | --- | --- |
| P, concentrated guard load | 200 lb | ASCE 7-22 §4.5.1 | `asce7.guard.concentrated` (verified) |
| w, distributed guard load | 50 lb/ft | ASCE 7-22 §4.5.1.1 | `asce7.guard.uniform` (verified) |
| w·s | 50 × 7.0 = **350.0 lb** | tributary length = span (output.md assumption) | brief |
| w_D,rail = W (Pipe1-1/2STD) | 2.72 lb/ft | AISC Shapes Database v16.0, `W` | workbook |
| W_post | 2.72 lb/ft | same | workbook |

The two guard loads are separate, never concurrent (loads-and-envelope.md);
each runs through the envelope.

### Dead load at each weld

- **Check 3:** D_3 = w_D,rail · s = 2.72 × 7.0 = **19.04 lb** (welds.md,
  W10 envelope note: "D in Check 3 is the rail's dead load over the span").
  No intermediate rail in this case.
- **Check 7:** D_post = W·(h − t_p) = 2.72 × 41.5/12 = **9.407 lb**;
  D_7 = D_3 + D_post = 19.04 + 9.407 = **28.45 lb**
  (loads-and-envelope.md, "Dead load at the post"). The baseplate's weight
  is below the weld and does not load it.

### Path

The guard load acts on the top rail. For the welds the worst position of
the concentrated load is directly over the post, and the distributed load
reaches the post as w·s (tributary length = span). Either load then passes
from the rail into the post through the Check 3 ring at the rail's
underside, down the post, and through the Check 7 ring at the top of the
baseplate (the post is fixed there; no bearing credit at either ring, W10).

- **Horizontal (outward, inward, longitudinal):** V = L acts at the rail
  centerline (h above concrete). At the Check 3 ring it is shear V plus
  moment V·e, e = 0.95 in. At the Check 7 ring it is shear V plus moment
  V·(h − t_p) = V·41.5. Dead load D acts as axial compression in both
  rings. Longitudinal is carried by the rail axially into the post through
  the same ring (loads-and-envelope.md), so it equals transverse for a
  round ring.
- **Downward:** D + L axial compression through each ring, uniform.
- **Upward:** 1.0L − 0.6D axial tension through each ring, uniform.

Combinations: ASCE 7-22 §2.4.1 combination 2, D + L
(`asce7.combo.asd.D_plus_L`, verified) for downward and the horizontal
cases; 0.6D + 1.0L for upward, engineering judgement
(`ej.combo.bending.upward`, verified; its note covers the welds).

### Envelope cases (both checks, each for P and for w·s)

| Case | V (lb) | Axial P_r (lb) | M (lb-in), Check 3 | M (lb-in), Check 7 |
| --- | --- | --- | --- | --- |
| Downward, conc. | 0 | 200 + D, comp. | 0 | 0 |
| Downward, dist. | 0 | 350 + D, comp. | 0 | 0 |
| Outward / inward / longitudinal, conc. | 200 | D, comp. | 200 × 0.95 = 190.0 | 200 × 41.5 = 8,300 |
| Outward / inward / longitudinal, dist. | 350 | D, comp. | 350 × 0.95 = 332.5 | 350 × 41.5 = 14,525 |
| Upward, conc. | 0 | 200 − 0.6D, tension | 0 | 0 |
| Upward, dist. | 0 | 350 − 0.6D, tension | 0 | 0 |

With D = D_3 = 19.04 lb for Check 3 and D = D_7 = 28.45 lb for Check 7.
Net tension check for upward: 0.6·D_3 = 11.42 lb and 0.6·D_7 = 17.07 lb,
both < L = 200 lb, so both upward cases have net tension and are checked.

## 4. Section and weld properties

Pipe1-1/2STD, AISC Shapes Database v16.0 (workbook row): OD = 1.900 in,
t_nom = 0.145 in, t_des = 0.135 in, W = 2.72 lb/ft. Rail and post are the
same section; post OD ≤ rail OD (equal), so W8 does not stop.

Weld ring (W3), D = post OD = 1.900 in:

| Symbol | Equation | Substituted | Result | Citation / source |
| --- | --- | --- | --- | --- |
| L_w | πD | π × 1.900 | **5.969 in** | W3 (brief, welds.md) |
| S_w | πD²/4 | π × 1.900²/4 | **2.835 in²** | W3; elastic section modulus of a thin ring as a line, I_w/(D/2) with I_w = πD³/8 |
| f_v | V/L_w | — | per case | W3, uniform shear |
| f_a | P_r/L_w | — | per case | W3 |
| f_b | M/S_w | — | per case | W3 |
| f_n | f_a ± f_b | — | per fiber | W3, W10 |
| f_r | √(f_n² + f_v²) | — | per fiber | W3, vector sum |

Material and weld values (none has a verified entry; all own reading):

| Symbol | Value | Citation | Source |
| --- | --- | --- | --- |
| F_EXX | 70 ksi | AWS A5.1 classification E70XX; AISC 360-22 Table J2.5 | own reading (memory) |
| F_nw | 0.60·F_EXX = 0.60 × 70 = **42.00 ksi** | AISC 360-22 §J2.4, Table J2.5 (fillet weld, shear on effective area) | own reading (memory) |
| Ω (weld metal) | 2.00 | AISC 360-22 Table J2.5 | own reading (memory) |
| Effective throat | 0.707w (= w/√2 for an equal-leg fillet) | AISC 360-22 §J2.2a | own reading (memory) |
| k_ds | 1.0 + 0.50 sin^1.5 θ | AISC 360-22 §J2.4, Eq. J2-5 (equation number from memory; in 360-16 the term was inside Eq. J2-5 for F_nw) | own reading (memory) |
| Fu, A53 Gr B | 60 ksi | AISC Manual 16th ed., Table 2-4 (ASTM A53 Gr B) | own reading (memory) |
| Fy, A53 Gr B | 35 ksi | AISC Manual Table 2-4 | `material.A53_GrB.Fy` (verified) |
| Fu, A36 | 58 ksi | AISC Manual 16th ed., Table 2-5 (ASTM A36 plate, Fu = 58–80 ksi, minimum used) | own reading (memory) |
| Ω (base metal shear rupture) | 2.00 | AISC 360-22 §J4.2(b), Eq. J4-4 | own reading (memory) |
| Table J2.4 rows | t ≤ 1/4 → 1/8; 1/4 < t ≤ 1/2 → 3/16; 1/2 < t ≤ 3/4 → 1/4; t > 3/4 → 5/16 (in) | AISC 360-22 Table J2.4, thinner part joined | own reading (memory) |

Effective throats:

- Check 3: t_e = 0.707 × 0.125 = **0.08838 in**
- Check 7: t_e = 0.707 × 0.25 = **0.1768 in**

## 5. Check 3: rail to post weld

### Case-independent capacities

**Weld metal** (k_ds = 1.0, W2 exception):

R_n/Ω = F_nw · k_ds · t_e / Ω = 42.00 × 1.0 × 0.08838 / 2.00
= 1.856 kip/in = **1,856 lb/in**
(AISC 360-22 §J2.4, Table J2.5; own reading.)

**Rail base metal, in-plane** (W5, W6):

R_n/Ω = 0.6 · Fu · t_des / Ω = 0.6 × 60 × 0.135 / 2.00
= 2.430 kip/in = **2,430 lb/in**
(AISC 360-22 §J4.2(b), Eq. J4-4, Manual Part 9 convention; own reading.
t_des per W4.)

**Minimum size** (W11): parts joined are the rail wall and the post wall,
both t_nom = 0.145 in. Thinner part t = **0.145 in** ≤ 1/4 in →
w_min = **1/8 in = 0.125 in**. Provided w_3 = 0.125 in ≥ 0.125 in: **OK**
(exactly at the minimum). AISC 360-22 Table J2.4; own reading.

§J2.2b(b) maximum size along edges: does not apply (T-joint). (W11)

Post side: covered by Check 5 (W5). Rail wall chord limit states: not
checked (W7).

### Envelope

Fiber convention: compression positive. In the horizontal cases f_n is
evaluated at both extreme fibers, f_a + f_b (compression side, where dead
load compression adds) and f_a − f_b (tension side); the larger f_r
governs (W10). In downward and upward f_b = 0 and f_v = 0, so the stress is
uniform.

**Downward, concentrated:** P_r = 200 + 19.04 = 219.0 lb (comp.)
f_a = 219.04/5.969 = 36.70 lb/in; f_n = 36.70; f_v = 0;
f_r = **36.70 lb/in**, uniform. Weld ratio = 36.70/1,856 = **0.01977**.
Base metal (in-plane f_v = 0): 0. Ratio **0.01977**.

**Downward, distributed:** P_r = 350 + 19.04 = 369.0 lb
f_a = 369.04/5.969 = 61.83 lb/in; f_r = **61.83 lb/in**, uniform.
Weld ratio = 61.83/1,856 = **0.03331**. Base metal 0. Ratio **0.03331**.

**Outward, concentrated:** V = 200 lb, M = 200 × 0.95 = 190.0 lb-in,
P_r = 19.04 lb (comp.)
f_v = 200/5.969 = 33.51 lb/in
f_a = 19.04/5.969 = 3.190 lb/in
f_b = 190.0/2.835 = 67.01 lb/in
Compression side: f_n = 3.190 + 67.01 = 70.20 lb/in;
f_r = √(70.20² + 33.51²) = **77.79 lb/in**
Tension side: f_n = 3.190 − 67.01 = −63.82; f_r = √(63.82² + 33.51²) =
72.08 lb/in
Governing: **compression side**, f_r = 77.79 lb/in.
Weld ratio = 77.79/1,856 = **0.04191**.
Base metal (rail, in-plane): 33.51/2,430 = **0.01379**.
Ratio = max = **0.04191**.

**Outward, distributed:** V = 350 lb, M = 350 × 0.95 = 332.5 lb-in,
P_r = 19.04 lb
f_v = 350/5.969 = 58.64 lb/in
f_a = 3.190 lb/in
f_b = 332.5/2.835 = 117.3 lb/in
Compression side: f_n = 3.190 + 117.27 = 120.5 lb/in;
f_r = √(120.46² + 58.64²) = **134.0 lb/in**
Tension side: f_n = −114.1; f_r = 128.3 lb/in
Governing: **compression side**.
Weld ratio = 133.97/1,855.9 = **0.07219**.
Base metal: 58.64/2,430 = **0.02413**.
Ratio = **0.07219**.

**Inward, concentrated / distributed:** identical to outward for the round
ring (the opposite fiber becomes the compression side). Ratios **0.04191**
and **0.07219**; base metal 0.01379 and 0.02413.

**Longitudinal, concentrated / distributed:** V = L along the rail, carried
axially by the rail into the ring at the same e; identical to transverse for
the round ring. Ratios **0.04191** and **0.07219**; base metal 0.01379 and
0.02413.

**Upward, concentrated:** P_r = 1.0 × 200 − 0.6 × 19.04 = 188.6 lb
(tension). f_a = 188.58/5.969 = 31.59 lb/in (tension), uniform;
f_r = **31.59 lb/in**. Weld ratio = 31.59/1,856 = **0.01702**. Base metal
(in-plane) 0. Ratio **0.01702**.

**Upward, distributed:** P_r = 350 − 11.42 = 338.6 lb (tension).
f_a = 56.72 lb/in; f_r = **56.72 lb/in**. Weld ratio = **0.03056**. Ratio
**0.03056**.

### Check 3 envelope summary

| Case | f_a | f_b | f_v | f_n | f_r | Fiber | Weld ratio | Base ratio | Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Downward, conc. | 36.70 | — | 0 | 36.70 | 36.70 | uniform | 0.01977 | 0 | 0.01977 |
| Downward, dist. | 61.83 | — | 0 | 61.83 | 61.83 | uniform | 0.03331 | 0 | 0.03331 |
| Outward, conc. | 3.190 | 67.01 | 33.51 | 70.20 | 77.79 | comp. | 0.04191 | 0.01379 | 0.04191 |
| Outward, dist. | 3.190 | 117.3 | 58.64 | 120.5 | 134.0 | comp. | 0.07219 | 0.02413 | **0.07219** |
| Inward, conc. | 3.190 | 67.01 | 33.51 | 70.20 | 77.79 | comp. | 0.04191 | 0.01379 | 0.04191 |
| Inward, dist. | 3.190 | 117.3 | 58.64 | 120.5 | 134.0 | comp. | 0.07219 | 0.02413 | 0.07219 |
| Upward, conc. | 31.59 (T) | — | 0 | 31.59 | 31.59 | uniform | 0.01702 | 0 | 0.01702 |
| Upward, dist. | 56.72 (T) | — | 0 | 56.72 | 56.72 | uniform | 0.03056 | 0 | 0.03056 |
| Longitudinal, conc. | 3.190 | 67.01 | 33.51 | 70.20 | 77.79 | comp. | 0.04191 | 0.01379 | 0.04191 |
| Longitudinal, dist. | 3.190 | 117.3 | 58.64 | 120.5 | 134.0 | comp. | 0.07219 | 0.02413 | 0.07219 |

(lb/in; T = tension.) Controlling: **outward, distributed** (tied with
inward and longitudinal, distributed). Ratio **0.07219**, weld metal
governs. Minimum size OK. **Check 3 OK.**

## 6. Check 7: post to baseplate weld

### Case-independent values

**θ and k_ds.** At each extreme fiber of the ring the weld axis is the
tangent to the ring, horizontal and perpendicular to the plane of bending.
f_n is vertical (perpendicular to the weld axis). f_v acts in the direction
of V, which at the extreme fiber is also perpendicular to the tangent. So
the resultant is perpendicular to the weld axis: **θ = 90°**. In downward
and upward the force is purely vertical everywhere on the ring and the weld
axis is horizontal: θ = 90° at every point. So in every case:

k_ds = 1.0 + 0.50 × sin^1.5(90°) = 1.0 + 0.50 × 1.0 = **1.500**
(AISC 360-22 §J2.4; applied to round HSS per W2; own reading.)

**Weld metal:**

R_n/Ω = F_nw · k_ds · t_e / Ω = 42.00 × 1.500 × 0.1768 / 2.00
= 5.568 kip/in = **5,568 lb/in** (every case)

**Baseplate base metal** (W5):

R_n/Ω = 0.6 · Fu · t_p / Ω = 0.6 × 58 × 0.5 / 2.00
= 8.700 kip/in = **8,700 lb/in**
(AISC 360-22 §J4.2(b) form; Fu of A36 from Manual Table 2-5; own reading.)

**Minimum size:** parts joined are the post wall (t_nom = 0.145 in) and the
baseplate (t_p = 0.5 in). Thinner part t = **0.145 in** ≤ 1/4 in →
w_min = **0.125 in**. Provided 0.25 in ≥ 0.125 in: **OK**. (Table J2.4;
W11, t_nom for the pipe wall.)

§J2.2b(b): does not apply (T-joint). Post wall: covered by Check 5 (W5;
Fu/Fy = 1.714 ≥ 1.20). Baseplate bending: not checked (D12).

### Envelope

**Downward, concentrated:** P_r = 200 + 28.45 = 228.4 lb (comp.)
f_a = 228.45/5.969 = 38.27 lb/in; f_r = **38.27 lb/in**, uniform.
Weld ratio = 38.27/5,568 = **0.006874**.
Base ratio = 38.27/8,700 = **0.004399**. Ratio **0.006874**.

**Downward, distributed:** P_r = 350 + 28.45 = 378.4 lb.
f_a = 63.40 lb/in; f_r = **63.40 lb/in**.
Weld ratio = **0.01139**; base ratio = **0.007288**. Ratio **0.01139**.

**Outward, concentrated:** V = 200 lb, M = 200 × 41.5 = 8,300 lb-in,
P_r = 28.45 lb (comp.)
f_v = 200/5.969 = 33.51 lb/in
f_a = 28.447/5.969 = 4.766 lb/in
f_b = 8,300/2.8353 = 2,927 lb/in
Compression side: f_n = 4.766 + 2,927.4 = 2,932 lb/in;
f_r = √(2,932.16² + 33.51²) = **2,932 lb/in** (2,932.35)
Tension side: f_n = −2,922.6; f_r = 2,922.8 lb/in
Governing: **compression side**. θ = 90°, k_ds = 1.500.
Weld ratio = 2,932.35/5,567.6 = **0.5267**.
Base ratio = 2,932.35/8,700 = **0.3371**.
Ratio **0.5267**.

**Outward, distributed:** V = 350 lb, M = 350 × 41.5 = 14,525 lb-in,
P_r = 28.45 lb
f_v = 350/5.969 = 58.64 lb/in
f_a = 4.766 lb/in
f_b = 14,525/2.8353 = 5,123 lb/in
Compression side: f_n = 4.766 + 5,122.9 = 5,128 lb/in (5,127.70);
f_r = √(5,127.70² + 58.64²) = **5,128 lb/in** (5,128.04)
Tension side: f_n = −5,118.2; f_r = 5,118.5 lb/in
Governing: **compression side**. θ = 90°, k_ds = 1.500.
Weld ratio = 5,128.04/5,567.63 = **0.9210**.
Base ratio = 5,128.04/8,700 = **0.5894**.
Ratio **0.9210**.

**Inward and longitudinal, concentrated / distributed:** identical to
outward for the round ring: ratios **0.5267** and **0.9210**.

**Upward, concentrated:** P_r = 200 − 0.6 × 28.447 = 182.9 lb (tension).
f_a = 182.93/5.969 = 30.65 lb/in; f_r = **30.65 lb/in**, uniform.
Weld ratio = **0.005504**; base ratio = **0.003523**. Ratio **0.005504**.

**Upward, distributed:** P_r = 350 − 17.07 = 332.9 lb (tension).
f_a = 55.78 lb/in; f_r = **55.78 lb/in**.
Weld ratio = **0.01002**; base ratio = **0.006411**. Ratio **0.01002**.

### Check 7 envelope summary

| Case | f_a | f_b | f_v | f_n | f_r | Fiber | θ | k_ds | Weld allow | Weld ratio | Base ratio | Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Downward, conc. | 38.27 | — | 0 | 38.27 | 38.27 | uniform | 90° | 1.5 | 5,568 | 0.006874 | 0.004399 | 0.006874 |
| Downward, dist. | 63.40 | — | 0 | 63.40 | 63.40 | uniform | 90° | 1.5 | 5,568 | 0.01139 | 0.007288 | 0.01139 |
| Outward, conc. | 4.766 | 2,927 | 33.51 | 2,932 | 2,932 | comp. | 90° | 1.5 | 5,568 | 0.5267 | 0.3371 | 0.5267 |
| Outward, dist. | 4.766 | 5,123 | 58.64 | 5,128 | 5,128 | comp. | 90° | 1.5 | 5,568 | 0.9210 | 0.5894 | **0.9210** |
| Inward, conc. | 4.766 | 2,927 | 33.51 | 2,932 | 2,932 | comp. | 90° | 1.5 | 5,568 | 0.5267 | 0.3371 | 0.5267 |
| Inward, dist. | 4.766 | 5,123 | 58.64 | 5,128 | 5,128 | comp. | 90° | 1.5 | 5,568 | 0.9210 | 0.5894 | 0.9210 |
| Upward, conc. | 30.65 (T) | — | 0 | 30.65 | 30.65 | uniform | 90° | 1.5 | 5,568 | 0.005504 | 0.003523 | 0.005504 |
| Upward, dist. | 55.78 (T) | — | 0 | 55.78 | 55.78 | uniform | 90° | 1.5 | 5,568 | 0.01002 | 0.006411 | 0.01002 |
| Longitudinal, conc. | 4.766 | 2,927 | 33.51 | 2,932 | 2,932 | comp. | 90° | 1.5 | 5,568 | 0.5267 | 0.3371 | 0.5267 |
| Longitudinal, dist. | 4.766 | 5,123 | 58.64 | 5,128 | 5,128 | comp. | 90° | 1.5 | 5,568 | 0.9210 | 0.5894 | 0.9210 |

(lb/in; T = tension.) Controlling: **outward, distributed** (tied with
inward and longitudinal, distributed). Ratio **0.9210**, weld metal
governs. Minimum size OK. **Check 7 OK.**

## 7. Summary

| Check | Controlling case | Governing limit state | Ratio | Result |
| --- | --- | --- | --- | --- |
| 3, rail to post weld | outward, distributed (ties inward, longitudinal) | weld metal, k_ds = 1.0, compression-side fiber | 0.07219 | OK; min size OK (at the minimum) |
| 7, post to baseplate weld | outward, distributed (ties inward, longitudinal) | weld metal, k_ds = 1.5, compression-side fiber | 0.9210 | OK; min size OK |

Check 7 depends on the directional increase: with k_ds = 1.0 the ratio
would be 0.9210 × 1.5 = 1.382 (NG). Its basis for round HSS under base
moment is a drafted, non-primary, engineering-judgement entry (W2), so
Check 7 passing in this case rests on that ruling.

## 8. Values from my own reading (no verified entry)

All from memory of AISC 360-22 / 360-16 and the AISC Manual 16th ed.; no
web page was opened.

| Value | Used as | Citation |
| --- | --- | --- |
| F_EXX = 70 ksi | weld metal | E70XX classification; AISC 360-22 Table J2.5 |
| F_nw = 0.60·F_EXX | weld metal | AISC 360-22 §J2.4, Table J2.5 |
| Ω = 2.00, weld metal | weld metal | AISC 360-22 Table J2.5 |
| t_e = 0.707w | effective throat | AISC 360-22 §J2.2a |
| k_ds = 1.0 + 0.50 sin^1.5 θ | Check 7 | AISC 360-22 §J2.4 (Eq. J2-5, number unsure) |
| k_ds applies to round HSS / pipe welds, incl. under base moment | Check 7 | Brief W2 (STI, Packer et al.), engineering judgement |
| k_ds = 1.0 for the branch-to-chord weld | Check 3 | Brief W2, Chapter K commentary (not read) |
| Table J2.4 minimum sizes | both checks | AISC 360-22 Table J2.4 |
| §J2.2b(b) maximum size along edges, not applicable | both checks | AISC 360-22 §J2.2b(b) |
| 0.6·Fu·t, Ω = 2.00 shear rupture | both base metal lines | AISC 360-22 §J4.2(b), Eq. J4-4 |
| Fu = 60 ksi, A53 Gr B | Check 3 rail base metal, W5 guard | AISC Manual Table 2-4 |
| Fu = 58 ksi, A36 | Check 7 baseplate base metal | AISC Manual Table 2-5 |
| S_w = πD²/4 for a ring line | both | mechanics (W3) |

Verified entries used: `asce7.guard.concentrated`, `asce7.guard.uniform`,
`asce7.combo.asd.D_plus_L`, `ej.combo.bending.upward`,
`material.A53_GrB.Fy` (only for the W5 Fu/Fy guard),
`aisc360.pipe_as_round_hss` (pipe treated as round HSS for W2).

## 9. Open questions

**Q1. "Any direction" for the welds (Check 3 understated about 8%).** The
2026-10-03 ruling that the five orthogonal cases cover ASCE 7-22's "any
direction" was argued for Check 5 (H1-1b). For the Check 3 ring it does not
hold well, because the axial and moment terms are comparable: e/S_w =
0.95/2.835 = 0.3351 /in against 1/L_w = 0.1675 /in. A single load L
inclined φ below horizontal (in the plane of V) gives
f_n = (D + L sin φ)/L_w + L cos φ · e/S_w, f_v = L cos φ/L_w.
Maximized numerically: distributed, f_r = 144.5 lb/in at φ = 22.6°,
against 134.0 horizontal, a factor of **1.079** (ratio 0.07787 against
0.07219); concentrated, factor 1.078 (ratio 0.04518). Check 7: the factor
is 1.00007 (φ = 0.66°), negligible, as for Check 5. This cannot flip Check
3 here, but the envelope as decided does not find the worst direction for
Check 3. Decision for Micah: accept and record (as for Check 5), or add an
inclined case for the rail to post weld. **Not in the values file**; the
values above follow the decided five-case envelope.

**Q2. Torsion on the Check 3 ring.** A load applied at the rail's surface
rather than its centerline is not modeled (W1 puts V at the centerline).
A downward 200 lb at the rail's outer face (0.95 in off the post axis)
twists the ring: f = 2T/(πD²) = 2 × 190/(π × 1.900²) = 33.51 lb/in along
the weld axis. A horizontal load at the top of the rail raises e from
D/2 to D. Neither is in the envelope; Check 3 runs at 0.07, so neither can
flip a result. Flagged for completeness.

**Q3. Fusion face on the baseplate surface (leg on the plate).** I am not
sure whether AISC 360-22 requires a base metal check at the fusion face of
a fillet weld (area = leg w per inch), separate from the connected-element
rupture of §J4. If it did, as shear rupture 0.6·Fu·w/Ω = 0.6 × 58 × 0.25/2.00
= 4,350 lb/in it would govern Check 7 over the weld metal (5,568 lb/in) and
give 5,128/4,350 = 1.179 (NG); as tension rupture Fu·w/Ω = 7,250 lb/in it
would not govern (0.707). My recollection is that the 2005 and later
specifications dropped the fusion-face check for fillet welds and that
Table J2.5 sends base metal to §J4 (the connected element, which W5
models as rupture through t_p), but I could not confirm that from the
text. Worth Micah's look at Table J2.5 and the §J2.4 Commentary, since
this case passes with only 8% margin.

**Q4. Rail wall chord limit states (W7).** Not checked by decision. I did
not compute the chord plastification ratio and do not confirm the brief's
"about 20×" margin.

**Q5. Elastic shear distribution.** W3 takes the shear as uniform V/(πD)
and combines it at the extreme fiber, where the elastic shear flow (VQ/I) is
actually zero; at the neutral axis the elastic shear is 2V/(πD) with θ ≈ 0
(k_ds ≈ 1.0). I checked that point under the elastic distribution:
Check 7 distributed, f_r = 117.4 lb/in, θ = 2.33°, k_ds = 1.004, ratio
0.03149; Check 3 distributed, ratio 0.06307 (< 0.07219). The decided method
is conservative at the governing fiber and the neutral-axis point does not
govern.

## 10. Mapping gaps (step 7)

- **Keys I could not fill:** none. Every key in the template has a value.
- **Values I computed with no key:**
  - Check 3 base metal ratio in the downward and upward cases (0: no
    in-plane force); the template has `ratio_base` for the horizontal cases
    only.
  - The non-governing (tension-side) fiber f_r in each horizontal case
    (Check 3: 72.08, 128.3; Check 7: 2,923, 5,118 lb/in).
  - θ and k_ds for Check 3 (k_ds = 1.0 by W2; θ = 90° at the governing
    fiber, not used).
  - D_3 = 19.04 lb, D_7 = 28.45 lb, and the per-case V, P_r and M.
  - Fu/Fy = 1.714 for the W5 guard.
  - Q1's inclined-load ratios (0.07787, 0.04518) and Q5's neutral-axis
    ratios.
- **Text keys:** fiber recorded as "uniform" for downward and upward and
  "compression side" for the horizontal cases. Controlling recorded as
  "outward, distributed" for both checks (first of the exact ties in the
  file's key order).
- **F_nw_ksi** is recorded as 42 ksi (0.60·F_EXX, without k_ds) for both
  checks; k_ds is its own key for Check 7. If the tool's F_nw includes k_ds
  (the 360-16 form), Check 7 will differ by 1.5×, a naming mismatch rather
  than an engineering one.
- **t_min_in** recorded as the thinner part's t_nom, 0.145 in, for both
  checks.

## 11. Review checklist (docs/brief/verification.md, items 1–9)

1. **Loads complete.** Rail dead load over the span in Check 3; rail plus
   post dead load in Check 7 (post over h − t_p); both guard load types;
   no intermediate rail in this case, so no intermediate rail dead load;
   component load not applicable to either weld (it acts on the
   intermediate rail, whose connection is not checked). Baseplate weight is
   below the weld. Yes.
2. **Direction and worst case.** All five directions for both load types,
   both fibers evaluated in the moment cases, compression side found to
   govern by calculation (dead load compression adds). Upward net tension
   confirmed (0.6D < L). Inclined loads: Q1 (Check 3 understated ~8% by
   the decided envelope; Check 7 negligible).
3. **Checks complete.** Weld metal, base metal on the rail and the
   baseplate, minimum size, and the not-applicable maximum size. Post wall
   covered by Check 5 with the Fu/Fy guard met. Not checked by decision:
   chord wall (W7), baseplate bending (D12). Open: fusion-face leg (Q3),
   torsion (Q2). Minimum length cannot govern.
4. **Geometry.** Moment arm h − t_p = 41.5 in (not h); e = D_rail/2 =
   0.95 in; ring diameter is the post OD, 1.900 in; tributary length = span
   = 7.0 ft; D_post over h − t_p. Yes.
5. **Method and equations.** Elastic ring per W3; F_nw = 0.60F_EXX;
   Ω = 2.00; throat 0.707w; k_ds at θ = 90° = 1.5 for Check 7 and 1.0 for
   Check 3; base metal 0.6Fu·t/2.00 with t_des for the rail and t_p for the
   plate; Table J2.4 on t_nom of the thinner part. Applicability: §J2.2b(b)
   not applicable (T-joint); W8 (equal ODs) and W5 guard (1.714) met.
6. **Assumptions.** Fixity at top of baseplate; no bearing credit; weld at
   the rail's underside with V at the rail CL; fillet model all around at
   equal ODs (W9); longitudinal equals transverse for the ring. All are
   brief decisions, stated above.
7. **Code editions.** AISC 360-22, AISC Manual 16th ed., ASCE 7-22
   throughout; equation numbers from memory, flagged where unsure (Eq.
   J2-5).
8. **Magnitude sense.** f_b dominates Check 7 (5,123 of 5,128 lb/in), as
   expected for a 41.5 in cantilever on a 1.9 in ring; Check 3 is two
   orders smaller, consistent with e = 0.95 in. A 1/4 in E70 fillet with
   the 1.5 increase at ~5.6 kip/in is the familiar order. Units consistent
   (lb, in, lb/in).
9. **Governing case.** The horizontal distributed case governs both, as
   expected (w·s = 350 lb > P = 200 lb, and moment dominates). Outward,
   inward and longitudinal tie for the round ring.
