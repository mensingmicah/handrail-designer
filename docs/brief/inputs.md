# Brief: inputs

Part of the product brief; index in docs/BRIEF.md. What the engineer enters
and how it is entered.

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
- The span is the tributary length for the post, a stated assumption
  (output.md)
- Every project has a post, post height and baseplate thickness: v1 always
  checks one post. A baseplate thickness of zero or less, or not less than
  h, is rejected at input. (Slice 2, D9.)
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
