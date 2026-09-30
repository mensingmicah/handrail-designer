# Slice 1 plan: top rail bending and deflection, AISC pipe

Status: **completed.** Merged to main in PR #2 and released as v0.1.0
(see CHANGELOG.md).

> This plan is history, not current guidance. It records what slice 1 set
> out to build and why. Where it differs from docs/BRIEF.md, CLAUDE.md or
> later plans, those govern.

## Goal

The smallest case that goes all the way from inputs to a printed calc Micah
can backcheck by hand: Checks 1 and 2 (top rail bending and top rail
deflection) for an AISC pipe top rail in A53 Gr B, over the full envelope.
The slice is thin in engineering but runs through every layer the full tool
needs: project file, dimension parser, section data, code-value registry,
calc lines, envelope, PDF, and the hand-calc test. Every later slice adds
checks and shapes to layers that already work.

## Decisions settled for this slice

**D1. Equations have registry entries.** Every formula or equation the tool
uses carries a registry entry with its reference, the same as any other code
reference: document, edition, exact equation or table, source and status.
That applies to AISC 360-22 equations (Eq. F8-1, for example) and equally to
the beam formulas, which cite AISC Manual Table 3-23. The equation itself is
implemented once in Python as a calc-line definition (ADR 0002), and the
calc line prints the registry citation. Equation entries appear in the
review list and trigger the DRAFT stamp like any other entry. The hand-calc
tests check that each equation is implemented correctly.

**D2. Every direction case is computed and shown; only the controlling
case prints in full.** In both checks, every direction case in the envelope,
upward included, is computed and listed in the check's envelope table with
its demand, capacity and ratio. Only the controlling case gets the full calc
lines. Upward-case deflection is live load only; it is expected not to
control, but it is computed and shown like every other case.

## What the slice does

### Input

A TOML project file that Micah edits by hand. Its header comment states
that loading is per ASCE 7-22; the input form will carry the same note when
it is built. One command produces the PDF:

```
uv run handrail calc examples/slice-1.toml
```

There is no form (deferred, per P9). The project file holds only what this
slice uses; later slices add fields:

- Project info: name, phase, one-line description, reference documents,
  added assumptions
- Span, in any accepted dimension form (bare number = inches)
- Top rail: AISC pipe designation, grade (A53 Gr B only)
- Guard loads: optional overrides; the defaults come from the registry
- Distributed-load exemption: flag plus the engineer's statement text
- Rail deflection limit (default L/120) and its bypass flag

### Engineering

- **Section properties** come from the AISC database as published: D, t_des,
  A, W, I, S, Z, D/t. The rail dead load w_D is the tabulated W.
- **Classification** (AISC 360-22 Table B4.1b, round HSS in flexure): D/t
  against λp and λr, and the §F8 applicability limit. Slender or beyond the
  §F8 limit is a hard stop that names the ratio and the limit. Noncompact
  computes the §F8 local buckling strength and is flagged. Pipe is designed
  under the round HSS provisions; the registry records the basis for that.
- **Flexure (Check 1)**: Mn per §F8, allowable Mn/Ωb. There is no LTB for
  round sections, so no Cb is needed in this slice.
- **Envelope**: the concentrated load P at midspan (M = PL/4) and the
  distributed load w (M = wL²/8) are separate, non-concurrent load types.
  The exemption flag removes the distributed load. The direction cases:
  - Downward: D + L on the vertical axis
  - Outward and inward: dead load on the vertical axis and live load on the
    horizontal axis, combined by SRSS. Both are listed even though they are
    identical for a round section, so the envelope is explicit.
  - Upward: 0.6D + 1.0L, net on the vertical axis, labeled "engineering
    judgement"
  - Longitudinal: listed as "rail carries axially; not checked"
- **Deflection (Check 2)**: simple-span formulas. Downward is D + L. Outward
  and inward are live only. Upward is live only (D2), shown as not
  controlling. The limit is L/120 unless edited, and "Bypassed by engineer"
  when bypassed.
- **What is and isn't a registry entry**: the beam formulas (PL/4, wL²/8,
  PL³/48EI, 5wL⁴/384EI) are registry entries citing AISC Manual Table 3-23
  (D1). Engineering-judgement formulas are registry entries too, with
  source "engineer" and status drafted (Micah's ruling on the PR #2
  review, which resolves the conflict between this bullet and CLAUDE.md
  rule 1): SRSS for round sections, the upward 0.6D + 1.0L combination,
  the deflection D + L and live-only combinations, and Δ_allow = L/ratio.
  Combination labels are generated from the same factors the expressions
  use. The deflection D + L is labeled engineering judgement
  (serviceability, not an ASD strength combination). The default ratio
  (120) stays an input default, not a code value.

### Output (PDF)

- A "DEVELOPMENT — NOT FOR CONSTRUCTION" watermark on every page
- The "DRAFT: contains unverified code values" stamp on every page, with a
  list of the drafted entries used. Every entry starts as drafted, so the
  stamp will be present until Micah verifies them all. The list prints once,
  in the front matter, and the stamp on every page points to it (confirmed
  by Micah on the PR #2 review).
- A reserved, empty header area. The footer shows the tool version (git
  commit), the registry version (git commit of the registry file) and
  "page x of y". If the code or the registry has uncommitted changes when
  the calc runs, the footer prints "uncommitted changes" next to the
  affected commit ID, so a printed calc can always be traced to exact code.
- Front matter: project info; the locked assumptions, plus any added; the
  references (AISC 360-22, ASCE 7-22, AISC Manual 16th Ed., AISC Shapes
  Database v16.0); an image-area placeholder (image upload is a later slice)
- Dimensions page: each dimension as entered and normalized (for example
  "72 → 6'-0"")
- Section properties page
- Loading page: guard loads with citations, the exemption statement if
  used, and the dead load
- Checks 1 and 2: each opens with the envelope summary table (every case,
  with its demand, capacity and ratio), then the full calc lines for the
  controlling case (symbol, expression, substituted values, result, unit,
  citation, margin note), ending with the ratio and OK or NG
- Summary table: Checks 1 and 2 only, with demand, capacity, ratio,
  controlling direction and OK / NG / "Bypassed by engineer"
- No reactions, and no Checks 3–7

## Registry entries this slice will draft

These are added as drafted entries, each with an exact citation and source,
and listed in the review list. A value read from a table cites the table
(Fy from AISC Manual Table 2-4, beam formulas from Table 3-23 by case
number):

- ASCE 7-22 guard concentrated load and uniform load (values and sections)
- ASCE 7-22 §2.4 ASD combination used for D + L
- A53 Gr B Fy (AISC Manual Table 2-4)
- Ωb (AISC 360-22 §F1)
- Table B4.1b round HSS in flexure: λp and λr
- §F8 applicability limit on D/t
- §F8 yielding and local buckling equations
- Beam formulas for the simple span: midspan moment and midspan deflection
  under a concentrated load at midspan and under a uniform load (AISC Manual
  Table 3-23, with case numbers)
- The basis for designing pipe as round HSS
- Already drafted: steel density, E, the pipe grade list, and the four
  exemption text entries

## Tests

- **Test case 1 (Micah's hand calc)**: Micah picks the pipe size and span
  and records his hand values in `tests/cases/case-01.toml`. The values to
  record:
  - w_D and the section properties used
  - M for each envelope case, Mn, Mn/Ωb, and each ratio
  - Δ for each envelope case, Δ_allow, and each ratio
  - the controlling direction for each check

  Every value must fall within 0.5% relative of the tool's value. A mismatch
  stops the work under rule 2 until we know which side is wrong.
- **Dimension parser**: every form in the brief (5' 6-1/8", 66.125 in,
  3 ft 6 in, 42), plus malformed input that must be rejected with a clear
  message
- **Database extraction**: the extracted pipe rows match the original
  `.xlsx` row for row
- **Registry**:
  - the review list matches exactly the set of drafted entries
  - a missing entry is a hard stop naming the entry
  - a calc using a drafted entry carries the DRAFT stamp and list
- **Classification**: a slender or out-of-range D/t is a hard stop
- **Eq. F8-2 is tested for machinery only.** Test case 1 is compact, so no
  hand calc covers the noncompact branch (Eq. F8-2 and the min(Mp, Mn,LB)
  step of §F8). `tests/test_checks.py` checks it against a plain-arithmetic
  rewrite by the same author, which proves the calc-line machinery but not
  the equation: a wrong coefficient in both would pass. A noncompact hand
  case is added when thin-wall round HSS arrives (GitHub issue #3; Micah's
  ruling on the PR #2 review).
- **Units**: an attempt to mix incompatible units raises an error

## Build order

Each step is committed and pushed when its tests pass.

1. **Environment.** Install uv, create the project, and add pint, typst and
   pytest. First confirm that the typst Python package compiles a PDF on
   this machine; if it doesn't, stop and report before going further.
2. **Dimension parser** and its tests.
3. **Database extraction script** (PIPE rows into a derived TOML file under
   `data/`, headed as generated), its test, and an update to
   `data/README.md`.
4. **Registry loader**: the review-list check, the missing-entry hard stop,
   and the drafted-entry tracking. Draft the slice's entries.
5. **Calc-line machinery** (ADR 0002) with pint.
6. **Checks 1 and 2 with the envelope**, and the classification hard stops.
7. **Typst template and renderer**: layout, watermark, DRAFT stamp, header,
   footer, envelope tables, summary table.
8. **Command-line entry point** and `examples/slice-1.toml`.
9. **Test case 1** wired in, using Micah's hand values.

## What Micah does

- Choose the pipe size and span for test case 1, and do the hand calc.
- Review the registry review list in one pass after the slice is complete,
  starting with exemption 2. The build proceeds with drafted entries,
  because every PDF carries the DRAFT stamp.
- Backcheck the slice PDF.

## Done when

- `uv run handrail calc examples/slice-1.toml` produces the PDF described
  above
- All tests pass, including test case 1 against Micah's hand calc at 0.5%
- Micah has backchecked the PDF and agrees with it

## Not in slice 1

- The input form
- Round and rectangular HSS, bars and custom sections
- Checks 3–7, the intermediate rail, the post, welds and reactions
- The image in the front matter
- Baseplate inputs
- Display-unit settings (issue #1)
