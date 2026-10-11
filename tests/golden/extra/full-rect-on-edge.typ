
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
+ #"The rail to post weld is modeled as a flat line at the underside of the rail, with eccentricity e = half the rail depth from the rail centerline: the post's own outline (a ring of its perimeter for a round post, its rounded rectangle for a rectangular post under a round rail), or, where post and rail are both rectangular, the effective weld of AISC 360-22 Table K5.1. For a round member the saddle of the cope is ignored, which is conservative (the saddle centroid is at 2R/π for equal round diameters). It is modeled as a fillet of the entered size all around, although at equal widths the sides form a flare-bevel joint."
+ #"The intermediate rail to post weld is modeled the same way at the post face, on the intermediate rail's outline or, where both are rectangular, the effective weld of Table K5.1. It is a simple shear connection consistent with the simple-span intermediate rail: the end reaction acts at the weld with no end moment. It is modeled as a fillet of the entered size all around, although at equal widths the sides form a flare-bevel joint."
+ #"Local strength of the rail wall at the post (AISC 360-22 Chapter K and §J10 chord limit states) is checked for a round post on a round rail. It is not checked where the rail is rectangular or where a round and a rectangular member meet; the rail is then held to the Chapter K limits of applicability."
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

#table(columns: (auto, 1fr, auto), table.header(strong("Entry"), strong("Citation"), strong("Source")), "material.grades.hss_rect", "AISC Manual Table 2-4", "memory", "aisc360.K1.3.rect_chord.wall_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "material.A500_GrB.hss_rect.Fy", "AISC Manual Table 2-4", "memory", "material.A500_GrB.hss_rect.Fu", "AISC Manual Table 2-4", "memory", "ej.weld.post_wall.fu_fy_min", "Engineering judgement (EOR): post wall at the weld covered by Check 5 while Fu/Fy >= 1.20", "engineer", "aisc360.K1.3.Fy_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "aisc360.K1.3.Fy_Fu_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "asce7.guard.component", "ASCE 7-22 §4.5.1.2", "memory", "ej.post.axial_dead_load", "Engineering judgement (EOR): post dead load", "engineer", "ej.section.orientation.rail_vertical", "Engineering judgement (EOR): a rectangular member's axes follow from its long side", "engineer", "ej.section.orientation.post_perpendicular", "Engineering judgement (EOR): a rectangular member's axes follow from its long side", "engineer", "aisc360.B4.1b.rect_hss.flange.lambda_p", "AISC 360-22 Table B4.1b, Case 17", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.flange.lambda_r", "AISC 360-22 Table B4.1b, Case 17", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.web.lambda_p", "AISC 360-22 Table B4.1b, Case 19", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.web.lambda_r", "AISC 360-22 Table B4.1b, Case 19", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-1", "AISC 360-22 Eq. F7-1", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.compact_no_local_buckling", "AISC 360-22 §F7.2(a), §F7.3(a)", "AISC 360-22 text, read 2026-10-11", "ej.flexure.unbraced_length", "Engineering judgement (EOR): unbraced length for lateral-torsional buckling", "engineer", "aisc360.eq.F7-10.coeff", "AISC 360-22 Eq. F7-10", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-10", "AISC 360-22 Eq. F7-10", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-11.coeff", "AISC 360-22 Eq. F7-11", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.4.inelastic_coeff", "AISC 360-22 §F7.4", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-11", "AISC 360-22 Eq. F7-11", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-8", "AISC 360-22 Eq. F7-8", "AISC 360-22 text, read 2026-10-11", "aisc_manual.t3-23.case1.Mx", "AISC Manual Table 3-23, Case 1", "memory", "aisc_manual.t3-23.case7.Mx", "AISC Manual Table 3-23, Case 7", "memory", "aisc360.eq.F1-1.coeff_numerator", "AISC 360-22 Eq. F1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F1-1.coeff_max", "AISC 360-22 Eq. F1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F1-1.coeff_quarter", "AISC 360-22 Eq. F1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F1-1.coeff_center", "AISC 360-22 Eq. F1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F1-1", "AISC 360-22 Eq. F1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.nominal_strength", "AISC 360-22 §F7", "AISC 360-22 text, read 2026-10-11", "ej.bending.biaxial_rect", "Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "engineer", "aisc360.eq.F7-2", "AISC 360-22 Eq. F7-2", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.4.no_ltb_note", "AISC 360-22 §F7.4, User Note", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.H1-1b", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.K1-1.coeff", "AISC 360-22 Eq. K1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.K1-1", "AISC 360-22 Eq. K1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.K5.1.Be_cap", "AISC 360-22 Table K5.1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.K5-5", "AISC 360-22 Eq. K5-5", "AISC 360-22 text, read 2026-10-11", "aisc360.K5.nonuniform", "AISC 360-22 §K5", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.K5-6", "AISC 360-22 Eq. K5-6", "AISC 360-22 text, read 2026-10-11", "ej.weld.k5.case_mapping", "Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties", "engineer", "aisc360.eq.K5-7", "AISC 360-22 Eq. K5-7", "AISC 360-22 text, read 2026-10-11", "aisc360.J2.2a.throat.coeff", "AISC 360-22 §J2.2a", "memory", "aisc360.J2.2a.throat", "AISC 360-22 §J2.2a", "memory", "ej.weld.equal_width_fillet", "Engineering judgement (EOR): fillet model kept at equal widths", "engineer", "aisc360.J2.4.min_size", "AISC 360-22 Table J2.4", "memory", "ej.weld.max_size_not_applicable", "Engineering judgement (EOR): no maximum fillet size at a T-joint", "engineer", "aisc360.J2.2b.max_size_edges", "AISC 360-22 §J2.2b(b)", "memory", "material.E70XX.FEXX", "AISC 360-22 §J2.6; AWS A5.1", "memory", "aisc360.J2.5.fnw.coeff", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.fnw", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.omega_w", "AISC 360-22 Table J2.5", "memory", "ej.weld.branch_kds", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld", "engineer", "aisc360.eq.J4-4.coeff", "AISC 360-22 Eq. J4-4", "memory", "aisc360.eq.J4-4", "AISC 360-22 Eq. J4-4", "memory", "aisc_manual.part9.base_metal", "AISC Manual Part 9, base metal at welds", "memory", "aisc360.J4.2.omega_rupture", "AISC 360-22 §J4.2(b)", "memory", "ej.weld.chord_wall.rect", "Engineering judgement (EOR): a rectangular chord's limit states not checked", "engineer", "ej.weld.post_wall_covered", "Engineering judgement (EOR): post wall at the weld covered by Check 5", "engineer", "aws.d1_1.thickness_min", "AWS D1.1/D1.1M:2020, Clause 1", "memory", "ej.weld.line_method", "Engineering judgement (EOR): elastic weld as a line", "engineer", "ej.weld.no_bearing", "Engineering judgement (EOR): no bearing credit at the weld", "engineer", "aisc360.J2.4.fillet_strength", "AISC 360-22 Eq. J2-4", "memory", "ej.component.downward", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "engineer", "ej.component.midspan", "Engineering judgement (EOR): component load as a point load at midspan", "engineer", "ej.weld.intermediate_simple_shear", "Engineering judgement (EOR): intermediate rail to post weld as a simple shear connection", "engineer", "ej.weld.intermediate_line_model", "Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post", "engineer", "ej.weld.intermediate_base_metal", "Engineering judgement (EOR): Check 4b base metal on both walls, lower governs", "engineer", "ej.weld.check4b.no_chord_demand", "Engineering judgement (EOR): no chord limit state demand at the intermediate rail", "engineer", "aisc_manual.t3-23.case1.R", "AISC Manual Table 3-23, Case 1", "memory", "aisc360.B4.1a.rect_hss.lambda_r", "AISC 360-22 Table B4.1a, Case 6", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1a.classification", "AISC 360-22 §B4.1a", "memory", "aisc360.CA7.K_fixed_free", "AISC 360-22 Comm. Table C-A-7.1, case (e)", "memory", "aisc360.E2.effective_length", "AISC 360-22 §E2", "memory", "ej.post.unbraced_length", "Engineering judgement (EOR): unbraced length is the post height", "engineer", "aisc360.eq.E3-4", "AISC 360-22 Eq. E3-4", "memory", "aisc360.E2.user_note.slenderness", "AISC 360-22 §E2, User Note", "memory", "aisc360.E2.user_note.slenderness.limit", "AISC 360-22 §E2, User Note", "memory", "aisc360.E3.branch_limit", "AISC 360-22 §E3(a), (b)", "memory", "aisc360.eq.E3-3", "AISC 360-22 Eq. E3-3", "memory", "aisc360.eq.E3-3.coeff", "AISC 360-22 Eq. E3-3", "memory", "aisc360.eq.E3-1", "AISC 360-22 Eq. E3-1", "memory", "aisc360.E1.omega_c", "AISC 360-22 §E1", "memory", "aisc360.F1.c.cantilever_cb", "AISC 360-22 §F1(c)", "AISC 360-22 text, read 2026-10-11", "aisc_manual.t3-23.case22.M", "AISC Manual Table 3-23, Case 22", "memory", "aisc360.eq.A-8-5", "AISC 360-22 Eq. A-8-5", "memory", "ej.second_order.pe_length", "Engineering judgement (EOR): Pe at Lc = 2.1h", "engineer", "aisc360.app8.alpha_asd", "AISC 360-22 App. 8", "memory", "ej.second_order.limit", "Engineering judgement (EOR): second-order limit", "engineer", "ej.second_order.negligible", "Engineering judgement (EOR): second-order limit", "engineer", "aisc360.H1.1.threshold", "AISC 360-22 §H1.1", "memory", "aisc360.eq.H1-1b.coeff", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.D2-1", "AISC 360-22 Eq. D2-1", "memory", "aisc360.D2.omega_t", "AISC 360-22 §D2(a)", "memory", "aisc_manual.t3-23.case22.delta", "AISC Manual Table 3-23, Case 22", "memory", "ej.deflection.limit.post", "Engineering judgement (EOR): post deflection limit, not code", "engineer", "ej.weld.line.corner_radius_coeff", "Engineering judgement (EOR): weld line on the true rounded rectangle", "engineer", "ej.weld.line.rounded_rectangle", "Engineering judgement (EOR): weld line on the true rounded rectangle", "engineer", "ej.weld.line.face_pair", "Engineering judgement (EOR): weld line on a pair of faces, flats only", "engineer", "aisc360.J2.4.kds_rect_hss", "AISC 360-22 §J2.4(a)(2)", "AISC 360-22 text, read 2026-10-11", "aisc360.K5.user_note.rect_hss_kds", "AISC 360-22 §K5, User Note", "AISC 360-22 text, read 2026-10-11", "material.A36.Fu", "AISC Manual Table 2-5", "memory", "ej.weld.post_wall.face_pair", "Engineering judgement (EOR): post wall at a face-pair base weld checked on its own lines", "engineer", "aisc360.eq.J4-1", "AISC 360-22 Eq. J4-1", "AISC 360-22 text, read 2026-10-11", "aisc360.J4.1.omega_yield", "AISC 360-22 §J4.1(a)", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.J4-2", "AISC 360-22 Eq. J4-2", "AISC 360-22 text, read 2026-10-11", "aisc360.J4.1.omega_rupture", "AISC 360-22 §J4.1(b)", "AISC 360-22 text, read 2026-10-11", "material.steel.density", "AISC Manual 16th Ed., Part 17", "memory", "ej.reaction.location", "Engineering judgement (EOR): reactions at the top of concrete, arm h", "engineer", "ej.combo.reaction", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "engineer", "ej.reaction.lateral_note", "Engineering judgement (EOR): one lateral set, any horizontal direction", "engineer")

= Dimensions

Every dimension as entered, and as the tool read it. A bare number is inches.

#table(columns: (1fr, auto, auto, auto), table.header(strong("Dimension"), strong("As entered"), strong("Read as"), strong("Inches")), "Span, post to post (c/c)", "6'-0\"", "6'-0\"", "72.00 in", "Post height h, top of concrete to top rail centerline", "42", "3'-6\"", "42.00 in", "Baseplate thickness t_p", "1/2", "1/2\"", "0.5000 in", "Baseplate B, parallel to the rail", "6", "6\"", "6.000 in", "Baseplate N, perpendicular to the rail", "8", "8\"", "8.000 in", "Fillet weld, top rail to post", "1/8", "1/8\"", "0.1250 in", "Fillet weld, post to baseplate", "3/16", "3/16\"", "0.1875 in", "Fillet weld, intermediate rail to post", "1/8", "1/8\"", "0.1250 in")

#text("Directional strength increase at the post to baseplate weld: not elected (directional_increase = false).")

#text("Post to baseplate weld pattern: faces perpendicular to rail (base_pattern).")

Derived lengths, each computed in the calc where it is used:

#table(columns: (1fr, auto, auto, auto), table.header(strong("Derived length"), strong("Formula"), strong("Inches"), strong("Computed in")), "Post cantilever length, top of baseplate to top rail centerline", [$L_"post" = h - t_p$], "41.50 in", "Loading", "Eccentricity: rail centerline to the weld plane at the rail underside", [$e = frac(d_"rail", "2")$], "2.000 in", "Check 3", "Effective length, with the unbraced length taken as the post height h", [$L_c = K h$], "88.20 in", "Check 5")

= Section properties

#text("Top rail: HSS4X2X1/8, A500 Gr B (default).") Properties are used exactly as published in the AISC Shapes Database v16.0.

#calcline([$H = "4.000 in"$], "HSS4X2X1/8: outside dimension of the longer side", "AISC Shapes Database v16.0")
#calcline([$B = "2.000 in"$], "Outside dimension of the shorter side", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.1250 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1160 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "1.300 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "0.3958 lb/in"$], "Nominal weight: tabulated 4.75 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I_x = "2.650 in"^4$], "Moment of inertia about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$S_x = "1.320 in"^3$], "Elastic section modulus about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$Z_x = "1.660 in"^3$], "Plastic section modulus about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$r_x = "1.430 in"$], "Radius of gyration about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$I_y = "0.8980 in"^4$], "Moment of inertia about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$S_y = "0.8980 in"^3$], "Elastic section modulus about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$Z_y = "1.020 in"^3$], "Plastic section modulus about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$r_y = "0.8300 in"$], "Radius of gyration about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$J = "2.200 in"^4$], "Torsional constant", "AISC Shapes Database v16.0")
#calcline([$b slash t = "14.20"$], "Width-to-thickness ratio of the shorter walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$h slash t = "31.50"$], "Width-to-thickness ratio of the longer walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$"long_side = vertical"$ #h(6pt) $arrow.r$ #h(6pt) *#"Long side vertical: a vertical load bends the strong axis (x); the horizontal guard load bends the weak axis (y)."*], "Orientation, and the axis each load bends", "Engineering judgement (EOR): a rectangular member's axes follow from its long side")

#text("Post: HSS2X1X3/16, A500 Gr B (default).")

#calcline([$H = "2.000 in"$], "HSS2X1X3/16: outside dimension of the longer side", "AISC Shapes Database v16.0")
#calcline([$B = "1.000 in"$], "Outside dimension of the shorter side", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.1875 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1740 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "0.8450 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "0.2533 lb/in"$], "Nominal weight: tabulated 3.04 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I_x = "0.3500 in"^4$], "Moment of inertia about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$S_x = "0.3500 in"^3$], "Elastic section modulus about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$Z_x = "0.4800 in"^3$], "Plastic section modulus about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$r_x = "0.6430 in"$], "Radius of gyration about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$I_y = "0.1120 in"^4$], "Moment of inertia about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$S_y = "0.2250 in"^3$], "Elastic section modulus about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$Z_y = "0.2880 in"^3$], "Plastic section modulus about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$r_y = "0.3650 in"$], "Radius of gyration about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$J = "0.3010 in"^4$], "Torsional constant", "AISC Shapes Database v16.0")
#calcline([$b slash t = "2.750"$], "Width-to-thickness ratio of the shorter walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$h slash t = "8.490"$], "Width-to-thickness ratio of the longer walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$"long_side = perpendicular to rail"$ #h(6pt) $arrow.r$ #h(6pt) *#"Long side perpendicular to the rail: a load across the guard (outward or inward) bends the strong axis (x); a load along the rail bends the weak axis (y)."*], "Orientation, and the axis each load bends", "Engineering judgement (EOR): a rectangular member's axes follow from its long side")

#text("Intermediate rail: HSS2X1X1/8, A500 Gr B (default).")

#calcline([$H = "2.000 in"$], "HSS2X1X1/8: outside dimension of the longer side", "AISC Shapes Database v16.0")
#calcline([$B = "1.000 in"$], "Outside dimension of the shorter side", "AISC Shapes Database v16.0")
#calcline([$t_"nom" = "0.1250 in"$], "Nominal wall thickness", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1160 in"$], "Design wall thickness", "AISC Shapes Database v16.0")
#calcline([$A = "0.6080 in"^2$], "Area (design wall)", "AISC Shapes Database v16.0")
#calcline([$W = "0.1833 lb/in"$], "Nominal weight: tabulated 2.2 lb/ft (nominal wall)", "AISC Shapes Database v16.0")
#calcline([$I_x = "0.2800 in"^4$], "Moment of inertia about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$S_x = "0.2800 in"^3$], "Elastic section modulus about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$Z_x = "0.3660 in"^3$], "Plastic section modulus about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$r_x = "0.6790 in"$], "Radius of gyration about the x axis, the strong axis", "AISC Shapes Database v16.0")
#calcline([$I_y = "0.09220 in"^4$], "Moment of inertia about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$S_y = "0.1840 in"^3$], "Elastic section modulus about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$Z_y = "0.2230 in"^3$], "Plastic section modulus about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$r_y = "0.3900 in"$], "Radius of gyration about the y axis, the weak axis", "AISC Shapes Database v16.0")
#calcline([$J = "0.2380 in"^4$], "Torsional constant", "AISC Shapes Database v16.0")
#calcline([$b slash t = "5.620"$], "Width-to-thickness ratio of the shorter walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$h slash t = "14.20"$], "Width-to-thickness ratio of the longer walls, tabulated", "AISC Shapes Database v16.0")
#calcline([$"long_side = vertical"$ #h(6pt) $arrow.r$ #h(6pt) *#"Long side vertical: a vertical load bends the strong axis (x); the horizontal guard load bends the weak axis (y)."*], "Orientation, and the axis each load bends", "Engineering judgement (EOR): a rectangular member's axes follow from its long side")

#text("Baseplate: A36. Welds: fillet, electrode E70XX; all around at the rails, and at the baseplate on the faces perpendicular to rail.")

= Loading

Guard loads per ASCE 7-22. The concentrated and uniform loads are separate load types and do not act concurrently. Each check applies them in every direction case and reports the controlling one.

#calcline([$P = "200.0 lb"$], "Concentrated guard load, any direction, any point on the top rail", "ASCE 7-22 §4.5.1")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load, 50 lb/ft, any direction; not concurrent with P", "ASCE 7-22 §4.5.1.1")
#calcline([$P_c = "50.00 lb"$], "Component load on the intermediate rail, horizontal; also applied downward (engineering judgement)", "ASCE 7-22 §4.5.1.2")
#calcline([$w_D = "0.3958 lb/in"$], "Top rail self-weight: tabulated W = 4.75 lb/ft", "AISC Shapes Database v16.0")
#subhead("Dead load at the post")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(L_"post" = h - t_p = ("42.00 in") - ("0.5000 in") = "41.50 in")$], "Post cantilever length, top of baseplate to top rail centerline", "Stated assumption: post fixed at the top of the baseplate")
#calcline([$W_"post" = "0.2533 lb/in"$], "Post self-weight: HSS2X1X3/16, tabulated W = 3.04 lb/ft", "AISC Shapes Database v16.0")
#calcline([$display(D_"post" = W_"post" L_"post" = ("0.2533 lb/in") ("41.50 in") = "10.51 lb")$], "Post dead load, full weight at the base", "Engineering judgement (EOR): post dead load")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post (stated assumption)", "Input")
#calcline([$display(D_"rail" = w_D L = ("0.3958 lb/in") ("72.00 in") = "28.50 lb")$], "Top rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$w_(D,"int") = "0.1833 lb/in"$], "Intermediate rail self-weight: HSS2X1X1/8, tabulated W = 2.2 lb/ft", "AISC Shapes Database v16.0")
#calcline([$display(D_"int" = w_(D,"int") L = ("0.1833 lb/in") ("72.00 in") = "13.20 lb")$], "Intermediate rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$display(P_D = D_"rail" + D_"int" + D_"post" = ("28.50 lb") + ("13.20 lb") + ("10.51 lb") = "52.21 lb")$], "D at the post: axial dead load at the top of the baseplate", "Engineering judgement (EOR): post dead load")

= Check 1: Top rail bending

#flag("NONCOMPACT: HSS4X2X1/8 flange, h/t = 31.5, exceeds lambda_p = 28.12 (lambda_r = 35.15) in bending about the y axis; Mn reduced by flange local buckling, AISC 360-22 Eq. F7-2.")

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Vertical load* \ $M_r$, $M_c$], [*Horizontal load* \ $M_r$, $M_c$], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2", "Mrx = 3,856 lb-in\nMcx = 45,720 lb-in", "—", "0.08", "", "Downward", "Distributed", "1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2", "Mrx = 2,956 lb-in\nMcx = 45,720 lb-in", "—", "0.06", "", strong("Outward"), strong("Concentrated"), strong("1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS"), strong("Mrx = 256.5 lb-in\nMcx = 45,720 lb-in"), strong("Mry = 3,600 lb-in\nMcy = 26,480 lb-in"), strong("0.14"), strong("Controls"), "Outward", "Distributed", "1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "Mrx = 256.5 lb-in\nMcx = 45,720 lb-in", "Mry = 2,700 lb-in\nMcy = 26,480 lb-in", "0.11", "", "Inward", "Concentrated", "1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "Mrx = 256.5 lb-in\nMcx = 45,720 lb-in", "Mry = 3,600 lb-in\nMcy = 26,480 lb-in", "0.14", "", "Inward", "Distributed", "1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "Mrx = 256.5 lb-in\nMcx = 45,720 lb-in", "Mry = 2,700 lb-in\nMcy = 26,480 lb-in", "0.11", "", "Upward", "Concentrated", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "Mrx = 3,446 lb-in\nMcx = 45,720 lb-in", "—", "0.08", "", "Upward", "Distributed", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "Mrx = 2,546 lb-in\nMcx = 45,720 lb-in", "—", "0.06", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Outward, concentrated (1.0D vertical, 1.0L horizontal, each on its own axis; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS)")

#subhead("Demand: outward, concentrated load")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$w_D = "0.3958 lb/in"$], "Top rail self-weight", "Loading")
#calcline([$display(M_D = frac(w_D L^("2"), "8") = frac(("0.3958 lb/in") ("72.00 in")^("2"), "8") = "256.5 lb-in")$], "Dead-load moment, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$P = "200.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(M_L = frac(P L, "4") = frac(("200.0 lb") ("72.00 in"), "4") = "3,600 lb-in")$], "Live-load moment, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$display(M_"rx" = "1.0" M_D = "1.0" ("256.5 lb-in") = "256.5 lb-in")$], "Required flexural strength about the x axis: dead load, vertical", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M_"ry" = "1.0" M_L = "1.0" ("3,600 lb-in") = "3,600 lb-in")$], "Required flexural strength about the y axis: guard load outward", "ASCE 7-22 §2.4.1, Comb. 2")
#subhead("Section")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$display(lambda_"pf" = "1.12" sqrt(frac(E, F_y)) = "1.12" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "28.12")$], "Compact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"rf" = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "35.15")$], "Noncompact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"pw" = "2.42" sqrt(frac(E, F_y)) = "2.42" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "60.76")$], "Compact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$display(lambda_"rw" = "5.7" sqrt(frac(E, F_y)) = "5.7" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "143.1")$], "Noncompact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#subhead("Capacity about the x axis (vertical load)")
#calcline([$Z_x = "1.660 in"^3$], "Plastic section modulus about the x axis", "AISC Shapes Database v16.0")
#calcline([$display(M_"px" = F_y Z_x = ("46.00 ksi") ("1.660 in"^3) = "76,360 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "14.20"$], "Flange slenderness about the x axis: b/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_f = 14.2 <= lambda_"pf" = 28.12$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact flange: flange local buckling does not apply"*], "Flange classification, bending about the x axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$lambda_w = "31.50"$], "Web slenderness about the x axis: h/t of the 4.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_w = 31.5 <= lambda_"pw" = 60.76$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the x axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$display(L_b = L = "72.00 in")$], "Laterally unbraced length: the span between posts", "Engineering judgement (EOR): unbraced length for lateral-torsional buckling")
#calcline([$r_y = "0.8300 in"$], "Radius of gyration about the y axis", "AISC Shapes Database v16.0")
#calcline([$J = "2.200 in"^4$], "Torsional constant", "AISC Shapes Database v16.0")
#calcline([$A_g = "1.300 in"^2$], "Gross area", "AISC Shapes Database v16.0")
#calcline([$display(L_p = frac("0.13" E r_y sqrt(J A_g), M_"px") = frac("0.13" ("29,000 ksi") ("0.8300 in") dot sqrt(("2.200 in"^4) ("1.300 in"^2)), ("76,360 lb-in")) = "69.30 in")$], "Limiting unbraced length for yielding", "AISC 360-22 Eq. F7-10")
#calcline([$S_x = "1.320 in"^3$], "Elastic section modulus about the x axis", "AISC Shapes Database v16.0")
#calcline([$display(L_r = frac("2" E r_y sqrt(J A_g), "0.7" F_y S_x) = frac("2" ("29,000 ksi") ("0.8300 in") dot sqrt(("2.200 in"^4) ("1.300 in"^2)), "0.7" ("46.00 ksi") ("1.320 in"^3)) = "1,915 in")$], "Limiting unbraced length for inelastic lateral-torsional buckling", "AISC 360-22 Eq. F7-11; AISC 360-22 §F7.4")
#calcline([$L_p = 69.30 in < L_b = 72.00 in <= L_r = 1,915 in$ #h(6pt) $arrow.r$ #h(6pt) *#"Inelastic lateral-torsional buckling: Eq. F7-8"*], "", "AISC 360-22 Eq. F7-8")
#calcline([$display(x_A = frac(L, "4") = frac(("72.00 in"), "4") = "18.00 in")$], "Quarter point of the unbraced length", "")
#calcline([$display(M_A = frac("1.0" w_D x_A (L - x_A), "2") = frac("1.0" ("0.3958 lb/in") ("18.00 in") (("72.00 in") - ("18.00 in")), "2") = "192.4 lb-in")$], "Moment at the quarter point", "AISC Manual Table 3-23, Case 1; ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M_B = M_"rx" = "256.5 lb-in")$], "Moment at the centerline: the required moment about this axis", "")
#calcline([$display(M_C = M_A = "192.4 lb-in")$], "Moment at the three-quarter point: the diagram is symmetric about midspan", "")
#calcline([$display(M_"max" = M_B = "256.5 lb-in")$], "Maximum moment in the unbraced length: at midspan", "")
#calcline([$display(C_b = frac("12.5" M_"max", "2.5" M_"max" + "3" M_A + "4" M_B + "3" M_C) = frac("12.5" ("256.5 lb-in"), "2.5" ("256.5 lb-in") + "3" ("192.4 lb-in") + "4" ("256.5 lb-in") + "3" ("192.4 lb-in")) = "1.136")$], "Lateral-torsional buckling modification factor, from this case's moment diagram", "AISC 360-22 Eq. F1-1")
#calcline([$display(M_("n,LTB") = C_b (M_"px" - (M_"px" - "0.7" F_y S_x) frac(L_b - L_p, L_r - L_p)) = "1.136" (("76,360 lb-in") - (("76,360 lb-in") - "0.7" ("46.00 ksi") ("1.320 in"^3)) dot frac(("72.00 in") - ("69.30 in"), ("1,915 in") - ("69.30 in"))) = "86,720 lb-in")$], "Lateral-torsional buckling", "AISC 360-22 Eq. F7-8; AISC 360-22 §F7.4")
#calcline([$display(M_"nx" = "min"(M_"px", M_("n,LTB")) = "min"(("76,360 lb-in"), ("86,720 lb-in")) = "76,360 lb-in")$], "Nominal flexural strength about the x axis: the lowest of yielding and lateral-torsional buckling", "AISC 360-22 §F7")
#calcline([$display(M_"cx" = frac(M_"nx", Omega_b) = frac(("76,360 lb-in"), "1.670") = "45,720 lb-in")$], "Allowable flexural strength about the x axis", "AISC 360-22 Eq. B3-2")
#subhead("Capacity about the y axis (horizontal load)")
#calcline([$Z_y = "1.020 in"^3$], "Plastic section modulus about the y axis", "AISC Shapes Database v16.0")
#calcline([$display(M_"py" = F_y Z_y = ("46.00 ksi") ("1.020 in"^3) = "46,920 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "31.50"$], "Flange slenderness about the y axis: h/t of the 4.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_"pf" = 28.12 < lambda_f = 31.5 <= lambda_"rf" = 35.15$ #h(6pt) $arrow.r$ #h(6pt) *#"NONCOMPACT FLANGE"*], "Flange classification, bending about the y axis: reduced capacity", "AISC 360-22 §B4.1b")
#calcline([$S_y = "0.8980 in"^3$], "Elastic section modulus about the y axis", "AISC Shapes Database v16.0")
#calcline([$display(M_("n,FLB") = M_"py" - (M_"py" - F_y S_y) frac(lambda_f - lambda_"pf", lambda_"rf" - lambda_"pf") = ("46,920 lb-in") - (("46,920 lb-in") - ("46.00 ksi") ("0.8980 in"^3)) dot frac("31.50" - "28.12", "35.15" - "28.12") = "44,220 lb-in")$], "Flange local buckling, noncompact flange", "AISC 360-22 Eq. F7-2")
#calcline([$lambda_w = "14.20"$], "Web slenderness about the y axis: b/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_w = 14.2 <= lambda_"pw" = 60.76$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$"Bending about the minor axis"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "", "AISC 360-22 §F7.4, User Note")
#calcline([$display(M_"ny" = "min"(M_"py", M_("n,FLB")) = "min"(("46,920 lb-in"), ("44,220 lb-in")) = "44,220 lb-in")$], "Nominal flexural strength about the y axis: the lowest of yielding and flange local buckling", "AISC 360-22 §F7")
#calcline([$display(M_"cy" = frac(M_"ny", Omega_b) = frac(("44,220 lb-in"), "1.670") = "26,480 lb-in")$], "Allowable flexural strength about the y axis", "AISC 360-22 Eq. B3-2")
#subhead("Interaction")
#calcline([$display("Ratio" = frac(M_"rx", M_"cx") + frac(M_"ry", M_"cy") = frac(("256.5 lb-in"), ("45,720 lb-in")) + frac(("3,600 lb-in"), ("26,480 lb-in")) = "0.14")$], "Both axes combined, with no axial force", "AISC 360-22 Eq. H1-1b; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.14 <= 1.00$ #h(10pt) #"OK"])

= Check 2: Top rail deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.02204 in", "0.6000 in", "0.04", "", "Downward", "Distributed", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.02077 in", "0.6000 in", "0.03", "", strong("Outward"), strong("Concentrated"), strong("1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only"), strong("0.05972 in"), strong("0.6000 in"), strong("0.10"), strong("Controls"), "Outward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.05599 in", "0.6000 in", "0.09", "", "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.05972 in", "0.6000 in", "0.10", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.05599 in", "0.6000 in", "0.09", "", "Upward", "Concentrated", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.02024 in", "0.6000 in", "0.03", "", "Upward", "Distributed", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.01897 in", "0.6000 in", "0.03", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Outward, concentrated (1.0L, horizontal; Engineering judgement (EOR): serviceability, live load only)")

#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_y = "0.8980 in"^4$], "Moment of inertia about the y axis (horizontal load)", "AISC Shapes Database v16.0")
#calcline([$P = "200.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(Delta_L = frac(P L^("3"), "48" E I_y) = frac(("200.0 lb") ("72.00 in")^("3"), "48" ("29,000 ksi") ("0.8980 in"^4)) = "0.05972 in")$], "Live-load deflection, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$display(Delta = "1.0" Delta_L = "1.0" ("0.05972 in") = "0.05972 in")$], "Live load only", "Engineering judgement (EOR): serviceability, live load only")
#calcline([$display(Delta_"allow" = frac(L, "120") = frac(("72.00 in"), "120") = "0.6000 in")$], "Limit L/120", "Engineering judgement (EOR): deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.05972 in"), ("0.6000 in")) = "0.10")$], "Deflection / limit", "Engineering judgement (EOR): deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.10 <= 1.00$ #h(10pt) #"OK"])

= Check 3: Top rail weld to post

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "64.43 lb/in\nuniform", "—", "64.43 lb/in", "Weld 1,856 lb/in\nBase —", "0.03", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "92.62 lb/in\nuniform", "—", "92.62 lb/in", "Weld 1,856 lb/in\nBase —", "0.05", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "140.2 lb/in\ncompression side", "56.39 lb/in", "151.1 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.08", "", "Outward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "206.3 lb/in\ncompression side", "84.59 lb/in", "223.0 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.12", "", "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "140.2 lb/in\ncompression side", "56.39 lb/in", "151.1 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.08", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "206.3 lb/in\ncompression side", "84.59 lb/in", "223.0 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.12", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "51.57 lb/in\nuniform", "—", "51.57 lb/in", "Weld 1,856 lb/in\nBase —", "0.03", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "79.77 lb/in\nuniform", "—", "79.77 lb/in", "Weld 1,856 lb/in\nBase —", "0.04", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "369.5 lb/in\ncompression side", "56.39 lb/in", "373.8 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.20", "", strong("Longitudinal"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("550.2 lb/in\ncompression side"), strong("84.59 lb/in"), strong("556.7 lb/in"), strong("Weld 1,856 lb/in\nBase 2,018 lb/in"), strong("0.30"), strong("Controls"))]

#heading(level: 2, "Controlling case: Longitudinal, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$B = "2.000 in"$], "HSS4X2X1/8: width of the chord face, the rail's horizontal dimension", "AISC Shapes Database v16.0")
#calcline([$t = "0.1160 in"$], "Top rail design wall thickness, the chord", "AISC Shapes Database v16.0")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$H_b = "1.000 in"$], "HSS2X1X3/16: branch dimension along the chord, the post's dimension parallel to the rail", "AISC Shapes Database v16.0")
#calcline([$B_b = "2.000 in"$], "Branch width across the chord face, the post's dimension perpendicular to the rail", "AISC Shapes Database v16.0")
#calcline([$t_b = "0.1740 in"$], "Post design wall thickness, the branch", "AISC Shapes Database v16.0")
#calcline([$F_"yb" = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$display(B_("e,K1") = frac("10", frac(B, t)) frac(F_y t, F_"yb" t_b) B_b = frac("10", frac(("2.000 in"), ("0.1160 in"))) dot frac(("46.00 ksi") ("0.1160 in"), ("46.00 ksi") ("0.1740 in")) ("2.000 in") = "0.7733 in")$], "Effective width of the branch across the chord face", "AISC 360-22 Eq. K1-1")
#calcline([$display(B_e = "min"(B_("e,K1"), frac(B_b, "2")) = "min"(("0.7733 in"), frac(("2.000 in"), "2")) = "0.7733 in")$], "Effective width: B_e/2 not more than B_b/4, the branch being at 90 degrees", "AISC 360-22 Table K5.1")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(l_e = "2" H_b + "2" B_e = "2" ("1.000 in") + "2" ("0.7733 in") = "3.547 in")$], "Effective weld length", "AISC 360-22 Eq. K5-5; AISC 360-22 §K5")
#calcline([$display(S_"ip" = frac(H_b^("2"), "3") + B_e H_b = frac(("1.000 in")^("2"), "3") + ("0.7733 in") ("1.000 in") = "1.107 in"^2)$], "Effective section modulus of the weld as a line, in-plane bending: a load along the rail", "AISC 360-22 Eq. K5-6; Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#calcline([$display(S_"op" = H_b B_b + frac(B_b^("2"), "3") - frac((B_b - B_e)^("3"), "3" B_b) = ("1.000 in") ("2.000 in") + frac(("2.000 in")^("2"), "3") - frac((("2.000 in") - ("0.7733 in"))^("3"), "3" ("2.000 in")) = "3.026 in"^2)$], "Effective section modulus of the weld as a line, out-of-plane bending: a load across the guard", "AISC 360-22 Eq. K5-7; Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#calcline([$B_"b" = "2.000 in" = B = "2.000 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Fillet model kept"*], "Post as wide as the rail: At equal widths the side welds of a rectangular branch land on the chord's rounded corner and are flare-bevel welds; the fillet model of the entered size all around is kept.", "Engineering judgement (EOR): fillet model kept at equal widths")
#subhead("Eccentricity")
#calcline([$d_"rail" = "4.000 in"$], "HSS4X2X1/8: outside dimension in the vertical direction, the rail depth", "AISC Shapes Database v16.0")
#calcline([$display(e = frac(d_"rail", "2") = frac(("4.000 in"), "2") = "2.000 in")$], "Eccentricity: rail centerline to the weld plane at the rail underside", "Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#subhead("Fillet size limits")
#calcline([$t_"rail,nom" = "0.1250 in"$], "Top rail nominal wall thickness, HSS4X2X1/8", "AISC Shapes Database v16.0")
#calcline([$t_"post,nom" = "0.1875 in"$], "Post nominal wall thickness, HSS2X1X3/16", "AISC Shapes Database v16.0")
#calcline([$display(t_"min" = "min"(t_"rail,nom", t_"post,nom") = "min"(("0.1250 in"), ("0.1875 in")) = "0.1250 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
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
#calcline([$t_"rail" = "0.1160 in"$], "Top rail design wall thickness, HSS4X2X1/8", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM") = "0.6" F_u t_"rail" = "0.6" ("58.00 ksi") ("0.1160 in") = "4,037 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM"), Omega_"BM") = frac(("4,037 lb/in"), "2.000") = "2,018 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$"Rail wall, normal force"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not checked"*], "Rail wall, force normal to the wall: the chord limit states of a rectangular chord (AISC 360-22 Chapter K and §J10) are not computed; not checked (stated assumption). The rail is held to the Chapter K limits of applicability.", "Engineering judgement (EOR): a rectangular chord's limit states not checked")
#calcline([$"Post wall at the weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Covered by Check 5"*], "Post wall at the weld: covered by Check 5. The wall carries the weld force as stress along the post axis, the same demand as Check 5 at its critical section; member shear is not checked (stated assumption).", "Engineering judgement (EOR): post wall at the weld covered by Check 5")
#subhead("Demand: longitudinal, distributed load")
#calcline([$D_"rail" = "28.50 lb"$], "Top rail dead load at the weld: w_D over the span (the tributary length)", "Loading")
#calcline([$display(P = "1.0" D_"rail" = "1.0" ("28.50 lb") = "28.50 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (longitudinal), on the rail at the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("300.0 lb") = "300.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V e = ("300.0 lb") ("2.000 in") = "600.0 lb-in")$], "Moment at the weld plane: V at the rail centerline, arm e", "Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#calcline([$display(f_a = frac(P, l_e) = frac(("28.50 lb"), ("3.547 in")) = "8.036 lb/in")$], "Axial force per inch of weld, compression, uniform over the effective weld length", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_"ip") = frac(("600.0 lb-in"), ("1.107 in"^2)) = "542.2 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("8.036 lb/in") + ("542.2 lb/in") = "550.2 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("8.036 lb/in") - ("542.2 lb/in")) = "534.1 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "550.2 lb/in" >= f_(n,"t") = "534.1 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "550.2 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, l_e) = frac(("300.0 lb"), ("3.547 in")) = "84.59 lb/in")$], "Shear per inch of weld, taken as uniform over the effective weld length", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("550.2 lb/in")^("2") + ("84.59 lb/in")^("2")) = "556.7 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("556.7 lb/in"), ("1,856 lb/in")) = "0.30")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM"), Omega_"BM")) = frac(("84.59 lb/in"), ("2,018 lb/in")) = "0.04")$], "Rail fusion face: in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.2999", "0.04191") = "0.30")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.30 <= 1.00$ #h(10pt) #"OK"])

= Check 4a: Intermediate rail

== Envelope summary

Each limit state is computed in both directions of the component load. The full calculation follows for the governing case of each limit state.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Limit state*], [*Direction*], [*Combination*], [*Demand* $M_a$ or $Delta$], [*Capacity* $M_n / Omega_b$ or $Delta_"allow"$], [*Ratio*], []), "Bending", "Downward", "1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "1,019 lb-in", "10,080 lb-in", "0.10", "", "Bending", "Horizontal", "1.0L horizontal, alone\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "900.0 lb-in", "6,143 lb-in", "0.15", "", "Deflection", "Downward", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.05578 in", "0.6000 in", "0.09", "", strong("Deflection"), strong("Horizontal"), strong("1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only"), strong("0.1454 in"), strong("0.6000 in"), strong("0.24"), strong("Controls"))

#heading(level: 2, "Controlling case: Horizontal, deflection (1.0L, horizontal; Engineering judgement (EOR): serviceability, live load only)")

#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_"int,y" = "0.09220 in"^4$], "Moment of inertia about the y axis (horizontal load), HSS2X1X1/8", "AISC Shapes Database v16.0")
#calcline([$P_c = "50.00 lb"$], "Component load, a point load at midspan", "Loading")
#calcline([$display(Delta_L = frac(P_c L^("3"), "48" E I_"int,y") = frac(("50.00 lb") ("72.00 in")^("3"), "48" ("29,000 ksi") ("0.09220 in"^4)) = "0.1454 in")$], "Component load deflection, midspan", "AISC Manual Table 3-23, Case 7; Engineering judgement (EOR): component load as a point load at midspan")
#calcline([$display(Delta = "1.0" Delta_L = "1.0" ("0.1454 in") = "0.1454 in")$], "Component load only", "Engineering judgement (EOR): serviceability, live load only")
#calcline([$display(Delta_"allow" = frac(L, "120") = frac(("72.00 in"), "120") = "0.6000 in")$], "Limit L/120", "Engineering judgement (EOR): deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.1454 in"), ("0.6000 in")) = "0.24")$], "Deflection / limit", "Engineering judgement (EOR): deflection limit, not code")

#heading(level: 2, "Governing bending case: Horizontal, bending (1.0L horizontal, alone; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5))")

#subhead("Demand: horizontal, component load")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$P_c = "50.00 lb"$], "Component load, a point load at midspan", "Loading")
#calcline([$display(M_L = frac(P_c L, "4") = frac(("50.00 lb") ("72.00 in"), "4") = "900.0 lb-in")$], "Component load moment, midspan", "AISC Manual Table 3-23, Case 7; Engineering judgement (EOR): component load as a point load at midspan")
#calcline([$display(M_"ry" = "1.0" M_L = "1.0" ("900.0 lb-in") = "900.0 lb-in")$], "Required flexural strength about the y axis: the component load alone, not combined with dead load", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); ASCE 7-22 §2.4.1, Comb. 2")
#subhead("Section")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$display(lambda_"pf" = "1.12" sqrt(frac(E, F_y)) = "1.12" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "28.12")$], "Compact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"rf" = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "35.15")$], "Noncompact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"pw" = "2.42" sqrt(frac(E, F_y)) = "2.42" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "60.76")$], "Compact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$display(lambda_"rw" = "5.7" sqrt(frac(E, F_y)) = "5.7" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "143.1")$], "Noncompact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#subhead("Capacity about the y axis (horizontal load)")
#calcline([$Z_y = "0.2230 in"^3$], "Plastic section modulus about the y axis", "AISC Shapes Database v16.0")
#calcline([$display(M_"py" = F_y Z_y = ("46.00 ksi") ("0.2230 in"^3) = "10,260 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "14.20"$], "Flange slenderness about the y axis: h/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_f = 14.2 <= lambda_"pf" = 28.12$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact flange: flange local buckling does not apply"*], "Flange classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$lambda_w = "5.620"$], "Web slenderness about the y axis: b/t of the 1.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_w = 5.62 <= lambda_"pw" = 60.76$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$"Bending about the minor axis"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "", "AISC 360-22 §F7.4, User Note")
#calcline([$display(M_"ny" = M_"py" = "10,260 lb-in")$], "Nominal flexural strength about the y axis: yielding", "AISC 360-22 §F7")
#calcline([$display(M_"cy" = frac(M_"ny", Omega_b) = frac(("10,260 lb-in"), "1.670") = "6,143 lb-in")$], "Allowable flexural strength about the y axis", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = frac(M_"ry", M_"cy") = frac(("900.0 lb-in"), ("6,143 lb-in")) = "0.15")$], "Demand / capacity", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.24 <= 1.00$ #h(10pt) #"OK"])

= Check 4b: Intermediate rail weld to post

== Envelope summary

Both directions of the component load are computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), strong("Downward"), strong("Component"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)"), strong("—\nshear only"), strong("11.32 lb/in"), strong("11.32 lb/in"), strong("Weld 1,856 lb/in\nBase 2,018 lb/in"), strong("0.01"), strong("Controls"), "Horizontal", "Component", "1.0D vertical, 1.0L horizontal, vector sum\nASCE 7-22 §2.4.1, Comb. 2", "—\nshear only", "10.09 lb/in", "10.09 lb/in", "Weld 1,856 lb/in\nBase 2,018 lb/in", "0.01", "")]

#heading(level: 2, "Controlling case: Downward, component (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5))")

#subhead("Weld properties")
#calcline([$B = "2.000 in"$], "HSS2X1X3/16: width of the chord face, the post's dimension perpendicular to the rail", "AISC Shapes Database v16.0")
#calcline([$t = "0.1740 in"$], "Post design wall thickness, the chord", "AISC Shapes Database v16.0")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$H_b = "2.000 in"$], "HSS2X1X1/8: branch dimension along the chord, the intermediate rail's vertical dimension", "AISC Shapes Database v16.0")
#calcline([$B_b = "1.000 in"$], "Branch width across the chord face, the intermediate rail's horizontal dimension", "AISC Shapes Database v16.0")
#calcline([$t_b = "0.1160 in"$], "Intermediate rail design wall thickness, the branch", "AISC Shapes Database v16.0")
#calcline([$F_"yb" = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$display(B_("e,K1") = frac("10", frac(B, t)) frac(F_y t, F_"yb" t_b) B_b = frac("10", frac(("2.000 in"), ("0.1740 in"))) dot frac(("46.00 ksi") ("0.1740 in"), ("46.00 ksi") ("0.1160 in")) ("1.000 in") = "1.305 in")$], "Effective width of the branch across the chord face", "AISC 360-22 Eq. K1-1")
#calcline([$display(B_e = "min"(B_("e,K1"), frac(B_b, "2")) = "min"(("1.305 in"), frac(("1.000 in"), "2")) = "0.5000 in")$], "Effective width: B_e/2 not more than B_b/4, the branch being at 90 degrees", "AISC 360-22 Table K5.1")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(l_e = "2" H_b + "2" B_e = "2" ("2.000 in") + "2" ("0.5000 in") = "5.000 in")$], "Effective weld length", "AISC 360-22 Eq. K5-5; AISC 360-22 §K5")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Connection model")
#calcline([$"Intermediate rail to post weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Simple shear connection"*], "Simple shear connection consistent with the simple-span member assumption; no end moment at the weld.", "Engineering judgement (EOR): intermediate rail to post weld as a simple shear connection; Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post")
#subhead("Fillet size limits")
#calcline([$t_"int,nom" = "0.1250 in"$], "Intermediate rail nominal wall thickness, HSS2X1X1/8", "AISC Shapes Database v16.0")
#calcline([$t_"post,nom" = "0.1875 in"$], "Post nominal wall thickness, HSS2X1X3/16", "AISC Shapes Database v16.0")
#calcline([$display(t_"min" = "min"(t_"int,nom", t_"post,nom") = "min"(("0.1250 in"), ("0.1875 in")) = "0.1250 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
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
#calcline([$t_"post" = "0.1740 in"$], "Post design wall thickness, HSS2X1X3/16", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM,post") = "0.6" F_u t_"post" = "0.6" ("58.00 ksi") ("0.1740 in") = "6,055 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM,post"), Omega_"BM") = frac(("6,055 lb/in"), "2.000") = "3,028 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#subhead("Base metal: intermediate rail wall fusion face (branch)")
#calcline([$F_u = "58.00 ksi"$], "Tensile strength, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"int" = "0.1160 in"$], "Intermediate rail design wall thickness, HSS2X1X1/8", "AISC Shapes Database v16.0")
#calcline([$display(R_(n,"BM,int") = "0.6" F_u t_"int" = "0.6" ("58.00 ksi") ("0.1160 in") = "4,037 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM,int"), Omega_"BM") = frac(("4,037 lb/in"), "2.000") = "2,018 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$frac(R_(n,"BM,int"), Omega_"BM") = "2,018 lb/in" < frac(R_(n,"BM,post"), Omega_"BM") = "3,028 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Intermediate rail wall governs"*], "Base metal is checked at the fusion face of both connected parts, the post wall (the chord) and the intermediate rail wall (the branch), each in shear rupture against the in-plane shear per inch; the lower allowable governs.", "Engineering judgement (EOR): Check 4b base metal on both walls, lower governs")
#calcline([$"Post wall, chord limit states"$ #h(6pt) $arrow.r$ #h(6pt) *#"No demand"*], "Chapter K chord limit states: the intermediate rail delivers no axial force or moment to the post wall (simple shear connection); the post wall's in-plane shear is checked by the base metal line above.", "Engineering judgement (EOR): no chord limit state demand at the intermediate rail")
#subhead("Demand: downward, component load")
#calcline([$w_(D,"int") = "0.1833 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$display(R_D = frac(w_(D,"int") L, "2") = frac(("0.1833 lb/in") ("72.00 in"), "2") = "6.600 lb")$], "Dead-load end reaction at the post", "AISC Manual Table 3-23, Case 1")
#calcline([$P_c = "50.00 lb"$], "Component load adjacent to the post: the full P_c to this end", "Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post")
#calcline([$display(R = "1.0" R_D + "1.0" P_c = "1.0" ("6.600 lb") + "1.0" ("50.00 lb") = "56.60 lb")$], "Weld reaction: dead and component loads in the same (vertical) direction, in the plane of the weld", "Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(f_v = frac(R, l_e) = frac(("56.60 lb"), ("5.000 in")) = "11.32 lb/in")$], "Shear per inch of weld, taken as uniform over the effective weld length", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = f_v = "11.32 lb/in")$], "Resultant per inch: shear only, no axial force and no moment", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("11.32 lb/in"), ("1,856 lb/in")) = "0.01")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM,int"), Omega_"BM")) = frac(("11.32 lb/in"), ("2,018 lb/in")) = "0.01")$], "Base metal, intermediate rail wall fusion face (governs): in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.006100", "0.005608") = "0.01")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.01 <= 1.00$ #h(10pt) #"OK"])

= Check 5: Post combined axial and flexure

#flag("SLENDERNESS: HSS2X1X3/16 Lc/r = 241.6 exceeds 200, the limit recommended by the AISC 360-22 §E2, User Note. Flagged; the calc continues.")

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Axial* $P_r$ \ capacity $P_c$ or $P_t$], [*Moment* $M_r$ \ capacity $M_c$], [*Equation*], [$frac(alpha P_r, P_e)$], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "252.2 lb comp.\nPc = 2,175 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.12", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "352.2 lb comp.\nPc = 2,175 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.16", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "52.21 lb comp.\nPc = 2,175 lb", "8,300 lb-in\nMc = 13,150 lb-in\nabout x", "Eq. H1-1b", "0.006487", "0.64", "", "Outward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "52.21 lb comp.\nPc = 2,175 lb", "12,450 lb-in\nMc = 13,150 lb-in\nabout x", "Eq. H1-1b", "0.006487", "0.96", "", "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "52.21 lb comp.\nPc = 2,175 lb", "8,300 lb-in\nMc = 13,150 lb-in\nabout x", "Eq. H1-1b", "0.006487", "0.64", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "52.21 lb comp.\nPc = 2,175 lb", "12,450 lb-in\nMc = 13,150 lb-in\nabout x", "Eq. H1-1b", "0.006487", "0.96", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "168.7 lb tension\nPt = 23,280 lb", "—", "Pr/Pt\n(Eq. D2-1)", "—", "0.01", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "268.7 lb tension\nPt = 23,280 lb", "—", "Pr/Pt\n(Eq. D2-1)", "—", "0.01", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "52.21 lb comp.\nPc = 2,175 lb", "8,300 lb-in\nMc = 7,933 lb-in\nabout y", "Eq. H1-1b", "0.02027", "1.06", "", strong("Longitudinal"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("52.21 lb comp.\nPc = 2,175 lb"), strong("12,450 lb-in\nMc = 7,933 lb-in\nabout y"), strong("Eq. H1-1b"), strong("0.02027"), strong("1.58"), strong("Controls"))]

#heading(level: 2, "Controlling case: Longitudinal, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Capacity")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$display(lambda_"pf" = "1.12" sqrt(frac(E, F_y)) = "1.12" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "28.12")$], "Compact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"rf" = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "35.15")$], "Noncompact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"pw" = "2.42" sqrt(frac(E, F_y)) = "2.42" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "60.76")$], "Compact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$display(lambda_"rw" = "5.7" sqrt(frac(E, F_y)) = "5.7" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "143.1")$], "Noncompact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$Z_y = "0.2880 in"^3$], "Plastic section modulus about the y axis", "AISC Shapes Database v16.0")
#calcline([$display(M_"py" = F_y Z_y = ("46.00 ksi") ("0.2880 in"^3) = "13,250 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "8.490"$], "Flange slenderness about the y axis: h/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_f = 8.49 <= lambda_"pf" = 28.12$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact flange: flange local buckling does not apply"*], "Flange classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$lambda_w = "2.750"$], "Web slenderness about the y axis: b/t of the 1.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_w = 2.75 <= lambda_"pw" = 60.76$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$"Bending about the minor axis"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "", "AISC 360-22 §F7.4, User Note")
#calcline([$display(M_"ny" = M_"py" = "13,250 lb-in")$], "Nominal flexural strength about the y axis: yielding", "AISC 360-22 §F7")
#calcline([$display(M_"cy" = frac(M_"ny", Omega_b) = frac(("13,250 lb-in"), "1.670") = "7,933 lb-in")$], "Allowable flexural strength about the y axis", "AISC 360-22 Eq. B3-2")
#calcline([$display(lambda_(r,c) = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "35.15")$], "Slender limit, walls of rectangular HSS in compression", "AISC 360-22 Table B4.1a, Case 6")
#calcline([$lambda_b = "2.750"$], "Wall slenderness: b/t of the 1.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_b = 2.75 <= lambda_(r,c) = 35.15$ #h(6pt) $arrow.r$ #h(6pt) *#"Nonslender"*], "Wall classification, compression: no noncompact category", "AISC 360-22 §B4.1a")
#calcline([$lambda_h = "8.490"$], "Wall slenderness: h/t of the 2.000 in walls, tabulated (design wall)", "AISC Shapes Database v16.0")
#calcline([$lambda_h = 8.49 <= lambda_(r,c) = 35.15$ #h(6pt) $arrow.r$ #h(6pt) *#"Nonslender"*], "Wall classification, compression: no noncompact category", "AISC 360-22 §B4.1a")
#calcline([$K = "2.100"$], "Effective length factor, fixed-free (recommended design value)", "AISC 360-22 Comm. Table C-A-7.1, case (e)")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$display(L_c = K h = "2.100" ("42.00 in") = "88.20 in")$], "Effective length, with the unbraced length taken as the post height h", "AISC 360-22 §E2; Engineering judgement (EOR): unbraced length is the post height")
#calcline([$r_y = "0.3650 in"$], "Radius of gyration: the smaller, about the y axis, in every case", "AISC Shapes Database v16.0")
#calcline([$display(frac(L_c, r) = frac(L_c, r_y) = frac(("88.20 in"), ("0.3650 in")) = "241.6")$], "Effective slenderness ratio", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 241.6 > 200$ #h(6pt) $arrow.r$ #h(6pt) *#"FLAG: exceeds the recommended limit"*], "For members designed on the basis of compression, the effective slenderness ratio Lc/r preferably should not exceed 200. A recommendation, not a requirement: flagged, and the calc continues.", "AISC 360-22 §E2, User Note")
#calcline([$display("4.71" sqrt(frac(E, F_y)) = "4.71" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "118.3")$], "Limit between inelastic and elastic buckling", "AISC 360-22 §E3(a), (b)")
#calcline([$display(F_e = frac(pi^("2") E, (frac(L_c, r))^("2")) = frac(pi^("2") ("29,000 ksi"), "241.6"^("2")) = "4.902 ksi")$], "Elastic buckling stress", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 241.6 > 118.3$ #h(6pt) $arrow.r$ #h(6pt) *#"Elastic buckling: Eq. E3-3"*], "", "AISC 360-22 §E3(a), (b)")
#calcline([$display(F_"cr" = "0.877" F_e = "0.877" ("4.902 ksi") = "4.299 ksi")$], "Critical stress", "AISC 360-22 Eq. E3-3")
#calcline([$A_g = "0.8450 in"^2$], "Gross area", "AISC Shapes Database v16.0")
#calcline([$display(P_n = F_"cr" A_g = ("4.299 ksi") ("0.8450 in"^2) = "3,632 lb")$], "Nominal compressive strength", "AISC 360-22 Eq. E3-1")
#calcline([$Omega_c = "1.670"$], "Safety factor for compression (ASD)", "AISC 360-22 §E1")
#calcline([$display(P_c = frac(P_n, Omega_c) = frac(("3,632 lb"), "1.670") = "2,175 lb")$], "Allowable compressive strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: longitudinal, distributed load")
#calcline([$P_D = "52.21 lb"$], "D at the post: axial dead load", "Loading")
#calcline([$display(P_r = "1.0" P_D = "1.0" ("52.21 lb") = "52.21 lb")$], "Required axial strength: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (longitudinal) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p (critical section at the top of the baseplate)", "Loading")
#calcline([$display(M_L = V_L L_"post" = ("300.0 lb") ("41.50 in") = "12,450 lb-in")$], "Live-load moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(M_r = "1.0" M_L = "1.0" ("12,450 lb-in") = "12,450 lb-in")$], "Required flexural strength", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$I_y = "0.1120 in"^4$], "Moment of inertia about the y axis, which this case bends", "AISC Shapes Database v16.0")
#calcline([$display(P_e = frac(pi^("2") E I_y, L_c^("2")) = frac(pi^("2") ("29,000 ksi") ("0.1120 in"^4), ("88.20 in")^("2")) = "4,121 lb")$], "Elastic critical buckling load, at the compression Lc", "AISC 360-22 Eq. A-8-5; Engineering judgement (EOR): Pe at Lc = 2.1h")
#calcline([$display(frac(alpha P_r, P_e) = frac("1.6" P_r, P_e) = frac("1.6" ("52.21 lb"), ("4,121 lb")) = "0.02027")$], "Second-order ratio", "AISC 360-22 App. 8")
#calcline([$frac(alpha P_r, P_e) <= 0.05$ #h(6pt) $arrow.r$ #h(6pt) *#"Second-order effects negligible: αPr/Pe = 0.02027; amplification taken as 1.0."*], "", "Engineering judgement (EOR): second-order limit")
#calcline([$display(frac(P_r, P_c) = frac(("52.21 lb"), ("2,175 lb")) = "0.02400")$], "Axial ratio, selects the interaction equation", "AISC 360-22 §H1.1")
#calcline([$frac(P_r, P_c) = 0.02400 < 0.2$ #h(6pt) $arrow.r$ #h(6pt) *#"Eq. H1-1b"*], "", "AISC 360-22 §H1.1")
#calcline([$display("Ratio" = frac(P_r, "2" P_c) + frac(M_r, M_"cy") = frac(("52.21 lb"), "2" ("2,175 lb")) + frac(("12,450 lb-in"), ("7,933 lb-in")) = "1.58")$], "Combined axial and flexure", "AISC 360-22 Eq. H1-1b")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 1.58 > 1.00$ #h(10pt) #"NG"])

= Check 6: Post deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), "Downward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Outward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.4694 in", "0.6917 in", "0.68", "", "Outward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.7042 in", "0.6917 in", "1.02", "", "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.4694 in", "0.6917 in", "0.68", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.7042 in", "0.6917 in", "1.02", "", "Upward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Longitudinal", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "1.467 in", "0.6917 in", "2.12", "", strong("Longitudinal"), strong("Distributed"), strong("1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only"), strong("2.201 in"), strong("0.6917 in"), strong("3.18"), strong("Controls"))

#heading(level: 2, "Controlling case: Longitudinal, distributed (1.0L, horizontal; Engineering judgement (EOR): serviceability, live load only)")

#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p", "Loading")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_y = "0.1120 in"^4$], "Moment of inertia about the y axis, which this case bends", "AISC Shapes Database v16.0")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (longitudinal) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(Delta_L = frac(V_L L_"post"^("3"), "3" E I_y) = frac(("300.0 lb") ("41.50 in")^("3"), "3" ("29,000 ksi") ("0.1120 in"^4)) = "2.201 in")$], "Live-load deflection at the top of the post", "AISC Manual Table 3-23, Case 22")
#calcline([$display(Delta = "1.0" Delta_L = "1.0" ("2.201 in") = "2.201 in")$], "Live load only; dead load acts axially", "Engineering judgement (EOR): serviceability, live load only")
#calcline([$display(Delta_"allow" = frac(L_"post", "60") = frac(("41.50 in"), "60") = "0.6917 in")$], "Limit (h - t_p)/60", "Engineering judgement (EOR): post deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("2.201 in"), ("0.6917 in")) = "3.18")$], "Deflection / limit", "Engineering judgement (EOR): post deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 3.18 > 1.00$ #h(10pt) #"NG"])

= Check 7: Post weld to baseplate

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "96.71 lb/in\nuniform", "—", "96.71 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 4,793 lb/in", "0.03", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "135.1 lb/in\nuniform", "—", "135.1 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 4,793 lb/in", "0.05", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "14,660 lb/in\ncompression side", "76.69 lb/in", "14,660 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 4,793 lb/in", "5.27", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("21,990 lb/in\ncompression side"), strong("115.0 lb/in"), strong("21,990 lb/in"), strong("Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 4,793 lb/in"), strong("7.90"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "14,660 lb/in\ncompression side", "76.69 lb/in", "14,660 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 4,793 lb/in", "5.27", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "21,990 lb/in\ncompression side", "115.0 lb/in", "21,990 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 4,793 lb/in", "7.90", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "64.67 lb/in\nuniform", "—", "64.67 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 4,793 lb/in", "0.02", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "103.0 lb/in\nuniform", "—", "103.0 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 4,793 lb/in", "0.04", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "6,385 lb/in\ncompression side", "76.69 lb/in", "6,386 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 4,793 lb/in", "2.29", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "9,568 lb/in\ncompression side", "115.0 lb/in", "9,568 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in\nWall 4,793 lb/in", "3.44", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$a_"face" = "2.000 in"$], "HSS2X1X3/16: outside width of each welded face, the faces perpendicular to the rail", "AISC Shapes Database v16.0")
#calcline([$d_"faces" = "1.000 in"$], "Distance between the two weld lines: the post's outside dimension parallel to the rail", "AISC Shapes Database v16.0")
#calcline([$t_"des" = "0.1740 in"$], "Design wall thickness, HSS2X1X3/16: it sets the outside corner radius", "AISC Shapes Database v16.0")
#calcline([$display(R_o = "2" t_"des" = "2" ("0.1740 in") = "0.3480 in")$], "Outside corner radius", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$w = "0.1875 in"$], "Fillet weld leg size, each welded face (3/16 as entered)", "Input")
#calcline([$display(l_w = a_"face" - "2" R_o = ("2.000 in") - "2" ("0.3480 in") = "1.304 in")$], "Length of each weld line: the flat of its face, between the tangent points", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(L_w = "2" l_w = "2" ("1.304 in") = "2.608 in")$], "Weld length: the two lines", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(S_("w,l") = l_w d_"faces" = ("1.304 in") ("1.000 in") = "1.304 in"^2)$], "Section modulus of the weld lines, a load along the rail: the lines are the extreme fibers", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(S_("w,t") = frac(l_w^("2"), "3") = frac(("1.304 in")^("2"), "3") = "0.5668 in"^2)$], "Section modulus of the weld lines, a load across the guard: each line bends about its own middle", "Engineering judgement (EOR): weld line on a pair of faces, flats only")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1875 in") = "0.1326 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Moment arm")
#calcline([$L_"post" = "41.50 in"$], "Moment arm, h - t_p: guard load at the top rail centerline, weld at the top of the baseplate", "Loading")
#subhead("Fillet size limits")
#calcline([$t_"post,nom" = "0.1875 in"$], "Post nominal wall thickness, HSS2X1X3/16", "AISC Shapes Database v16.0")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(t_"min" = "min"(t_"post,nom", t_p) = "min"(("0.1875 in"), ("0.5000 in")) = "0.1875 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
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
#calcline([$t_"wall" = "0.1740 in"$], "Post design wall thickness, HSS2X1X3/16", "AISC Shapes Database v16.0")
#calcline([$display(R_("n,y") = F_y t_"wall" = ("46.00 ksi") ("0.1740 in") = "8,004 lb/in")$], "Yielding of the wall under the force along the post axis, per inch of weld", "AISC 360-22 Eq. J4-1")
#calcline([$Omega_y = "1.670"$], "Safety factor, yielding (ASD)", "AISC 360-22 §J4.1(a)")
#calcline([$display(R_("n,u") = F_u t_"wall" = ("58.00 ksi") ("0.1740 in") = "10,090 lb/in")$], "Rupture of the wall under the force along the post axis, per inch of weld", "AISC 360-22 Eq. J4-2")
#calcline([$Omega_u = "2.000"$], "Safety factor, rupture (ASD)", "AISC 360-22 §J4.1(b)")
#calcline([$display(R_("wall,a") = "min"(frac(R_("n,y"), Omega_y), frac(R_("n,u"), Omega_u)) = "min"(frac(("8,004 lb/in"), "1.670"), frac(("10,090 lb/in"), "2.000")) = "4,793 lb/in")$], "Allowable force along the post axis per inch: the lower of yielding and rupture", "AISC 360-22 Eq. B3-2")
#calcline([$display(R_("n,v") = "0.6" F_u t_"wall" = "0.6" ("58.00 ksi") ("0.1740 in") = "6,055 lb/in")$], "Shear rupture of the wall under the force along the face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_v = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(R_("wall,f") = frac(R_("n,v"), Omega_v) = frac(("6,055 lb/in"), "2.000") = "3,028 lb/in")$], "Allowable force along the face per inch", "AISC 360-22 Eq. B3-2")
#subhead("Demand: outward, distributed load")
#calcline([$P_D = "52.21 lb"$], "D at the post: axial dead load at the top of the baseplate", "Loading")
#calcline([$display(P = "1.0" P_D = "1.0" ("52.21 lb") = "52.21 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (outward), at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("300.0 lb") = "300.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V L_"post" = ("300.0 lb") ("41.50 in") = "12,450 lb-in")$], "Moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(f_a = frac(P, L_w) = frac(("52.21 lb"), ("2.608 in")) = "20.02 lb/in")$], "Axial force per inch of weld, compression, uniform along the weld lines", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_("w,t")) = frac(("12,450 lb-in"), ("0.5668 in"^2)) = "21,970 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("20.02 lb/in") + ("21,970 lb/in") = "21,990 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("20.02 lb/in") - ("21,970 lb/in")) = "21,950 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "21,990 lb/in" >= f_(n,"t") = "21,950 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "21,990 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, L_w) = frac(("300.0 lb"), ("2.608 in")) = "115.0 lb/in")$], "Shear per inch of weld, taken as uniform along the weld lines", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("21,990 lb/in")^("2") + ("115.0 lb/in")^("2")) = "21,990 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.1326 in") dot "1.000" = "5,568 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("5,568 lb/in"), "2.000") = "2,784 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("21,990 lb/in"), ("2,784 lb/in")) = "7.90")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_r, frac(R_(n,"BM"), Omega_"BM")) = frac(("21,990 lb/in"), ("8,700 lb/in")) = "2.53")$], "Baseplate fusion face: the resultant per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_("wall,a") = frac(f_n, R_("wall,a")) = frac(("21,990 lb/in"), ("4,793 lb/in")) = "4.59")$], "Post wall: force along the post axis / allowable", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_("wall,f") = frac(f_v, R_("wall,f")) = frac(("115.0 lb/in"), ("3,028 lb/in")) = "0.04")$], "Post wall: force along the face / allowable", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"wall" = "max"("Ratio"_("wall,a"), "Ratio"_("wall,f")) = "max"("4.587", "0.03799") = "4.59")$], "Post wall: the larger of the two, not combined", "Engineering judgement (EOR): post wall at a face-pair base weld checked on its own lines")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM", "Ratio"_"wall") = "max"("7.898", "2.527", "4.587") = "7.90")$], "The largest of weld metal, base metal and post wall", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 7.90 > 1.00$ #h(10pt) #"NG"])

= Summary

#table(columns: (1fr, auto, auto, auto, auto, auto), table.header(strong("Check"), strong("Demand"), strong("Capacity"), strong("Ratio"), strong("Controlling direction"), strong("Result")), "1. Top rail bending", "Mrx = 256.5 lb-in; Mry = 3,600 lb-in", "Mcx = 45,720 lb-in; Mcy = 26,480 lb-in", "0.14", "Outward, concentrated", "OK", "2. Top rail deflection", "0.05972 in", "0.6000 in", "0.10", "Outward, concentrated", "OK", "3. Top rail weld to post", "556.7 lb/in", "1,856 lb/in (weld metal)", "0.30", "Longitudinal, distributed", "OK", "4a. Intermediate rail", "0.1454 in", "0.6000 in", "0.24", "Horizontal, deflection", "OK", "4b. Intermediate rail weld to post", "11.32 lb/in", "1,856 lb/in (weld metal)", "0.01", "Downward, component", "OK", "5. Post combined axial and flexure", "Pr = 52.21 lb; Mr = 12,450 lb-in", "Pc = 2,175 lb; Mc = 7,933 lb-in", "1.58", "Longitudinal, distributed", "NG (Lc/r = 241.6 > 200, flagged)", "6. Post deflection", "2.201 in", "0.6917 in", "3.18", "Longitudinal, distributed", "NG", "7. Post weld to baseplate", "21,990 lb/in", "2,784 lb/in (weld metal)", "7.90", "Outward, distributed", "NG")

= Anchor reactions

LRFD reactions at the top of concrete, for direct input into anchor software: reporting, not a pass/fail check. Each set is simultaneous: the shear, axial force and moment that occur together.

#text(weight: "bold", "Baseplate: B = 6.000 in (parallel to rail) × N = 8.000 in (perpendicular to rail)")

#subhead("Dead load at the base")
#calcline([$D_"rail" = "28.50 lb"$], "Top rail", "Loading")
#calcline([$D_"int" = "13.20 lb"$], "Intermediate rail", "Loading")
#calcline([$D_"post" = "10.51 lb"$], "Post, over h - t_p", "Loading")
#calcline([$rho = "0.2836 lb/in"^3$], "Steel unit weight", "AISC Manual 16th Ed., Part 17")
#calcline([$B = "6.000 in"$], "Baseplate, parallel to the rail", "Input")
#calcline([$N = "8.000 in"$], "Baseplate, perpendicular to the rail", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(W_"bp" = rho B N t_p = ("0.2836 lb/in"^3) ("6.000 in") ("8.000 in") ("0.5000 in") = "6.806 lb")$], "Baseplate weight: in the reaction sets only, below the critical section of Checks 5 and 7", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$display(D = D_"rail" + D_"int" + D_"post" + W_"bp" = ("28.50 lb") + ("13.20 lb") + ("10.51 lb") + ("6.806 lb") = "59.02 lb")$], "Dead load at the base", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#subhead("Governing guard load type")
#calcline([$P = "200.0 lb"$], "Concentrated guard load P, at the top of the post", "Loading")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$w_L L = "300.0 lb" > P = "200.0 lb"$ #h(6pt) $arrow.r$ #h(6pt) *#"Distributed load governs"*], "The larger at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Lateral set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "480.0 lb", "−53.12 lb (compression)", "20,160 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D axial, 1.6L horizontal; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "28.50 lb", "D, intermediate rail", "13.20 lb", "D, post", "10.51 lb", "D, baseplate", "6.806 lb", strong("D, total"), strong("59.02 lb"))

#"V and M act in the same vertical plane; M = V·h."

#"Lateral set applies in any horizontal direction; enter it in the anchor software in the orientation that governs the anchor pattern. Loads can reverse."

#subhead("Demand: lateral, distributed load")
#calcline([$D = "59.02 lb"$], "Dead load at the base", "Reactions")
#calcline([$display(abs(N_u) = "0.9" D = "0.9" ("59.02 lb") = "53.12 lb")$], "Axial force at the base: dead load, compression", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal at the top of the post, in any horizontal direction", "Stated assumption: the tributary length is the span")
#calcline([$display(V_u = "1.6" V_L = "1.6" ("300.0 lb") = "480.0 lb")$], "Base shear", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$h = "42.00 in"$], "Moment arm: top rail centerline to top of concrete", "Input")
#calcline([$display(M_u = V_u h = ("480.0 lb") ("42.00 in") = "20,160 lb-in")$], "Base moment at the top of concrete: V_u at the top rail centerline, arm h", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Upward set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "0 lb", "+426.9 lb (tension)", "0 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D + 1.6L, net axial; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "28.50 lb", "D, intermediate rail", "13.20 lb", "D, post", "10.51 lb", "D, baseplate", "6.806 lb", strong("D, total"), strong("59.02 lb"))

#subhead("Demand: upward, distributed load")
#calcline([$D = "59.02 lb"$], "Dead load at the base", "Reactions")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(P_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, upward at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(abs(N_u) = "1.6" P_L - "0.9" D = "1.6" ("300.0 lb") - "0.9" ("59.02 lb") = "426.9 lb")$], "Axial force at the base: net tension (uplift), guard load opposing dead load", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
