---
paths:
  - "registry/**"
  - "src/handrail/**"
---

# Code-value registry (CLAUDE.md rule 1, in full)

Code values and code provision text live only in the code-value registry
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

Editing a verified entry: a change to its note or edition field keeps it
verified, since neither prints in the calc. A change to its value, unit,
cite or section sends it back to drafted: set status "drafted", blank
verified-by and date, and add its id to the review list.
