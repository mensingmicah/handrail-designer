---
name: independent-calc
description: Write the independent calc for one test case, in a fresh session. Usage /independent-calc case-02.
disable-model-invocation: true
argument-hint: case-NN
---

# Independent calc

You are the second calc for test case `$ARGUMENTS`. Another agent wrote the
tool; you work the same problem from the code and the inputs alone, the way
an independent checker works a calc without opening the designer's. Your
whole value is **independence**: a number that agrees with the tool only
because it was copied, or nudged toward the tool, is worthless. Verification
model: docs/brief/verification.md.

## Your sources

Read exactly these, through the commands given where one is given:

- **Case inputs.** The case file with its value tables stripped:

  ```bash
  uv run python -c "import tomllib,sys,json; d=tomllib.load(open(sys.argv[1],'rb')); [d.pop(k,None) for k in ('hand','independent')]; print(json.dumps(d,indent=2))" tests/cases/$ARGUMENTS.toml
  ```

- **The brief:** docs/BRIEF.md and every file in docs/brief/.
- **CONTEXT.md**, for the project's terms.
- **The current slice plan** in docs/plans/ (the newest one not marked
  completed): its decisions bind you exactly as they bind the tool. Use
  the plan's decisions only. Ignore any computed values in it (ratios, Pe,
  Lc/r, equation branches for specific cases); derive every number
  yourself.
- **Verified registry entries**, and only those:

  ```bash
  uv run python -c "import tomllib,json; r=tomllib.load(open('registry/code-values.toml','rb')); print(json.dumps([e for e in r['entry'] if e['status']=='verified'],indent=2,default=str))"
  ```

- **Section properties** from AISC's original workbook, one row per section
  (US customary columns). Run it once for each section in the case (rail,
  post and, where the case has one, the intermediate rail):

  ```bash
  uv run python -c "import openpyxl,sys
  ws=openpyxl.load_workbook('data/aisc-shapes-database-v16.0.xlsx',read_only=True,data_only=True)['Database v16.0']
  rows=ws.iter_rows(values_only=True); h=next(rows); n=h.index('AISC_Manual_Label',3)
  for r in rows:
      if r[2]==sys.argv[1]: print({k:v for k,v in zip(h[:n],r[:n]) if v not in (None,'–')})" Pipe1-1/2STD
  ```

- **Your own reading of the code** (AISC 360-22, the AISC Manual, ASCE
  7-22), from memory or the web, for any value or provision with no
  verified entry. Record the document, edition, section and source of each.

Everything else in the repo is off limits: src/, tests/ beyond the
commands here and the two files you write, the shapes TOML in data/,
drafted registry entries, git history and diffs, and every tool output (PDF, Typst source, `--json`, test runs, the
`handrail` command). If the calc seems to need something only those hold,
write it as an open question in the calc and carry on with your own
reading.

Named, because each of these holds tool output or is derived from it:

- **tests/golden/**, every file in it and in tests/golden/extra/: the
  printed calcs and stop messages the tool produced, saved as snapshots.
- **tests/golden_scenarios.py**, the inputs of the direct snapshots.
- **Every other file under tests/**: every test file, every other case
  file, and every other case's independent calc and values. In tests/ you
  read only your own case file, through the command above, and your own
  values template, tests/cases/independent/$ARGUMENTS.toml, in step 7.
- **Everything in out/** except out/aisc-360-22.pdf, the Specification's
  own text, which you may read. The rest of out/ is calc PDFs, review
  workbooks and saved patches.

## Steps

1. **Confirm the session is clean.** This session must not have read
   src/, tests/ (tests/golden/ and tests/golden_scenarios.py included),
   out/ other than out/aisc-360-22.pdf, tool output or drafted registry
   entries before this skill started. If it has, stop and tell Micah to start a fresh session.
   Done when you have checked the transcript so far.
2. **Read your sources.** Done when you have the case inputs, the plan's
   decisions, every verified entry and each section's row.
3. **List the limit states.** For every member and connection in the
   case, list every limit state the code could apply, from the code rather
   than from the plan's list of checks, and say why each does or doesn't
   apply here. Done when nothing that could govern is missing, including
   ones the plan doesn't mention; flag those for Micah.
4. **Trace the load path.** For every load (each member's dead load, each
   guard load type, the component load where it applies): its magnitude,
   direction, point of application, combination, and how it reaches each
   critical section. List every envelope case. Done when every direction
   case of every load is accounted for and the worst case of each check is
   identified by calculation, not assumed.
5. **Work the calc.** Every check in the plan's scope, every envelope case,
   every branch condition evaluated (classification, branch limits,
   interaction thresholds). Use Python's standard library as a calculator
   (`python -c`); carry full precision and round only when reporting, to
   four significant figures. Done when every case of every check ends in a
   ratio, or a stated reason it isn't checked.
6. **Run Micah's review checklist** (docs/brief/verification.md) on your
   own calc, items 1–9, and fix what it finds. Done when each item is
   answered in the calc's last section.
7. **Fill the values file.** Only now, print the key names the test
   compares, from the values template (names only):

   ```bash
   uv run python -c "import tomllib,sys
   def keys(d,p=''):
       for k,v in d.items(): yield from (keys(v,p+k+'.') if isinstance(v,dict) else [p+k])
   print('\n'.join(keys(tomllib.load(open(sys.argv[1],'rb'))['independent'])))" tests/cases/independent/$ARGUMENTS.toml
   ```

   Replace each "pending" with your value, in the unit its suffix names.
   Forces are positive magnitudes; the case name gives the sense (an
   upward P_r is tension, recorded as a positive number). Done when every key has a value, and you have listed any key you could not fill
   and any value you computed that has no key. Both are findings for
   Micah: a check one side has and the other doesn't.
8. **Write, commit and report.** Write the two files below and commit them
   on the current branch (never main). Commit; do not push. The pre-push
   hook runs the test suite, which can print tool values. Then tell Micah: the files, every value
   taken from your own reading rather than a verified entry, every open
   question, and the mapping gaps from step 7. Stop there; the comparison
   with the tool is run by someone else.

## The calc: tests/cases/independent/$ARGUMENTS.md

Written as a hand calc a junior engineer would hand Micah for review,
complete enough to follow with a calculator.

- **Header:** the case, date, your model, the branch and commit you ran
  on, and every source you read.
- **Sections, in order:** inputs; limit states considered (step 3); loads
  and load path (step 4); section properties; one section per check, with
  case-independent capacities first, then every envelope case in full; a
  summary of each check's controlling case and ratio; values from your own
  reading; open questions; the checklist (step 6).
- **Every line:** symbol, equation, values substituted, result with units,
  the citation (document, edition, section or equation), and its source:
  a verified entry's id, or "own reading" with memory or the URL.

## The values: tests/cases/independent/$ARGUMENTS.toml

The file already exists as a template, every key "pending". Fill in
`[provenance]` and replace each "pending":

```toml
[provenance]
calc = "tests/cases/independent/case-NN.md"
written_on = 2026-01-01
model = "your model id"
commit = "the commit you ran on"

[independent]
check5.ratio.outward_concentrated = "pending"   # becomes your number
# ... one line per key the test compares
```

Numbers are bare TOML numbers; text values (an equation name, a
controlling case) are quoted, as the key names show.
