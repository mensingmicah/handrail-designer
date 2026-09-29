# Handrail Designer — Product Brief

This brief says what the tool must do and which engineering decisions are
already made. It says nothing about how to build the tool: platform,
language, libraries and architecture are all open, and I want the tradeoffs
explained before any are chosen.

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
- Dead load of rail and post: the AISC tabulated weight for database shapes,
  computed from section area for sections defined by dimensions

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

- Project info: name, phase, one-line description, assumptions text (we should provide some basic assumptions about steel weight etc.),
  reference documents
- Post height (ground to center of top rail), span (post to post, center to
  center)
- For now the span is assumed to be the tributary length for the post
- Top rail and post sections: pick an AISC designation, or define a custom
  section by dimensions. For tubes, the engineer says whether the entered wall
  thickness is nominal or design. For rectangular sections, the engineer sets
  which axis resists the horizontal guard load.
- Intermediate rail section (optional). Defaults to the top rail section.
- Material grade for rail, post and baseplate, with sensible defaults. Bars
  default to A36. An unusual grade pairing gets a warning, not a block; the
  engineer may pick a nonstandard grade for a shape (for example A500 Gr B or
  Gr C for a bar).
- Weld size and type at the rail to post connection and the post to base connection. for now it can be a two sided or all around fillet weld.
- Guard loads (concentrated, distributed, component), defaulting to code
  values, editable
- Deflection limits: L/120 for the rail span and L/60 for the post
  cantilever by default. These are engineering experience, not code. Each is editable
  and each can be bypassed by checkbox.
- Dimensions must accept the forms engineers actually type: 5' 6-1/8",
  66.125 in, 3 ft 6 in, 42

## Checks

1. Top rail bending (simple span)
2. Top rail deflection
3. Top Rail weld to post
4. Intermediate rail component check: the ASCE 7-22 §4.5.1.2 component load,
   applied horizontally at midspan of the intermediate rail spanning between
   posts. It acts alone: not combined with dead load and not concurrent with
   the top-rail loads. Computed every time, even when the intermediate rail
   is the same section as the top rail.
5. Post combined axial and flexure (cantilever)
6. Post deflection (cantilever)
7. Post weld to baseplate

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
  inward, downward and upward. Each check runs the envelope of direction
  cases, finds its own controlling direction and reports it; two checks
  controlled by different directions is expected, not a conflict. For some
  members the controlling case has live load parallel to dead load; for
  others (a flat bar loaded about its weak axis, for example) a horizontal
  case may control.
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
  anchor software. Two sets are reported: the worst-case moment
  (0.9D + 1.6L, horizontal) and the worst-case vertical tension
  (0.9D + 1.6L, upward), the latter only if there is net tension. Each set
  is simultaneous: the shear, axial and moment that occur together in that
  case, never a max of each component. A max-of-everything row is a load
  case that never happens and misleads the anchor software.
- Section classification runs before capacity. Compact computes normally.
  Noncompact computes at reduced capacity and is flagged visibly, with the
  width-to-thickness ratio and limits shown. Slender, in either flexure
  (AISC 360-22 Table B4.1b) or compression (Table B4.1a), is a hard stop
  that names the element, its ratio and the limit. Slender-member checks may
  be added later if the need shows up.

## Open engineering questions (mine to answer)

1. Top rail deflection: dead plus live, with the controlling case being live
   load in line with dead load. Still open: whether the perpendicular
   (horizontal) case can be ignored for every section and orientation.

## Future versions (not v1)

- Mounting types with checks run by the tool: steel baseplate and anchor to
  steel, wood, cold-formed steel. Concrete stays as reactions reported for
  anchor software.
- Future code references as those mounts are added: ACI 318-19, the current
  AISI S100, the current NDS.
- LRFD member checks.
- Slender-section checks.

## Output

- A PDF calculation package I can seal and a checker can follow with a
  calculator
- Every computed line shows symbol, expression, value and unit, with a code
  citation and a short margin note
- Every check shows its intermediate values, not just a ratio. If I can't
  reproduce a number by hand from what's shown, it's wrong.
- Order: front matter (project info, assumptions, references, an image area
  for a sketch or photo), dimensions, section properties, loading, the seven
  checks, a summary table (demand, capacity, ratio, controlling direction,
  pass/fail for each check), then the reaction tables
- Each check ends with its ratio and OK, or NG. If bypassed, do not show the calculation
- A reserved header area at the top, not filled in v1
