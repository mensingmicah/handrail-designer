# Governing-case recompute deferred to the release review; verification process frozen until v1

Changes ADR 0004, as amended by ADR 0005. From slice 2 on, the engineer of record's governing-case calc, his line-by-line recompute of the tool's printed controlling case recorded in [hand], is done in the v1 release review (docs/ROADMAP.md, slice 9) alongside the registry review, not within the slice. Until then each of those [hand] values is marked "deferred". The test harness skips a deferred value as it skips a pending one, without showing the tool's value, and only a [hand] value can be deferred. A "pending" value still blocks merge; a "deferred" one does not (the calc-code-review skill). Every deferred test case and every batch of drafted registry entries is listed on the release-review issue (#18, label `release-blocker`), which carries the checklist the release can't ship without. Test cases 2 and 3 are the first deferred cases. What stays in each slice is unchanged: the independent calc of every new test case, the 0.5% comparison with rule 2 stops, and his checklist review of the independent calc and the printed calc. Decided by Micah, 2026-10-04; docs/brief/verification.md, "The release review".

The reason is the one in ADR 0005: the engineer of record will not use the tool on real work until v1 is complete, so a recompute within the slice protects no real calc. Done after the registry review, the recompute also runs on corrected entries, so a registry correction doesn't send it back to be redone.

The cost is that until the release review, no value in a test case from slice 2 on is the engineer's own arithmetic. ADR 0005 left the governing-case calc and the checklist review as the only defence against a misreading the tool and the independent calc share on a drafted value; within a slice the checklist review is now the only one, and a shared error in a governing value passes the test until the release. The release review also grows by one recompute per deferred case.

## Verification process frozen until v1

The verification process is frozen until the v1 release: docs/brief/verification.md, ADRs 0004 to 0006, the harness's rules for test case values (tests/test_hand_cases.py), and the calc-code-review skill's merge rules. It changes only when a real problem forces it, such as a defect it let through or a step that can't be carried out as written, and not for convenience or preference. A change made under that exception gets its own ADR naming the problem.

## Considered Options

- Recompute within each slice, before merge (ADR 0004 as amended 2026-10-04): the engineer's arithmetic checks each check as it lands, but the work protects no real calc before v1 and may have to be redone after a registry correction. Replaced by this decision.
- Defer the recompute to the release review: chosen, for the reasons above.
