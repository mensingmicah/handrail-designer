# Brief: verification

Part of the product brief; index in docs/BRIEF.md. How the tool's check
code is verified as it is built: test cases, the independent calc, my
review, the release review, and the shapes database extraction test.

This file describes the current process only. How it got here is in
docs/adr/: 0004 (verification by independent calc), 0005 (registry
verification at release), 0006 (governing-case recompute at release), 0007
(reaction sets join that recompute) and 0008 (registry verification at each
slice close, amended the same day: verification is back at release, with a
review workbook at each slice close and the verdict workflow below).
The process is frozen until v1. It changes only when a real problem forces
it, such as a defect it let through or a step that can't be carried out as
written, and that change gets its own ADR naming the problem (ADR 0006).

Verification happens once per check, as the check is built. Once a check
passes, every later job inherits it, and the test cases rerun on every
change to keep it true. My review of each real job (its inputs, and whether
the guard fits the tool's assumptions) is separate and unchanged.

## Who verifies what

- **Every value: the independent calc, in the slice.** An agent in a clean
  context writes a complete calc of each new test case, working from the
  code, the brief, the plan's decisions and the case inputs, never from the
  tool's code or output. The procedure is the independent-calc skill
  (.claude/skills/independent-calc/SKILL.md). The test compares every one
  of its values with the tool.
- **The process: me, by review, in the slice.** I backcheck the
  independent calc line by line, the way I review a junior engineer's
  calc, and read the tool's printed calc for the controlling case, using
  the checklist below.
- **Code values: me, in the release review.** I verify every drafted
  registry entry against the standard (CLAUDE.md rule 1) before v1, in the
  release review. Verifying earlier is optional and blocks nothing: no
  slice's build waits on registry verification (ADR 0008 as amended, Micah
  2026-10-09). A registry review workbook is produced at each slice close
  so I can verify entries early when I choose; its "By fan-out" tab (the
  number of test cases that read each entry) is the suggested order,
  because a late correction to a widely read entry sends the most
  independent calcs back to fresh sessions ("Registry corrections", below).
  I accepted that risk. Until an
  entry is verified, the check code runs on it and every calc that uses it
  prints the DRAFT stamp. The independent calc reads verified entries only,
  so it works every still-drafted value from its own reading of the code.
  When it agrees with the tool on a drafted value, that agreement does not
  verify the value: both may hold the same misreading.
- **The governing case: me, by recomputation, in the release review.** For
  each new check and each new reaction set in each test case, I follow the
  tool's printed controlling case (for the post: the horizontal load at
  the top producing moment at the base) and recompute every line myself
  with a calculator, checking each provision against the code. I record at
  least the governing ratio (or deflection, for a deflection check) and
  which case governs, plus any intermediate values I recompute; for a
  reaction set, its V, N and M (ADR 0007, Micah 2026-10-09). My [hand] values are my own recomputed
  results, never copied from the PDF (CLAUDE.md rule 5). This check is not
  blind; blind independence comes from the independent calc. Because it
  follows the printed case, it confirms what the tool did rather than
  finding what the tool left out; omissions are caught by the independent
  calc and checklist items 1–3.
  - **What counts as new in a section family's first case.** (S5-2, Micah
    2026-10-09; a reading of the rule above, not a change to it.) Slices 5
    to 7 add section families, not checks. My recompute covers a check in
    a family's first test case when that case reaches a provision, an
    equation branch or a computed property that none of my own arithmetic
    has touched. A new section name alone does not trigger it: a check
    whose provisions and branches I have already recomputed, run on a new
    section with only its registry values (Fy, Fu) or published
    properties different, is covered by the independent calc and my
    registry verification. Each slice plan names the groups this reading
    gives, and the case lists them in `[verification] recompute`. Slice
    5: Check 1 on the noncompact rail (Eq. F8-2), and the custom tube's
    section properties (the §B4.2 design wall, and A, I, S, Z and r from
    dimensions).

## In each slice

1. The independent calc is written for each new test case, in a fresh
   session, by the independent-calc skill.
2. I review the independent calc and the tool's printed calc against the
   checklist.
3. The test compares the tool to every independent-calc value at 0.5%.
4. My [hand] values for the case are marked "deferred". When the slice
   closes, its deferred cases are added to the release-review issue's
   checklist (#18; CLAUDE.md), and Claude produces the registry review
   workbook for the slice's drafted entries (an xlsx in out/, not
   committed: id, value and unit, cite, source, fan-out, a verdict
   dropdown and a notes column, one tab by fan-out and one by document and
   section). Verifying those entries before the release review is
   optional; nothing waits on it (ADR 0008 as amended).

## The release review

Before v1, in one review (issue #18, label `release-blocker`; docs/ROADMAP.md,
slice 9), in this order:

1. I verify every registry entry still drafted: all of them, less any I
   verified early from a slice-close workbook (ADRs 0005 and 0008).
2. I recompute the printed controlling case of each new check and each
   new reaction set in every deferred test case, and replace each "deferred" [hand] value with my
   own result. The test then compares those too.
3. The full test suite reruns.

The registry comes first, so the recompute runs on corrected entries.

### Applying the verdicts

I record each verdict in the registry review workbook (out/registry-review-drafted.xlsx, not
committed; ADR 0008), in its verdict column: verified, wrong or unsure, with
my notes beside it. I do not edit registry/code-values.toml myself. A
separate agent session applies the workbook to the registry:

1. It works on a branch and reaches main only through a pull request I
   approve, because a registry value feeds the calc (CLAUDE.md, Git).
2. It reads each row of the workbook and acts on the verdict. A "verified"
   row: status "verified", verified_by "Micah Mensing", verified_date the
   date I give it (the date the workbook was last saved if I give none),
   and its id removed from the review list. A "wrong" or "unsure" row, or
   a row with no verdict: no change to the entry, which stays drafted.
3. It edits the registry with the file-edit tool only, never a shell
   command (.claude/rules/code-values.md). It changes no value, unit, cite,
   section or note, and drafts no correction on its own.
4. The pull request description is the record, since the workbook is not
   committed: a table of every row's id, verdict and my note, the date used,
   and a separate list of every "wrong" and "unsure" entry with its note,
   for me to resolve. The registry lint test and the full suite pass before
   the pull request is opened.
5. A "wrong" entry is corrected by me, or by an agent from what I state,
   in a later change; it stays drafted until I verify the corrected entry
   (CLAUDE.md rule 1), and "Registry corrections" below applies.

The verdict is mine, and my "verified" in the workbook counts as me
marking the entry verified; the agent only records it (CLAUDE.md rule 1,
.claude/rules/code-values.md). This workflow is the same whether I verify
early or in the release review. The workbook is regenerated at each
slice close under a new dated name, so a workbook holding verdicts is never
overwritten.

### Registry corrections

An entry I correct changes the tool's values. Correcting only a note or
edition changes no value (.claude/rules/code-values.md). A value that
depended on a corrected entry will now disagree with the tool. That is a
rule 2 stop whose cause is already known: the entry was wrong. So the
value is redone from the corrected entry:

- independent-calc values, by a fresh independent calc (the skill);
- my values, by me.

No value is edited to match the tool's new output (CLAUDE.md rules 5 and
6). Each redone value carries a note naming the registry correction that
caused it.

## Pending and deferred values

A value in a test case that has not been worked yet reads "pending" or
"deferred". The test skips both without showing the tool's value.

- **Pending:** not yet worked, in [hand] or in an independent-calc file.
  A pending value blocks merge (the calc-code-review skill).
- **Deferred:** a [hand] value whose recompute waits for the release
  review. It does not block merge. Only [hand] values can be deferred; the
  independent calc is never deferred, and a "deferred" in an
  independent-calc file fails the test.

## Test cases

- Each test case holds a project's inputs and the values the tool is
  compared against. Every change reruns all cases. Any value more than 0.5%
  (relative) from the tool fails, and any mismatch, against my value or the
  independent calc, is a rule 2 stop: neither side changes until we know
  which one is wrong.
- **Full-hand case:** every tool value has a value from my hand calc. Test
  case 1 (slice 1) is this kind and stays exactly as it is.
- **Independent-calc case:** every tool value has an independent-calc
  value, and my governing-case values are a subset. Every test case from
  slice 2 on is this kind.
- Each new check arrives with at least one test case, and each code branch
  it adds (for example Eq. E3-2 and Eq. E3-3) is reached by at least one
  case.
- **A section family's case covers the groups its family changes.** (S5-2,
  Micah 2026-10-09.) From slice 5 on, a test case for a new section family
  need not cover all seven checks. It lists in `[verification] covers`
  the groups its new member changes: a rail case, the section group and
  the rail's checks; a post case, the post group, the post's checks and
  the reactions. The members it leaves on pipe stay covered by cases 1 to
  5, which rerun on every change. One addition: a narrowed case still
  records, as independent-calc values, every cross-member quantity its
  family changes, even when the checks downstream of it are not covered.
  A custom rail case records the rail's weight and D at the post, for
  example, though it does not cover Checks 5 to 7. Each slice plan lists
  each case's groups and those quantities.
- Every value records its provenance. A value corrected after comparison
  with the tool keeps a note saying so, because it is no longer an
  independent check. Tool output is never used to fill or edit a test
  case value (CLAUDE.md rule 5).

## What the independent calc may read

- Allowed: the brief, the current slice plan's decisions, CONTEXT.md, the
  test case's inputs, registry entries with status "verified", and section
  properties from AISC's original Shapes Database workbook. Where a value
  or provision has no verified entry, it works from its own reading of the
  code and records the source of each value.
- Forbidden: src/, every tool output (PDF, Typst source, `--json`, test
  runs), tests/ other than the case inputs and the key names of its own
  values file, any recorded hand or independent-calc value, drafted
  registry entries, the shapes TOML extracted from the workbook, and the
  branch's history and diffs. The test files are forbidden because they
  hold expected values and running them can print the tool's.
- It states where each load acts and how it reaches the critical section,
  and lists every limit state it considered and why each does or doesn't
  apply, from the code rather than from the tool's list of checks. These
  target the errors the tool and the independent calc could share.

The skill gives the exact commands for each allowed read.

## Review checklist

My review of the independent calc and the tool's printed calc. The
mistakes I catch most often come first.

1. **Loads complete:** every load that should act is included: each
   member's dead load carried down, both guard load types, the component
   load where it applies.
2. **Direction and worst case:** each load acts in the right direction at
   the right point; every envelope direction is considered and the worst
   case found.
3. **Checks complete:** every limit state that applies is checked, and none
   is left out.
4. **Geometry:** heights, distances, spans and lever arms are right
   (h vs h − t_p, the eccentricity, the span).
5. **Method and equations:** the right provision and equation, with its
   applicability conditions checked (classification, branch limits, the
   H1-1a/b threshold).
6. **Assumptions:** stated and reasonable (fixity, K and Lc, the critical
   section).
7. **Code editions:** every citation names the right edition and section,
   consistently.
8. **Magnitude sense:** values in the expected range, units consistent.
9. **Governing case:** the one I expected, or there is a reason it isn't.

Arithmetic is not on the list for the independent calc: the 0.5%
comparison covers it. My own arithmetic is the governing-case recompute.

## Accepted limitation

Values that don't govern are checked by agreement between the tool and the
independent calc plus my review, not by my own arithmetic. Two agents can
share a misreading of a provision. My checklist review is the defence
against that within a slice, and my governing-case recompute joins it in
the release review; until then a shared error in a governing value passes
the test. A non-governing branch can be wrong by a large factor without
moving the governing ratio: in test case 2 the H1-1b axial term Pr/(2Pc)
is about 0.15% of the controlling H1-1b ratio (Pr/Pc itself is about
0.3%), so an Fcr error of 2× would move my governing value by only about
0.15%, well inside the 0.5% tolerance.

## Shapes database

Section properties come from a file extracted by script from the
unmodified AISC Shapes Database, and a test confirms the extracted file
matches the original row for row.
