# Brief: loads and envelope

Part of the product brief; index in docs/BRIEF.md. Direction cases, load
combinations, dead/live separation, and the anchor reaction sets.

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
