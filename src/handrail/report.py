"""Render a calc to PDF with Typst.

Python writes one Typst source file for the whole calc, then the typst
package compiles it. Calc lines are printed from their records (ADR 0002);
this module decides only layout. User-entered text enters Typst only as
string literals (typst_str), so it prints as text and never runs as markup.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import typst

from handrail.calc import Line, fmt_quantity_plain, fmt_ratio, fmt_sig, typst_str
from handrail.intermediate import ComponentCase
from handrail.post import PostCase
from handrail.dimensions import Dimension
from handrail.project import OWN_SECTION, SAME_AS_TOP, Member
from handrail.directions import LATERAL
from handrail.reactions import Reactions, ReactionSet
from handrail.registry import Registry
from handrail.results import Case, Check, Results
from handrail.shapes import PipeSection
from handrail.welds import WeldCase
from handrail.version import Stamp

# The tool's own stated assumptions (docs/brief/output.md). Locked: always printed;
# the engineer can add to them in the project file but not edit or remove them.
LOCKED_ASSUMPTIONS = (
    "No shear checks in any member.",
    "Interior post; the tributary length is the span. End posts and rail overhangs are not checked.",
    ("Post loads use tributary length = span; rail continuity effects on post reactions are neglected "
     "(engineering judgement)."),
    ("The top rail runs continuously over the post; the post is coped and welded to its underside. "
     "The rail is designed as a simple span."),
    ("The rail to post weld is modeled as a flat ring of the post's perimeter at the underside of the rail, "
     "with eccentricity e = half the rail depth from the rail centerline; this is conservative against the "
     "saddle centroid (2R/π for equal round diameters). It is modeled as a fillet of the entered size all "
     "around, although at equal diameters the sides of the saddle form a flare-bevel joint."),
    ("The intermediate rail to post weld is modeled as a flat ring of the intermediate rail's perimeter at the "
     "post face, a simple shear connection consistent with the simple-span intermediate rail: the end reaction "
     "acts at the weld with no end moment. It is modeled as a fillet of the entered size all around, although at "
     "equal diameters the sides of the saddle form a flare-bevel joint."),
    ("Local strength of the rail wall at the post, and of the post wall at the intermediate rail (AISC 360-22 "
     "Chapter K chord limit states), is not checked."),
    "The component load's effect on the post is not checked.",
    "Guard loads are not combined with floor or roof live load; wind, snow and ice are not considered.",
    "Base reactions can reverse; direction is set in the anchor software.",
    "The baseplate is rigid; the post is fixed at the top of the baseplate.",
    ("Baseplate thickness and bending are not checked; baseplate and anchorage design by others "
     "(e.g., PROFIS)."),
    ("Notional loads (AISC 360-22 App. 7) are neglected. In gravity-only combinations they produce a "
     "negligible moment, and the reported axial-only ratio bounds the H1-1b result."),
)

REFERENCES = (
    "AISC 360-22, Specification for Structural Steel Buildings",
    "ASCE/SEI 7-22, Minimum Design Loads and Associated Criteria for Buildings and Other Structures",
    "AISC Steel Construction Manual, 16th Edition",
    "AISC Shapes Database v16.0",
)

TEMPLATE = r"""
#let draft = @@DRAFT@@
#let footer-code = @@FOOTER_CODE@@
#let footer-reg = @@FOOTER_REG@@

#set document(title: @@TITLE@@)
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
"""


# What the report may rely on, said for the type checker (typing.cast changes
# nothing at run time). The report prints the controlling case and the
# ratios of computed checks and checked cases only, and those always exist.


def _controlling(chk: Check) -> Case:
    """The controlling case of a computed check."""
    return cast(Case, chk.controlling)


def _ratio(c: Case) -> float:
    """The ratio of a checked case."""
    return cast(float, c.ratio)


def _lines(lines: list[Line]) -> str:
    out = []
    for ln in lines:
        if ln.kind == "heading":
            out.append(f"#subhead({typst_str(ln.symbol)})")
            continue
        if ln.kind == "decision":
            eq = f"[${ln.symbol}$ #h(6pt) $arrow.r$ #h(6pt) *#{typst_str(cast(str, ln.text))}*]"
        elif ln.symbolic is not None:
            parts = [ln.symbol] + ([ln.symbolic] if ln.symbolic != ln.symbol else [])
            if ln.substituted not in (ln.symbolic, f"({ln.result})", ln.result):
                parts.append(cast(str, ln.substituted))
            parts.append(ln.result)
            eq = f"[$display({' = '.join(parts)})$]"
        else:
            eq = f"[${ln.symbol} = {ln.result}$]"
        out.append(f"#calcline({eq}, {typst_str(ln.note)}, {typst_str(ln.cite)})")
    return "\n".join(out)


def _table(header: list[str], rows: list[list[str]], columns: str, bold_rows=(), raw_header=False,
           stroke: str | None = None) -> str:
    """A table. Cells are user-safe string literals; with raw_header, header
    cells are Typst content written by this module (for math symbols).
    ``stroke`` is a Typst stroke value ("none" for a borderless table); left
    out, the document's table stroke applies."""
    head = [h if raw_header else f"strong({typst_str(h)})" for h in header]
    cells = [f"table.header({', '.join(head)})"] if head else []
    for i, row in enumerate(rows):
        for c in row:
            cells.append(f"strong({typst_str(c)})" if i in bold_rows else typst_str(c))
    stroke_arg = f"stroke: {stroke}, " if stroke is not None else ""
    return f"#table(columns: {columns}, {stroke_arg}{', '.join(cells)})"


def _envelope(chk: Check) -> str:
    ctrl = chk.controlling
    rows, bold = [], []
    for i, c in enumerate(chk.cases):
        if c.status == "checked":
            rows.append([
                c.direction, c.load_type, c.combination,
                fmt_quantity_plain(c.demand), fmt_quantity_plain(c.capacity), fmt_ratio(_ratio(c)),
                "Controls" if c is ctrl else "",
            ])
            if c is ctrl:
                bold.append(i)
        else:
            rows.append([c.direction, c.load_type or "", c.remark, "", "", "", ""])
    return _table(
        ["[*Direction*]", "[*Load*]", "[*Combination*]", f"[*Demand* ${chk.demand_label}$]",
         f"[*Capacity* ${chk.capacity_label}$]", "[*Ratio*]", "[]"],
        rows, "(auto, auto, 1fr, auto, auto, auto, auto)", bold, raw_header=True,
    )


def _envelope_5(chk: Check) -> str:
    """Check 5 envelope: axial and moment demands, each with its capacity on the
    line below, the equation, and alpha Pr/Pe for every case the second-order
    stop checks (plan D1)."""
    ctrl = chk.controlling
    rows, bold = [], []
    for i, c in enumerate(cast("list[PostCase]", chk.cases)):
        if c.status == "checked":
            sense = "tension" if c.sense == "tension" else "comp."
            _, P_cap, _, M_cap = _post_terms(c)
            rows.append([
                c.direction, c.load_type, c.combination,
                f"{fmt_quantity_plain(c.Pr)} {sense}\n{P_cap}",
                f"{fmt_quantity_plain(c.Mr)}\n{M_cap}" if c.Mr is not None else "—",
                c.equation.replace(" (", "\n("),  # the source equation on its own line keeps the column narrow
                fmt_sig(c.second_order) if c.second_order is not None else "—",
                fmt_ratio(_ratio(c)),
                "Controls" if c is ctrl else "",
            ])
            if c is ctrl:
                bold.append(i)
        else:
            rows.append([c.direction, c.load_type or "", c.remark, "", "", "", "", "", ""])
    table = _table(
        ["[*Direction*]", "[*Load*]", "[*Combination*]",
         "[*Axial* $P_r$ \\ capacity $P_c$ or $P_t$]", "[*Moment* $M_r$ \\ capacity $M_c$]",
         "[*Equation*]", "[$frac(alpha P_r, P_e)$]", "[*Ratio*]", "[]"],
        rows, "(auto, auto, 1fr, auto, auto, auto, auto, auto, auto)", bold, raw_header=True,
    )
    return f"#text(size: 8pt)[{table}]"  # nine columns: set small so the rows stay a few lines


def _envelope_weld(chk: Check) -> str:
    """Weld envelope (Checks 3 and 7): the forces per inch at the governing
    fiber, theta and k_ds where k_ds comes from theta (Check 7), and the weld
    metal and base metal capacities per inch."""
    with_theta = any(c.theta is not None for c in cast("list[WeldCase]", chk.checked))
    ctrl = chk.controlling
    rows, bold = [], []
    for i, c in enumerate(cast("list[WeldCase]", chk.cases)):
        if c.status == "checked":
            row = [c.direction, c.load_type, c.combination,
                   f"{fmt_quantity_plain(c.f_n)}\n{c.fiber}" if c.f_n is not None else "—\nshear only",
                   fmt_quantity_plain(c.f_v) if c.f_v is not None else "—",
                   fmt_quantity_plain(c.f_r)]
            if with_theta:
                row.append(f"{fmt_quantity_plain(c.theta)}\n{fmt_sig(cast(float, c.k_ds))}")  # a checked case has k_ds
            row += [_weld_capacities(c), fmt_ratio(_ratio(c)), "Controls" if c is ctrl else ""]
            rows.append(row)
            if c is ctrl:
                bold.append(i)
        else:
            rows.append([c.direction, c.load_type or "", c.remark] + [""] * (7 if with_theta else 6))
    header = ["[*Direction*]", "[*Load*]", "[*Combination*]", "[$f_n$ \\ fiber]", "[$f_v$]", "[$f_r$]"]
    columns = "(auto, auto, 1fr, auto, auto, auto, "
    if with_theta:
        header.append('[$theta$ \\ $k_"ds"$]')
        columns += "auto, "
    header += ["[*Capacity* per inch]", "[*Ratio*]", "[]"]
    columns += "auto, auto, auto)"
    table = _table(header, rows, columns, bold, raw_header=True)
    return f"#text(size: 8pt)[{table}]"


def _envelope_4a(chk: Check) -> str:
    """Check 4a envelope: bending and deflection, each downward and
    horizontal, with the controlling row over both limit states."""
    ctrl = chk.controlling
    rows, bold = [], []
    for i, c in enumerate(cast("list[ComponentCase]", chk.cases)):
        if c.status == "checked":
            rows.append([c.limit_state, c.direction, c.combination, fmt_quantity_plain(c.demand),
                         fmt_quantity_plain(c.capacity), fmt_ratio(_ratio(c)), "Controls" if c is ctrl else ""])
            if c is ctrl:
                bold.append(i)
        else:
            rows.append([c.limit_state, c.direction, c.remark, "", "", "", ""])
    return _table(
        ["[*Limit state*]", "[*Direction*]", "[*Combination*]", "[*Demand* $M_a$ or $Delta$]",
         '[*Capacity* $M_n / Omega_b$ or $Delta_"allow"$]', "[*Ratio*]", "[]"],
        rows, "(auto, auto, 1fr, auto, auto, auto, auto)", bold, raw_header=True,
    )


def _governing_by_limit_state(chk: Check) -> list[ComponentCase]:
    """Check 4a: the governing case of each limit state, the controlling one
    first, so bending and deflection each print in full as Checks 1 and 2 do."""
    out: dict[str, ComponentCase] = {}
    for c in cast("list[ComponentCase]", chk.checked):
        best = out.get(c.limit_state)
        if best is None or _ratio(c) > _ratio(best):
            out[c.limit_state] = c
    ctrl = cast(ComponentCase, chk.controlling)
    return [ctrl] + [c for c in out.values() if c is not ctrl]


def _weld_capacities(c: WeldCase) -> str:
    """Weld metal, and base metal where the fusion face carries force in the case."""
    base = f"Base {fmt_quantity_plain(c.base_allow)}" if c.base_demand is not None else "Base —"
    return f"Weld {fmt_quantity_plain(c.weld_allow)}\n{base}"


def _check(chk: Check) -> str:
    out = [f"= Check {chk.number}: {chk.title}"]
    if chk.bypassed:
        out.append("*Bypassed by engineer.* No calculation is shown.")
        return "\n\n".join(out)
    if chk.observation:
        out.append(f"#{typst_str(chk.observation)}")
        if chk.observation_lines:
            out.append(_lines(chk.observation_lines))
        return "\n\n".join(out)
    for f in chk.flags:
        out.append(f"#flag({typst_str(f)})")
    out.append("== Envelope summary")
    if isinstance(chk.controlling, ComponentCase):
        out.append("Each limit state is computed in both directions of the component load. The full calculation "
                   "follows for the governing case of each limit state.")
    elif chk.number == "4b":
        out.append("Both directions of the component load are computed. The full calculation follows for the "
                   "controlling case only.")
    else:
        out.append("Every direction case and load type is computed. The full calculation follows for the "
                   "controlling case only.")
    if chk.number == 5:
        out.append(_envelope_5(chk))
    elif isinstance(chk.controlling, WeldCase):
        out.append(_envelope_weld(chk))
    elif isinstance(chk.controlling, ComponentCase):
        out.append(_envelope_4a(chk))
    else:
        out.append(_envelope(chk))
    ctrl = _controlling(chk)
    printed = _governing_by_limit_state(chk) if isinstance(ctrl, ComponentCase) else [ctrl]
    for c in printed:
        combination = c.combination.replace("\n", "; ")  # table cells break the label; a heading doesn't
        # A case other than the controlling one is printed for Check 4a only.
        title = "Controlling case" if c is ctrl else f"Governing {cast(ComponentCase, c).limit_state.lower()} case"
        out.append(f"#heading(level: 2, {typst_str(f'{title}: {c.label} ({combination})')})")
        out.append(_lines(c.lines))
    # The verdict is decided once, by the Check; the page only prints it. The
    # relation is the Check's own comparison of the ratio alone: a check can
    # be NG with its ratio under 1.00 (a weld below the minimum size), and
    # then says why.
    why = f"#h(6pt) #{typst_str('; ' + chk.summary_flag)}" if chk.failures else ""
    out.append(f"#align(right, text(size: 12pt, weight: \"bold\")[${chk.within_unity.text}$ "
               f"{why}#h(10pt) #{typst_str(chk.verdict)}])")
    return "\n\n".join(out)


def _demand_capacity(c: Case) -> tuple[str, str]:
    """Summary cells. An interaction check has no single demand and capacity, so
    Check 5 prints its axial and moment terms side by side. A weld check prints
    the line that governs its ratio, weld metal or base metal, as the case set it."""
    if isinstance(c, WeldCase):
        return fmt_quantity_plain(c.demand), f"{fmt_quantity_plain(c.capacity)} ({c.governs})"
    if not isinstance(c, PostCase):
        return fmt_quantity_plain(c.demand), fmt_quantity_plain(c.capacity)
    Pr, P_cap, Mr, M_cap = _post_terms(c)
    if c.Mr is None:
        return Pr, P_cap
    return f"{Pr}; {Mr}", f"{P_cap}; {M_cap}"


def _post_terms(c: PostCase) -> tuple[str, ...]:
    """'Pr = ...', 'Pc = ...' (or 'Pt = ...' in tension), 'Mr = ...', 'Mc = ...';
    the moment terms are empty in the axial-only cases. The envelope and the
    summary both print these."""
    P_cap = "Pt" if c.sense == "tension" else "Pc"
    terms = [f"Pr = {fmt_quantity_plain(c.Pr)}", f"{P_cap} = {fmt_quantity_plain(c.P_allow)}", "", ""]
    if c.Mr is not None:
        terms[2:] = [f"Mr = {fmt_quantity_plain(c.Mr)}", f"Mc = {fmt_quantity_plain(c.M_allow)}"]
    return tuple(terms)


def _summary(checks: list[Check]) -> str:
    rows = []
    for chk in checks:
        if not chk.computed:
            rows.append([f"{chk.number}. {chk.title}", "", "", "", "", chk.verdict])
            continue
        c = _controlling(chk)
        demand, capacity = _demand_capacity(c)
        verdict = f"{chk.verdict} ({chk.summary_flag})" if chk.summary_flag else chk.verdict
        rows.append([f"{chk.number}. {chk.title}", demand, capacity, fmt_ratio(_ratio(c)), c.label, verdict])
    return _table(["Check", "Demand", "Capacity", "Ratio", "Controlling direction", "Result"], rows,
                  "(1fr, auto, auto, auto, auto, auto)")


# Printed under each reaction table (S4-7): the sign convention and the
# reversibility of V and M. Output wording, not a code provision.
REACTION_CONVENTION = ("N positive = tension (uplift), matching common anchor-software convention. "
                       "V and M are reversible; apply them in the governing direction.")
SAME_PLANE = "V and M act in the same vertical plane; M = V·h."


def _signed_N(N) -> str:
    """N with its sign and its sense in words (S4-7): '+430.5 lb (tension)'."""
    text = fmt_quantity_plain(abs(N))
    if N.magnitude > 0:
        return f"+{text} (tension)"
    if N.magnitude < 0:
        return f"\u2212{text} (compression)"
    return text


def _plate(proj) -> str:
    bp = proj.baseplate
    return (f"B = {fmt_quantity_plain(bp.B.value)} (parallel to rail) \u00d7 "
            f"N = {fmt_quantity_plain(bp.N.value)} (perpendicular to rail)")


def _reaction_set(rs: ReactionSet, reactions: Reactions) -> list[str]:
    out = [f"== {rs.name} set"]
    if not rs.present:
        out.append(f"#{typst_str(rs.remark + '.')}")
        out.append(_lines(rs.lines))
        return out
    out.append(_table(["V", "N", "M"], [[fmt_quantity_plain(rs.V), _signed_N(rs.N), fmt_quantity_plain(rs.M)]],
                      "(1fr, 1fr, 1fr)"))
    out.append(f"#text(size: 8.5pt, {typst_str(REACTION_CONVENTION)})")
    rows = [["Combination", rs.combination.replace("\n", "; ")],
            ["Governing load type", rs.load_type]]
    rows += [[f"D, {name.lower()}" if name != "Total D" else "D, total", fmt_quantity_plain(v)]
             for name, v in reactions.dead]
    out.append(_table([], rows, "(auto, 1fr)", bold_rows=(len(rows) - 1,)))
    if rs.name == LATERAL:
        out.append(f"#{typst_str(SAME_PLANE)}")
        out.append(f"#{typst_str(reactions.lateral_note)}")
    out.append(_lines(rs.lines))
    return out


def _reactions(results: Results) -> list[str]:
    """The reaction tables, after the summary (S4-7)."""
    r = cast(Reactions, results.reactions)  # engine.compute always fills the reaction sets
    out = ["= Anchor reactions",
           ("LRFD reactions at the top of concrete, for direct input into anchor software: reporting, not a "
            "pass/fail check. Each set is simultaneous: the shear, axial force and moment that occur together."),
           f"#text(weight: \"bold\", {typst_str('Baseplate: ' + _plate(results.project))})",
           _lines(r.head)]
    for rs in r.sets:
        out += _reaction_set(rs, r)
    return out


def _derived_lengths(results: Results) -> str:
    """Each derived length printed from its own calc line: the note, the formula
    and the value are the ones that computed it (ADR 0002). Symbols and
    formulas are Typst math the calc writes, never user text."""
    cells = [('table.header(strong("Derived length"), strong("Formula"), strong("Inches"), '
             'strong("Computed in"))')]
    for ln, where in results.derived_lengths:
        cells += [typst_str(ln.note), f"[${ln.symbol} = {ln.symbolic}$]",
                  typst_str(fmt_quantity_plain(ln.value)), typst_str(where)]
    return f"#table(columns: (1fr, auto, auto, auto), {', '.join(cells)})"


def build_source(results: Results, registry: Registry, stamp: Stamp) -> str:
    proj = results.project
    info = proj.info
    # The DRAFT stamp and the "Draft code values" list are filled last, after
    # the whole body is built (issue #11, option A): an entry read anywhere
    # below is then stamped and listed, wherever in the build it is read.
    # Until then the template is src[0], still holding its @@ tokens, and
    # draft_list_at marks where the list goes in the front matter.
    # The design method is stated as a registry-cited line; the references list
    # names only the specification, so adding LRFD later does not change it.
    asd = registry.get("aisc360.B3.2.asd")
    src = [TEMPLATE]

    # Front matter
    src.append("#align(center, text(size: 16pt, weight: \"bold\")[Guard Calculation])")
    src.append("#align(center)[Top rail bending and deflection; top rail weld to post; intermediate rail and "
               "its weld to the post; post combined axial and flexure, and deflection; post weld to baseplate; "
               "anchor reactions]")
    src.append("== Project")
    src.append(_table([], [["Project", info.name], ["Phase", info.phase], ["Description", info.description]],
                      "(auto, 1fr)", stroke="none"))
    src.append("Loading is per ASCE 7-22.")
    src.append(f"#text(weight: \"bold\", {typst_str(f'Design method: {asd.value} per {asd.cite}')})")
    src.append("== Assumptions")
    items = [f"+ #{typst_str(a)}" for a in LOCKED_ASSUMPTIONS]
    items += [f"+ #{typst_str(a)} _(added by engineer)_" for a in info.assumptions]
    src.append("\n".join(items))
    src.append("== References")
    src.append("\n".join(f"- #{typst_str(r)}" for r in REFERENCES + info.references))
    src.append("== Sketch")
    src.append('#block(width: 100%, height: 2.2in, stroke: (dash: "dashed", paint: luma(150)), '
               'align(center + horizon, text(fill: luma(120))[Image area (image upload is a later slice)]))')
    draft_list_at = len(src)

    # Dimensions
    src.append("= Dimensions")
    src.append("Every dimension as entered, and as the tool read it. A bare number is inches.")
    dims = [
        ("Span, post to post (c/c)", proj.span),
        ("Post height h, top of concrete to top rail centerline", proj.post_height),
        ("Baseplate thickness t_p", proj.baseplate_thickness),
        ("Baseplate B, parallel to the rail", proj.baseplate.B),
        ("Baseplate N, perpendicular to the rail", proj.baseplate.N),
        ("Fillet weld, top rail to post", proj.welds.rail_to_post),
        ("Fillet weld, post to baseplate", proj.welds.post_to_baseplate),
    ]
    if proj.intermediate_rail.state == OWN_SECTION:
        # Its own section always has its own weld size (project.py requires it).
        dims.append(("Fillet weld, intermediate rail to post",
                     cast(Dimension, proj.welds.intermediate_rail_to_post)))
    rows = [[label, d.entered, d.normalized, fmt_quantity_plain(d.value)] for label, d in dims]
    src.append(_table(["Dimension", "As entered", "Read as", "Inches"], rows, "(1fr, auto, auto, auto)"))
    src.append("Derived lengths, each computed in the calc where it is used:")
    src.append(_derived_lengths(results))

    # Section properties
    src.append("= Section properties")
    src.append(f"#text({typst_str(f'Top rail: {results.rail.label}, {proj.top_rail.grade}.')}) "
               "Properties are used exactly as published in the AISC Shapes Database v16.0.")
    src.append(_lines(results.section_lines))
    src.append(f"#text({typst_str(f'Post: {results.post.label}, {proj.post.grade}.')})")
    src.append(_lines(results.post_section_lines))
    state = proj.intermediate_rail.state
    if state == OWN_SECTION:
        member = cast(Member, proj.intermediate_member)
        inter_label = cast(PipeSection, results.inter).label
        src.append(f"#text({typst_str(f'Intermediate rail: {inter_label}, {member.grade}.')})")
        src.append(_lines(results.inter_section_lines))
    elif state == SAME_AS_TOP:
        src.append(f"#text({typst_str('Intermediate rail: same section and grade as the top rail.')})")
    else:
        src.append(f"#text({typst_str('Intermediate rail: none.')})")
    materials = f"Baseplate: {proj.baseplate.grade}. Welds: fillet, all around, electrode {proj.welds.electrode}."
    src.append(f"#text({typst_str(materials)})")

    # Loading
    src.append("= Loading")
    src.append("Guard loads per ASCE 7-22. The concentrated and uniform loads are separate load types and do "
               "not act concurrently. Each check applies them in every direction case and reports the "
               "controlling one.")
    src.append(_lines(results.loading.lines))
    if results.loading.exempt:
        src.append("== Uniform load exemption (engineer's statement)")
        src.append(f"#quote(block: true)[#{typst_str(results.loading.exemption_statement)}]")

    for chk in results.checks:
        src.append(_check(chk))

    src.append("= Summary")
    src.append(_summary(results.checks))
    src += _reactions(results)

    # Last: every registry read is behind us, so this is every drafted entry
    # the calc used. Nothing below reads the registry.
    drafted = registry.drafted_used
    if drafted:
        src[draft_list_at:draft_list_at] = [
            "== Draft code values",
            ("This calc uses the following registry entries, which the engineer of record has not yet "
             "verified against the standard:"),
            _table(["Entry", "Citation", "Source"], [[e.id, e.cite, e.source] for e in drafted],
                   "(auto, 1fr, auto)"),
        ]
    code, reg = stamp.footer_parts()
    fills = {
        "@@DRAFT@@": "true" if drafted else "false",
        "@@FOOTER_CODE@@": typst_str(code),
        "@@FOOTER_REG@@": typst_str(reg),
        "@@TITLE@@": typst_str(f"{info.name}: guard calculation"),
    }
    # Only the template is filled, never the body, which holds the engineer's text.
    for token, value in fills.items():
        src[0] = src[0].replace(token, value)
    return "\n\n".join(src) + "\n"


def render_pdf(results: Results, registry: Registry, stamp: Stamp, out_pdf: Path) -> Path:
    out_pdf = Path(out_pdf)
    source = build_source(results, registry, stamp)
    typ = out_pdf.with_suffix(".typ")
    typ.write_text(source, encoding="utf-8")
    try:
        typst.compile(str(typ), output=str(out_pdf))
    finally:
        typ.unlink(missing_ok=True)
    return out_pdf
