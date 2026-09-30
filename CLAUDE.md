# Handrail Designer

A checker for baseplate-mounted steel guardrail and handrail systems that
produces a hand-checkable calculation package. The product brief is
docs/BRIEF.md; read it before any design or build work.

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

The repo documents are the only source of truth for this project. Don't rely
on, or write, auto-memory for it.

## Rules

1. Code values and code provision text live only in the code-value registry
   (registry/code-values.toml). Every formula or equation the tool uses also
   has a registry entry giving its reference (beam formulas cite AISC Manual
   Table 3-23 by case number); the equation itself is implemented once in
   the code and prints that citation. A value read from a table cites that
   table (Fy and Fu: AISC Manual Table 2-4 for shapes, Table 2-5 for plates
   and bars). Claude may draft entries from memory or the
   web. Each drafted entry records the value or text; the document, edition
   and exact section, table or equation; the source, one of "memory", the
   URL, or "engineer" for a value I supplied directly; status "drafted"; and
   blank verified-by and date fields that only I fill in. An entry with
   source "engineer" stays "drafted" until I verify it, like any other. Every drafted entry is listed in the review list at the top of
   the registry. Any calc that uses a drafted entry prints "DRAFT: contains
   unverified code values" on every page and lists those entries. The tool
   stops with an error naming any entry it needs that does not exist.
2. If the tool's result disagrees with my hand calc, stop and tell me. Don't
   change the tool to match until we know which one is wrong.
3. Nothing client-identifying in the repo: no client names, project numbers,
   network paths, or job-specific references.
4. Hold the v1 scope in docs/BRIEF.md. Push back when I try to expand it.

## Git

Calc code goes on a branch and reaches main only through a pull request I
approve. Calc code means anything that can change a printed calc: src/,
tests/, data/, and registry/ (a registry value feeds the calc). Docs-only
changes (docs/, CLAUDE.md, CONTEXT.md) can still be committed directly on
main and pushed to origin/main without asking. Never force-push.

## Agent skills

### Issue tracker

Issues live in this repo's GitHub Issues (private), managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
