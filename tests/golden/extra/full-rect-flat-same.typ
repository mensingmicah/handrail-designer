
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

#table(columns: (auto, 1fr, auto), table.header(strong("Entry"), strong("Citation"), strong("Source")), "aisc360.K1.3.rect_chord.wall_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "material.A500_GrB.hss_rect.Fy", "AISC Manual Table 2-4", "memory", "material.A500_GrB.hss_rect.Fu", "AISC Manual Table 2-4", "memory", "aisc360.K1.3.Fy_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "aisc360.K1.3.Fy_Fu_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "ej.weld.post_wall.fu_fy_min", "Engineering judgement (EOR): post wall at the weld covered by Check 5 while Fu/Fy >= 1.20", "engineer", "asce7.guard.component", "ASCE 7-22 §4.5.1.2", "memory", "ej.post.axial_dead_load", "Engineering judgement (EOR): post dead load", "engineer", "ej.section.orientation.rail_horizontal", "Engineering judgement (EOR): a rectangular member's axes follow from its long side", "engineer", "ej.section.orientation.post_perpendicular", "Engineering judgement (EOR): a rectangular member's axes follow from its long side", "engineer", "material.grades.hss_rect", "AISC Manual Table 2-4", "memory", "aisc360.B4.1b.rect_hss.flange.lambda_p", "AISC 360-22 Table B4.1b, Case 17", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.flange.lambda_r", "AISC 360-22 Table B4.1b, Case 17", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.web.lambda_p", "AISC 360-22 Table B4.1b, Case 19", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.web.lambda_r", "AISC 360-22 Table B4.1b, Case 19", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-1", "AISC 360-22 Eq. F7-1", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.compact_no_local_buckling", "AISC 360-22 §F7.2(a), §F7.3(a)", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.4.no_ltb_note", "AISC 360-22 §F7.4, User Note", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.nominal_strength", "AISC 360-22 §F7", "AISC 360-22 text, read 2026-10-11", "ej.bending.biaxial_rect", "Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "engineer", "ej.flexure.unbraced_length", "Engineering judgement (EOR): unbraced length for lateral-torsional buckling", "engineer", "aisc360.eq.F7-10.coeff", "AISC 360-22 Eq. F7-10", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-10", "AISC 360-22 Eq. F7-10", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.4a.no_ltb_below_Lp", "AISC 360-22 §F7.4(a)", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.H1-1b", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.K1-1.coeff", "AISC 360-22 Eq. K1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.K1-1", "AISC 360-22 Eq. K1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.K5.1.Be_cap", "AISC 360-22 Table K5.1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.K5-5", "AISC 360-22 Eq. K5-5", "AISC 360-22 text, read 2026-10-11", "aisc360.K5.nonuniform", "AISC 360-22 §K5", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.K5-6", "AISC 360-22 Eq. K5-6", "AISC 360-22 text, read 2026-10-11", "ej.weld.k5.case_mapping", "Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties", "engineer", "aisc360.eq.K5-7", "AISC 360-22 Eq. K5-7", "AISC 360-22 text, read 2026-10-11", "aisc360.J2.2a.throat.coeff", "AISC 360-22 §J2.2a", "memory", "aisc360.J2.2a.throat", "AISC 360-22 §J2.2a", "memory", "ej.weld.equal_width_fillet", "Engineering judgement (EOR): fillet model kept at equal widths", "engineer", "aisc360.J2.4.min_size", "AISC 360-22 Table J2.4", "memory", "ej.weld.max_size_not_applicable", "Engineering judgement (EOR): no maximum fillet size at a T-joint", "engineer", "aisc360.J2.2b.max_size_edges", "AISC 360-22 §J2.2b(b)", "memory", "material.E70XX.FEXX", "AISC 360-22 §J2.6; AWS A5.1", "memory", "aisc360.J2.5.fnw.coeff", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.fnw", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.omega_w", "AISC 360-22 Table J2.5", "memory", "ej.weld.branch_kds", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld", "engineer", "aisc360.eq.J4-4.coeff", "AISC 360-22 Eq. J4-4", "memory", "aisc360.eq.J4-4", "AISC 360-22 Eq. J4-4", "memory", "aisc_manual.part9.base_metal", "AISC Manual Part 9, base metal at welds", "memory", "aisc360.J4.2.omega_rupture", "AISC 360-22 §J4.2(b)", "memory", "ej.weld.chord_wall.rect", "Engineering judgement (EOR): a rectangular chord's limit states not checked", "engineer", "ej.weld.post_wall_covered", "Engineering judgement (EOR): post wall at the weld covered by Check 5", "engineer", "aws.d1_1.thickness_min", "AWS D1.1/D1.1M:2020, Clause 1", "memory", "ej.weld.line_method", "Engineering judgement (EOR): elastic weld as a line", "engineer", "ej.weld.no_bearing", "Engineering judgement (EOR): no bearing credit at the weld", "engineer", "aisc360.J2.4.fillet_strength", "AISC 360-22 Eq. J2-4", "memory", "ej.intermediate.same_as_top", "Engineering judgement (EOR): intermediate rail controlled by Checks 1 and 2", "engineer", "ej.weld.intermediate.rect_full", "Engineering judgement (EOR): Check 4b computed in full at a joint with a rectangular member", "engineer", "ej.weld.intermediate_simple_shear", "Engineering judgement (EOR): intermediate rail to post weld as a simple shear connection", "engineer", "ej.weld.intermediate_line_model", "Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post", "engineer", "ej.weld.intermediate_base_metal", "Engineering judgement (EOR): Check 4b base metal on both walls, lower governs", "engineer", "ej.weld.check4b.no_chord_demand", "Engineering judgement (EOR): no chord limit state demand at the intermediate rail", "engineer", "ej.component.downward", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "engineer", "aisc_manual.t3-23.case1.R", "AISC Manual Table 3-23, Case 1", "memory", "aisc360.B4.1a.rect_hss.lambda_r", "AISC 360-22 Table B4.1a, Case 6", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1a.classification", "AISC 360-22 §B4.1a", "memory", "aisc360.CA7.K_fixed_free", "AISC 360-22 Comm. Table C-A-7.1, case (e)", "memory", "aisc360.E2.effective_length", "AISC 360-22 §E2", "memory", "ej.post.unbraced_length", "Engineering judgement (EOR): unbraced length is the post height", "engineer", "aisc360.eq.E3-4", "AISC 360-22 Eq. E3-4", "memory", "aisc360.E2.user_note.slenderness", "AISC 360-22 §E2, User Note", "memory", "aisc360.E2.user_note.slenderness.limit", "AISC 360-22 §E2, User Note", "memory", "aisc360.E3.branch_limit", "AISC 360-22 §E3(a), (b)", "memory", "aisc360.eq.E3-2", "AISC 360-22 Eq. E3-2", "memory", "aisc360.eq.E3-2.base", "AISC 360-22 Eq. E3-2", "memory", "aisc360.eq.E3-1", "AISC 360-22 Eq. E3-1", "memory", "aisc360.E1.omega_c", "AISC 360-22 §E1", "memory", "aisc_manual.t3-23.case22.M", "AISC Manual Table 3-23, Case 22", "memory", "aisc360.eq.A-8-5", "AISC 360-22 Eq. A-8-5", "memory", "ej.second_order.pe_length", "Engineering judgement (EOR): Pe at Lc = 2.1h", "engineer", "aisc360.app8.alpha_asd", "AISC 360-22 App. 8", "memory", "ej.second_order.limit", "Engineering judgement (EOR): second-order limit", "engineer", "ej.second_order.negligible", "Engineering judgement (EOR): second-order limit", "engineer", "aisc360.H1.1.threshold", "AISC 360-22 §H1.1", "memory", "aisc360.eq.H1-1b.coeff", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.D2-1", "AISC 360-22 Eq. D2-1", "memory", "aisc360.D2.omega_t", "AISC 360-22 §D2(a)", "memory", "aisc_manual.t3-23.case22.delta", "AISC Manual Table 3-23, Case 22", "memory", "ej.deflection.limit.post", "Engineering judgement (EOR): post deflection limit, not code", "engineer", "ej.weld.line.corner_radius_coeff", "Engineering judgement (EOR): weld line on the true rounded rectangle", "engineer", "ej.weld.line.rounded_rectangle", "Engineering judgement (EOR): weld line on the true rounded rectangle", "engineer", "ej.weld.line.face_pair", "Engineering judgement (EOR): weld line on a pair of faces, flats only", "engineer", "aisc360.J2.4.kds_rect_hss", "AISC 360-22 §J2.4(a)(2)", "AISC 360-22 text, read 2026-10-11", "aisc360.K5.user_note.rect_hss_kds", "AISC 360-22 §K5, User Note", "AISC 360-22 text, read 2026-10-11", "material.A36.Fu", "AISC Manual Table 2-5", "memory", "ej.weld.post_wall.face_pair", "Engineering judgement (EOR): post wall at a face-pair base weld checked on its own lines", "engineer", "aisc360.eq.J4-1", "AISC 360-22 Eq. J4-1", "AISC 360-22 text, read 2026-10-11", "aisc360.J4.1.omega_yield", "AISC 360-22 §J4.1(a)", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.J4-2", "AISC 360-22 Eq. J4-2", "AISC 360-22 text, read 2026-10-11", "aisc360.J4.1.omega_rupture", "AISC 360-22 §J4.1(b)", "AISC 360-22 text, read 2026-10-11", "material.steel.density", "AISC Manual 16th Ed., Part 17", "memory", "ej.reaction.location", "Engineering judgement (EOR): reactions at the top of concrete, arm h", "engineer", "ej.combo.reaction", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "engineer", "ej.reaction.lateral_note", "Engineering judgement (EOR): one lateral set, any horizontal direction", "engineer")

= Dimensions

Every dimension as entered, and as the tool read it. A bare number is inches.

#table(columns: (1fr, auto, auto, auto), table.header(strong("Dimension"), strong("As entered"), strong("Read as"), strong("Inches")), "Span, post to post (c/c)", "6'-0\"", "6'-0\"", "72.00 in", "Post height h, top of concrete to top rail centerline", "42", "3'-6\"", "42.00 in", "Baseplate thickness t_p", "1/2", "1/2\"", "0.5000 in", "Baseplate B, parallel to the rail", "6", "6\"", "6.000 in", "Baseplate N, perpendicular to the rail", "8", "8\"", "8.000 in", "Fillet weld, top rail to post", "1/8", "1/8\"", "0.1250 in", "Fillet weld, post to baseplate", "3/16", "3/16\"", "0.1875 in")

#text("Directional strength increase at the post to baseplate weld: not elected (directional_increase = false).")

#text("Post to baseplate weld pattern: faces parallel to rail (base_pattern).")

Derived lengths, each computed in the calc where it is used:

#table(columns: (1fr, auto, auto, auto), table.header(strong("Derived length"), strong("Formula"), strong("Inches"), strong("Computed in")), "Post cantilever length, top of baseplate to top rail centerline", [$L_"post" = h - t_p$], "41.50 in", "Loading", "Eccentricity: rail centerline to the weld plane at the rail underside", [$e = frac(d_"rail", "2")$], "1.000 in", "Check 3", "Effective length, with the unbraced length taken as the post height h", [$L_c = K h$], "88.20 in", "Check 5")

= Section properties

#text("Top rail: HSS3X2X1/8, A500 Gr B (default).") Properties are used exactly as published in the AISC Shapes Database v16.0.

#calcline([$H = "3.000 in"$], "HSS3X2X1/8: outside dimension of the longer side", "AISC Shapes Database v16.0")
#calcline([$B = "2.000 in"$], "Outside dimension of the shorter side", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.1250 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1160 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "1.070 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "0.3250 lb/in"$], "Nominal weight: tabulated 3.9 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I_x = "1.300 in"^4$], "Moment of inertia about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$S_x = "0.8670 in"^3$], "Elastic section modulus about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$Z_x = "1.060 in"^3$], "Plastic section modulus about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$r_x = "1.100 in"$], "Radius of gyration about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$I_y = "0.6920 in"^4$], "Moment of inertia about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$S_y = "0.6920 in"^3$], "Elastic section modulus about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$Z_y = "0.8030 in"^3$], "Plastic section modulus about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$r_y = "0.8040 in"$], "Radius of gyration about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$J = "1.470 in"^4$], "Torsional constant", "AISC Shapes Database v16.0")
#calcline([$b slash t = "14.20"$], "Width-to-thickness ratio of the shorter walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$h slash t = "22.90"$], "Width-to-thickness ratio of the longer walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$"long_side = horizontal"$ #h(6pt) $arrow.r$ #h(6pt) *#"Long side horizontal: a vertical load bends the weak axis (y); the horizontal guard load bends the strong axis (x)."*], "Orientation, and the axis each load bends", "Engineering judgement (EOR): a rectangular member's axes follow from its long side")

#text("Post: HSS3X2X1/8, A500 Gr B (default).")

#calcline([$H = "3.000 in"$], "HSS3X2X1/8: outside dimension of the longer side", "AISC Shapes Database v16.0")
#calcline([$B = "2.000 in"$], "Outside dimension of the shorter side", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.1250 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1160 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "1.070 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "0.3250 lb/in"$], "Nominal weight: tabulated 3.9 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I_x = "1.300 in"^4$], "Moment of inertia about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$S_x = "0.8670 in"^3$], "Elastic section modulus about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$Z_x = "1.060 in"^3$], "Plastic section modulus about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$r_x = "1.100 in"$], "Radius of gyration about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$I_y = "0.6920 in"^4$], "Moment of inertia about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$S_y = "0.6920 in"^3$], "Elastic section modulus about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$Z_y = "0.8030 in"^3$], "Plastic section modulus about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$r_y = "0.8040 in"$], "Radius of gyration about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$J = "1.470 in"^4$], "Torsional constant", "AISC Shapes Database v16.0")
#calcline([$b slash t = "14.20"$], "Width-to-thickness ratio of the shorter walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$h slash t = "22.90"$], "Width-to-thickness ratio of the longer walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$"long_side = perpendicular to rail"$ #h(6pt) $arrow.r$ #h(6pt) *#"Long side perpendicular to the rail: a load across the guard (outward or inward) bends the strong axis (x); a load along the rail bends the weak axis (y)."*], "Orientation, and the axis each load bends", "Engineering judgement (EOR): a rectangular member's axes follow from its long side")

#text("Intermediate rail: same section and grade as the top rail.")

#text("Baseplate: A36. Welds: fillet, electrode E70XX; all around at the rails, and at the baseplate on the faces parallel to rail.")

= Loading

Guard loads per ASCE 7-22. The concentrated and uniform loads are separate load types and do not act concurrently. Each check applies them in every direction case and reports the controlling one.

#calcline([$P = "200.0 lb"$], "Concentrated guard load, any direction, any point on the top rail", "ASCE 7-22 §4.5.1")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load, 50 lb/ft, any direction; not concurrent with P", "ASCE 7-22 §4.5.1.1")
#calcline([$P_c = "50.00 lb"$], "Component load on the intermediate rail, horizontal; also applied downward (engineering judgement)", "ASCE 7-22 §4.5.1.2")
#calcline([$w_D = "0.3250 lb/in"$], "Top rail self-weight: tabulated W = 3.9 lb/ft", "AISC Shapes Database v16.0")
#subhead("Dead load at the post")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(L_"post" = h - t_p = ("42.00 in") - ("0.5000 in") = "41.50 in")$], "Post cantilever length, top of baseplate to top rail centerline", "Stated assumption: post fixed at the top of the baseplate")
#calcline([$W_"post" = "0.3250 lb/in"$], "Post self-weight: HSS3X2X1/8, tabulated W = 3.9 lb/ft", "AISC Shapes Database v16.0")
#calcline([$display(D_"post" = W_"post" L_"post" = ("0.3250 lb/in") ("41.50 in") = "13.49 lb")$], "Post dead load, full weight at the base", "Engineering judgement (EOR): post dead load")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post (stated assumption)", "Input")
#calcline([$display(D_"rail" = w_D L = ("0.3250 lb/in") ("72.00 in") = "23.40 lb")$], "Top rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$w_(D,"int") = "0.3250 lb/in"$], "Intermediate rail self-weight: HSS3X2X1/8 (same section as the top rail), tabulated W = 3.9 lb/ft", "AISC Shapes Database v16.0")
#calcline([$display(D_"int" = w_(D,"int") L = ("0.3250 lb/in") ("72.00 in") = "23.40 lb")$], "Intermediate rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$display(P_D = D_"rail" + D_"int" + D_"post" = ("23.40 lb") + ("23.40 lb") + ("13.49 lb") = "60.29 lb")$], "D at the post: axial dead load at the top of the baseplate", "Engineering judgement (EOR): post dead load")

= Check 1: Top rail bending

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Vertical load* \ $M_r$, $M_c$], [*Horizontal load* \ $M_r$, $M_c$], [*Ratio*], []), strong("Downward"), strong("Concentrated"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2"), strong("Mry = 3,811 lb-in\nMcy = 22,120 lb-in"), strong("—"), strong("0.17"), strong("Controls"), "Downward", "Distributed", "1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2", "Mry = 2,911 lb-in\nMcy = 22,120 lb-in", "—", "0.13", "", "Outward", "Concentrated", "1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "Mry = 210.6 lb-in\nMcy = 22,120 lb-in", "Mrx = 3,600 lb-in\nMcx = 29,200 lb-in", "0.13", "", "Outward", "Distributed", "1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "Mry = 210.6 lb-in\nMcy = 22,120 lb-in", "Mrx = 2,700 lb-in\nMcx = 29,200 lb-in", "0.10", "", "Inward", "Concentrated", "1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "Mry = 210.6 lb-in\nMcy = 22,120 lb-in", "Mrx = 3,600 lb-in\nMcx = 29,200 lb-in", "0.13", "", "Inward", "Distributed", "1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "Mry = 210.6 lb-in\nMcy = 22,120 lb-in", "Mrx = 2,700 lb-in\nMcx = 29,200 lb-in", "0.10", "", "Upward", "Concentrated", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "Mry = 3,474 lb-in\nMcy = 22,120 lb-in", "—", "0.16", "", "Upward", "Distributed", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "Mry = 2,574 lb-in\nMcy = 22,120 lb-in", "—", "0.12", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Downward, concentrated (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Demand: downward, concentrated load")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$w_D = "0.3250 lb/in"$], "Top rail self-weight", "Loading")
#calcline([$display(M_D = frac(w_D L^("2"), "8") = frac(("0.3250 lb/in") ("72.00 in")^("2"), "8") = "210.6 lb-in")$], "Dead-load moment, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$P = "200.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(M_L = frac(P L, "4") = frac(("200.0 lb") ("72.00 in"), "4") = "3,600 lb-in")$], "Live-load moment, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$display(M_"ry" = "1.0" M_D + "1.0" M_L = "1.0" ("210.6 lb-in") + "1.0" ("3,600 lb-in") = "3,811 lb-in")$], "Required flexural strength about the y axis: D and L, both vertical", "ASCE 7-22 §2.4.1, Comb. 2")
#subhead("Section")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$display(lambda_"pf" = "1.12" sqrt(frac(E, F_y)) = "1.12" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "28.12")$], "Compact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"rf" = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "35.15")$], "Noncompact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"pw" = "2.42" sqrt(frac(E, F_y)) = "2.42" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "60.76")$], "Compact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$display(lambda_"rw" = "5.7" sqrt(frac(E, F_y)) = "5.7" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "143.1")$], "Noncompact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#subhead("Capacity about the y axis (vertical load)")
#calcline([$Z_y = "0.8030 in"^3$], "Plastic section modulus about the y axis", "AISC Shapes Database v16.0")
#calcline([$display(M_"py" = F_y Z_y = ("46.00 ksi") ("0.8030 in"^3) = "36,940 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "22.90"$], "Flange slenderness about the y axis: h/t of the 3.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_f = 22.9 <= lambda_"pf" = 28.12$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact flange: flange local buckling does not apply"*], "Flange classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$lambda_w = "14.20"$], "Web slenderness about the y axis: b/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_w = 14.2 <= lambda_"pw" = 60.76$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$"Bending about the minor axis"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "", "AISC 360-22 §F7.4, User Note")
#calcline([$display(M_"ny" = M_"py" = "36,940 lb-in")$], "Nominal flexural strength about the y axis: yielding", "AISC 360-22 §F7")
#calcline([$display(M_"cy" = frac(M_"ny", Omega_b) = frac(("36,940 lb-in"), "1.670") = "22,120 lb-in")$], "Allowable flexural strength about the y axis", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = frac(M_"ry", M_"cy") = frac(("3,811 lb-in"), ("22,120 lb-in")) = "0.17")$], "Demand / capacity", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.17 <= 1.00$ #h(10pt) #"OK"])

= Check 2: Top rail deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), strong("Downward"), strong("Concentrated"), strong("1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability"), strong("0.08316 in"), strong("0.6000 in"), strong("0.14"), strong("Controls"), "Downward", "Distributed", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.07832 in", "0.6000 in", "0.13", "", "Outward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.04125 in", "0.6000 in", "0.07", "", "Outward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.03867 in", "0.6000 in", "0.06", "", "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.04125 in", "0.6000 in", "0.07", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.03867 in", "0.6000 in", "0.06", "", "Upward", "Concentrated", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.07750 in", "0.6000 in", "0.13", "", "Upward", "Distributed", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.07265 in", "0.6000 in", "0.12", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Downward, concentrated (1.0D + 1.0L, vertical; Engineering judgement (EOR): serviceability)")

#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_y = "0.6920 in"^4$], "Moment of inertia about the y axis (vertical load)", "AISC Shapes Database v16.0")
#calcline([$P = "200.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(Delta_L = frac(P L^("3"), "48" E I_y) = frac(("200.0 lb") ("72.00 in")^("3"), "48" ("29,000 ksi") ("0.6920 in"^4)) = "0.07750 in")$], "Live-load deflection, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$w_D = "0.3250 lb/in"$], "Top rail self-weight", "Loading")
#calcline([$display(Delta_D = frac("5" w_D L^("4"), "384" E I_y) = frac("5" ("0.3250 lb/in") ("72.00 in")^("4"), "384" ("29,000 ksi") ("0.6920 in"^4)) = "0.005667 in")$], "Dead-load deflection, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$display(Delta = "1.0" Delta_D + "1.0" Delta_L = "1.0" ("0.005667 in") + "1.0" ("0.07750 in") = "0.08316 in")$], "D and L on the same (vertical) axis", "Engineering judgement (EOR): serviceability")
#calcline([$display(Delta_"allow" = frac(L, "120") = frac(("72.00 in"), "120") = "0.6000 in")$], "Limit L/120", "Engineering judgement (EOR): deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.08316 in"), ("0.6000 in")) = "0.14")$], "Deflection / limit", "Engineering judgement (EOR): deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.14 <= 1.00$ #h(10pt) #"OK"])

= Check 3: Top rail weld to post

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "35.35 lb/in\nuniform", "—", "35.35 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "51.17 lb/in\nuniform", "—", "51.17 lb/in", "Weld 1,856 lb/in\nBase —", "0.03", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "27.78 lb/in\ncompression side", "31.65 lb/in", "42.11 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.02", "", "Outward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "39.81 lb/in\ncompression side", "47.47 lb/in", "61.95 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.03", "", "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "27.78 lb/in\ncompression side", "31.65 lb/in", "42.11 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.02", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "39.81 lb/in\ncompression side", "47.47 lb/in", "61.95 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.03", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "29.42 lb/in\nuniform", "—", "29.42 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "45.25 lb/in\nuniform", "—", "45.25 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "58.45 lb/in\ncompression side", "31.65 lb/in", "66.46 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.04", "", strong("Longitudinal"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("85.82 lb/in\ncompression side"), strong("47.47 lb/in"), strong("98.07 lb/in"), strong("Weld 1,856 lb/in\nBase 2,018 lb/in"), strong("0.05"), strong("Controls"))]

#heading(level: 2, "Controlling case: Longitudinal, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$B = "3.000 in"$], "HSS3X2X1/8: width of the chord face, the rail's horizontal dimension", "AISC Shapes Database v16.0")
#calcline([$t = "0.1160 in"$], "Top rail design wall thickness, the chord", "AISC Shapes Database v16.0")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$H_b = "2.000 in"$], "HSS3X2X1/8: branch dimension along the chord, the post's dimension parallel to the rail", "AISC Shapes Database v16.0")
#calcline([$B_b = "3.000 in"$], "Branch width across the chord face, the post's dimension perpendicular to the rail", "AISC Shapes Database v16.0")
#calcline([$t_b = "0.1160 in"$], "Post design wall thickness, the branch", "AISC Shapes Database v16.0")
#calcline([$F_"yb" = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$display(B_("e,K1") = frac("10", frac(B, t)) frac(F_y t, F_"yb" t_b) B_b = frac("10", frac(("3.000 in"), ("0.1160 in"))) dot frac(("46.00 ksi") ("0.1160 in"), ("46.00 ksi") ("0.1160 in")) ("3.000 in") = "1.160 in")$], "Effective width of the branch across the chord face", "AISC 360-22 Eq. K1-1")
#calcline([$display(B_e = "min"(B_("e,K1"), frac(B_b, "2")) = "min"(("1.160 in"), frac(("3.000 in"), "2")) = "1.160 in")$], "Effective width: B_e/2 not more than B_b/4, the branch being at 90 degrees", "AISC 360-22 Table K5.1")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(l_e = "2" H_b + "2" B_e = "2" ("2.000 in") + "2" ("1.160 in") = "6.320 in")$], "Effective weld length", "AISC 360-22 Eq. K5-5; AISC 360-22 §K5")
#calcline([$display(S_"ip" = frac(H_b^("2"), "3") + B_e H_b = frac(("2.000 in")^("2"), "3") + ("1.160 in") ("2.000 in") = "3.653 in"^2)$], "Effective section modulus of the weld as a line, in-plane bending: a load along the rail", "AISC 360-22 Eq. K5-6; Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#calcline([$display(S_"op" = H_b B_b + frac(B_b^("2"), "3") - frac((B_b - B_e)^("3"), "3" B_b) = ("2.000 in") ("3.000 in") + frac(("3.000 in")^("2"), "3") - frac((("3.000 in") - ("1.160 in"))^("3"), "3" ("3.000 in")) = "8.308 in"^2)$], "Effective section modulus of the weld as a line, out-of-plane bending: a load across the guard", "AISC 360-22 Eq. K5-7; Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#calcline([$B_"b" = "3.000 in" = B = "3.000 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Fillet model kept"*], "Post as wide as the rail: At equal widths the side welds of a rectangular branch land on the chord's rounded corner and are flare-bevel welds; the fillet model of the entered size all around is kept.", "Engineering judgement (EOR): fillet model kept at equal widths")
#subhead("Eccentricity")
#calcline([$d_"rail" = "2.000 in"$], "HSS3X2X1/8: outside dimension in the vertical direction, the rail depth", "AISC Shapes Database v16.0")
#calcline([$display(e = frac(d_"rail", "2") = frac(("2.000 in"), "2") = "1.000 in")$], "Eccentricity: rail centerline to the weld plane at the rail underside", "Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#subhead("Fillet size limits")
#calcline([$t_"rail,nom" = "0.1250 in"$], "Top rail nominal wall thickness, HSS3X2X1/8", "AISC Shapes Database v16.0")
#calcline([$t_"post,nom" = "0.1250 in"$], "Post nominal wall thickness, HSS3X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(t_"min" = "min"(t_"rail,nom", t_"post,nom") = "min"(("0.1250 in"), ("0.1250 in")) = "0.1250 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w_"min" = "0.1250 in"$], "Minimum fillet size for the thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w = "0.1250 in" >= w_"min" = "0.1250 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"OK"*], "Minimum size", "AISC 360-22 Table J2.4")
#calcline([$"Maximum fillet size"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not applicable"*], "Maximum fillet size along edges of material does not apply: this weld is a T-joint, not a weld along an edge. No maximum size is checked.", "AISC 360-22 §J2.2b(b); Engineering judgement (EOR): no maximum fillet size at a T-joint")
#subhead("Weld metal")
#calcline([$F_"EXX" = "70.00 ksi"$], "Electrode classification strength, E70XX", "AISC 360-22 §J2.6; AWS A5.1")
#calcline([$display(F_"nw" = "0.6" F_"EXX" = "0.6" ("70.00 ksi") = "42.00 ksi")$], "Nominal stress of the weld metal", "AISC 360-22 Table J2.5")
#calcline([$Omega_w = "2.000"$], "Safety factor, fillet weld (ASD)", "AISC 360-22 Table J2.5")
#calcline([$k_"ds" = "1.000"$], "No directional increase at the rail to post weld (a branch-to-chord joint)", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld")
#subhead("Base metal: rail fusion face")
#calcline([$F_u = "58.00 ksi"$], "Tensile strength, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"rail" = "0.1160 in"$], "Top rail design wall thickness, HSS3X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM") = "0.6" F_u t_"rail" = "0.6" ("58.00 ksi") ("0.1160 in") = "4,037 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM"), Omega_"BM") = frac(("4,037 lb/in"), "2.000") = "2,018 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$"Rail wall, normal force"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not checked"*], "Rail wall, force normal to the wall: the chord limit states of a rectangular chord (AISC 360-22 Chapter K and §J10) are not computed; not checked (stated assumption). The rail is held to the Chapter K limits of applicability.", "Engineering judgement (EOR): a rectangular chord's limit states not checked")
#calcline([$"Post wall at the weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Covered by Check 5"*], "Post wall at the weld: covered by Check 5. The wall carries the weld force as stress along the post axis, the same demand as Check 5 at its critical section; member shear is not checked (stated assumption).", "Engineering judgement (EOR): post wall at the weld covered by Check 5")
#subhead("Demand: longitudinal, distributed load")
#calcline([$D_"rail" = "23.40 lb"$], "Top rail dead load at the weld: w_D over the span (the tributary length)", "Loading")
#calcline([$display(P = "1.0" D_"rail" = "1.0" ("23.40 lb") = "23.40 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (longitudinal), on the rail at the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("300.0 lb") = "300.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V e = ("300.0 lb") ("1.000 in") = "300.0 lb-in")$], "Moment at the weld plane: V at the rail centerline, arm e", "Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#calcline([$display(f_a = frac(P, l_e) = frac(("23.40 lb"), ("6.320 in")) = "3.703 lb/in")$], "Axial force per inch of weld, compression, uniform over the effective weld length", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_"ip") = frac(("300.0 lb-in"), ("3.653 in"^2)) = "82.12 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("3.703 lb/in") + ("82.12 lb/in") = "85.82 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("3.703 lb/in") - ("82.12 lb/in")) = "78.41 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "85.82 lb/in" >= f_(n,"t") = "78.41 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "85.82 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, l_e) = frac(("300.0 lb"), ("6.320 in")) = "47.47 lb/in")$], "Shear per inch of weld, taken as uniform over the effective weld length", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("85.82 lb/in")^("2") + ("47.47 lb/in")^("2")) = "98.07 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("98.07 lb/in"), ("1,856 lb/in")) = "0.05")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM"), Omega_"BM")) = frac(("47.47 lb/in"), ("2,018 lb/in")) = "0.02")$], "Rail fusion face: in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.05284", "0.02352") = "0.05")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.05 <= 1.00$ #h(10pt) #"OK"])

= Check 4a: Intermediate rail

#"Controlled by Checks 1 and 2 by observation: same section, grade and span as the top rail; component load P_c = 50.00 lb ≤ concentrated guard load P = 200.0 lb. See Checks 1 and 2 for the result."

= Check 4b: Intermediate rail weld to post

== Envelope summary

Both directions of the component load are computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), strong("Downward"), strong("Component"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)"), strong("—\nshear only"), strong("9.763 lb/in"), strong("9.763 lb/in"), strong("Weld 1,856 lb/in\nBase 2,018 lb/in"), strong("0.01"), strong("Controls"), "Horizontal", "Component", "1.0D vertical, 1.0L horizontal, vector sum\nASCE 7-22 §2.4.1, Comb. 2", "—\nshear only", "8.125 lb/in", "8.125 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.00", "")]

#heading(level: 2, "Controlling case: Downward, component (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5))")

#calcline([$"Same section as the top rail"$ #h(6pt) $arrow.r$ #h(6pt) *#"Computed in full"*], "A joint with a rectangular member runs the full Check 4b: the effective weld length of AISC 360-22 Table K5.1 depends on the chord wall, so the comparison with Check 3 is no longer true by inspection.", "Engineering judgement (EOR): Check 4b computed in full at a joint with a rectangular member")
#subhead("Weld properties")
#calcline([$B = "3.000 in"$], "HSS3X2X1/8: width of the chord face, the post's dimension perpendicular to the rail", "AISC Shapes Database v16.0")
#calcline([$t = "0.1160 in"$], "Post design wall thickness, the chord", "AISC Shapes Database v16.0")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$H_b = "2.000 in"$], "HSS3X2X1/8: branch dimension along the chord, the intermediate rail's vertical dimension", "AISC Shapes Database v16.0")
#calcline([$B_b = "3.000 in"$], "Branch width across the chord face, the intermediate rail's horizontal dimension", "AISC Shapes Database v16.0")
#calcline([$t_b = "0.1160 in"$], "Intermediate rail design wall thickness, the branch", "AISC Shapes Database v16.0")
#calcline([$F_"yb" = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$display(B_("e,K1") = frac("10", frac(B, t)) frac(F_y t, F_"yb" t_b) B_b = frac("10", frac(("3.000 in"), ("0.1160 in"))) dot frac(("46.00 ksi") ("0.1160 in"), ("46.00 ksi") ("0.1160 in")) ("3.000 in") = "1.160 in")$], "Effective width of the branch across the chord face", "AISC 360-22 Eq. K1-1")
#calcline([$display(B_e = "min"(B_("e,K1"), frac(B_b, "2")) = "min"(("1.160 in"), frac(("3.000 in"), "2")) = "1.160 in")$], "Effective width: B_e/2 not more than B_b/4, the branch being at 90 degrees", "AISC 360-22 Table K5.1")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(l_e = "2" H_b + "2" B_e = "2" ("2.000 in") + "2" ("1.160 in") = "6.320 in")$], "Effective weld length", "AISC 360-22 Eq. K5-5; AISC 360-22 §K5")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#calcline([$B_"b" = "3.000 in" = B = "3.000 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Fillet model kept"*], "Intermediate rail as wide as the post: At equal widths the side welds of a rectangular branch land on the chord's rounded corner and are flare-bevel welds; the fillet model of the entered size all around is kept.", "Engineering judgement (EOR): fillet model kept at equal widths")
#subhead("Connection model")
#calcline([$"Intermediate rail to post weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Simple shear connection"*], "Simple shear connection consistent with the simple-span member assumption; no end moment at the weld.", "Engineering judgement (EOR): intermediate rail to post weld as a simple shear connection; Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post")
#subhead("Fillet size limits")
#calcline([$t_"int,nom" = "0.1250 in"$], "Intermediate rail nominal wall thickness, HSS3X2X1/8", "AISC Shapes Database v16.0")
#calcline([$t_"post,nom" = "0.1250 in"$], "Post nominal wall thickness, HSS3X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(t_"min" = "min"(t_"int,nom", t_"post,nom") = "min"(("0.1250 in"), ("0.1250 in")) = "0.1250 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
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
#calcline([$t_"post" = "0.1160 in"$], "Post design wall thickness, HSS3X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM,post") = "0.6" F_u t_"post" = "0.6" ("58.00 ksi") ("0.1160 in") = "4,037 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM,post"), Omega_"BM") = frac(("4,037 lb/in"), "2.000") = "2,018 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#subhead("Base metal: intermediate rail wall fusion face (branch)")
#calcline([$F_u = "58.00 ksi"$], "Tensile strength, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"int" = "0.1160 in"$], "Intermediate rail design wall thickness, HSS3X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM,int") = "0.6" F_u t_"int" = "0.6" ("58.00 ksi") ("0.1160 in") = "4,037 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM,int"), Omega_"BM") = frac(("4,037 lb/in"), "2.000") = "2,018 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$frac(R_(n,"BM,int"), Omega_"BM") = "2,018 lb/in" = frac(R_(n,"BM,post"), Omega_"BM") = "2,018 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Post wall governs"*], "Base metal is checked at the fusion face of both connected parts, the post wall (the chord) and the intermediate rail wall (the branch), each in shear rupture against the in-plane shear per inch; the lower allowable governs.", "Engineering judgement (EOR): Check 4b base metal on both walls, lower governs")
#calcline([$"Post wall, chord limit states"$ #h(6pt) $arrow.r$ #h(6pt) *#"No demand"*], "Chapter K chord limit states: the intermediate rail delivers no axial force or moment to the post wall (simple shear connection); the post wall's in-plane shear is checked by the base metal line above.", "Engineering judgement (EOR): no chord limit state demand at the intermediate rail")
#subhead("Demand: downward, component load")
#calcline([$w_(D,"int") = "0.3250 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$display(R_D = frac(w_(D,"int") L, "2") = frac(("0.3250 lb/in") ("72.00 in"), "2") = "11.70 lb")$], "Dead-load end reaction at the post", "AISC Manual Table 3-23, Case 1")
#calcline([$P_c = "50.00 lb"$], "Component load adjacent to the post: the full P_c to this end", "Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post")
#calcline([$display(R = "1.0" R_D + "1.0" P_c = "1.0" ("11.70 lb") + "1.0" ("50.00 lb") = "61.70 lb")$], "Weld reaction: dead and component loads in the same (vertical) direction, in the plane of the weld", "Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(f_v = frac(R, l_e) = frac(("61.70 lb"), ("6.320 in")) = "9.763 lb/in")$], "Shear per inch of weld, taken as uniform over the effective weld length", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = f_v = "9.763 lb/in")$], "Resultant per inch: shear only, no axial force and no moment", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("9.763 lb/in"), ("1,856 lb/in")) = "0.01")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM,post"), Omega_"BM")) = frac(("9.763 lb/in"), ("2,018 lb/in")) = "0.00")$], "Base metal, post wall fusion face (governs): in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.005260", "0.004837") = "0.01")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.01 <= 1.00$ #h(10pt) #"OK"])

= Check 5: Post combined axial and flexure

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Axial* $P_r$ \ capacity $P_c$ or $P_t$], [*Moment* $M_r$ \ capacity $M_c$], [*Equation*], [$frac(alpha P_r, P_e)$], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "260.3 lb comp.\nPc = 13,120 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.02", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "360.3 lb comp.\nPc = 13,120 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.03", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "60.29 lb comp.\nPc = 13,120 lb", "8,300 lb-in\nMc = 29,200 lb-in\nabout x", "Eq. H1-1b", "0.002017", "0.29", "", "Outward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "60.29 lb comp.\nPc = 13,120 lb", "12,450 lb-in\nMc = 29,200 lb-in\nabout x", "Eq. H1-1b", "0.002017", "0.43", "", "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "60.29 lb comp.\nPc = 13,120 lb", "8,300 lb-in\nMc = 29,200 lb-in\nabout x", "Eq. H1-1b", "0.002017", "0.29", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "60.29 lb comp.\nPc = 13,120 lb", "12,450 lb-in\nMc = 29,200 lb-in\nabout x", "Eq. H1-1b", "0.002017", "0.43", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "163.8 lb tension\nPt = 29,470 lb", "—", "Pr/Pt\n(Eq. D2-1)", "—", "0.01", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "263.8 lb tension\nPt = 29,470 lb", "—", "Pr/Pt\n(Eq. D2-1)", "—", "0.01", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "60.29 lb comp.\nPc = 13,120 lb", "8,300 lb-in\nMc = 22,120 lb-in\nabout y", "Eq. H1-1b", "0.003789", "0.38", "", strong("Longitudinal"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("60.29 lb comp.\nPc = 13,120 lb"), strong("12,450 lb-in\nMc = 22,120 lb-in\nabout y"), strong("Eq. H1-1b"), strong("0.003789"), strong("0.57"), strong("Controls"))]

#heading(level: 2, "Controlling case: Longitudinal, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Capacity")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$display(lambda_"pf" = "1.12" sqrt(frac(E, F_y)) = "1.12" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "28.12")$], "Compact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"rf" = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "35.15")$], "Noncompact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"pw" = "2.42" sqrt(frac(E, F_y)) = "2.42" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "60.76")$], "Compact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$display(lambda_"rw" = "5.7" sqrt(frac(E, F_y)) = "5.7" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "143.1")$], "Noncompact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$Z_y = "0.8030 in"^3$], "Plastic section modulus about the y axis", "AISC Shapes Database v16.0")
#calcline([$display(M_"py" = F_y Z_y = ("46.00 ksi") ("0.8030 in"^3) = "36,940 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "22.90"$], "Flange slenderness about the y axis: h/t of the 3.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_f = 22.9 <= lambda_"pf" = 28.12$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact flange: flange local buckling does not apply"*], "Flange classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$lambda_w = "14.20"$], "Web slenderness about the y axis: b/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_w = 14.2 <= lambda_"pw" = 60.76$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$"Bending about the minor axis"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "", "AISC 360-22 §F7.4, User Note")
#calcline([$display(M_"ny" = M_"py" = "36,940 lb-in")$], "Nominal flexural strength about the y axis: yielding", "AISC 360-22 §F7")
#calcline([$display(M_"cy" = frac(M_"ny", Omega_b) = frac(("36,940 lb-in"), "1.670") = "22,120 lb-in")$], "Allowable flexural strength about the y axis", "AISC 360-22 Eq. B3-2")
#calcline([$display(lambda_(r,c) = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "35.15")$], "Slender limit, walls of rectangular HSS in compression", "AISC 360-22 Table B4.1a, Case 6")
#calcline([$lambda_b = "14.20"$], "Wall slenderness: b/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_b = 14.2 <= lambda_(r,c) = 35.15$ #h(6pt) $arrow.r$ #h(6pt) *#"Nonslender"*], "Wall classification, compression: no noncompact category", "AISC 360-22 §B4.1a")
#calcline([$lambda_h = "22.90"$], "Wall slenderness: h/t of the 3.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_h = 22.9 <= lambda_(r,c) = 35.15$ #h(6pt) $arrow.r$ #h(6pt) *#"Nonslender"*], "Wall classification, compression: no noncompact category", "AISC 360-22 §B4.1a")
#calcline([$K = "2.100"$], "Effective length factor, fixed-free (recommended design value)", "AISC 360-22 Comm. Table C-A-7.1, case (e)")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$display(L_c = K h = "2.100" ("42.00 in") = "88.20 in")$], "Effective length, with the unbraced length taken as the post height h", "AISC 360-22 §E2; Engineering judgement (EOR): unbraced length is the post height")
#calcline([$r_y = "0.8040 in"$], "Radius of gyration: the smaller, about the y axis, in every case", "AISC Shapes Database v16.0")
#calcline([$display(frac(L_c, r) = frac(L_c, r_y) = frac(("88.20 in"), ("0.8040 in")) = "109.7")$], "Effective slenderness ratio", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 109.7 <= 200$ #h(6pt) $arrow.r$ #h(6pt) *#"Within the recommended limit"*], "For members designed on the basis of compression, the effective slenderness ratio Lc/r preferably should not exceed 200.", "AISC 360-22 §E2, User Note")
#calcline([$display("4.71" sqrt(frac(E, F_y)) = "4.71" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "118.3")$], "Limit between inelastic and elastic buckling", "AISC 360-22 §E3(a), (b)")
#calcline([$display(F_e = frac(pi^("2") E, (frac(L_c, r))^("2")) = frac(pi^("2") ("29,000 ksi"), "109.7"^("2")) = "23.78 ksi")$], "Elastic buckling stress", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 109.7 <= 118.3$ #h(6pt) $arrow.r$ #h(6pt) *#"Inelastic buckling: Eq. E3-2"*], "", "AISC 360-22 §E3(a), (b)")
#calcline([$display(frac(F_y, F_e) = frac(("46.00 ksi"), ("23.78 ksi")) = "1.934")$], "Exponent in Eq. E3-2", "AISC 360-22 Eq. E3-2")
#calcline([$display(F_"cr" = "0.658"^(frac(F_y, F_e)) F_y = "0.658"^("1.934") ("46.00 ksi") = "20.47 ksi")$], "Critical stress", "AISC 360-22 Eq. E3-2")
#calcline([$A_g = "1.070 in"^2$], "Gross area", "AISC Shapes Database v16.0")
#calcline([$display(P_n = F_"cr" A_g = ("20.47 ksi") ("1.070 in"^2) = "21,910 lb")$], "Nominal compressive strength", "AISC 360-22 Eq. E3-1")
#calcline([$Omega_c = "1.670"$], "Safety factor for compression (ASD)", "AISC 360-22 §E1")
#calcline([$display(P_c = frac(P_n, Omega_c) = frac(("21,910 lb"), "1.670") = "13,120 lb")$], "Allowable compressive strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: longitudinal, distributed load")
#calcline([$P_D = "60.29 lb"$], "D at the post: axial dead load", "Loading")
#calcline([$display(P_r = "1.0" P_D = "1.0" ("60.29 lb") = "60.29 lb")$], "Required axial strength: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (longitudinal) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p (critical section at the top of the baseplate)", "Loading")
#calcline([$display(M_L = V_L L_"post" = ("300.0 lb") ("41.50 in") = "12,450 lb-in")$], "Live-load moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(M_r = "1.0" M_L = "1.0" ("12,450 lb-in") = "12,450 lb-in")$], "Required flexural strength", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$I_y = "0.6920 in"^4$], "Moment of inertia about the y axis, which this case bends", "AISC Shapes Database v16.0")
#calcline([$display(P_e = frac(pi^("2") E I_y, L_c^("2")) = frac(pi^("2") ("29,000 ksi") ("0.6920 in"^4), ("88.20 in")^("2")) = "25,460 lb")$], "Elastic critical buckling load, at the compression Lc", "AISC 360-22 Eq. A-8-5; Engineering judgement (EOR): Pe at Lc = 2.1h")
#calcline([$display(frac(alpha P_r, P_e) = frac("1.6" P_r, P_e) = frac("1.6" ("60.29 lb"), ("25,460 lb")) = "0.003789")$], "Second-order ratio", "AISC 360-22 App. 8")
#calcline([$frac(alpha P_r, P_e) <= 0.05$ #h(6pt) $arrow.r$ #h(6pt) *#"Second-order effects negligible: αPr/Pe = 0.003789; amplification taken as 1.0."*], "", "Engineering judgement (EOR): second-order limit")
#calcline([$display(frac(P_r, P_c) = frac(("60.29 lb"), ("13,120 lb")) = "0.004596")$], "Axial ratio, selects the interaction equation", "AISC 360-22 §H1.1")
#calcline([$frac(P_r, P_c) = 0.004596 < 0.2$ #h(6pt) $arrow.r$ #h(6pt) *#"Eq. H1-1b"*], "", "AISC 360-22 §H1.1")
#calcline([$display("Ratio" = frac(P_r, "2" P_c) + frac(M_r, M_"cy") = frac(("60.29 lb"), "2" ("13,120 lb")) + frac(("12,450 lb-in"), ("22,120 lb-in")) = "0.57")$], "Combined axial and flexure", "AISC 360-22 Eq. H1-1b")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.57 <= 1.00$ #h(10pt) #"OK"])

= Check 6: Post deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), "Downward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Outward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.1264 in", "0.6917 in", "0.18", "", "Outward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.1896 in", "0.6917 in", "0.27", "", "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.1264 in", "0.6917 in", "0.18", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.1896 in", "0.6917 in", "0.27", "", "Upward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Longitudinal", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.2374 in", "0.6917 in", "0.34", "", strong("Longitudinal"), strong("Distributed"), strong("1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only"), strong("0.3562 in"), strong("0.6917 in"), strong("0.51"), strong("Controls"))

#heading(level: 2, "Controlling case: Longitudinal, distributed (1.0L, horizontal; Engineering judgement (EOR): serviceability, live load only)")

#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p", "Loading")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_y = "0.6920 in"^4$], "Moment of inertia about the y axis, which this case bends", "AISC Shapes Database v16.0")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (longitudinal) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(Delta_L = frac(V_L L_"post"^("3"), "3" E I_y) = frac(("300.0 lb") ("41.50 in")^("3"), "3" ("29,000 ksi") ("0.6920 in"^4)) = "0.3562 in")$], "Live-load deflection at the top of the post", "AISC Manual Table 3-23, Case 22")
#calcline([$display(Delta = "1.0" Delta_L = "1.0" ("0.3562 in") = "0.3562 in")$], "Live load only; dead load acts axially", "Engineering judgement (EOR): serviceability, live load only")
#calcline([$display(Delta_"allow" = frac(L_"post", "60") = frac(("41.50 in"), "60") = "0.6917 in")$], "Limit (h - t_p)/60", "Engineering judgement (EOR): post deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.3562 in"), ("0.6917 in")) = "0.51")$], "Deflection / limit", "Engineering judgement (EOR): post deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.51 <= 1.00$ #h(10pt) #"OK"])

= Check 7: Post weld to baseplate

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "84.73 lb/in\nuniform", "—", "84.73 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.03", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "117.3 lb/in\nuniform", "—", "117.3 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.04", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "1,821 lb/in\ncompression side", "65.10 lb/in", "1,822 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.65", "", "Outward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,721 lb/in\ncompression side", "97.66 lb/in", "2,723 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.98", "", "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "1,821 lb/in\ncompression side", "65.10 lb/in", "1,822 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.65", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,721 lb/in\ncompression side", "97.66 lb/in", "2,723 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.98", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "53.33 lb/in\nuniform", "—", "53.33 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.02", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "85.88 lb/in\nuniform", "—", "85.88 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "0.03", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "10,570 lb/in\ncompression side", "65.10 lb/in", "10,570 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in", "3.80", "", strong("Longitudinal"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("15,850 lb/in\ncompression side"), strong("97.66 lb/in"), strong("15,850 lb/in"), strong("Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 3,195 lb/in"), strong("5.69"), strong("Controls"))]

#heading(level: 2, "Controlling case: Longitudinal, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$a_"face" = "2.000 in"$], "HSS3X2X1/8: outside width of each welded face, the faces parallel to the rail", "AISC Shapes Database v16.0")
#calcline([$d_"faces" = "3.000 in"$], "Distance between the two weld lines: the post's outside dimension perpendicular to the rail", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1160 in"$], "Design wall thickness, HSS3X2X1/8: it sets the outside corner radius", "AISC Shapes Database v16.0")
#calcline([$display(R_o = "2" t_"des" = "2" ("0.1160 in") = "0.2320 in")$], "Outside corner radius", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$w = "0.1875 in"$], "Fillet weld leg size, each welded face (3/16 as entered)", "Input")
#calcline([$display(l_w = a_"face" - "2" R_o = ("2.000 in") - "2" ("0.2320 in") = "1.536 in")$], "Length of each weld line: the flat of its face, between the tangent points", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(L_w = "2" l_w = "2" ("1.536 in") = "3.072 in")$], "Weld length: the two lines", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(S_("w,t") = l_w d_"faces" = ("1.536 in") ("3.000 in") = "4.608 in"^2)$], "Section modulus of the weld lines, a load across the guard: the lines are the extreme fibers", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(S_("w,l") = frac(l_w^("2"), "3") = frac(("1.536 in")^("2"), "3") = "0.7864 in"^2)$], "Section modulus of the weld lines, a load along the rail: each line bends about its own middle", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1875 in") = "0.1326 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Moment arm")
#calcline([$L_"post" = "41.50 in"$], "Moment arm, h - t_p: guard load at the top rail centerline, weld at the top of the baseplate", "Loading")
#subhead("Fillet size limits")
#calcline([$t_"post,nom" = "0.1250 in"$], "Post nominal wall thickness, HSS3X2X1/8", "AISC Shapes Database v16.0")
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
#calcline([$t_"wall" = "0.1160 in"$], "Post design wall thickness, HSS3X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(R_("n,y") = F_y t_"wall" = ("46.00 ksi") ("0.1160 in") = "5,336 lb/in")$], "Yielding of the wall under the force along the post axis, per inch of weld", "AISC 360-22 Eq. J4-1")
#calcline([$Omega_y = "1.670"$], "Safety factor, yielding (ASD)", "AISC 360-22 §J4.1(a)")
#calcline([$display(R_("n,u") = F_u t_"wall" = ("58.00 ksi") ("0.1160 in") = "6,728 lb/in")$], "Rupture of the wall under the force along the post axis, per inch of weld", "AISC 360-22 Eq. J4-2")
#calcline([$Omega_u = "2.000"$], "Safety factor, rupture (ASD)", "AISC 360-22 §J4.1(b)")
#calcline([$display(R_("wall,a") = "min"(frac(R_("n,y"), Omega_y), frac(R_("n,u"), Omega_u)) = "min"(frac(("5,336 lb/in"), "1.670"), frac(("6,728 lb/in"), "2.000")) = "3,195 lb/in")$], "Allowable force along the post axis per inch: the lower of yielding and rupture", "AISC 360-22 Eq. B3-2")
#calcline([$display(R_("n,v") = "0.6" F_u t_"wall" = "0.6" ("58.00 ksi") ("0.1160 in") = "4,037 lb/in")$], "Shear rupture of the wall under the force along the face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_v = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(R_("wall,f") = frac(R_("n,v"), Omega_v) = frac(("4,037 lb/in"), "2.000") = "2,018 lb/in")$], "Allowable force along the face per inch", "AISC 360-22 Eq. B3-2")
#subhead("Demand: longitudinal, distributed load")
#calcline([$P_D = "60.29 lb"$], "D at the post: axial dead load at the top of the baseplate", "Loading")
#calcline([$display(P = "1.0" P_D = "1.0" ("60.29 lb") = "60.29 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (longitudinal), at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("300.0 lb") = "300.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V L_"post" = ("300.0 lb") ("41.50 in") = "12,450 lb-in")$], "Moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(f_a = frac(P, L_w) = frac(("60.29 lb"), ("3.072 in")) = "19.62 lb/in")$], "Axial force per inch of weld, compression, uniform along the weld lines", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_("w,l")) = frac(("12,450 lb-in"), ("0.7864 in"^2)) = "15,830 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("19.62 lb/in") + ("15,830 lb/in") = "15,850 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("19.62 lb/in") - ("15,830 lb/in")) = "15,810 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "15,850 lb/in" >= f_(n,"t") = "15,810 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "15,850 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, L_w) = frac(("300.0 lb"), ("3.072 in")) = "97.66 lb/in")$], "Shear per inch of weld, taken as uniform along the weld lines", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("15,850 lb/in")^("2") + ("97.66 lb/in")^("2")) = "15,850 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.1326 in") dot "1.000" = "5,568 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("5,568 lb/in"), "2.000") = "2,784 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("15,850 lb/in"), ("2,784 lb/in")) = "5.69")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_r, frac(R_(n,"BM"), Omega_"BM")) = frac(("15,850 lb/in"), ("8,700 lb/in")) = "1.82")$], "Baseplate fusion face: the resultant per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_("wall,a") = frac(f_n, R_("wall,a")) = frac(("15,850 lb/in"), ("3,195 lb/in")) = "4.96")$], "Post wall: force along the post axis / allowable", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_("wall,f") = frac(f_v, R_("wall,f")) = frac(("97.66 lb/in"), ("2,018 lb/in")) = "0.05")$], "Post wall: force along the face / allowable", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"wall" = "max"("Ratio"_("wall,a"), "Ratio"_("wall,f")) = "max"("4.961", "0.04838") = "4.96")$], "Post wall: the larger of the two, not combined", "Engineering judgement (EOR): post wall at a face-pair base weld checked on its own lines")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM", "Ratio"_"wall") = "max"("5.694", "1.822", "4.961") = "5.69")$], "The largest of weld metal, base metal and post wall", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 5.69 > 1.00$ #h(10pt) #"NG"])

= Summary

#table(columns: (1fr, auto, auto, auto, auto, auto), table.header(strong("Check"), strong("Demand"), strong("Capacity"), strong("Ratio"), strong("Controlling direction"), strong("Result")), "1. Top rail bending", "Mry = 3,811 lb-in", "Mcy = 22,120 lb-in", "0.17", "Downward, concentrated", "OK", "2. Top rail deflection", "0.08316 in", "0.6000 in", "0.14", "Downward, concentrated", "OK", "3. Top rail weld to post", "98.07 lb/in", "1,856 lb/in (weld metal)", "0.05", "Longitudinal, distributed", "OK", "4a. Intermediate rail", "", "", "", "", "Controlled by Checks 1 and 2", "4b. Intermediate rail weld to post", "9.763 lb/in", "1,856 lb/in (weld metal)", "0.01", "Downward, component", "OK", "5. Post combined axial and flexure", "Pr = 60.29 lb; Mr = 12,450 lb-in", "Pc = 13,120 lb; Mc = 22,120 lb-in", "0.57", "Longitudinal, distributed", "OK", "6. Post deflection", "0.3562 in", "0.6917 in", "0.51", "Longitudinal, distributed", "OK", "7. Post weld to baseplate", "15,850 lb/in", "2,784 lb/in (weld metal)", "5.69", "Longitudinal, distributed", "NG")

= Anchor reactions

LRFD reactions at the top of concrete, for direct input into anchor software: reporting, not a pass/fail check. Each set is simultaneous: the shear, axial force and moment that occur together.

#text(weight: "bold", "Baseplate: B = 6.000 in (parallel to rail) × N = 8.000 in (perpendicular to rail)")

#subhead("Dead load at the base")
#calcline([$D_"rail" = "23.40 lb"$], "Top rail", "Loading")
#calcline([$D_"int" = "23.40 lb"$], "Intermediate rail", "Loading")
#calcline([$D_"post" = "13.49 lb"$], "Post, over h - t_p", "Loading")
#calcline([$rho = "0.2836 lb/in"^3$], "Steel unit weight", "AISC Manual 16th Ed., Part 17")
#calcline([$B = "6.000 in"$], "Baseplate, parallel to the rail", "Input")
#calcline([$N = "8.000 in"$], "Baseplate, perpendicular to the rail", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(W_"bp" = rho B N t_p = ("0.2836 lb/in"^3) ("6.000 in") ("8.000 in") ("0.5000 in") = "6.806 lb")$], "Baseplate weight: in the reaction sets only, below the critical section of Checks 5 and 7", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$display(D = D_"rail" + D_"int" + D_"post" + W_"bp" = ("23.40 lb") + ("23.40 lb") + ("13.49 lb") + ("6.806 lb") = "67.09 lb")$], "Dead load at the base", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#subhead("Governing guard load type")
#calcline([$P = "200.0 lb"$], "Concentrated guard load P, at the top of the post", "Loading")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$w_L L = "300.0 lb" > P = "200.0 lb"$ #h(6pt) $arrow.r$ #h(6pt) *#"Distributed load governs"*], "The larger at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Lateral set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "480.0 lb", "−60.38 lb (compression)", "20,160 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D axial, 1.6L horizontal; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "23.40 lb", "D, intermediate rail", "23.40 lb", "D, post", "13.49 lb", "D, baseplate", "6.806 lb", strong("D, total"), strong("67.09 lb"))

#"V and M act in the same vertical plane; M = V·h."

#"Lateral set applies in any horizontal direction; enter it in the anchor software in the orientation that governs the anchor pattern. Loads can reverse."

#subhead("Demand: lateral, distributed load")
#calcline([$D = "67.09 lb"$], "Dead load at the base", "Reactions")
#calcline([$display(abs(N_u) = "0.9" D = "0.9" ("67.09 lb") = "60.38 lb")$], "Axial force at the base: dead load, compression", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal at the top of the post, in any horizontal direction", "Stated assumption: the tributary length is the span")
#calcline([$display(V_u = "1.6" V_L = "1.6" ("300.0 lb") = "480.0 lb")$], "Base shear", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$h = "42.00 in"$], "Moment arm: top rail centerline to top of concrete", "Input")
#calcline([$display(M_u = V_u h = ("480.0 lb") ("42.00 in") = "20,160 lb-in")$], "Base moment at the top of concrete: V_u at the top rail centerline, arm h", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Upward set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "0 lb", "+419.6 lb (tension)", "0 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D + 1.6L, net axial; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "23.40 lb", "D, intermediate rail", "23.40 lb", "D, post", "13.49 lb", "D, baseplate", "6.806 lb", strong("D, total"), strong("67.09 lb"))

#subhead("Demand: upward, distributed load")
#calcline([$D = "67.09 lb"$], "Dead load at the base", "Reactions")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(P_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, upward at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(abs(N_u) = "1.6" P_L - "0.9" D = "1.6" ("300.0 lb") - "0.9" ("67.09 lb") = "419.6 lb")$], "Axial force at the base: net tension (uplift), guard load opposing dead load", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
