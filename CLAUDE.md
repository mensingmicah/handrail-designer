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

## Rules

1. Code values are never embedded silently. Any value drafted from memory is
   cited by document, edition and section and marked unverified until I check
   it. Never source code values from web search.
2. If the tool's result disagrees with my hand calc, stop and tell me. Don't
   change the tool to match until we know which one is wrong.
3. Nothing client-identifying in the repo: no client names, project numbers,
   network paths, or job-specific references.
4. Hold the v1 scope in docs/BRIEF.md. Push back when I try to expand it.

## Git

Commit directly on main; no feature branch needed. After any commit, push
to origin/main without asking. Never force-push.

## Agent skills

### Issue tracker

Issues live in this repo's GitHub Issues (private), managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
