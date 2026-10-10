# Brief: scope

Part of the product brief; index in docs/BRIEF.md. What the tool is, who
uses it, what v1 covers and excludes, and what is deferred to later
versions.

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
- The AISC 360-22 Chapter K chord limit states at the two HSS-to-HSS
  joints: the rail wall at the post (Check 3) and the post wall at the
  intermediate rail (Check 4b), for round and rectangular chords. A scope
  addition (Micah, 2026-10-09; S5-3, welds.md), built in slice 6. Until
  then they are a stated assumption, not checked, and the tool stops when
  a chord's D/t exceeds 50.
- Dead load of rails, post and baseplate: the AISC tabulated weight for
  database shapes, computed from area and steel density (a registry entry)
  for sections defined by dimensions and for the baseplate. A custom tube's
  wall is entered as the nominal wall: its weight uses that, and its
  strength uses the design wall (see checks.md; S5-8, inputs.md).

Out of scope for v1 (push back if I try to add these):
- Anchorage or substrate checks of any kind. The tool stops at the baseplate
  and reports reactions for Hilti PROFIS or Simpson Anchor Designer.
- Sloped and stair geometry
- Aluminum and stainless
- Infill: mesh, glass, pickets
- LRFD member checks
- Connection design beyond the fillet welds checked in Checks 3, 4b and 7
  and the chord limit states above (for example baseplate design)
- Automatic member selection. This is a checker, not an optimizer.
- Shear checks in any member (decided; stated in the output's assumptions)
- Slender sections, in flexure or compression. The tool stops and computes
  nothing (see checks.md).
- Combining guard loads with floor or roof live load, and wind, snow or ice
  on the guard

## Future versions (not v1)

- Mounting types with checks run by the tool: steel baseplate and anchor to
  steel, wood, cold-formed steel. Concrete stays as reactions reported for
  anchor software.
- Future code references as those mounts are added: ACI 318-19, the current
  AISI S100, the current NDS.
- LRFD member checks.
- Slender-section checks.
- A settings tab where the engineer picks display units.
