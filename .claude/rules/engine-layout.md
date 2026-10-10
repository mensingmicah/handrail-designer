---
paths:
  - "src/handrail/**"
  - "tests/**"
---

# Where things are in the calc engine

Written in slice 5 step 1 (issue #21), when checks.py was split. Each
convention below is held by a test, named beside it.

## Modules (src/handrail/)

| Module | Holds |
| --- | --- |
| calc.py | Calc lines, the expression tree, number formatting, comparisons |
| directions.py | Direction, LoadType and Kind enums; the envelope orders |
| stops.py, errors.py | The id of every stop; the error classes that carry one |
| joints.py | Which section families may meet at each joint, as data |
| results.py | Case, Check, Loading, Results |
| loading.py | The guard loads and the dead load at the post |
| properties.py | The section properties block |
| flexure.py | §F8 flexural capacity, shared by Checks 1, 4a and 5 |
| rail.py | Checks 1 and 2 |
| intermediate.py | Check 4a |
| post.py | Checks 5 and 6 |
| welds.py | Checks 3, 4b and 7 |
| demand.py, reactions.py | The shared per-direction demand; the anchor reaction sets |
| validate.py, engine.py | Input validation; compute() and run() |
| report.py | The Typst source and the PDF |

engine.py imports every check at the top of the file. No module imports
another inside a function (tests/test_structure.py).

## Conventions

- **A printed-text change shows in the golden snapshots**
  (tests/test_golden.py, tests/golden/). A refactor leaves them
  byte-identical. A change made on purpose regenerates them in a commit of
  its own, one commit per intended change. An unexplained difference is a
  stop: find the cause before regenerating.
- **A decision line prints the comparison the code branched on.** Evaluate
  the relation once with `calc.compare` or `calc.order` and pass the result
  to `Sheet.decision`; never type a relation beside a separate `if`
  (ADR 0002).
- **A branch on a direction or a load type names its members and ends by
  refusing anything else** (`directions.unknown`). No bare `else`
  (tests/test_directions.py).
- **Every value line takes a key first**, then its Typst symbol:
  `sh.line("M_n", "M_n", ...)`. The key is a plain name, never printed; the
  test harness reads lines by key (tests/test_line_keys.py).
- **Every stop has an id.** Raising an input error needs
  `stop=Stop.SOMETHING`, a row in docs/brief/stops.md and a trigger in
  tests/test_stops.py, all in the same commit. A new section family needs
  its cells in joints.py and in stops.md's tables; a pair with no cell
  stops (S5-9).
- **`uv run ruff check .` and `uv run pyright` pass.** CI runs both. Not
  `ruff format`.
