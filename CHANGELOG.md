# Changelog

## v0.1.0 (2026-09-30)

Slice 1: the first end-to-end run from a project file to a printed calc.

`uv run handrail calc examples/slice-1.toml` produces a PDF calc package for
an AISC pipe top rail in A53 Gr B, spanning simple-span between posts.

### Checks covered

- **Check 1, top rail bending**: round HSS classification (AISC 360-22
  Table B4.1b), Mn per §F8, allowable Mn/Ωb, over the full direction envelope.
- **Check 2, top rail deflection**: simple-span midspan deflection against
  L/120 (editable, bypassable by the engineer).

Checks 3-7, reactions, other shapes and the input form are not in this
release.

### What it delivers

- TOML project file, and a dimension parser accepting the forms in the brief
  (5' 6-1/8", 66.125 in, 3 ft 6 in, bare number as inches).
- AISC Shapes Database v16.0 PIPE rows extracted to `data/shapes-pipe.toml`,
  verified row for row against the original workbook.
- Code-value registry with drafted entries, review list, hard stop on a
  missing entry, and the "DRAFT: contains unverified code values" stamp.
  Every entry is still drafted; none is engineer-verified.
- Calc-line machinery with pint units; beam formulas cite AISC Manual
  Table 3-23.
- Envelope of direction cases (downward, outward, inward, upward,
  longitudinal). Every case is computed and listed; the controlling case
  prints in full. Slender sections and D/t beyond the §F8 limit stop the
  calc.
- PDF via Typst: development watermark, DRAFT stamp, version footer with
  uncommitted-changes flag, front matter, dimensions, section properties,
  loading, both checks, summary table.
- Test case 1 (Micah's hand calc) within 0.5% of the tool.

### Known gaps

- The noncompact branch (Eq. F8-2) is tested only against a same-author
  arithmetic rewrite, not a hand calc; a noncompact hand case is tracked in
  GitHub issue #3.
- Display-unit settings: issue #1.
