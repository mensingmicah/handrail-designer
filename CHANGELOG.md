# Changelog

## v0.2.0 (2026-10-04)

Slice 2: the post. Merged in PR #17; plan in docs/plans/slice-2.md.

`uv run handrail calc examples/slice-1.toml` now prints Checks 1, 2, 5 and
6 for an AISC pipe top rail and pipe post in A53 Gr B.

### Checks covered

- **Check 5, post combined axial and flexure** at the top of the baseplate,
  over the full envelope. Compression per AISC 360-22 Chapter E (Eq. E3-2
  or E3-3, Lc = K·h with K = 2.1 from Commentary Table C-A-7.1); tension
  yielding per §D2 for the upward case; flexure per §F8; interaction per
  Eq. H1-1a/H1-1b in the cases with moment. The downward and upward cases
  have no moment and report the Chapter E or Chapter D ratio instead. The
  longitudinal case is now a real, checked case for the post.
- **Check 6, post deflection**: cantilever deflection over h − t_p, live
  load only, in the horizontal cases, against L/60 (editable, bypassable).

### What it delivers

- Project file: post section, post height h, baseplate thickness t_p and
  the post deflection limit. Every project file now has a post.
- The first load path between members: the top rail's dead load and guard
  loads reach the post over the span as its tributary length, plus the
  post's own weight over h − t_p.
- Hard stops: slender in compression (Table B4.1a), and αPr/Pe above 0.05
  in a moment case (second-order effects; Appendix 8 amplification is not
  implemented). Lc/r above 200 is flagged, not stopped.
- Three new locked assumptions in the front matter: notional loads
  neglected, post loads on tributary length = span with rail continuity
  neglected, and baseplate thickness and bending not checked.
- 31 new drafted registry entries (34 drafted, 32 verified in all). Every
  calc still prints the DRAFT stamp.
- Pre-push hook (.githooks/pre-push) runs the test suite before a push.

### Verification model

From this slice on, checks are verified by an independent calc instead of
Micah's full hand calc (docs/brief/verification.md; ADRs 0004–0006). An
agent in a fresh session, which never reads `src/` or any tool output,
writes a complete calc of each new test case, and the test compares every
one of its values with the tool at 0.5%. Micah reviews that calc and the
printed calc against a written checklist.

- Test cases 2 (Pipe1-1/2STD post, Eq. E3-3) and 3 (Pipe2STD post,
  Eq. E3-2) are independent-calc cases; every value agrees within 0.5%.
- Test case 1 stays a full-hand case with its values unchanged.
- At release: 409 tests passed, 10 skipped (the deferred values below).

### Deferred to the release review (issue #18)

- Verification of every drafted registry entry: the 3 left from slice 1
  and the 31 from slice 2 (ADR 0005).
- Micah's line-by-line recompute of the printed controlling case of
  Checks 5 and 6 in test cases 2 and 3. Until then their [hand] values
  read "deferred" and the test skips them (ADR 0006).
- Any test case value that depends on an entry corrected in that review is
  redone from the corrected entry, never edited to the tool's output.

### Known gaps

- Eq. H1-1a is tested only against a same-author arithmetic test: in the
  moment cases Pr is dead load only, so no realistic guard post reaches
  Pr/Pc ≥ 0.2.
- Checks 3, 4 and 7, the intermediate rail, the anchor reaction sets,
  sections other than AISC pipe and the input form are not in this release.

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
