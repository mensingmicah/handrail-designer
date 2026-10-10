
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
+ #"Local strength of the rail wall at the post, and of the post wall at the intermediate rail (AISC 360-22 Chapter K chord limit states), is not checked."
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

#table(columns: (auto, 1fr, auto), table.header(strong("Entry"), strong("Citation"), strong("Source")), "material.A53_GrB.Fu", "AISC Manual Table 2-4", "memory", "ej.weld.post_wall.fu_fy_min", "Engineering judgement (EOR): post wall at the weld covered by Check 5 while Fu/Fy >= 1.20", "engineer", "asce7.guard.component", "ASCE 7-22 §4.5.1.2", "memory", "ej.post.axial_dead_load", "Engineering judgement (EOR): post dead load", "engineer", "ej.weld.line_method", "Engineering judgement (EOR): elastic weld as a line", "engineer", "aisc360.J2.2a.throat.coeff", "AISC 360-22 §J2.2a", "memory", "aisc360.J2.2a.throat", "AISC 360-22 §J2.2a", "memory", "ej.weld.ring_model", "Engineering judgement (EOR): weld ring at the rail underside, e = D_rail/2", "engineer", "aisc360.J2.4.min_size", "AISC 360-22 Table J2.4", "memory", "ej.weld.max_size_not_applicable", "Engineering judgement (EOR): no maximum fillet size at a T-joint", "engineer", "aisc360.J2.2b.max_size_edges", "AISC 360-22 §J2.2b(b)", "memory", "material.E70XX.FEXX", "AISC 360-22 §J2.6; AWS A5.1", "memory", "aisc360.J2.5.fnw.coeff", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.fnw", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.omega_w", "AISC 360-22 Table J2.5", "memory", "ej.weld.branch_kds", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld", "engineer", "aisc360.eq.J4-4.coeff", "AISC 360-22 Eq. J4-4", "memory", "aisc360.eq.J4-4", "AISC 360-22 Eq. J4-4", "memory", "aisc_manual.part9.base_metal", "AISC Manual Part 9, base metal at welds", "memory", "aisc360.J4.2.omega_rupture", "AISC 360-22 §J4.2(b)", "memory", "ej.weld.rail_wall_normal", "Engineering judgement (EOR): rail wall chord limit states not checked", "engineer", "ej.weld.post_wall_covered", "Engineering judgement (EOR): post wall at the weld covered by Check 5", "engineer", "ej.weld.no_bearing", "Engineering judgement (EOR): no bearing credit at the weld", "engineer", "aisc360.J2.4.fillet_strength", "AISC 360-22 §J2.4", "memory", "ej.intermediate.same_as_top", "Engineering judgement (EOR): intermediate rail controlled by Checks 1 and 2", "engineer", "ej.component.downward", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "engineer", "ej.component.midspan", "Engineering judgement (EOR): component load as a point load at midspan", "engineer", "aisc_manual.t3-23.case1.R", "AISC Manual Table 3-23, Case 1", "memory", "ej.weld.intermediate_ring_model", "Engineering judgement (EOR): weld ring at the post face, simple shear, P_c at the post", "engineer", "ej.weld.intermediate.same_as_top", "Engineering judgement (EOR): intermediate rail weld controlled by Check 3", "engineer", "ej.weld.intermediate_simple_shear", "Engineering judgement (EOR): intermediate rail to post weld as a simple shear connection", "engineer", "ej.weld.intermediate_base_metal", "Engineering judgement (EOR): Check 4b base metal on both walls, lower governs", "engineer", "ej.weld.post_wall_chord_intermediate", "Engineering judgement (EOR): post wall chord limit states at the intermediate rail not checked", "engineer", "aisc360.B4.1a.round_hss.lambda_r", "AISC 360-22 Table B4.1a, Case 9", "memory", "aisc360.B4.1a.classification", "AISC 360-22 §B4.1a", "memory", "aisc360.CA7.K_fixed_free", "AISC 360-22 Comm. Table C-A-7.1, case (e)", "memory", "aisc360.E2.effective_length", "AISC 360-22 §E2", "memory", "ej.post.unbraced_length", "Engineering judgement (EOR): unbraced length is the post height", "engineer", "aisc360.eq.E3-4", "AISC 360-22 Eq. E3-4", "memory", "aisc360.E2.user_note.slenderness", "AISC 360-22 §E2, User Note", "memory", "aisc360.E2.user_note.slenderness.limit", "AISC 360-22 §E2, User Note", "memory", "aisc360.E3.branch_limit", "AISC 360-22 §E3(a), (b)", "memory", "aisc360.eq.E3-2", "AISC 360-22 Eq. E3-2", "memory", "aisc360.eq.E3-2.base", "AISC 360-22 Eq. E3-2", "memory", "aisc360.eq.E3-1", "AISC 360-22 Eq. E3-1", "memory", "aisc360.E1.omega_c", "AISC 360-22 §E1", "memory", "aisc_manual.t3-23.case22.M", "AISC Manual Table 3-23, Case 22", "memory", "aisc360.eq.A-8-5", "AISC 360-22 Eq. A-8-5", "memory", "ej.second_order.pe_length", "Engineering judgement (EOR): Pe at Lc = 2.1h", "engineer", "aisc360.app8.alpha_asd", "AISC 360-22 App. 8", "memory", "ej.second_order.limit", "Engineering judgement (EOR): second-order limit", "engineer", "ej.second_order.negligible", "Engineering judgement (EOR): second-order limit", "engineer", "aisc360.H1.1.threshold", "AISC 360-22 §H1.1", "memory", "aisc360.eq.H1-1b", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.H1-1b.coeff", "AISC 360-22 Eq. H1-1b", "memory", "aisc_manual.t3-23.case22.delta", "AISC Manual Table 3-23, Case 22", "memory", "ej.deflection.limit.post", "Engineering judgement (EOR): post deflection limit, not code", "engineer", "material.A36.Fu", "AISC Manual Table 2-5", "memory", "aisc360.eq.J2-5", "AISC 360-22 Eq. J2-5", "memory", "aisc360.eq.J2-5.base", "AISC 360-22 Eq. J2-5", "memory", "aisc360.eq.J2-5.coeff", "AISC 360-22 Eq. J2-5", "memory", "aisc360.eq.J2-5.exponent", "AISC 360-22 Eq. J2-5", "memory", "ej.weld.directional_round_hss", "Engineering judgement (EOR), after STI: directional increase on round HSS", "engineer", "material.steel.density", "AISC Manual 16th Ed., Part 17", "memory", "ej.reaction.location", "Engineering judgement (EOR): reactions at the top of concrete, arm h", "engineer", "ej.combo.reaction", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "engineer", "ej.reaction.lateral_note", "Engineering judgement (EOR): one lateral set, any horizontal direction", "engineer")

= Dimensions

Every dimension as entered, and as the tool read it. A bare number is inches.

#table(columns: (1fr, auto, auto, auto), table.header(strong("Dimension"), strong("As entered"), strong("Read as"), strong("Inches")), "Span, post to post (c/c)", "12'-0\"", "12'-0\"", "144.0 in", "Post height h, top of concrete to top rail centerline", "42", "3'-6\"", "42.00 in", "Baseplate thickness t_p", "1/2", "1/2\"", "0.5000 in", "Baseplate B, parallel to the rail", "30", "2'-6\"", "30.00 in", "Baseplate N, perpendicular to the rail", "30", "2'-6\"", "30.00 in", "Fillet weld, top rail to post", "1/8", "1/8\"", "0.1250 in", "Fillet weld, post to baseplate", "1/4", "1/4\"", "0.2500 in")

Derived lengths, each computed in the calc where it is used:

#table(columns: (1fr, auto, auto, auto), table.header(strong("Derived length"), strong("Formula"), strong("Inches"), strong("Computed in")), "Post cantilever length, top of baseplate to top rail centerline", [$L_"post" = h - t_p$], "41.50 in", "Loading", "Eccentricity: rail centerline to the weld plane at the rail underside", [$e = frac(d_"rail", "2")$], "13.00 in", "Check 3", "Effective length, with the unbraced length taken as the post height h", [$L_c = K h$], "88.20 in", "Check 5")

= Section properties

#text("Top rail: Pipe26STD, A53 Gr B (default).") Properties are used exactly as published in the AISC Shapes Database v16.0.

#calcline([$D = "26.00 in"$], "Pipe26STD: outside diameter", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.3750 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.3490 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "28.20 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "8.583 lb/in"$], "Nominal weight: tabulated 103 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I = "2,320 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$S = "178.0 in"^3$], "Elastic section modulus", "AISC Shapes Database v16.0")
#calcline([$Z = "230.0 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$D slash t = "74.50"$], "Diameter-to-thickness ratio, tabulated", "AISC Shapes Database v16.0")

#text("Post: Pipe26STD, A53 Gr B (default).")

#calcline([$D = "26.00 in"$], "Pipe26STD: outside diameter", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.3750 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.3490 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "28.20 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "8.583 lb/in"$], "Nominal weight: tabulated 103 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I = "2,320 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$S = "178.0 in"^3$], "Elastic section modulus", "AISC Shapes Database v16.0")
#calcline([$Z = "230.0 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$r = "9.070 in"$], "Radius of gyration", "AISC Shapes Database v16.0")
#calcline([$D slash t = "74.50"$], "Diameter-to-thickness ratio, tabulated", "AISC Shapes Database v16.0")

#text("Intermediate rail: same section and grade as the top rail.")

#text("Baseplate: A36. Welds: fillet, all around, electrode E70XX.")

= Loading

Guard loads per ASCE 7-22. The concentrated and uniform loads are separate load types and do not act concurrently. Each check applies them in every direction case and reports the controlling one.

#calcline([$P = "400.0 lb"$], "Concentrated guard load, engineer override (code value 200.0 lb)", "Input; ASCE 7-22 §4.5.1")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load, 50 lb/ft, any direction; not concurrent with P", "ASCE 7-22 §4.5.1.1")
#calcline([$P_c = "5,000 lb"$], "Component load on the intermediate rail, engineer override (code value 50.00 lb)", "Input; ASCE 7-22 §4.5.1.2")
#calcline([$w_D = "8.583 lb/in"$], "Top rail self-weight: tabulated W = 103 lb/ft", "AISC Shapes Database v16.0")
#subhead("Dead load at the post")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(L_"post" = h - t_p = ("42.00 in") - ("0.5000 in") = "41.50 in")$], "Post cantilever length, top of baseplate to top rail centerline", "Stated assumption: post fixed at the top of the baseplate")
#calcline([$W_"post" = "8.583 lb/in"$], "Post self-weight: Pipe26STD, tabulated W = 103 lb/ft", "AISC Shapes Database v16.0")
#calcline([$display(D_"post" = W_"post" L_"post" = ("8.583 lb/in") ("41.50 in") = "356.2 lb")$], "Post dead load, full weight at the base", "Engineering judgement (EOR): post dead load")
#calcline([$L = "144.0 in"$], "Span: the tributary length for the post (stated assumption)", "Input")
#calcline([$display(D_"rail" = w_D L = ("8.583 lb/in") ("144.0 in") = "1,236 lb")$], "Top rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$w_(D,"int") = "8.583 lb/in"$], "Intermediate rail self-weight: Pipe26STD (same section as the top rail), tabulated W = 103 lb/ft", "AISC Shapes Database v16.0")
#calcline([$display(D_"int" = w_(D,"int") L = ("8.583 lb/in") ("144.0 in") = "1,236 lb")$], "Intermediate rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$display(P_D = D_"rail" + D_"int" + D_"post" = ("1,236 lb") + ("1,236 lb") + ("356.2 lb") = "2,828 lb")$], "D at the post: axial dead load at the top of the baseplate", "Engineering judgement (EOR): post dead load")

= Check 1: Top rail bending

#flag("NONCOMPACT: Pipe26STD D/t = 74.5 exceeds lambda_p = 58.00 (lambda_r = 256.9); Mn reduced by local buckling, AISC 360-22 Eq. F8-2.")

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $M_a$], [*Capacity* $M_n / Omega_b$], [*Ratio*], []), strong("Downward"), strong("Concentrated"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2"), strong("36,650 lb-in"), strong("4,602,000 lb-in"), strong("0.01"), strong("Controls"), "Downward", "Distributed", "1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2", "33,050 lb-in", "4,602,000 lb-in", "0.01", "", "Outward", "Concentrated", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "26,500 lb-in", "4,602,000 lb-in", "0.01", "", "Outward", "Distributed", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "24,730 lb-in", "4,602,000 lb-in", "0.01", "", "Inward", "Concentrated", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "26,500 lb-in", "4,602,000 lb-in", "0.01", "", "Inward", "Distributed", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "24,730 lb-in", "4,602,000 lb-in", "0.01", "", "Upward", "Concentrated", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "1,051 lb-in", "4,602,000 lb-in", "0.00", "", "Upward", "Distributed", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "2,549 lb-in", "4,602,000 lb-in", "0.00", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Downward, concentrated (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Capacity")
#calcline([$"Pipe26STD, A53 Gr B"$ #h(6pt) $arrow.r$ #h(6pt) *#"Designed as round HSS"*], "Pipe is designed under the round HSS provisions", "AISC Manual Table 2-4")
#calcline([$F_y = "35.00 ksi"$], "Yield stress, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$lambda = "74.50"$], "lambda = D/t, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$display(lambda_"lim" = frac("0.45" E, F_y) = frac("0.45" ("29,000 ksi"), ("35.00 ksi")) = "372.9")$], "Applicability limit on D/t", "AISC 360-22 §F8")
#calcline([$display(lambda_p = frac("0.07" E, F_y) = frac("0.07" ("29,000 ksi"), ("35.00 ksi")) = "58.00")$], "Compact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$display(lambda_r = frac("0.31" E, F_y) = frac("0.31" ("29,000 ksi"), ("35.00 ksi")) = "256.9")$], "Noncompact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$lambda = 74.5 < lambda_"lim" = 372.9$ #h(6pt) $arrow.r$ #h(6pt) *#"Applies"*], "Applicability", "AISC 360-22 §F8")
#calcline([$"Round HSS"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "Limit states: yielding and local buckling only; Lb and Cb do not enter", "AISC 360-22 §F8")
#calcline([$Z = "230.0 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$display(M_p = F_y Z = ("35.00 ksi") ("230.0 in"^3) = "8,050,000 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F8-1")
#calcline([$lambda_p = 58.00 < lambda = 74.5 <= lambda_r = 256.9$ #h(6pt) $arrow.r$ #h(6pt) *#"NONCOMPACT"*], "Section classification: reduced capacity", "AISC 360-22 §B4.1b")
#calcline([$S = "178.0 in"^3$], "Elastic section modulus", "AISC Shapes Database v16.0")
#calcline([$display(M_(n,"LB") = (frac("0.021" E, lambda) + F_y) S = (frac("0.021" ("29,000 ksi"), "74.50") + ("35.00 ksi")) ("178.0 in"^3) = "7,685,000 lb-in")$], "Local buckling, noncompact wall", "AISC 360-22 Eq. F8-2")
#calcline([$display(M_n = "min"(M_p, M_(n,"LB")) = "min"(("8,050,000 lb-in"), ("7,685,000 lb-in")) = "7,685,000 lb-in")$], "Lower of yielding and local buckling", "AISC 360-22 §F8")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$display(frac(M_n, Omega_b) = frac(("7,685,000 lb-in"), "1.670") = "4,602,000 lb-in")$], "Allowable flexural strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: downward, concentrated load")
#calcline([$L = "144.0 in"$], "Span, simple beam", "Input")
#calcline([$w_D = "8.583 lb/in"$], "Top rail self-weight", "Loading")
#calcline([$display(M_D = frac(w_D L^("2"), "8") = frac(("8.583 lb/in") ("144.0 in")^("2"), "8") = "22,250 lb-in")$], "Dead-load moment, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$P = "400.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(M_L = frac(P L, "4") = frac(("400.0 lb") ("144.0 in"), "4") = "14,400 lb-in")$], "Live-load moment, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$display(M_a = "1.0" M_D + "1.0" M_L = "1.0" ("22,250 lb-in") + "1.0" ("14,400 lb-in") = "36,650 lb-in")$], "Required flexural strength: D and L on the same axis", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display("Ratio" = frac(M_a, frac(M_n, Omega_b)) = frac(("36,650 lb-in"), ("4,602,000 lb-in")) = "0.01")$], "Demand / capacity", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.01 <= 1.00$ #h(10pt) #"OK"])

= Check 2: Top rail deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), strong("Downward"), strong("Concentrated"), strong("1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability"), strong("0.001084 in"), strong("1.200 in"), strong("0.00"), strong("Controls"), "Downward", "Distributed", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.001061 in", "1.200 in", "0.00", "", "Outward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.0003698 in", "1.200 in", "0.00", "", "Outward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.0003467 in", "1.200 in", "0.00", "", "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.0003698 in", "1.200 in", "0.00", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.0003467 in", "1.200 in", "0.00", "", "Upward", "Concentrated", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.0003698 in", "1.200 in", "0.00", "", "Upward", "Distributed", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.0003467 in", "1.200 in", "0.00", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Downward, concentrated (1.0D + 1.0L, vertical; Engineering judgement (EOR): serviceability)")

#calcline([$L = "144.0 in"$], "Span, simple beam", "Input")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I = "2,320 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$P = "400.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(Delta_L = frac(P L^("3"), "48" E I) = frac(("400.0 lb") ("144.0 in")^("3"), "48" ("29,000 ksi") ("2,320 in"^4)) = "0.0003698 in")$], "Live-load deflection, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$w_D = "8.583 lb/in"$], "Top rail self-weight", "Loading")
#calcline([$display(Delta_D = frac("5" w_D L^("4"), "384" E I) = frac("5" ("8.583 lb/in") ("144.0 in")^("4"), "384" ("29,000 ksi") ("2,320 in"^4)) = "0.0007143 in")$], "Dead-load deflection, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$display(Delta = "1.0" Delta_D + "1.0" Delta_L = "1.0" ("0.0007143 in") + "1.0" ("0.0003698 in") = "0.001084 in")$], "D and L on the same (vertical) axis", "Engineering judgement (EOR): serviceability")
#calcline([$display(Delta_"allow" = frac(L, "120") = frac(("144.0 in"), "120") = "1.200 in")$], "Limit L/120", "Engineering judgement (EOR): deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.001084 in"), ("1.200 in")) = "0.00")$], "Deflection / limit", "Engineering judgement (EOR): deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.00 <= 1.00$ #h(10pt) #"OK"])

= Check 3: Top rail weld to post

#flag("BELOW MINIMUM SIZE: Fillet weld w = 0.1250 in is below the minimum size 0.1875 in for the thinner part joined, t = 0.3750 in (AISC 360-22 Table J2.4).")

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "20.03 lb/in\nuniform", "—", "20.03 lb/in", "Weld 1,856 lb/in\nBase —", "0.01", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "22.48 lb/in\nuniform", "—", "22.48 lb/in", "Weld 1,856 lb/in\nBase —", "0.01", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "24.93 lb/in\ncompression side", "4.897 lb/in", "25.40 lb/in", "Weld 1,856 lb/in\nBase 6,282 lb/in", "0.01", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("29.82 lb/in\ncompression side"), strong("7.346 lb/in"), strong("30.71 lb/in"), strong("Weld 1,856 lb/in\nBase 6,282 lb/in"), strong("0.02"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "24.93 lb/in\ncompression side", "4.897 lb/in", "25.40 lb/in", "Weld 1,856 lb/in\nBase 6,282 lb/in", "0.01", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "29.82 lb/in\ncompression side", "7.346 lb/in", "30.71 lb/in", "Weld 1,856 lb/in\nBase 6,282 lb/in", "0.02", "", "Upward", "Concentrated", "No net tension (0.6D >= 1.0L); compression covered by downward", "", "", "", "", "", "", "Upward", "Distributed", "No net tension (0.6D >= 1.0L); compression covered by downward", "", "", "", "", "", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "24.93 lb/in\ncompression side", "4.897 lb/in", "25.40 lb/in", "Weld 1,856 lb/in\nBase 6,282 lb/in", "0.01", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "29.82 lb/in\ncompression side", "7.346 lb/in", "30.71 lb/in", "Weld 1,856 lb/in\nBase 6,282 lb/in", "0.02", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$D = "26.00 in"$], "Pipe26STD: outside diameter; the weld ring is the post perimeter", "AISC Shapes Database v16.0")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(L_w = pi D = pi ("26.00 in") = "81.68 in")$], "Weld length: the post perimeter", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(S_w = frac(pi D^("2"), "4") = frac(pi ("26.00 in")^("2"), "4") = "530.9 in"^2)$], "Section modulus of the ring as a line", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Eccentricity")
#calcline([$d_"rail" = "26.00 in"$], "Pipe26STD: outside diameter, the rail depth", "AISC Shapes Database v16.0")
#calcline([$display(e = frac(d_"rail", "2") = frac(("26.00 in"), "2") = "13.00 in")$], "Eccentricity: rail centerline to the weld plane at the rail underside", "Engineering judgement (EOR): weld ring at the rail underside, e = D_rail/2")
#subhead("Fillet size limits")
#calcline([$t_"rail,nom" = "0.3750 in"$], "Top rail nominal wall thickness, Pipe26STD", "AISC Shapes Database v16.0")
#calcline([$t_"post,nom" = "0.3750 in"$], "Post nominal wall thickness, Pipe26STD", "AISC Shapes Database v16.0")
#calcline([$display(t_"min" = "min"(t_"rail,nom", t_"post,nom") = "min"(("0.3750 in"), ("0.3750 in")) = "0.3750 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w_"min" = "0.1875 in"$], "Minimum fillet size for the thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w = "0.1250 in" < w_"min" = "0.1875 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"NG: below the minimum size"*], "Minimum size: the check fails whatever its ratio", "AISC 360-22 Table J2.4")
#calcline([$"Maximum fillet size"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not applicable"*], "Maximum fillet size along edges of material does not apply: this weld is a T-joint, not a weld along an edge. No maximum size is checked.", "AISC 360-22 §J2.2b(b); Engineering judgement (EOR): no maximum fillet size at a T-joint")
#subhead("Weld metal")
#calcline([$F_"EXX" = "70.00 ksi"$], "Electrode classification strength, E70XX", "AISC 360-22 §J2.6; AWS A5.1")
#calcline([$display(F_"nw" = "0.6" F_"EXX" = "0.6" ("70.00 ksi") = "42.00 ksi")$], "Nominal stress of the weld metal", "AISC 360-22 Table J2.5")
#calcline([$Omega_w = "2.000"$], "Safety factor, fillet weld (ASD)", "AISC 360-22 Table J2.5")
#calcline([$k_"ds" = "1.000"$], "No directional increase at the rail to post weld (a branch-to-chord joint)", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld")
#subhead("Base metal: rail fusion face")
#calcline([$F_u = "60.00 ksi"$], "Tensile strength, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"rail" = "0.3490 in"$], "Top rail design wall thickness, Pipe26STD", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM") = "0.6" F_u t_"rail" = "0.6" ("60.00 ksi") ("0.3490 in") = "12,560 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM"), Omega_"BM") = frac(("12,560 lb/in"), "2.000") = "6,282 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$"Rail wall, normal force"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not checked"*], "Rail wall, force normal to the wall: a chord-wall limit state of the round T-connection (AISC 360-22 Chapter K), not weld base metal; not checked (stated assumption).", "Engineering judgement (EOR): rail wall chord limit states not checked")
#calcline([$"Post wall at the weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Covered by Check 5"*], "Post wall at the weld: covered by Check 5. The wall carries the weld force as stress along the post axis, the same demand as Check 5 at its critical section; member shear is not checked (stated assumption).", "Engineering judgement (EOR): post wall at the weld covered by Check 5")
#subhead("Demand: outward, distributed load")
#calcline([$D_"rail" = "1,236 lb"$], "Top rail dead load at the weld: w_D over the span (the tributary length)", "Loading")
#calcline([$display(P = "1.0" D_"rail" = "1.0" ("1,236 lb") = "1,236 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "144.0 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("144.0 in") = "600.0 lb")$], "Uniform guard load collected over the span, horizontal (outward), on the rail at the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("600.0 lb") = "600.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V e = ("600.0 lb") ("13.00 in") = "7,800 lb-in")$], "Moment at the weld plane: V at the rail centerline, arm e", "Engineering judgement (EOR): weld ring at the rail underside, e = D_rail/2")
#calcline([$display(f_a = frac(P, L_w) = frac(("1,236 lb"), ("81.68 in")) = "15.13 lb/in")$], "Axial force per inch of weld, compression, uniform around the ring", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_w) = frac(("7,800 lb-in"), ("530.9 in"^2)) = "14.69 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("15.13 lb/in") + ("14.69 lb/in") = "29.82 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("15.13 lb/in") - ("14.69 lb/in")) = "0.4407 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "29.82 lb/in" >= f_(n,"t") = "0.4407 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "29.82 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, L_w) = frac(("600.0 lb"), ("81.68 in")) = "7.346 lb/in")$], "Shear per inch of weld, taken as uniform around the ring", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("29.82 lb/in")^("2") + ("7.346 lb/in")^("2")) = "30.71 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 §J2.4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("30.71 lb/in"), ("1,856 lb/in")) = "0.02")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM"), Omega_"BM")) = frac(("7.346 lb/in"), ("6,282 lb/in")) = "0.00")$], "Rail fusion face: in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.01655", "0.001169") = "0.02")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.02 <= 1.00$ #h(6pt) #"; below minimum size"#h(10pt) #"NG"])

= Check 4a: Intermediate rail

#flag("NONCOMPACT: Pipe26STD D/t = 74.5 exceeds lambda_p = 58.00 (lambda_r = 256.9); Mn reduced by local buckling, AISC 360-22 Eq. F8-2.")

== Envelope summary

Each limit state is computed in both directions of the component load. The full calculation follows for the governing case of each limit state.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Limit state*], [*Direction*], [*Combination*], [*Demand* $M_a$ or $Delta$], [*Capacity* $M_n / Omega_b$ or $Delta_"allow"$], [*Ratio*], []), strong("Bending"), strong("Downward"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)"), strong("202,200 lb-in"), strong("4,602,000 lb-in"), strong("0.04"), strong("Controls"), "Bending", "Horizontal", "1.0L horizontal, alone\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "180,000 lb-in", "4,602,000 lb-in", "0.04", "", "Deflection", "Downward", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.005337 in", "1.200 in", "0.00", "", "Deflection", "Horizontal", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.004623 in", "1.200 in", "0.00", "")

#heading(level: 2, "Controlling case: Downward, bending (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5))")

#calcline([$P_c = "5,000 lb" > P = "400.0 lb"$ #h(6pt) $arrow.r$ #h(6pt) *#"Computed in full"*], "Same section as the top rail, but the component load exceeds the concentrated guard load, so Checks 1 and 2 do not cover it", "Engineering judgement (EOR): intermediate rail controlled by Checks 1 and 2")
#subhead("Capacity")
#calcline([$"Pipe26STD, A53 Gr B"$ #h(6pt) $arrow.r$ #h(6pt) *#"Designed as round HSS"*], "Pipe is designed under the round HSS provisions", "AISC Manual Table 2-4")
#calcline([$F_y = "35.00 ksi"$], "Yield stress, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$lambda = "74.50"$], "lambda = D/t, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$display(lambda_"lim" = frac("0.45" E, F_y) = frac("0.45" ("29,000 ksi"), ("35.00 ksi")) = "372.9")$], "Applicability limit on D/t", "AISC 360-22 §F8")
#calcline([$display(lambda_p = frac("0.07" E, F_y) = frac("0.07" ("29,000 ksi"), ("35.00 ksi")) = "58.00")$], "Compact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$display(lambda_r = frac("0.31" E, F_y) = frac("0.31" ("29,000 ksi"), ("35.00 ksi")) = "256.9")$], "Noncompact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$lambda = 74.5 < lambda_"lim" = 372.9$ #h(6pt) $arrow.r$ #h(6pt) *#"Applies"*], "Applicability", "AISC 360-22 §F8")
#calcline([$"Round HSS"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "Limit states: yielding and local buckling only; Lb and Cb do not enter", "AISC 360-22 §F8")
#calcline([$Z = "230.0 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$display(M_p = F_y Z = ("35.00 ksi") ("230.0 in"^3) = "8,050,000 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F8-1")
#calcline([$lambda_p = 58.00 < lambda = 74.5 <= lambda_r = 256.9$ #h(6pt) $arrow.r$ #h(6pt) *#"NONCOMPACT"*], "Section classification: reduced capacity", "AISC 360-22 §B4.1b")
#calcline([$S = "178.0 in"^3$], "Elastic section modulus", "AISC Shapes Database v16.0")
#calcline([$display(M_(n,"LB") = (frac("0.021" E, lambda) + F_y) S = (frac("0.021" ("29,000 ksi"), "74.50") + ("35.00 ksi")) ("178.0 in"^3) = "7,685,000 lb-in")$], "Local buckling, noncompact wall", "AISC 360-22 Eq. F8-2")
#calcline([$display(M_n = "min"(M_p, M_(n,"LB")) = "min"(("8,050,000 lb-in"), ("7,685,000 lb-in")) = "7,685,000 lb-in")$], "Lower of yielding and local buckling", "AISC 360-22 §F8")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$display(frac(M_n, Omega_b) = frac(("7,685,000 lb-in"), "1.670") = "4,602,000 lb-in")$], "Allowable flexural strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: downward, component load")
#calcline([$L = "144.0 in"$], "Span, simple beam", "Input")
#calcline([$P_c = "5,000 lb"$], "Component load, a point load at midspan", "Loading")
#calcline([$display(M_L = frac(P_c L, "4") = frac(("5,000 lb") ("144.0 in"), "4") = "180,000 lb-in")$], "Component load moment, midspan", "AISC Manual Table 3-23, Case 7; Engineering judgement (EOR): component load as a point load at midspan")
#calcline([$w_(D,"int") = "8.583 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$display(M_D = frac(w_(D,"int") L^("2"), "8") = frac(("8.583 lb/in") ("144.0 in")^("2"), "8") = "22,250 lb-in")$], "Dead-load moment, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$display(M_a = "1.0" M_D + "1.0" M_L = "1.0" ("22,250 lb-in") + "1.0" ("180,000 lb-in") = "202,200 lb-in")$], "Required flexural strength: D and L on the same axis", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display("Ratio" = frac(M_a, frac(M_n, Omega_b)) = frac(("202,200 lb-in"), ("4,602,000 lb-in")) = "0.04")$], "Demand / capacity", "AISC 360-22 Eq. B3-2")

#heading(level: 2, "Governing deflection case: Downward, deflection (1.0D + 1.0L, vertical; Engineering judgement (EOR): serviceability)")

#calcline([$P_c = "5,000 lb" > P = "400.0 lb"$ #h(6pt) $arrow.r$ #h(6pt) *#"Computed in full"*], "Same section as the top rail, but the component load exceeds the concentrated guard load, so Checks 1 and 2 do not cover it", "Engineering judgement (EOR): intermediate rail controlled by Checks 1 and 2")
#calcline([$L = "144.0 in"$], "Span, simple beam", "Input")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_"int" = "2,320 in"^4$], "Moment of inertia, Pipe26STD", "AISC Shapes Database v16.0")
#calcline([$P_c = "5,000 lb"$], "Component load, a point load at midspan", "Loading")
#calcline([$display(Delta_L = frac(P_c L^("3"), "48" E I_"int") = frac(("5,000 lb") ("144.0 in")^("3"), "48" ("29,000 ksi") ("2,320 in"^4)) = "0.004623 in")$], "Component load deflection, midspan", "AISC Manual Table 3-23, Case 7; Engineering judgement (EOR): component load as a point load at midspan")
#calcline([$w_(D,"int") = "8.583 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$display(Delta_D = frac("5" w_(D,"int") L^("4"), "384" E I_"int") = frac("5" ("8.583 lb/in") ("144.0 in")^("4"), "384" ("29,000 ksi") ("2,320 in"^4)) = "0.0007143 in")$], "Dead-load deflection, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$display(Delta = "1.0" Delta_D + "1.0" Delta_L = "1.0" ("0.0007143 in") + "1.0" ("0.004623 in") = "0.005337 in")$], "D and L on the same (vertical) axis", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); Engineering judgement (EOR): serviceability")
#calcline([$display(Delta_"allow" = frac(L, "120") = frac(("144.0 in"), "120") = "1.200 in")$], "Limit L/120", "Engineering judgement (EOR): deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.005337 in"), ("1.200 in")) = "0.00")$], "Deflection / limit", "Engineering judgement (EOR): deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.04 <= 1.00$ #h(10pt) #"OK"])

= Check 4b: Intermediate rail weld to post

#flag("BELOW MINIMUM SIZE: Fillet weld w = 0.1250 in is below the minimum size 0.1875 in for the thinner part joined, t = 0.3750 in (AISC 360-22 Table J2.4).")

== Envelope summary

Both directions of the component load are computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), strong("Downward"), strong("Component"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)"), strong("—\nshear only"), strong("68.78 lb/in"), strong("68.78 lb/in"), strong("Weld 1,856 lb/in\nBase 6,282 lb/in"), strong("0.04"), strong("Controls"), "Horizontal", "Component", "1.0D vertical, 1.0L horizontal, vector sum\nASCE 7-22 §2.4.1, Comb. 2", "—\nshear only", "61.68 lb/in", "61.68 lb/in", "Weld 1,856 lb/in\nBase 6,282 lb/in", "0.03", "")]

#heading(level: 2, "Controlling case: Downward, component (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5))")

#calcline([$R = "5,618 lb" > P = "400.0 lb"$ #h(6pt) $arrow.r$ #h(6pt) *#"Computed in full"*], "Same section as the top rail, but the weld reaction exceeds the concentrated guard load, so Check 3 does not cover it", "Engineering judgement (EOR): intermediate rail weld controlled by Check 3")
#subhead("Weld properties")
#calcline([$D_"int" = "26.00 in"$], "Pipe26STD: outside diameter; the weld ring is the intermediate rail perimeter", "AISC Shapes Database v16.0")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(L_w = pi D_"int" = pi ("26.00 in") = "81.68 in")$], "Weld length: the intermediate rail perimeter", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Connection model")
#calcline([$"Intermediate rail to post weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Simple shear connection"*], "Simple shear connection consistent with the simple-span member assumption; no end moment at the weld.", "Engineering judgement (EOR): intermediate rail to post weld as a simple shear connection; Engineering judgement (EOR): weld ring at the post face, simple shear, P_c at the post")
#subhead("Fillet size limits")
#calcline([$t_"int,nom" = "0.3750 in"$], "Intermediate rail nominal wall thickness, Pipe26STD", "AISC Shapes Database v16.0")
#calcline([$t_"post,nom" = "0.3750 in"$], "Post nominal wall thickness, Pipe26STD", "AISC Shapes Database v16.0")
#calcline([$display(t_"min" = "min"(t_"int,nom", t_"post,nom") = "min"(("0.3750 in"), ("0.3750 in")) = "0.3750 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w_"min" = "0.1875 in"$], "Minimum fillet size for the thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w = "0.1250 in" < w_"min" = "0.1875 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"NG: below the minimum size"*], "Minimum size: the check fails whatever its ratio", "AISC 360-22 Table J2.4")
#calcline([$"Maximum fillet size"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not applicable"*], "Maximum fillet size along edges of material does not apply: this weld is a T-joint, not a weld along an edge. No maximum size is checked.", "AISC 360-22 §J2.2b(b); Engineering judgement (EOR): no maximum fillet size at a T-joint")
#subhead("Weld metal")
#calcline([$F_"EXX" = "70.00 ksi"$], "Electrode classification strength, E70XX", "AISC 360-22 §J2.6; AWS A5.1")
#calcline([$display(F_"nw" = "0.6" F_"EXX" = "0.6" ("70.00 ksi") = "42.00 ksi")$], "Nominal stress of the weld metal", "AISC 360-22 Table J2.5")
#calcline([$Omega_w = "2.000"$], "Safety factor, fillet weld (ASD)", "AISC 360-22 Table J2.5")
#calcline([$k_"ds" = "1.000"$], "No directional increase at the intermediate rail to post weld (a branch-to-chord joint)", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld")
#subhead("Base metal: post wall fusion face (chord)")
#calcline([$F_u = "60.00 ksi"$], "Tensile strength, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"post" = "0.3490 in"$], "Post design wall thickness, Pipe26STD", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM,post") = "0.6" F_u t_"post" = "0.6" ("60.00 ksi") ("0.3490 in") = "12,560 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM,post"), Omega_"BM") = frac(("12,560 lb/in"), "2.000") = "6,282 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#subhead("Base metal: intermediate rail wall fusion face (branch)")
#calcline([$F_u = "60.00 ksi"$], "Tensile strength, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"int" = "0.3490 in"$], "Intermediate rail design wall thickness, Pipe26STD", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM,int") = "0.6" F_u t_"int" = "0.6" ("60.00 ksi") ("0.3490 in") = "12,560 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM,int"), Omega_"BM") = frac(("12,560 lb/in"), "2.000") = "6,282 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$frac(R_(n,"BM,int"), Omega_"BM") = "6,282 lb/in" = frac(R_(n,"BM,post"), Omega_"BM") = "6,282 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Post wall governs"*], "Base metal is checked at the fusion face of both connected parts, the post wall (the chord) and the intermediate rail wall (the branch), each in shear rupture against the in-plane shear per inch; the lower allowable governs.", "Engineering judgement (EOR): Check 4b base metal on both walls, lower governs")
#calcline([$"Post wall, chord limit states"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not checked"*], "Post wall at the intermediate rail: chord-wall limit states of the round T-connection (AISC 360-22 Chapter K) not checked (stated assumption).", "Engineering judgement (EOR): post wall chord limit states at the intermediate rail not checked")
#subhead("Demand: downward, component load")
#calcline([$w_(D,"int") = "8.583 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$L = "144.0 in"$], "Span, simple beam", "Input")
#calcline([$display(R_D = frac(w_(D,"int") L, "2") = frac(("8.583 lb/in") ("144.0 in"), "2") = "618.0 lb")$], "Dead-load end reaction at the post", "AISC Manual Table 3-23, Case 1")
#calcline([$P_c = "5,000 lb"$], "Component load adjacent to the post: the full P_c to this end", "Engineering judgement (EOR): weld ring at the post face, simple shear, P_c at the post")
#calcline([$display(R = "1.0" R_D + "1.0" P_c = "1.0" ("618.0 lb") + "1.0" ("5,000 lb") = "5,618 lb")$], "Weld reaction: dead and component loads in the same (vertical) direction, in the ring's plane", "Engineering judgement (EOR): weld ring at the post face, simple shear, P_c at the post; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(f_v = frac(R, L_w) = frac(("5,618 lb"), ("81.68 in")) = "68.78 lb/in")$], "Shear per inch of weld, taken as uniform around the ring", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = f_v = "68.78 lb/in")$], "Resultant per inch: shear only, no axial force and no moment", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 §J2.4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("68.78 lb/in"), ("1,856 lb/in")) = "0.04")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM,post"), Omega_"BM")) = frac(("68.78 lb/in"), ("6,282 lb/in")) = "0.01")$], "Base metal, post wall fusion face (governs): in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.03706", "0.01095") = "0.04")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.04 <= 1.00$ #h(6pt) #"; below minimum size"#h(10pt) #"NG"])

= Check 5: Post combined axial and flexure

#flag("NONCOMPACT: Pipe26STD D/t = 74.5 exceeds lambda_p = 58.00 (lambda_r = 256.9); Mn reduced by local buckling, AISC 360-22 Eq. F8-2.")

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Axial* $P_r$ \ capacity $P_c$ or $P_t$], [*Moment* $M_r$ \ capacity $M_c$], [*Equation*], [$frac(alpha P_r, P_e)$], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "3,228 lb comp.\nPc = 588,200 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.01", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "3,428 lb comp.\nPc = 588,200 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.01", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,828 lb comp.\nPc = 588,200 lb", "16,600 lb-in\nMc = 4,602,000 lb-in", "Eq. H1-1b", "0.00005301", "0.01", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("2,828 lb comp.\nPc = 588,200 lb"), strong("24,900 lb-in\nMc = 4,602,000 lb-in"), strong("Eq. H1-1b"), strong("0.00005301"), strong("0.01"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,828 lb comp.\nPc = 588,200 lb", "16,600 lb-in\nMc = 4,602,000 lb-in", "Eq. H1-1b", "0.00005301", "0.01", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,828 lb comp.\nPc = 588,200 lb", "24,900 lb-in\nMc = 4,602,000 lb-in", "Eq. H1-1b", "0.00005301", "0.01", "", "Upward", "Concentrated", "No net tension (0.6D >= 1.0L); compression covered by downward", "", "", "", "", "", "", "Upward", "Distributed", "No net tension (0.6D >= 1.0L); compression covered by downward", "", "", "", "", "", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,828 lb comp.\nPc = 588,200 lb", "16,600 lb-in\nMc = 4,602,000 lb-in", "Eq. H1-1b", "0.00005301", "0.01", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,828 lb comp.\nPc = 588,200 lb", "24,900 lb-in\nMc = 4,602,000 lb-in", "Eq. H1-1b", "0.00005301", "0.01", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Capacity")
#calcline([$"Pipe26STD, A53 Gr B"$ #h(6pt) $arrow.r$ #h(6pt) *#"Designed as round HSS"*], "Pipe is designed under the round HSS provisions", "AISC Manual Table 2-4")
#calcline([$F_y = "35.00 ksi"$], "Yield stress, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$lambda = "74.50"$], "lambda = D/t, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$display(lambda_"lim" = frac("0.45" E, F_y) = frac("0.45" ("29,000 ksi"), ("35.00 ksi")) = "372.9")$], "Applicability limit on D/t", "AISC 360-22 §F8")
#calcline([$display(lambda_p = frac("0.07" E, F_y) = frac("0.07" ("29,000 ksi"), ("35.00 ksi")) = "58.00")$], "Compact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$display(lambda_r = frac("0.31" E, F_y) = frac("0.31" ("29,000 ksi"), ("35.00 ksi")) = "256.9")$], "Noncompact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$lambda = 74.5 < lambda_"lim" = 372.9$ #h(6pt) $arrow.r$ #h(6pt) *#"Applies"*], "Applicability", "AISC 360-22 §F8")
#calcline([$"Round HSS"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "Limit states: yielding and local buckling only; Lb and Cb do not enter", "AISC 360-22 §F8")
#calcline([$Z = "230.0 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$display(M_p = F_y Z = ("35.00 ksi") ("230.0 in"^3) = "8,050,000 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F8-1")
#calcline([$lambda_p = 58.00 < lambda = 74.5 <= lambda_r = 256.9$ #h(6pt) $arrow.r$ #h(6pt) *#"NONCOMPACT"*], "Section classification: reduced capacity", "AISC 360-22 §B4.1b")
#calcline([$S = "178.0 in"^3$], "Elastic section modulus", "AISC Shapes Database v16.0")
#calcline([$display(M_(n,"LB") = (frac("0.021" E, lambda) + F_y) S = (frac("0.021" ("29,000 ksi"), "74.50") + ("35.00 ksi")) ("178.0 in"^3) = "7,685,000 lb-in")$], "Local buckling, noncompact wall", "AISC 360-22 Eq. F8-2")
#calcline([$display(M_n = "min"(M_p, M_(n,"LB")) = "min"(("8,050,000 lb-in"), ("7,685,000 lb-in")) = "7,685,000 lb-in")$], "Lower of yielding and local buckling", "AISC 360-22 §F8")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$display(frac(M_n, Omega_b) = frac(("7,685,000 lb-in"), "1.670") = "4,602,000 lb-in")$], "Allowable flexural strength", "AISC 360-22 Eq. B3-2")
#calcline([$display(M_c = frac(M_n, Omega_b) = "4,602,000 lb-in")$], "Allowable flexural strength, as used in Chapter H", "AISC 360-22 Eq. B3-2")
#calcline([$display(lambda_(r,c) = frac("0.11" E, F_y) = frac("0.11" ("29,000 ksi"), ("35.00 ksi")) = "91.14")$], "Slender limit, round HSS in compression", "AISC 360-22 Table B4.1a, Case 9")
#calcline([$lambda = 74.5 <= lambda_(r,c) = 91.14$ #h(6pt) $arrow.r$ #h(6pt) *#"Nonslender"*], "Section classification, compression: no noncompact category", "AISC 360-22 §B4.1a")
#calcline([$K = "2.100"$], "Effective length factor, fixed-free (recommended design value)", "AISC 360-22 Comm. Table C-A-7.1, case (e)")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$display(L_c = K h = "2.100" ("42.00 in") = "88.20 in")$], "Effective length, with the unbraced length taken as the post height h", "AISC 360-22 §E2; Engineering judgement (EOR): unbraced length is the post height")
#calcline([$r = "9.070 in"$], "Radius of gyration", "AISC Shapes Database v16.0")
#calcline([$display(frac(L_c, r) = frac(("88.20 in"), ("9.070 in")) = "9.724")$], "Effective slenderness ratio", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 9.724 <= 200$ #h(6pt) $arrow.r$ #h(6pt) *#"Within the recommended limit"*], "For members designed on the basis of compression, the effective slenderness ratio Lc/r preferably should not exceed 200.", "AISC 360-22 §E2, User Note")
#calcline([$display("4.71" sqrt(frac(E, F_y)) = "4.71" dot sqrt(frac(("29,000 ksi"), ("35.00 ksi"))) = "135.6")$], "Limit between inelastic and elastic buckling", "AISC 360-22 §E3(a), (b)")
#calcline([$display(F_e = frac(pi^("2") E, (frac(L_c, r))^("2")) = frac(pi^("2") ("29,000 ksi"), "9.724"^("2")) = "3,027 ksi")$], "Elastic buckling stress", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 9.724 <= 135.6$ #h(6pt) $arrow.r$ #h(6pt) *#"Inelastic buckling: Eq. E3-2"*], "", "AISC 360-22 §E3(a), (b)")
#calcline([$display(frac(F_y, F_e) = frac(("35.00 ksi"), ("3,027 ksi")) = "0.01156")$], "Exponent in Eq. E3-2", "AISC 360-22 Eq. E3-2")
#calcline([$display(F_"cr" = "0.658"^(frac(F_y, F_e)) F_y = "0.658"^("0.01156") ("35.00 ksi") = "34.83 ksi")$], "Critical stress", "AISC 360-22 Eq. E3-2")
#calcline([$A_g = "28.20 in"^2$], "Gross area", "AISC Shapes Database v16.0")
#calcline([$display(P_n = F_"cr" A_g = ("34.83 ksi") ("28.20 in"^2) = "982,200 lb")$], "Nominal compressive strength", "AISC 360-22 Eq. E3-1")
#calcline([$Omega_c = "1.670"$], "Safety factor for compression (ASD)", "AISC 360-22 §E1")
#calcline([$display(P_c = frac(P_n, Omega_c) = frac(("982,200 lb"), "1.670") = "588,200 lb")$], "Allowable compressive strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: outward, distributed load")
#calcline([$P_D = "2,828 lb"$], "D at the post: axial dead load", "Loading")
#calcline([$display(P_r = "1.0" P_D = "1.0" ("2,828 lb") = "2,828 lb")$], "Required axial strength: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "144.0 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("144.0 in") = "600.0 lb")$], "Uniform guard load collected over the span, horizontal (outward) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p (critical section at the top of the baseplate)", "Loading")
#calcline([$display(M_L = V_L L_"post" = ("600.0 lb") ("41.50 in") = "24,900 lb-in")$], "Live-load moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(M_r = "1.0" M_L = "1.0" ("24,900 lb-in") = "24,900 lb-in")$], "Required flexural strength", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$I = "2,320 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$display(P_e = frac(pi^("2") E I, L_c^("2")) = frac(pi^("2") ("29,000 ksi") ("2,320 in"^4), ("88.20 in")^("2")) = "85,360,000 lb")$], "Elastic critical buckling load, at the compression Lc", "AISC 360-22 Eq. A-8-5; Engineering judgement (EOR): Pe at Lc = 2.1h")
#calcline([$display(frac(alpha P_r, P_e) = frac("1.6" P_r, P_e) = frac("1.6" ("2,828 lb"), ("85,360,000 lb")) = "0.00005301")$], "Second-order ratio", "AISC 360-22 App. 8")
#calcline([$frac(alpha P_r, P_e) <= 0.05$ #h(6pt) $arrow.r$ #h(6pt) *#"Second-order effects negligible: αPr/Pe = 0.00005301; amplification taken as 1.0."*], "", "Engineering judgement (EOR): second-order limit")
#calcline([$display(frac(P_r, P_c) = frac(("2,828 lb"), ("588,200 lb")) = "0.004809")$], "Axial ratio, selects the interaction equation", "AISC 360-22 §H1.1")
#calcline([$frac(P_r, P_c) = 0.004809 < 0.2$ #h(6pt) $arrow.r$ #h(6pt) *#"Eq. H1-1b"*], "", "AISC 360-22 §H1.1")
#calcline([$display("Ratio" = frac(P_r, "2" P_c) + frac(M_r, M_c) = frac(("2,828 lb"), "2" ("588,200 lb")) + frac(("24,900 lb-in"), ("4,602,000 lb-in")) = "0.01")$], "Combined axial and flexure", "AISC 360-22 Eq. H1-1b")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.01 <= 1.00$ #h(10pt) #"OK"])

= Check 6: Post deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), "Downward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Outward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.0001416 in", "0.6917 in", "0.00", "", strong("Outward"), strong("Distributed"), strong("1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only"), strong("0.0002125 in"), strong("0.6917 in"), strong("0.00"), strong("Controls"), "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.0001416 in", "0.6917 in", "0.00", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.0002125 in", "0.6917 in", "0.00", "", "Upward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Longitudinal", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.0001416 in", "0.6917 in", "0.00", "", "Longitudinal", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.0002125 in", "0.6917 in", "0.00", "")

#heading(level: 2, "Controlling case: Outward, distributed (1.0L, horizontal; Engineering judgement (EOR): serviceability, live load only)")

#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p", "Loading")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I = "2,320 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "144.0 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("144.0 in") = "600.0 lb")$], "Uniform guard load collected over the span, horizontal (outward) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(Delta_L = frac(V_L L_"post"^("3"), "3" E I) = frac(("600.0 lb") ("41.50 in")^("3"), "3" ("29,000 ksi") ("2,320 in"^4)) = "0.0002125 in")$], "Live-load deflection at the top of the post", "AISC Manual Table 3-23, Case 22")
#calcline([$display(Delta = "1.0" Delta_L = "1.0" ("0.0002125 in") = "0.0002125 in")$], "Live load only; dead load acts axially", "Engineering judgement (EOR): serviceability, live load only")
#calcline([$display(Delta_"allow" = frac(L_"post", "60") = frac(("41.50 in"), "60") = "0.6917 in")$], "Limit (h - t_p)/60", "Engineering judgement (EOR): post deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.0002125 in"), ("0.6917 in")) = "0.00")$], "Deflection / limit", "Engineering judgement (EOR): post deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.00 <= 1.00$ #h(10pt) #"OK"])

= Check 7: Post weld to baseplate

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [$theta$ \ $k_"ds"$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "39.52 lb/in\nuniform", "—", "39.52 lb/in", "90.00°\n1.500", "Weld 5,568 lb/in\nBase 8,700 lb/in", "0.01", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "41.97 lb/in\nuniform", "—", "41.97 lb/in", "90.00°\n1.500", "Weld 5,568 lb/in\nBase 8,700 lb/in", "0.01", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "65.89 lb/in\ncompression side", "4.897 lb/in", "66.07 lb/in", "90.00°\n1.500", "Weld 5,568 lb/in\nBase 8,700 lb/in", "0.01", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("81.52 lb/in\ncompression side"), strong("7.346 lb/in"), strong("81.85 lb/in"), strong("90.00°\n1.500"), strong("Weld 5,568 lb/in\nBase 8,700 lb/in"), strong("0.01"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "65.89 lb/in\ncompression side", "4.897 lb/in", "66.07 lb/in", "90.00°\n1.500", "Weld 5,568 lb/in\nBase 8,700 lb/in", "0.01", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "81.52 lb/in\ncompression side", "7.346 lb/in", "81.85 lb/in", "90.00°\n1.500", "Weld 5,568 lb/in\nBase 8,700 lb/in", "0.01", "", "Upward", "Concentrated", "No net tension (0.6D >= 1.0L); compression covered by downward", "", "", "", "", "", "", "", "Upward", "Distributed", "No net tension (0.6D >= 1.0L); compression covered by downward", "", "", "", "", "", "", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "65.89 lb/in\ncompression side", "4.897 lb/in", "66.07 lb/in", "90.00°\n1.500", "Weld 5,568 lb/in\nBase 8,700 lb/in", "0.01", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "81.52 lb/in\ncompression side", "7.346 lb/in", "81.85 lb/in", "90.00°\n1.500", "Weld 5,568 lb/in\nBase 8,700 lb/in", "0.01", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$D = "26.00 in"$], "Pipe26STD: outside diameter; the weld ring is the post perimeter", "AISC Shapes Database v16.0")
#calcline([$w = "0.2500 in"$], "Fillet weld leg size, all around (1/4 as entered)", "Input")
#calcline([$display(L_w = pi D = pi ("26.00 in") = "81.68 in")$], "Weld length: the post perimeter", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(S_w = frac(pi D^("2"), "4") = frac(pi ("26.00 in")^("2"), "4") = "530.9 in"^2)$], "Section modulus of the ring as a line", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.2500 in") = "0.1767 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Moment arm")
#calcline([$L_"post" = "41.50 in"$], "Moment arm, h - t_p: guard load at the top rail centerline, weld at the top of the baseplate", "Loading")
#subhead("Fillet size limits")
#calcline([$t_"post,nom" = "0.3750 in"$], "Post nominal wall thickness, Pipe26STD", "AISC Shapes Database v16.0")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(t_"min" = "min"(t_"post,nom", t_p) = "min"(("0.3750 in"), ("0.5000 in")) = "0.3750 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w_"min" = "0.1875 in"$], "Minimum fillet size for the thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w = "0.2500 in" >= w_"min" = "0.1875 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"OK"*], "Minimum size", "AISC 360-22 Table J2.4")
#calcline([$"Maximum fillet size"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not applicable"*], "Maximum fillet size along edges of material does not apply: this weld is a T-joint, not a weld along an edge. No maximum size is checked.", "AISC 360-22 §J2.2b(b); Engineering judgement (EOR): no maximum fillet size at a T-joint")
#subhead("Weld metal")
#calcline([$F_"EXX" = "70.00 ksi"$], "Electrode classification strength, E70XX", "AISC 360-22 §J2.6; AWS A5.1")
#calcline([$display(F_"nw" = "0.6" F_"EXX" = "0.6" ("70.00 ksi") = "42.00 ksi")$], "Nominal stress of the weld metal", "AISC 360-22 Table J2.5")
#calcline([$Omega_w = "2.000"$], "Safety factor, fillet weld (ASD)", "AISC 360-22 Table J2.5")
#subhead("Base metal: baseplate fusion face")
#calcline([$F_u = "58.00 ksi"$], "Tensile strength, baseplate A36", "AISC Manual Table 2-5")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(R_(n,"BM") = "0.6" F_u t_p = "0.6" ("58.00 ksi") ("0.5000 in") = "17,400 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM"), Omega_"BM") = frac(("17,400 lb/in"), "2.000") = "8,700 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$"Post wall at the weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Covered by Check 5"*], "Post wall at the weld: covered by Check 5. The wall carries the weld force as stress along the post axis, the same demand as Check 5 at its critical section; member shear is not checked (stated assumption).", "Engineering judgement (EOR): post wall at the weld covered by Check 5")
#subhead("Demand: outward, distributed load")
#calcline([$P_D = "2,828 lb"$], "D at the post: axial dead load at the top of the baseplate", "Loading")
#calcline([$display(P = "1.0" P_D = "1.0" ("2,828 lb") = "2,828 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "144.0 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("144.0 in") = "600.0 lb")$], "Uniform guard load collected over the span, horizontal (outward), at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("600.0 lb") = "600.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V L_"post" = ("600.0 lb") ("41.50 in") = "24,900 lb-in")$], "Moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(f_a = frac(P, L_w) = frac(("2,828 lb"), ("81.68 in")) = "34.62 lb/in")$], "Axial force per inch of weld, compression, uniform around the ring", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_w) = frac(("24,900 lb-in"), ("530.9 in"^2)) = "46.90 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("34.62 lb/in") + ("46.90 lb/in") = "81.52 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("34.62 lb/in") - ("46.90 lb/in")) = "12.27 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "81.52 lb/in" >= f_(n,"t") = "12.27 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "81.52 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, L_w) = frac(("600.0 lb"), ("81.68 in")) = "7.346 lb/in")$], "Shear per inch of weld, taken as uniform around the ring", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("81.52 lb/in")^("2") + ("7.346 lb/in")^("2")) = "81.85 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$f_parallel = "0 lb/in"$], "Force component along the weld axis: at the extreme fiber the weld axis is perpendicular to the plane of bending, and V acts in that plane", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(theta = arccos(frac(f_parallel, f_r)) = arccos(frac(("0 lb/in"), ("81.85 lb/in"))) = "90.00°")$], "Angle between the resultant and the weld axis", "AISC 360-22 Eq. J2-5; Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(k_"ds" = "1.0" + "0.5" sin(theta)^("1.5") = "1.0" + "0.5" dot sin("90.00°")^("1.5") = "1.500")$], "Directional strength increase", "AISC 360-22 Eq. J2-5; Engineering judgement (EOR), after STI: directional increase on round HSS")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.1767 in") dot "1.500" = "11,140 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 §J2.4")
#calcline([$display(frac(R_n, Omega_w) = frac(("11,140 lb/in"), "2.000") = "5,568 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("81.85 lb/in"), ("5,568 lb/in")) = "0.01")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_r, frac(R_(n,"BM"), Omega_"BM")) = frac(("81.85 lb/in"), ("8,700 lb/in")) = "0.01")$], "Baseplate fusion face: the resultant per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.01470", "0.009409") = "0.01")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.01 <= 1.00$ #h(10pt) #"OK"])

= Summary

#table(columns: (1fr, auto, auto, auto, auto, auto), table.header(strong("Check"), strong("Demand"), strong("Capacity"), strong("Ratio"), strong("Controlling direction"), strong("Result")), "1. Top rail bending", "36,650 lb-in", "4,602,000 lb-in", "0.01", "Downward, concentrated", "OK", "2. Top rail deflection", "0.001084 in", "1.200 in", "0.00", "Downward, concentrated", "OK", "3. Top rail weld to post", "30.71 lb/in", "1,856 lb/in (weld metal)", "0.02", "Outward, distributed", "NG (below minimum size)", "4a. Intermediate rail", "202,200 lb-in", "4,602,000 lb-in", "0.04", "Downward, bending", "OK", "4b. Intermediate rail weld to post", "68.78 lb/in", "1,856 lb/in (weld metal)", "0.04", "Downward, component", "NG (below minimum size)", "5. Post combined axial and flexure", "Pr = 2,828 lb; Mr = 24,900 lb-in", "Pc = 588,200 lb; Mc = 4,602,000 lb-in", "0.01", "Outward, distributed", "OK", "6. Post deflection", "0.0002125 in", "0.6917 in", "0.00", "Outward, distributed", "OK", "7. Post weld to baseplate", "81.85 lb/in", "5,568 lb/in (weld metal)", "0.01", "Outward, distributed", "OK")

= Anchor reactions

LRFD reactions at the top of concrete, for direct input into anchor software: reporting, not a pass/fail check. Each set is simultaneous: the shear, axial force and moment that occur together.

#text(weight: "bold", "Baseplate: B = 30.00 in (parallel to rail) × N = 30.00 in (perpendicular to rail)")

#subhead("Dead load at the base")
#calcline([$D_"rail" = "1,236 lb"$], "Top rail", "Loading")
#calcline([$D_"int" = "1,236 lb"$], "Intermediate rail", "Loading")
#calcline([$D_"post" = "356.2 lb"$], "Post, over h - t_p", "Loading")
#calcline([$rho = "0.2836 lb/in"^3$], "Steel unit weight", "AISC Manual 16th Ed., Part 17")
#calcline([$B = "30.00 in"$], "Baseplate, parallel to the rail", "Input")
#calcline([$N = "30.00 in"$], "Baseplate, perpendicular to the rail", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(W_"bp" = rho B N t_p = ("0.2836 lb/in"^3) ("30.00 in") ("30.00 in") ("0.5000 in") = "127.6 lb")$], "Baseplate weight: in the reaction sets only, below the critical section of Checks 5 and 7", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$display(D = D_"rail" + D_"int" + D_"post" + W_"bp" = ("1,236 lb") + ("1,236 lb") + ("356.2 lb") + ("127.6 lb") = "2,956 lb")$], "Dead load at the base", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#subhead("Governing guard load type")
#calcline([$P = "400.0 lb"$], "Concentrated guard load P, at the top of the post", "Loading")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "144.0 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(w_L L = ("4.167 lb/in") ("144.0 in") = "600.0 lb")$], "Uniform guard load collected over the span, at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$w_L L = "600.0 lb" > P = "400.0 lb"$ #h(6pt) $arrow.r$ #h(6pt) *#"Distributed load governs"*], "The larger at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Lateral set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "960.0 lb", "−2,660 lb (compression)", "40,320 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D axial, 1.6L horizontal; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "1,236 lb", "D, intermediate rail", "1,236 lb", "D, post", "356.2 lb", "D, baseplate", "127.6 lb", strong("D, total"), strong("2,956 lb"))

#"V and M act in the same vertical plane; M = V·h."

#"Lateral set applies in any horizontal direction; enter it in the anchor software in the orientation that governs the anchor pattern. Loads can reverse."

#subhead("Demand: lateral, distributed load")
#calcline([$D = "2,956 lb"$], "Dead load at the base", "Reactions")
#calcline([$display(abs(N_u) = "0.9" D = "0.9" ("2,956 lb") = "2,660 lb")$], "Axial force at the base: dead load, compression", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "144.0 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("144.0 in") = "600.0 lb")$], "Uniform guard load collected over the span, horizontal at the top of the post, in any horizontal direction", "Stated assumption: the tributary length is the span")
#calcline([$display(V_u = "1.6" V_L = "1.6" ("600.0 lb") = "960.0 lb")$], "Base shear", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$h = "42.00 in"$], "Moment arm: top rail centerline to top of concrete", "Input")
#calcline([$display(M_u = V_u h = ("960.0 lb") ("42.00 in") = "40,320 lb-in")$], "Base moment at the top of concrete: V_u at the top rail centerline, arm h", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Upward set

#"No net uplift (0.9D >= 1.6L): no upward set."

#subhead("Demand: upward, distributed load")
#calcline([$D = "2,956 lb"$], "Dead load at the base", "Reactions")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "144.0 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(P_L = w_L L = ("4.167 lb/in") ("144.0 in") = "600.0 lb")$], "Uniform guard load collected over the span, upward at the top of the post", "Stated assumption: the tributary length is the span")
