# Slice 3 plan: the welds (Checks 3 and 7), pipe rail on pipe post

Status: **planned, not started.** Decisions settled with Micah on
2026-10-04 and 2026-10-08. Branch `slice-3`.

> The binding engineering decisions (W1–W12) are already in the brief:
> docs/brief/welds.md ("Engineering decisions already made") and the weld,
> electrode and baseplate grade inputs in docs/brief/inputs.md. Where this
> plan and the brief differ, the brief governs. This plan holds the build
> order, the tests, and the case-specific numbers each decision was worked
> from.

## Goal

Add Check 3 (top rail weld to post) and Check 7 (post weld to baseplate)
for a pipe rail on a pipe post, both welded all around with fillet welds,
run over the full envelope and printed in a PDF Micah can backcheck. The
weld method is built once and used by both checks. The section layer stays
at pipe. Checks 1, 2, 5 and 6 are unchanged, and test cases 1–3 must pass
exactly as they do today.

## Decisions settled for this slice

W1–W12 are in docs/brief/welds.md, with W12's inputs in
docs/brief/inputs.md. In short:

| No. | Decision |
| --- | --- |
| W1 | Check 3 weld is a flat ring of the post perimeter at the rail's underside; e = D_rail/2. Stated assumption. |
| W2 | §J2.4 directional increase applies to round HSS welds (Check 7); Check 3 uses k_ds = 1.0; non-round sections stop. |
| W3 | Elastic weld-as-a-line, S_w = πD²/4, uniform shear V/(πD), vector sum at the governing point, θ printed. |
| W4 | Fusion face thickness: t_des for rail and post, t_p as entered for the baseplate. |
| W5 | Base metal limit state follows the force direction at each fusion face; the post wall is covered by Check 5, with an Fu/Fy ≥ 1.20 grade guard. |
| W6 | Rail fusion face: shear rupture only, §J4.2(b), per Manual Part 9. |
| W7 | Rail wall Chapter K chord limit states not checked; stated assumption; non-round rail or post stops. |
| W8 | Post OD > rail OD stops at input validation. |
| W9 | Fillet model all around at equal diameters; flare-bevel sentence added to the W1 assumption. |
| W10 | No bearing credit at either weld; both extreme fibers evaluated; the envelope table. |
| W11 | Minimum size (Table J2.4) is pass/fail; no maximum size check and no warning; a printed line says §J2.2b(b) does not apply. |
| W12 | Weld sizes required; E70XX only; baseplate grade input, A36 only for all of v1; Fu for A53 Gr B and A36. |

Two test decisions are not tool behavior and stay here:

**T1. Case 3 tests the compute step, and the W8 stop.** Case 3 (Pipe2STD
post under a Pipe1-1/2STD rail) now fails W8. `checks.run()` is split into
a validate step (geometry checks across members, including W8) and a
compute step; the CLI calls both, in that order. Case 3's value test calls
only the compute step, and a new test asserts that the full case 3 file
stops with the W8 message. Case 3's existing inputs and recorded values
stay untouched; it gains only the two weld sizes (T2). The split is a test
seam (an entry point that exists so a test can reach code past a guard);
the only thing it skips is the validation itself. Not chosen: changing
case 3's rail to Pipe2STD, which changes D at the post and so every Check
5 value, and would need a fresh independent calc and Micah's review; and
testing the post functions outside `run()`, which can drift from how
`run()` builds loading. (Micah, 2026-10-08.)

**T2. Test case 4, and weld inputs for cases 1–3.** Case 4 is case 2's
inputs (Pipe1-1/2STD rail on a Pipe1-1/2STD post, A53 Gr B, 7'-0" span,
h = 42 in, t_p = 1/2 in, default loads, no exemption) plus
`rail_to_post = 1/8"` and `post_to_baseplate = 1/4"`, E70XX, A36
baseplate. It covers Checks 3 and 7 only and gets a fresh independent
calc. Cases 1–3 gain the same two weld sizes as input-only additions (as
slice 2's D9 added post inputs) and record no weld values. Extending case
2 instead would mean redoing its whole independent calc. (Micah,
2026-10-08.)

Rough figures for case 4, from planning arithmetic (Claude, not test
values; rule 5): the governing horizontal load is the distributed one,
w·s = 350 lb.

- Check 7: M = 350 × 41.5 = 14,525 lb-in; S_w = π(1.900)²/4 = 2.835 in²;
  f ≈ 5.13 kip/in; 1/4" E70 with k_ds = 1.5 gives
  0.6·70·0.707·0.25·1.5/2.00 = 5.57 kip/in, about 0.92. Weld metal
  governs (baseplate fusion face 0.6·58·0.5/2.00 = 8.7 kip/in).
- Check 3: M = 350 × 0.95 = 332.5 lb-in; f_n ≈ 117 + 3 lb/in, f_v ≈ 59
  lb/in, resultant about 134 lb/in; 1/8" with k_ds = 1.0 gives 1.86
  kip/in, about 0.07. Rail fusion face: 59 lb/in against 2.43 kip/in.

Case 4 reaches both k_ds branches (1.0 in Check 3, 1.5 in Check 7) and
sits exactly at the minimum size in Check 3. Case 2's post fails Check 5
in the distributed case, so case 4's package prints NG for Check 5; that
does not matter to a test case.

## What the slice does

### Input

The project file gains (bare numbers are inches):

- `[welds]`: `rail_to_post` and `post_to_baseplate`, required dimensions
  with no default; `electrode`, default "E70XX", the only value accepted.
- `[baseplate]`: `grade`, default "A36", the only value accepted.
- Validation step: post OD ≤ rail OD (W8); rail and post round hollow
  (W7); post grade Fu/Fy ≥ 1.20 (W5). Each stop names what it checked and
  why.

The dimensions page echoes both weld sizes as entered and normalized.

### Engineering

One weld-ring module serves both checks. For a ring of diameter D (the
post OD) and fillet size w:

- L_w = πD, S_w = πD²/4, throat 0.707w.
- Per case: f_v = V/L_w (uniform), f_a = P/L_w (axial, signed), f_b = M/S_w.
  At each extreme fiber, f_n = f_a ± f_b; f_r = √(f_n² + f_v²). The larger
  of the two governs, and the calc names it (W10).
- θ at the governing point between f_r and the weld axis, printed;
  k_ds = 1.0 + 0.50 sin^1.5 θ for Check 7, 1.0 for Check 3 (W2).
- Weld metal: R_n/Ω = 0.60·FEXX·k_ds·(0.707w)/2.00 per inch.
- Base metal: Check 3 rail side, f_v against 0.6·Fu·t_des/2.00 (W6);
  Check 7 baseplate side, f_r against 0.6·Fu·t_p/2.00 (W5). Post side of
  both: the printed "covered by Check 5" line (W5).
- Minimum size per Table J2.4 on the thinner part joined, pass/fail; the
  §J2.2b(b) "not applicable" line (W11).
- The check ratio is the larger of the weld metal and base metal ratios;
  a minimum-size failure makes the check NG whatever the ratio.

Envelope (W10): downward, outward, inward, longitudinal, upward, each for
both guard load types. Check 3 uses D = w_D,rail·s and e = D_rail/2; Check
7 uses D at the post and the arm h − t_p. Upward uses 0.6D + 1.0L and shows
"no net tension" when 0.6D ≥ L.

### Output (PDF)

- Front matter: the W1 (with W9) and W7 assumptions, added to output.md's
  list in the same commit that prints them.
- Checks 3 and 7 pages, in check-number order: weld properties, an envelope table (case, f_n, f_v, f_r,
  θ and k_ds for Check 7, capacity per inch, ratio), then the full calc
  lines for the controlling case, ending with the ratio and OK or NG.
- Summary table rows for Checks 3 and 7.

Layout details (column order, line wording beyond the decisions) are
Claude's to propose on the branch and Micah's to accept in the PR review.

## Registry entries this slice will draft

About 20, against the roadmap's estimate of 15. Citations from memory, to
be verified at the release review (#18):

- AISC 360-22 §J2.4: fillet weld strength R_n = F_nw·A_we; F_nw =
  0.60·F_EXX coefficient; Ω = 2.00
- §J2.4 directional increase equation and its coefficients (0.50, 1.5)
- §J2.2a: effective throat of an equal-leg fillet
- Table J2.4: minimum fillet sizes
- §J2.2b(b): maximum size along edges (provision text, for the
  not-applicable line)
- §J4.2(b): shear rupture, Eq. J4-4, and Ω = 2.00
- AISC Manual Part 9: base metal at welds, rupture convention (W6)
- Manual Table 2-4: Fu for A53 Gr B; Table 2-5: Fu for A36
- E70XX: F_EXX = 70 ksi
- Engineering judgement or non-primary (source "engineer" or the URL):
  the ring model and e (W1); the directional increase on round HSS, STI
  source (W2); k_ds = 1.0 for the branch-to-chord weld (W2); the elastic
  line method with uniform shear (W3); no bearing credit (W10); the post
  wall covered by Check 5 with the Fu/Fy ≥ 1.20 condition (W5)
- Note broadened, no printed change: `ej.combo.bending.upward` (also the
  welds' upward case)

## Tests

- **Test case 4** (independent-calc case): every weld value the tool
  prints for both checks: L_w, S_w, throat, per case f_a, f_b, f_v, f_n,
  f_r, governing fiber, θ and k_ds (Check 7), capacities per inch, ratio;
  the minimum size line; the controlling case of each check. Micah's
  [hand] values are "deferred" to the release review (ADR 0006).
- **Cases 1–3:** weld inputs added, no weld values recorded, every
  existing value unchanged. A changed value is a rule 2 stop.
- **Case 3 (T1):** values tested through the compute step; the full file
  stops with the W8 message.
- **Machinery tests** (same-author, like F8-2 in slice 1): a weld below
  the minimum size is NG; upward with no net tension shows the status; a
  non-E70XX electrode and a non-A36 baseplate stop; the non-round guard
  (W7), the rectangular k_ds stop (W2) and the Fu/Fy guard (W5), each with
  a stand-in section or grade; θ = 90° gives k_ds = 1.5.

## Build order

Each step is committed and pushed when its tests pass.

1. **Issue #4 cleanup:** items 4–7 (one input-error base class; defaults
   stated once; SCHEMA and parser test; table stroke parameter), the
   PR #17 registry items (broaden the `ej.combo.bending.upward` note;
   equation entries that restate their formula), and the harness's
   unconditional P_t read. All tests pass unchanged.
2. **Validate/compute split (T1)**, no output change.
3. **Project file:** `[welds]`, `[baseplate]`, validation (W7, W8, W5
   guard, W12); weld inputs added to cases 1–3 and the example; the case 3
   stop test.
4. **Registry entries** drafted; review list updated.
5. **Weld ring module** (W3, W10, W2, W11), with the machinery tests.
6. **Check 3.**
7. **Check 7.**
8. **Report:** assumptions into output.md and the front matter, the
   dimensions page, the Check 3 and 7 pages, summary rows.
9. **Test case 4** wired in, values pending; independent template
   created.
10. **Independent calc for case 4,** in a fresh session by the
    independent-calc skill. This planning session has read src/, so it
    must not write it (rule 6).
11. **Micah's review** of the independent calc and the PDF against the
    checklist. His governing-case recompute is deferred (#18).
12. **Pull request** to main, with the calc-code-review skill run first.

## What Micah does

- Review the case 4 independent calc and the slice PDF against the
  checklist in docs/brief/verification.md, and approve the pull request.
- At the release review: verify this slice's drafted entries and
  recompute case 4's printed controlling cases of Checks 3 and 7.

## Done when

- `uv run handrail calc examples/slice-1.toml` prints Checks 1, 2, 3, 5, 6
  and 7.
- All tests pass, cases 1–4 at 0.5%, with no pending value in case 4.
- Micah has reviewed the case 4 independent calc and the PDF.

## Not in slice 3

- Check 4, the intermediate rail, reaction sets, baseplate B × N
- Rail wall chord limit states (W7), baseplate bending (D12)
- Maximum fillet size, flare-bevel throats, plastic weld distribution
- Electrodes other than E70XX; baseplate grades other than A36 (all of v1)
- Non-round sections, posts wider than the rail
