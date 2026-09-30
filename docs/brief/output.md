# Brief: output

Part of the product brief; index in docs/BRIEF.md. Code references, stated
assumptions, and what the calc package prints and how.

## Code references

- AISC 360-22, Specification for Structural Steel Buildings
- ASCE 7-22, Minimum Design Loads and Associated Criteria for Buildings and
  Other Structures

The output lists the specification, not the design method, since LRFD member
checks may be added later. The design method is stated separately in the
front matter, as a registry-cited line ("Design method: ASD per AISC 360-22
§B3.2"), so the references list stays the same when LRFD is added.

## Stated assumptions (printed in the output)

- No shear checks in any member.
- Interior post; the tributary length is the span. End posts and rail
  overhangs are not checked.
- The top rail runs continuously over the post; the post is coped and
  welded to its underside. The rail is designed as a simple span.
- The intermediate rail's connection to the post, and the component load's
  effect on the post, are not checked.
- Guard loads are not combined with floor or roof live load; wind, snow and
  ice are not considered.
- Base reactions can reverse; direction is set in the anchor software.
- The baseplate is rigid; the post is fixed at the top of the baseplate.

## Output

- A PDF calculation package I can seal and a checker can follow with a
  calculator
- Each check opens with an envelope summary: every case checked, with its
  demand, capacity and ratio, so non-controlling cases are visibly checked.
  The full calculation with every intermediate value follows for the
  controlling case only.
- Every computed line shows symbol, expression, value and unit, with a code
  citation and a short margin note
- Every check shows its intermediate values, not just a ratio. If I can't
  reproduce a number by hand from what's shown, it's wrong.
- Order: front matter (project info, assumptions, references, an image area
  for a sketch or photo), dimensions, section properties, loading, the seven
  checks, a summary table (demand, capacity, ratio, controlling direction,
  pass/fail for each check), then the reaction tables
- Each check ends with its ratio and OK, or NG. Only deflection checks can
  be bypassed. A bypassed check shows no calculation, and the summary table
  shows a "Bypassed by engineer" row for it.
- Full internal precision; values displayed to 4 significant figures, so a
  checker can reproduce each intermediate and substituted value from the
  numbers printed before it. Ratios to 2 decimals; 3 when the rounded
  ratio would read 1.00; 4 when a failing ratio (over 1.0) would still
  read 1.000, so a ratio just over 1.0 shows its excess beside NG.
  Fixed units in v1: lb, lb-in, ksi, in, in³, in⁴.
- A reserved header area at the top, not filled in v1
- A footer on every page with the tool version and the code-value registry
  version the calc ran with
- A calc that uses any drafted (unverified) registry entry prints "DRAFT:
  contains unverified code values" on every page and lists those entries
- The inputs are saved as a plain-text project file alongside the PDF;
  reopening it regenerates the calc exactly
