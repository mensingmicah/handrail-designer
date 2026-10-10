# Handrail Designer

A checker for baseplate-mounted steel guardrail and handrail systems that
produces a hand-checkable calculation package. The product brief is indexed
in docs/BRIEF.md and split by topic under docs/brief/; read the parts of the
brief relevant to the task.

Micah is a licensed PE and the engineer of record for everything this tool
produces. He seals its output.

## How to work with me

Structural engineering: I am an expert. Skip fundamentals, use standard
notation, cite code by section. Software: I am new to coding. Explain the
reasoning behind technical recommendations, name the tradeoff, and tell me
when I use a term wrong. Lead with the answer, then the reasoning. Correct me
when my framing is off or I'm solving the wrong problem. Prose over bullet
lists for reasoning. Show assumptions and units on anything quantitative. Say
"I'm not sure" rather than producing a confident number.

End every report with 'In plain terms:' followed by three lines: what
changed, what happens next, and what you need from me (or 'nothing'). Define
any software term the first time you use it in a report.

When you finish a task, update the pinned 'Slice status' GitHub issue: done,
now, next, waiting on Micah. When a slice closes, add its new deferred test
cases to the checklist of the release-review issue (#18, label
`release-blocker`; ADR 0006), and produce the registry review workbook for
that slice's drafted entries; verification is optional before release
(ADR 0008, as amended). Each slice's pull request bumps the version in
pyproject.toml to the slice's version, because the footer prints it. Move
the slice plan's binding engineering decisions into the brief before
marking the plan completed.

The repo documents are the only source of truth for this project. Don't rely
on, or write, auto-memory for it.

## Rules

1. Code values, provision text and formula citations live only in
   registry/code-values.toml, never typed into code. You may draft entries
   from memory or the web; each records its citation, source and status.
   Only I mark an entry verified. My verdict in the registry review
   workbook counts as me marking it; an agent records it in the registry.
   Any calc using a drafted entry prints the DRAFT stamp. Full rule:
   .claude/rules/code-values.md.
2. If the tool's result disagrees with my hand calc or the independent calc,
   stop and tell me. Don't change either side to match until we know which
   one is wrong.
3. Nothing client-identifying in the repo: no client names, project numbers,
   network paths, or job-specific references.
4. Hold the v1 scope in docs/brief/scope.md. Push back when I try to expand
   it.
5. Test case values (tests/cases/) come only from my hand calc or the
   independent calc. Tool output never fills or edits one, whether a
   printed number, a test failure message or `--json`. A value corrected
   after comparison keeps a note saying so.
6. The independent calc is written in a fresh session by the
   independent-calc skill (.claude/skills/independent-calc/SKILL.md), which
   never reads src/ or any tool output. A session that has read either
   never writes or edits an independent calc. Verification model:
   docs/brief/verification.md.

## Git

Calc code goes on a branch and reaches main only through a pull request I
approve. Calc code means anything that can change a printed calc: src/,
tests/, data/, and registry/ (a registry value feeds the calc). It also
means two brief texts that tests hold the code to: docs/brief/stops.md and
the "Stated assumptions" list in docs/brief/output.md. They change only on
a calc branch, in the same commit as the code they describe. Every other
docs-only change (the rest of docs/, .claude/, CLAUDE.md, CONTEXT.md,
CHANGELOG.md) can be committed directly on main and pushed to origin/main
without asking. Never force-push.

For small issues that can't change a printed number or calc text (stale
comments, doc wording, dead references), add them to the open
next-calc-branch cleanup issue without asking me. Only raise things with me
that affect calc results, calc text, or a decision.

## Agent skills

Issue tracker (GitHub Issues via `gh`): docs/agents/issue-tracker.md.
Triage labels: docs/agents/triage-labels.md. Domain docs (one CONTEXT.md
and docs/adr/): docs/agents/domain.md.
