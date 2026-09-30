# Brief: verification

Part of the product brief; index in docs/BRIEF.md. How the tool is tested
against hand calcs and the shapes database.

## Verification

- Each of my hand calcs becomes an automated test case: its inputs and my
  hand-calculated values. Every change reruns all cases, and any value more
  than 0.5% (relative) from my hand value fails. The first slice's hand calc
  is test case 1; each later feature arrives with at least one hand-checked
  case.
- Section properties come from a file extracted by script from the
  unmodified AISC Shapes Database, and a test confirms the extracted file
  matches the original row for row.
