# Registry verification at each slice close; the recompute stays at release

**Status: accepted (Micah, 2026-10-09), with one change to the proposed CLAUDE.md wording: the engineer verifies a slice's entries before the next slice's build starts, not before the slice is marked done.**

Changes ADR 0005, under the freeze exception of ADR 0006 (a real problem, named below). Each slice's drafted registry entries are verified by the engineer of record at the slice close, not in the v1 release review, and the 77 entries already drafted are caught up in batches, highest fan-out first. The governing-case recompute of ADRs 0006 and 0007 stays at the release review. The rest of ADRs 0004 to 0007 is unchanged.

The problem has two parts, both from the architecture review of 2026-10-09 (F7).

First, size. ADR 0005 put every drafted entry into one review at the end. The registry held 109 entries after slice 4, 77 of them drafted, and the drafting rate has run above what the roadmap assumed; the projection for slice 9 is 140 to 165 drafted entries and 8 to 13 hours of the engineer's time on the registry alone, in one sitting, after every check is built.

Second, late correction. A drafted entry is read by every calc that uses it, and the independent calc of each slice works that value from its own reading of the code because it reads verified entries only. A correction at the release review to a widely used entry therefore invalidates every test case value that depended on it, and sends each affected independent calc back to a fresh session (docs/brief/verification.md, "Registry corrections"). Fan-out measured on 2026-10-09, by running test cases 1 to 5 through the tool and recording each registry lookup, shows how wide that is: of the 77 drafted entries, 56 are read by all five cases, and only 8 by none. The weld entries (AISC 360-22 J2 and J4) head that list, and a late correction to one of them would hit every case; the later the correction, the more cases and slices stand on it.

## Decision

When a slice closes, the engineer verifies every entry the slice drafted, against the standard, before the next slice's build starts, and fills verified-by and date himself (CLAUDE.md rule 1; only he marks an entry verified). The next slice's build does not begin until that is done; the slice's own "done when" is unchanged. Claude produces the registry review workbook for it (below); the workbook is a review aid and records nothing the registry does not.

The 77 entries drafted before this decision are caught up in batches, ordered by fan-out, highest first: the entries read by the most test cases are verified first, so a correction, if one is needed, is found while it touches the fewest independent calcs it will ever touch and before more slices build on it. Batch size is the engineer's to set, from his time. The workbook's "By fan-out" tab is the order. Entries no case yet reaches come last, since a wrong value there has changed no test value so far.

A correction found at slice close or in a catch-up batch follows "Registry corrections" in docs/brief/verification.md unchanged: values that depended on the entry are redone from the corrected entry, independent-calc values by a fresh independent calc and the engineer's by him, never by editing them to the tool's new output (CLAUDE.md rules 5 and 6), each noting the correction. What changes is only when it happens and how many cases it can reach.

The governing-case recompute is not moved. Per ADRs 0006 and 0007 it stays in the release review, now running on a registry that is already verified apart from entries drafted or revised since the last slice close. The release review's first step shrinks to that residual, and the release-review issue (#18) stops accumulating batches of drafted entries; it keeps the deferred test cases and the registry items that are not a batch (the W2 directional-increase entry and the Table J2.5 confirmation).

An independent calc written after this takes effect reads verified entries only, as ADR 0004 intended, so each entry verified at a slice close is one fewer value the independent calc has to work from its own reading, and one fewer place where it and the tool can share a misreading unnoticed.

## CLAUDE.md addition (applied 2026-10-09)

In the paragraph beginning "When you finish a task", the sentence about adding deferred test cases and drafted-entry batches to issue #18 now adds only the deferred test cases, and this follows it:

> When a slice closes, produce the registry review workbook for that slice's drafted entries. I verify them before the next slice's build starts (ADR 0008).

The same acceptance updates docs/brief/verification.md ("Who verifies what", "In each slice" step 4, "The release review" step 1), the header note of ADR 0005, docs/ROADMAP.md (the overview paragraph, slice 9 and "Registry verification at release") and the checklist of #18.

## Cost

The engineer's registry hours do not shrink much in total; they move earlier and are spread over each slice close, a few entries at a time, instead of one 8 to 13 hour sitting. That spread is the benefit. I'm not sure the total falls at all, and this decision does not claim it.

Verification at slice close, ahead of the next slice's build, brings back the cost ADR 0005 avoided: a later slice can revise, split or add entries that an earlier close already verified. Under CLAUDE.md rule 1 a change to a verified entry's value, unit, cite or section sends it back to drafted and onto the review list, so some entries will be verified twice. ADR 0005 judged that cost larger than the benefit when the set of entries was still growing quickly; this decision judges that the late-correction risk is now larger, because 77 entries and five cases already stand on drafted values. A wrong drafted entry also stays in the development calcs, under the DRAFT stamp, for less time than before.

The fan-out figures come from the five test cases only. A zero means no case exercises the entry yet (the H1-1a branch, the HSS grades and the intermediate-rail "same as top rail" entries are examples), not that no input could. A later slice can raise any of them, so the order is a starting point and the workbook is regenerated at each close.

## Notes

**Catch-up ruling (Micah, 2026-10-09).** The catch-up of the 77 entries drafted before this decision has two gates. The top 20 entries of the "By fan-out" tab of the registry review workbook are verified before slice 5's build starts. Every other entry drafted by 2026-10-09 is verified before slice 6's build starts. Slice 5's own drafted entries follow the ordinary rule above: verified before slice 6's build starts as well.

The workbook is not committed and its order depends on the measurement that produced it, so the top 20 are fixed here, in tab order (all read by all five test cases; weld entries first). There is no tie at the cut: the 20th reads in 6 case x check pairs and the 21st, `aisc360.eq.A-8-5`, in 5.

- `aisc360.eq.J4-4.coeff`
- `aisc360.J2.5.fnw`
- `aisc360.J2.5.omega_w`
- `aisc360.J2.5.fnw.coeff`
- `aisc360.J2.2a.throat`
- `aisc360.J2.2a.throat.coeff`
- `aisc360.J2.2b.max_size_edges`
- `aisc360.J2.4.min_size`
- `aisc360.J2.4.fillet_strength`
- `material.E70XX.FEXX`
- `aisc360.eq.J4-4`
- `aisc360.J4.2.omega_rupture`
- `aisc_manual.part9.base_metal`
- `ej.weld.max_size_not_applicable`
- `ej.weld.line_method`
- `material.A53_GrB.Fu`
- `aisc_manual.t3-23.case22.M`
- `ej.weld.post_wall_covered`
- `ej.weld.no_bearing`
- `ej.weld.branch_kds`

Micah records each verdict in the workbook; an agent applies the verdicts to registry/code-values.toml on a branch with a pull request he approves, and lists every "wrong" or "unsure" entry for him (Micah, 2026-10-09; docs/brief/verification.md, "Applying the verdicts"). A correction follows "Registry corrections" in the same file.

## Considered Options

- Keep ADR 0005: one review at release. Not chosen, because the late-correction exposure grows with every slice and the final sitting is projected at 8 to 13 hours.
- Verify each slice's entries at its close, and catch up the 77 by fan-out: chosen.
- Verify only the high-fan-out entries early and leave the rest to release. Not chosen: it needs a threshold the engineer would have to set and defend, and the entries read by one case are cheap to verify at the close that drafted them.
