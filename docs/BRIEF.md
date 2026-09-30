# Handrail Designer — Product Brief

This brief says what the tool must do and which engineering decisions are
already made. How the tool is built is recorded separately, in docs/adr/.

## What it is

A checker for baseplate-mounted steel guardrail and handrail systems. The
engineer enters geometry, member sizes, materials and loads. The tool checks
one post and one span and produces a hand-checkable calculation package in
the style of a Mathcad calc.

I am a licensed PE and the engineer of record for everything this tool
produces. I will seal its output.

## Who uses it

Me first. Later, possibly other engineers at my firm, including junior
engineers, once I trust it. Not public.

## v1 scope

In scope:
- Baseplate-mounted posts
- Level runs only; the engineer supplies the span, and sloped conditions are
  treated as flat
- Steel only. Standard shapes from AISC Shapes Database v16.0: AISC pipe,
  round HSS, rectangular HSS. Solid round bar and solid rectangular bar are
  not in the database and are always defined by dimensions (diameter, or
  width and thickness). Custom tube sections defined by dimensions.
- ASD member checks
- ASCE 7-22 guard loading, with an option to exempt the occupancies where the
  distributed load need not be considered
- Dead load of rails, post and baseplate: the AISC tabulated weight for
  database shapes, computed from area and steel density (a registry entry)
  for sections defined by dimensions and for the baseplate. A custom tube's
  weight uses the wall thickness as entered; its strength uses the design
  thickness (see decisions).

Out of scope for v1 (push back if I try to add these):
- Anchorage or substrate checks of any kind. The tool stops at the baseplate
  and reports reactions for Hilti PROFIS or Simpson Anchor Designer.
- Sloped and stair geometry
- Aluminum and stainless
- Infill: mesh, glass, pickets
- LRFD member checks
- Connection design
- Automatic member selection. This is a checker, not an optimizer.
- Shear checks in any member (decided; stated in the output's assumptions)
- Slender sections, in flexure or compression. The tool stops and computes
  nothing (see decisions).
- Combining guard loads with floor or roof live load, and wind, snow or ice
  on the guard

## Inputs

- Project info: name, phase, one-line description, reference documents,
  and additional assumptions. The tool's own stated assumptions are locked
  and always printed; the engineer can add to them but not edit or remove
  them.
- A note on the input page states that loading is per ASCE 7-22. The PDF
  covers this through its code references.
- Distributed-load exemption: a checkbox. Ticking it opens a short text box
  where the engineer states that the guard falls under the ASCE 7-22
  §4.5.1.1 exemption; that text prints on the loading page. An info box next
  to the checkbox explains the exemption's requirements; its text comes from
  registry entries.
- Post height h, from top of concrete to the top rail centerline; span (post
  to post, center to center); baseplate thickness t_p and plan dimensions
  B × N. B and N give the baseplate weight and print beside the anchor
  reaction sets.
- For now the span is assumed to be the tributary length for the post
- Top rail and post sections: pick an AISC designation, or define a custom
  section by dimensions. For tubes, the engineer says whether the entered wall
  thickness is nominal or design. For rectangular sections, the engineer sets
  which axis resists the horizontal guard load.
- Intermediate rail section (optional). Defaults to the top rail section.
- Material grade for rail, post and baseplate. The standard grade lists for
  pipe, round HSS and rectangular HSS are registry entries
  (material.grades.pipe, material.grades.hss_round, material.grades.hss_rect;
  AISC Manual Table 2-4); a grade outside the list for the shape is an
  unusual pairing and gets a warning, not a block. The grade list for solid
  bars and baseplate is not yet in the registry. A500 (Gr B, Gr C) is offered
  for round and rectangular HSS only, never for solid bars, and the defaults
  are bars A36, pipe A53 Gr B, baseplate A36: these are my engineering
  decisions, not registry entries. Every Fy and Fu is a registry entry
  citing the AISC Manual: Table 2-4 for shapes (pipe, HSS), Table 2-5 for
  plates and bars (for example, A36 Fy per Table 2-5).
- Welds at the rail to post and post to baseplate connections: fillet welds,
  size entered, E70XX electrode by default. Round posts are welded all
  around. Rectangular posts (HSS or bar) are welded all around or on one
  pair of faces, which the engineer picks by the section's width or depth
  faces.
- Guard loads (concentrated, distributed, component), defaulting to code
  values, editable
- Deflection limits: L/120 for the rail span and L/60 for the post
  cantilever by default. These are engineering experience, not code. Each is editable
  and each can be bypassed by checkbox.
- Dimensions must accept the forms engineers actually type: 5' 6-1/8",
  66.125 in, 3 ft 6 in, 42. A bare number is inches in every field. The
  normalized value is echoed in gray next to the box (42 → 3'-6") and again
  on the calc's dimensions page.

## Checks

1. Top rail bending (simple span)
2. Top rail deflection: downward case D + L on the vertical axis; horizontal
   cases live load only on the horizontal axis; upward case live load only,
   computed and shown though it will not control; run over the full envelope
3. Top rail weld to post: horizontal shear V plus the moment V·e, where e is
   the distance from the rail centerline to the weld plane. Downward load
   passes through the weld; no credit is taken for bearing at the cope.
4. Intermediate rail component check: the ASCE 7-22 §4.5.1.2 component load,
   applied horizontally at midspan of the intermediate rail spanning between
   posts. It acts alone: not combined with dead load and not concurrent with
   the top-rail loads. Computed every time, even when the intermediate rail
   is the same section as the top rail. Includes a deflection check under
   the component load, default L/120, editable and bypassable. If there is
   no intermediate rail, the check shows "none".
5. Post combined axial and flexure (cantilever)
6. Post deflection (cantilever), horizontal live load only, over the
   cantilever length h − t_p; the L/60 limit uses the same length
7. Post weld to baseplate

Weld checks (3 and 7) use the elastic method, treating the weld as a line.
The AISC 360-22 §J2.4 directional strength increase is allowed for fillet
welds, based on the angle between the weld force and the weld axis; its
limits on weld groups loaded at varying angles, and any Chapter K
restrictions for welds to HSS, are registry entries to verify, and the
increase is not assumed to apply everywhere. Base metal: per inch of weld,
weld shear strength on the throat is compared with base metal shear rupture
over the thickness on the fusion face (§J2.4 with §J4.2), for both
connected parts (post wall and rail, or post wall and baseplate); the lower
governs. Minimum and maximum fillet sizes are pass/fail lines. The rail to
post weld length is the post perimeter, conservative against the true
saddle length. The post to baseplate weld moment arm is h minus the
baseplate thickness.

Flexural capacity: top rail Lb = span, with Cb from the §F1 moment diagram
for each load case. Post Lb = h using the §F1 cantilever provision. Post
compression uses the recommended design K. In the upward case the post is
checked for axial tension (yielding on the gross section); it is computed
and shown in the envelope summary even though it will not control.

Plus reporting, not pass/fail: factored (LRFD) base reactions for a concrete
substrate, labeled for direct input into anchor software (see decisions).

## Code references

- AISC 360-22, Specification for Structural Steel Buildings
- ASCE 7-22, Minimum Design Loads and Associated Criteria for Buildings and
  Other Structures

The output lists the specification, not the design method, since LRFD member
checks may be added later.

## Engineering decisions already made

- Load direction: the guard load is applied in whichever direction produces
  the worst case for the component being checked. The cases are outward,
  inward, downward, upward and longitudinal (parallel to the rail). Each check runs the envelope of direction
  cases, finds its own controlling direction and reports it; two checks
  controlled by different directions is expected, not a conflict. For some
  members the controlling case has live load parallel to dead load; for
  others (a flat bar loaded about its weak axis, for example) a horizontal
  case may control.
- Longitudinal is a real load case, not only a reaction row. It enters the
  post interaction, post deflection and both welds, since a rectangular post
  may take it on the weak axis. Both guard loads apply at the top of the
  post, the same way as the transverse case: the concentrated load, and the
  distributed load times the tributary length. The longitudinal distributed
  load is engineering judgement. The top rail carries it axially and is not
  checked for it.
- Downward is kept. It is the only case where live load shares the dead-load
  bending axis in the rail, and the only case that puts live axial
  compression into the post.
- Biaxial bending (dead load about one axis, horizontal guard load about the
  other): round HSS and pipe use the square root of the sum of the squares
  of the two moments against a single capacity, which is exact for a round
  section. All other sections use the AISC 360-22 provisions for combined
  strong- and weak-axis bending.
- Upward opposes dead load, so it uses a minimum-dead-load combination, not
  D + L. The ASD member check uses 0.6D + 1.0L. ASCE 7-22 has no combination
  for this case, so the output labels it "engineering judgement", not as an
  ASCE combination. Crediting a reduced dead load is deliberate: the point of
  the tool is to sharpen the pencil.
- Dead and live effects stay separate until each check combines them, so one
  analysis produces both the ASD member checks and the factored reactions.
- Base reactions (v1, concrete substrate only): LRFD, for direct input into
  anchor software; no service reactions in v1. Three sets are reported, as
  separate, non-interacting load cases: (1) transverse load, 0.9D + 1.6L;
  (2) longitudinal load, 0.9D + 1.6L; (3) upward load, 0.9D + 1.6L, only if
  there is net tension. Both combinations are engineering judgement, not
  ASCE combinations, and are labeled that way. Reactions are reported on
  their own axes at the top of concrete (moment arm h), with a note that
  loads can reverse; the engineer sets direction in the anchor software.
  Dead load includes the top rail, the post and the intermediate rail. Each
  set is simultaneous: the shear, axial and moment that occur together in that
  case, never a max of each component. A max-of-everything row is a load
  case that never happens and misleads the anchor software.
- Section classification runs before capacity. Compact computes normally.
  Noncompact computes at reduced capacity and is flagged visibly, with the
  width-to-thickness ratio and limits shown. Slender, in either flexure
  (AISC 360-22 Table B4.1b) or compression (Table B4.1a), is a hard stop
  that names the element, its ratio and the limit. Slender-member checks may
  be added later if the need shows up.

- Biaxial SRSS applies to every round section, solid round bar included.
- Standard-section properties are used exactly as published in the
  database, even when the grade (A1085, for example) implies a different
  design wall thickness; the output notes it. Custom rectangular tubes use
  the AISC corner-radius convention, a registry entry. Custom tubes convert
  nominal to design wall thickness per AISC 360-22 §B4.2, a registry entry.
- Custom tube thickness: dead weight uses the wall thickness as entered.
  Strength and section properties use the design thickness, reduced from
  nominal when the input is marked nominal. This matches AISC's convention
  (tabulated weight on nominal wall, properties on design wall).

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

## Future versions (not v1)

- Mounting types with checks run by the tool: steel baseplate and anchor to
  steel, wood, cold-formed steel. Concrete stays as reactions reported for
  anchor software.
- Future code references as those mounts are added: ACI 318-19, the current
  AISI S100, the current NDS.
- LRFD member checks.
- Slender-section checks.
- A settings tab where the engineer picks display units.

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
  numbers printed before it. Ratios to 2 decimals, or 3 when the rounded
  ratio would read 1.00, so a ratio just over 1.0 never prints as 1.00
  beside NG. Fixed units in v1: lb, lb-in, ksi, in, in³, in⁴.
- A reserved header area at the top, not filled in v1
- A footer on every page with the tool version and the code-value registry
  version the calc ran with
- A calc that uses any drafted (unverified) registry entry prints "DRAFT:
  contains unverified code values" on every page and lists those entries
- The inputs are saved as a plain-text project file alongside the PDF;
  reopening it regenerates the calc exactly

## Verification

- Each of my hand calcs becomes an automated test case: its inputs and my
  hand-calculated values. Every change reruns all cases, and any value more
  than 0.5% (relative) from my hand value fails. The first slice's hand calc
  is test case 1; each later feature arrives with at least one hand-checked
  case.
- Section properties come from a file extracted by script from the
  unmodified AISC Shapes Database, and a test confirms the extracted file
  matches the original row for row.
