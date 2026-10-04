# Brief: verification

Part of the product brief; index in docs/BRIEF.md. How the tool's check
code is verified as it is built: test cases, the independent calc, my
review, the release review, and the shapes database extraction test.

This file describes the current process only. How it got here is in
docs/adr/: 0004 (verification by independent calc), 0005 (registry
verification at release) and 0006 (governing-case recompute at release).
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
  registry entry against the standard (CLAUDE.md rule 1) in one review
  before v1, not slice by slice. Until then the check code runs on drafted
  entries and every calc prints the DRAFT stamp. The independent calc reads
  verified entries only, so it works every still-drafted value from its own
  reading of the code. When it agrees with the tool on a drafted value,
  that agreement does not verify the value: both may hold the same
  misreading.
- **The governing case: me, by recomputation, in the release review.** For
  each new check in each test case, I follow the tool's printed controlling
  case (for the post: the horizontal load at the top producing moment at
  the base) and recompute every line myself with a calculator, checking
  each provision against the code. I record at least the governing ratio
  (or deflection, for a deflection check) and which case governs, plus any
  intermediate values I recompute. My [hand] values are my own recomputed
  results, never copied from the PDF (CLAUDE.md rule 5). This check is not
  blind; blind independence comes from the independent calc. Because it
  follows the printed case, it confirms what the tool did rather than
  finding what the tool left out; omissions are caught by the independent
  calc and checklist items 1–3.

## In each slice

1. The independent calc is written for each new test case, in a fresh
   session, by the independent-calc skill.
2. I review the independent calc and the tool's printed calc against the
   checklist.
3. The test compares the tool to every independent-calc value at 0.5%.
4. My [hand] values for the case are marked "deferred". When the slice
   closes, its deferred cases and its batch of drafted registry entries
   are added to the release-review issue's checklist (#18; CLAUDE.md).

## The release review

Before v1, in one review (issue #18, label `release-blocker`; docs/ROADMAP.md,
slice 9), in this order:

1. I verify every drafted registry entry.
2. I recompute the printed controlling case of each new check in every
   deferred test case, and replace each "deferred" [hand] value with my
   own result. The test then compares those too.
3. The full test suite reruns.

The registry comes first, so the recompute runs on corrected entries.

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
