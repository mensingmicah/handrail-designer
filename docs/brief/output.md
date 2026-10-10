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

The front matter's references list also names the AISC Steel Construction
Manual, 16th Edition, and the AISC Shapes Database v16.0. (Slice 1.)

## Stated assumptions (printed in the output)

- No shear checks in any member.
- Interior post; the tributary length is the span. End posts and rail
  overhangs are not checked.
- Post loads use tributary length = span; rail continuity effects on post
  reactions are neglected (engineering judgement).
- The top rail runs continuously over the post; the post is coped and
  welded to its underside. The rail is designed as a simple span.
- The rail to post weld is modeled as a flat ring of the post's perimeter
  at the underside of the rail, with eccentricity e = half the rail depth
  from the rail centerline; this is conservative against the saddle
  centroid (2R/π for equal round diameters). It is modeled as a fillet of
  the entered size all around, although at equal diameters the sides of
  the saddle form a flare-bevel joint.
- The intermediate rail to post weld is modeled as a flat ring of the
  intermediate rail's perimeter at the post face, a simple shear
  connection consistent with the simple-span intermediate rail: the end
  reaction acts at the weld with no end moment. It is modeled as a fillet
  of the entered size all around, although at equal diameters the sides
  of the saddle form a flare-bevel joint.
- Local strength of the rail wall at the post, and of the post wall at the
  intermediate rail (AISC 360-22 Chapter K chord limit states), is not
  checked; the chord's D/t is limited to 50, the Chapter K limit of
  applicability.
- The component load's effect on the post is not checked.
- Guard loads are not combined with floor or roof live load; wind, snow and
  ice are not considered.
- Base reactions can reverse; direction is set in the anchor software.
- The baseplate is rigid; the post is fixed at the top of the baseplate.
- Baseplate thickness and bending are not checked; baseplate and anchorage
  design by others (e.g., PROFIS).
- Notional loads (AISC 360-22 App. 7) are neglected. In gravity-only
  combinations they produce a negligible moment, and the reported
  axial-only ratio bounds the H1-1b result.

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
  contains unverified code values" on every page and lists those entries.
  The list prints once, in the front matter, and the stamp on every page
  points to it. (Slice 1.)
- Until the v1 release, every page carries a "DEVELOPMENT — NOT FOR
  CONSTRUCTION" watermark; removing it is my call alone (docs/ROADMAP.md,
  slice 9). (Slice 1.)
- The footer's tool and registry versions are the git commits of the code
  and of the registry file, with "page x of y". If either has uncommitted
  changes when the calc runs, "uncommitted changes" prints beside that
  commit, so a printed calc can always be traced to exact code. (Slice 1.)
- The dimensions page shows each dimension as entered and normalized
  (72 → 6'-0"). Each derived length (h − t_p, Lc) prints the note, formula
  and value of the calc line that computed it. (Slices 1 and 2.)
- Under the dimensions table, one line echoes the engineer's election of
  the directional strength increase at the post to baseplate weld:
  "elected by the engineer" or "not elected", with the input's value.
  Where it is elected, Check 7 prints a line under k_ds saying the
  increase is applied at the engineer's election, with its basis.
  (Micah, 2026-10-10; welds.md, W2 as revised.)
- The Check 5 envelope table has an αPr/Pe column, with "—" for the
  downward and upward cases, so the value is visible for every case the
  second-order stop checks; the printed sentence goes in the calc lines.
  Each capacity (Pc or Pt, and Mc) prints under its demand. The Check 5
  calc lines name the interaction equation used. (Slice 2, D1.)
- Reaction tables (S4-7, Micah 2026-10-08). Each set prints V, N and M
  at 4 significant figures in lb and lb-in. N is signed in the
  anchor-software convention, with its sense in words: "N = +268 lb
  (tension)", "N = −52.1 lb (compression)". The lateral set prints "V and
  M act in the same vertical plane; M = V·h." Each set shows its
  combination label (0.9D + 1.6L, engineering judgement), the governing
  load type (S4-5), and the D breakdown (top rail, intermediate rail,
  post, baseplate) with its total. Under each table: "N positive =
  tension (uplift), matching common anchor-software convention. V and M
  are reversible; apply them in the governing direction." B × N prints
  beside the tables with its orientation (S4-6).
- The inputs are saved as a plain-text project file alongside the PDF;
  reopening it regenerates the calc exactly
