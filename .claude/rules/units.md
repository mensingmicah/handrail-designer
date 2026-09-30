---
paths:
  - "src/handrail/**"
---

# Units in the calc engine

From ADR 0003 (pint) and the calc-code-review checklist; this states them
as a rule for writing the code, not only for reviewing it.

- Every dimensioned value is a pint quantity from the one registry in
  src/handrail/units.py (`ureg`, `Q_`). Never create a second
  `UnitRegistry`.
- Forces are `lbf` internally; pint's `lb` is mass. The PDF prints `lb`.
- Quantities keep their units through the whole calc. Unit conversion and
  unit stripping (`.magnitude`, `.m`, `float()`) happen only at input
  parsing and display rendering.
