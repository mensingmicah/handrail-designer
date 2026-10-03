# Brief: verification

Part of the product brief; index in docs/BRIEF.md. How the tool's check
code is verified as it is built: test cases, the independent calc, my own
governing-case calc, my review, and the shapes database extraction test.
Decided 2026-09-30 (issue #13; docs/adr/0004-verification-by-independent-calc.md).
Registry verification moved to one review before release on 2026-10-03.

Verification happens once per check, as the check is built. Once a check
passes, every later job inherits it, and the test cases rerun on every
change to keep it true. My review of each real job (its inputs, and whether
the guard fits the tool's assumptions) is separate and unchanged.

## Who verifies what

- **Code values: me, in one review before release.** I verify every
  drafted registry entry against the standard (CLAUDE.md rule 1) in a
  single review in the v1 release slice, not slice by slice (decided
  2026-10-03; see "The release registry review" below). Until then the
  check code runs on drafted entries and every calc prints the DRAFT
  stamp. The independent calc reads verified entries only, so it works
  every still-drafted value from its own reading of the code. When it
  agrees with the tool on a drafted value, that agreement does not verify
  the value: both may have the same misreading.
- **Every value: the independent calc.** An agent in a clean context writes
  a complete calc of each new test case, working from the code, the brief,
  the plan's decisions and the case inputs, never from the tool's code or
  output. The procedure is the independent-calc skill
  (.claude/skills/independent-calc/SKILL.md).
- **The governing case: me, on my own.** For each new check I work the
  case I expect to govern (for the post: the horizontal load at the top
  producing moment at the base), before I open the independent calc or any
  tool output. I record at least the governing ratio (or deflection, for a
  deflection check) and which case governs, plus any intermediate values I
  work along the way.
- **The process: me, by review.** I then backcheck the independent calc
  line by line, the way I review a junior engineer's calc, and read the
  tool's printed calc for the controlling case, using the checklist below.

## Order for each new check

1. The independent calc is written for each new test case.
2. I work the governing case without looking at the independent calc or
   the tool's output.
3. I review the independent calc and the tool's printed calc against the
   checklist.
4. The test compares the tool to every independent-calc value and to every
   value of mine.

## The release registry review

Before v1 I verify every drafted entry in one review. An entry I correct
changes the tool's values, so the full test suite reruns afterwards.
Correcting a note or edition changes no value. A value that depended on a
corrected entry will now disagree with the tool. That is a rule 2 stop
whose cause is already known: the entry was wrong. So the value is
redone from the corrected entry:

- independent-calc values, by a fresh independent calc (the skill);
- my values, by me.

No value is edited to match the tool's new output (CLAUDE.md rules 5 and
6). Each redone value carries a note naming the registry correction that
caused it.

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
  case value (CLAUDE.md).

## What the independent calc may read

- Allowed: the brief, the current slice plan's decisions, CONTEXT.md, the
  test case's inputs, and registry entries with status "verified". Where a
  value or provision has no verified entry, it works from its own reading
  of the code and records the source of each value.
- Forbidden: src/, every tool output (PDF, Typst source, `--json`), tests/
  other than the case inputs, any recorded hand or independent-calc value,
  drafted registry entries, and the slice branch's history and diffs. Test
  files are forbidden because they hold expected values derived from the
  tool.
- It states where each load acts and how it reaches the critical section,
  and lists every limit state it considered and why each does or doesn't
  apply, from the code rather than from the tool's list of checks. These
  target the errors the tool and the independent calc could share.

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
comparison covers it. My own arithmetic is the governing-case calc.

## Accepted limitation

Values that don't govern are checked by agreement between the tool and the
independent calc plus my review, not by my own arithmetic. Two agents can
share a misreading of a provision; my governing-case calc and checklist
review are the defence against that. A non-governing branch can be wrong by
a large factor without moving the governing ratio: in test case 2 the
Chapter E term is about 0.3% of the controlling H1-1b ratio, so an Fcr
error of 2× would not show in my governing value.

## Shapes database

Section properties come from a file extracted by script from the
unmodified AISC Shapes Database, and a test confirms the extracted file
matches the original row for row.
