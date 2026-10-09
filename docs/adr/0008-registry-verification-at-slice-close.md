# Registry verification at each slice close; the recompute stays at release

**Status: proposed (2026-10-09), awaiting Micah's acceptance. Not in force until he marks it accepted.**

Changes ADR 0005, under the freeze exception of ADR 0006 (a real problem, named below). If accepted, each slice's drafted registry entries are verified by the engineer of record when the slice closes, not in the v1 release review, and the 77 entries already drafted are caught up in batches, highest fan-out first. The governing-case recompute of ADRs 0006 and 0007 stays at the release review. The rest of ADRs 0004 to 0007 is unchanged.

The problem has two parts, both from the architecture review of 2026-10-09 (F7).

First, size. ADR 0005 put every drafted entry into one review at the end. The registry held 109 entries after slice 4, 77 of them drafted, and the drafting rate has run above what the roadmap assumed; the projection for slice 9 is 140 to 165 drafted entries and 8 to 13 hours of the engineer's time on the registry alone, in one sitting, after every check is built.

Second, late correction. A drafted entry is read by every calc that uses it, and the independent calc of each slice works that value from its own reading of the code because it reads verified entries only. A correction at the release review to a widely used entry therefore invalidates every test case value that depended on it, and sends each affected independent calc back to a fresh session (docs/brief/verification.md, "Registry corrections"). Fan-out measured on 2026-10-09, by running test cases 1 to 5 through the tool and recording each registry lookup, shows how wide that is: of the 77 drafted entries, 56 are read by all five cases, and only 8 by none. The weld entries (AISC 360-22 J2 and J4) head that list, and a late correction to one of them would hit every case; the later the correction, the more cases and slices stand on it.

## Decision

At each slice close, before the slice is marked done, the engineer verifies every entry the slice drafted, against the standard, and fills verified-by and date himself (CLAUDE.md rule 1; only he marks an entry verified). The slice's "done when" gains that step. Claude produces the registry review workbook for it (below); the workbook is a review aid and records nothing the registry does not.

The 77 entries drafted before this decision are caught up in batches, ordered by fan-out, highest first: the entries read by the most test cases are verified first, so a correction, if one is needed, is found while it touches the fewest independent calcs it will ever touch and before more slices build on it. Batch size is the engineer's to set, from his time. The workbook's "By fan-out" tab is the order. Entries no case yet reaches come last, since a wrong value there has changed no test value so far.

A correction found at slice close or in a catch-up batch follows "Registry corrections" in docs/brief/verification.md unchanged: values that depended on the entry are redone from the corrected entry, independent-calc values by a fresh independent calc and the engineer's by him, never by editing them to the tool's new output (CLAUDE.md rules 5 and 6), each noting the correction. What changes is only when it happens and how many cases it can reach.

The governing-case recompute is not moved. Per ADRs 0006 and 0007 it stays in the release review, now running on a registry that is already verified apart from entries drafted or revised since the last slice close. The release review's first step shrinks to that residual, and the release-review issue (#18) stops accumulating batches of drafted entries; it keeps the deferred test cases.

An independent calc written after this takes effect reads verified entries only, as ADR 0004 intended, so each entry verified at a slice close is one fewer value the independent calc has to work from its own reading, and one fewer place where it and the tool can share a misreading unnoticed.

## Proposed addition to CLAUDE.md (not applied)

In the paragraph beginning "When you finish a task", after the sentence about adding deferred test cases to issue #18, replace the registry-entries clause and add:

> When a slice closes, produce the registry review workbook: an xlsx in out/ (not committed) of every drafted entry, with id, value and unit, cite, source, fan-out, a verdict dropdown (verified / wrong / unsure) and a notes column, one tab sorted by fan-out and one grouped by document and section. I verify that slice's entries from it before the slice is marked done (ADR 0008).

The same acceptance would update docs/brief/verification.md ("Who verifies what", "In each slice" step 4, "The release review" step 1), the header note of ADR 0005, docs/ROADMAP.md (slice 9's size estimate and the "Registry verification at release" section), and the checklist wording of #18. None of these is changed by this draft.

## Cost

The engineer's registry hours do not shrink much in total; they move earlier and are spread over each slice close, a few entries at a time, instead of one 8 to 13 hour sitting. That spread is the benefit. I'm not sure the total falls at all, and this decision does not claim it.

Verification at slice close brings back the cost ADR 0005 avoided: a later slice can revise, split or add entries that an earlier close already verified. Under CLAUDE.md rule 1 a change to a verified entry's value, unit, cite or section sends it back to drafted and onto the review list, so some entries will be verified twice. ADR 0005 judged that cost larger than the benefit when the set of entries was still growing quickly; this decision judges that the late-correction risk is now larger, because 77 entries and five cases already stand on drafted values. A wrong drafted entry also stays in the development calcs, under the DRAFT stamp, for less time than before.

The fan-out figures come from the five test cases only. A zero means no case exercises the entry yet (the H1-1a branch, the HSS grades and the intermediate-rail "same as top rail" entries are examples), not that no input could. A later slice can raise any of them, so the order is a starting point and the workbook is regenerated at each close.

## Considered Options

- Keep ADR 0005: one review at release. Not chosen, because the late-correction exposure grows with every slice and the final sitting is projected at 8 to 13 hours.
- Verify each slice's entries at its close, and catch up the 77 by fan-out: chosen.
- Verify only the high-fan-out entries early and leave the rest to release. Not chosen: it needs a threshold the engineer would have to set and defend, and the entries read by one case are cheap to verify at the close that drafted them.
