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
- The concentrated and distributed guard loads are separate load types,
  never concurrent, and each is run through the envelope. The
  distributed-load exemption removes the distributed load. On the top
  rail, the concentrated load P acts at midspan of the simple span and the
  distributed load w along it. On the post, both act at the top: P, and
  w·s with the span s as the tributary length. (Slices 1 and 2.)
- Dead load at the post: D = w_D,rail·s + D_post, with D_post = W·(h − t_p),
  the tabulated weight over the length from the top of the baseplate to
  the top rail centerline. All of it acts as axial load at the critical
  section. The span is the tributary length, with no increase for rail
  continuity (a stated assumption, output.md). (Slice 2, D2 and D11.)
- The post envelope, at the top of the baseplate:

  | Case | Axial Pr | Moment Mr | Combination |
  | --- | --- | --- | --- |
  | Downward | D + L, compression | 0 | ASCE 7-22 ASD D + L |
  | Outward, inward | D, compression | L·(h − t_p) | ASCE 7-22 ASD D + L |
  | Longitudinal | D, compression | L·(h − t_p) | ASCE 7-22 ASD D + L |
  | Upward | 1.0L − 0.6D, tension | 0 | 0.6D + 1.0L, engineering judgement |

  Outward and inward are identical for a round post, and longitudinal
  equals transverse, but all are listed so the envelope is explicit. If
  0.6D ≥ L, the upward case shows "no net tension; compression covered by
  downward" and is not checked. (Slice 2.)
- For round sections the five direction cases cover the ASCE 7-22 "any
  direction". An inclined load trades moment for axial load: in Eq. H1-1b
  the worst inclination above horizontal is θ = atan[Mc/(2Pc·(h − t_p))],
  and the ratio rises by the factor √(1 + tan²θ). That increase is
  negligible whenever Mc is much smaller than 2Pc·(h − t_p), which holds
  for guard posts, whose axial capacity far exceeds their lateral load.
  (Ruled 2026-10-03.)
- Dead and live effects stay separate until each check combines them, so one
  analysis produces both the ASD member checks and the factored reactions.
- Base reactions (v1, concrete substrate only): LRFD, for direct input into
  anchor software; no service reactions in v1. Two sets are reported, as
  separate, non-interacting load cases (S4-4, Micah 2026-10-08, replacing
  the earlier three sets, transverse, longitudinal and upward):
  (1) lateral: the horizontal guard load at the top of the post, in any
  horizontal direction, 0.9D + 1.6L; (2) upward, 0.9D + 1.6L, only when
  there is net tension (1.6L > 0.9D). Both combinations are engineering
  judgement, not ASCE combinations, and are labeled that way.
  - One lateral set covers transverse and longitudinal because in v1 they
    give identical reactions: both guard loads act at the top of the post
    with the span as the tributary length, so V, M and D are the same.
    The set prints the note: "Lateral set applies in any horizontal
    direction; enter it in the anchor software in the orientation that
    governs the anchor pattern. Loads can reverse." To revisit if the
    longitudinal load is ever modeled differently, for example a
    multi-span frame with moment-connected posts (docs/ROADMAP.md, after
    v1).
  - Each set uses the larger of the two guard load types, P or w·s, at
    the top of the post, and names the type. The smaller is enveloped
    in every component with the same D, so the set stays simultaneous.
    With the exemption on, P is the only type. If P = w·s, one set is
    reported naming both. (S4-5, Micah 2026-10-08.)
  - Reactions are reported at the top of concrete (moment arm h). Dead
    load includes the top rail, the post and the intermediate rail. Each
    set is simultaneous: the shear, axial and moment that occur together
    in that case, never a max of each component. A max-of-everything row
    is a load case that never happens and misleads the anchor software.
