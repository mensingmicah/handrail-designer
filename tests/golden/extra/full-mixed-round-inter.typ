
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
+ #"At a post to baseplate weld on one pair of faces, the post wall is checked for the weld force along the post axis and for the force along the face separately; the two are not combined, the force along the face being small next to the other."
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

#table(columns: (auto, 1fr, auto), table.header(strong("Entry"), strong("Citation"), strong("Source")), "aisc360.K.round_chord.D_over_t_max", "AISC 360-22 Tables K3.1A and K4.1A", "AISC 360-22 text, read 2026-10-10", "material.A53_GrB.Fu", "AISC Manual Table 2-4", "memory", "aisc360.K1.3.Fy_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "aisc360.K1.3.Fy_Fu_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "material.A500_GrB.hss_rect.Fy", "AISC Manual Table 2-4", "memory", "material.A500_GrB.hss_rect.Fu", "AISC Manual Table 2-4", "memory", "ej.weld.post_wall.fu_fy_min", "Engineering judgement (EOR): post wall at the weld covered by Check 5 while Fu/Fy >= 1.20", "engineer", "asce7.guard.component", "ASCE 7-22 §4.5.1.2", "memory", "ej.post.axial_dead_load", "Engineering judgement (EOR): post dead load", "engineer", "ej.section.orientation.square", "Engineering judgement (EOR): a rectangular member's axes follow from its long side", "engineer", "material.grades.hss_rect", "AISC Manual Table 2-4", "memory", "ej.weld.line.corner_radius_coeff", "Engineering judgement (EOR): weld line on the true rounded rectangle", "engineer", "ej.weld.line.rounded_rectangle", "Engineering judgement (EOR): weld line on the true rounded rectangle", "engineer", "aisc360.J2.2a.throat.coeff", "AISC 360-22 §J2.2a", "memory", "aisc360.J2.2a.throat", "AISC 360-22 §J2.2a", "memory", "ej.weld.line.outline_model", "Engineering judgement (EOR): weld on the branch's outline where a round and a rectangular member meet", "engineer", "aisc360.J2.4.min_size", "AISC 360-22 Table J2.4", "memory", "ej.weld.max_size_not_applicable", "Engineering judgement (EOR): no maximum fillet size at a T-joint", "engineer", "aisc360.J2.2b.max_size_edges", "AISC 360-22 §J2.2b(b)", "memory", "material.E70XX.FEXX", "AISC 360-22 §J2.6; AWS A5.1", "memory", "aisc360.J2.5.fnw.coeff", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.fnw", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.omega_w", "AISC 360-22 Table J2.5", "memory", "ej.weld.branch_kds", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld", "engineer", "aisc360.eq.J4-4.coeff", "AISC 360-22 Eq. J4-4", "memory", "aisc360.eq.J4-4", "AISC 360-22 Eq. J4-4", "memory", "aisc_manual.part9.base_metal", "AISC Manual Part 9, base metal at welds", "memory", "aisc360.J4.2.omega_rupture", "AISC 360-22 §J4.2(b)", "memory", "ej.weld.chord_wall.mixed", "Engineering judgement (EOR): chord wall not checked where a round and a rectangular member meet", "engineer", "ej.weld.post_wall_covered", "Engineering judgement (EOR): post wall at the weld covered by Check 5", "engineer", "aws.d1_1.thickness_min", "AWS D1.1/D1.1M:2020, Clause 1", "memory", "ej.weld.line_method", "Engineering judgement (EOR): elastic weld as a line", "engineer", "ej.weld.no_bearing", "Engineering judgement (EOR): no bearing credit at the weld", "engineer", "aisc360.J2.4.fillet_strength", "AISC 360-22 Eq. J2-4", "memory", "ej.component.downward", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "engineer", "ej.component.midspan", "Engineering judgement (EOR): component load as a point load at midspan", "engineer", "ej.weld.intermediate_simple_shear", "Engineering judgement (EOR): intermediate rail to post weld as a simple shear connection", "engineer", "ej.weld.intermediate_ring_model", "Engineering judgement (EOR): weld ring at the post face, simple shear, P_c at the post", "engineer", "ej.weld.intermediate_base_metal", "Engineering judgement (EOR): Check 4b base metal on both walls, lower governs", "engineer", "ej.weld.check4b.no_chord_demand", "Engineering judgement (EOR): no chord limit state demand at the intermediate rail", "engineer", "aisc_manual.t3-23.case1.R", "AISC Manual Table 3-23, Case 1", "memory", "aisc360.B4.1a.rect_hss.lambda_r", "AISC 360-22 Table B4.1a, Case 6", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1a.classification", "AISC 360-22 §B4.1a", "memory", "aisc360.CA7.K_fixed_free", "AISC 360-22 Comm. Table C-A-7.1, case (e)", "memory", "aisc360.E2.effective_length", "AISC 360-22 §E2", "memory", "ej.post.unbraced_length", "Engineering judgement (EOR): unbraced length is the post height", "engineer", "aisc360.eq.E3-4", "AISC 360-22 Eq. E3-4", "memory", "aisc360.E2.user_note.slenderness", "AISC 360-22 §E2, User Note", "memory", "aisc360.E2.user_note.slenderness.limit", "AISC 360-22 §E2, User Note", "memory", "aisc360.E3.branch_limit", "AISC 360-22 §E3(a), (b)", "memory", "aisc360.eq.E3-2", "AISC 360-22 Eq. E3-2", "memory", "aisc360.eq.E3-2.base", "AISC 360-22 Eq. E3-2", "memory", "aisc360.eq.E3-1", "AISC 360-22 Eq. E3-1", "memory", "aisc360.E1.omega_c", "AISC 360-22 §E1", "memory", "aisc360.B4.1b.rect_hss.flange.lambda_p", "AISC 360-22 Table B4.1b, Case 17", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.flange.lambda_r", "AISC 360-22 Table B4.1b, Case 17", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.web.lambda_p", "AISC 360-22 Table B4.1b, Case 19", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.web.lambda_r", "AISC 360-22 Table B4.1b, Case 19", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-1", "AISC 360-22 Eq. F7-1", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.compact_no_local_buckling", "AISC 360-22 §F7.2(a), §F7.3(a)", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.4.no_ltb_note", "AISC 360-22 §F7.4, User Note", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.nominal_strength", "AISC 360-22 §F7", "AISC 360-22 text, read 2026-10-11", "aisc_manual.t3-23.case22.M", "AISC Manual Table 3-23, Case 22", "memory", "aisc360.eq.A-8-5", "AISC 360-22 Eq. A-8-5", "memory", "ej.second_order.pe_length", "Engineering judgement (EOR): Pe at Lc = 2.1h", "engineer", "aisc360.app8.alpha_asd", "AISC 360-22 App. 8", "memory", "ej.second_order.limit", "Engineering judgement (EOR): second-order limit", "engineer", "ej.second_order.negligible", "Engineering judgement (EOR): second-order limit", "engineer", "aisc360.H1.1.threshold", "AISC 360-22 §H1.1", "memory", "aisc360.eq.H1-1b", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.H1-1b.coeff", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.D2-1", "AISC 360-22 Eq. D2-1", "memory", "aisc360.D2.omega_t", "AISC 360-22 §D2(a)", "memory", "aisc_manual.t3-23.case22.delta", "AISC Manual Table 3-23, Case 22", "memory", "ej.deflection.limit.post", "Engineering judgement (EOR): post deflection limit, not code", "engineer", "ej.weld.line.face_pair", "Engineering judgement (EOR): weld line on a pair of faces, flats only", "engineer", "aisc360.J2.4.kds_rect_hss", "AISC 360-22 §J2.4(a)(2)", "AISC 360-22 text, read 2026-10-11", "aisc360.K5.user_note.rect_hss_kds", "AISC 360-22 §K5, User Note", "AISC 360-22 text, read 2026-10-11", "material.A36.Fu", "AISC Manual Table 2-5", "memory", "ej.weld.post_wall.face_pair", "Engineering judgement (EOR): post wall at a face-pair base weld checked on its own lines", "engineer", "aisc360.eq.J4-1", "AISC 360-22 Eq. J4-1", "AISC 360-22 text, read 2026-10-11", "aisc360.J4.1.omega_yield", "AISC 360-22 §J4.1(a)", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.J4-2", "AISC 360-22 Eq. J4-2", "AISC 360-22 text, read 2026-10-11", "aisc360.J4.1.omega_rupture", "AISC 360-22 §J4.1(b)", "AISC 360-22 text, read 2026-10-11", "material.steel.density", "AISC Manual 16th Ed., Part 17", "memory", "ej.reaction.location", "Engineering judgement (EOR): reactions at the top of concrete, arm h", "engineer", "ej.combo.reaction", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "engineer", "ej.reaction.lateral_note", "Engineering judgement (EOR): one lateral set, any horizontal direction", "engineer")

= Dimensions

Every dimension as entered, and as the tool read it. A bare number is inches.

#table(columns: (1fr, auto, auto, auto), table.header(strong("Dimension"), strong("As entered"), strong("Read as"), strong("Inches")), "Span, post to post (c/c)", "6'-0\"", "6'-0\"", "72.00 in", "Post height h, top of concrete to top rail centerline", "42", "3'-6\"", "42.00 in", "Baseplate thickness t_p", "1/2", "1/2\"", "0.5000 in", "Baseplate B, parallel to the rail", "6", "6\"", "6.000 in", "Baseplate N, perpendicular to the rail", "8", "8\"", "8.000 in", "Fillet weld, top rail to post", "1/8", "1/8\"", "0.1250 in", "Fillet weld, post to baseplate", "3/16", "3/16\"", "0.1875 in", "Fillet weld, intermediate rail to post", "1/8", "1/8\"", "0.1250 in")

#text("Directional strength increase at the post to baseplate weld: not elected (directional_increase = false).")

#text("Post to baseplate weld pattern: faces perpendicular to rail (base_pattern).")

Derived lengths, each computed in the calc where it is used:

#table(columns: (1fr, auto, auto, auto), table.header(strong("Derived length"), strong("Formula"), strong("Inches"), strong("Computed in")), "Post cantilever length, top of baseplate to top rail centerline", [$L_"post" = h - t_p$], "41.50 in", "Loading", "Eccentricity: rail centerline to the weld plane at the rail underside", [$e = frac(d_"rail", "2")$], "1.188 in", "Check 3", "Effective length, with the unbraced length taken as the post height h", [$L_c = K h$], "88.20 in", "Check 5")

= Section properties

#text("Top rail: Pipe2STD, A53 Gr B (default).") Properties are used exactly as published in the AISC Shapes Database v16.0.

#calcline([$D = "2.375 in"$], "Pipe2STD: outside diameter", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.1540 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1430 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "1.020 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "0.3050 lb/in"$], "Nominal weight: tabulated 3.66 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I = "0.6270 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$S = "0.5280 in"^3$], "Elastic section modulus", "AISC Shapes Database v16.0")
#calcline([$Z = "0.7130 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$D slash t = "16.60"$], "Diameter-to-thickness ratio, tabulated", "AISC Shapes Database v16.0")

#text("Post: HSS2X2X1/8, A500 Gr B (default).")

#calcline([$H = "2.000 in"$], "HSS2X2X1/8: outside dimension of the longer side", "AISC Shapes Database v16.0")
#calcline([$B = "2.000 in"$], "Outside dimension of the shorter side", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.1250 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1160 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "0.8400 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "0.2542 lb/in"$], "Nominal weight: tabulated 3.05 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I_x = "0.4860 in"^4$], "Moment of inertia about the x axis", "AISC Shapes Database v16.0")
#calcline([$S_x = "0.4860 in"^3$], "Elastic section modulus about the x axis", "AISC Shapes Database v16.0")
#calcline([$Z_x = "0.5840 in"^3$], "Plastic section modulus about the x axis", "AISC Shapes Database v16.0")
#calcline([$r_x = "0.7610 in"$], "Radius of gyration about the x axis", "AISC Shapes Database v16.0")
#calcline([$I_y = "0.4860 in"^4$], "Moment of inertia about the y axis", "AISC Shapes Database v16.0")
#calcline([$S_y = "0.4860 in"^3$], "Elastic section modulus about the y axis", "AISC Shapes Database v16.0")
#calcline([$Z_y = "0.5840 in"^3$], "Plastic section modulus about the y axis", "AISC Shapes Database v16.0")
#calcline([$r_y = "0.7610 in"$], "Radius of gyration about the y axis", "AISC Shapes Database v16.0")
#calcline([$J = "0.7960 in"^4$], "Torsional constant", "AISC Shapes Database v16.0")
#calcline([$b slash t = "14.20"$], "Width-to-thickness ratio of the shorter walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$h slash t = "14.20"$], "Width-to-thickness ratio of the longer walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$"Square section"$ #h(6pt) $arrow.r$ #h(6pt) *#"Square section: both axes have the same properties, and no orientation is entered. The calc names the axis a vertical load bends (for a post, a load across the guard) x, and the other y."*], "Orientation, and the axis each load bends", "Engineering judgement (EOR): a rectangular member's axes follow from its long side")

#text("Intermediate rail: Pipe1-1/4STD, A53 Gr B (default).")

#calcline([$D = "1.660 in"$], "Pipe1-1/4STD: outside diameter", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.1400 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1300 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "0.6250 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "0.1892 lb/in"$], "Nominal weight: tabulated 2.27 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I = "0.1840 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$S = "0.2220 in"^3$], "Elastic section modulus", "AISC Shapes Database v16.0")
#calcline([$Z = "0.3050 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$D slash t = "12.80"$], "Diameter-to-thickness ratio, tabulated", "AISC Shapes Database v16.0")

#text("Baseplate: A36. Welds: fillet, electrode E70XX; all around at the rails, and at the baseplate on the faces perpendicular to rail.")

= Loading

Guard loads per ASCE 7-22. The concentrated and uniform loads are separate load types and do not act concurrently. Each check applies them in every direction case and reports the controlling one.

#calcline([$P = "200.0 lb"$], "Concentrated guard load, any direction, any point on the top rail", "ASCE 7-22 §4.5.1")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load, 50 lb/ft, any direction; not concurrent with P", "ASCE 7-22 §4.5.1.1")
#calcline([$P_c = "50.00 lb"$], "Component load on the intermediate rail, horizontal; also applied downward (engineering judgement)", "ASCE 7-22 §4.5.1.2")
#calcline([$w_D = "0.3050 lb/in"$], "Top rail self-weight: tabulated W = 3.66 lb/ft", "AISC Shapes Database v16.0")
#subhead("Dead load at the post")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(L_"post" = h - t_p = ("42.00 in") - ("0.5000 in") = "41.50 in")$], "Post cantilever length, top of baseplate to top rail centerline", "Stated assumption: post fixed at the top of the baseplate")
#calcline([$W_"post" = "0.2542 lb/in"$], "Post self-weight: HSS2X2X1/8, tabulated W = 3.05 lb/ft", "AISC Shapes Database v16.0")
#calcline([$display(D_"post" = W_"post" L_"post" = ("0.2542 lb/in") ("41.50 in") = "10.55 lb")$], "Post dead load, full weight at the base", "Engineering judgement (EOR): post dead load")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post (stated assumption)", "Input")
#calcline([$display(D_"rail" = w_D L = ("0.3050 lb/in") ("72.00 in") = "21.96 lb")$], "Top rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$w_(D,"int") = "0.1892 lb/in"$], "Intermediate rail self-weight: Pipe1-1/4STD, tabulated W = 2.27 lb/ft", "AISC Shapes Database v16.0")
#calcline([$display(D_"int" = w_(D,"int") L = ("0.1892 lb/in") ("72.00 in") = "13.62 lb")$], "Intermediate rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$display(P_D = D_"rail" + D_"int" + D_"post" = ("21.96 lb") + ("13.62 lb") + ("10.55 lb") = "46.13 lb")$], "D at the post: axial dead load at the top of the baseplate", "Engineering judgement (EOR): post dead load")

= Check 1: Top rail bending

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $M_a$], [*Capacity* $M_n / Omega_b$], [*Ratio*], []), strong("Downward"), strong("Concentrated"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2"), strong("3,798 lb-in"), strong("14,940 lb-in"), strong("0.25"), strong("Controls"), "Downward", "Distributed", "1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2", "2,898 lb-in", "14,940 lb-in", "0.19", "", "Outward", "Concentrated", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "3,605 lb-in", "14,940 lb-in", "0.24", "", "Outward", "Distributed", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "2,707 lb-in", "14,940 lb-in", "0.18", "", "Inward", "Concentrated", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "3,605 lb-in", "14,940 lb-in", "0.24", "", "Inward", "Distributed", "1.0D vertical, 1.0L horizontal, SRSS\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): SRSS, round section", "2,707 lb-in", "14,940 lb-in", "0.18", "", "Upward", "Concentrated", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "3,481 lb-in", "14,940 lb-in", "0.23", "", "Upward", "Distributed", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "2,581 lb-in", "14,940 lb-in", "0.17", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Downward, concentrated (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Capacity")
#calcline([$"Pipe2STD, A53 Gr B"$ #h(6pt) $arrow.r$ #h(6pt) *#"Designed as round HSS"*], "Pipe is designed under the round HSS provisions", "AISC Manual Table 2-4")
#calcline([$F_y = "35.00 ksi"$], "Yield stress, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$lambda = "16.60"$], "lambda = D/t, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$display(lambda_"lim" = frac("0.45" E, F_y) = frac("0.45" ("29,000 ksi"), ("35.00 ksi")) = "372.9")$], "Applicability limit on D/t", "AISC 360-22 §F8")
#calcline([$display(lambda_p = frac("0.07" E, F_y) = frac("0.07" ("29,000 ksi"), ("35.00 ksi")) = "58.00")$], "Compact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$display(lambda_r = frac("0.31" E, F_y) = frac("0.31" ("29,000 ksi"), ("35.00 ksi")) = "256.9")$], "Noncompact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$lambda = 16.6 < lambda_"lim" = 372.9$ #h(6pt) $arrow.r$ #h(6pt) *#"Applies"*], "Applicability", "AISC 360-22 §F8")
#calcline([$"Round HSS"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "Limit states: yielding and local buckling only; Lb and Cb do not enter", "AISC 360-22 §F8")
#calcline([$Z = "0.7130 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$display(M_p = F_y Z = ("35.00 ksi") ("0.7130 in"^3) = "24,960 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F8-1")
#calcline([$lambda = 16.6 <= lambda_p = 58.00$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact"*], "Section classification", "AISC 360-22 §B4.1b")
#calcline([$"Compact wall"$ #h(6pt) $arrow.r$ #h(6pt) *#"Local buckling does not apply"*], "", "AISC 360-22 §F8")
#calcline([$display(M_n = M_p = "24,960 lb-in")$], "Nominal flexural strength", "AISC 360-22 §F8")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$display(frac(M_n, Omega_b) = frac(("24,960 lb-in"), "1.670") = "14,940 lb-in")$], "Allowable flexural strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: downward, concentrated load")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$w_D = "0.3050 lb/in"$], "Top rail self-weight", "Loading")
#calcline([$display(M_D = frac(w_D L^("2"), "8") = frac(("0.3050 lb/in") ("72.00 in")^("2"), "8") = "197.6 lb-in")$], "Dead-load moment, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$P = "200.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(M_L = frac(P L, "4") = frac(("200.0 lb") ("72.00 in"), "4") = "3,600 lb-in")$], "Live-load moment, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$display(M_a = "1.0" M_D + "1.0" M_L = "1.0" ("197.6 lb-in") + "1.0" ("3,600 lb-in") = "3,798 lb-in")$], "Required flexural strength: D and L on the same axis", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display("Ratio" = frac(M_a, frac(M_n, Omega_b)) = frac(("3,798 lb-in"), ("14,940 lb-in")) = "0.25")$], "Demand / capacity", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.25 <= 1.00$ #h(10pt) #"OK"])

= Check 2: Top rail deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), strong("Downward"), strong("Concentrated"), strong("1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability"), strong("0.09140 in"), strong("0.6000 in"), strong("0.15"), strong("Controls"), "Downward", "Distributed", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.08605 in", "0.6000 in", "0.14", "", "Outward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.08553 in", "0.6000 in", "0.14", "", "Outward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.08018 in", "0.6000 in", "0.13", "", "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.08553 in", "0.6000 in", "0.14", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.08018 in", "0.6000 in", "0.13", "", "Upward", "Concentrated", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.08553 in", "0.6000 in", "0.14", "", "Upward", "Distributed", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.08018 in", "0.6000 in", "0.13", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Downward, concentrated (1.0D + 1.0L, vertical; Engineering judgement (EOR): serviceability)")

#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I = "0.6270 in"^4$], "Moment of inertia", "AISC Shapes Database v16.0")
#calcline([$P = "200.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(Delta_L = frac(P L^("3"), "48" E I) = frac(("200.0 lb") ("72.00 in")^("3"), "48" ("29,000 ksi") ("0.6270 in"^4)) = "0.08553 in")$], "Live-load deflection, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$w_D = "0.3050 lb/in"$], "Top rail self-weight", "Loading")
#calcline([$display(Delta_D = frac("5" w_D L^("4"), "384" E I) = frac("5" ("0.3050 lb/in") ("72.00 in")^("4"), "384" ("29,000 ksi") ("0.6270 in"^4)) = "0.005870 in")$], "Dead-load deflection, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$display(Delta = "1.0" Delta_D + "1.0" Delta_L = "1.0" ("0.005870 in") + "1.0" ("0.08553 in") = "0.09140 in")$], "D and L on the same (vertical) axis", "Engineering judgement (EOR): serviceability")
#calcline([$display(Delta_"allow" = frac(L, "120") = frac(("72.00 in"), "120") = "0.6000 in")$], "Limit L/120", "Engineering judgement (EOR): deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.09140 in"), ("0.6000 in")) = "0.15")$], "Deflection / limit", "Engineering judgement (EOR): deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.15 <= 1.00$ #h(10pt) #"OK"])

= Check 3: Top rail weld to post

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "29.20 lb/in\nuniform", "—", "29.20 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "42.35 lb/in\nuniform", "—", "42.35 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "51.30 lb/in\ncompression side", "26.31 lb/in", "57.66 lb/in", "Weld 1,856 lb/in\nBase 2,574 lb/in", "0.03", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("75.51 lb/in\ncompression side"), strong("39.46 lb/in"), strong("85.20 lb/in"), strong("Weld 1,856 lb/in\nBase 2,574 lb/in"), strong("0.05"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "51.30 lb/in\ncompression side", "26.31 lb/in", "57.66 lb/in", "Weld 1,856 lb/in\nBase 2,574 lb/in", "0.03", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "75.51 lb/in\ncompression side", "39.46 lb/in", "85.20 lb/in", "Weld 1,856 lb/in\nBase 2,574 lb/in", "0.05", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "24.58 lb/in\nuniform", "—", "24.58 lb/in", "Weld 1,856 lb/in\nBase —", "0.01", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "37.73 lb/in\nuniform", "—", "37.73 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "51.30 lb/in\ncompression side", "26.31 lb/in", "57.66 lb/in", "Weld 1,856 lb/in\nBase 2,574 lb/in", "0.03", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "75.51 lb/in\ncompression side", "39.46 lb/in", "85.20 lb/in", "Weld 1,856 lb/in\nBase 2,574 lb/in", "0.05", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$a_"par" = "2.000 in"$], "HSS2X2X1/8: outside dimension parallel to the rail; the weld line is the post outline", "AISC Shapes Database v16.0")
#calcline([$a_"perp" = "2.000 in"$], "Outside dimension perpendicular to the rail", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1160 in"$], "Design wall thickness, HSS2X2X1/8: it sets the outside corner radius", "AISC Shapes Database v16.0")
#calcline([$display(R_o = "2" t_"des" = "2" ("0.1160 in") = "0.2320 in")$], "Outside corner radius", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(L_w = "2" (a_"par" - "2" R_o) + "2" (a_"perp" - "2" R_o) + "2" pi R_o = "2" (("2.000 in") - "2" ("0.2320 in")) + "2" (("2.000 in") - "2" ("0.2320 in")) + "2" dot pi ("0.2320 in") = "7.602 in")$], "Weld length: the post outline, four flats and four corner arcs", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(y_("c,t") = frac(a_"perp", "2") - R_o = frac(("2.000 in"), "2") - ("0.2320 in") = "0.7680 in")$], "Distance from the axis to the corner arc centers, a load across the guard", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(I_("w,t") = "2" (a_"par" - "2" R_o) (frac(a_"perp", "2"))^("2") + frac((a_"perp" - "2" R_o)^("3"), "6") + "2" pi R_o y_("c,t")^("2") + "8" y_("c,t") R_o^("2") + pi R_o^("3") = "2" (("2.000 in") - "2" ("0.2320 in")) (frac(("2.000 in"), "2"))^("2") + frac((("2.000 in") - "2" ("0.2320 in"))^("3"), "6") + "2" dot pi ("0.2320 in") ("0.7680 in")^("2") + "8" ("0.7680 in") ("0.2320 in")^("2") + pi ("0.2320 in")^("3") = "4.906 in"^3)$], "Moment of inertia of the weld line, a load across the guard: flats and corner arcs", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(S_("w,t") = frac(I_("w,t"), frac(a_"perp", "2")) = frac(("4.906 in"^3), frac(("2.000 in"), "2")) = "4.906 in"^2)$], "Section modulus of the weld line, a load across the guard", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(y_("c,l") = frac(a_"par", "2") - R_o = frac(("2.000 in"), "2") - ("0.2320 in") = "0.7680 in")$], "Distance from the axis to the corner arc centers, a load along the rail", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(I_("w,l") = "2" (a_"perp" - "2" R_o) (frac(a_"par", "2"))^("2") + frac((a_"par" - "2" R_o)^("3"), "6") + "2" pi R_o y_("c,l")^("2") + "8" y_("c,l") R_o^("2") + pi R_o^("3") = "2" (("2.000 in") - "2" ("0.2320 in")) (frac(("2.000 in"), "2"))^("2") + frac((("2.000 in") - "2" ("0.2320 in"))^("3"), "6") + "2" dot pi ("0.2320 in") ("0.7680 in")^("2") + "8" ("0.7680 in") ("0.2320 in")^("2") + pi ("0.2320 in")^("3") = "4.906 in"^3)$], "Moment of inertia of the weld line, a load along the rail: flats and corner arcs", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(S_("w,l") = frac(I_("w,l"), frac(a_"par", "2")) = frac(("4.906 in"^3), frac(("2.000 in"), "2")) = "4.906 in"^2)$], "Section modulus of the weld line, a load along the rail", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Eccentricity")
#calcline([$d_"rail" = "2.375 in"$], "Pipe2STD: outside diameter, the rail depth", "AISC Shapes Database v16.0")
#calcline([$display(e = frac(d_"rail", "2") = frac(("2.375 in"), "2") = "1.188 in")$], "Eccentricity: rail centerline to the weld plane at the rail underside", "Engineering judgement (EOR): weld on the branch's outline where a round and a rectangular member meet")
#subhead("Fillet size limits")
#calcline([$t_"rail,nom" = "0.1540 in"$], "Top rail nominal wall thickness, Pipe2STD", "AISC Shapes Database v16.0")
#calcline([$t_"post,nom" = "0.1250 in"$], "Post nominal wall thickness, HSS2X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(t_"min" = "min"(t_"rail,nom", t_"post,nom") = "min"(("0.1540 in"), ("0.1250 in")) = "0.1250 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w_"min" = "0.1250 in"$], "Minimum fillet size for the thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w = "0.1250 in" >= w_"min" = "0.1250 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"OK"*], "Minimum size", "AISC 360-22 Table J2.4")
#calcline([$"Maximum fillet size"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not applicable"*], "Maximum fillet size along edges of material does not apply: this weld is a T-joint, not a weld along an edge. No maximum size is checked.", "AISC 360-22 §J2.2b(b); Engineering judgement (EOR): no maximum fillet size at a T-joint")
#subhead("Weld metal")
#calcline([$F_"EXX" = "70.00 ksi"$], "Electrode classification strength, E70XX", "AISC 360-22 §J2.6; AWS A5.1")
#calcline([$display(F_"nw" = "0.6" F_"EXX" = "0.6" ("70.00 ksi") = "42.00 ksi")$], "Nominal stress of the weld metal", "AISC 360-22 Table J2.5")
#calcline([$Omega_w = "2.000"$], "Safety factor, fillet weld (ASD)", "AISC 360-22 Table J2.5")
#calcline([$k_"ds" = "1.000"$], "No directional increase at the rail to post weld (a branch-to-chord joint)", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld")
#subhead("Base metal: rail fusion face")
#calcline([$F_u = "60.00 ksi"$], "Tensile strength, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"rail" = "0.1430 in"$], "Top rail design wall thickness, Pipe2STD", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM") = "0.6" F_u t_"rail" = "0.6" ("60.00 ksi") ("0.1430 in") = "5,148 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM"), Omega_"BM") = frac(("5,148 lb/in"), "2.000") = "2,574 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$"Rail wall, normal force"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not checked"*], "Rail wall, force normal to the wall: AISC 360-22 has no chord limit states for a round member meeting a rectangular one; not checked (stated assumption). The rail is held to the Chapter K limits of applicability for its own wall.", "Engineering judgement (EOR): chord wall not checked where a round and a rectangular member meet")
#calcline([$"Post wall at the weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Covered by Check 5"*], "Post wall at the weld: covered by Check 5. The wall carries the weld force as stress along the post axis, the same demand as Check 5 at its critical section; member shear is not checked (stated assumption).", "Engineering judgement (EOR): post wall at the weld covered by Check 5")
#subhead("Demand: outward, distributed load")
#calcline([$D_"rail" = "21.96 lb"$], "Top rail dead load at the weld: w_D over the span (the tributary length)", "Loading")
#calcline([$display(P = "1.0" D_"rail" = "1.0" ("21.96 lb") = "21.96 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (outward), on the rail at the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("300.0 lb") = "300.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V e = ("300.0 lb") ("1.188 in") = "356.2 lb-in")$], "Moment at the weld plane: V at the rail centerline, arm e", "Engineering judgement (EOR): weld on the branch's outline where a round and a rectangular member meet")
#calcline([$display(f_a = frac(P, L_w) = frac(("21.96 lb"), ("7.602 in")) = "2.889 lb/in")$], "Axial force per inch of weld, compression, uniform along the weld line", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_("w,t")) = frac(("356.2 lb-in"), ("4.906 in"^2)) = "72.62 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("2.889 lb/in") + ("72.62 lb/in") = "75.51 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("2.889 lb/in") - ("72.62 lb/in")) = "69.73 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "75.51 lb/in" >= f_(n,"t") = "69.73 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "75.51 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, L_w) = frac(("300.0 lb"), ("7.602 in")) = "39.46 lb/in")$], "Shear per inch of weld, taken as uniform along the weld line", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("75.51 lb/in")^("2") + ("39.46 lb/in")^("2")) = "85.20 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("85.20 lb/in"), ("1,856 lb/in")) = "0.05")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM"), Omega_"BM")) = frac(("39.46 lb/in"), ("2,574 lb/in")) = "0.02")$], "Rail fusion face: in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.04591", "0.01533") = "0.05")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.05 <= 1.00$ #h(10pt) #"OK"])

= Check 4a: Intermediate rail

== Envelope summary

Each limit state is computed in both directions of the component load. The full calculation follows for the governing case of each limit state.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Limit state*], [*Direction*], [*Combination*], [*Demand* $M_a$ or $Delta$], [*Capacity* $M_n / Omega_b$ or $Delta_"allow"$], [*Ratio*], []), strong("Bending"), strong("Downward"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)"), strong("1,023 lb-in"), strong("6,392 lb-in"), strong("0.16"), strong("Controls"), "Bending", "Horizontal", "1.0L horizontal, alone\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "900.0 lb-in", "6,392 lb-in", "0.14", "", "Deflection", "Downward", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.08527 in", "0.6000 in", "0.14", "", "Deflection", "Horizontal", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.07286 in", "0.6000 in", "0.12", "")

#heading(level: 2, "Controlling case: Downward, bending (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5))")

#subhead("Capacity")
#calcline([$"Pipe1-1/4STD, A53 Gr B"$ #h(6pt) $arrow.r$ #h(6pt) *#"Designed as round HSS"*], "Pipe is designed under the round HSS provisions", "AISC Manual Table 2-4")
#calcline([$F_y = "35.00 ksi"$], "Yield stress, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$lambda = "12.80"$], "lambda = D/t, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$display(lambda_"lim" = frac("0.45" E, F_y) = frac("0.45" ("29,000 ksi"), ("35.00 ksi")) = "372.9")$], "Applicability limit on D/t", "AISC 360-22 §F8")
#calcline([$display(lambda_p = frac("0.07" E, F_y) = frac("0.07" ("29,000 ksi"), ("35.00 ksi")) = "58.00")$], "Compact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$display(lambda_r = frac("0.31" E, F_y) = frac("0.31" ("29,000 ksi"), ("35.00 ksi")) = "256.9")$], "Noncompact limit, round HSS in flexure", "AISC 360-22 Table B4.1b, Case 20")
#calcline([$lambda = 12.8 < lambda_"lim" = 372.9$ #h(6pt) $arrow.r$ #h(6pt) *#"Applies"*], "Applicability", "AISC 360-22 §F8")
#calcline([$"Round HSS"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "Limit states: yielding and local buckling only; Lb and Cb do not enter", "AISC 360-22 §F8")
#calcline([$Z = "0.3050 in"^3$], "Plastic section modulus", "AISC Shapes Database v16.0")
#calcline([$display(M_p = F_y Z = ("35.00 ksi") ("0.3050 in"^3) = "10,670 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F8-1")
#calcline([$lambda = 12.8 <= lambda_p = 58.00$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact"*], "Section classification", "AISC 360-22 §B4.1b")
#calcline([$"Compact wall"$ #h(6pt) $arrow.r$ #h(6pt) *#"Local buckling does not apply"*], "", "AISC 360-22 §F8")
#calcline([$display(M_n = M_p = "10,670 lb-in")$], "Nominal flexural strength", "AISC 360-22 §F8")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$display(frac(M_n, Omega_b) = frac(("10,670 lb-in"), "1.670") = "6,392 lb-in")$], "Allowable flexural strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: downward, component load")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$P_c = "50.00 lb"$], "Component load, a point load at midspan", "Loading")
#calcline([$display(M_L = frac(P_c L, "4") = frac(("50.00 lb") ("72.00 in"), "4") = "900.0 lb-in")$], "Component load moment, midspan", "AISC Manual Table 3-23, Case 7; Engineering judgement (EOR): component load as a point load at midspan")
#calcline([$w_(D,"int") = "0.1892 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$display(M_D = frac(w_(D,"int") L^("2"), "8") = frac(("0.1892 lb/in") ("72.00 in")^("2"), "8") = "122.6 lb-in")$], "Dead-load moment, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$display(M_a = "1.0" M_D + "1.0" M_L = "1.0" ("122.6 lb-in") + "1.0" ("900.0 lb-in") = "1,023 lb-in")$], "Required flexural strength: D and L on the same axis", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display("Ratio" = frac(M_a, frac(M_n, Omega_b)) = frac(("1,023 lb-in"), ("6,392 lb-in")) = "0.16")$], "Demand / capacity", "AISC 360-22 Eq. B3-2")

#heading(level: 2, "Governing deflection case: Downward, deflection (1.0D + 1.0L, vertical; Engineering judgement (EOR): serviceability)")

#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_"int" = "0.1840 in"^4$], "Moment of inertia, Pipe1-1/4STD", "AISC Shapes Database v16.0")
#calcline([$P_c = "50.00 lb"$], "Component load, a point load at midspan", "Loading")
#calcline([$display(Delta_L = frac(P_c L^("3"), "48" E I_"int") = frac(("50.00 lb") ("72.00 in")^("3"), "48" ("29,000 ksi") ("0.1840 in"^4)) = "0.07286 in")$], "Component load deflection, midspan", "AISC Manual Table 3-23, Case 7; Engineering judgement (EOR): component load as a point load at midspan")
#calcline([$w_(D,"int") = "0.1892 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$display(Delta_D = frac("5" w_(D,"int") L^("4"), "384" E I_"int") = frac("5" ("0.1892 lb/in") ("72.00 in")^("4"), "384" ("29,000 ksi") ("0.1840 in"^4)) = "0.01241 in")$], "Dead-load deflection, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$display(Delta = "1.0" Delta_D + "1.0" Delta_L = "1.0" ("0.01241 in") + "1.0" ("0.07286 in") = "0.08527 in")$], "D and L on the same (vertical) axis", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); Engineering judgement (EOR): serviceability")
#calcline([$display(Delta_"allow" = frac(L, "120") = frac(("72.00 in"), "120") = "0.6000 in")$], "Limit L/120", "Engineering judgement (EOR): deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.08527 in"), ("0.6000 in")) = "0.14")$], "Deflection / limit", "Engineering judgement (EOR): deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.16 <= 1.00$ #h(10pt) #"OK"])

= Check 4b: Intermediate rail weld to post

== Envelope summary

Both directions of the component load are computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), strong("Downward"), strong("Component"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)"), strong("—\nshear only"), strong("10.89 lb/in"), strong("10.89 lb/in"), strong("Weld 1,856 lb/in\nBase 2,018 lb/in"), strong("0.01"), strong("Controls"), "Horizontal", "Component", "1.0D vertical, 1.0L horizontal, vector sum\nASCE 7-22 §2.4.1, Comb. 2", "—\nshear only", "9.676 lb/in", "9.676 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.01", "")]

#heading(level: 2, "Controlling case: Downward, component (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5))")

#subhead("Weld properties")
#calcline([$D_"int" = "1.660 in"$], "Pipe1-1/4STD: outside diameter; the weld ring is the intermediate rail perimeter", "AISC Shapes Database v16.0")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(L_w = pi D_"int" = pi ("1.660 in") = "5.215 in")$], "Weld length: the intermediate rail perimeter", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Connection model")
#calcline([$"Intermediate rail to post weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Simple shear connection"*], "Simple shear connection consistent with the simple-span member assumption; no end moment at the weld.", "Engineering judgement (EOR): intermediate rail to post weld as a simple shear connection; Engineering judgement (EOR): weld ring at the post face, simple shear, P_c at the post")
#subhead("Fillet size limits")
#calcline([$t_"int,nom" = "0.1400 in"$], "Intermediate rail nominal wall thickness, Pipe1-1/4STD", "AISC Shapes Database v16.0")
#calcline([$t_"post,nom" = "0.1250 in"$], "Post nominal wall thickness, HSS2X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(t_"min" = "min"(t_"int,nom", t_"post,nom") = "min"(("0.1400 in"), ("0.1250 in")) = "0.1250 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w_"min" = "0.1250 in"$], "Minimum fillet size for the thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w = "0.1250 in" >= w_"min" = "0.1250 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"OK"*], "Minimum size", "AISC 360-22 Table J2.4")
#calcline([$"Maximum fillet size"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not applicable"*], "Maximum fillet size along edges of material does not apply: this weld is a T-joint, not a weld along an edge. No maximum size is checked.", "AISC 360-22 §J2.2b(b); Engineering judgement (EOR): no maximum fillet size at a T-joint")
#subhead("Weld metal")
#calcline([$F_"EXX" = "70.00 ksi"$], "Electrode classification strength, E70XX", "AISC 360-22 §J2.6; AWS A5.1")
#calcline([$display(F_"nw" = "0.6" F_"EXX" = "0.6" ("70.00 ksi") = "42.00 ksi")$], "Nominal stress of the weld metal", "AISC 360-22 Table J2.5")
#calcline([$Omega_w = "2.000"$], "Safety factor, fillet weld (ASD)", "AISC 360-22 Table J2.5")
#calcline([$k_"ds" = "1.000"$], "No directional increase at the intermediate rail to post weld (a branch-to-chord joint)", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld")
#subhead("Base metal: post wall fusion face (chord)")
#calcline([$F_u = "58.00 ksi"$], "Tensile strength, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"post" = "0.1160 in"$], "Post design wall thickness, HSS2X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM,post") = "0.6" F_u t_"post" = "0.6" ("58.00 ksi") ("0.1160 in") = "4,037 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM,post"), Omega_"BM") = frac(("4,037 lb/in"), "2.000") = "2,018 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#subhead("Base metal: intermediate rail wall fusion face (branch)")
#calcline([$F_u = "60.00 ksi"$], "Tensile strength, A53 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"int" = "0.1300 in"$], "Intermediate rail design wall thickness, Pipe1-1/4STD", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM,int") = "0.6" F_u t_"int" = "0.6" ("60.00 ksi") ("0.1300 in") = "4,680 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM,int"), Omega_"BM") = frac(("4,680 lb/in"), "2.000") = "2,340 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$frac(R_(n,"BM,int"), Omega_"BM") = "2,340 lb/in" > frac(R_(n,"BM,post"), Omega_"BM") = "2,018 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Post wall governs"*], "Base metal is checked at the fusion face of both connected parts, the post wall (the chord) and the intermediate rail wall (the branch), each in shear rupture against the in-plane shear per inch; the lower allowable governs.", "Engineering judgement (EOR): Check 4b base metal on both walls, lower governs")
#calcline([$"Post wall, chord limit states"$ #h(6pt) $arrow.r$ #h(6pt) *#"No demand"*], "Chapter K chord limit states: the intermediate rail delivers no axial force or moment to the post wall (simple shear connection); the post wall's in-plane shear is checked by the base metal line above.", "Engineering judgement (EOR): no chord limit state demand at the intermediate rail")
#subhead("Demand: downward, component load")
#calcline([$w_(D,"int") = "0.1892 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$display(R_D = frac(w_(D,"int") L, "2") = frac(("0.1892 lb/in") ("72.00 in"), "2") = "6.810 lb")$], "Dead-load end reaction at the post", "AISC Manual Table 3-23, Case 1")
#calcline([$P_c = "50.00 lb"$], "Component load adjacent to the post: the full P_c to this end", "Engineering judgement (EOR): weld ring at the post face, simple shear, P_c at the post")
#calcline([$display(R = "1.0" R_D + "1.0" P_c = "1.0" ("6.810 lb") + "1.0" ("50.00 lb") = "56.81 lb")$], "Weld reaction: dead and component loads in the same (vertical) direction, in the ring's plane", "Engineering judgement (EOR): weld ring at the post face, simple shear, P_c at the post; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(f_v = frac(R, L_w) = frac(("56.81 lb"), ("5.215 in")) = "10.89 lb/in")$], "Shear per inch of weld, taken as uniform around the ring", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = f_v = "10.89 lb/in")$], "Resultant per inch: shear only, no axial force and no moment", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("10.89 lb/in"), ("1,856 lb/in")) = "0.01")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM,post"), Omega_"BM")) = frac(("10.89 lb/in"), ("2,018 lb/in")) = "0.01")$], "Base metal, post wall fusion face (governs): in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.005870", "0.005397") = "0.01")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.01 <= 1.00$ #h(10pt) #"OK"])

= Check 5: Post combined axial and flexure

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Axial* $P_r$ \ capacity $P_c$ or $P_t$], [*Moment* $M_r$ \ capacity $M_c$], [*Equation*], [$frac(alpha P_r, P_e)$], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "246.1 lb comp.\nPc = 9,373 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.03", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "346.1 lb comp.\nPc = 9,373 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.04", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "46.13 lb comp.\nPc = 9,373 lb", "8,300 lb-in\nMc = 16,090 lb-in\nabout x", "Eq. H1-1b", "0.004127", "0.52", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("46.13 lb comp.\nPc = 9,373 lb"), strong("12,450 lb-in\nMc = 16,090 lb-in\nabout x"), strong("Eq. H1-1b"), strong("0.004127"), strong("0.78"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "46.13 lb comp.\nPc = 9,373 lb", "8,300 lb-in\nMc = 16,090 lb-in\nabout x", "Eq. H1-1b", "0.004127", "0.52", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "46.13 lb comp.\nPc = 9,373 lb", "12,450 lb-in\nMc = 16,090 lb-in\nabout x", "Eq. H1-1b", "0.004127", "0.78", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "172.3 lb tension\nPt = 23,140 lb", "—", "Pr/Pt\n(Eq. D2-1)", "—", "0.01", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "272.3 lb tension\nPt = 23,140 lb", "—", "Pr/Pt\n(Eq. D2-1)", "—", "0.01", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "46.13 lb comp.\nPc = 9,373 lb", "8,300 lb-in\nMc = 16,090 lb-in\nabout y", "Eq. H1-1b", "0.004127", "0.52", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "46.13 lb comp.\nPc = 9,373 lb", "12,450 lb-in\nMc = 16,090 lb-in\nabout y", "Eq. H1-1b", "0.004127", "0.78", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Capacity")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$display(lambda_"pf" = "1.12" sqrt(frac(E, F_y)) = "1.12" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "28.12")$], "Compact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"rf" = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "35.15")$], "Noncompact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"pw" = "2.42" sqrt(frac(E, F_y)) = "2.42" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "60.76")$], "Compact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$display(lambda_"rw" = "5.7" sqrt(frac(E, F_y)) = "5.7" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "143.1")$], "Noncompact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$Z_x = "0.5840 in"^3$], "Plastic section modulus about the x axis", "AISC Shapes Database v16.0")
#calcline([$display(M_"px" = F_y Z_x = ("46.00 ksi") ("0.5840 in"^3) = "26,860 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "14.20"$], "Flange slenderness about the x axis: b/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_f = 14.2 <= lambda_"pf" = 28.12$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact flange: flange local buckling does not apply"*], "Flange classification, bending about the x axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$lambda_w = "14.20"$], "Web slenderness about the x axis: h/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_w = 14.2 <= lambda_"pw" = 60.76$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the x axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$"Square section"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "", "AISC 360-22 §F7.4, User Note")
#calcline([$display(M_"nx" = M_"px" = "26,860 lb-in")$], "Nominal flexural strength about the x axis: yielding", "AISC 360-22 §F7")
#calcline([$display(M_"cx" = frac(M_"nx", Omega_b) = frac(("26,860 lb-in"), "1.670") = "16,090 lb-in")$], "Allowable flexural strength about the x axis", "AISC 360-22 Eq. B3-2")
#calcline([$display(lambda_(r,c) = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "35.15")$], "Slender limit, walls of rectangular HSS in compression", "AISC 360-22 Table B4.1a, Case 6")
#calcline([$lambda_b = "14.20"$], "Wall slenderness: b/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_b = 14.2 <= lambda_(r,c) = 35.15$ #h(6pt) $arrow.r$ #h(6pt) *#"Nonslender"*], "Wall classification, compression: no noncompact category", "AISC 360-22 §B4.1a")
#calcline([$K = "2.100"$], "Effective length factor, fixed-free (recommended design value)", "AISC 360-22 Comm. Table C-A-7.1, case (e)")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$display(L_c = K h = "2.100" ("42.00 in") = "88.20 in")$], "Effective length, with the unbraced length taken as the post height h", "AISC 360-22 §E2; Engineering judgement (EOR): unbraced length is the post height")
#calcline([$r = "0.7610 in"$], "Radius of gyration, the same about both axes", "AISC Shapes Database v16.0")
#calcline([$display(frac(L_c, r) = frac(("88.20 in"), ("0.7610 in")) = "115.9")$], "Effective slenderness ratio", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 115.9 <= 200$ #h(6pt) $arrow.r$ #h(6pt) *#"Within the recommended limit"*], "For members designed on the basis of compression, the effective slenderness ratio Lc/r preferably should not exceed 200.", "AISC 360-22 §E2, User Note")
#calcline([$display("4.71" sqrt(frac(E, F_y)) = "4.71" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "118.3")$], "Limit between inelastic and elastic buckling", "AISC 360-22 §E3(a), (b)")
#calcline([$display(F_e = frac(pi^("2") E, (frac(L_c, r))^("2")) = frac(pi^("2") ("29,000 ksi"), "115.9"^("2")) = "21.31 ksi")$], "Elastic buckling stress", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 115.9 <= 118.3$ #h(6pt) $arrow.r$ #h(6pt) *#"Inelastic buckling: Eq. E3-2"*], "", "AISC 360-22 §E3(a), (b)")
#calcline([$display(frac(F_y, F_e) = frac(("46.00 ksi"), ("21.31 ksi")) = "2.159")$], "Exponent in Eq. E3-2", "AISC 360-22 Eq. E3-2")
#calcline([$display(F_"cr" = "0.658"^(frac(F_y, F_e)) F_y = "0.658"^("2.159") ("46.00 ksi") = "18.64 ksi")$], "Critical stress", "AISC 360-22 Eq. E3-2")
#calcline([$A_g = "0.8400 in"^2$], "Gross area", "AISC Shapes Database v16.0")
#calcline([$display(P_n = F_"cr" A_g = ("18.64 ksi") ("0.8400 in"^2) = "15,650 lb")$], "Nominal compressive strength", "AISC 360-22 Eq. E3-1")
#calcline([$Omega_c = "1.670"$], "Safety factor for compression (ASD)", "AISC 360-22 §E1")
#calcline([$display(P_c = frac(P_n, Omega_c) = frac(("15,650 lb"), "1.670") = "9,373 lb")$], "Allowable compressive strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: outward, distributed load")
#calcline([$P_D = "46.13 lb"$], "D at the post: axial dead load", "Loading")
#calcline([$display(P_r = "1.0" P_D = "1.0" ("46.13 lb") = "46.13 lb")$], "Required axial strength: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (outward) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p (critical section at the top of the baseplate)", "Loading")
#calcline([$display(M_L = V_L L_"post" = ("300.0 lb") ("41.50 in") = "12,450 lb-in")$], "Live-load moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(M_r = "1.0" M_L = "1.0" ("12,450 lb-in") = "12,450 lb-in")$], "Required flexural strength", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$I_x = "0.4860 in"^4$], "Moment of inertia about the x axis, which this case bends", "AISC Shapes Database v16.0")
#calcline([$display(P_e = frac(pi^("2") E I_x, L_c^("2")) = frac(pi^("2") ("29,000 ksi") ("0.4860 in"^4), ("88.20 in")^("2")) = "17,880 lb")$], "Elastic critical buckling load, at the compression Lc", "AISC 360-22 Eq. A-8-5; Engineering judgement (EOR): Pe at Lc = 2.1h")
#calcline([$display(frac(alpha P_r, P_e) = frac("1.6" P_r, P_e) = frac("1.6" ("46.13 lb"), ("17,880 lb")) = "0.004127")$], "Second-order ratio", "AISC 360-22 App. 8")
#calcline([$frac(alpha P_r, P_e) <= 0.05$ #h(6pt) $arrow.r$ #h(6pt) *#"Second-order effects negligible: αPr/Pe = 0.004127; amplification taken as 1.0."*], "", "Engineering judgement (EOR): second-order limit")
#calcline([$display(frac(P_r, P_c) = frac(("46.13 lb"), ("9,373 lb")) = "0.004921")$], "Axial ratio, selects the interaction equation", "AISC 360-22 §H1.1")
#calcline([$frac(P_r, P_c) = 0.004921 < 0.2$ #h(6pt) $arrow.r$ #h(6pt) *#"Eq. H1-1b"*], "", "AISC 360-22 §H1.1")
#calcline([$display("Ratio" = frac(P_r, "2" P_c) + frac(M_r, M_"cx") = frac(("46.13 lb"), "2" ("9,373 lb")) + frac(("12,450 lb-in"), ("16,090 lb-in")) = "0.78")$], "Combined axial and flexure", "AISC 360-22 Eq. H1-1b")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.78 <= 1.00$ #h(10pt) #"OK"])

= Check 6: Post deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), "Downward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Outward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.3381 in", "0.6917 in", "0.49", "", strong("Outward"), strong("Distributed"), strong("1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only"), strong("0.5071 in"), strong("0.6917 in"), strong("0.73"), strong("Controls"), "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.3381 in", "0.6917 in", "0.49", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.5071 in", "0.6917 in", "0.73", "", "Upward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Longitudinal", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.3381 in", "0.6917 in", "0.49", "", "Longitudinal", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.5071 in", "0.6917 in", "0.73", "")

#heading(level: 2, "Controlling case: Outward, distributed (1.0L, horizontal; Engineering judgement (EOR): serviceability, live load only)")

#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p", "Loading")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_x = "0.4860 in"^4$], "Moment of inertia about the x axis, which this case bends", "AISC Shapes Database v16.0")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (outward) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(Delta_L = frac(V_L L_"post"^("3"), "3" E I_x) = frac(("300.0 lb") ("41.50 in")^("3"), "3" ("29,000 ksi") ("0.4860 in"^4)) = "0.5071 in")$], "Live-load deflection at the top of the post", "AISC Manual Table 3-23, Case 22")
#calcline([$display(Delta = "1.0" Delta_L = "1.0" ("0.5071 in") = "0.5071 in")$], "Live load only; dead load acts axially", "Engineering judgement (EOR): serviceability, live load only")
#calcline([$display(Delta_"allow" = frac(L_"post", "60") = frac(("41.50 in"), "60") = "0.6917 in")$], "Limit (h - t_p)/60", "Engineering judgement (EOR): post deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.5071 in"), ("0.6917 in")) = "0.73")$], "Deflection / limit", "Engineering judgement (EOR): post deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.73 <= 1.00$ #h(10pt) #"OK"])

= Check 7: Post weld to baseplate

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "80.12 lb/in\nuniform", "—", "80.12 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.03", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "112.7 lb/in\nuniform", "—", "112.7 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.04", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "10,570 lb/in\ncompression side", "65.10 lb/in", "10,570 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "3.80", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("15,850 lb/in\ncompression side"), strong("97.66 lb/in"), strong("15,850 lb/in"), strong("Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in"), strong("5.69"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "10,570 lb/in\ncompression side", "65.10 lb/in", "10,570 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "3.80", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "15,850 lb/in\ncompression side", "97.66 lb/in", "15,850 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "5.69", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "56.09 lb/in\nuniform", "—", "56.09 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.02", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "88.65 lb/in\nuniform", "—", "88.65 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.03", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,717 lb/in\ncompression side", "65.10 lb/in", "2,718 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.98", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "4,068 lb/in\ncompression side", "97.66 lb/in", "4,069 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "1.46", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$a_"face" = "2.000 in"$], "HSS2X2X1/8: outside width of each welded face, the faces perpendicular to the rail", "AISC Shapes Database v16.0")
#calcline([$d_"faces" = "2.000 in"$], "Distance between the two weld lines: the post's outside dimension parallel to the rail", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1160 in"$], "Design wall thickness, HSS2X2X1/8: it sets the outside corner radius", "AISC Shapes Database v16.0")
#calcline([$display(R_o = "2" t_"des" = "2" ("0.1160 in") = "0.2320 in")$], "Outside corner radius", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$w = "0.1875 in"$], "Fillet weld leg size, each welded face (3/16 as entered)", "Input")
#calcline([$display(l_w = a_"face" - "2" R_o = ("2.000 in") - "2" ("0.2320 in") = "1.536 in")$], "Length of each weld line: the flat of its face, between the tangent points", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(L_w = "2" l_w = "2" ("1.536 in") = "3.072 in")$], "Weld length: the two lines", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(S_("w,l") = l_w d_"faces" = ("1.536 in") ("2.000 in") = "3.072 in"^2)$], "Section modulus of the weld lines, a load along the rail: the lines are the extreme fibers", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(S_("w,t") = frac(l_w^("2"), "3") = frac(("1.536 in")^("2"), "3") = "0.7864 in"^2)$], "Section modulus of the weld lines, a load across the guard: each line bends about its own middle", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1875 in") = "0.1326 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Moment arm")
#calcline([$L_"post" = "41.50 in"$], "Moment arm, h - t_p: guard load at the top rail centerline, weld at the top of the baseplate", "Loading")
#subhead("Fillet size limits")
#calcline([$t_"post,nom" = "0.1250 in"$], "Post nominal wall thickness, HSS2X2X1/8", "AISC Shapes Database v16.0")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(t_"min" = "min"(t_"post,nom", t_p) = "min"(("0.1250 in"), ("0.5000 in")) = "0.1250 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w_"min" = "0.1250 in"$], "Minimum fillet size for the thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w = "0.1875 in" >= w_"min" = "0.1250 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"OK"*], "Minimum size", "AISC 360-22 Table J2.4")
#calcline([$"Maximum fillet size"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not applicable"*], "Maximum fillet size along edges of material does not apply: this weld is a T-joint, not a weld along an edge. No maximum size is checked.", "AISC 360-22 §J2.2b(b); Engineering judgement (EOR): no maximum fillet size at a T-joint")
#subhead("Weld metal")
#calcline([$F_"EXX" = "70.00 ksi"$], "Electrode classification strength, E70XX", "AISC 360-22 §J2.6; AWS A5.1")
#calcline([$display(F_"nw" = "0.6" F_"EXX" = "0.6" ("70.00 ksi") = "42.00 ksi")$], "Nominal stress of the weld metal", "AISC 360-22 Table J2.5")
#calcline([$Omega_w = "2.000"$], "Safety factor, fillet weld (ASD)", "AISC 360-22 Table J2.5")
#calcline([$k_"ds" = "1.000"$], "No directional strength increase at the base weld of a rectangular post", "AISC 360-22 §J2.4(a)(2)")
#calcline([$"Rectangular HSS, weld in flexure"$ #h(6pt) $arrow.r$ #h(6pt) *#"No directional increase"*], "Where flexure results in tension in the weld in any load case, the directional strength increase factor cannot exceed 1.0 in fillet welds to the end of rectangular HSS.", "AISC 360-22 §K5, User Note")
#subhead("Base metal: baseplate fusion face")
#calcline([$F_u = "58.00 ksi"$], "Tensile strength, baseplate A36", "AISC Manual Table 2-5")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(R_(n,"BM") = "0.6" F_u t_p = "0.6" ("58.00 ksi") ("0.5000 in") = "17,400 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM"), Omega_"BM") = frac(("17,400 lb/in"), "2.000") = "8,700 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#subhead("Post wall at the welded faces")
#calcline([$"Post wall at the weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Checked on its own lines"*], "At a post to baseplate weld on one pair of faces, the post wall is checked for the weld force along the post axis and for the force along the face separately; the two are not combined, the force along the face being small next to the other.", "Engineering judgement (EOR): post wall at a face-pair base weld checked on its own lines")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$F_u = "58.00 ksi"$], "Tensile strength, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"wall" = "0.1160 in"$], "Post design wall thickness, HSS2X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(R_("n,y") = F_y t_"wall" = ("46.00 ksi") ("0.1160 in") = "5,336 lb/in")$], "Yielding of the wall under the force along the post axis, per inch of weld", "AISC 360-22 Eq. J4-1")
#calcline([$Omega_y = "1.670"$], "Safety factor, yielding (ASD)", "AISC 360-22 §J4.1(a)")
#calcline([$display(R_("n,u") = F_u t_"wall" = ("58.00 ksi") ("0.1160 in") = "6,728 lb/in")$], "Rupture of the wall under the force along the post axis, per inch of weld", "AISC 360-22 Eq. J4-2")
#calcline([$Omega_u = "2.000"$], "Safety factor, rupture (ASD)", "AISC 360-22 §J4.1(b)")
#calcline([$display(R_("wall,a") = "min"(frac(R_("n,y"), Omega_y), frac(R_("n,u"), Omega_u)) = "min"(frac(("5,336 lb/in"), "1.670"), frac(("6,728 lb/in"), "2.000")) = "3,195 lb/in")$], "Allowable force along the post axis per inch: the lower of yielding and rupture", "AISC 360-22 Eq. B3-2")
#calcline([$display(R_("n,v") = "0.6" F_u t_"wall" = "0.6" ("58.00 ksi") ("0.1160 in") = "4,037 lb/in")$], "Shear rupture of the wall under the force along the face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_v = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(R_("wall,f") = frac(R_("n,v"), Omega_v) = frac(("4,037 lb/in"), "2.000") = "2,018 lb/in")$], "Allowable force along the face per inch", "AISC 360-22 Eq. B3-2")
#subhead("Demand: outward, distributed load")
#calcline([$P_D = "46.13 lb"$], "D at the post: axial dead load at the top of the baseplate", "Loading")
#calcline([$display(P = "1.0" P_D = "1.0" ("46.13 lb") = "46.13 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (outward), at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("300.0 lb") = "300.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V L_"post" = ("300.0 lb") ("41.50 in") = "12,450 lb-in")$], "Moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(f_a = frac(P, L_w) = frac(("46.13 lb"), ("3.072 in")) = "15.02 lb/in")$], "Axial force per inch of weld, compression, uniform along the weld lines", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_("w,t")) = frac(("12,450 lb-in"), ("0.7864 in"^2)) = "15,830 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("15.02 lb/in") + ("15,830 lb/in") = "15,850 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("15.02 lb/in") - ("15,830 lb/in")) = "15,820 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "15,850 lb/in" >= f_(n,"t") = "15,820 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "15,850 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, L_w) = frac(("300.0 lb"), ("3.072 in")) = "97.66 lb/in")$], "Shear per inch of weld, taken as uniform along the weld lines", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("15,850 lb/in")^("2") + ("97.66 lb/in")^("2")) = "15,850 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.1326 in") dot "1.000" = "5,568 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("5,568 lb/in"), "2.000") = "2,784 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("15,850 lb/in"), ("2,784 lb/in")) = "5.69")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_r, frac(R_(n,"BM"), Omega_"BM")) = frac(("15,850 lb/in"), ("8,700 lb/in")) = "1.82")$], "Baseplate fusion face: the resultant per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_("wall,a") = frac(f_n, R_("wall,a")) = frac(("15,850 lb/in"), ("3,195 lb/in")) = "4.96")$], "Post wall: force along the post axis / allowable", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_("wall,f") = frac(f_v, R_("wall,f")) = frac(("97.66 lb/in"), ("2,018 lb/in")) = "0.05")$], "Post wall: force along the face / allowable", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"wall" = "max"("Ratio"_("wall,a"), "Ratio"_("wall,f")) = "max"("4.959", "0.04838") = "4.96")$], "Post wall: the larger of the two, not combined", "Engineering judgement (EOR): post wall at a face-pair base weld checked on its own lines")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM", "Ratio"_"wall") = "max"("5.692", "1.821", "4.959") = "5.69")$], "The largest of weld metal, base metal and post wall", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 5.69 > 1.00$ #h(10pt) #"NG"])

= Summary

#table(columns: (1fr, auto, auto, auto, auto, auto), table.header(strong("Check"), strong("Demand"), strong("Capacity"), strong("Ratio"), strong("Controlling direction"), strong("Result")), "1. Top rail bending", "3,798 lb-in", "14,940 lb-in", "0.25", "Downward, concentrated", "OK", "2. Top rail deflection", "0.09140 in", "0.6000 in", "0.15", "Downward, concentrated", "OK", "3. Top rail weld to post", "85.20 lb/in", "1,856 lb/in (weld metal)", "0.05", "Outward, distributed", "OK", "4a. Intermediate rail", "1,023 lb-in", "6,392 lb-in", "0.16", "Downward, bending", "OK", "4b. Intermediate rail weld to post", "10.89 lb/in", "1,856 lb/in (weld metal)", "0.01", "Downward, component", "OK", "5. Post combined axial and flexure", "Pr = 46.13 lb; Mr = 12,450 lb-in", "Pc = 9,373 lb; Mc = 16,090 lb-in", "0.78", "Outward, distributed", "OK", "6. Post deflection", "0.5071 in", "0.6917 in", "0.73", "Outward, distributed", "OK", "7. Post weld to baseplate", "15,850 lb/in", "2,784 lb/in (weld metal)", "5.69", "Outward, distributed", "NG")

= Anchor reactions

LRFD reactions at the top of concrete, for direct input into anchor software: reporting, not a pass/fail check. Each set is simultaneous: the shear, axial force and moment that occur together.

#text(weight: "bold", "Baseplate: B = 6.000 in (parallel to rail) × N = 8.000 in (perpendicular to rail)")

#subhead("Dead load at the base")
#calcline([$D_"rail" = "21.96 lb"$], "Top rail", "Loading")
#calcline([$D_"int" = "13.62 lb"$], "Intermediate rail", "Loading")
#calcline([$D_"post" = "10.55 lb"$], "Post, over h - t_p", "Loading")
#calcline([$rho = "0.2836 lb/in"^3$], "Steel unit weight", "AISC Manual 16th Ed., Part 17")
#calcline([$B = "6.000 in"$], "Baseplate, parallel to the rail", "Input")
#calcline([$N = "8.000 in"$], "Baseplate, perpendicular to the rail", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(W_"bp" = rho B N t_p = ("0.2836 lb/in"^3) ("6.000 in") ("8.000 in") ("0.5000 in") = "6.806 lb")$], "Baseplate weight: in the reaction sets only, below the critical section of Checks 5 and 7", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$display(D = D_"rail" + D_"int" + D_"post" + W_"bp" = ("21.96 lb") + ("13.62 lb") + ("10.55 lb") + ("6.806 lb") = "52.93 lb")$], "Dead load at the base", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#subhead("Governing guard load type")
#calcline([$P = "200.0 lb"$], "Concentrated guard load P, at the top of the post", "Loading")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$w_L L = "300.0 lb" > P = "200.0 lb"$ #h(6pt) $arrow.r$ #h(6pt) *#"Distributed load governs"*], "The larger at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Lateral set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "480.0 lb", "−47.64 lb (compression)", "20,160 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D axial, 1.6L horizontal; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "21.96 lb", "D, intermediate rail", "13.62 lb", "D, post", "10.55 lb", "D, baseplate", "6.806 lb", strong("D, total"), strong("52.93 lb"))

#"V and M act in the same vertical plane; M = V·h."

#"Lateral set applies in any horizontal direction; enter it in the anchor software in the orientation that governs the anchor pattern. Loads can reverse."

#subhead("Demand: lateral, distributed load")
#calcline([$D = "52.93 lb"$], "Dead load at the base", "Reactions")
#calcline([$display(abs(N_u) = "0.9" D = "0.9" ("52.93 lb") = "47.64 lb")$], "Axial force at the base: dead load, compression", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal at the top of the post, in any horizontal direction", "Stated assumption: the tributary length is the span")
#calcline([$display(V_u = "1.6" V_L = "1.6" ("300.0 lb") = "480.0 lb")$], "Base shear", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$h = "42.00 in"$], "Moment arm: top rail centerline to top of concrete", "Input")
#calcline([$display(M_u = V_u h = ("480.0 lb") ("42.00 in") = "20,160 lb-in")$], "Base moment at the top of concrete: V_u at the top rail centerline, arm h", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Upward set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "0 lb", "+432.4 lb (tension)", "0 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D + 1.6L, net axial; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "21.96 lb", "D, intermediate rail", "13.62 lb", "D, post", "10.55 lb", "D, baseplate", "6.806 lb", strong("D, total"), strong("52.93 lb"))

#subhead("Demand: upward, distributed load")
#calcline([$D = "52.93 lb"$], "Dead load at the base", "Reactions")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(P_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, upward at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(abs(N_u) = "1.6" P_L - "0.9" D = "1.6" ("300.0 lb") - "0.9" ("52.93 lb") = "432.4 lb")$], "Axial force at the base: net tension (uplift), guard load opposing dead load", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
