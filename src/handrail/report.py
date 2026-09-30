"""Render a calc to PDF with Typst.

Python writes one Typst source file for the whole calc, then the typst
package compiles it. Calc lines are printed from their records (ADR 0002);
this module decides only layout. User-entered text enters Typst only as
string literals (typst_str), so it prints as text and never runs as markup.
"""

from __future__ import annotations

from pathlib import Path

import typst

from handrail.calc import Line, fmt_quantity_plain, fmt_ratio, typst_str
from handrail.checks import Check, Results
from handrail.registry import Registry
from handrail.version import Stamp

# The tool's own stated assumptions (docs/BRIEF.md). Locked: always printed;
# the engineer can add to them in the project file but not edit or remove them.
LOCKED_ASSUMPTIONS = (
    "No shear checks in any member.",
    "Interior post; the tributary length is the span. End posts and rail overhangs are not checked.",
    "The top rail runs continuously over the post; the post is coped and welded to its underside. "
    "The rail is designed as a simple span.",
    "The intermediate rail's connection to the post, and the component load's effect on the post, "
    "are not checked.",
    "Guard loads are not combined with floor or roof live load; wind, snow and ice are not considered.",
    "Base reactions can reverse; direction is set in the anchor software.",
    "The baseplate is rigid; the post is fixed at the top of the baseplate.",
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


def _lines(lines: list[Line]) -> str:
    out = []
    for ln in lines:
        if ln.kind == "heading":
            out.append(f"#subhead({typst_str(ln.symbol)})")
            continue
        if ln.kind == "decision":
            eq = f"[${ln.symbol}$ #h(6pt) $arrow.r$ #h(6pt) *#{typst_str(ln.text)}*]"
        elif ln.symbolic is not None:
            parts = [ln.symbol] + ([ln.symbolic] if ln.symbolic != ln.symbol else [])
            if ln.substituted not in (ln.symbolic, f"({ln.result})", ln.result):
                parts.append(ln.substituted)
            parts.append(ln.result)
            eq = f"[$display({' = '.join(parts)})$]"
        else:
            eq = f"[${ln.symbol} = {ln.result}$]"
        out.append(f"#calcline({eq}, {typst_str(ln.note)}, {typst_str(ln.cite)})")
    return "\n".join(out)


def _table(header: list[str], rows: list[list[str]], columns: str, bold_rows=(), raw_header=False) -> str:
    """A table. Cells are user-safe string literals; with raw_header, header
    cells are Typst content written by this module (for math symbols)."""
    head = [h if raw_header else f"strong({typst_str(h)})" for h in header]
    cells = [f"table.header({', '.join(head)})"] if head else []
    for i, row in enumerate(rows):
        for c in row:
            cells.append(f"strong({typst_str(c)})" if i in bold_rows else typst_str(c))
    return f"#table(columns: {columns}, {', '.join(cells)})"


def _envelope(chk: Check) -> str:
    ctrl = chk.controlling
    rows, bold = [], []
    for i, c in enumerate(chk.cases):
        if c.status == "checked":
            rows.append([
                c.direction, c.load_type, c.combination,
                fmt_quantity_plain(c.demand), fmt_quantity_plain(c.capacity), fmt_ratio(c.ratio),
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


def _check(chk: Check) -> str:
    out = [f"= Check {chk.number}: {chk.title}"]
    if chk.bypassed:
        out.append("*Bypassed by engineer.* No calculation is shown.")
        return "\n\n".join(out)
    for f in chk.flags:
        out.append(f"#flag({typst_str(f)})")
    out.append("== Envelope summary")
    out.append("Every direction case and load type is computed. The full calculation follows for the "
               "controlling case only.")
    out.append(_envelope(chk))
    ctrl = chk.controlling
    combination = ctrl.combination.replace("
", "; ")  # table cells break the label; a heading doesn't
    out.append(f"#heading(level: 2, {typst_str(f'Controlling case: {ctrl.label} ({combination})')})")
    out.append(_lines(ctrl.lines))
    # The verdict is decided once, by the Check; the page only prints it.
    cmp = "<=" if chk.ok else ">"
    out.append(f"#align(right, text(size: 12pt, weight: \"bold\")[$\"Ratio\" = {fmt_ratio(ctrl.ratio)} {cmp} 1.00$ "
               f"#h(10pt) #{typst_str(chk.verdict)}])")
    return "\n\n".join(out)


def _summary(checks: list[Check]) -> str:
    rows = []
    for chk in checks:
        if chk.bypassed:
            rows.append([f"{chk.number}. {chk.title}", "", "", "", "", "Bypassed by engineer"])
            continue
        c = chk.controlling
        rows.append([f"{chk.number}. {chk.title}", fmt_quantity_plain(c.demand), fmt_quantity_plain(c.capacity),
                     fmt_ratio(c.ratio), c.label, chk.verdict])
    return _table(["Check", "Demand", "Capacity", "Ratio", "Controlling direction", "Result"], rows,
                  "(1fr, auto, auto, auto, auto, auto)")


def build_source(results: Results, registry: Registry, stamp: Stamp) -> str:
    proj = results.project
    info = proj.info
    drafted = registry.drafted_used
    code, reg = stamp.footer_parts()
    fills = {
        "@@DRAFT@@": "true" if drafted else "false",
        "@@FOOTER_CODE@@": typst_str(code),
        "@@FOOTER_REG@@": typst_str(reg),
        "@@TITLE@@": typst_str(f"{info.name}: guard calculation"),
    }
    template = TEMPLATE
    for token, value in fills.items():
        template = template.replace(token, value)
    src = [template]

    # Front matter
    src.append("#align(center, text(size: 16pt, weight: \"bold\")[Guard Calculation])")
    src.append("#align(center)[Top rail: bending and deflection]")
    src.append("== Project")
    src.append(_table([], [["Project", info.name], ["Phase", info.phase], ["Description", info.description]],
                      "(auto, 1fr)").replace("columns: (auto, 1fr), ", "columns: (auto, 1fr), stroke: none, "))
    src.append("Loading is per ASCE 7-22.")
    src.append("== Assumptions")
    items = [f"+ #{typst_str(a)}" for a in LOCKED_ASSUMPTIONS]
    items += [f"+ #{typst_str(a)} _(added by engineer)_" for a in info.assumptions]
    src.append("\n".join(items))
    src.append("== References")
    src.append("\n".join(f"- #{typst_str(r)}" for r in REFERENCES + info.references))
    src.append("== Sketch")
    src.append('#block(width: 100%, height: 2.2in, stroke: (dash: "dashed", paint: luma(150)), '
               'align(center + horizon, text(fill: luma(120))[Image area (image upload is a later slice)]))')
    if drafted:
        src.append("== Draft code values")
        src.append("This calc uses the following registry entries, which the engineer of record has not yet "
                   "verified against the standard:")
        src.append(_table(["Entry", "Citation", "Source"],
                          [[e.id, e.cite, e.source] for e in drafted], "(auto, 1fr, auto)"))

    # Dimensions
    src.append("= Dimensions")
    src.append("Every dimension as entered, and as the tool read it. A bare number is inches.")
    d = proj.span
    src.append(_table(["Dimension", "As entered", "Read as", "Inches"],
                      [["Span, post to post (c/c)", d.entered, d.normalized, fmt_quantity_plain(d.value)]],
                      "(1fr, auto, auto, auto)"))

    # Section properties
    src.append("= Section properties")
    src.append(f"#text({typst_str(f'Top rail: {results.rail.label}, {proj.top_rail.grade}.')}) "
               "Properties are used exactly as published in the AISC Shapes Database v16.0.")
    src.append(_lines(results.section_lines))

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
