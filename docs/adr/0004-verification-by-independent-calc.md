# Verification by independent calc, governing-case check and review

> Per-slice registry verification below is superseded by ADR 0005: one review of every drafted entry before the v1 release (2026-10-03).

> From slice 2 on, the governing-case calc below is deferred to the same release review, and the verification process is frozen until v1: ADR 0006 (2026-10-04).

> The governing-case calc below is no longer blind (2026-10-04): the engineer of record follows the tool's printed controlling case and recomputes every line himself, checking each provision against the code. His [hand] values are his own recomputed results, never copied from the output. Blind independence comes from the independent calc. See docs/brief/verification.md.

> Correction (2026-10-04): the second paragraph's "the Chapter E term is about 0.3% of the governing H1-1b ratio" should read: the H1-1b axial term Pr/(2Pc) is about 0.15% of it; Pr/Pc itself is about 0.3%. The conclusion is unchanged.

> The current process, with these amendments applied, is described in docs/brief/verification.md alone. This ADR records the decision as it was made.

Supersedes the verification model in docs/brief/verification.md as it stood through slice 1 (no earlier ADR recorded it), under which every new check was verified against the engineer of record's full hand calc: every envelope case and every intermediate value, recorded in the test case and compared to the tool at 0.5%. That cost the engineer of record a complete hand calc for each check, about 44 values for slice 1 alone, and it is not how he reviews a junior engineer's calc. From slice 2 on, each new check is verified in four parts. The engineer of record verifies the slice's registry entries first. An agent in a clean context writes an independent calc of every value in the test case, from the code, the brief, the plan's decisions, the case inputs and verified registry entries only, never from `src/`, the tool's output, the tests or drafted entries. The engineer of record works the case he expects to govern on his own, before seeing either calc. Then he backchecks the independent calc and the tool's printed calc against a written checklist. The test compares the tool to every independent-calc value and every one of his values at 0.5%, and any mismatch is a rule 2 stop. Verification is still paid once per check, not per job, so the reason for front-loading it stands: a tool's errors are systematic and repeat in every calc. What changes is that a machine does the arithmetic, and the engineer of record's time goes to the method, the load path and the governing number. Test case 1 keeps its full hand values unchanged. Decided by Micah, 2026-09-30, issue #13.

The known weakness is shared misreading: the tool and the independent calc are written by the same kind of model from the same code text, so a provision both read the same wrong way passes the comparison. The governing-case calc and the checklist review (loads complete, direction and worst case, checks complete, geometry, method) are the defence, and values that don't govern rely on the review alone. In test case 2 the Chapter E term is about 0.3% of the governing H1-1b ratio, so an Fcr error of 2× would not move the governing value. Micah accepted that.

## Considered Options

- Full hand calc for each new check (the slice 1 model): the most independent, but it spends the engineer of record's time on arithmetic a machine can do independently.
- Full hand calc the first time a check appears, spot checks after: still a complete hand calc per check, since each slice adds new checks.
- Review only, with no blind value from the engineer of record: the cheapest, but every independent number is machine-made, and a backcheck tends to approve a plausible wrong step. Rejected for a ten-minute blind governing-case calc per case.
- Independent calc reads the whole registry: fewer false mismatches, but a wrong drafted value would feed both calcs and agree with itself. Reading none of it would produce mismatches on values already verified. Verified entries only, with verification done before the independent calc runs.
- Verify every registry entry before any check code is written: rejected because a slice's entries can't all be known before the build starts (slice 2 planned about 20 and drafted 30).
