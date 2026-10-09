# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | (not used)           | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-decision`     | Waiting on Micah's ruling; assigned to him |
| `ready-for-agent`          | (not used)           | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | (not used)           | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table. A role marked "(not used)" has no label here: skip the labelling step for it.

Other labels in use: `release-blocker` (the release review, #18), `next-calc-branch` (small fixes for the next calc branch that change no printed number or calc text), `enhancement`, `question`, `bug`, `documentation`, `duplicate`.

Placement is by milestone, not label: every open issue sits in one milestone (Slice 5 to Slice 8, "Slice 9 (v1 release)", or "After v1"), except the pinned "Slice status" issue. See docs/ROADMAP.md.
