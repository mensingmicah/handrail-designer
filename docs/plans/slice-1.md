# Slice 1 plan: top rail bending and deflection, AISC pipe

Status: **proposed, awaiting Micah's approval. Nothing is built.**

## Goal

The smallest case that goes all the way from inputs to a printed calc Micah
can backcheck by hand: Checks 1 and 2 (top rail bending and top rail
deflection) for an AISC pipe top rail in A53 Gr B, over the full envelope.
The slice is thin in engineering but runs through every layer the full tool
needs: project file, dimension parser, section data, code-value registry,
calc lines, envelope, PDF, and the hand-calc test. Every later slice adds
checks and shapes to layers that already work.

## Two decisions needed before building

**D1. How code equations relate to the registry.** Rule 1 puts code values
and provision text in the registry. Code *equations* (AISC 360-22 Eq. F8-1,
for example) are neither a single number nor text. The options:

- (a) Each equation is implemented once in Python as a calc-line definition
  (ADR 0002). Its citation, source and status live in the registry as an
  entry of kind "equation", which appears in the review list, and whose
  status drives the DRAFT stamp like any other entry. Numeric coefficients
  inside the equation live with it in the code; the hand-calc tests check
  the implementation.
- (b) Equations are written as text expressions in the registry and the
  engine evaluates them. Everything code-derived is in one file, but the
  equations lose the checks and tooling Python provides, and a typo becomes
  a runtime error instead of an error caught while editing.
- (c) Equations live only in Python with a citation, outside the registry.
  Simplest, but they never enter the review list or the DRAFT logic.

Recommendation: (a).

**D2. Deflection in the upward case.** The brief fixes the downward case
(D + L) and the horizontal cases (live only) but not upward. For a round
section upward never controls, but the envelope table still needs a
defined number. The options:

- (a) Live only, the same as the horizontal cases
- (b) L − D, the service condition
- (c) L − 0.6D, mirroring the strength combination

Recommendation: (a). It is simplest to hand-check, conservative, and
consistent with the horizontal cases.

## What the slice does

### Input

A TOML project file that Micah edits by hand. One command produces the PDF:

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
  and inward are live only. Upward per D2. The limit is L/120 unless edited,
  and "Bypassed by engineer" when bypassed.
- **Mechanics versus code**: the beam formulas (PL/4, wL²/8, PL³/48EI,
  5wL⁴/384EI) are statics, not code values, so they carry a mechanics
  citation, not a registry entry. The L/120 limit and the engineering-
  judgement combination are Micah's decisions recorded in the brief, not
  registry entries.

### Output (PDF)

- A "DEVELOPMENT — NOT FOR CONSTRUCTION" watermark on every page
- The "DRAFT: contains unverified code values" stamp on every page, with a
  list of the drafted entries used. Every entry starts as drafted, so the
  stamp will be present until Micah verifies them all.
- A reserved, empty header area. The footer shows the tool version (git
  commit), the registry version (git commit of the registry file) and
  "page x of y".
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
and listed in the review list:

- ASCE 7-22 guard concentrated load and uniform load (values and sections)
- ASCE 7-22 §2.4 ASD combination used for D + L
- A53 Gr B Fy (AISC Manual Table 2-4)
- Ωb (AISC 360-22 §F1)
- Table B4.1b round HSS in flexure: λp and λr
- §F8 applicability limit on D/t
- §F8 yielding and local buckling equations (per D1)
- The basis for designing pipe as round HSS
- Already drafted: steel density, E, and the four exemption text entries

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

- Answer D1 and D2.
- Choose the pipe size and span for test case 1, and do the hand calc.
- Review the registry review list in one pass. The build can proceed while
  entries are drafted, because every PDF carries the DRAFT stamp.
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
