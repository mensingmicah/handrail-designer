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
- Steel only: AISC pipe, round HSS, rectangular HSS, solid round bar, solid
  rectangular bar (standard shapes from AISC Shapes Database v16.0), plus
  custom sections defined by dimensions
- ASD member checks
- ASCE 7-22 guard loading, with an option to exempt the occupancies where the
  distributed load need not be considered
- Dead load of rail and post, computed from member weights or provided by AISC when not using a custom shape

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

## Inputs

- Project info: name, phase, one-line description, assumptions text (we should provide some basic assumptions about steel weight etc.),
  reference documents
- Post height (ground to center of top rail), span (post to post, center to
  center)
- For now the span is assumed to be the tributary area
- Top rail and post sections: pick an AISC designation, or define a custom
  section by dimensions. For tubes, the engineer says whether the entered wall
  thickness is nominal or design. For rectangular sections, the engineer sets
  which axis resists the horizontal guard load.
- Material grade for rail, post and baseplate, with sensible defaults. An
  unusual grade pairing gets a warning, not a block.
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
4. Guard component check: component load at midspan of the member spanning
   between posts, not concurrent with the top-rail loads
5. Post combined axial and flexure (cantilever)
6. Post deflection (cantilever)
7. Post weld to baseplate

Plus reporting, not pass/fail: base reactions (shear, axial, moment) in both
service and factored form, labeled for use in external anchor software.

## Engineering decisions already made

- Load direction: the guard load is applied in whichever direction produces
  the worst case for the component being checked. The cases are outward,
  inward, downward and upward. Each check finds its own controlling direction
  and reports it; two checks controlled by different directions is expected,
  not a conflict.
- Downward is kept. It is the only case where live load shares the dead-load
  bending axis in the rail, and the only case that puts live axial
  compression into the post.
- Upward opposes dead load, so it needs a minimum-dead-load combination, not
  D + L. It must never credit dead load against uplift.
- Dead and live effects stay separate until each check combines them. The
  tool has to produce ASD member checks and both service and factored
  reactions from the same analysis.
- Base reactions are reported as one simultaneous set per direction case, not
  as a max of each component. Moment peaks in the horizontal cases and axial
  in the downward case; a max-of-everything row is a load case that never
  happens and misleads the anchor software.
- Section classification runs before flexural capacity. Compact computes
  normally. Noncompact computes at reduced capacity and is flagged visibly,
  with the width-to-thickness ratio and limits shown.

## Open engineering questions (mine to answer)

1. Rail dead load is vertical; horizontal guard load bends the rail about
   the other axis. How to combine them: vector resultant (exact for round
   sections), biaxial interaction (general, conservative for rounds), or
   ignore the coupling? The earlier proposal was resultant for round
   sections and interaction for rectangular.
2. Deflection: live only, or dead plus live? If both, combined how, given
   the same two-axis issue?
3. Slender sections: stop with an error, or compute a reduced capacity? The
   earlier proposal was a hard stop, since a slender handrail member is a
   selection error.
4. Does the component check include the member's self-weight?
5. Do guard loads combine with floor or roof live load?
6. Fy for A500 when it's selected for a solid bar.

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


