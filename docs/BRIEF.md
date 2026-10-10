# Handrail Designer — Product Brief

This brief says what the tool must do and which engineering decisions are
already made. How the tool is built is recorded separately, in docs/adr/.

The brief is split by topic under docs/brief/. Read the files relevant to
the task; a whole-tool review reads all of them.

| File | Covers |
| --- | --- |
| [scope.md](brief/scope.md) | What the tool is, who uses it, v1 in scope and out of scope, future versions |
| [inputs.md](brief/inputs.md) | Project info, geometry, sections, materials and grades, welds, guard loads, deflection limits, dimension entry |
| [loads-and-envelope.md](brief/loads-and-envelope.md) | Decisions on direction cases (outward, inward, downward, upward, longitudinal), guard load types and where they act, dead load at the post, the post envelope, any-direction coverage, the upward combination, dead/live separation, anchor reaction sets |
| [checks.md](brief/checks.md) | The seven checks, flexural and compression capacity, upward tension; decisions on biaxial bending, section classification, section properties, custom tube thickness; the post (critical section, K, Lc/r flag, axial-only cases, second-order stop, notional loads, Check 6); the intermediate rail (Check 4); the order section families arrive in and the two-axis section type (S5) |
| [welds.md](brief/welds.md) | Weld method for Checks 3 and 7: elastic line method, directional increase, base metal, fillet size limits, weld length and moment arm |
| [output.md](brief/output.md) | Code references, stated assumptions printed in the output, PDF content, order, precision and units, DRAFT stamp, project file |
| [verification.md](brief/verification.md) | The current verification process: who verifies what, each slice's steps, the release review (registry verification and Micah's governing-case recompute), pending and deferred values, test cases and the 0.5% tolerance, what the independent calc may read, the review checklist, shapes database extraction test |

The brief's "Engineering decisions already made" are split between
loads-and-envelope.md and checks.md; both files keep that heading.
