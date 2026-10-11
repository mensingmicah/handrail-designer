
#let draft = true
#let footer-code = "Tool 0.1.0 (abc1234)"
#let footer-reg = "Registry def5678"

#set document(title: "char: guard calculation")
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10pt)
#set par(justify: false)
#set page(
  paper: "us-letter",
  margin: (top: 1.1in, bottom: 1.0in, x: 0.75in),
  // Reserved header area: kept empty in v1.
  header: block(width: 100%, height: 0.45in, stroke: (bottom: 0.4pt + luma(180)))[],
  header-ascent: 0.15in,
  footer: context [
    #set text(size: 8pt)
    #if draft [
      #align(center, text(fill: rgb("#b00000"), weight: "bold")[DRAFT: contains unverified code values (see Draft code values list)])
      #v(-4pt)
    ]
    #line(length: 100%, stroke: 0.4pt + luma(180))
    #v(-4pt)
    #grid(columns: (1fr, 1fr, auto), footer-code, align(center, footer-reg),
      [Page #counter(page).display() of #counter(page).final().first()])
  ],
  background: rotate(-40deg, text(size: 44pt, fill: rgb(200, 0, 0, 28), weight: "bold")[
    #align(center)[DEVELOPMENT \ NOT FOR CONSTRUCTION]
  ]),
)
#set heading(numbering: none)
#show heading.where(level: 1): it => { pagebreak(weak: true); text(size: 14pt, it) ; v(4pt) }
#show heading.where(level: 2): it => { v(6pt); text(size: 11.5pt, it); v(2pt) }
#set table(stroke: 0.4pt + luma(160), inset: 4pt)

#let calcline(eq, note, cite) = block(above: 8pt, below: 8pt, grid(
  columns: (1fr, 2.3in), column-gutter: 10pt,
  eq,
  text(size: 8pt)[#note #if cite != "" [\ #text(fill: luma(90), style: "italic", cite)]],
))
#let subhead(t) = block(above: 14pt, below: 8pt, text(weight: "bold", t))
#let flag(t) = block(width: 100%, inset: 6pt, fill: rgb("#fff2cc"), stroke: 0.6pt + rgb("#c09000"), text(weight: "bold", t))


#align(center, text(size: 16pt, weight: "bold")[Guard Calculation])

#align(center)[Top rail bending and deflection; top rail weld to post; intermediate rail and its weld to the post; post combined axial and flexure, and deflection; post weld to baseplate; anchor reactions]

== Project

#table(columns: (auto, 1fr), stroke: none, "Project", "char", "Phase", "", "Description", "")

Loading is per ASCE 7-22.

#text(weight: "bold", "Design method: ASD per AISC 360-22 §B3.2")

== Assumptions

+ #"No shear checks in any member."
+ #"Interior post; the tributary length is the span. End posts and rail overhangs are not checked."
+ #"Post loads use tributary length = span; rail continuity effects on post reactions are neglected (engineering judgement)."
+ #"The top rail runs continuously over the post; the post is coped and welded to its underside. The rail is designed as a simple span."
+ #"The rail to post weld is modeled as a flat ring of the post's perimeter at the underside of the rail, with eccentricity e = half the rail depth from the rail centerline; this is conservative against the saddle centroid (2R/π for equal round diameters). It is modeled as a fillet of the entered size all around, although at equal diameters the sides of the saddle form a flare-bevel joint."
+ #"The intermediate rail to post weld is modeled as a flat ring of the intermediate rail's perimeter at the post face, a simple shear connection consistent with the simple-span intermediate rail: the end reaction acts at the weld with no end moment. It is modeled as a fillet of the entered size all around, although at equal diameters the sides of the saddle form a flare-bevel joint."
+ #"Local strength of the rail wall at the post, and of the post wall at the intermediate rail (AISC 360-22 Chapter K chord limit states), is not checked; the chord's D/t is limited to 50, the Chapter K limit of applicability."
+ #"The component load's effect on the post is not checked."
+ #"Guard loads are not combined with floor or roof live load; wind, snow and ice are not considered."
+ #"Base reactions can reverse; direction is set in the anchor software."
+ #"The baseplate is rigid; the post is fixed at the top of the baseplate."
+ #"Baseplate thickness and bending are not checked; baseplate and anchorage design by others (e.g., PROFIS)."
+ #"Notional loads (AISC 360-22 App. 7) are neglected. In gravity-only combinations they produce a negligible moment, and the reported axial-only ratio bounds the H1-1b result."

== References

- #"AISC 360-22, Specification for Structural Steel Buildings"
- #"ASCE/SEI 7-22, Minimum Design Loads and Associated Criteria for Buildings and Other Structures"
- #"AISC Steel Construction Manual, 16th Edition"
- #"AISC Shapes Database v16.0"

== Sketch

#block(width: 100%, height: 2.2in, stroke: (dash: "dashed", paint: luma(150)), align(center + horizon, text(fill: luma(120))[Image area (image upload is a later slice)]))

== Draft code values

This calc uses the following registry entries, which the engineer of record has not yet verified against the standard:

#table(columns: (auto, 1fr, auto), table.header(strong("Entry"), strong("Citation"), strong("Source")), "ej.section.custom_wall_nominal", "Engineering judgement (EOR): a custom tube's wall is entered as the nominal wall", "engineer", "aisc360.B4.2.coeff", "AISC 360-22 §B4.2", "AISC 360-22 text, read 2026-10-10", "aisc360.B4.2.design_wall", "AISC 360-22 §B4.2", "AISC 360-22 text, read 2026-10-10", "geometry.round_tube.inside_diameter", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.round_tube.A", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "material.steel.density", "AISC Manual 16th Ed., Part 17", "memory", "geometry.round_tube.weight", "Engineering judgement (EOR): custom tube weight on the nominal wall", "engineer", "geometry.round_tube.I", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.round_tube.S", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.round_tube.Z", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.round_tube.r", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.round_tube.D_over_t", "AISC 360-22 Tables B4.1a and B4.1b", "memory", "aisc360.K.round_chord.D_over_t_max", "AISC 360-22 Tables K3.1A and K4.1A", "AISC 360-22 text, read 2026-10-10", "material.A53_GrB.Fu", "AISC Manual Table 2-4", "memory", "ej.weld.post_wall.fu_fy_min", "Engineering judgement (EOR): post wall at the weld covered by Check 5 while Fu/Fy >= 1.20", "engineer", "ej.post.axial_dead_load", "Engineering judgement (EOR): post dead load", "engineer", "material.A500_GrC.hss_round.Fy", "AISC Manual Table 2-4", "memory", "ej.weld.line_method", "Engineering judgement (EOR): elastic weld as a line", "engineer", "aisc360.J2.2a.throat.coeff", "AISC 360-22 §J2.2a", "memory", "aisc360.J2.2a.throat", "AISC 360-22 §J2.2a", "memory", "ej.weld.ring_model", "Engineering judgement (EOR): weld ring at the rail underside, e = D_rail/2", "engineer", "aisc360.J2.4.min_size", "AISC 360-22 Table J2.4", "memory", "ej.weld.max_size_not_applicable", "Engineering judgement (EOR): no maximum fillet size at a T-joint", "engineer", "aisc360.J2.2b.max_size_edges", "AISC 360-22 §J2.2b(b)", "memory", "material.E70XX.FEXX", "AISC 360-22 §J2.6; AWS A5.1", "memory", "aisc360.J2.5.fnw.coeff", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.fnw", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.omega_w", "AISC 360-22 Table J2.5", "memory", "ej.weld.branch_kds", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld", "engineer", "material.A500_GrC.hss_round.Fu", "AISC Manual Table 2-4", "memory", "aisc360.eq.J4-4.coeff", "AISC 360-22 Eq. J4-4", "memory", "aisc360.eq.J4-4", "AISC 360-22 Eq. J4-4", "memory", "aisc_manual.part9.base_metal", "AISC Manual Part 9, base metal at welds", "memory", "aisc360.J4.2.omega_rupture", "AISC 360-22 §J4.2(b)", "memory", "ej.weld.rail_wall_normal", "Engineering judgement (EOR): rail wall chord limit states not checked", "engineer", "ej.weld.post_wall_covered", "Engineering judgement (EOR): post wall at the weld covered by Check 5", "engineer", "aws.d1_1.thickness_min", "AWS D1.1/D1.1M:2020, Clause 1", "memory", "ej.weld.thin_material", "Engineering judgement (EOR): thin material at a weld is warned of, not stopped", "engineer", "aws.d1_1.scope", "AWS D1.1/D1.1M:2020, Clause 1", "memory", "ej.weld.no_bearing", "Engineering judgement (EOR): no bearing credit at the weld", "engineer", "aisc360.J2.4.fillet_strength", "AISC 360-22 Eq. J2-4", "memory", "aisc360.B4.1a.round_hss.lambda_r", "AISC 360-22 Table B4.1a, Case 9", "memory", "aisc360.B4.1a.classification", "AISC 360-22 §B4.1a", "memory", "aisc360.CA7.K_fixed_free", "AISC 360-22 Comm. Table C-A-7.1, case (e)", "memory", "aisc360.E2.effective_length", "AISC 360-22 §E2", "memory", "ej.post.unbraced_length", "Engineering judgement (EOR): unbraced length is the post height", "engineer", "aisc360.eq.E3-4", "AISC 360-22 Eq. E3-4", "memory", "aisc360.E2.user_note.slenderness", "AISC 360-22 §E2, User Note", "memory", "aisc360.E2.user_note.slenderness.limit", "AISC 360-22 §E2, User Note", "memory", "aisc360.E3.branch_limit", "AISC 360-22 §E3(a), (b)", "memory", "aisc360.eq.E3-3", "AISC 360-22 Eq. E3-3", "memory", "aisc360.eq.E3-3.coeff", "AISC 360-22 Eq. E3-3", "memory", "aisc360.eq.E3-1", "AISC 360-22 Eq. E3-1", "memory", "aisc360.E1.omega_c", "AISC 360-22 §E1", "memory", "aisc_manual.t3-23.case22.M", "AISC Manual Table 3-23, Case 22", "memory", "aisc360.eq.A-8-5", "AISC 360-22 Eq. A-8-5", "memory", "ej.second_order.pe_length", "Engineering judgement (EOR): Pe at Lc = 2.1h", "engineer", "aisc360.app8.alpha_asd", "AISC 360-22 App. 8", "memory", "ej.second_order.limit", "Engineering judgement (EOR): second-order limit", "engineer", "ej.second_order.negligible", "Engineering judgement (EOR): second-order limit", "engineer", "aisc360.H1.1.threshold", "AISC 360-22 §H1.1", "memory", "aisc360.eq.H1-1b", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.H1-1b.coeff", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.D2-1", "AISC 360-22 Eq. D2-1", "memory", "aisc360.D2.omega_t", "AISC 360-22 §D2(a)", "memory", "aisc_manual.t3-23.case22.delta", "AISC Manual Table 3-23, Case 22", "memory", "ej.deflection.limit.post", "Engineering judgement (EOR): post deflection limit, not code", "engineer", "aisc360.J2.4.kds_other", "AISC 360-22 §J2.4(a)(3)", "AISC 360-22 text, read 2026-10-10", "material.A36.Fu", "AISC Manual Table 2-5", "memory", "ej.reaction.location", "Engineering judgement (EOR): reactions at the top of concrete, arm h", "engineer", "ej.combo.reaction", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "engineer", "ej.reaction.lateral_note", "Engineering judgement (EOR): one lateral set, any horizontal direction", "engineer")

= Dimensions

Every dimension as entered, and as the tool read it. A bare number is inches.

#table(columns: (1fr, auto, auto, auto), table.header(strong("Dimension"), strong("As entered"), strong("Read as"), strong("Inches")), "Span, post to post (c/c)", "5'-0\"", "5'-0\"", "60.00 in", "Post height h, top of concrete to top rail centerline", "42", "3'-6\"", "42.00 in", "Baseplate thickness t_p", "1/2", "1/2\"", "0.5000 in", "Baseplate B, parallel to the rail", "6", "6\"", "6.000 in", "Baseplate N, perpendicular to the rail", "8", "8\"", "8.000 in", "Fillet weld, top rail to post", "1/8", "1/8\"", "0.1250 in", "Fillet weld, post to baseplate", "1/4", "1/4\"", "0.2500 in", "Top rail, custom round tube: outside diameter", "1.9", "1.9\"", "1.900 in", "Top rail, custom round tube: nominal wall", "0.045", "0.045\"", "0.04500 in")

#text("Directional strength increase at the post to baseplate weld: not elected (directional_increase = false).")

Derived lengths, each computed in the calc where it is used:

#table(columns: (1fr, auto, auto, auto), table.header(strong("Derived length"), strong("Formula"), strong("Inches"), strong("Computed in")), "Post cantilever length, top of baseplate to top rail centerline", [$L_"post" = h - t_p$], "41.50 in", "Loading", "Eccentricity: rail centerline to the weld plane at the rail underside", [$e = frac(d_"rail", "2")$], "0.9500 in", "Check 3", "Effective length, with the unbraced length taken as the post height h", [$L_c = K h$], "88.20 in", "Check 5")

= Section properties

#text("Top rail: Round tube 1.9 × 0.045 (custom), A500 Gr C.") Properties are computed below from the dimensions entered, on the design wall thickness of AISC 360-22 §B4.2; the weight is on the nominal wall.

#calcline([$D = "1.900 in"$], "Round tube 1.9 × 0.045 (custom): outside diameter (1.9 as entered)", "Input")
#calcline([$t_"nom" = "0.04500 in"$], "Nominal wall thickness (0.045 as entered)", "Input; Engineering judgement (EOR): a custom tube's wall is entered as the nominal wall")
#calcline([$display(t_"des" = "0.93" t_"nom" = "0.93" ("0.04500 in") = "0.04185 in")$], "Design wall thickness", "AISC 360-22 §B4.2")
#calcline([$display(D_i = D - "2" t_"des" = ("1.900 in") - "2" ("0.04185 in") = "1.816 in")$], "Inside diameter, on the design wall", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A = frac(pi, "4") (D^("2") - D_i^("2")) = frac(pi, "4") (("1.900 in")^("2") - ("1.816 in")^("2")) = "0.2443 in"^2)$], "Area (design wall)", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(D_"i,nom" = D - "2" t_"nom" = ("1.900 in") - "2" ("0.04500 in") = "1.810 in")$], "Inside diameter, on the nominal wall (for the weight)", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A_"nom" = frac(pi, "4") (D^("2") - D_"i,nom"^("2")) = frac(pi, "4") (("1.900 in")^("2") - ("1.810 in")^("2")) = "0.2622 in"^2)$], "Area on the nominal wall (for the weight)", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$rho = "0.2836 lb/in"^3$], "Steel unit weight", "AISC Manual 16th Ed., Part 17")
#calcline([$display(W = rho A_"nom" = ("0.2836 lb/in"^3) ("0.2622 in"^2) = "0.07436 lb/in")$], "Weight per unit length: steel unit weight times the area on the nominal wall", "Engineering judgement (EOR): custom tube weight on the nominal wall")
#calcline([$display(I = frac(pi, "64") (D^("4") - D_i^("4")) = frac(pi, "64") (("1.900 in")^("4") - ("1.816 in")^("4")) = "0.1055 in"^4)$], "Moment of inertia", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(S = frac(I, frac(D, "2")) = frac(("0.1055 in"^4), frac(("1.900 in"), "2")) = "0.1110 in"^3)$], "Elastic section modulus", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z = frac(D^("3") - D_i^("3"), "6") = frac(("1.900 in")^("3") - ("1.816 in")^("3"), "6") = "0.1445 in"^3)$], "Plastic section modulus", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(D slash t = frac(D, t_"des") = frac(("1.900 in"), ("0.04185 in")) = "45.40")$], "Diameter-to-thickness ratio, computed (design wall)", "AISC 360-22 Tables B4.1a and B4.1b")

#text("Post: Pipe1-1/2STD, A53 Gr B (default).") Properties are used exactly as published in the AISC Shapes Database v16.0.

#calcline([$D = "1.900 in"$], "Pipe1-1/2STD: outside diameter", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.1450 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1350 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "0.7490 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "0.2267 lb/in"$], "Nominal weight: tabulated 2.72 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I = "0.2930 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$S = "0.3090 in"^3$], "Elastic section modulus", "AISC Shapes Database v16.0")
#calcline([$Z = "0.4210 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$r = "0.6260 in"$], "Radius of gyration", "AISC Shapes Database v16.0")
#calcline([$D slash t = "14.10"$], "Diameter-to-thickness ratio, tabulated", "AISC Shapes Database v16.0")

#text("Intermediate rail: none.")

#text("Baseplate: A36. Welds: fillet, all around, electrode E70XX.")

= Loading

Guard loads per ASCE 7-22. The concentrated and uniform loads are separate load types and do not act concurrently. Each check applies them in every direction case and reports the controlling one.

#calcline([$P = "200.0 lb"$], "Concentrated guard load, any direction, any point on the top rail", "ASCE 7-22 §4.5.1")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load, 50 lb/ft, any direction; not concurrent with P", "ASCE 7-22 §4.5.1.1")
#calcline([$w_D = "0.07436 lb/in"$], "Top rail self-weight: computed W = 0.8924 lb/ft", "Section properties (custom section)")
#subhead("Dead load at the post")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(L_"post" = h - t_p = ("42.00 in") - ("0.5000 in") = "41.50 in")$], "Post cantilever length, top of baseplate to top rail centerline", "Stated assumption: post fixed at the top of the baseplate")
#calcline([$W_"post" = "0.2267 lb/in"$], "Post self-weight: Pipe1-1/2STD, tabulated W = 2.72 lb/ft", "AISC Shapes Database v16.0")
#calcline([$display(D_"post" = W_"post" L_"post" = ("0.2267 lb/in") ("41.50 in") = "9.407 lb")$], "Post dead load, full weight at the base", "Engineering judgement (EOR): post dead load")
#calcline([$L = "60.00 in"$], "Span: the tributary length for the post (stated assumption)", "Input")
#calcline([$display(D_"rail" = w_D L = ("0.07436 lb/in") ("60.00 in") = "4.462 lb")$], "Top rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$display(P_D = D_"rail" + D_"post" = ("4.462 lb") + ("9.407 lb") = "13.87 lb")$], "D at the post: axial dead load at the top of the baseplate", "Engineering judgement (EOR): post dead load")

= Check 1: Top rail bending

#flag("NONCOMPACT: Round tube 1.9 × 0.045 (custom) D/t = 45.40 exceeds lambda_p = 40.60 (lambda_r = 179.8); Mn reduced by local buckling, AISC 360-22 Eq. F8-2.")

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $M_a$], [*Capacity* $M_n / Omega_b$], [*Ratio*], []), strong("Downward"), strong("Concentrated"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2"), strong("3,033 lb-in"), strong("4,217 lb-in"), strong("0.72"), strong("Controls"), "Downward", "Distributed", "1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2", "1,908 lb-in", "4,217 lb-in", "0.45", "", "Outward", "Concentrated", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "3,000 lb-in", "4,217 lb-in", "0.71", "", "Outward", "Distributed", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "1,875 lb-in", "4,217 lb-in", "0.44", "", "Inward", "Concentrated", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "3,000 lb-in", "4,217 lb-in", "0.71", "", "Inward", "Distributed", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "1,875 lb-in", "4,217 lb-in", "0.44", "", "Upward", "Concentrated", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "2,980 lb-in", "4,217 lb-in", "0.71", "", "Upward", "Distributed", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "1,855 lb-in", "4,217 lb-in", "0.44", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Downward, concentrated (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Capacity")
#calcline([$F_y = "50.00 ksi"$], "Yield stress, A500 Gr C", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$lambda = "45.40"$], "lambda = D/t, computed (design wall)", "Section properties (custom section)")
#calcline([$display(lambda_"lim" = frac("0.45" E, F_y) = frac("0.45" ("29,000 ksi"), ("50.00 ksi")) = "261.0")$], "Applicability limit on D/t", "AISC 360-22 §F8")
#calcline([$display(lambda_p = frac("0.07" E, F_y) = frac("0.07" ("29,000 ksi"), ("50.00 ksi")) = "40.60")$], "Compact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$display(lambda_r = frac("0.31" E, F_y) = frac("0.31" ("29,000 ksi"), ("50.00 ksi")) = "179.8")$], "Noncompact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$lambda = 45.40 < lambda_"lim" = 261.0$ #h(6pt) $arrow.r$ #h(6pt) *#"Applies"*], "Applicability", "AISC 360-22 §F8")
#calcline([$"Round HSS"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "Limit states: yielding and local buckling only; Lb and Cb do not enter", "AISC 360-22 §F8")
#calcline([$Z = "0.1445 in"^3$], "Plastic section modulus", "Section properties (custom section)")
#calcline([$display(M_p = F_y Z = ("50.00 ksi") ("0.1445 in"^3) = "7,226 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F8-1")
#calcline([$lambda_p = 40.60 < lambda = 45.40 <= lambda_r = 179.8$ #h(6pt) $arrow.r$ #h(6pt) *#"NONCOMPACT"*], "Section classification: reduced capacity", "AISC 360-22 §B4.1b")
#calcline([$S = "0.1110 in"^3$], "Elastic section modulus", "Section properties (custom section)")
#calcline([$display(M_(n,"LB") = (frac("0.021" E, lambda) + F_y) S = (frac("0.021" ("29,000 ksi"), "45.40") + ("50.00 ksi")) ("0.1110 in"^3) = "7,042 lb-in")$], "Local buckling, noncompact wall", "AISC 360-22 Eq. F8-2")
#calcline([$display(M_n = "min"(M_p, M_(n,"LB")) = "min"(("7,226 lb-in"), ("7,042 lb-in")) = "7,042 lb-in")$], "Lower of yielding and local buckling", "AISC 360-22 §F8")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$display(frac(M_n, Omega_b) = frac(("7,042 lb-in"), "1.670") = "4,217 lb-in")$], "Allowable flexural strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: downward, concentrated load")
#calcline([$L = "60.00 in"$], "Span, simple beam", "Input")
#calcline([$w_D = "0.07436 lb/in"$], "Top rail self-weight", "Loading")
#calcline([$display(M_D = frac(w_D L^("2"), "8") = frac(("0.07436 lb/in") ("60.00 in")^("2"), "8") = "33.46 lb-in")$], "Dead-load moment, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$P = "200.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(M_L = frac(P L, "4") = frac(("200.0 lb") ("60.00 in"), "4") = "3,000 lb-in")$], "Live-load moment, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$display(M_a = "1.0" M_D + "1.0" M_L = "1.0" ("33.46 lb-in") + "1.0" ("3,000 lb-in") = "3,033 lb-in")$], "Required flexural strength: D and L on the same axis", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display("Ratio" = frac(M_a, frac(M_n, Omega_b)) = frac(("3,033 lb-in"), ("4,217 lb-in")) = "0.72")$], "Demand / capacity", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.72 <= 1.00$ #h(10pt) #"OK"])

= Check 2: Top rail deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), strong("Downward"), strong("Concentrated"), strong("1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability"), strong("0.2983 in"), strong("0.5000 in"), strong("0.60"), strong("Controls"), "Downward", "Distributed", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.2339 in", "0.5000 in", "0.47", "", "Outward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.2942 in", "0.5000 in", "0.59", "", "Outward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.2298 in", "0.5000 in", "0.46", "", "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.2942 in", "0.5000 in", "0.59", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.2298 in", "0.5000 in", "0.46", "", "Upward", "Concentrated", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.2942 in", "0.5000 in", "0.59", "", "Upward", "Distributed", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.2298 in", "0.5000 in", "0.46", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Downward, concentrated (1.0D + 1.0L, vertical; Engineering judgement (EOR): serviceability)")

#calcline([$L = "60.00 in"$], "Span, simple beam", "Input")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I = "0.1055 in"^4$], "Moment of inertia", "Section properties (custom section)")
#calcline([$P = "200.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(Delta_L = frac(P L^("3"), "48" E I) = frac(("200.0 lb") ("60.00 in")^("3"), "48" ("29,000 ksi") ("0.1055 in"^4)) = "0.2942 in")$], "Live-load deflection, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$w_D = "0.07436 lb/in"$], "Top rail self-weight", "Loading")
#calcline([$display(Delta_D = frac("5" w_D L^("4"), "384" E I) = frac("5" ("0.07436 lb/in") ("60.00 in")^("4"), "384" ("29,000 ksi") ("0.1055 in"^4)) = "0.004102 in")$], "Dead-load deflection, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$display(Delta = "1.0" Delta_D + "1.0" Delta_L = "1.0" ("0.004102 in") + "1.0" ("0.2942 in") = "0.2983 in")$], "D and L on the same (vertical) axis", "Engineering judgement (EOR): serviceability")
#calcline([$display(Delta_"allow" = frac(L, "120") = frac(("60.00 in"), "120") = "0.5000 in")$], "Limit L/120", "Engineering judgement (EOR): deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.2983 in"), ("0.5000 in")) = "0.60")$], "Deflection / limit", "Engineering judgement (EOR): deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.60 <= 1.00$ #h(10pt) #"OK"])

= Check 3: Top rail weld to post

#flag("THIN MATERIAL AT WELD: Top rail nominal wall thickness, Round tube 1.9 × 0.045 (custom), 0.04500 in, is thinner than 0.1250 in: the joined material is below the AWS D1.1 thickness range, and the welding procedure is the engineer's responsibility (for example AWS D1.3, sheet steel). AWS D1.1, Structural Welding Code - Steel, applies to carbon and low-alloy steel 1/8 in (3 mm) or thicker (AWS D1.1/D1.1M:2020, Clause 1).")

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "34.25 lb/in\nuniform", "—", "34.25 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "42.63 lb/in\nuniform", "—", "42.63 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "67.76 lb/in\ncompression side", "33.51 lb/in", "75.59 lb/in", "Weld 1,856 lb/in\nBase 778.4 lb/in", "0.04", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("84.51 lb/in\ncompression side"), strong("41.88 lb/in"), strong("94.32 lb/in"), strong("Weld 1,856 lb/in\nBase 778.4 lb/in"), strong("0.05"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "67.76 lb/in\ncompression side", "33.51 lb/in", "75.59 lb/in", "Weld 1,856 lb/in\nBase 778.4 lb/in", "0.04", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "84.51 lb/in\ncompression side", "41.88 lb/in", "94.32 lb/in", "Weld 1,856 lb/in\nBase 778.4 lb/in", "0.05", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "33.06 lb/in\nuniform", "—", "33.06 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "41.43 lb/in\nuniform", "—", "41.43 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "67.76 lb/in\ncompression side", "33.51 lb/in", "75.59 lb/in", "Weld 1,856 lb/in\nBase 778.4 lb/in", "0.04", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "84.51 lb/in\ncompression side", "41.88 lb/in", "94.32 lb/in", "Weld 1,856 lb/in\nBase 778.4 lb/in", "0.05", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$D = "1.900 in"$], "Pipe1-1/2STD: outside diameter; the weld ring is the post perimeter", "AISC Shapes Database v16.0")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(L_w = pi D = pi ("1.900 in") = "5.969 in")$], "Weld length: the post perimeter", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(S_w = frac(pi D^("2"), "4") = frac(pi ("1.900 in")^("2"), "4") = "2.835 in"^2)$], "Section modulus of the ring as a line", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Eccentricity")
#calcline([$d_"rail" = "1.900 in"$], "Round tube 1.9 × 0.045 (custom): outside diameter, the rail depth", "Section properties (custom section)")
#calcline([$display(e = frac(d_"rail", "2") = frac(("1.900 in"), "2") = "0.9500 in")$], "Eccentricity: rail centerline to the weld plane at the rail underside", "Engineering judgement (EOR): weld ring at the rail underside, e = D_rail/2")
#subhead("Fillet size limits")
#calcline([$t_"rail,nom" = "0.04500 in"$], "Top rail nominal wall thickness, Round tube 1.9 × 0.045 (custom)", "Section properties (custom section)")
#calcline([$t_"post,nom" = "0.1450 in"$], "Post nominal wall thickness, Pipe1-1/2STD", "AISC Shapes Database v16.0")
#calcline([$display(t_"min" = "min"(t_"rail,nom", t_"post,nom") = "min"(("0.04500 in"), ("0.1450 in")) = "0.04500 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w_"min" = "0.1250 in"$], "Minimum fillet size for the thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w = "0.1250 in" >= w_"min" = "0.1250 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"OK"*], "Minimum size", "AISC 360-22 Table J2.4")
#calcline([$"Maximum fillet size"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not applicable"*], "Maximum fillet size along edges of material does not apply: this weld is a T-joint, not a weld along an edge. No maximum size is checked.", "AISC 360-22 §J2.2b(b); Engineering judgement (EOR): no maximum fillet size at a T-joint")
#subhead("Weld metal")
#calcline([$F_"EXX" = "70.00 ksi"$], "Electrode classification strength, E70XX", "AISC 360-22 §J2.6; AWS A5.1")
#calcline([$display(F_"nw" = "0.6" F_"EXX" = "0.6" ("70.00 ksi") = "42.00 ksi")$], "Nominal stress of the weld metal", "AISC 360-22 Table J2.5")
#calcline([$Omega_w = "2.000"$], "Safety factor, fillet weld (ASD)", "AISC 360-22 Table J2.5")
#calcline([$k_"ds" = "1.000"$], "No directional increase at the rail to post weld (a branch-to-chord joint)", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld")
#subhead("Base metal: rail fusion face")
#calcline([$F_u = "62.00 ksi"$], "Tensile strength, A500 Gr C", "AISC Manual Table 2-4")
#calcline([$t_"rail" = "0.04185 in"$], "Top rail design wall thickness, Round tube 1.9 × 0.045 (custom)", "Section properties (custom section)")
#calcline([$display(R_(n,"BM") = "0.6" F_u t_"rail" = "0.6" ("62.00 ksi") ("0.04185 in") = "1,557 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM"), Omega_"BM") = frac(("1,557 lb/in"), "2.000") = "778.4 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$"Rail wall, normal force"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not checked"*], "Rail wall, force normal to the wall: a chord-wall limit state of the round T-connection (AISC 360-22 Chapter K), not weld base metal; not checked (stated assumption).", "Engineering judgement (EOR): rail wall chord limit states not checked")
#calcline([$"Post wall at the weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Covered by Check 5"*], "Post wall at the weld: covered by Check 5. The wall carries the weld force as stress along the post axis, the same demand as Check 5 at its critical section; member shear is not checked (stated assumption).", "Engineering judgement (EOR): post wall at the weld covered by Check 5")
#subhead("Demand: outward, distributed load")
#calcline([$D_"rail" = "4.462 lb"$], "Top rail dead load at the weld: w_D over the span (the tributary length)", "Loading")
#calcline([$display(P = "1.0" D_"rail" = "1.0" ("4.462 lb") = "4.462 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "60.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("60.00 in") = "250.0 lb")$], "Uniform guard load collected over the span, horizontal (outward), on the rail at the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("250.0 lb") = "250.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V e = ("250.0 lb") ("0.9500 in") = "237.5 lb-in")$], "Moment at the weld plane: V at the rail centerline, arm e", "Engineering judgement (EOR): weld ring at the rail underside, e = D_rail/2")
#calcline([$display(f_a = frac(P, L_w) = frac(("4.462 lb"), ("5.969 in")) = "0.7475 lb/in")$], "Axial force per inch of weld, compression, uniform around the ring", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_w) = frac(("237.5 lb-in"), ("2.835 in"^2)) = "83.77 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("0.7475 lb/in") + ("83.77 lb/in") = "84.51 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("0.7475 lb/in") - ("83.77 lb/in")) = "83.02 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "84.51 lb/in" >= f_(n,"t") = "83.02 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "84.51 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, L_w) = frac(("250.0 lb"), ("5.969 in")) = "41.88 lb/in")$], "Shear per inch of weld, taken as uniform around the ring", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("84.51 lb/in")^("2") + ("41.88 lb/in")^("2")) = "94.32 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("94.32 lb/in"), ("1,856 lb/in")) = "0.05")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM"), Omega_"BM")) = frac(("41.88 lb/in"), ("778.4 lb/in")) = "0.05")$], "Rail fusion face: in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.05082", "0.05381") = "0.05")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.05 <= 1.00$ #h(10pt) #"OK"])

= Check 4a: Intermediate rail

#"None: no intermediate rail."

= Check 4b: Intermediate rail weld to post

#"None: no intermediate rail."

= Check 5: Post combined axial and flexure

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Axial* $P_r$ \ capacity $P_c$ or $P_t$], [*Moment* $M_r$ \ capacity $M_c$], [*Equation*], [$frac(alpha P_r, P_e)$], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "213.9 lb comp.\nPc = 5,671 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.04", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "263.9 lb comp.\nPc = 5,671 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.05", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "13.87 lb comp.\nPc = 5,671 lb", "8,300 lb-in\nMc = 8,823 lb-in", "Eq. H1-1b", "0.002058", "0.94", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("13.87 lb comp.\nPc = 5,671 lb"), strong("10,380 lb-in\nMc = 8,823 lb-in"), strong("Eq. H1-1b"), strong("0.002058"), strong("1.18"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "13.87 lb comp.\nPc = 5,671 lb", "8,300 lb-in\nMc = 8,823 lb-in", "Eq. H1-1b", "0.002058", "0.94", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "13.87 lb comp.\nPc = 5,671 lb", "10,380 lb-in\nMc = 8,823 lb-in", "Eq. H1-1b", "0.002058", "1.18", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "191.7 lb tension\nPt = 15,700 lb", "—", "Pr/Pt\n(Eq. D2-1)", "—", "0.01", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "241.7 lb tension\nPt = 15,700 lb", "—", "Pr/Pt\n(Eq. D2-1)", "—", "0.02", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "13.87 lb comp.\nPc = 5,671 lb", "8,300 lb-in\nMc = 8,823 lb-in", "Eq. H1-1b", "0.002058", "0.94", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "13.87 lb comp.\nPc = 5,671 lb", "10,380 lb-in\nMc = 8,823 lb-in", "Eq. H1-1b", "0.002058", "1.18", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Capacity")
#calcline([$"Pipe1-1/2STD, A53 Gr B"$ #h(6pt) $arrow.r$ #h(6pt) *#"Designed as round HSS"*], "Pipe is designed under the round HSS provisions", "AISC Manual Table 2-4")
#calcline([$F_y = "35.00 ksi"$], "Yield stress, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$lambda = "14.10"$], "lambda = D/t, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$display(lambda_"lim" = frac("0.45" E, F_y) = frac("0.45" ("29,000 ksi"), ("35.00 ksi")) = "372.9")$], "Applicability limit on D/t", "AISC 360-22 §F8")
#calcline([$display(lambda_p = frac("0.07" E, F_y) = frac("0.07" ("29,000 ksi"), ("35.00 ksi")) = "58.00")$], "Compact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$display(lambda_r = frac("0.31" E, F_y) = frac("0.31" ("29,000 ksi"), ("35.00 ksi")) = "256.9")$], "Noncompact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$lambda = 14.1 < lambda_"lim" = 372.9$ #h(6pt) $arrow.r$ #h(6pt) *#"Applies"*], "Applicability", "AISC 360-22 §F8")
#calcline([$"Round HSS"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "Limit states: yielding and local buckling only; Lb and Cb do not enter", "AISC 360-22 §F8")
#calcline([$Z = "0.4210 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$display(M_p = F_y Z = ("35.00 ksi") ("0.4210 in"^3) = "14,740 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F8-1")
#calcline([$lambda = 14.1 <= lambda_p = 58.00$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact"*], "Section classification", "AISC 360-22 §B4.1b")
#calcline([$"Compact wall"$ #h(6pt) $arrow.r$ #h(6pt) *#"Local buckling does not apply"*], "", "AISC 360-22 §F8")
#calcline([$display(M_n = M_p = "14,740 lb-in")$], "Nominal flexural strength", "AISC 360-22 §F8")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$display(frac(M_n, Omega_b) = frac(("14,740 lb-in"), "1.670") = "8,823 lb-in")$], "Allowable flexural strength", "AISC 360-22 Eq. B3-2")
#calcline([$display(M_c = frac(M_n, Omega_b) = "8,823 lb-in")$], "Allowable flexural strength, as used in Chapter H", "AISC 360-22 Eq. B3-2")
#calcline([$display(lambda_(r,c) = frac("0.11" E, F_y) = frac("0.11" ("29,000 ksi"), ("35.00 ksi")) = "91.14")$], "Slender limit, round HSS in compression", "AISC 360-22 Table B4.1a, Case 9")
#calcline([$lambda = 14.1 <= lambda_(r,c) = 91.14$ #h(6pt) $arrow.r$ #h(6pt) *#"Nonslender"*], "Section classification, compression: no noncompact category", "AISC 360-22 §B4.1a")
#calcline([$K = "2.100"$], "Effective length factor, fixed-free (recommended design value)", "AISC 360-22 Comm. Table C-A-7.1, case (e)")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$display(L_c = K h = "2.100" ("42.00 in") = "88.20 in")$], "Effective length, with the unbraced length taken as the post height h", "AISC 360-22 §E2; Engineering judgement (EOR): unbraced length is the post height")
#calcline([$r = "0.6260 in"$], "Radius of gyration", "AISC Shapes Database v16.0")
#calcline([$display(frac(L_c, r) = frac(("88.20 in"), ("0.6260 in")) = "140.9")$], "Effective slenderness ratio", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 140.9 <= 200$ #h(6pt) $arrow.r$ #h(6pt) *#"Within the recommended limit"*], "For members designed on the basis of compression, the effective slenderness ratio Lc/r preferably should not exceed 200.", "AISC 360-22 §E2, User Note")
#calcline([$display("4.71" sqrt(frac(E, F_y)) = "4.71" dot sqrt(frac(("29,000 ksi"), ("35.00 ksi"))) = "135.6")$], "Limit between inelastic and elastic buckling", "AISC 360-22 §E3(a), (b)")
#calcline([$display(F_e = frac(pi^("2") E, (frac(L_c, r))^("2")) = frac(pi^("2") ("29,000 ksi"), "140.9"^("2")) = "14.42 ksi")$], "Elastic buckling stress", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 140.9 > 135.6$ #h(6pt) $arrow.r$ #h(6pt) *#"Elastic buckling: Eq. E3-3"*], "", "AISC 360-22 §E3(a), (b)")
#calcline([$display(F_"cr" = "0.877" F_e = "0.877" ("14.42 ksi") = "12.64 ksi")$], "Critical stress", "AISC 360-22 Eq. E3-3")
#calcline([$A_g = "0.7490 in"^2$], "Gross area", "AISC Shapes Database v16.0")
#calcline([$display(P_n = F_"cr" A_g = ("12.64 ksi") ("0.7490 in"^2) = "9,471 lb")$], "Nominal compressive strength", "AISC 360-22 Eq. E3-1")
#calcline([$Omega_c = "1.670"$], "Safety factor for compression (ASD)", "AISC 360-22 §E1")
#calcline([$display(P_c = frac(P_n, Omega_c) = frac(("9,471 lb"), "1.670") = "5,671 lb")$], "Allowable compressive strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: outward, distributed load")
#calcline([$P_D = "13.87 lb"$], "D at the post: axial dead load", "Loading")
#calcline([$display(P_r = "1.0" P_D = "1.0" ("13.87 lb") = "13.87 lb")$], "Required axial strength: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "60.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("60.00 in") = "250.0 lb")$], "Uniform guard load collected over the span, horizontal (outward) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p (critical section at the top of the baseplate)", "Loading")
#calcline([$display(M_L = V_L L_"post" = ("250.0 lb") ("41.50 in") = "10,380 lb-in")$], "Live-load moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(M_r = "1.0" M_L = "1.0" ("10,380 lb-in") = "10,380 lb-in")$], "Required flexural strength", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$I = "0.2930 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$display(P_e = frac(pi^("2") E I, L_c^("2")) = frac(pi^("2") ("29,000 ksi") ("0.2930 in"^4), ("88.20 in")^("2")) = "10,780 lb")$], "Elastic critical buckling load, at the compression Lc", "AISC 360-22 Eq. A-8-5; Engineering judgement (EOR): Pe at Lc = 2.1h")
#calcline([$display(frac(alpha P_r, P_e) = frac("1.6" P_r, P_e) = frac("1.6" ("13.87 lb"), ("10,780 lb")) = "0.002058")$], "Second-order ratio", "AISC 360-22 App. 8")
#calcline([$frac(alpha P_r, P_e) <= 0.05$ #h(6pt) $arrow.r$ #h(6pt) *#"Second-order effects negligible: αPr/Pe = 0.002058; amplification taken as 1.0."*], "", "Engineering judgement (EOR): second-order limit")
#calcline([$display(frac(P_r, P_c) = frac(("13.87 lb"), ("5,671 lb")) = "0.002445")$], "Axial ratio, selects the interaction equation", "AISC 360-22 §H1.1")
#calcline([$frac(P_r, P_c) = 0.002445 < 0.2$ #h(6pt) $arrow.r$ #h(6pt) *#"Eq. H1-1b"*], "", "AISC 360-22 §H1.1")
#calcline([$display("Ratio" = frac(P_r, "2" P_c) + frac(M_r, M_c) = frac(("13.87 lb"), "2" ("5,671 lb")) + frac(("10,380 lb-in"), ("8,823 lb-in")) = "1.18")$], "Combined axial and flexure", "AISC 360-22 Eq. H1-1b")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 1.18 > 1.00$ #h(10pt) #"NG"])

= Check 6: Post deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), "Downward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Outward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.5608 in", "0.6917 in", "0.81", "", strong("Outward"), strong("Distributed"), strong("1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only"), strong("0.7010 in"), strong("0.6917 in"), strong("1.01"), strong("Controls"), "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.5608 in", "0.6917 in", "0.81", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.7010 in", "0.6917 in", "1.01", "", "Upward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Longitudinal", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.5608 in", "0.6917 in", "0.81", "", "Longitudinal", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.7010 in", "0.6917 in", "1.01", "")

#heading(level: 2, "Controlling case: Outward, distributed (1.0L, horizontal; Engineering judgement (EOR): serviceability, live load only)")

#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p", "Loading")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I = "0.2930 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "60.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("60.00 in") = "250.0 lb")$], "Uniform guard load collected over the span, horizontal (outward) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(Delta_L = frac(V_L L_"post"^("3"), "3" E I) = frac(("250.0 lb") ("41.50 in")^("3"), "3" ("29,000 ksi") ("0.2930 in"^4)) = "0.7010 in")$], "Live-load deflection at the top of the post", "AISC Manual Table 3-23, Case 22")
#calcline([$display(Delta = "1.0" Delta_L = "1.0" ("0.7010 in") = "0.7010 in")$], "Live load only; dead load acts axially", "Engineering judgement (EOR): serviceability, live load only")
#calcline([$display(Delta_"allow" = frac(L_"post", "60") = frac(("41.50 in"), "60") = "0.6917 in")$], "Limit (h - t_p)/60", "Engineering judgement (EOR): post deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.7010 in"), ("0.6917 in")) = "1.01")$], "Deflection / limit", "Engineering judgement (EOR): post deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 1.01 > 1.00$ #h(10pt) #"NG"])

= Check 7: Post weld to baseplate

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "35.83 lb/in\nuniform", "—", "35.83 lb/in", "Weld 3,712 lb/in\nBase 8,700 lb/in", "0.01", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "44.21 lb/in\nuniform", "—", "44.21 lb/in", "Weld 3,712 lb/in\nBase 8,700 lb/in", "0.01", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,930 lb/in\ncompression side", "33.51 lb/in", "2,930 lb/in", "Weld 3,712 lb/in\nBase 8,700 lb/in", "0.79", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("3,662 lb/in\ncompression side"), strong("41.88 lb/in"), strong("3,662 lb/in"), strong("Weld 3,712 lb/in\nBase 8,700 lb/in"), strong("0.99"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,930 lb/in\ncompression side", "33.51 lb/in", "2,930 lb/in", "Weld 3,712 lb/in\nBase 8,700 lb/in", "0.79", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "3,662 lb/in\ncompression side", "41.88 lb/in", "3,662 lb/in", "Weld 3,712 lb/in\nBase 8,700 lb/in", "0.99", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "32.11 lb/in\nuniform", "—", "32.11 lb/in", "Weld 3,712 lb/in\nBase 8,700 lb/in", "0.01", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "40.49 lb/in\nuniform", "—", "40.49 lb/in", "Weld 3,712 lb/in\nBase 8,700 lb/in", "0.01", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,930 lb/in\ncompression side", "33.51 lb/in", "2,930 lb/in", "Weld 3,712 lb/in\nBase 8,700 lb/in", "0.79", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "3,662 lb/in\ncompression side", "41.88 lb/in", "3,662 lb/in", "Weld 3,712 lb/in\nBase 8,700 lb/in", "0.99", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$D = "1.900 in"$], "Pipe1-1/2STD: outside diameter; the weld ring is the post perimeter", "AISC Shapes Database v16.0")
#calcline([$w = "0.2500 in"$], "Fillet weld leg size, all around (1/4 as entered)", "Input")
#calcline([$display(L_w = pi D = pi ("1.900 in") = "5.969 in")$], "Weld length: the post perimeter", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(S_w = frac(pi D^("2"), "4") = frac(pi ("1.900 in")^("2"), "4") = "2.835 in"^2)$], "Section modulus of the ring as a line", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.2500 in") = "0.1767 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Moment arm")
#calcline([$L_"post" = "41.50 in"$], "Moment arm, h - t_p: guard load at the top rail centerline, weld at the top of the baseplate", "Loading")
#subhead("Fillet size limits")
#calcline([$t_"post,nom" = "0.1450 in"$], "Post nominal wall thickness, Pipe1-1/2STD", "AISC Shapes Database v16.0")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(t_"min" = "min"(t_"post,nom", t_p) = "min"(("0.1450 in"), ("0.5000 in")) = "0.1450 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w_"min" = "0.1250 in"$], "Minimum fillet size for the thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w = "0.2500 in" >= w_"min" = "0.1250 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"OK"*], "Minimum size", "AISC 360-22 Table J2.4")
#calcline([$"Maximum fillet size"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not applicable"*], "Maximum fillet size along edges of material does not apply: this weld is a T-joint, not a weld along an edge. No maximum size is checked.", "AISC 360-22 §J2.2b(b); Engineering judgement (EOR): no maximum fillet size at a T-joint")
#subhead("Weld metal")
#calcline([$F_"EXX" = "70.00 ksi"$], "Electrode classification strength, E70XX", "AISC 360-22 §J2.6; AWS A5.1")
#calcline([$display(F_"nw" = "0.6" F_"EXX" = "0.6" ("70.00 ksi") = "42.00 ksi")$], "Nominal stress of the weld metal", "AISC 360-22 Table J2.5")
#calcline([$Omega_w = "2.000"$], "Safety factor, fillet weld (ASD)", "AISC 360-22 Table J2.5")
#calcline([$k_"ds" = "1.000"$], "No directional strength increase at the post to baseplate weld: not elected by the engineer", "AISC 360-22 §J2.4(a)(3)")
#subhead("Base metal: baseplate fusion face")
#calcline([$F_u = "58.00 ksi"$], "Tensile strength, baseplate A36", "AISC Manual Table 2-5")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(R_(n,"BM") = "0.6" F_u t_p = "0.6" ("58.00 ksi") ("0.5000 in") = "17,400 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM"), Omega_"BM") = frac(("17,400 lb/in"), "2.000") = "8,700 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$"Post wall at the weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Covered by Check 5"*], "Post wall at the weld: covered by Check 5. The wall carries the weld force as stress along the post axis, the same demand as Check 5 at its critical section; member shear is not checked (stated assumption).", "Engineering judgement (EOR): post wall at the weld covered by Check 5")
#subhead("Demand: outward, distributed load")
#calcline([$P_D = "13.87 lb"$], "D at the post: axial dead load at the top of the baseplate", "Loading")
#calcline([$display(P = "1.0" P_D = "1.0" ("13.87 lb") = "13.87 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "60.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("60.00 in") = "250.0 lb")$], "Uniform guard load collected over the span, horizontal (outward), at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("250.0 lb") = "250.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V L_"post" = ("250.0 lb") ("41.50 in") = "10,380 lb-in")$], "Moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(f_a = frac(P, L_w) = frac(("13.87 lb"), ("5.969 in")) = "2.323 lb/in")$], "Axial force per inch of weld, compression, uniform around the ring", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_w) = frac(("10,380 lb-in"), ("2.835 in"^2)) = "3,659 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("2.323 lb/in") + ("3,659 lb/in") = "3,662 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("2.323 lb/in") - ("3,659 lb/in")) = "3,657 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "3,662 lb/in" >= f_(n,"t") = "3,657 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "3,662 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, L_w) = frac(("250.0 lb"), ("5.969 in")) = "41.88 lb/in")$], "Shear per inch of weld, taken as uniform around the ring", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("3,662 lb/in")^("2") + ("41.88 lb/in")^("2")) = "3,662 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.1767 in") dot "1.000" = "7,424 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("7,424 lb/in"), "2.000") = "3,712 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("3,662 lb/in"), ("3,712 lb/in")) = "0.99")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_r, frac(R_(n,"BM"), Omega_"BM")) = frac(("3,662 lb/in"), ("8,700 lb/in")) = "0.42")$], "Baseplate fusion face: the resultant per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.9865", "0.4209") = "0.99")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.99 <= 1.00$ #h(10pt) #"OK"])

= Summary

#table(columns: (1fr, auto, auto, auto, auto, auto), table.header(strong("Check"), strong("Demand"), strong("Capacity"), strong("Ratio"), strong("Controlling direction"), strong("Result")), "1. Top rail bending", "3,033 lb-in", "4,217 lb-in", "0.72", "Downward, concentrated", "OK", "2. Top rail deflection", "0.2983 in", "0.5000 in", "0.60", "Downward, concentrated", "OK", "3. Top rail weld to post", "41.88 lb/in", "778.4 lb/in (base metal)", "0.05", "Outward, distributed", "OK", "4a. Intermediate rail", "", "", "", "", "None", "4b. Intermediate rail weld to post", "", "", "", "", "None", "5. Post combined axial and flexure", "Pr = 13.87 lb; Mr = 10,380 lb-in", "Pc = 5,671 lb; Mc = 8,823 lb-in", "1.18", "Outward, distributed", "NG", "6. Post deflection", "0.7010 in", "0.6917 in", "1.01", "Outward, distributed", "NG", "7. Post weld to baseplate", "3,662 lb/in", "3,712 lb/in (weld metal)", "0.99", "Outward, distributed", "OK")

= Anchor reactions

LRFD reactions at the top of concrete, for direct input into anchor software: reporting, not a pass/fail check. Each set is simultaneous: the shear, axial force and moment that occur together.

#text(weight: "bold", "Baseplate: B = 6.000 in (parallel to rail) × N = 8.000 in (perpendicular to rail)")

#subhead("Dead load at the base")
#calcline([$D_"rail" = "4.462 lb"$], "Top rail", "Loading")
#calcline([$D_"post" = "9.407 lb"$], "Post, over h - t_p", "Loading")
#calcline([$rho = "0.2836 lb/in"^3$], "Steel unit weight", "AISC Manual 16th Ed., Part 17")
#calcline([$B = "6.000 in"$], "Baseplate, parallel to the rail", "Input")
#calcline([$N = "8.000 in"$], "Baseplate, perpendicular to the rail", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(W_"bp" = rho B N t_p = ("0.2836 lb/in"^3) ("6.000 in") ("8.000 in") ("0.5000 in") = "6.806 lb")$], "Baseplate weight: in the reaction sets only, below the critical section of Checks 5 and 7", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$display(D = D_"rail" + D_"post" + W_"bp" = ("4.462 lb") + ("9.407 lb") + ("6.806 lb") = "20.67 lb")$], "Dead load at the base", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#subhead("Governing guard load type")
#calcline([$P = "200.0 lb"$], "Concentrated guard load P, at the top of the post", "Loading")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "60.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(w_L L = ("4.167 lb/in") ("60.00 in") = "250.0 lb")$], "Uniform guard load collected over the span, at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$w_L L = "250.0 lb" > P = "200.0 lb"$ #h(6pt) $arrow.r$ #h(6pt) *#"Distributed load governs"*], "The larger at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Lateral set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "400.0 lb", "−18.61 lb (compression)", "16,800 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D axial, 1.6L horizontal; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "4.462 lb", "D, post", "9.407 lb", "D, baseplate", "6.806 lb", strong("D, total"), strong("20.67 lb"))

#"V and M act in the same vertical plane; M = V·h."

#"Lateral set applies in any horizontal direction; enter it in the anchor software in the orientation that governs the anchor pattern. Loads can reverse."

#subhead("Demand: lateral, distributed load")
#calcline([$D = "20.67 lb"$], "Dead load at the base", "Reactions")
#calcline([$display(abs(N_u) = "0.9" D = "0.9" ("20.67 lb") = "18.61 lb")$], "Axial force at the base: dead load, compression", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "60.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("60.00 in") = "250.0 lb")$], "Uniform guard load collected over the span, horizontal at the top of the post, in any horizontal direction", "Stated assumption: the tributary length is the span")
#calcline([$display(V_u = "1.6" V_L = "1.6" ("250.0 lb") = "400.0 lb")$], "Base shear", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$h = "42.00 in"$], "Moment arm: top rail centerline to top of concrete", "Input")
#calcline([$display(M_u = V_u h = ("400.0 lb") ("42.00 in") = "16,800 lb-in")$], "Base moment at the top of concrete: V_u at the top rail centerline, arm h", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Upward set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "0 lb", "+381.4 lb (tension)", "0 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D + 1.6L, net axial; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "4.462 lb", "D, post", "9.407 lb", "D, baseplate", "6.806 lb", strong("D, total"), strong("20.67 lb"))

#subhead("Demand: upward, distributed load")
#calcline([$D = "20.67 lb"$], "Dead load at the base", "Reactions")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "60.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(P_L = w_L L = ("4.167 lb/in") ("60.00 in") = "250.0 lb")$], "Uniform guard load collected over the span, upward at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(abs(N_u) = "1.6" P_L - "0.9" D = "1.6" ("250.0 lb") - "0.9" ("20.67 lb") = "381.4 lb")$], "Axial force at the base: net tension (uplift), guard load opposing dead load", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
