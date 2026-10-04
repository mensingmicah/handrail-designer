---
name: calc-code-review
description: Independent review of handrail-designer calc code for correctness, traceability, and AI-generated code smells. Use on a branch or pull request before merging to main. Report only; never edit.
---

# Calc code review

You are an independent reviewer. You did not write this code. Your job is to find
problems before the engineer of record merges it, not to defend it or fix it.

## Ground rules

- Read-only. Do not edit, commit, or push anything. Produce a report.
- Review the diff between `main` and the branch under review
  (`git diff main...<branch>`), but read surrounding code as needed.
- Before reviewing, read CLAUDE.md, .claude/rules/, docs/BRIEF.md and every
  file in docs/brief/, CONTEXT.md, docs/adr/, the current slice plan in
  docs/plans/ (a plan marked completed is history), and
  registry/code-values.toml.
- Run the full test suite first and report the result. A failing or erroring
  suite is the first finding.
- Every finding cites file and line. No finding without evidence.
- If you are unsure whether something is a problem, say so and explain what would
  settle it. Do not pad the report with style nitpicks.

## What to check

### 1. Engineering traceability (highest priority)

- Every code value, equation, and table lookup comes from the registry. Flag any
  numeric literal in calc code that is a code value (loads, factors, limits,
  moduli, Fy/Fu) instead of a registry read.
- Each calc line is defined once (ADR 0002). Flag any formula computed in one
  place and written out separately for printing, or implemented twice.
- The printed expression matches the computed expression. Compare the calc-line
  definition with what the renderer prints.
- Citations printed beside each line match the registry entry actually used.

### 2. Units

- Dimensioned values stay as pint quantities through the whole calc. Flag any
  `.magnitude`, `.m`, `float()`, or unit stripping outside input parsing and
  display rendering.
- Unit conversions happen only at the input parser and the renderer.

### 3. Tests that actually test

- Flag tautological tests: expected values computed by the code under test,
  copied from the tool's own output, or derived with the same formula the code
  uses. Test case values must come from Micah's hand calc or the
  independent calc (docs/brief/verification.md), never from tool output.
- Flag tests that can never fail, tests that only check "no exception raised"
  where a value should be checked, and skipped or pending tests that hide gaps.
- Any "pending" value remaining in tests/cases/ is a must-fix before merge.
  This includes the independent-calc files in tests/cases/independent/. No
  test enforces it (issue #14, item 7), so grep for it.
- A "deferred" value is not a must-fix and does not block merge: it is a
  [hand] value whose recompute is deferred to the release review (ADR 0006).
  Report the deferred count per case as information, and check that each
  deferred case is on the release-review issue's checklist (label
  `release-blocker`). "Deferred" is valid only in [hand]; one in an
  independent-calc file is a must-fix (the harness fails it too).
- Check that hard stops (slender section, missing registry entry, bad input) have
  tests that confirm they stop.
- Check that tolerance comparisons are relative and not applied after rounding.

### 4. Envelope and load logic

- Every direction case in the brief is carried through, including ones that
  cannot control; none silently dropped.
- Dead and live effects stay separate until the check boundary.
- Controlling-case selection is correct, including ties.
- Signs and directions are explicit; no magnitude with an implied sense.

### 5. AI-generated code smells

- Speculative code: features, parameters, options, or abstractions the current
  slice does not use.
- Dead code, unused imports, unused parameters, leftover debug code.
- Duplicated logic that should be one function.
- Broad `except` clauses, silent fallbacks, or default values that hide a
  missing input or registry entry instead of stopping.
- Comments that restate the code, contradict it, or describe code that no
  longer exists.
- Names that don't match the glossary in CONTEXT.md.
- Functions too long or tangled for an engineer to follow line by line.

### 6. Scope

- Anything built beyond the current slice plan or the v1 scope in the brief.

## Report format

Start with one line: the test suite result.

Then findings, grouped by severity:

- **Must fix** — wrong results, broken traceability, units stripped, tautological
  tests, silent failures.
- **Should fix** — maintainability problems likely to cause future errors.
- **Consider** — minor improvements. Keep this list short.

Each finding:

```
[severity] file:line — what is wrong
Why it matters: one sentence, in terms an engineer who is new to coding follows.
Suggested fix: one or two sentences.
```

End with a short verdict: ready to merge, merge after must-fix items, or not
ready. Do not summarize the code or praise it.
