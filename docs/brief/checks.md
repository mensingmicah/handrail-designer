# Brief: checks

Part of the product brief; index in docs/BRIEF.md. The seven checks,
flexural and compression capacity, section classification and section
properties. Weld method is in welds.md.

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

Flexural capacity: top rail Lb = span, with Cb from the §F1 moment diagram
for each load case. Post Lb = h using the §F1 cantilever provision. Post
compression uses the recommended design K. In the upward case the post is
checked for axial tension (yielding on the gross section); it is computed
and shown in the envelope summary even though it will not control.

Plus reporting, not pass/fail: factored (LRFD) base reactions for a concrete
substrate, labeled for direct input into anchor software (see
loads-and-envelope.md).

## Engineering decisions already made

- Biaxial bending (dead load about one axis, horizontal guard load about the
  other): round HSS and pipe use the square root of the sum of the squares
  of the two moments against a single capacity, which is exact for a round
  section. All other sections use the AISC 360-22 provisions for combined
  strong- and weak-axis bending.
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
