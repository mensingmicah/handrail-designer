# Independent calc: test case 8

All rectangular: HSS4X2X1/8 top rail on edge, HSS3X2X1/8 post, HSS2X1-1/2X1/8
intermediate rail, post welded to the baseplate on the faces parallel to the
rail.

| | |
| --- | --- |
| Case | case-08 (tests/cases/case-08.toml, inputs only) |
| Date | 2026-10-11 |
| Model | Claude, fresh independent-calc session. The model id is given in the session report to Micah and is not recorded in repo files. |
| Branch, commit | slice-6, 33daa9a6a0d40a93ef3ae44821d8e8136ceb3e86 |
| Method | ASD, AISC 360-22 §B3.2 (page 16.1-16) |

**Sources read.** The case inputs (value tables stripped, by the skill's
command). docs/BRIEF.md and every file in docs/brief/ as they stand on
slice-6; checks.md and welds.md also as they stand on origin/main, which
carries the S6-17 rulings (Micah, 2026-10-11) that slice-6 does not yet have.
CONTEXT.md. docs/plans/slice-6.md, decisions only. The three section rows of
data/aisc-shapes-database-v16.0.xlsx. out/aisc-360-22.pdf, read as extracted
text (pdftotext); the extraction drops radicals, Greek letters and inequality
signs, so each equation below is the form I know from the Specification,
confirmed against the surviving terms on the cited page. My values template,
tests/cases/independent/case-08.toml, in step 7 only.

**Not read.** src/, every other file under tests/, out/ other than the
Specification PDF, git history, any tool output, and
registry/code-values.toml in any part. The session instruction barred the
registry outright, so no verified entry was read either: every code value
below is "own reading", with its source.

Units: lb, in, lb-in, ksi unless noted. Full precision is carried; values
are shown to four significant figures.

## 1. Inputs

| Item | Value |
| --- | --- |
| Span L (post to post, tributary length s) | 6'-0" = 72 in |
| Post height h (top of concrete to top rail centerline) | 42 in |
| Baseplate t_p; B × N; grade | 1/2 in; 6 in (parallel to rail) × 8 in (perpendicular); A36 |
| h − t_p | 41.5 in |
| Top rail | HSS4X2X1/8, long side vertical |
| Post | HSS3X2X1/8, long side parallel to rail |
| Intermediate rail | HSS2X1-1/2X1/8, own section, long side horizontal |
| Grades | none entered: A500 Gr B (default) for all three members (S6-5) |
| Welds | rail to post 1/8 in; intermediate rail to post 1/8 in; post to baseplate 3/16 in on the faces parallel to the rail; E70XX; directional increase not elected |
| Guard loads | none entered: defaults, no exemption |
| Deflection limits | rail L/120, post (h − t_p)/60, intermediate rail L/120; none bypassed |

Orientation, derived (S6-2):

| Member | Vertical dimension | Horizontal dimension | Vertical load bends | Horizontal (transverse) load bends |
| --- | --- | --- | --- | --- |
| Top rail | 4 in | 2 in | strong axis x | weak axis y |
| Intermediate rail | 1.5 in | 2 in | weak axis y | strong axis x |

| Member | Parallel to rail | Perpendicular to rail | Transverse load bends | Longitudinal load bends |
| --- | --- | --- | --- | --- |
| Post | 3 in | 2 in | weak axis y | strong axis x |

## 2. Limit states considered

From the Specification, not from the plan's list. "Plan" means the slice 6
plan and the brief.

**Top rail (HSS4X2X1/8, flexure about both axes).**

| Limit state | Applies? | Why |
| --- | --- | --- |
| Yielding, §F7.1 | yes | both axes |
| Flange local buckling, §F7.2 | yes, weak axis | horizontal load puts a 4 in wall in compression as the flange: 31.5 is between λp and λr, noncompact, Eq. F7-2. Strong axis: the 2 in wall, 14.2, compact |
| Web local buckling, §F7.3 | no | strong axis web 31.5 < 60.76; weak axis web 14.2 < 60.76 |
| Lateral-torsional buckling, §F7.4 | yes, strong axis | Lb = 72 in > Lp = 69.30 in: Eq. F7-8 with Cb. Weak axis: none (User Note) |
| Biaxial interaction, §H1.1 | yes | outward and inward: dead load on x, guard load on y; Pr = 0 |
| Deflection | yes | Check 2 |
| Shear, Chapter G | not checked | stated assumption (output.md) |
| Axial force in the longitudinal case | not checked | the brief: the rail carries it axially and is not checked. For scale, 300 lb / 1.30 in² = 231 psi |
| Torsion, §H3 | none | loads act through the rail centerline (W1, S6-14 item 1) |
| Local wall strength under the concentrated load away from a joint | not checked | plan open item 5; flagged, section 16 |
| Chord wall at the post, Chapter K and §J10 | not checked | S6-12: a rectangular chord is a stated assumption inside the Chapter K limits. The limits are checked in section 7 |

**Post (HSS3X2X1/8, cantilever, axial and flexure).**

| Limit state | Applies? | Why |
| --- | --- | --- |
| Flexural buckling, §E3 | yes | Lc = 2.1·h, smaller r |
| Torsional buckling, §E4 | no | closed section; flexural buckling governs |
| Local buckling in compression | no | both walls nonslender (22.9 and 14.2 < 35.15) |
| Flexural yielding, §F7.1 | yes | each axis in its own case |
| Flange and web local buckling | no | transverse: flange 22.9 < 28.12, web 14.2; longitudinal: flange 14.2, web 22.9 |
| Lateral-torsional buckling | no | longitudinal (strong axis): Lb = 42 in < Lp = 77.96 in. Transverse is weak-axis bending |
| Interaction, §H1.1 | yes | outward, inward, longitudinal |
| Tension yielding, §D2(a) | yes | upward |
| Tension rupture, §D2(b) | not checked by the plan | see section 16, item 3: the brief's reason (welded all around, U = 1.0) does not hold for a face-pair weld |
| Second-order effects | ratio and stop | αPr/Pe against 0.05 (D1) |
| Biaxial bending under a horizontal load at an angle to the rail | not in the plan | S6-14 item 2 gives the post no biaxial case. It raises Check 5 here by about 25%: section 16, item 1 |
| Shear | not checked | stated assumption |
| Deflection | yes | Check 6 |

**Intermediate rail (HSS2X1-1/2X1/8).** Yielding on both axes; no local
buckling (9.93 and 14.2, compact as flange or web on either axis); LTB on
the strong axis in the horizontal case (Lb = 72 in > Lp = 60.07 in, Eq. F7-8
with Cb); no LTB in the downward case (weak axis); no biaxial case (S6-16
item 3); deflection in both cases; shear not checked.

**Rail to post weld (Check 3).** Weld metal on Table K5.1's effective
properties; base metal shear rupture of the rail wall under the in-plane
shear; Table J2.4 minimum size; post wall covered by Check 5 (W5), with the
Fu/Fy ≥ 1.20 guard (58/46 = 1.261); chord wall not checked (S6-12). At equal
widths the side welds land on the rail's corner radius and are flare-bevel
welds, modeled as fillets (stated assumption).

**Intermediate rail to post weld (Check 4b).** Simple shear connection:
weld metal over le, base metal shear rupture on both walls, Table J2.4;
chord limit states have no demand (S6-11).

**Post to baseplate weld (Check 7), two faces.** Weld metal by the elastic
line method on two flat lines; baseplate shear rupture through t_p; post
wall on its own lines (S6-7 as amended by S6-17 item 3): normal force
against §J4.1, shear against §J4.2(b), not combined; Table J2.4. Not
checked: baseplate bending and thickness, anchorage (by others).

## 3. Loads and load path

**Dead load.**

| Symbol | Equation | Substitution | Result | Source |
| --- | --- | --- | --- | --- |
| w_D,rail | tabulated weight | HSS4X2X1/8 | 4.75 lb/ft = 0.3958 lb/in | workbook, W |
| w_D,int | tabulated weight | HSS2X1-1/2X1/8 | 2.63 lb/ft = 0.2192 lb/in | workbook, W |
| D_rail | w_D,rail·s | 4.75 × 6 | 28.50 lb | loads-and-envelope.md |
| D_int | w_D,int·L | 2.63 × 6 | 15.78 lb | loads-and-envelope.md |
| D_post | W·(h − t_p) | 3.90 × 41.5/12 | 13.49 lb | loads-and-envelope.md |
| D (at the post) | D_rail + D_int + D_post | 28.50 + 15.78 + 13.4875 | 57.77 lb | loads-and-envelope.md |
| W_bp | ρ·B·N·t_p | (490/1728) × 6 × 8 × 0.5 | 6.806 lb | S4-6; reactions only |

**Guard loads.** P = 200 lb and w = 50 lb/ft, never concurrent. On the
rail: P at midspan, w along the span. On the post: P, or w·s = 50 × 6 =
300 lb, at the top of the post (the top rail centerline, h above concrete).
Component load P_c = 50 lb on the intermediate rail only, not concurrent
with the guard loads; at midspan for the member (4a), adjacent to the post
for the weld (4b).

**Path.** Rail dead load and vertical guard load: simple-span bending of
the rail about x, end reactions through the rail to post weld (no bearing
credit) into the post as axial load. Horizontal transverse guard load:
simple-span bending of the rail about y; at the post, a shear V at the rail
centerline, e = 2 in above the weld plane (rail underside), then cantilever
bending of the post about its weak axis to the top of the baseplate,
M = V·(h − t_p), and through the two base weld lines into the plate.
Longitudinal guard load: along the rail (not checked), into the post top as
V, cantilever bending of the post about its strong axis, which bends each
base weld line about its own mid-length. Intermediate rail dead load:
through its end weld to the post face as shear, then axial in the post.

**Envelope.** Five direction cases × two load types:

| Case | Rail (Checks 1, 2) | Rail to post weld (Check 3) | Post (Check 5), base weld (Check 7) | Combination |
| --- | --- | --- | --- | --- |
| Downward | D + L on x | (D_rail + L) axial, uniform | Pr = D + L, no moment | ASCE 7-22 ASD D + L |
| Outward, inward | D on x, L on y | V = L, M = V·e out-of-plane, D_rail axial | Pr = D, Mr = L·(h − t_p), weak axis | ASD D + L |
| Longitudinal | not checked (axial) | V = L, M = V·e in-plane, D_rail axial | Pr = D, Mr = L·(h − t_p), strong axis | ASD D + L |
| Upward | L − 0.6D on x | (L − 0.6·D_rail) tension | Pr = L − 0.6D tension | 0.6D + 1.0L, engineering judgement |

Outward and inward are identical for every check here (doubly symmetric
sections, symmetric weld lines); both are listed. Upward: 0.6D = 34.66 lb at
the post and 17.10 lb at the rail weld, both less than L, so there is net
tension in every upward case.

## 4. Section properties

AISC Shapes Database v16.0, as published (workbook rows read by the skill's
command).

| Property | Top rail HSS4X2X1/8 | Post HSS3X2X1/8 | Intermediate rail HSS2X1-1/2X1/8 |
| --- | --- | --- | --- |
| W, lb/ft | 4.75 | 3.90 | 2.63 |
| A, in² | 1.30 | 1.07 | 0.724 |
| Ht, in | 4 | 3 | 2 |
| B, in | 2 | 2 | 1.5 |
| t_nom, in | 0.125 | 0.125 | 0.125 |
| t_des, in | 0.116 | 0.116 | 0.116 |
| b/t_des (the B wall) | 14.2 | 14.2 | 9.93 |
| h/t_des (the Ht wall) | 31.5 | 22.9 | 14.2 |
| Ix, in⁴ | 2.65 | 1.30 | 0.383 |
| Zx, in³ | 1.66 | 1.06 | 0.475 |
| Sx, in³ | 1.32 | 0.867 | 0.383 |
| rx, in | 1.43 | 1.10 | 0.728 |
| Iy, in⁴ | 0.898 | 0.692 | 0.244 |
| Zy, in³ | 1.02 | 0.803 | 0.389 |
| Sy, in³ | 0.898 | 0.692 | 0.325 |
| ry, in | 0.830 | 0.804 | 0.581 |
| J, in⁴ | 2.20 | 1.47 | 0.496 |

Classification limits at Fy = 46 ksi: √(E/Fy) = √(29000/46) = 25.11.
Flange λp = 1.12 × 25.11 = 28.12, λr = 1.40 × 25.11 = 35.15 (Case 17). Web
λp = 2.42 × 25.11 = 60.76, λr = 5.70 × 25.11 = 143.1 (Case 19). Compression
λr = 1.40 × 25.11 = 35.15 (Table B4.1a Case 6).

## 5. Check 1: top rail bending

### Capacities

Strong axis x (vertical load). Flange 14.2 ≤ 28.12, web 31.5 ≤ 60.76:
compact.

| Symbol | Equation | Substitution | Result | Citation |
| --- | --- | --- | --- | --- |
| Mp,x | Fy·Zx | 46 × 1.66 | 76.36 kip-in = 76,360 lb-in | Eq. F7-1, p. 16.1-63 |
| √(J·Ag) | | √(2.20 × 1.30) | 1.691 in³ | |
| Lp | 0.13·E·ry·√(J·Ag)/Mp | 0.13 × 29000 × 0.830 × 1.691/76.36 | 69.30 in | Eq. F7-10, p. 16.1-64 |
| 0.7·Fy·Sx | | 0.7 × 46 × 1.32 | 42.50 kip-in | |
| Lr | 2·E·ry·√(J·Ag)/(0.7·Fy·Sx) | 2 × 29000 × 0.830 × 1.691/42.50 | 1915 in | Eq. F7-11, p. 16.1-64 |
| Lb | span | | 72 in | S6-4 |
| branch | Lp < Lb ≤ Lr | 69.30 < 72 ≤ 1915 | Eq. F7-8 | §F7.4(b) |
| bracket | Mp − (Mp − 0.7FySx)(Lb − Lp)/(Lr − Lp) | 76.36 − (76.36 − 42.50)(72 − 69.30)/(1915 − 69.30) | 76.31 kip-in | Eq. F7-8 |
| Mn,x | Cb × bracket ≤ Mp | lowest Cb is 1.136: 1.136 × 76.31 = 86.72 > 76.36 | 76.36 kip-in in every case | Eq. F7-8 |
| Mc,x | Mn,x/Ω_b | 76.36/1.67 | 45.72 kip-in = 45,720 lb-in | §F1(a) |

Weak axis y (horizontal load). The flange is the 4 in wall: λ = 31.5,
28.12 < 31.5 ≤ 35.15, **noncompact flange**. The web is the 2 in wall:
14.2 ≤ 60.76, compact. No LTB (User Note to §F7.4).

| Symbol | Equation | Substitution | Result | Citation |
| --- | --- | --- | --- | --- |
| Mp,y | Fy·Zy | 46 × 1.02 | 46.92 kip-in = 46,920 lb-in | Eq. F7-1 |
| Fy·Sy | | 46 × 0.898 | 41.31 kip-in | |
| Mn,y | Mp − (Mp − Fy·S)(λ − λpf)/(λrf − λpf) ≤ Mp | 46.92 − (46.92 − 41.31)(31.5 − 28.12)/(35.15 − 28.12) | 44.22 kip-in | Eq. F7-2, p. 16.1-63 |
| Mc,y | Mn,y/Ω_b | 44.22/1.67 | 26.48 kip-in = 26,480 lb-in | §F1(a) |

### Demands and Cb

M_D = w_D·L²/8 = 0.3958 × 72²/8 = 256.5 lb-in (x). Concentrated:
M_L = P·L/4 = 200 × 72/4 = 3600 lb-in. Distributed: M_L = w·L²/8 =
(50/12) × 72²/8 = 2700 lb-in.

Cb = 12.5·Mmax/(2.5·Mmax + 3·MA + 4·MB + 3·MC) (Eq. F1-1), on the x-axis
diagram of each case; MB = Mmax at midspan and MC = MA by symmetry.

| Case | x-axis diagram | Mmax | MA (quarter point) | Cb |
| --- | --- | --- | --- | --- |
| Downward, concentrated | w_D uniform + P at midspan | 256.5 + 3600 = 3856.5 | 3·w_D·L²/32 + P·L/8 = 192.4 + 1800 = 1992 | 12.5 × 3856.5/(6.5 × 3856.5 + 6 × 1992.4) = 1.302 |
| Downward, distributed | (w_D + w) uniform | 2956.5 | 0.75·Mmax = 2217 | 12.5/11 = 1.136 |
| Outward, inward (both types) | w_D uniform | 256.5 | 192.4 | 1.136 |
| Upward, concentrated | P at midspan less 0.6·w_D uniform | 3600 − 0.6 × 256.5 = 3446.1 | 1800 − 0.6 × 192.4 = 1685 | 12.5 × 3446.1/(6.5 × 3446.1 + 6 × 1684.6) = 1.325 |
| Upward, distributed | (w − 0.6·w_D) uniform | 2700 − 153.9 = 2546.1 | 1910 | 1.136 |

In the upward concentrated case the net moment rises monotonically to
midspan (P/2 = 100 lb exceeds 0.6·w_D·L/2 = 8.55 lb), so Mmax is at midspan.

### Envelope

Ratio = Mrx/Mcx + Mry/Mcy (Eq. H1-1b with Pr = 0; S6-4).

| Case | Mrx, lb-in | Mcx, lb-in | Mry, lb-in | Mcy, lb-in | Ratio |
| --- | --- | --- | --- | --- | --- |
| Downward, concentrated | 3856.5 | 45,720 | 0 | | 0.08434 |
| Downward, distributed | 2956.5 | 45,720 | 0 | | 0.06466 |
| Outward, concentrated | 256.5 | 45,720 | 3600 | 26,480 | 0.005610 + 0.1359 = **0.1416** |
| Outward, distributed | 256.5 | 45,720 | 2700 | 26,480 | 0.005610 + 0.1020 = 0.1076 |
| Inward, concentrated | 256.5 | 45,720 | 3600 | 26,480 | 0.1416 |
| Inward, distributed | 256.5 | 45,720 | 2700 | 26,480 | 0.1076 |
| Upward, concentrated | 3446.1 | 45,720 | 0 | | 0.07537 |
| Upward, distributed | 2546.1 | 45,720 | 0 | | 0.05568 |

Longitudinal: the rail is not checked for the axial load (brief); its
bending is the dead load alone, 256.5/45,720 = 0.005610, below every case
above. **Controls: outward (= inward), concentrated, 0.1416, OK.**

## 6. Check 2: top rail deflection

Allowable Δ = L/120 = 72/120 = 0.6000 in. Horizontal cases: live load only
on Iy = 0.898 in⁴. Downward: D + L on Ix = 2.65 in⁴ (engineering-judgement
serviceability combination). Upward: live load only on Ix.

| Symbol | Equation | Substitution | Result |
| --- | --- | --- | --- |
| Δ_P,y | P·L³/(48·E·Iy) | 200 × 72³/(48 × 29×10⁶ × 0.898) | 0.05972 in |
| Δ_w,y | 5·w·L⁴/(384·E·Iy) | 5 × 4.1667 × 72⁴/(384 × 29×10⁶ × 0.898) | 0.05599 in |
| Δ_P,x | P·L³/(48·E·Ix) | 200 × 72³/(48 × 29×10⁶ × 2.65) | 0.02024 in |
| Δ_w,x | 5·w·L⁴/(384·E·Ix) | 5 × 4.1667 × 72⁴/(384 × 29×10⁶ × 2.65) | 0.01897 in |
| Δ_D,x | 5·w_D·L⁴/(384·E·Ix) | 5 × 0.3958 × 72⁴/(384 × 29×10⁶ × 2.65) | 0.001802 in |

| Case | Δ, in | Ratio Δ/0.6 |
| --- | --- | --- |
| Downward, concentrated | 0.02024 + 0.001802 = 0.02204 | 0.03673 |
| Downward, distributed | 0.01897 + 0.001802 = 0.02077 | 0.03462 |
| Outward, concentrated | 0.05972 | **0.09953** |
| Outward, distributed | 0.05599 | 0.09331 |
| Inward, concentrated | 0.05972 | 0.09953 |
| Inward, distributed | 0.05599 | 0.09331 |
| Upward, concentrated | 0.02024 | 0.03373 |
| Upward, distributed | 0.01897 | 0.03162 |

**Controls: outward (= inward), concentrated, 0.09953, OK.**

## 7. Check 3: top rail weld to post

### Joint and limits

Chord: the rail, connecting face its 2 in underside, B = 2 in, H = 4 in,
t = 0.116 in. Branch: the post, Bb = 2 in across the rail (its dimension
perpendicular to the rail), Hb = 3 in along the rail (in the plane of the
connection), tb = 0.116 in. θ = 90°.

- Width rule (S6-9): Bb = 2 in ≤ B = 2 in. Equal widths, allowed.
- Chapter K limits for a rectangular chord (S6-13): B/t = 2/0.116 = 17.24
  and H/t = 4/0.116 = 34.48, both ≤ 35; Fy = 46 ≤ 52 ksi; Fy/Fu = 46/58 =
  0.7931 ≤ 0.8. No stop. H/t is within 1.5% of the limit.

### Effective weld (Table K5.1, page 16.1-171)

| Symbol | Equation | Substitution | Result | Citation |
| --- | --- | --- | --- | --- |
| β | Bb/B | 2/2 | 1.000 | §K1.1 |
| Be | [10/(B/t)]·[Fy·t/(Fyb·tb)]·Bb ≤ Bb | (10/17.24) × 1.0 × 2 | 1.160 in | Eq. K1-1, p. 16.1-159 |
| cap | Be/2 ≤ Bb/4 when β > 0.85 or θ > 50° | Be ≤ 2/2 | Be = 1.000 in | Table K5.1; S6-17 item 4 |
| le | 2·Hb/sin θ + 2·Be | 2 × 3 + 2 × 1.000 | 8.000 in | Eq. K5-5 |
| S_ip/tw | (1/3)·Hb² + Be·Hb | 9/3 + 1.000 × 3 | 6.000 in² | Eq. K5-6, per unit throat |
| S_op/tw | Hb·Bb + Bb²/3 − (Bb − Be)³/(3·Bb) | 6 + 4/3 − 1/6 | 7.167 in² | Eq. K5-7, per unit throat |

The weld is treated as a line (W3), so the section moduli are taken per
unit of throat, in in². Longitudinal case: in-plane bending, S_ip.
Transverse cases: out-of-plane bending, S_op. Vertical cases: axial over le.
Shear uniform over le (S6-8).

### Strengths

| Symbol | Equation | Substitution | Result | Citation |
| --- | --- | --- | --- | --- |
| e | half the rail depth | 4/2 | 2.000 in | W1 |
| throat | 0.707·w | 0.707 × 0.125 | 0.08838 in | §J2.2a |
| Fnw | 0.60·FEXX | 0.60 × 70 | 42.00 ksi | Table J2.5 |
| weld allowable | Fnw·throat·k_ds/Ω | 42 × 0.08838 × 1.0/2.00 | 1.856 kip/in = 1856 lb/in | Eq. J2-4; k_ds = 1.0 (W2) |
| rail wall allowable | 0.6·Fu·t_des/Ω | 0.6 × 58 × 0.116/2.00 | 2.018 kip/in = 2018 lb/in | Eq. J4-4 (W6) |
| minimum size | thinner part t_nom = 0.125 in ≤ 1/4 in | w_min = 1/8 in; w = 1/8 in | OK | Table J2.4 |

Post wall: covered by Check 5 (W5). Rail wall, normal force: not checked
(S6-12).

### Envelope

D here is the rail's dead load, D_rail = 28.50 lb. f_a = axial/le;
f_b = V·e/S; f_v = V/le; f_n = f_a + f_b on the compression side of bending
(dead-load compression adds there, W10); f_r = √(f_n² + f_v²). Weld ratio =
f_r/1856. Base metal ratio = f_v/2018.

| Case | Axial, lb | V, lb | f_a | f_b | f_v | f_n | f_r, lb/in | Fiber | Weld ratio | Base ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Downward, concentrated | 228.5 | | 28.56 | | | 28.56 | 28.56 | uniform | 0.01539 | |
| Downward, distributed | 328.5 | | 41.06 | | | 41.06 | 41.06 | uniform | 0.02213 | |
| Outward, concentrated | 28.5 | 200 | 3.563 | 400/7.167 = 55.81 | 25.00 | 59.38 | 64.42 | compression side | 0.03471 | 0.01239 |
| Outward, distributed | 28.5 | 300 | 3.563 | 600/7.167 = 83.72 | 37.50 | 87.28 | 95.00 | compression side | 0.05119 | 0.01858 |
| Inward, concentrated | 28.5 | 200 | 3.563 | 55.81 | 25.00 | 59.38 | 64.42 | compression side | 0.03471 | 0.01239 |
| Inward, distributed | 28.5 | 300 | 3.563 | 83.72 | 37.50 | 87.28 | 95.00 | compression side | 0.05119 | 0.01858 |
| Longitudinal, concentrated | 28.5 | 200 | 3.563 | 400/6.000 = 66.67 | 25.00 | 70.23 | 74.55 | compression side | 0.04017 | 0.01239 |
| Longitudinal, distributed | 28.5 | 300 | 3.563 | 600/6.000 = 100.0 | 37.50 | 103.6 | 110.1 | compression side | **0.05935** | 0.01858 |
| Upward, concentrated | 200 − 17.1 = 182.9 | | 22.86 | | | 22.86 | 22.86 | uniform | 0.01232 | |
| Upward, distributed | 300 − 17.1 = 282.9 | | 35.36 | | | 35.36 | 35.36 | uniform | 0.01905 | |

The weld metal ratio exceeds the base metal ratio in every case, so the
check's ratio is the weld ratio. **Controls: longitudinal, distributed,
0.05935, OK** (weld metal).

## 8. Check 4a: intermediate rail, component load

Horizontal case: P_c alone at midspan, bending the strong axis x. Downward
case: P_c at midspan plus the rail's dead load, bending the weak axis y.

| Symbol | Equation | Substitution | Result | Citation |
| --- | --- | --- | --- | --- |
| Mp,x | Fy·Zx | 46 × 0.475 | 21.85 kip-in = 21,850 lb-in | Eq. F7-1 |
| Mp,y | Fy·Zy | 46 × 0.389 | 17.89 kip-in = 17,890 lb-in | Eq. F7-1 |
| √(J·Ag) | | √(0.496 × 0.724) | 0.5993 in³ | |
| Lp | 0.13·E·ry·√(J·Ag)/Mp | 0.13 × 29000 × 0.581 × 0.5993/21.85 | 60.07 in | Eq. F7-10 |
| 0.7·Fy·Sx | | 0.7 × 46 × 0.383 | 12.33 kip-in | |
| Lr | 2·E·ry·√(J·Ag)/(0.7·Fy·Sx) | 2 × 29000 × 0.581 × 0.5993/12.33 | 1637 in | Eq. F7-11 |
| Cb, horizontal | 12.5/(2.5 + 3 × 0.5 + 4 + 3 × 0.5) | midspan point load alone: MA = MC = 0.5·Mmax | 1.316 | Eq. F1-1 |
| bracket | Mp − (Mp − 0.7FySx)(Lb − Lp)/(Lr − Lp) | 21.85 − (21.85 − 12.33)(72 − 60.07)/(1637 − 60.07) | 21.78 kip-in | Eq. F7-8 |
| Mn,x | Cb × bracket ≤ Mp | 1.316 × 21.78 = 28.66 > 21.85 | 21.85 kip-in | Eq. F7-8 |
| Mc, horizontal | Mn,x/1.67 | 21.85/1.67 | 13.08 kip-in = 13,080 lb-in | §F1(a) |
| Mc, downward | Mp,y/1.67 (no LTB, compact) | 17.894/1.67 | 10.71 kip-in = 10,710 lb-in | §F1(a) |
| M, horizontal | P_c·L/4 | 50 × 72/4 | 900.0 lb-in | S4-3 |
| M, downward | P_c·L/4 + w_D,int·L²/8 | 900 + 0.2192 × 72²/8 = 900 + 142.0 | 1042 lb-in | S4-10 |
| Δ allowable | L/120 | 72/120 | 0.6000 in | inputs |
| Δ, horizontal | P_c·L³/(48·E·Ix) | 50 × 72³/(48 × 29×10⁶ × 0.383) | 0.03500 in | |
| Δ, downward | P_c·L³/(48·E·Iy) + 5·w_D,int·L⁴/(384·E·Iy) | 0.05495 + 0.01084 | 0.06578 in | D + L |

| Case | Bending ratio | Deflection ratio |
| --- | --- | --- |
| Horizontal | 900.0/13,080 = 0.06879 | 0.03500/0.6 = 0.05834 |
| Downward | 1042/10,710 = 0.09725 | 0.06578/0.6 = **0.1096** |

**Controls: downward, deflection, 0.1096, OK.**

## 9. Check 4b: intermediate rail weld to post

Chord: the post. The intermediate rail's end lands on the post face that
looks along the rail, whose width is the post's dimension perpendicular to
the rail: B = 2 in, t = 0.116 in. Branch: the intermediate rail, Bb = 2 in
(horizontal), Hb = 1.5 in (vertical, along the post's axis). Width rule:
2 in ≤ 2 in, allowed. No applicability stop at Check 4b (S6-13).

| Symbol | Equation | Substitution | Result | Citation |
| --- | --- | --- | --- | --- |
| β | Bb/B | 2/2 | 1.000 | |
| Be | [10/(B/t)]·[Fy·t/(Fyb·tb)]·Bb, capped at Bb/2 | (10/17.24) × 1.0 × 2 = 1.160, capped | 1.000 in | Eq. K1-1; Table K5.1 |
| le | 2·Hb + 2·Be | 2 × 1.5 + 2 × 1.000 | 5.000 in | Eq. K5-5 |
| R_D | w_D,int·L/2 | 2.63 × 6/2 | 7.890 lb | S4-9 |
| R, horizontal | √(P_c² + R_D²) | √(50² + 7.89²) | 50.62 lb | S4-9 |
| R, downward | R_D + P_c | 7.89 + 50 | 57.89 lb | S4-9 |
| throat | 0.707·w | 0.707 × 0.125 | 0.08838 in | §J2.2a |
| weld allowable | 0.60 × 70 × 0.08838 × 1.0/2.00 | | 1856 lb/in | Eq. J2-4 |
| post wall allowable | 0.6·Fu·t_des,post/2.00 | 0.6 × 58 × 0.116/2 | 2018 lb/in | Eq. J4-4 |
| intermediate rail wall allowable | 0.6·Fu·t_des,int/2.00 | 0.6 × 58 × 0.116/2 | 2018 lb/in | Eq. J4-4 |
| base metal governs | lower allowable; a tie goes to the post wall | 2018 = 2018 | post wall | S4-12 |
| minimum size | thinner part 0.125 in ≤ 1/4 in | w_min = 1/8 in; w = 1/8 in | OK | Table J2.4 |

Simple shear connection: e = 0, no end moment, f_r = f_v = R/le.

| Case | R, lb | f_v = f_r, lb/in | Weld ratio | Base metal ratio |
| --- | --- | --- | --- | --- |
| Horizontal | 50.62 | 10.12 | 0.005455 | 0.005016 |
| Downward | 57.89 | 11.58 | **0.006239** | 0.005736 |

Chord limit states of the post wall: no demand (S6-11). **Controls:
downward, component, 0.006239, OK** (weld metal).

## 10. Check 5: post, combined axial and flexure

### Capacities

Compression. Walls 22.9 and 14.2 ≤ 35.15: nonslender.

| Symbol | Equation | Substitution | Result | Citation |
| --- | --- | --- | --- | --- |
| Lc | K·h | 2.1 × 42 | 88.20 in | D3 |
| Lc/r | Lc/ry (smaller r) | 88.2/0.804 | 109.7 | S6-14 item 2; under 200 |
| limit | 4.71·√(E/Fy) | 4.71 × 25.11 | 118.3 | §E3 |
| Fe | π²·E/(Lc/r)² | π² × 29000/109.7² | 23.78 ksi | Eq. E3-4 |
| Fcr | 0.658^(Fy/Fe)·Fy | 0.658^(46/23.78) × 46 = 0.658^1.934 × 46 | 20.47 ksi, Eq. E3-2 | 109.7 ≤ 118.3 |
| Pn | Fcr·Ag | 20.47 × 1.07 | 21.91 kips = 21,910 lb | Eq. E3-1 |
| Pc | Pn/Ω_c | 21.906/1.67 | 13.12 kips = 13,120 lb | §E1 |
| Pt | Fy·Ag/Ω_t | 46 × 1.07/1.67 | 29.47 kips = 29,470 lb | Eq. D2-1 |

Flexure, weak axis y (outward, inward). Flange is the 3 in wall, 22.9 ≤
28.12; web the 2 in wall, 14.2: compact. No LTB.

| Symbol | Equation | Substitution | Result |
| --- | --- | --- | --- |
| Mn,y | Fy·Zy | 46 × 0.803 | 36.94 kip-in = 36,940 lb-in |
| Mc,y | Mn,y/1.67 | 36.938/1.67 | 22.12 kip-in = 22,120 lb-in |

Flexure, strong axis x (longitudinal). Flange 14.2, web 22.9: compact.
Cb = 1.0 (cantilever, free end unbraced, §F1(c)); Lb = h = 42 in.

| Symbol | Equation | Substitution | Result |
| --- | --- | --- | --- |
| Mp,x | Fy·Zx | 46 × 1.06 | 48.76 kip-in |
| Lp | 0.13·E·ry·√(J·Ag)/Mp | 0.13 × 29000 × 0.804 × √(1.47 × 1.07)/48.76 | 77.96 in |
| branch | Lb ≤ Lp | 42 ≤ 77.96 | LTB does not apply, §F7.4(a) |
| Mn,x | Mp | | 48.76 kip-in = 48,760 lb-in |
| Mc,x | Mn,x/1.67 | 48.76/1.67 | 29.20 kip-in = 29,200 lb-in |

Second-order ratio (D1), α = 1.6, Pr = D = 57.77 lb:

| Case | Pe = π²·E·I/Lc² | αPr/Pe |
| --- | --- | --- |
| Outward, inward (Iy = 0.692) | π² × 29000 × 0.692/88.2² = 25.46 kips | 1.6 × 57.77/25,460 = 0.003630 |
| Longitudinal (Ix = 1.30) | π² × 29000 × 1.30/88.2² = 47.83 kips | 1.6 × 57.77/47,830 = 0.001932 |

Both are below 0.05: second-order effects negligible, no stop.

### Envelope

Moment cases: Pr/Pc = 57.77/13,120 = 0.004404 < 0.2, so Eq. H1-1b:
Pr/(2Pc) + Mr/Mc, with Pr/(2Pc) = 0.002202. Mr = L·(h − t_p).

| Case | Pr, lb | Mr, lb-in | Mc, lb-in | Equation | Ratio |
| --- | --- | --- | --- | --- | --- |
| Downward, concentrated | 57.77 + 200 = 257.8 | | | Pr/Pc | 0.01965 |
| Downward, distributed | 57.77 + 300 = 357.8 | | | Pr/Pc | 0.02727 |
| Outward, concentrated | 57.77 | 200 × 41.5 = 8300 | 22,120 | H1-1b | 0.002202 + 0.3753 = 0.3775 |
| Outward, distributed | 57.77 | 300 × 41.5 = 12,450 | 22,120 | H1-1b | 0.002202 + 0.5629 = **0.5651** |
| Inward, concentrated | 57.77 | 8300 | 22,120 | H1-1b | 0.3775 |
| Inward, distributed | 57.77 | 12,450 | 22,120 | H1-1b | 0.5651 |
| Longitudinal, concentrated | 57.77 | 8300 | 29,200 | H1-1b | 0.002202 + 0.2843 = 0.2865 |
| Longitudinal, distributed | 57.77 | 12,450 | 29,200 | H1-1b | 0.002202 + 0.4264 = 0.4286 |
| Upward, concentrated | 200 − 0.6 × 57.77 = 165.3 | | | Pr/Pt | 0.005610 |
| Upward, distributed | 300 − 34.66 = 265.3 | | | Pr/Pt | 0.009003 |

**Controls: outward (= inward), distributed, 0.5651, OK.**

## 11. Check 6: post deflection

Δ = V·(h − t_p)³/(3·E·I), live load only, on the I of the axis the case
bends. Allowable = (h − t_p)/60 = 41.5/60 = 0.6917 in. (h − t_p)³ = 71,473
in³.

| Case | V, lb | I, in⁴ | Δ, in | Ratio |
| --- | --- | --- | --- | --- |
| Outward, concentrated | 200 | 0.692 | 200 × 71,473/(3 × 29×10⁶ × 0.692) = 0.2374 | 0.3433 |
| Outward, distributed | 300 | 0.692 | 0.3562 | **0.5149** |
| Inward, concentrated | 200 | 0.692 | 0.2374 | 0.3433 |
| Inward, distributed | 300 | 0.692 | 0.3562 | 0.5149 |
| Longitudinal, concentrated | 200 | 1.30 | 0.1264 | 0.1827 |
| Longitudinal, distributed | 300 | 1.30 | 0.1896 | 0.2741 |

Downward and upward: vertical, no lateral deflection. **Controls: outward
(= inward), distributed, 0.5149, OK.**

## 12. Check 7: post weld to baseplate

### Weld line (S6-6, face pair)

The faces parallel to the rail are the post's two 3 in faces. They sit
1.0 in each side of the post's centroid in the transverse direction (the
post is 2 in perpendicular to the rail), and each runs along the rail.

| Symbol | Equation | Substitution | Result | Citation |
| --- | --- | --- | --- | --- |
| ℓ (one flat) | outside dimension − 4·t_des | 3 − 4 × 0.116 | 2.536 in | S6-6 |
| L_w | 2·ℓ | 2 × 2.536 | 5.072 in | S6-6 |
| S_w,t (transverse cases) | I/c = 2·ℓ·(1.0)²/1.0 | 2 × 2.536 × 1.0 | 5.072 in² | W3; two lines at ±1.0 in from the bending axis |
| S_w,l (longitudinal case) | I/c = (2·ℓ³/12)/(ℓ/2) = ℓ²/3 | 2.536²/3 | 2.144 in² | W3; each line bent about its own mid-length |
| arm | h − t_p | 42 − 0.5 | 41.50 in | D4 |

### Strengths

| Symbol | Equation | Substitution | Result | Citation |
| --- | --- | --- | --- | --- |
| throat | 0.707·w | 0.707 × 0.1875 | 0.1326 in | §J2.2a |
| Fnw | 0.60·FEXX | 0.60 × 70 | 42.00 ksi | Table J2.5 |
| weld allowable | Fnw·throat·k_ds/Ω | 42 × 0.1326 × 1.0/2.00 | 2.784 kip/in = 2784 lb/in | Eq. J2-4; k_ds = 1.0, §J2.4(a)(2), User Note to §K5 (S6-6) |
| baseplate allowable | 0.6·Fu·t_p/Ω | 0.6 × 58 × 0.5/2.00 | 8.700 kip/in = 8700 lb/in | Eq. J4-4 (W5) |
| post wall, yielding | Fy·t_des/1.67 | 46 × 0.116/1.67 | 3.195 kip/in = 3195 lb/in | Eq. J4-1 |
| post wall, rupture | Fu·t_des/2.00 | 58 × 0.116/2.00 | 3.364 kip/in = 3364 lb/in | Eq. J4-2 |
| post wall, normal force allowable | lower of the two | | 3195 lb/in (yielding) | S6-7 |
| post wall, shear allowable | 0.6·Fu·t_des/2.00 | 0.6 × 58 × 0.116/2.00 | 2.018 kip/in = 2018 lb/in | Eq. J4-4; S6-17 item 3 |
| minimum size | thinner part: post wall t_nom = 0.125 in (plate 0.5 in) | w_min = 1/8 in; w = 3/16 in | OK | Table J2.4 |

The welded walls are nonslender in compression (h/t = 22.9 ≤ 35.15), so
yielding applies on the compression side (S6-7).

### Envelope

D = 57.77 lb at the post. f_a = axial/L_w; f_b = M/S_w with M = V × 41.5;
f_v = V/L_w; f_n = f_a + f_b at the compression-side extreme fiber;
f_r = √(f_n² + f_v²). Weld ratio = f_r/2784; baseplate ratio = f_r/8700;
post wall normal ratio = f_n/3195; post wall shear ratio = f_v/2018 (the
full shear, whatever its direction relative to the welded faces).

| Case | f_a | f_b | f_v | f_n | f_r, lb/in | Fiber | Weld | Baseplate | Wall, normal | Wall, shear | Check ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Downward, concentrated | 257.8/5.072 = 50.82 | | | 50.82 | 50.82 | uniform | 0.01826 | 0.005842 | 0.01591 | | 0.01826 |
| Downward, distributed | 357.8/5.072 = 70.54 | | | 70.54 | 70.54 | uniform | 0.02534 | 0.008108 | 0.02208 | | 0.02534 |
| Outward, concentrated | 11.39 | 8300/5.072 = 1636 | 39.43 | 1648 | 1648 | compression side | 0.5921 | 0.1895 | 0.5157 | 0.01954 | 0.5921 |
| Outward, distributed | 11.39 | 12,450/5.072 = 2455 | 59.15 | 2466 | 2467 | compression side | 0.8861 | 0.2835 | 0.7718 | 0.02930 | 0.8861 |
| Inward, concentrated | 11.39 | 1636 | 39.43 | 1648 | 1648 | compression side | 0.5921 | 0.1895 | 0.5157 | 0.01954 | 0.5921 |
| Inward, distributed | 11.39 | 2455 | 59.15 | 2466 | 2467 | compression side | 0.8861 | 0.2835 | 0.7718 | 0.02930 | 0.8861 |
| Longitudinal, concentrated | 11.39 | 8300/2.144 = 3872 | 39.43 | 3883 | 3883 | compression side | 1.395 | 0.4464 | 1.215 | 0.01954 | 1.395 **NG** |
| Longitudinal, distributed | 11.39 | 12,450/2.144 = 5808 | 59.15 | 5819 | 5819 | compression side | **2.090** | 0.6689 | 1.821 | 0.02930 | 2.090 **NG** |
| Upward, concentrated | 165.3/5.072 = 32.60 | | | 32.60 | 32.60 | uniform | 0.01171 | 0.003747 | 0.01020 | | 0.01171 |
| Upward, distributed | 265.3/5.072 = 52.31 | | | 52.31 | 52.31 | uniform | 0.01879 | 0.006013 | 0.01637 | | 0.01879 |

Tension side of bending, for the record: f_n = f_b − f_a (longitudinal,
distributed: 5796 lb/in, 1.814 against the 3195 lb/in yielding limit, which
is also the lower limit in tension). The compression side is larger in every
lateral case, so it governs both the weld and the wall.

**Controls: longitudinal, distributed, 2.090, NG** (weld metal; the post
wall's normal-force line is also NG at 1.821). Expected by S6-17 item 9: the
longitudinal moment bends two 2.536 in lines about their own mid-length.
The transverse cases pass at 0.8861.

## 13. Reactions (LRFD, at the top of concrete)

0.9D + 1.6L, engineering judgement; arm h = 42 in; D includes the
baseplate.

| Symbol | Equation | Substitution | Result |
| --- | --- | --- | --- |
| D | D_rail + D_int + D_post + W_bp | 28.50 + 15.78 + 13.4875 + 6.806 | 64.57 lb |
| governing load type | larger of P and w·s | 200 < 300 | distributed |
| Lateral: V | 1.6·w·s | 1.6 × 300 | 480.0 lb |
| Lateral: N | 0.9·D, compression | 0.9 × 64.57 | −58.12 lb (compression) |
| Lateral: M | V·h | 480 × 42 | 20,160 lb-in |
| Upward: N | 1.6·w·s − 0.9·D, tension (1.6L = 480 > 0.9D = 58.12) | 480 − 58.12 | +421.9 lb (tension) |
| Upward: V, M | | | 0, 0 |

## 14. Summary

| Check | Controlling case | Ratio | |
| --- | --- | --- | --- |
| 1 Top rail bending | outward (= inward), concentrated | 0.1416 | OK |
| 2 Top rail deflection | outward (= inward), concentrated | 0.09953 | OK |
| 3 Top rail weld to post | longitudinal, distributed (weld metal) | 0.05935 | OK |
| 4a Intermediate rail | downward, deflection | 0.1096 | OK |
| 4b Intermediate rail weld | downward, component (weld metal) | 0.006239 | OK |
| 5 Post axial and flexure | outward (= inward), distributed, Eq. H1-1b | 0.5651 | OK |
| 6 Post deflection | outward (= inward), distributed | 0.5149 | OK |
| 7 Post weld to baseplate | longitudinal, distributed (weld metal) | 2.090 | NG |

## 15. Values from my own reading

No verified registry entry was read. Each value below is mine.

| Value | Used | Document, section | Source |
| --- | --- | --- | --- |
| E = 29,000 ksi | all | AISC 360-22 Table B4.1a note, page 16.1-21 | PDF |
| Fy = 46 ksi, Fu = 58 ksi, A500 Gr B rectangular HSS | all members | AISC Manual, 16th Ed., Table 2-4 | memory. I am confident of 46/58 for shaped A500 Gr B in the 15th Edition table and believe the 16th is unchanged; I have not seen the 16th Edition page. The brief also drafts 46/58 (S6-17 item 1). |
| Fu = 58 ksi, A36 plate | baseplate | AISC Manual, 16th Ed., Table 2-5 | memory |
| FEXX = 70 ksi | welds | E70XX classification | memory |
| P = 200 lb, any direction, at any point on the top rail | guard | ASCE 7-22 §4.5.1 | memory |
| w = 50 lb/ft | guard | ASCE 7-22 §4.5.1.1 | memory |
| P_c = 50 lb | component | ASCE 7-22 §4.5.1.2 | memory |
| ASD D + L | combinations | ASCE 7-22 §2.4.1 | memory |
| Steel unit weight 490 lb/ft³ | baseplate weight | AISC Manual, 16th Ed., Part 17 | memory |
| K = 2.1, fixed-free | post | AISC 360-22 Commentary Table C-A-7.1, page 16.1-650; the brief's ruling D3 | PDF (table located; value from memory, the brief agrees) |
| Ω_b = 1.67 | flexure | §F1(a), page 16.1-52 | PDF |
| Ω_c = 1.67 | compression | §E1, page 16.1-39 | memory of the text on the cited page |
| Ω_t = 1.67 | tension yielding | §D2(a), page 16.1-32 | PDF |
| λp = 1.12√(E/Fy), λr = 1.40√(E/Fy), flanges of rectangular HSS | classification | Table B4.1b Case 17, page 16.1-23 | PDF |
| λp = 2.42√(E/Fy), λr = 5.70√(E/Fy), webs of rectangular HSS | classification | Table B4.1b Case 19, page 16.1-23 | PDF |
| λr = 1.40√(E/Fy), walls of rectangular HSS in compression | classification | Table B4.1a Case 6, page 16.1-21 | PDF |
| Eqs. F7-1, F7-2, F7-8, F7-10, F7-11 | flexure | §F7, pages 16.1-63 and 16.1-64 | PDF |
| No LTB for minor-axis bending | flexure | User Note to §F7.4, page 16.1-65 | PDF |
| Eq. F1-1; Cb = 1.0 for a cantilever with the free end unbraced | flexure | §F1(c), page 16.1-52 | PDF |
| Eqs. E3-1, E3-2, E3-4; the 4.71√(E/Fy) limit | compression | §E3, pages 16.1-40 and 16.1-41 | PDF |
| Eq. D2-1 | tension | §D2, page 16.1-32 | PDF |
| Eqs. H1-1a, H1-1b | interaction | §H1.1, page 16.1-82 | PDF |
| Pe = π²EI/Lc² | second-order ratio | Appendix 8, Eq. A-8-5, page 16.1-284, with the brief's Lc = K·h and EI (D1) | PDF |
| α = 1.6 (ASD) | second-order ratio | Appendix 8, §8.1 | memory |
| Fnw = 0.60·FEXX, Ω = 2.00, fillet weld shear | welds | Table J2.5, page 16.1-132; Eq. J2-4, page 16.1-130 | PDF |
| k_ds = 1.0 | welds | §J2.4(a)(2) and (3), page 16.1-130; User Note to §K5, page 16.1-170 | PDF |
| Throat = 0.707·w | welds | §J2.2a, page 16.1-126; the form is the brief's (welds.md, "Effective throat") | PDF, brief |
| Minimum fillet 1/8 in for a thinner part to 1/4 in | welds | Table J2.4, page 16.1-128 | PDF |
| Eq. K1-1 | Checks 3, 4b | §K1.2a, page 16.1-159 | PDF |
| Eqs. K5-5, K5-6, K5-7 and the cap "Be/2 shall not exceed Bb/4 when β > 0.85 or θ > 50°" | Checks 3, 4b | Table K5.1, page 16.1-171 | PDF |
| B/t and H/t ≤ 35; Fy ≤ 52 ksi; Fy/Fu ≤ 0.8 | Check 3 limits | §K1.3, page 16.1-160; Table K4.2A, page 16.1-170 | PDF |
| Rn = 0.60·Fu·Anv, Ω = 2.00 | base metal | Eq. J4-4, §J4.2(b), page 16.1-146 | PDF |
| Rn = Fy·Ag, Ω = 1.67; Rn = Fu·Ae, Ω = 2.00 | post wall at the face-pair weld | Eqs. J4-1 and J4-2, §J4.1, page 16.1-145 | PDF |
| Deflection limits L/120 and (h − t_p)/60 | Checks 2, 4a, 6 | the case inputs; engineering judgement per the brief | inputs |

## 16. Open questions and findings for Micah

1. **A horizontal load at an angle to the rail governs Check 5 on a
   rectangular post.** ASCE 7-22 §4.5.1 applies the guard load in any
   direction. S6-14 item 2 gives the post one moment per case and no biaxial
   case, expecting no change to what governs. For this post it is not small.
   A horizontal load V at angle θ from transverse gives Mry = V·cos θ·41.5
   and Mrx = V·sin θ·41.5; Eq. H1-1b is linear in the two, so the worst
   angle is tan θ = Mcy/Mcx (37.1° here) and the ratio is
   12,450 × √(1/22,120² + 1/29,200²) + 0.0022 = 0.708, against 0.5651 for
   the worst orthogonal case: 25% higher. The same load on the face-pair
   base weld loads a line's end with both bending components: f_b =
   12,450 × √(1/5.072² + 1/2.144²) = 6305 lb/in, weld ratio about 2.27
   against 2.090. Not computed as a check and not in the values file; the
   plan has no such case. Your call whether the rectangular post needs a
   skew case or a printed assumption.
2. **The same point for the rail, already ruled.** A load inclined between
   downward and outward bends both rail axes with the live load. Worst
   inclination 30.1° from horizontal: 3600 × √(1/26,480² + 1/45,720²) +
   0.0056 = 0.163 against 0.1416, 15% higher. S6-14 records an inclined
   case for rectangular rails as not chosen; I give the number only so the
   ruling has one for this section.
3. **Tension rupture and shear lag at a face-pair weld.** The brief rules
   out a tension-rupture check on the post because a post welded all around
   has U = 1.0. With two faces welded the upward tension enters through two
   walls and U is less than 1. Here it cannot matter (upward Pr/Pt = 0.009,
   and the wall's normal-force line already checks the welded walls against
   rupture, 0.016), but the brief's stated reason does not cover the face
   pair.
4. **The Specification text was read as extracted text only.** No page
   images could be rendered in this session. Radicals, Greek letters and
   inequality signs are lost in the extraction (Eqs. F7-2, F7-8, F7-10,
   F7-11, K1-1, K5-5 to K5-7, E3-2, E3-4, and the cap in Table K5.1), so
   those forms are from my memory of the Specification, checked against the
   terms that survive on each cited page. Worth a look at the page for
   Eqs. K5-6 and K5-7 in particular: Check 3 is on your recompute list.
5. **Material values.** Fy = 46 and Fu = 58 ksi for A500 Gr B rectangular
   are from memory of AISC Manual Table 2-4; I assumed the 16th Edition and
   have not seen that page. Every check here turns on them.
6. **Check 3 at H/t = 34.48.** The rail is within 1.5% of the Chapter K
   limit of 35 on the outside dimension and design wall. On the published
   h/t = 31.5 it is well inside. S6-13 says outside dimension; I used that.
7. **Table K5.1 at β = 1.** Eq. K1-1 gives Be = 1.16 in and the cap
   (β > 0.85) brings it to Bb/2 = 1.0 in at both rectangular joints, so
   neither joint here tests an uncapped Be. Known gap in the plan.
8. **Rail chord wall, for scale only** (not checked, S6-12). Sidewall local
   yielding under the out-of-plane moment, Eq. K4-6 as I read it on page
   16.1-169: Mn-op = Fy·t·(B − t)·(Hb + 5t) = 46 × 0.116 × 1.884 × 3.58 =
   36.0 kip-in, 24.0 kip-in allowable at Ω = 1.50, against V·e = 0.6
   kip-in: about 0.025. Informational; it supports the assumption.
9. **Local effect of the concentrated load on the rail wall away from the
   post** is not checked anywhere (plan open item 5).
10. **Model id.** The skill asks for the model id in this header and in
    `[provenance]`. This session is under an instruction not to write a
    model identifier into anything pushed to a repository, so both say
    where to find it instead. It is in the session report.

**Mapping (step 7).** Every key in the values template has a value; none
could not be filled. Computed here with no key: the rail's longitudinal
(dead-load-only) bending ratio; the tension-side wall ratio at the base
weld; Mn,y of the rail by Eq. F7-2 (it is in the file only through Mcy);
the Chapter K limit ratios of Check 3; and items 1, 2 and 8 above.

Text keys: ties between outward and inward are recorded as "outward", the
first in the file's key order. `check7.wall_axial_allow_lbpin` is the lower
of yielding and rupture (yielding, 3195 lb/in). `check7.ratio_base` is the
resultant against the baseplate's shear rupture. `t_min_in` is the thinner
part's nominal thickness read into Table J2.4, and `w_min_in` its minimum
fillet. `check3.S_w_t_in2` is S_op per unit throat and `S_w_l_in2` is S_ip
per unit throat. `reactions.lateral.N_lb` is signed, compression negative,
as the template's header says.

## 17. Review checklist (docs/brief/verification.md)

1. **Loads complete.** Top rail, intermediate rail and post dead load are
   carried to the post (57.77 lb); the baseplate is added for the reactions
   only (64.57 lb). Check 3 uses the rail's dead load alone, as the brief
   rules. Both guard load types run in every check; the component load runs
   in Checks 4a and 4b, horizontal and downward.
2. **Direction and worst case.** All five direction cases for each load
   type are computed where the check has them (the rail has no longitudinal
   bending case; Check 6 has no vertical case). The worst case of each
   check is found by calculation. Item 1 of section 16 is a direction the
   envelope does not contain.
3. **Checks complete.** Section 3 lists every limit state considered. Not
   in the plan and flagged: the skew horizontal load on the post, tension
   rupture at a face-pair weld, the concentrated load's local effect.
4. **Geometry.** h = 42 in for Lc and the reactions; h − t_p = 41.5 in for
   the post moment, Check 6 and the Check 7 arm; e = 2 in (half the 4 in
   rail depth); flats of 3 − 4 × 0.116 = 2.536 in at ±1.0 in; Hb = 3 in
   along the rail and Bb = 2 in across it at Check 3; Hb = 1.5 in and
   Bb = 2 in at Check 4b.
5. **Method and equations.** Classification done for each bent axis before
   capacity: the rail's weak axis has a noncompact flange (Eq. F7-2); all
   else compact and nonslender. LTB branch evaluated for each strong-axis
   case (rail and intermediate rail: Eq. F7-8, capped at Mp by Cb; post:
   Lb < Lp). Eq. E3-2 by Lc/r = 109.7 ≤ 118.3. H1-1b by Pr/Pc = 0.0044 <
   0.2. Table K5.1's cap applied at β = 1.
6. **Assumptions.** Post fixed at the top of the baseplate; K = 2.1 on h;
   simple-span rails; span as tributary length; no bearing credit at either
   weld; simple shear connection at Check 4b; loads through member
   centerlines. All are the brief's.
7. **Code editions.** AISC 360-22 throughout, cited by section and page of
   out/aisc-360-22.pdf. ASCE 7-22. AISC Manual 16th Edition assumed for
   Tables 2-4 and 2-5, from memory (section 16, item 5).
8. **Magnitude sense.** Rail ratios 0.06 to 0.14 for a 4 × 2 tube on a 6 ft
   span; post 0.57 in bending and 0.51 in deflection for a 3 × 2 × 1/8 tube
   at 42 in under 300 lb, bent the weak way; weld forces of tens of lb/in at
   the rail and thousands at the base. Units are consistent (lb, in, ksi
   converted to lb where ratios are formed).
9. **Governing case.** Checks 1 and 2: horizontal load on the rail's weak
   axis, as expected for a rail on edge. Checks 5 and 6: transverse, the
   post's weak axis, under w·s = 300 lb. Check 3: longitudinal, because
   S_ip (6.00 in²) is less than S_op (7.17 in²) at this joint. Check 7:
   longitudinal and NG, as S6-17 item 9 expects of a face pair bent about
   the lines' own length.
