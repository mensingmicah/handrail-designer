# Reaction sets join the release-review recompute

Changes ADR 0006, under its freeze exception (a real problem, named below). From slice 4 on, the engineer of record's governing-case recompute at the release review covers each new check's printed controlling case **and each new anchor reaction set**. For each reaction set in a deferred test case he recomputes V, N and M from the printed calc and records them as [hand] values, marked "deferred" until the review like the rest. Test case 5 (slice 4) is the first: its lateral and upward sets, V, N and M each, alongside Checks 4a and 4b. Decided by Micah, 2026-10-09 (slice 4 planning, Q11); docs/brief/verification.md, "Who verifies what" and "The release review".

The problem: the reaction sets are reporting, not a check, so the process as ADR 0006 wrote it never puts the engineer's own arithmetic on them. Yet they leave his hands and go straight into anchor software for anchorage designed by others, with no later check by him. Agreement between the tool and the independent calc at 0.5% cannot catch a misreading both share, for example taking the moment arm at the top of concrete as h − t_p (the arm at the post's critical section) instead of h, or leaving a dead-load component out of 0.9D. Within a slice his checklist review is the only defence against such an error; this decision adds his arithmetic at the release.

The cost is six more recomputed numbers per deferred case with reaction sets (fewer when there is no net uplift), and the release review grows accordingly. Nothing else in the frozen process changes.

## Considered Options

- Keep ADR 0006 as written: the reaction sets are covered by the independent calc and the checklist review only, like every non-governing value. Not chosen, because the reactions are an end product handed to others, not an intermediate value.
- Recompute each new reaction set at the release review: chosen.
