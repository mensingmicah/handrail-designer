
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
+ #"Local strength of the rail wall at the post (AISC 360-22 Chapter K chord limit states) is checked for a round post on a round rail. It is not checked where the rail is rectangular or where a round and a rectangular member meet; the rail is then held to the Chapter K limits of applicability."
+ #"At a face-pair base weld, the post wall's normal force and its shear are each checked against their own limit, not combined; the shear is small next to the normal force."
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

#table(columns: (auto, 1fr, auto), table.header(strong("Entry"), strong("Citation"), strong("Source")), "ej.section.custom_wall_nominal", "Engineering judgement (EOR): a custom tube's wall is entered as the nominal wall", "engineer", "aisc360.B4.2.coeff", "AISC 360-22 §B4.2", "AISC 360-22 text, read 2026-10-10", "aisc360.B4.2.design_wall", "AISC 360-22 §B4.2", "AISC 360-22 text, read 2026-10-10", "ej.section.rect_tube.corner_radius.outside_coeff", "Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention", "engineer", "ej.section.rect_tube.corner_radius", "Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention", "engineer", "geometry.rect_tube.inside_dimensions", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.rect_tube.A", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.rect_tube.weight", "Engineering judgement (EOR): a custom tube's weight is on its nominal wall", "engineer", "material.steel.density", "AISC Manual 16th Ed., Part 17", "memory", "geometry.rect_tube.corner_centroids", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.rect_tube.I", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.rect_tube.Z", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.rect_tube.S", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "geometry.rect_tube.r", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "aisc360.CH3.midline_radius_coeff", "AISC 360-22 Commentary §H3", "AISC 360-22 text, read 2026-10-11", "aisc360.CH3.midline_area", "AISC 360-22 Commentary §H3, Eq. C-H3-2", "AISC 360-22 text, read 2026-10-11", "geometry.rect_tube.midline_perimeter", "AISC Manual Part 17, Properties of Geometric Sections", "memory", "ej.section.rect_tube.J", "Engineering judgement (EOR): J of a custom rectangular tube from its midline", "engineer", "aisc360.B4.1b.d.coeff", "AISC 360-22 §B4.1b(d)", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.d.width", "AISC 360-22 §B4.1b(d)", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.2.nominal_wall", "AISC 360-22 §B4.2", "AISC 360-22 text, read 2026-10-10", "aisc360.K1.3.rect_chord.wall_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "material.A1085_GrA.hss_rect.Fy", "AISC Manual Table 2-4", "memory", "material.A1085_GrA.hss_rect.Fu", "AISC Manual Table 2-4", "memory", "ej.weld.post_wall.fu_fy_min", "Engineering judgement (EOR): post wall at the weld covered by Check 5 while Fu/Fy >= 1.20", "engineer", "material.A500_GrB.hss_rect.Fy", "AISC Manual Table 2-4", "memory", "material.A500_GrB.hss_rect.Fu", "AISC Manual Table 2-4", "memory", "aisc360.K1.3.Fy_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "aisc360.K1.3.Fy_Fu_max", "AISC 360-22 §K1.3", "AISC 360-22 text, read 2026-10-11", "asce7.guard.component", "ASCE 7-22 §4.5.1.2", "memory", "ej.post.axial_dead_load", "Engineering judgement (EOR): post dead load", "engineer", "ej.section.orientation.rail_vertical", "Engineering judgement (EOR): a rectangular member's axes follow from its long side", "engineer", "ej.section.orientation.square", "Engineering judgement (EOR): a rectangular member's axes follow from its long side", "engineer", "ej.section.orientation.rail_horizontal", "Engineering judgement (EOR): a rectangular member's axes follow from its long side", "engineer", "aisc360.B4.1b.rect_hss.flange.lambda_p", "AISC 360-22 Table B4.1b, Case 17", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.flange.lambda_r", "AISC 360-22 Table B4.1b, Case 17", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.web.lambda_p", "AISC 360-22 Table B4.1b, Case 19", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1b.rect_hss.web.lambda_r", "AISC 360-22 Table B4.1b, Case 19", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-1", "AISC 360-22 Eq. F7-1", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.compact_no_local_buckling", "AISC 360-22 §F7.2(a), §F7.3(a)", "AISC 360-22 text, read 2026-10-11", "ej.flexure.unbraced_length", "Engineering judgement (EOR): unbraced length for lateral-torsional buckling", "engineer", "aisc360.eq.F7-10.coeff", "AISC 360-22 Eq. F7-10", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-10", "AISC 360-22 Eq. F7-10", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.4a.no_ltb_below_Lp", "AISC 360-22 §F7.4(a)", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.nominal_strength", "AISC 360-22 §F7", "AISC 360-22 text, read 2026-10-11", "ej.bending.biaxial_rect", "Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "engineer", "aisc360.F7.4.no_ltb_note", "AISC 360-22 §F7.4, User Note", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.H1-1b", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.K1-1.coeff", "AISC 360-22 Eq. K1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.K1-1", "AISC 360-22 Eq. K1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.K5.1.Be_cap", "AISC 360-22 Table K5.1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.K5-5", "AISC 360-22 Eq. K5-5", "AISC 360-22 text, read 2026-10-11", "aisc360.K5.nonuniform", "AISC 360-22 §K5", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.K5-6", "AISC 360-22 Eq. K5-6", "AISC 360-22 text, read 2026-10-11", "ej.weld.k5.case_mapping", "Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties", "engineer", "aisc360.eq.K5-7", "AISC 360-22 Eq. K5-7", "AISC 360-22 text, read 2026-10-11", "aisc360.J2.2a.throat.coeff", "AISC 360-22 §J2.2a", "memory", "aisc360.J2.2a.throat", "AISC 360-22 §J2.2a", "memory", "ej.weld.equal_width_fillet", "Engineering judgement (EOR): fillet model kept at equal widths", "engineer", "aisc360.J2.4.min_size", "AISC 360-22 Table J2.4", "memory", "ej.weld.max_size_not_applicable", "Engineering judgement (EOR): no maximum fillet size at a T-joint", "engineer", "aisc360.J2.2b.max_size_edges", "AISC 360-22 §J2.2b(b)", "memory", "material.E70XX.FEXX", "AISC 360-22 §J2.6; AWS A5.1", "memory", "aisc360.J2.5.fnw.coeff", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.fnw", "AISC 360-22 Table J2.5", "memory", "aisc360.J2.5.omega_w", "AISC 360-22 Table J2.5", "memory", "ej.weld.branch_kds", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld", "engineer", "aisc360.eq.J4-4.coeff", "AISC 360-22 Eq. J4-4", "memory", "aisc360.eq.J4-4", "AISC 360-22 Eq. J4-4", "memory", "aisc_manual.part9.base_metal", "AISC Manual Part 9, base metal at welds", "memory", "aisc360.J4.2.omega_rupture", "AISC 360-22 §J4.2(b)", "memory", "ej.weld.chord_wall.rect", "Engineering judgement (EOR): a rectangular chord's limit states not checked", "engineer", "ej.weld.post_wall_covered", "Engineering judgement (EOR): post wall at the weld covered by Check 5", "engineer", "aws.d1_1.thickness_min", "AWS D1.1/D1.1M:2020, Clause 1", "memory", "ej.weld.thin_material", "Engineering judgement (EOR): thin material at a weld is warned of, not stopped", "engineer", "aws.d1_1.scope", "AWS D1.1/D1.1M:2020, Clause 1", "memory", "ej.weld.line_method", "Engineering judgement (EOR): elastic weld as a line", "engineer", "ej.weld.no_bearing", "Engineering judgement (EOR): no bearing credit at the weld", "engineer", "aisc360.J2.4.fillet_strength", "AISC 360-22 Eq. J2-4", "memory", "ej.component.downward", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "engineer", "ej.component.midspan", "Engineering judgement (EOR): component load as a point load at midspan", "engineer", "aisc360.eq.F7-11.coeff", "AISC 360-22 Eq. F7-11", "AISC 360-22 text, read 2026-10-11", "aisc360.F7.4.inelastic_coeff", "AISC 360-22 §F7.4", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-11", "AISC 360-22 Eq. F7-11", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F7-8", "AISC 360-22 Eq. F7-8", "AISC 360-22 text, read 2026-10-11", "aisc_manual.t3-23.case7.Mx", "AISC Manual Table 3-23, Case 7", "memory", "aisc360.eq.F1-1.coeff_numerator", "AISC 360-22 Eq. F1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F1-1.coeff_max", "AISC 360-22 Eq. F1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F1-1.coeff_quarter", "AISC 360-22 Eq. F1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F1-1.coeff_center", "AISC 360-22 Eq. F1-1", "AISC 360-22 text, read 2026-10-11", "aisc360.eq.F1-1", "AISC 360-22 Eq. F1-1", "AISC 360-22 text, read 2026-10-11", "ej.weld.intermediate_simple_shear", "Engineering judgement (EOR): intermediate rail to post weld as a simple shear connection", "engineer", "ej.weld.intermediate_line_model", "Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post", "engineer", "ej.weld.intermediate_base_metal", "Engineering judgement (EOR): Check 4b base metal on both walls, lower governs", "engineer", "ej.weld.check4b.no_chord_demand", "Engineering judgement (EOR): no chord limit state demand at the intermediate rail", "engineer", "aisc_manual.t3-23.case1.R", "AISC Manual Table 3-23, Case 1", "memory", "aisc360.B4.1a.rect_hss.lambda_r", "AISC 360-22 Table B4.1a, Case 6", "AISC 360-22 text, read 2026-10-11", "aisc360.B4.1a.classification", "AISC 360-22 §B4.1a", "memory", "aisc360.CA7.K_fixed_free", "AISC 360-22 Comm. Table C-A-7.1, case (e)", "memory", "aisc360.E2.effective_length", "AISC 360-22 §E2", "memory", "ej.post.unbraced_length", "Engineering judgement (EOR): unbraced length is the post height", "engineer", "aisc360.eq.E3-4", "AISC 360-22 Eq. E3-4", "memory", "aisc360.E2.user_note.slenderness", "AISC 360-22 §E2, User Note", "memory", "aisc360.E2.user_note.slenderness.limit", "AISC 360-22 §E2, User Note", "memory", "aisc360.E3.branch_limit", "AISC 360-22 §E3(a), (b)", "memory", "aisc360.eq.E3-3", "AISC 360-22 Eq. E3-3", "memory", "aisc360.eq.E3-3.coeff", "AISC 360-22 Eq. E3-3", "memory", "aisc360.eq.E3-1", "AISC 360-22 Eq. E3-1", "memory", "aisc360.E1.omega_c", "AISC 360-22 §E1", "memory", "aisc_manual.t3-23.case22.M", "AISC Manual Table 3-23, Case 22", "memory", "aisc360.eq.A-8-5", "AISC 360-22 Eq. A-8-5", "memory", "ej.second_order.pe_length", "Engineering judgement (EOR): Pe at Lc = 2.1h", "engineer", "aisc360.app8.alpha_asd", "AISC 360-22 App. 8", "memory", "ej.second_order.limit", "Engineering judgement (EOR): second-order limit", "engineer", "ej.second_order.negligible", "Engineering judgement (EOR): second-order limit", "engineer", "aisc360.H1.1.threshold", "AISC 360-22 §H1.1", "memory", "aisc360.eq.H1-1b.coeff", "AISC 360-22 Eq. H1-1b", "memory", "aisc360.eq.D2-1", "AISC 360-22 Eq. D2-1", "memory", "aisc360.D2.omega_t", "AISC 360-22 §D2(a)", "memory", "aisc_manual.t3-23.case22.delta", "AISC Manual Table 3-23, Case 22", "memory", "ej.deflection.limit.post", "Engineering judgement (EOR): post deflection limit, not code", "engineer", "ej.weld.line.corner_radius_coeff", "Engineering judgement (EOR): weld line on the true rounded rectangle", "engineer", "ej.weld.line.rounded_rectangle", "Engineering judgement (EOR): weld line on the true rounded rectangle", "engineer", "aisc360.J2.4.kds_rect_hss", "AISC 360-22 §J2.4(a)(2)", "AISC 360-22 text, read 2026-10-11", "aisc360.K5.user_note.rect_hss_kds", "AISC 360-22 §K5, User Note", "AISC 360-22 text, read 2026-10-11", "material.A36.Fu", "AISC Manual Table 2-5", "memory", "ej.reaction.location", "Engineering judgement (EOR): reactions at the top of concrete, arm h", "engineer", "ej.combo.reaction", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "engineer", "ej.reaction.lateral_note", "Engineering judgement (EOR): one lateral set, any horizontal direction", "engineer")

= Dimensions

Every dimension as entered, and as the tool read it. A bare number is inches.

#table(columns: (1fr, auto, auto, auto), table.header(strong("Dimension"), strong("As entered"), strong("Read as"), strong("Inches")), "Span, post to post (c/c)", "6'-0\"", "6'-0\"", "72.00 in", "Post height h, top of concrete to top rail centerline", "42", "3'-6\"", "42.00 in", "Baseplate thickness t_p", "1/2", "1/2\"", "0.5000 in", "Baseplate B, parallel to the rail", "6", "6\"", "6.000 in", "Baseplate N, perpendicular to the rail", "8", "8\"", "8.000 in", "Fillet weld, top rail to post", "1/8", "1/8\"", "0.1250 in", "Fillet weld, post to baseplate", "3/16", "3/16\"", "0.1875 in", "Fillet weld, intermediate rail to post", "1/8", "1/8\"", "0.1250 in", "Top rail, custom rectangular tube: longer side H", "3", "3\"", "3.000 in", "Top rail, custom rectangular tube: shorter side B", "2", "2\"", "2.000 in", "Top rail, custom rectangular tube: nominal wall", "0.12", "0.12\"", "0.1200 in", "Post, custom rectangular tube: longer side H", "2", "2\"", "2.000 in", "Post, custom rectangular tube: shorter side B", "2", "2\"", "2.000 in", "Post, custom rectangular tube: nominal wall", "1/8", "1/8\"", "0.1250 in", "Intermediate rail, custom rectangular tube: longer side H", "2", "2\"", "2.000 in", "Intermediate rail, custom rectangular tube: shorter side B", "1", "1\"", "1.000 in", "Intermediate rail, custom rectangular tube: nominal wall", "0.083", "0.083\"", "0.08300 in")

#text("Directional strength increase at the post to baseplate weld: not elected (directional_increase = false).")

#text("Post to baseplate weld pattern: all around (base_pattern).")

Derived lengths, each computed in the calc where it is used:

#table(columns: (1fr, auto, auto, auto), table.header(strong("Derived length"), strong("Formula"), strong("Inches"), strong("Computed in")), "Post cantilever length, top of baseplate to top rail centerline", [$L_"post" = h - t_p$], "41.50 in", "Loading", "Eccentricity: rail centerline to the weld plane at the rail underside", [$e = frac(d_"rail", "2")$], "1.500 in", "Check 3", "Effective length, with the unbraced length taken as the post height h", [$L_c = K h$], "88.20 in", "Check 5")

= Section properties

#text("Top rail: Rect. tube 3 × 2 × 0.12 (custom), A500 Gr B (default).") Properties are computed below from the dimensions entered, on the design wall thickness of AISC 360-22 §B4.2; the weight is on the nominal wall.

#calcline([$H = "3.000 in"$], "Rect. tube 3 × 2 × 0.12 (custom): outside dimension of the longer side (3 as entered)", "Input")
#calcline([$B = "2.000 in"$], "Outside dimension of the shorter side (2 as entered)", "Input")
#calcline([$t_"nom" = "0.1200 in"$], "Nominal wall thickness (0.12 as entered)", "Input; Engineering judgement (EOR): a custom tube's wall is entered as the nominal wall")
#calcline([$display(t_"des" = "0.93" t_"nom" = "0.93" ("0.1200 in") = "0.1116 in")$], "Design wall thickness", "AISC 360-22 §B4.2")
#calcline([$display(R_o = "2" t_"des" = "2" ("0.1116 in") = "0.2232 in")$], "Outside corner radius", "Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention")
#calcline([$display(R_i = t_"des" = "0.1116 in")$], "Inside corner radius: the design wall", "Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention")
#calcline([$display(H_i = H - "2" t_"des" = ("3.000 in") - "2" ("0.1116 in") = "2.777 in")$], "Inside dimension of the longer side", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(B_i = B - "2" t_"des" = ("2.000 in") - "2" ("0.1116 in") = "1.777 in")$], "Inside dimension of the shorter side", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A_o = B H - ("4" - pi) R_o^("2") = ("2.000 in") ("3.000 in") - ("4" - pi) ("0.2232 in")^("2") = "5.957 in"^2)$], "Area within the outside outline", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A_i = B_i H_i - ("4" - pi) R_i^("2") = ("1.777 in") ("2.777 in") - ("4" - pi) ("0.1116 in")^("2") = "4.923 in"^2)$], "Area within the inside outline", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A = A_o - A_i = ("5.957 in"^2) - ("4.923 in"^2) = "1.034 in"^2)$], "Area (design wall)", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(R_"o,nom" = "2" t_"nom" = "2" ("0.1200 in") = "0.2400 in")$], "Outside corner radius on the nominal wall (for the weight)", "Engineering judgement (EOR): a custom tube's weight is on its nominal wall; Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention")
#calcline([$display(A_"nom" = B H - ("4" - pi) R_"o,nom"^("2") - ((B - "2" t_"nom") (H - "2" t_"nom") - ("4" - pi) t_"nom"^("2")) = ("2.000 in") ("3.000 in") - ("4" - pi) ("0.2400 in")^("2") - ((("2.000 in") - "2" ("0.1200 in")) (("3.000 in") - "2" ("0.1200 in")) - ("4" - pi) ("0.1200 in")^("2")) = "1.105 in"^2)$], "Area on the nominal wall (for the weight)", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$rho = "0.2836 lb/in"^3$], "Steel unit weight", "AISC Manual 16th Ed., Part 17")
#calcline([$display(W = rho A_"nom" = ("0.2836 lb/in"^3) ("1.105 in"^2) = "0.3134 lb/in")$], "Weight per unit length: steel unit weight times the area on the nominal wall", "Engineering judgement (EOR): a custom tube's weight is on its nominal wall")
#calcline([$display(c_("sq,xo") = frac(H, "2") - frac(R_o, "2") = frac(("3.000 in"), "2") - frac(("0.2232 in"), "2") = "1.388 in")$], "Outside outline, x axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,xo") = frac(H, "2") - R_o + frac("4" R_o, "3" pi) = frac(("3.000 in"), "2") - ("0.2232 in") + frac("4" ("0.2232 in"), "3" dot pi) = "1.372 in")$], "Outside outline, x axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"xo" = frac(B H^("3"), "12") - "4" (frac(R_o^("4"), "12") + R_o^("2") c_("sq,xo")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_o^("4") + frac(pi R_o^("2"), "4") c_("qc,xo")^("2"))) = frac(("2.000 in") ("3.000 in")^("3"), "12") - "4" dot (frac(("0.2232 in")^("4"), "12") + ("0.2232 in")^("2") ("1.388 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.2232 in")^("4") + frac(pi ("0.2232 in")^("2"), "4") ("1.372 in")^("2"))) = "4.410 in"^4)$], "Outside outline: moment of inertia about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"xo" = frac(B H^("2"), "4") - "4" (R_o^("2") c_("sq,xo") - frac(pi R_o^("2"), "4") c_("qc,xo")) = frac(("2.000 in") ("3.000 in")^("2"), "4") - "4" (("0.2232 in")^("2") ("1.388 in") - frac(pi ("0.2232 in")^("2"), "4") ("1.372 in")) = "4.438 in"^3)$], "Outside outline: plastic section modulus about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("sq,xi") = frac(H_i, "2") - frac(R_i, "2") = frac(("2.777 in"), "2") - frac(("0.1116 in"), "2") = "1.333 in")$], "Inside outline, x axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,xi") = frac(H_i, "2") - R_i + frac("4" R_i, "3" pi) = frac(("2.777 in"), "2") - ("0.1116 in") + frac("4" ("0.1116 in"), "3" dot pi) = "1.324 in")$], "Inside outline, x axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"xi" = frac(B_i H_i^("3"), "12") - "4" (frac(R_i^("4"), "12") + R_i^("2") c_("sq,xi")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_i^("4") + frac(pi R_i^("2"), "4") c_("qc,xi")^("2"))) = frac(("1.777 in") ("2.777 in")^("3"), "12") - "4" dot (frac(("0.1116 in")^("4"), "12") + ("0.1116 in")^("2") ("1.333 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.1116 in")^("4") + frac(pi ("0.1116 in")^("2"), "4") ("1.324 in")^("2"))) = "3.150 in"^4)$], "Inside outline: moment of inertia about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"xi" = frac(B_i H_i^("2"), "4") - "4" (R_i^("2") c_("sq,xi") - frac(pi R_i^("2"), "4") c_("qc,xi")) = frac(("1.777 in") ("2.777 in")^("2"), "4") - "4" (("0.1116 in")^("2") ("1.333 in") - frac(pi ("0.1116 in")^("2"), "4") ("1.324 in")) = "3.410 in"^3)$], "Inside outline: plastic section modulus about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_x = I_"xo" - I_"xi" = ("4.410 in"^4) - ("3.150 in"^4) = "1.260 in"^4)$], "Moment of inertia about the x axis, the strong axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(S_x = frac(I_x, frac(H, "2")) = frac(("1.260 in"^4), frac(("3.000 in"), "2")) = "0.8398 in"^3)$], "Elastic section modulus about the x axis, the strong axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_x = Z_"xo" - Z_"xi" = ("4.438 in"^3) - ("3.410 in"^3) = "1.028 in"^3)$], "Plastic section modulus about the x axis, the strong axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(r_x = sqrt(frac(I_x, A)) = sqrt(frac(("1.260 in"^4), ("1.034 in"^2))) = "1.104 in")$], "Radius of gyration about the x axis, the strong axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("sq,yo") = frac(B, "2") - frac(R_o, "2") = frac(("2.000 in"), "2") - frac(("0.2232 in"), "2") = "0.8884 in")$], "Outside outline, y axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,yo") = frac(B, "2") - R_o + frac("4" R_o, "3" pi) = frac(("2.000 in"), "2") - ("0.2232 in") + frac("4" ("0.2232 in"), "3" dot pi) = "0.8715 in")$], "Outside outline, y axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"yo" = frac(H B^("3"), "12") - "4" (frac(R_o^("4"), "12") + R_o^("2") c_("sq,yo")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_o^("4") + frac(pi R_o^("2"), "4") c_("qc,yo")^("2"))) = frac(("3.000 in") ("2.000 in")^("3"), "12") - "4" dot (frac(("0.2232 in")^("4"), "12") + ("0.2232 in")^("2") ("0.8884 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.2232 in")^("4") + frac(pi ("0.2232 in")^("2"), "4") ("0.8715 in")^("2"))) = "1.961 in"^4)$], "Outside outline: moment of inertia about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"yo" = frac(H B^("2"), "4") - "4" (R_o^("2") c_("sq,yo") - frac(pi R_o^("2"), "4") c_("qc,yo")) = frac(("3.000 in") ("2.000 in")^("2"), "4") - "4" (("0.2232 in")^("2") ("0.8884 in") - frac(pi ("0.2232 in")^("2"), "4") ("0.8715 in")) = "2.959 in"^3)$], "Outside outline: plastic section modulus about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("sq,yi") = frac(B_i, "2") - frac(R_i, "2") = frac(("1.777 in"), "2") - frac(("0.1116 in"), "2") = "0.8326 in")$], "Inside outline, y axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,yi") = frac(B_i, "2") - R_i + frac("4" R_i, "3" pi) = frac(("1.777 in"), "2") - ("0.1116 in") + frac("4" ("0.1116 in"), "3" dot pi) = "0.8242 in")$], "Inside outline, y axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"yi" = frac(H_i B_i^("3"), "12") - "4" (frac(R_i^("4"), "12") + R_i^("2") c_("sq,yi")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_i^("4") + frac(pi R_i^("2"), "4") c_("qc,yi")^("2"))) = frac(("2.777 in") ("1.777 in")^("3"), "12") - "4" dot (frac(("0.1116 in")^("4"), "12") + ("0.1116 in")^("2") ("0.8326 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.1116 in")^("4") + frac(pi ("0.1116 in")^("2"), "4") ("0.8242 in")^("2"))) = "1.290 in"^4)$], "Inside outline: moment of inertia about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"yi" = frac(H_i B_i^("2"), "4") - "4" (R_i^("2") c_("sq,yi") - frac(pi R_i^("2"), "4") c_("qc,yi")) = frac(("2.777 in") ("1.777 in")^("2"), "4") - "4" (("0.1116 in")^("2") ("0.8326 in") - frac(pi ("0.1116 in")^("2"), "4") ("0.8242 in")) = "2.182 in"^3)$], "Inside outline: plastic section modulus about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_y = I_"yo" - I_"yi" = ("1.961 in"^4) - ("1.290 in"^4) = "0.6713 in"^4)$], "Moment of inertia about the y axis, the weak axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(S_y = frac(I_y, frac(B, "2")) = frac(("0.6713 in"^4), frac(("2.000 in"), "2")) = "0.6713 in"^3)$], "Elastic section modulus about the y axis, the weak axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_y = Z_"yo" - Z_"yi" = ("2.959 in"^3) - ("2.182 in"^3) = "0.7770 in"^3)$], "Plastic section modulus about the y axis, the weak axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(r_y = sqrt(frac(I_y, A)) = sqrt(frac(("0.6713 in"^4), ("1.034 in"^2))) = "0.8057 in")$], "Radius of gyration about the y axis, the weak axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(R_m = "1.5" t_"des" = "1.5" ("0.1116 in") = "0.1674 in")$], "Corner radius of the wall's midline", "AISC 360-22 Commentary §H3")
#calcline([$display(A_m = (H - t_"des") (B - t_"des") - ("4" - pi) R_m^("2") = (("3.000 in") - ("0.1116 in")) (("2.000 in") - ("0.1116 in")) - ("4" - pi) ("0.1674 in")^("2") = "5.430 in"^2)$], "Area enclosed by the wall's midline", "AISC 360-22 Commentary §H3, Eq. C-H3-2")
#calcline([$display(p_m = "2" (H - t_"des" + B - t_"des") - "2" ("4" - pi) R_m = "2" (("3.000 in") - ("0.1116 in") + ("2.000 in") - ("0.1116 in")) - "2" dot ("4" - pi) ("0.1674 in") = "9.266 in")$], "Perimeter of the wall's midline", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(J = frac("4" A_m^("2") t_"des", p_m) = frac("4" ("5.430 in"^2)^("2") ("0.1116 in"), ("9.266 in")) = "1.421 in"^4)$], "Torsional constant", "Engineering judgement (EOR): J of a custom rectangular tube from its midline")
#calcline([$display(b slash t = frac(B - "3" t_"des", t_"des") = frac(("2.000 in") - "3" ("0.1116 in"), ("0.1116 in")) = "14.92")$], "Width-to-thickness ratio of the shorter walls, computed (design wall)", "AISC 360-22 §B4.1b(d)")
#calcline([$display(h slash t = frac(H - "3" t_"des", t_"des") = frac(("3.000 in") - "3" ("0.1116 in"), ("0.1116 in")) = "23.88")$], "Width-to-thickness ratio of the longer walls, computed (design wall)", "AISC 360-22 §B4.1b(d)")
#calcline([$"long_side = vertical"$ #h(6pt) $arrow.r$ #h(6pt) *#"Long side vertical: a vertical load bends the strong axis (x); the horizontal guard load bends the weak axis (y)."*], "Orientation, and the axis each load bends", "Engineering judgement (EOR): a rectangular member's axes follow from its long side")

#text("Post: Rect. tube 2 × 2 × 0.125 (custom), A1085 Gr A.") Properties are computed below from the dimensions entered, on the design wall thickness of AISC 360-22 §B4.2; the weight is on the nominal wall.

#calcline([$H = "2.000 in"$], "Rect. tube 2 × 2 × 0.125 (custom): outside dimension of the longer side (2 as entered)", "Input")
#calcline([$B = "2.000 in"$], "Outside dimension of the shorter side (2 as entered)", "Input")
#calcline([$t_"nom" = "0.1250 in"$], "Nominal wall thickness (1/8 as entered)", "Input; Engineering judgement (EOR): a custom tube's wall is entered as the nominal wall")
#calcline([$display(t_"des" = t_"nom" = "0.1250 in")$], "Design wall thickness: the nominal wall, A1085 Gr A", "AISC 360-22 §B4.2")
#calcline([$display(R_o = "2" t_"des" = "2" ("0.1250 in") = "0.2500 in")$], "Outside corner radius", "Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention")
#calcline([$display(R_i = t_"des" = "0.1250 in")$], "Inside corner radius: the design wall", "Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention")
#calcline([$display(H_i = H - "2" t_"des" = ("2.000 in") - "2" ("0.1250 in") = "1.750 in")$], "Inside dimension of the longer side", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(B_i = B - "2" t_"des" = ("2.000 in") - "2" ("0.1250 in") = "1.750 in")$], "Inside dimension of the shorter side", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A_o = B H - ("4" - pi) R_o^("2") = ("2.000 in") ("2.000 in") - ("4" - pi) ("0.2500 in")^("2") = "3.946 in"^2)$], "Area within the outside outline", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A_i = B_i H_i - ("4" - pi) R_i^("2") = ("1.750 in") ("1.750 in") - ("4" - pi) ("0.1250 in")^("2") = "3.049 in"^2)$], "Area within the inside outline", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A = A_o - A_i = ("3.946 in"^2) - ("3.049 in"^2) = "0.8973 in"^2)$], "Area (design wall)", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(R_"o,nom" = "2" t_"nom" = "2" ("0.1250 in") = "0.2500 in")$], "Outside corner radius on the nominal wall (for the weight)", "Engineering judgement (EOR): a custom tube's weight is on its nominal wall; Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention")
#calcline([$display(A_"nom" = B H - ("4" - pi) R_"o,nom"^("2") - ((B - "2" t_"nom") (H - "2" t_"nom") - ("4" - pi) t_"nom"^("2")) = ("2.000 in") ("2.000 in") - ("4" - pi) ("0.2500 in")^("2") - ((("2.000 in") - "2" ("0.1250 in")) (("2.000 in") - "2" ("0.1250 in")) - ("4" - pi) ("0.1250 in")^("2")) = "0.8973 in"^2)$], "Area on the nominal wall (for the weight)", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$rho = "0.2836 lb/in"^3$], "Steel unit weight", "AISC Manual 16th Ed., Part 17")
#calcline([$display(W = rho A_"nom" = ("0.2836 lb/in"^3) ("0.8973 in"^2) = "0.2544 lb/in")$], "Weight per unit length: steel unit weight times the area on the nominal wall", "Engineering judgement (EOR): a custom tube's weight is on its nominal wall")
#calcline([$display(c_("sq,xo") = frac(H, "2") - frac(R_o, "2") = frac(("2.000 in"), "2") - frac(("0.2500 in"), "2") = "0.8750 in")$], "Outside outline, x axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,xo") = frac(H, "2") - R_o + frac("4" R_o, "3" pi) = frac(("2.000 in"), "2") - ("0.2500 in") + frac("4" ("0.2500 in"), "3" dot pi) = "0.8561 in")$], "Outside outline, x axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"xo" = frac(B H^("3"), "12") - "4" (frac(R_o^("4"), "12") + R_o^("2") c_("sq,xo")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_o^("4") + frac(pi R_o^("2"), "4") c_("qc,xo")^("2"))) = frac(("2.000 in") ("2.000 in")^("3"), "12") - "4" dot (frac(("0.2500 in")^("4"), "12") + ("0.2500 in")^("2") ("0.8750 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.2500 in")^("4") + frac(pi ("0.2500 in")^("2"), "4") ("0.8561 in")^("2"))) = "1.285 in"^4)$], "Outside outline: moment of inertia about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"xo" = frac(B H^("2"), "4") - "4" (R_o^("2") c_("sq,xo") - frac(pi R_o^("2"), "4") c_("qc,xo")) = frac(("2.000 in") ("2.000 in")^("2"), "4") - "4" (("0.2500 in")^("2") ("0.8750 in") - frac(pi ("0.2500 in")^("2"), "4") ("0.8561 in")) = "1.949 in"^3)$], "Outside outline: plastic section modulus about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("sq,xi") = frac(H_i, "2") - frac(R_i, "2") = frac(("1.750 in"), "2") - frac(("0.1250 in"), "2") = "0.8125 in")$], "Inside outline, x axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,xi") = frac(H_i, "2") - R_i + frac("4" R_i, "3" pi) = frac(("1.750 in"), "2") - ("0.1250 in") + frac("4" ("0.1250 in"), "3" dot pi) = "0.8031 in")$], "Inside outline, x axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"xi" = frac(B_i H_i^("3"), "12") - "4" (frac(R_i^("4"), "12") + R_i^("2") c_("sq,xi")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_i^("4") + frac(pi R_i^("2"), "4") c_("qc,xi")^("2"))) = frac(("1.750 in") ("1.750 in")^("3"), "12") - "4" dot (frac(("0.1250 in")^("4"), "12") + ("0.1250 in")^("2") ("0.8125 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.1250 in")^("4") + frac(pi ("0.1250 in")^("2"), "4") ("0.8031 in")^("2"))) = "0.7719 in"^4)$], "Inside outline: moment of inertia about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"xi" = frac(B_i H_i^("2"), "4") - "4" (R_i^("2") c_("sq,xi") - frac(pi R_i^("2"), "4") c_("qc,xi")) = frac(("1.750 in") ("1.750 in")^("2"), "4") - "4" (("0.1250 in")^("2") ("0.8125 in") - frac(pi ("0.1250 in")^("2"), "4") ("0.8031 in")) = "1.328 in"^3)$], "Inside outline: plastic section modulus about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_x = I_"xo" - I_"xi" = ("1.285 in"^4) - ("0.7719 in"^4) = "0.5134 in"^4)$], "Moment of inertia about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(S_x = frac(I_x, frac(H, "2")) = frac(("0.5134 in"^4), frac(("2.000 in"), "2")) = "0.5134 in"^3)$], "Elastic section modulus about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_x = Z_"xo" - Z_"xi" = ("1.949 in"^3) - ("1.328 in"^3) = "0.6209 in"^3)$], "Plastic section modulus about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(r_x = sqrt(frac(I_x, A)) = sqrt(frac(("0.5134 in"^4), ("0.8973 in"^2))) = "0.7565 in")$], "Radius of gyration about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("sq,yo") = frac(B, "2") - frac(R_o, "2") = frac(("2.000 in"), "2") - frac(("0.2500 in"), "2") = "0.8750 in")$], "Outside outline, y axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,yo") = frac(B, "2") - R_o + frac("4" R_o, "3" pi) = frac(("2.000 in"), "2") - ("0.2500 in") + frac("4" ("0.2500 in"), "3" dot pi) = "0.8561 in")$], "Outside outline, y axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"yo" = frac(H B^("3"), "12") - "4" (frac(R_o^("4"), "12") + R_o^("2") c_("sq,yo")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_o^("4") + frac(pi R_o^("2"), "4") c_("qc,yo")^("2"))) = frac(("2.000 in") ("2.000 in")^("3"), "12") - "4" dot (frac(("0.2500 in")^("4"), "12") + ("0.2500 in")^("2") ("0.8750 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.2500 in")^("4") + frac(pi ("0.2500 in")^("2"), "4") ("0.8561 in")^("2"))) = "1.285 in"^4)$], "Outside outline: moment of inertia about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"yo" = frac(H B^("2"), "4") - "4" (R_o^("2") c_("sq,yo") - frac(pi R_o^("2"), "4") c_("qc,yo")) = frac(("2.000 in") ("2.000 in")^("2"), "4") - "4" (("0.2500 in")^("2") ("0.8750 in") - frac(pi ("0.2500 in")^("2"), "4") ("0.8561 in")) = "1.949 in"^3)$], "Outside outline: plastic section modulus about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("sq,yi") = frac(B_i, "2") - frac(R_i, "2") = frac(("1.750 in"), "2") - frac(("0.1250 in"), "2") = "0.8125 in")$], "Inside outline, y axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,yi") = frac(B_i, "2") - R_i + frac("4" R_i, "3" pi) = frac(("1.750 in"), "2") - ("0.1250 in") + frac("4" ("0.1250 in"), "3" dot pi) = "0.8031 in")$], "Inside outline, y axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"yi" = frac(H_i B_i^("3"), "12") - "4" (frac(R_i^("4"), "12") + R_i^("2") c_("sq,yi")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_i^("4") + frac(pi R_i^("2"), "4") c_("qc,yi")^("2"))) = frac(("1.750 in") ("1.750 in")^("3"), "12") - "4" dot (frac(("0.1250 in")^("4"), "12") + ("0.1250 in")^("2") ("0.8125 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.1250 in")^("4") + frac(pi ("0.1250 in")^("2"), "4") ("0.8031 in")^("2"))) = "0.7719 in"^4)$], "Inside outline: moment of inertia about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"yi" = frac(H_i B_i^("2"), "4") - "4" (R_i^("2") c_("sq,yi") - frac(pi R_i^("2"), "4") c_("qc,yi")) = frac(("1.750 in") ("1.750 in")^("2"), "4") - "4" (("0.1250 in")^("2") ("0.8125 in") - frac(pi ("0.1250 in")^("2"), "4") ("0.8031 in")) = "1.328 in"^3)$], "Inside outline: plastic section modulus about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_y = I_"yo" - I_"yi" = ("1.285 in"^4) - ("0.7719 in"^4) = "0.5134 in"^4)$], "Moment of inertia about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(S_y = frac(I_y, frac(B, "2")) = frac(("0.5134 in"^4), frac(("2.000 in"), "2")) = "0.5134 in"^3)$], "Elastic section modulus about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_y = Z_"yo" - Z_"yi" = ("1.949 in"^3) - ("1.328 in"^3) = "0.6209 in"^3)$], "Plastic section modulus about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(r_y = sqrt(frac(I_y, A)) = sqrt(frac(("0.5134 in"^4), ("0.8973 in"^2))) = "0.7565 in")$], "Radius of gyration about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(R_m = "1.5" t_"des" = "1.5" ("0.1250 in") = "0.1875 in")$], "Corner radius of the wall's midline", "AISC 360-22 Commentary §H3")
#calcline([$display(A_m = (H - t_"des") (B - t_"des") - ("4" - pi) R_m^("2") = (("2.000 in") - ("0.1250 in")) (("2.000 in") - ("0.1250 in")) - ("4" - pi) ("0.1875 in")^("2") = "3.485 in"^2)$], "Area enclosed by the wall's midline", "AISC 360-22 Commentary §H3, Eq. C-H3-2")
#calcline([$display(p_m = "2" (H - t_"des" + B - t_"des") - "2" ("4" - pi) R_m = "2" (("2.000 in") - ("0.1250 in") + ("2.000 in") - ("0.1250 in")) - "2" dot ("4" - pi) ("0.1875 in") = "7.178 in")$], "Perimeter of the wall's midline", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(J = frac("4" A_m^("2") t_"des", p_m) = frac("4" ("3.485 in"^2)^("2") ("0.1250 in"), ("7.178 in")) = "0.8462 in"^4)$], "Torsional constant", "Engineering judgement (EOR): J of a custom rectangular tube from its midline")
#calcline([$display(b slash t = frac(B - "3" t_"des", t_"des") = frac(("2.000 in") - "3" ("0.1250 in"), ("0.1250 in")) = "13.00")$], "Width-to-thickness ratio of the shorter walls, computed (design wall)", "AISC 360-22 §B4.1b(d)")
#calcline([$display(h slash t = frac(H - "3" t_"des", t_"des") = frac(("2.000 in") - "3" ("0.1250 in"), ("0.1250 in")) = "13.00")$], "Width-to-thickness ratio of the longer walls, computed (design wall)", "AISC 360-22 §B4.1b(d)")
#calcline([$"Square section"$ #h(6pt) $arrow.r$ #h(6pt) *#"Square section: both axes have the same properties, and no orientation is entered. The calc names the axis a vertical load bends (for a post, a load across the guard) x, and the other y."*], "Orientation, and the axis each load bends", "Engineering judgement (EOR): a rectangular member's axes follow from its long side")

#text("Intermediate rail: Rect. tube 2 × 1 × 0.083 (custom), A500 Gr B (default).") Properties are computed below from the dimensions entered, on the design wall thickness of AISC 360-22 §B4.2; the weight is on the nominal wall.

#calcline([$H = "2.000 in"$], "Rect. tube 2 × 1 × 0.083 (custom): outside dimension of the longer side (2 as entered)", "Input")
#calcline([$B = "1.000 in"$], "Outside dimension of the shorter side (1 as entered)", "Input")
#calcline([$t_"nom" = "0.08300 in"$], "Nominal wall thickness (0.083 as entered)", "Input; Engineering judgement (EOR): a custom tube's wall is entered as the nominal wall")
#calcline([$display(t_"des" = "0.93" t_"nom" = "0.93" ("0.08300 in") = "0.07719 in")$], "Design wall thickness", "AISC 360-22 §B4.2")
#calcline([$display(R_o = "2" t_"des" = "2" ("0.07719 in") = "0.1544 in")$], "Outside corner radius", "Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention")
#calcline([$display(R_i = t_"des" = "0.07719 in")$], "Inside corner radius: the design wall", "Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention")
#calcline([$display(H_i = H - "2" t_"des" = ("2.000 in") - "2" ("0.07719 in") = "1.846 in")$], "Inside dimension of the longer side", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(B_i = B - "2" t_"des" = ("1.000 in") - "2" ("0.07719 in") = "0.8456 in")$], "Inside dimension of the shorter side", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A_o = B H - ("4" - pi) R_o^("2") = ("1.000 in") ("2.000 in") - ("4" - pi) ("0.1544 in")^("2") = "1.980 in"^2)$], "Area within the outside outline", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A_i = B_i H_i - ("4" - pi) R_i^("2") = ("0.8456 in") ("1.846 in") - ("4" - pi) ("0.07719 in")^("2") = "1.556 in"^2)$], "Area within the inside outline", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(A = A_o - A_i = ("1.980 in"^2) - ("1.556 in"^2) = "0.4240 in"^2)$], "Area (design wall)", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(R_"o,nom" = "2" t_"nom" = "2" ("0.08300 in") = "0.1660 in")$], "Outside corner radius on the nominal wall (for the weight)", "Engineering judgement (EOR): a custom tube's weight is on its nominal wall; Engineering judgement (EOR): a custom rectangular tube's corners follow AISC's convention")
#calcline([$display(A_"nom" = B H - ("4" - pi) R_"o,nom"^("2") - ((B - "2" t_"nom") (H - "2" t_"nom") - ("4" - pi) t_"nom"^("2")) = ("1.000 in") ("2.000 in") - ("4" - pi) ("0.1660 in")^("2") - ((("1.000 in") - "2" ("0.08300 in")) (("2.000 in") - "2" ("0.08300 in")) - ("4" - pi) ("0.08300 in")^("2")) = "0.4527 in"^2)$], "Area on the nominal wall (for the weight)", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$rho = "0.2836 lb/in"^3$], "Steel unit weight", "AISC Manual 16th Ed., Part 17")
#calcline([$display(W = rho A_"nom" = ("0.2836 lb/in"^3) ("0.4527 in"^2) = "0.1284 lb/in")$], "Weight per unit length: steel unit weight times the area on the nominal wall", "Engineering judgement (EOR): a custom tube's weight is on its nominal wall")
#calcline([$display(c_("sq,xo") = frac(H, "2") - frac(R_o, "2") = frac(("2.000 in"), "2") - frac(("0.1544 in"), "2") = "0.9228 in")$], "Outside outline, x axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,xo") = frac(H, "2") - R_o + frac("4" R_o, "3" pi) = frac(("2.000 in"), "2") - ("0.1544 in") + frac("4" ("0.1544 in"), "3" dot pi) = "0.9111 in")$], "Outside outline, x axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"xo" = frac(B H^("3"), "12") - "4" (frac(R_o^("4"), "12") + R_o^("2") c_("sq,xo")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_o^("4") + frac(pi R_o^("2"), "4") c_("qc,xo")^("2"))) = frac(("1.000 in") ("2.000 in")^("3"), "12") - "4" dot (frac(("0.1544 in")^("4"), "12") + ("0.1544 in")^("2") ("0.9228 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.1544 in")^("4") + frac(pi ("0.1544 in")^("2"), "4") ("0.9111 in")^("2"))) = "0.6476 in"^4)$], "Outside outline: moment of inertia about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"xo" = frac(B H^("2"), "4") - "4" (R_o^("2") c_("sq,xo") - frac(pi R_o^("2"), "4") c_("qc,xo")) = frac(("1.000 in") ("2.000 in")^("2"), "4") - "4" (("0.1544 in")^("2") ("0.9228 in") - frac(pi ("0.1544 in")^("2"), "4") ("0.9111 in")) = "0.9802 in"^3)$], "Outside outline: plastic section modulus about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("sq,xi") = frac(H_i, "2") - frac(R_i, "2") = frac(("1.846 in"), "2") - frac(("0.07719 in"), "2") = "0.8842 in")$], "Inside outline, x axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,xi") = frac(H_i, "2") - R_i + frac("4" R_i, "3" pi) = frac(("1.846 in"), "2") - ("0.07719 in") + frac("4" ("0.07719 in"), "3" dot pi) = "0.8784 in")$], "Inside outline, x axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"xi" = frac(B_i H_i^("3"), "12") - "4" (frac(R_i^("4"), "12") + R_i^("2") c_("sq,xi")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_i^("4") + frac(pi R_i^("2"), "4") c_("qc,xi")^("2"))) = frac(("0.8456 in") ("1.846 in")^("3"), "12") - "4" dot (frac(("0.07719 in")^("4"), "12") + ("0.07719 in")^("2") ("0.8842 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.07719 in")^("4") + frac(pi ("0.07719 in")^("2"), "4") ("0.8784 in")^("2"))) = "0.4388 in"^4)$], "Inside outline: moment of inertia about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"xi" = frac(B_i H_i^("2"), "4") - "4" (R_i^("2") c_("sq,xi") - frac(pi R_i^("2"), "4") c_("qc,xi")) = frac(("0.8456 in") ("1.846 in")^("2"), "4") - "4" (("0.07719 in")^("2") ("0.8842 in") - frac(pi ("0.07719 in")^("2"), "4") ("0.8784 in")) = "0.7155 in"^3)$], "Inside outline: plastic section modulus about the x axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_x = I_"xo" - I_"xi" = ("0.6476 in"^4) - ("0.4388 in"^4) = "0.2088 in"^4)$], "Moment of inertia about the x axis, the strong axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(S_x = frac(I_x, frac(H, "2")) = frac(("0.2088 in"^4), frac(("2.000 in"), "2")) = "0.2088 in"^3)$], "Elastic section modulus about the x axis, the strong axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_x = Z_"xo" - Z_"xi" = ("0.9802 in"^3) - ("0.7155 in"^3) = "0.2648 in"^3)$], "Plastic section modulus about the x axis, the strong axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(r_x = sqrt(frac(I_x, A)) = sqrt(frac(("0.2088 in"^4), ("0.4240 in"^2))) = "0.7017 in")$], "Radius of gyration about the x axis, the strong axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("sq,yo") = frac(B, "2") - frac(R_o, "2") = frac(("1.000 in"), "2") - frac(("0.1544 in"), "2") = "0.4228 in")$], "Outside outline, y axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,yo") = frac(B, "2") - R_o + frac("4" R_o, "3" pi) = frac(("1.000 in"), "2") - ("0.1544 in") + frac("4" ("0.1544 in"), "3" dot pi) = "0.4111 in")$], "Outside outline, y axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"yo" = frac(H B^("3"), "12") - "4" (frac(R_o^("4"), "12") + R_o^("2") c_("sq,yo")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_o^("4") + frac(pi R_o^("2"), "4") c_("qc,yo")^("2"))) = frac(("2.000 in") ("1.000 in")^("3"), "12") - "4" dot (frac(("0.1544 in")^("4"), "12") + ("0.1544 in")^("2") ("0.4228 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.1544 in")^("4") + frac(pi ("0.1544 in")^("2"), "4") ("0.4111 in")^("2"))) = "0.1622 in"^4)$], "Outside outline: moment of inertia about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"yo" = frac(H B^("2"), "4") - "4" (R_o^("2") c_("sq,yo") - frac(pi R_o^("2"), "4") c_("qc,yo")) = frac(("2.000 in") ("1.000 in")^("2"), "4") - "4" (("0.1544 in")^("2") ("0.4228 in") - frac(pi ("0.1544 in")^("2"), "4") ("0.4111 in")) = "0.4905 in"^3)$], "Outside outline: plastic section modulus about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("sq,yi") = frac(B_i, "2") - frac(R_i, "2") = frac(("0.8456 in"), "2") - frac(("0.07719 in"), "2") = "0.3842 in")$], "Inside outline, y axis: distance to the centroid of a corner square", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(c_("qc,yi") = frac(B_i, "2") - R_i + frac("4" R_i, "3" pi) = frac(("0.8456 in"), "2") - ("0.07719 in") + frac("4" ("0.07719 in"), "3" dot pi) = "0.3784 in")$], "Inside outline, y axis: distance to the centroid of a corner's quarter circle", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_"yi" = frac(H_i B_i^("3"), "12") - "4" (frac(R_i^("4"), "12") + R_i^("2") c_("sq,yi")^("2") - ((frac(pi, "16") - frac("4", "9" pi)) R_i^("4") + frac(pi R_i^("2"), "4") c_("qc,yi")^("2"))) = frac(("1.846 in") ("0.8456 in")^("3"), "12") - "4" dot (frac(("0.07719 in")^("4"), "12") + ("0.07719 in")^("2") ("0.3842 in")^("2") - ((frac(pi, "16") - frac("4", "9" dot pi)) ("0.07719 in")^("4") + frac(pi ("0.07719 in")^("2"), "4") ("0.3784 in")^("2"))) = "0.09216 in"^4)$], "Inside outline: moment of inertia about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_"yi" = frac(H_i B_i^("2"), "4") - "4" (R_i^("2") c_("sq,yi") - frac(pi R_i^("2"), "4") c_("qc,yi")) = frac(("1.846 in") ("0.8456 in")^("2"), "4") - "4" (("0.07719 in")^("2") ("0.3842 in") - frac(pi ("0.07719 in")^("2"), "4") ("0.3784 in")) = "0.3279 in"^3)$], "Inside outline: plastic section modulus about the y axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(I_y = I_"yo" - I_"yi" = ("0.1622 in"^4) - ("0.09216 in"^4) = "0.07006 in"^4)$], "Moment of inertia about the y axis, the weak axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(S_y = frac(I_y, frac(B, "2")) = frac(("0.07006 in"^4), frac(("1.000 in"), "2")) = "0.1401 in"^3)$], "Elastic section modulus about the y axis, the weak axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(Z_y = Z_"yo" - Z_"yi" = ("0.4905 in"^3) - ("0.3279 in"^3) = "0.1626 in"^3)$], "Plastic section modulus about the y axis, the weak axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(r_y = sqrt(frac(I_y, A)) = sqrt(frac(("0.07006 in"^4), ("0.4240 in"^2))) = "0.4065 in")$], "Radius of gyration about the y axis, the weak axis", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(R_m = "1.5" t_"des" = "1.5" ("0.07719 in") = "0.1158 in")$], "Corner radius of the wall's midline", "AISC 360-22 Commentary §H3")
#calcline([$display(A_m = (H - t_"des") (B - t_"des") - ("4" - pi) R_m^("2") = (("2.000 in") - ("0.07719 in")) (("1.000 in") - ("0.07719 in")) - ("4" - pi) ("0.1158 in")^("2") = "1.763 in"^2)$], "Area enclosed by the wall's midline", "AISC 360-22 Commentary §H3, Eq. C-H3-2")
#calcline([$display(p_m = "2" (H - t_"des" + B - t_"des") - "2" ("4" - pi) R_m = "2" (("2.000 in") - ("0.07719 in") + ("1.000 in") - ("0.07719 in")) - "2" dot ("4" - pi) ("0.1158 in") = "5.492 in")$], "Perimeter of the wall's midline", "AISC Manual Part 17, Properties of Geometric Sections")
#calcline([$display(J = frac("4" A_m^("2") t_"des", p_m) = frac("4" ("1.763 in"^2)^("2") ("0.07719 in"), ("5.492 in")) = "0.1747 in"^4)$], "Torsional constant", "Engineering judgement (EOR): J of a custom rectangular tube from its midline")
#calcline([$display(b slash t = frac(B - "3" t_"des", t_"des") = frac(("1.000 in") - "3" ("0.07719 in"), ("0.07719 in")) = "9.955")$], "Width-to-thickness ratio of the shorter walls, computed (design wall)", "AISC 360-22 §B4.1b(d)")
#calcline([$display(h slash t = frac(H - "3" t_"des", t_"des") = frac(("2.000 in") - "3" ("0.07719 in"), ("0.07719 in")) = "22.91")$], "Width-to-thickness ratio of the longer walls, computed (design wall)", "AISC 360-22 §B4.1b(d)")
#calcline([$"long_side = horizontal"$ #h(6pt) $arrow.r$ #h(6pt) *#"Long side horizontal: a vertical load bends the weak axis (y); the horizontal guard load bends the strong axis (x)."*], "Orientation, and the axis each load bends", "Engineering judgement (EOR): a rectangular member's axes follow from its long side")

#text("Baseplate: A36. Welds: fillet, all around, electrode E70XX.")

= Loading

Guard loads per ASCE 7-22. The concentrated and uniform loads are separate load types and do not act concurrently. Each check applies them in every direction case and reports the controlling one.

#calcline([$P = "200.0 lb"$], "Concentrated guard load, any direction, any point on the top rail", "ASCE 7-22 §4.5.1")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load, 50 lb/ft, any direction; not concurrent with P", "ASCE 7-22 §4.5.1.1")
#calcline([$P_c = "50.00 lb"$], "Component load on the intermediate rail, horizontal; also applied downward (engineering judgement)", "ASCE 7-22 §4.5.1.2")
#calcline([$w_D = "0.3134 lb/in"$], "Top rail self-weight: computed W = 3.761 lb/ft", "Section properties (custom section)")
#subhead("Dead load at the post")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(L_"post" = h - t_p = ("42.00 in") - ("0.5000 in") = "41.50 in")$], "Post cantilever length, top of baseplate to top rail centerline", "Stated assumption: post fixed at the top of the baseplate")
#calcline([$W_"post" = "0.2544 lb/in"$], "Post self-weight: Rect. tube 2 × 2 × 0.125 (custom), computed W = 3.053 lb/ft", "Section properties (custom section)")
#calcline([$display(D_"post" = W_"post" L_"post" = ("0.2544 lb/in") ("41.50 in") = "10.56 lb")$], "Post dead load, full weight at the base", "Engineering judgement (EOR): post dead load")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post (stated assumption)", "Input")
#calcline([$display(D_"rail" = w_D L = ("0.3134 lb/in") ("72.00 in") = "22.57 lb")$], "Top rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$w_(D,"int") = "0.1284 lb/in"$], "Intermediate rail self-weight: Rect. tube 2 × 1 × 0.083 (custom), computed W = 1.540 lb/ft", "Section properties (custom section)")
#calcline([$display(D_"int" = w_(D,"int") L = ("0.1284 lb/in") ("72.00 in") = "9.243 lb")$], "Intermediate rail dead load delivered to the post", "Engineering judgement (EOR): post dead load")
#calcline([$display(P_D = D_"rail" + D_"int" + D_"post" = ("22.57 lb") + ("9.243 lb") + ("10.56 lb") = "42.37 lb")$], "D at the post: axial dead load at the top of the baseplate", "Engineering judgement (EOR): post dead load")

= Check 1: Top rail bending

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Vertical load* \ $M_r$, $M_c$], [*Horizontal load* \ $M_r$, $M_c$], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2", "Mrx = 3,803 lb-in\nMcx = 28,300 lb-in", "—", "0.13", "", "Downward", "Distributed", "1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2", "Mrx = 2,903 lb-in\nMcx = 28,300 lb-in", "—", "0.10", "", strong("Outward"), strong("Concentrated"), strong("1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS"), strong("Mrx = 203.1 lb-in\nMcx = 28,300 lb-in"), strong("Mry = 3,600 lb-in\nMcy = 21,400 lb-in"), strong("0.18"), strong("Controls"), "Outward", "Distributed", "1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "Mrx = 203.1 lb-in\nMcx = 28,300 lb-in", "Mry = 2,700 lb-in\nMcy = 21,400 lb-in", "0.13", "", "Inward", "Concentrated", "1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "Mrx = 203.1 lb-in\nMcx = 28,300 lb-in", "Mry = 3,600 lb-in\nMcy = 21,400 lb-in", "0.18", "", "Inward", "Distributed", "1.0D vertical, 1.0L horizontal, each on its own axis\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS", "Mrx = 203.1 lb-in\nMcx = 28,300 lb-in", "Mry = 2,700 lb-in\nMcy = 21,400 lb-in", "0.13", "", "Upward", "Concentrated", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "Mrx = 3,478 lb-in\nMcx = 28,300 lb-in", "—", "0.12", "", "Upward", "Distributed", "0.6D + 1.0L, net vertical\nEngineering judgement (EOR): upward case, not an ASCE combination", "Mrx = 2,578 lb-in\nMcx = 28,300 lb-in", "—", "0.09", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Outward, concentrated (1.0D vertical, 1.0L horizontal, each on its own axis; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS)")

#subhead("Demand: outward, concentrated load")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$w_D = "0.3134 lb/in"$], "Top rail self-weight", "Loading")
#calcline([$display(M_D = frac(w_D L^("2"), "8") = frac(("0.3134 lb/in") ("72.00 in")^("2"), "8") = "203.1 lb-in")$], "Dead-load moment, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$P = "200.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(M_L = frac(P L, "4") = frac(("200.0 lb") ("72.00 in"), "4") = "3,600 lb-in")$], "Live-load moment, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$display(M_"rx" = "1.0" M_D = "1.0" ("203.1 lb-in") = "203.1 lb-in")$], "Required flexural strength about the x axis: dead load, vertical", "ASCE 7-22 §2.4.1, Comb. 2")
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
#calcline([$Z_x = "1.028 in"^3$], "Plastic section modulus about the x axis", "Section properties (custom section)")
#calcline([$display(M_"px" = F_y Z_x = ("46.00 ksi") ("1.028 in"^3) = "47,270 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "14.92"$], "Flange slenderness about the x axis: b/t of the 2.000 in walls, computed (design wall)", "Section properties (custom section)")
#calcline([$lambda_f = 14.92 <= lambda_"pf" = 28.12$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact flange: flange local buckling does not apply"*], "Flange classification, bending about the x axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$lambda_w = "23.88"$], "Web slenderness about the x axis: h/t of the 3.000 in walls, computed (design wall)", "Section properties (custom section)")
#calcline([$lambda_w = 23.88 <= lambda_"pw" = 60.76$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the x axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$display(L_b = L = "72.00 in")$], "Laterally unbraced length: the span between posts", "Engineering judgement (EOR): unbraced length for lateral-torsional buckling")
#calcline([$r_y = "0.8057 in"$], "Radius of gyration about the y axis", "Section properties (custom section)")
#calcline([$J = "1.421 in"^4$], "Torsional constant", "Section properties (custom section)")
#calcline([$A_g = "1.034 in"^2$], "Gross area", "Section properties (custom section)")
#calcline([$display(L_p = frac("0.13" E r_y sqrt(J A_g), M_"px") = frac("0.13" ("29,000 ksi") ("0.8057 in") dot sqrt(("1.421 in"^4) ("1.034 in"^2)), ("47,270 lb-in")) = "77.89 in")$], "Limiting unbraced length for yielding", "AISC 360-22 Eq. F7-10")
#calcline([$L_b = 72.00 in <= L_p = 77.89 in$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "", "AISC 360-22 §F7.4(a)")
#calcline([$display(M_"nx" = M_"px" = "47,270 lb-in")$], "Nominal flexural strength about the x axis: yielding", "AISC 360-22 §F7")
#calcline([$display(M_"cx" = frac(M_"nx", Omega_b) = frac(("47,270 lb-in"), "1.670") = "28,300 lb-in")$], "Allowable flexural strength about the x axis", "AISC 360-22 Eq. B3-2")
#subhead("Capacity about the y axis (horizontal load)")
#calcline([$Z_y = "0.7770 in"^3$], "Plastic section modulus about the y axis", "Section properties (custom section)")
#calcline([$display(M_"py" = F_y Z_y = ("46.00 ksi") ("0.7770 in"^3) = "35,740 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "23.88"$], "Flange slenderness about the y axis: h/t of the 3.000 in walls, computed (design wall)", "Section properties (custom section)")
#calcline([$lambda_f = 23.88 <= lambda_"pf" = 28.12$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact flange: flange local buckling does not apply"*], "Flange classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$lambda_w = "14.92"$], "Web slenderness about the y axis: b/t of the 2.000 in walls, computed (design wall)", "Section properties (custom section)")
#calcline([$lambda_w = 14.92 <= lambda_"pw" = 60.76$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$"Bending about the minor axis"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "", "AISC 360-22 §F7.4, User Note")
#calcline([$display(M_"ny" = M_"py" = "35,740 lb-in")$], "Nominal flexural strength about the y axis: yielding", "AISC 360-22 §F7")
#calcline([$display(M_"cy" = frac(M_"ny", Omega_b) = frac(("35,740 lb-in"), "1.670") = "21,400 lb-in")$], "Allowable flexural strength about the y axis", "AISC 360-22 Eq. B3-2")
#subhead("Interaction")
#calcline([$display("Ratio" = frac(M_"rx", M_"cx") + frac(M_"ry", M_"cy") = frac(("203.1 lb-in"), ("28,300 lb-in")) + frac(("3,600 lb-in"), ("21,400 lb-in")) = "0.18")$], "Both axes combined, with no axial force", "AISC 360-22 Eq. H1-1b; Engineering judgement (EOR): rectangular members combine axes by §H1.1, not SRSS")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.18 <= 1.00$ #h(10pt) #"OK"])

= Check 2: Top rail deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.04558 in", "0.6000 in", "0.08", "", "Downward", "Distributed", "1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability", "0.04292 in", "0.6000 in", "0.07", "", strong("Outward"), strong("Concentrated"), strong("1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only"), strong("0.07989 in"), strong("0.6000 in"), strong("0.13"), strong("Controls"), "Outward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.07490 in", "0.6000 in", "0.12", "", "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.07989 in", "0.6000 in", "0.13", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.07490 in", "0.6000 in", "0.12", "", "Upward", "Concentrated", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.04257 in", "0.6000 in", "0.07", "", "Upward", "Distributed", "1.0L, vertical\nEngineering judgement (EOR): serviceability, live load only", "0.03991 in", "0.6000 in", "0.07", "", "Longitudinal", "", "Rail carries the longitudinal load axially; not checked", "", "", "", "")

#heading(level: 2, "Controlling case: Outward, concentrated (1.0L, horizontal; Engineering judgement (EOR): serviceability, live load only)")

#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_y = "0.6713 in"^4$], "Moment of inertia about the y axis (horizontal load)", "Section properties (custom section)")
#calcline([$P = "200.0 lb"$], "Concentrated guard load at midspan", "Loading")
#calcline([$display(Delta_L = frac(P L^("3"), "48" E I_y) = frac(("200.0 lb") ("72.00 in")^("3"), "48" ("29,000 ksi") ("0.6713 in"^4)) = "0.07989 in")$], "Live-load deflection, midspan", "AISC Manual Table 3-23, Case 7")
#calcline([$display(Delta = "1.0" Delta_L = "1.0" ("0.07989 in") = "0.07989 in")$], "Live load only", "Engineering judgement (EOR): serviceability, live load only")
#calcline([$display(Delta_"allow" = frac(L, "120") = frac(("72.00 in"), "120") = "0.6000 in")$], "Limit L/120", "Engineering judgement (EOR): deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.07989 in"), ("0.6000 in")) = "0.13")$], "Deflection / limit", "Engineering judgement (EOR): deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.13 <= 1.00$ #h(10pt) #"OK"])

= Check 3: Top rail weld to post

#flag("THIN MATERIAL AT WELD: Top rail nominal wall thickness, Rect. tube 3 × 2 × 0.12 (custom), 0.1200 in, is thinner than 0.1250 in: the joined material is below the AWS D1.1 thickness range, and the welding procedure is the engineer's responsibility (for example AWS D1.3, sheet steel). AWS D1.1, Structural Welding Code - Steel, applies to carbon and low-alloy steel 1/8 in (3 mm) or thicker (AWS D1.1/D1.1M:2020, Clause 1).")

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "38.15 lb/in\nuniform", "—", "38.15 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "55.30 lb/in\nuniform", "—", "55.30 lb/in", "Weld 1,856 lb/in\nBase —", "0.03", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "62.45 lb/in\ncompression side", "34.29 lb/in", "71.24 lb/in", "Weld 1,856 lb/in\nBase 1,942 lb/in", "0.04", "", "Outward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "91.73 lb/in\ncompression side", "51.43 lb/in", "105.2 lb/in", "Weld 1,856 lb/in\nBase 1,942 lb/in", "0.06", "", "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "62.45 lb/in\ncompression side", "34.29 lb/in", "71.24 lb/in", "Weld 1,856 lb/in\nBase 1,942 lb/in", "0.04", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "91.73 lb/in\ncompression side", "51.43 lb/in", "105.2 lb/in", "Weld 1,856 lb/in\nBase 1,942 lb/in", "0.06", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "31.96 lb/in\nuniform", "—", "31.96 lb/in", "Weld 1,856 lb/in\nBase —", "0.02", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "49.11 lb/in\nuniform", "—", "49.11 lb/in", "Weld 1,856 lb/in\nBase —", "0.03", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "98.61 lb/in\ncompression side", "34.29 lb/in", "104.4 lb/in", "Weld 1,856 lb/in\nBase 1,942 lb/in", "0.06", "", strong("Longitudinal"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("146.0 lb/in\ncompression side"), strong("51.43 lb/in"), strong("154.8 lb/in"), strong("Weld 1,856 lb/in\nBase 1,942 lb/in"), strong("0.08"), strong("Controls"))]

#heading(level: 2, "Controlling case: Longitudinal, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$B = "2.000 in"$], "Rect. tube 3 × 2 × 0.12 (custom): width of the chord face, the rail's horizontal dimension", "Section properties (custom section)")
#calcline([$t = "0.1116 in"$], "Top rail design wall thickness, the chord", "Section properties (custom section)")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$H_b = "2.000 in"$], "Rect. tube 2 × 2 × 0.125 (custom): branch dimension along the chord, the post's dimension parallel to the rail", "Section properties (custom section)")
#calcline([$B_b = "2.000 in"$], "Branch width across the chord face, the post's dimension perpendicular to the rail", "Section properties (custom section)")
#calcline([$t_b = "0.1250 in"$], "Post design wall thickness, the branch", "Section properties (custom section)")
#calcline([$F_"yb" = "50.00 ksi"$], "Yield stress, A1085 Gr A", "AISC Manual Table 2-4")
#calcline([$display(B_("e,K1") = frac("10", frac(B, t)) frac(F_y t, F_"yb" t_b) B_b = frac("10", frac(("2.000 in"), ("0.1116 in"))) dot frac(("46.00 ksi") ("0.1116 in"), ("50.00 ksi") ("0.1250 in")) ("2.000 in") = "0.9167 in")$], "Effective width of the branch across the chord face", "AISC 360-22 Eq. K1-1")
#calcline([$display(B_e = "min"(B_("e,K1"), frac(B_b, "2")) = "min"(("0.9167 in"), frac(("2.000 in"), "2")) = "0.9167 in")$], "Effective width: B_e/2 not more than B_b/4, the branch being at 90 degrees", "AISC 360-22 Table K5.1")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(l_e = "2" H_b + "2" B_e = "2" ("2.000 in") + "2" ("0.9167 in") = "5.833 in")$], "Effective weld length", "AISC 360-22 Eq. K5-5; AISC 360-22 §K5")
#calcline([$display(S_"ip" = frac(H_b^("2"), "3") + B_e H_b = frac(("2.000 in")^("2"), "3") + ("0.9167 in") ("2.000 in") = "3.167 in"^2)$], "Effective section modulus of the weld as a line, in-plane bending: a load along the rail", "AISC 360-22 Eq. K5-6; Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#calcline([$display(S_"op" = H_b B_b + frac(B_b^("2"), "3") - frac((B_b - B_e)^("3"), "3" B_b) = ("2.000 in") ("2.000 in") + frac(("2.000 in")^("2"), "3") - frac((("2.000 in") - ("0.9167 in"))^("3"), "3" ("2.000 in")) = "5.121 in"^2)$], "Effective section modulus of the weld as a line, out-of-plane bending: a load across the guard", "AISC 360-22 Eq. K5-7; Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#calcline([$B_"b" = "2.000 in" = B = "2.000 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Fillet model kept"*], "Post as wide as the rail: At equal widths the side welds of a rectangular branch land on the chord's rounded corner and are flare-bevel welds; the fillet model of the entered size all around is kept.", "Engineering judgement (EOR): fillet model kept at equal widths")
#subhead("Eccentricity")
#calcline([$d_"rail" = "3.000 in"$], "Rect. tube 3 × 2 × 0.12 (custom): outside dimension in the vertical direction, the rail depth", "Section properties (custom section)")
#calcline([$display(e = frac(d_"rail", "2") = frac(("3.000 in"), "2") = "1.500 in")$], "Eccentricity: rail centerline to the weld plane at the rail underside", "Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#subhead("Fillet size limits")
#calcline([$t_"rail,nom" = "0.1200 in"$], "Top rail nominal wall thickness, Rect. tube 3 × 2 × 0.12 (custom)", "Section properties (custom section)")
#calcline([$t_"post,nom" = "0.1250 in"$], "Post nominal wall thickness, Rect. tube 2 × 2 × 0.125 (custom)", "Section properties (custom section)")
#calcline([$display(t_"min" = "min"(t_"rail,nom", t_"post,nom") = "min"(("0.1200 in"), ("0.1250 in")) = "0.1200 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
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
#calcline([$t_"rail" = "0.1116 in"$], "Top rail design wall thickness, Rect. tube 3 × 2 × 0.12 (custom)", "Section properties (custom section)")
#calcline([$display(R_(n,"BM") = "0.6" F_u t_"rail" = "0.6" ("58.00 ksi") ("0.1116 in") = "3,884 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM"), Omega_"BM") = frac(("3,884 lb/in"), "2.000") = "1,942 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$"Rail wall, normal force"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not checked"*], "Rail wall, force normal to the wall: the chord limit states of a rectangular chord (AISC 360-22 Chapter K and §J10) are not computed; not checked (stated assumption). The rail is held to the Chapter K limits of applicability.", "Engineering judgement (EOR): a rectangular chord's limit states not checked")
#calcline([$"Post wall at the weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Covered by Check 5"*], "Post wall at the weld: covered by Check 5. The wall carries the weld force as stress along the post axis, the same demand as Check 5 at its critical section; member shear is not checked (stated assumption).", "Engineering judgement (EOR): post wall at the weld covered by Check 5")
#subhead("Demand: longitudinal, distributed load")
#calcline([$D_"rail" = "22.57 lb"$], "Top rail dead load at the weld: w_D over the span (the tributary length)", "Loading")
#calcline([$display(P = "1.0" D_"rail" = "1.0" ("22.57 lb") = "22.57 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (longitudinal), on the rail at the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("300.0 lb") = "300.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V e = ("300.0 lb") ("1.500 in") = "450.0 lb-in")$], "Moment at the weld plane: V at the rail centerline, arm e", "Engineering judgement (EOR): elastic weld as a line on Table K5.1's effective properties")
#calcline([$display(f_a = frac(P, l_e) = frac(("22.57 lb"), ("5.833 in")) = "3.869 lb/in")$], "Axial force per inch of weld, compression, uniform over the effective weld length", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_"ip") = frac(("450.0 lb-in"), ("3.167 in"^2)) = "142.1 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("3.869 lb/in") + ("142.1 lb/in") = "146.0 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("3.869 lb/in") - ("142.1 lb/in")) = "138.2 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "146.0 lb/in" >= f_(n,"t") = "138.2 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "146.0 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, l_e) = frac(("300.0 lb"), ("5.833 in")) = "51.43 lb/in")$], "Shear per inch of weld, taken as uniform over the effective weld length", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("146.0 lb/in")^("2") + ("51.43 lb/in")^("2")) = "154.8 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("154.8 lb/in"), ("1,856 lb/in")) = "0.08")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM"), Omega_"BM")) = frac(("51.43 lb/in"), ("1,942 lb/in")) = "0.03")$], "Rail fusion face: in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.08339", "0.02648") = "0.08")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.08 <= 1.00$ #h(10pt) #"OK"])

= Check 4a: Intermediate rail

== Envelope summary

Each limit state is computed in both directions of the component load. The full calculation follows for the governing case of each limit state.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Limit state*], [*Direction*], [*Combination*], [*Demand* $M_a$ or $Delta$], [*Capacity* $M_n / Omega_b$ or $Delta_"allow"$], [*Ratio*], []), "Bending", "Downward", "1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "983.2 lb-in", "4,479 lb-in", "0.22", "", "Bending", "Horizontal", "1.0L horizontal, alone\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)", "900.0 lb-in", "7,293 lb-in", "0.12", "", strong("Deflection"), strong("Downward"), strong("1.0D + 1.0L, vertical\nEngineering judgement (EOR): serviceability"), strong("0.2135 in"), strong("0.6000 in"), strong("0.36"), strong("Controls"), "Deflection", "Horizontal", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.06422 in", "0.6000 in", "0.11", "")

#heading(level: 2, "Controlling case: Downward, deflection (1.0D + 1.0L, vertical; Engineering judgement (EOR): serviceability)")

#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_"int,y" = "0.07006 in"^4$], "Moment of inertia about the y axis (vertical load), Rect. tube 2 × 1 × 0.083 (custom)", "Section properties (custom section)")
#calcline([$P_c = "50.00 lb"$], "Component load, a point load at midspan", "Loading")
#calcline([$display(Delta_L = frac(P_c L^("3"), "48" E I_"int,y") = frac(("50.00 lb") ("72.00 in")^("3"), "48" ("29,000 ksi") ("0.07006 in"^4)) = "0.1914 in")$], "Component load deflection, midspan", "AISC Manual Table 3-23, Case 7; Engineering judgement (EOR): component load as a point load at midspan")
#calcline([$w_(D,"int") = "0.1284 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$display(Delta_D = frac("5" w_(D,"int") L^("4"), "384" E I_"int,y") = frac("5" ("0.1284 lb/in") ("72.00 in")^("4"), "384" ("29,000 ksi") ("0.07006 in"^4)) = "0.02211 in")$], "Dead-load deflection, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$display(Delta = "1.0" Delta_D + "1.0" Delta_L = "1.0" ("0.02211 in") + "1.0" ("0.1914 in") = "0.2135 in")$], "D and L on the same (vertical) axis", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); Engineering judgement (EOR): serviceability")
#calcline([$display(Delta_"allow" = frac(L, "120") = frac(("72.00 in"), "120") = "0.6000 in")$], "Limit L/120", "Engineering judgement (EOR): deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.2135 in"), ("0.6000 in")) = "0.36")$], "Deflection / limit", "Engineering judgement (EOR): deflection limit, not code")

#heading(level: 2, "Governing bending case: Downward, bending (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5))")

#subhead("Demand: downward, component load")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$P_c = "50.00 lb"$], "Component load, a point load at midspan", "Loading")
#calcline([$display(M_L = frac(P_c L, "4") = frac(("50.00 lb") ("72.00 in"), "4") = "900.0 lb-in")$], "Component load moment, midspan", "AISC Manual Table 3-23, Case 7; Engineering judgement (EOR): component load as a point load at midspan")
#calcline([$w_(D,"int") = "0.1284 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$display(M_D = frac(w_(D,"int") L^("2"), "8") = frac(("0.1284 lb/in") ("72.00 in")^("2"), "8") = "83.18 lb-in")$], "Dead-load moment, midspan", "AISC Manual Table 3-23, Case 1")
#calcline([$display(M_"ry" = "1.0" M_D + "1.0" M_L = "1.0" ("83.18 lb-in") + "1.0" ("900.0 lb-in") = "983.2 lb-in")$], "Required flexural strength about the y axis: D and L, both vertical", "Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); ASCE 7-22 §2.4.1, Comb. 2")
#subhead("Section")
#calcline([$F_y = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$display(lambda_"pf" = "1.12" sqrt(frac(E, F_y)) = "1.12" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "28.12")$], "Compact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"rf" = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "35.15")$], "Noncompact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"pw" = "2.42" sqrt(frac(E, F_y)) = "2.42" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "60.76")$], "Compact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$display(lambda_"rw" = "5.7" sqrt(frac(E, F_y)) = "5.7" dot sqrt(frac(("29,000 ksi"), ("46.00 ksi"))) = "143.1")$], "Noncompact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#subhead("Capacity about the y axis (vertical load)")
#calcline([$Z_y = "0.1626 in"^3$], "Plastic section modulus about the y axis", "Section properties (custom section)")
#calcline([$display(M_"py" = F_y Z_y = ("46.00 ksi") ("0.1626 in"^3) = "7,480 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "22.91"$], "Flange slenderness about the y axis: h/t of the 2.000 in walls, computed (design wall)", "Section properties (custom section)")
#calcline([$lambda_f = 22.91 <= lambda_"pf" = 28.12$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact flange: flange local buckling does not apply"*], "Flange classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$lambda_w = "9.955"$], "Web slenderness about the y axis: b/t of the 1.000 in walls, computed (design wall)", "Section properties (custom section)")
#calcline([$lambda_w = 9.955 <= lambda_"pw" = 60.76$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the y axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$"Bending about the minor axis"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "", "AISC 360-22 §F7.4, User Note")
#calcline([$display(M_"ny" = M_"py" = "7,480 lb-in")$], "Nominal flexural strength about the y axis: yielding", "AISC 360-22 §F7")
#calcline([$display(M_"cy" = frac(M_"ny", Omega_b) = frac(("7,480 lb-in"), "1.670") = "4,479 lb-in")$], "Allowable flexural strength about the y axis", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = frac(M_"ry", M_"cy") = frac(("983.2 lb-in"), ("4,479 lb-in")) = "0.22")$], "Demand / capacity", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.36 <= 1.00$ #h(10pt) #"OK"])

= Check 4b: Intermediate rail weld to post

#flag("THIN MATERIAL AT WELD: Intermediate rail nominal wall thickness, Rect. tube 2 × 1 × 0.083 (custom), 0.08300 in, is thinner than 0.1250 in: the joined material is below the AWS D1.1 thickness range, and the welding procedure is the engineer's responsibility (for example AWS D1.3, sheet steel). AWS D1.1, Structural Welding Code - Steel, applies to carbon and low-alloy steel 1/8 in (3 mm) or thicker (AWS D1.1/D1.1M:2020, Clause 1).")

== Envelope summary

Both directions of the component load are computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), strong("Downward"), strong("Component"), strong("1.0D + 1.0L, vertical\nASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5)"), strong("—\nshear only"), strong("13.66 lb/in"), strong("13.66 lb/in"), strong("Weld 1,856 lb/in\nBase 1,343 lb/in"), strong("0.01"), strong("Controls"), "Horizontal", "Component", "1.0D vertical, 1.0L horizontal, vector sum\nASCE 7-22 §2.4.1, Comb. 2", "—\nshear only", "12.55 lb/in", "12.55 lb/in", "Weld 1,856 lb/in\nBase 1,343 lb/in", "0.01", "")]

#heading(level: 2, "Controlling case: Downward, component (1.0D + 1.0L, vertical; ASCE 7-22 §2.4.1, Comb. 2; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5))")

#subhead("Weld properties")
#calcline([$B = "2.000 in"$], "Rect. tube 2 × 2 × 0.125 (custom): width of the chord face, the post's dimension perpendicular to the rail", "Section properties (custom section)")
#calcline([$t = "0.1250 in"$], "Post design wall thickness, the chord", "Section properties (custom section)")
#calcline([$F_y = "50.00 ksi"$], "Yield stress, A1085 Gr A", "AISC Manual Table 2-4")
#calcline([$H_b = "1.000 in"$], "Rect. tube 2 × 1 × 0.083 (custom): branch dimension along the chord, the intermediate rail's vertical dimension", "Section properties (custom section)")
#calcline([$B_b = "2.000 in"$], "Branch width across the chord face, the intermediate rail's horizontal dimension", "Section properties (custom section)")
#calcline([$t_b = "0.07719 in"$], "Intermediate rail design wall thickness, the branch", "Section properties (custom section)")
#calcline([$F_"yb" = "46.00 ksi"$], "Yield stress, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$display(B_("e,K1") = frac("10", frac(B, t)) frac(F_y t, F_"yb" t_b) B_b = frac("10", frac(("2.000 in"), ("0.1250 in"))) dot frac(("50.00 ksi") ("0.1250 in"), ("46.00 ksi") ("0.07719 in")) ("2.000 in") = "2.200 in")$], "Effective width of the branch across the chord face", "AISC 360-22 Eq. K1-1")
#calcline([$display(B_e = "min"(B_("e,K1"), frac(B_b, "2")) = "min"(("2.200 in"), frac(("2.000 in"), "2")) = "1.000 in")$], "Effective width: B_e/2 not more than B_b/4, the branch being at 90 degrees", "AISC 360-22 Table K5.1")
#calcline([$w = "0.1250 in"$], "Fillet weld leg size, all around (1/8 as entered)", "Input")
#calcline([$display(l_e = "2" H_b + "2" B_e = "2" ("1.000 in") + "2" ("1.000 in") = "4.000 in")$], "Effective weld length", "AISC 360-22 Eq. K5-5; AISC 360-22 §K5")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1250 in") = "0.08837 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#calcline([$B_"b" = "2.000 in" = B = "2.000 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Fillet model kept"*], "Intermediate rail as wide as the post: At equal widths the side welds of a rectangular branch land on the chord's rounded corner and are flare-bevel welds; the fillet model of the entered size all around is kept.", "Engineering judgement (EOR): fillet model kept at equal widths")
#subhead("Connection model")
#calcline([$"Intermediate rail to post weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Simple shear connection"*], "Simple shear connection consistent with the simple-span member assumption; no end moment at the weld.", "Engineering judgement (EOR): intermediate rail to post weld as a simple shear connection; Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post")
#subhead("Fillet size limits")
#calcline([$t_"int,nom" = "0.08300 in"$], "Intermediate rail nominal wall thickness, Rect. tube 2 × 1 × 0.083 (custom)", "Section properties (custom section)")
#calcline([$t_"post,nom" = "0.1250 in"$], "Post nominal wall thickness, Rect. tube 2 × 2 × 0.125 (custom)", "Section properties (custom section)")
#calcline([$display(t_"min" = "min"(t_"int,nom", t_"post,nom") = "min"(("0.08300 in"), ("0.1250 in")) = "0.08300 in")$], "Thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w_"min" = "0.1250 in"$], "Minimum fillet size for the thinner part joined", "AISC 360-22 Table J2.4")
#calcline([$w = "0.1250 in" >= w_"min" = "0.1250 in"$ #h(6pt) $arrow.r$ #h(6pt) *#"OK"*], "Minimum size", "AISC 360-22 Table J2.4")
#calcline([$"Maximum fillet size"$ #h(6pt) $arrow.r$ #h(6pt) *#"Not applicable"*], "Maximum fillet size along edges of material does not apply: this weld is a T-joint, not a weld along an edge. No maximum size is checked.", "AISC 360-22 §J2.2b(b); Engineering judgement (EOR): no maximum fillet size at a T-joint")
#subhead("Weld metal")
#calcline([$F_"EXX" = "70.00 ksi"$], "Electrode classification strength, E70XX", "AISC 360-22 §J2.6; AWS A5.1")
#calcline([$display(F_"nw" = "0.6" F_"EXX" = "0.6" ("70.00 ksi") = "42.00 ksi")$], "Nominal stress of the weld metal", "AISC 360-22 Table J2.5")
#calcline([$Omega_w = "2.000"$], "Safety factor, fillet weld (ASD)", "AISC 360-22 Table J2.5")
#calcline([$k_"ds" = "1.000"$], "No directional increase at the intermediate rail to post weld (a branch-to-chord joint)", "Engineering judgement (EOR): k_ds = 1.0 at the rail to post weld")
#subhead("Base metal: post wall fusion face (chord)")
#calcline([$F_u = "65.00 ksi"$], "Tensile strength, A1085 Gr A", "AISC Manual Table 2-4")
#calcline([$t_"post" = "0.1250 in"$], "Post design wall thickness, Rect. tube 2 × 2 × 0.125 (custom)", "Section properties (custom section)")
#calcline([$display(R_(n,"BM,post") = "0.6" F_u t_"post" = "0.6" ("65.00 ksi") ("0.1250 in") = "4,875 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM,post"), Omega_"BM") = frac(("4,875 lb/in"), "2.000") = "2,438 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#subhead("Base metal: intermediate rail wall fusion face (branch)")
#calcline([$F_u = "58.00 ksi"$], "Tensile strength, A500 Gr B", "AISC Manual Table 2-4")
#calcline([$t_"int" = "0.07719 in"$], "Intermediate rail design wall thickness, Rect. tube 2 × 1 × 0.083 (custom)", "Section properties (custom section)")
#calcline([$display(R_(n,"BM,int") = "0.6" F_u t_"int" = "0.6" ("58.00 ksi") ("0.07719 in") = "2,686 lb/in")$], "Shear rupture at the fusion face, per inch of weld", "AISC 360-22 Eq. J4-4; AISC Manual Part 9, base metal at welds")
#calcline([$Omega_"BM" = "2.000"$], "Safety factor, shear rupture (ASD)", "AISC 360-22 §J4.2(b)")
#calcline([$display(frac(R_(n,"BM,int"), Omega_"BM") = frac(("2,686 lb/in"), "2.000") = "1,343 lb/in")$], "Allowable base metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$frac(R_(n,"BM,int"), Omega_"BM") = "1,343 lb/in" < frac(R_(n,"BM,post"), Omega_"BM") = "2,438 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Intermediate rail wall governs"*], "Base metal is checked at the fusion face of both connected parts, the post wall (the chord) and the intermediate rail wall (the branch), each in shear rupture against the in-plane shear per inch; the lower allowable governs.", "Engineering judgement (EOR): Check 4b base metal on both walls, lower governs")
#calcline([$"Post wall, chord limit states"$ #h(6pt) $arrow.r$ #h(6pt) *#"No demand"*], "Chapter K chord limit states: the intermediate rail delivers no axial force or moment to the post wall (simple shear connection); the post wall's in-plane shear is checked by the base metal line above.", "Engineering judgement (EOR): no chord limit state demand at the intermediate rail")
#subhead("Demand: downward, component load")
#calcline([$w_(D,"int") = "0.1284 lb/in"$], "Intermediate rail self-weight", "Loading")
#calcline([$L = "72.00 in"$], "Span, simple beam", "Input")
#calcline([$display(R_D = frac(w_(D,"int") L, "2") = frac(("0.1284 lb/in") ("72.00 in"), "2") = "4.621 lb")$], "Dead-load end reaction at the post", "AISC Manual Table 3-23, Case 1")
#calcline([$P_c = "50.00 lb"$], "Component load adjacent to the post: the full P_c to this end", "Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post")
#calcline([$display(R = "1.0" R_D + "1.0" P_c = "1.0" ("4.621 lb") + "1.0" ("50.00 lb") = "54.62 lb")$], "Weld reaction: dead and component loads in the same (vertical) direction, in the plane of the weld", "Engineering judgement (EOR): weld line at the post face, simple shear, P_c at the post; Engineering judgement (EOR): downward component load, after OSHA 1910.29(b)(5); ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(f_v = frac(R, l_e) = frac(("54.62 lb"), ("4.000 in")) = "13.66 lb/in")$], "Shear per inch of weld, taken as uniform over the effective weld length", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = f_v = "13.66 lb/in")$], "Resultant per inch: shear only, no axial force and no moment", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.08837 in") dot "1.000" = "3,712 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("3,712 lb/in"), "2.000") = "1,856 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("13.66 lb/in"), ("1,856 lb/in")) = "0.01")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_v, frac(R_(n,"BM,int"), Omega_"BM")) = frac(("13.66 lb/in"), ("1,343 lb/in")) = "0.01")$], "Base metal, intermediate rail wall fusion face (governs): in-plane shear only", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.007358", "0.01017") = "0.01")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.01 <= 1.00$ #h(10pt) #"OK"])

= Check 5: Post combined axial and flexure

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Axial* $P_r$ \ capacity $P_c$ or $P_t$], [*Moment* $M_r$ \ capacity $M_c$], [*Equation*], [$frac(alpha P_r, P_e)$], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "242.4 lb comp.\nPc = 9,921 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.02", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "342.4 lb comp.\nPc = 9,921 lb", "—", "Pr/Pc\n(Eq. E3-1)", "—", "0.03", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "42.37 lb comp.\nPc = 9,921 lb", "8,300 lb-in\nMc = 18,590 lb-in\nabout x", "Eq. H1-1b", "0.003588", "0.45", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("42.37 lb comp.\nPc = 9,921 lb"), strong("12,450 lb-in\nMc = 18,590 lb-in\nabout x"), strong("Eq. H1-1b"), strong("0.003588"), strong("0.67"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "42.37 lb comp.\nPc = 9,921 lb", "8,300 lb-in\nMc = 18,590 lb-in\nabout x", "Eq. H1-1b", "0.003588", "0.45", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "42.37 lb comp.\nPc = 9,921 lb", "12,450 lb-in\nMc = 18,590 lb-in\nabout x", "Eq. H1-1b", "0.003588", "0.67", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "174.6 lb tension\nPt = 26,860 lb", "—", "Pr/Pt\n(Eq. D2-1)", "—", "0.01", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "274.6 lb tension\nPt = 26,860 lb", "—", "Pr/Pt\n(Eq. D2-1)", "—", "0.01", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "42.37 lb comp.\nPc = 9,921 lb", "8,300 lb-in\nMc = 18,590 lb-in\nabout y", "Eq. H1-1b", "0.003588", "0.45", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "42.37 lb comp.\nPc = 9,921 lb", "12,450 lb-in\nMc = 18,590 lb-in\nabout y", "Eq. H1-1b", "0.003588", "0.67", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Capacity")
#calcline([$F_y = "50.00 ksi"$], "Yield stress, A1085 Gr A", "AISC Manual Table 2-4")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$display(lambda_"pf" = "1.12" sqrt(frac(E, F_y)) = "1.12" dot sqrt(frac(("29,000 ksi"), ("50.00 ksi"))) = "26.97")$], "Compact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"rf" = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("50.00 ksi"))) = "33.72")$], "Noncompact limit, flange of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 17")
#calcline([$display(lambda_"pw" = "2.42" sqrt(frac(E, F_y)) = "2.42" dot sqrt(frac(("29,000 ksi"), ("50.00 ksi"))) = "58.28")$], "Compact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$display(lambda_"rw" = "5.7" sqrt(frac(E, F_y)) = "5.7" dot sqrt(frac(("29,000 ksi"), ("50.00 ksi"))) = "137.3")$], "Noncompact limit, web of rectangular HSS in flexure", "AISC 360-22 Table B4.1b, Case 19")
#calcline([$Omega_b = "1.670"$], "Safety factor for flexure (ASD)", "AISC 360-22 §F1(a)")
#calcline([$Z_x = "0.6209 in"^3$], "Plastic section modulus about the x axis", "Section properties (custom section)")
#calcline([$display(M_"px" = F_y Z_x = ("50.00 ksi") ("0.6209 in"^3) = "31,040 lb-in")$], "Plastic moment (yielding)", "AISC 360-22 Eq. F7-1")
#calcline([$lambda_f = "13.00"$], "Flange slenderness about the x axis: b/t of the 2.000 in walls, computed (design wall)", "Section properties (custom section)")
#calcline([$lambda_f = 13.00 <= lambda_"pf" = 26.97$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact flange: flange local buckling does not apply"*], "Flange classification, bending about the x axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$lambda_w = "13.00"$], "Web slenderness about the x axis: h/t of the 2.000 in walls, computed (design wall)", "Section properties (custom section)")
#calcline([$lambda_w = 13.00 <= lambda_"pw" = 58.28$ #h(6pt) $arrow.r$ #h(6pt) *#"Compact web: web local buckling does not apply"*], "Web classification, bending about the x axis", "AISC 360-22 §B4.1b; AISC 360-22 §F7.2(a), §F7.3(a)")
#calcline([$"Square section"$ #h(6pt) $arrow.r$ #h(6pt) *#"Lateral-torsional buckling does not apply"*], "", "AISC 360-22 §F7.4, User Note")
#calcline([$display(M_"nx" = M_"px" = "31,040 lb-in")$], "Nominal flexural strength about the x axis: yielding", "AISC 360-22 §F7")
#calcline([$display(M_"cx" = frac(M_"nx", Omega_b) = frac(("31,040 lb-in"), "1.670") = "18,590 lb-in")$], "Allowable flexural strength about the x axis", "AISC 360-22 Eq. B3-2")
#calcline([$display(lambda_(r,c) = "1.4" sqrt(frac(E, F_y)) = "1.4" dot sqrt(frac(("29,000 ksi"), ("50.00 ksi"))) = "33.72")$], "Slender limit, walls of rectangular HSS in compression", "AISC 360-22 Table B4.1a, Case 6")
#calcline([$lambda_b = "13.00"$], "Wall slenderness: b/t of the 2.000 in walls, computed (design wall)", "Section properties (custom section)")
#calcline([$lambda_b = 13.00 <= lambda_(r,c) = 33.72$ #h(6pt) $arrow.r$ #h(6pt) *#"Nonslender"*], "Wall classification, compression: no noncompact category", "AISC 360-22 §B4.1a")
#calcline([$K = "2.100"$], "Effective length factor, fixed-free (recommended design value)", "AISC 360-22 Comm. Table C-A-7.1, case (e)")
#calcline([$h = "42.00 in"$], "Post height, top of concrete to top rail centerline", "Input")
#calcline([$display(L_c = K h = "2.100" ("42.00 in") = "88.20 in")$], "Effective length, with the unbraced length taken as the post height h", "AISC 360-22 §E2; Engineering judgement (EOR): unbraced length is the post height")
#calcline([$r = "0.7565 in"$], "Radius of gyration, the same about both axes", "Section properties (custom section)")
#calcline([$display(frac(L_c, r) = frac(("88.20 in"), ("0.7565 in")) = "116.6")$], "Effective slenderness ratio", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 116.6 <= 200$ #h(6pt) $arrow.r$ #h(6pt) *#"Within the recommended limit"*], "For members designed on the basis of compression, the effective slenderness ratio Lc/r preferably should not exceed 200.", "AISC 360-22 §E2, User Note")
#calcline([$display("4.71" sqrt(frac(E, F_y)) = "4.71" dot sqrt(frac(("29,000 ksi"), ("50.00 ksi"))) = "113.4")$], "Limit between inelastic and elastic buckling", "AISC 360-22 §E3(a), (b)")
#calcline([$display(F_e = frac(pi^("2") E, (frac(L_c, r))^("2")) = frac(pi^("2") ("29,000 ksi"), "116.6"^("2")) = "21.05 ksi")$], "Elastic buckling stress", "AISC 360-22 Eq. E3-4")
#calcline([$frac(L_c, r) = 116.6 > 113.4$ #h(6pt) $arrow.r$ #h(6pt) *#"Elastic buckling: Eq. E3-3"*], "", "AISC 360-22 §E3(a), (b)")
#calcline([$display(F_"cr" = "0.877" F_e = "0.877" ("21.05 ksi") = "18.46 ksi")$], "Critical stress", "AISC 360-22 Eq. E3-3")
#calcline([$A_g = "0.8973 in"^2$], "Gross area", "Section properties (custom section)")
#calcline([$display(P_n = F_"cr" A_g = ("18.46 ksi") ("0.8973 in"^2) = "16,570 lb")$], "Nominal compressive strength", "AISC 360-22 Eq. E3-1")
#calcline([$Omega_c = "1.670"$], "Safety factor for compression (ASD)", "AISC 360-22 §E1")
#calcline([$display(P_c = frac(P_n, Omega_c) = frac(("16,570 lb"), "1.670") = "9,921 lb")$], "Allowable compressive strength", "AISC 360-22 Eq. B3-2")
#subhead("Demand: outward, distributed load")
#calcline([$P_D = "42.37 lb"$], "D at the post: axial dead load", "Loading")
#calcline([$display(P_r = "1.0" P_D = "1.0" ("42.37 lb") = "42.37 lb")$], "Required axial strength: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (outward) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p (critical section at the top of the baseplate)", "Loading")
#calcline([$display(M_L = V_L L_"post" = ("300.0 lb") ("41.50 in") = "12,450 lb-in")$], "Live-load moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(M_r = "1.0" M_L = "1.0" ("12,450 lb-in") = "12,450 lb-in")$], "Required flexural strength", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$I_x = "0.5134 in"^4$], "Moment of inertia about the x axis, which this case bends", "Section properties (custom section)")
#calcline([$display(P_e = frac(pi^("2") E I_x, L_c^("2")) = frac(pi^("2") ("29,000 ksi") ("0.5134 in"^4), ("88.20 in")^("2")) = "18,890 lb")$], "Elastic critical buckling load, at the compression Lc", "AISC 360-22 Eq. A-8-5; Engineering judgement (EOR): Pe at Lc = 2.1h")
#calcline([$display(frac(alpha P_r, P_e) = frac("1.6" P_r, P_e) = frac("1.6" ("42.37 lb"), ("18,890 lb")) = "0.003588")$], "Second-order ratio", "AISC 360-22 App. 8")
#calcline([$frac(alpha P_r, P_e) <= 0.05$ #h(6pt) $arrow.r$ #h(6pt) *#"Second-order effects negligible: αPr/Pe = 0.003588; amplification taken as 1.0."*], "", "Engineering judgement (EOR): second-order limit")
#calcline([$display(frac(P_r, P_c) = frac(("42.37 lb"), ("9,921 lb")) = "0.004271")$], "Axial ratio, selects the interaction equation", "AISC 360-22 §H1.1")
#calcline([$frac(P_r, P_c) = 0.004271 < 0.2$ #h(6pt) $arrow.r$ #h(6pt) *#"Eq. H1-1b"*], "", "AISC 360-22 §H1.1")
#calcline([$display("Ratio" = frac(P_r, "2" P_c) + frac(M_r, M_"cx") = frac(("42.37 lb"), "2" ("9,921 lb")) + frac(("12,450 lb-in"), ("18,590 lb-in")) = "0.67")$], "Combined axial and flexure", "AISC 360-22 Eq. H1-1b")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.67 <= 1.00$ #h(10pt) #"OK"])

= Check 6: Post deflection

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#table(columns: (auto, auto, 1fr, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [*Demand* $Delta$], [*Capacity* $Delta_"allow"$], [*Ratio*], []), "Downward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Outward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.3200 in", "0.6917 in", "0.46", "", strong("Outward"), strong("Distributed"), strong("1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only"), strong("0.4800 in"), strong("0.6917 in"), strong("0.69"), strong("Controls"), "Inward", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.3200 in", "0.6917 in", "0.46", "", "Inward", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.4800 in", "0.6917 in", "0.69", "", "Upward", "", "Vertical load: no lateral deflection of the post", "", "", "", "", "Longitudinal", "Concentrated", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.3200 in", "0.6917 in", "0.46", "", "Longitudinal", "Distributed", "1.0L, horizontal\nEngineering judgement (EOR): serviceability, live load only", "0.4800 in", "0.6917 in", "0.69", "")

#heading(level: 2, "Controlling case: Outward, distributed (1.0L, horizontal; Engineering judgement (EOR): serviceability, live load only)")

#calcline([$L_"post" = "41.50 in"$], "Cantilever length, h - t_p", "Loading")
#calcline([$E = "29,000 ksi"$], "Modulus of elasticity", "AISC 360-22, Symbols")
#calcline([$I_x = "0.5134 in"^4$], "Moment of inertia about the x axis, which this case bends", "Section properties (custom section)")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (outward) at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(Delta_L = frac(V_L L_"post"^("3"), "3" E I_x) = frac(("300.0 lb") ("41.50 in")^("3"), "3" ("29,000 ksi") ("0.5134 in"^4)) = "0.4800 in")$], "Live-load deflection at the top of the post", "AISC Manual Table 3-23, Case 22")
#calcline([$display(Delta = "1.0" Delta_L = "1.0" ("0.4800 in") = "0.4800 in")$], "Live load only; dead load acts axially", "Engineering judgement (EOR): serviceability, live load only")
#calcline([$display(Delta_"allow" = frac(L_"post", "60") = frac(("41.50 in"), "60") = "0.6917 in")$], "Limit (h - t_p)/60", "Engineering judgement (EOR): post deflection limit, not code")
#calcline([$display("Ratio" = frac(Delta, Delta_"allow") = frac(("0.4800 in"), ("0.6917 in")) = "0.69")$], "Deflection / limit", "Engineering judgement (EOR): post deflection limit, not code")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.69 <= 1.00$ #h(10pt) #"OK"])

= Check 7: Post weld to baseplate

== Envelope summary

Every direction case and load type is computed. The full calculation follows for the controlling case only.

#text(size: 8pt)[#table(columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto), table.header([*Direction*], [*Load*], [*Combination*], [$f_n$ \ fiber], [$f_v$], [$f_r$], [*Capacity* per inch], [*Ratio*], []), "Downward", "Concentrated", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "32.01 lb/in\nuniform", "—", "32.01 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in", "0.01", "", "Downward", "Distributed", "1.0D + 1.0L, axial\nASCE 7-22 §2.4.1, Comb. 2", "45.22 lb/in\nuniform", "—", "45.22 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in", "0.02", "", "Outward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "1,710 lb/in\ncompression side", "26.42 lb/in", "1,710 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in", "0.61", "", strong("Outward"), strong("Distributed"), strong("1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2"), strong("2,562 lb/in\ncompression side"), strong("39.63 lb/in"), strong("2,562 lb/in"), strong("Weld 2,784 lb/in\nBase 8,700 lb/in"), strong("0.92"), strong("Controls"), "Inward", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "1,710 lb/in\ncompression side", "26.42 lb/in", "1,710 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in", "0.61", "", "Inward", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,562 lb/in\ncompression side", "39.63 lb/in", "2,562 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in", "0.92", "", "Upward", "Concentrated", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "23.06 lb/in\nuniform", "—", "23.06 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in", "0.01", "", "Upward", "Distributed", "0.6D + 1.0L, net axial\nEngineering judgement (EOR): upward case, not an ASCE combination", "36.27 lb/in\nuniform", "—", "36.27 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in", "0.01", "", "Longitudinal", "Concentrated", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "1,710 lb/in\ncompression side", "26.42 lb/in", "1,710 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in", "0.61", "", "Longitudinal", "Distributed", "1.0D axial, 1.0L horizontal\nASCE 7-22 §2.4.1, Comb. 2", "2,562 lb/in\ncompression side", "39.63 lb/in", "2,562 lb/in", "Weld 2,784 lb/in\nBase 8,700 lb/in", "0.92", "")]

#heading(level: 2, "Controlling case: Outward, distributed (1.0D axial, 1.0L horizontal; ASCE 7-22 §2.4.1, Comb. 2)")

#subhead("Weld properties")
#calcline([$a_"par" = "2.000 in"$], "Rect. tube 2 × 2 × 0.125 (custom): outside dimension parallel to the rail; the weld line is the post outline", "Section properties (custom section)")
#calcline([$a_"perp" = "2.000 in"$], "Outside dimension perpendicular to the rail", "Section properties (custom section)")
#calcline([$t_"des" = "0.1250 in"$], "Design wall thickness, Rect. tube 2 × 2 × 0.125 (custom): it sets the outside corner radius", "Section properties (custom section)")
#calcline([$display(R_o = "2" t_"des" = "2" ("0.1250 in") = "0.2500 in")$], "Outside corner radius", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$w = "0.1875 in"$], "Fillet weld leg size, all around (3/16 as entered)", "Input")
#calcline([$display(L_w = "2" (a_"par" - "2" R_o) + "2" (a_"perp" - "2" R_o) + "2" pi R_o = "2" (("2.000 in") - "2" ("0.2500 in")) + "2" (("2.000 in") - "2" ("0.2500 in")) + "2" dot pi ("0.2500 in") = "7.571 in")$], "Weld length: the post outline, four flats and four corner arcs", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(y_("c,t") = frac(a_"perp", "2") - R_o = frac(("2.000 in"), "2") - ("0.2500 in") = "0.7500 in")$], "Distance from the axis to the corner arc centers, a load across the guard", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(I_("w,t") = "2" (a_"par" - "2" R_o) (frac(a_"perp", "2"))^("2") + frac((a_"perp" - "2" R_o)^("3"), "6") + "2" pi R_o y_("c,t")^("2") + "8" y_("c,t") R_o^("2") + pi R_o^("3") = "2" (("2.000 in") - "2" ("0.2500 in")) (frac(("2.000 in"), "2"))^("2") + frac((("2.000 in") - "2" ("0.2500 in"))^("3"), "6") + "2" dot pi ("0.2500 in") ("0.7500 in")^("2") + "8" ("0.7500 in") ("0.2500 in")^("2") + pi ("0.2500 in")^("3") = "4.870 in"^3)$], "Moment of inertia of the weld line, a load across the guard: flats and corner arcs", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(S_("w,t") = frac(I_("w,t"), frac(a_"perp", "2")) = frac(("4.870 in"^3), frac(("2.000 in"), "2")) = "4.870 in"^2)$], "Section modulus of the weld line, a load across the guard", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(y_("c,l") = frac(a_"par", "2") - R_o = frac(("2.000 in"), "2") - ("0.2500 in") = "0.7500 in")$], "Distance from the axis to the corner arc centers, a load along the rail", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(I_("w,l") = "2" (a_"perp" - "2" R_o) (frac(a_"par", "2"))^("2") + frac((a_"par" - "2" R_o)^("3"), "6") + "2" pi R_o y_("c,l")^("2") + "8" y_("c,l") R_o^("2") + pi R_o^("3") = "2" (("2.000 in") - "2" ("0.2500 in")) (frac(("2.000 in"), "2"))^("2") + frac((("2.000 in") - "2" ("0.2500 in"))^("3"), "6") + "2" dot pi ("0.2500 in") ("0.7500 in")^("2") + "8" ("0.7500 in") ("0.2500 in")^("2") + pi ("0.2500 in")^("3") = "4.870 in"^3)$], "Moment of inertia of the weld line, a load along the rail: flats and corner arcs", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(S_("w,l") = frac(I_("w,l"), frac(a_"par", "2")) = frac(("4.870 in"^3), frac(("2.000 in"), "2")) = "4.870 in"^2)$], "Section modulus of the weld line, a load along the rail", "Engineering judgement (EOR): weld line on the true rounded rectangle")
#calcline([$display(t_e = "0.707" w = "0.707" ("0.1875 in") = "0.1326 in")$], "Effective throat, equal-leg fillet", "AISC 360-22 §J2.2a")
#subhead("Moment arm")
#calcline([$L_"post" = "41.50 in"$], "Moment arm, h - t_p: guard load at the top rail centerline, weld at the top of the baseplate", "Loading")
#subhead("Fillet size limits")
#calcline([$t_"post,nom" = "0.1250 in"$], "Post nominal wall thickness, Rect. tube 2 × 2 × 0.125 (custom)", "Section properties (custom section)")
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
#calcline([$"Post wall at the weld"$ #h(6pt) $arrow.r$ #h(6pt) *#"Covered by Check 5"*], "Post wall at the weld: covered by Check 5. The wall carries the weld force as stress along the post axis, the same demand as Check 5 at its critical section; member shear is not checked (stated assumption).", "Engineering judgement (EOR): post wall at the weld covered by Check 5")
#subhead("Demand: outward, distributed load")
#calcline([$P_D = "42.37 lb"$], "D at the post: axial dead load at the top of the baseplate", "Loading")
#calcline([$display(P = "1.0" P_D = "1.0" ("42.37 lb") = "42.37 lb")$], "Axial force on the weld: dead load, compression", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal (outward), at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(V = "1.0" V_L = "1.0" ("300.0 lb") = "300.0 lb")$], "Horizontal force on the weld", "ASCE 7-22 §2.4.1, Comb. 2")
#calcline([$display(M = V L_"post" = ("300.0 lb") ("41.50 in") = "12,450 lb-in")$], "Moment at the top of the baseplate", "AISC Manual Table 3-23, Case 22")
#calcline([$display(f_a = frac(P, L_w) = frac(("42.37 lb"), ("7.571 in")) = "5.596 lb/in")$], "Axial force per inch of weld, compression, uniform along the weld line", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_b = frac(M, S_("w,t")) = frac(("12,450 lb-in"), ("4.870 in"^2)) = "2,556 lb/in")$], "Bending force per inch at the extreme fiber", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_(n,"c") = f_a + f_b = ("5.596 lb/in") + ("2,556 lb/in") = "2,562 lb/in")$], "Normal force per inch, compression side of bending: axial and bending add", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_(n,"t") = abs(f_a - f_b) = abs(("5.596 lb/in") - ("2,556 lb/in")) = "2,551 lb/in")$], "Normal force per inch, tension side of bending", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$f_(n,"c") = "2,562 lb/in" >= f_(n,"t") = "2,551 lb/in"$ #h(6pt) $arrow.r$ #h(6pt) *#"Compression side governs"*], "No bearing credit: both extreme fibers checked", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_n = f_(n,"c") = "2,562 lb/in")$], "Normal force per inch at the governing fiber, compression side", "Engineering judgement (EOR): no bearing credit at the weld")
#calcline([$display(f_v = frac(V, L_w) = frac(("300.0 lb"), ("7.571 in")) = "39.63 lb/in")$], "Shear per inch of weld, taken as uniform along the weld line", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(f_r = sqrt(f_n^("2") + f_v^("2")) = sqrt(("2,562 lb/in")^("2") + ("39.63 lb/in")^("2")) = "2,562 lb/in")$], "Resultant per inch at the governing fiber: vector sum", "Engineering judgement (EOR): elastic weld as a line")
#calcline([$display(R_n = F_"nw" t_e k_"ds" = ("42.00 ksi") ("0.1326 in") dot "1.000" = "5,568 lb/in")$], "Nominal fillet weld strength per inch", "AISC 360-22 Eq. J2-4")
#calcline([$display(frac(R_n, Omega_w) = frac(("5,568 lb/in"), "2.000") = "2,784 lb/in")$], "Allowable weld metal strength per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_w = frac(f_r, frac(R_n, Omega_w)) = frac(("2,562 lb/in"), ("2,784 lb/in")) = "0.92")$], "Weld metal: demand / capacity", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio"_"BM" = frac(f_r, frac(R_(n,"BM"), Omega_"BM")) = frac(("2,562 lb/in"), ("8,700 lb/in")) = "0.29")$], "Baseplate fusion face: the resultant per inch", "AISC 360-22 Eq. B3-2")
#calcline([$display("Ratio" = "max"("Ratio"_w, "Ratio"_"BM") = "max"("0.9204", "0.2945") = "0.92")$], "The larger of weld metal and base metal", "AISC 360-22 Eq. B3-2")

#align(right, text(size: 12pt, weight: "bold")[$"Ratio" = 0.92 <= 1.00$ #h(10pt) #"OK"])

= Summary

#table(columns: (1fr, auto, auto, auto, auto, auto), table.header(strong("Check"), strong("Demand"), strong("Capacity"), strong("Ratio"), strong("Controlling direction"), strong("Result")), "1. Top rail bending", "Mrx = 203.1 lb-in; Mry = 3,600 lb-in", "Mcx = 28,300 lb-in; Mcy = 21,400 lb-in", "0.18", "Outward, concentrated", "OK", "2. Top rail deflection", "0.07989 in", "0.6000 in", "0.13", "Outward, concentrated", "OK", "3. Top rail weld to post", "154.8 lb/in", "1,856 lb/in (weld metal)", "0.08", "Longitudinal, distributed", "OK", "4a. Intermediate rail", "0.2135 in", "0.6000 in", "0.36", "Downward, deflection", "OK", "4b. Intermediate rail weld to post", "13.66 lb/in", "1,343 lb/in (base metal)", "0.01", "Downward, component", "OK", "5. Post combined axial and flexure", "Pr = 42.37 lb; Mr = 12,450 lb-in", "Pc = 9,921 lb; Mc = 18,590 lb-in", "0.67", "Outward, distributed", "OK", "6. Post deflection", "0.4800 in", "0.6917 in", "0.69", "Outward, distributed", "OK", "7. Post weld to baseplate", "2,562 lb/in", "2,784 lb/in (weld metal)", "0.92", "Outward, distributed", "OK")

= Anchor reactions

LRFD reactions at the top of concrete, for direct input into anchor software: reporting, not a pass/fail check. Each set is simultaneous: the shear, axial force and moment that occur together.

#text(weight: "bold", "Baseplate: B = 6.000 in (parallel to rail) × N = 8.000 in (perpendicular to rail)")

#subhead("Dead load at the base")
#calcline([$D_"rail" = "22.57 lb"$], "Top rail", "Loading")
#calcline([$D_"int" = "9.243 lb"$], "Intermediate rail", "Loading")
#calcline([$D_"post" = "10.56 lb"$], "Post, over h - t_p", "Loading")
#calcline([$rho = "0.2836 lb/in"^3$], "Steel unit weight", "AISC Manual 16th Ed., Part 17")
#calcline([$B = "6.000 in"$], "Baseplate, parallel to the rail", "Input")
#calcline([$N = "8.000 in"$], "Baseplate, perpendicular to the rail", "Input")
#calcline([$t_p = "0.5000 in"$], "Baseplate thickness", "Input")
#calcline([$display(W_"bp" = rho B N t_p = ("0.2836 lb/in"^3) ("6.000 in") ("8.000 in") ("0.5000 in") = "6.806 lb")$], "Baseplate weight: in the reaction sets only, below the critical section of Checks 5 and 7", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$display(D = D_"rail" + D_"int" + D_"post" + W_"bp" = ("22.57 lb") + ("9.243 lb") + ("10.56 lb") + ("6.806 lb") = "49.17 lb")$], "Dead load at the base", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#subhead("Governing guard load type")
#calcline([$P = "200.0 lb"$], "Concentrated guard load P, at the top of the post", "Loading")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")
#calcline([$w_L L = "300.0 lb" > P = "200.0 lb"$ #h(6pt) $arrow.r$ #h(6pt) *#"Distributed load governs"*], "The larger at the top of the post", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Lateral set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "480.0 lb", "−44.26 lb (compression)", "20,160 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D axial, 1.6L horizontal; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "22.57 lb", "D, intermediate rail", "9.243 lb", "D, post", "10.56 lb", "D, baseplate", "6.806 lb", strong("D, total"), strong("49.17 lb"))

#"V and M act in the same vertical plane; M = V·h."

#"Lateral set applies in any horizontal direction; enter it in the anchor software in the orientation that governs the anchor pattern. Loads can reverse."

#subhead("Demand: lateral, distributed load")
#calcline([$D = "49.17 lb"$], "Dead load at the base", "Reactions")
#calcline([$display(abs(N_u) = "0.9" D = "0.9" ("49.17 lb") = "44.26 lb")$], "Axial force at the base: dead load, compression", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(V_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, horizontal at the top of the post, in any horizontal direction", "Stated assumption: the tributary length is the span")
#calcline([$display(V_u = "1.6" V_L = "1.6" ("300.0 lb") = "480.0 lb")$], "Base shear", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
#calcline([$h = "42.00 in"$], "Moment arm: top rail centerline to top of concrete", "Input")
#calcline([$display(M_u = V_u h = ("480.0 lb") ("42.00 in") = "20,160 lb-in")$], "Base moment at the top of concrete: V_u at the top rail centerline, arm h", "Engineering judgement (EOR): reactions at the top of concrete, arm h")

== Upward set

#table(columns: (1fr, 1fr, 1fr), table.header(strong("V"), strong("N"), strong("M")), "0 lb", "+435.7 lb (tension)", "0 lb-in")

#text(size: 8.5pt, "N positive = tension (uplift), matching common anchor-software convention. V and M are reversible; apply them in the governing direction.")

#table(columns: (auto, 1fr), "Combination", "0.9D + 1.6L, net axial; Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination", "Governing load type", "Distributed", "D, top rail", "22.57 lb", "D, intermediate rail", "9.243 lb", "D, post", "10.56 lb", "D, baseplate", "6.806 lb", strong("D, total"), strong("49.17 lb"))

#subhead("Demand: upward, distributed load")
#calcline([$D = "49.17 lb"$], "Dead load at the base", "Reactions")
#calcline([$w_L = "4.167 lb/in"$], "Uniform guard load", "Loading")
#calcline([$L = "72.00 in"$], "Span: the tributary length for the post", "Input")
#calcline([$display(P_L = w_L L = ("4.167 lb/in") ("72.00 in") = "300.0 lb")$], "Uniform guard load collected over the span, upward at the top of the post", "Stated assumption: the tributary length is the span")
#calcline([$display(abs(N_u) = "1.6" P_L - "0.9" D = "1.6" ("300.0 lb") - "0.9" ("49.17 lb") = "435.7 lb")$], "Axial force at the base: net tension (uplift), guard load opposing dead load", "Engineering judgement (EOR): anchor reactions, LRFD, not an ASCE combination")
