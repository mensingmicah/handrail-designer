"""The loads every check starts from: the guard loads and the dead load
at the post (docs/brief/loads-and-envelope.md), and how a load combination
and the uniform-load exemption are printed.
"""

from __future__ import annotations

from handrail.calc import Sheet, fmt_quantity_plain
from handrail.directions import DISTRIBUTED, Direction
from handrail.project import Project
from handrail.registry import Entry, Registry
from handrail.results import Case, Loading
from handrail.shapes import Section

# ASCE 7-22 ASD D + L: the combination of every check where the guard load
# acts with or beside the dead load.
COMBO = "asce7.combo.asd.D_plus_L"


def build_loading(project: Project, registry: Registry, rail: Section, post: Section,
                  inter: Section | None = None) -> Loading:
    """The guard loads and the dead load at the post. ``inter`` is the
    intermediate rail's section (the top rail's when it is the same), or
    None when there is none."""
    sh = Sheet(registry)
    ld = project.loads

    code_P = registry.get("asce7.guard.concentrated")
    if ld.concentrated is None:
        P = sh.code_value("P", "P", code_P.id, "Concentrated guard load, any direction, any point on the top rail")
    else:
        P = sh.input(
            "P", "P", ld.concentrated,
            f"Concentrated guard load, engineer override (code value {fmt_quantity_plain(code_P.quantity)})",
            cite=f"Input; {code_P.cite}",
        )

    code_w = registry.get("asce7.guard.uniform")
    if ld.uniform_exempt:
        sh.decision(
            "w_L", "Not considered",
            f"Uniform guard load exempted by the engineer: {ld.exemption_statement}",
            cite=registry.get("asce7.guard.uniform.exemption.intro").cite,
        )
        w_L = None
    elif ld.uniform is None:
        w_L = sh.code_value("w_L", "w_L", code_w.id, f"Uniform guard load, {code_w.value} lb/ft, any direction; "
                            "not concurrent with P").value
    else:
        w_L = sh.input(
            "w_L", "w_L", ld.uniform,
            f"Uniform guard load, engineer override: {ld.uniform.m_as('lbf/ft'):g} lb/ft "
            f"(code value {code_w.quantity.m_as('lbf/ft'):g} lb/ft)",
            cite=f"Input; {code_w.cite}",
        ).value

    P_c = None
    if inter is not None:
        code_Pc = registry.get("asce7.guard.component")
        if ld.component is None:
            P_c = sh.code_value("P_c", "P_c", code_Pc.id, "Component load on the intermediate rail, horizontal; also "
                                "applied downward (engineering judgement)").value
        else:
            P_c = sh.input(
                "P_c", "P_c", ld.component,
                f"Component load on the intermediate rail, engineer override "
                f"(code value {fmt_quantity_plain(code_Pc.quantity)})",
                cite=f"Input; {code_Pc.cite}",
            ).value

    w_D = sh.given("w_D", "w_D", rail.W, f"Top rail self-weight: tabulated W = {rail.W.m_as('lbf/ft'):g} lb/ft", rail.source)

    # Dead load reaching the post (docs/plans/slice-2.md, D2). The critical
    # section is the top of the baseplate (D4), so the post weight is taken
    # over h - t_p, the same cantilever length Checks 5 and 6 use.
    sh.heading("Dead load at the post")
    dl = "ej.post.axial_dead_load"
    h = sh.given("h", "h", project.post_height.value, "Post height, top of concrete to top rail centerline", "Input")
    tp = sh.given("t_p", "t_p", project.baseplate_thickness.value, "Baseplate thickness", "Input")
    L_post = sh.line("L_post", 'L_"post"', h - tp, "Post cantilever length, top of baseplate to top rail centerline",
                     cite="Stated assumption: post fixed at the top of the baseplate", unit="inch")
    L_post_line = sh.lines[-1]
    W_post = sh.given("W_post", 'W_"post"', post.W,
                      f"Post self-weight: {post.label}, tabulated W = {post.W.m_as('lbf/ft'):g} lb/ft", post.source)
    D_post = sh.line("D_post", 'D_"post"', W_post * L_post, "Post dead load, full weight at the base",
                     cite_ids=(dl,), unit="lbf")
    s = sh.given("L", "L", project.span.value, "Span: the tributary length for the post (stated assumption)", "Input")
    D_rail = sh.line("D_rail", 'D_"rail"', w_D * s, "Top rail dead load delivered to the post", cite_ids=(dl,), unit="lbf")
    if inter is None:
        P_D = sh.line("P_D", "P_D", D_rail + D_post, "D at the post: axial dead load at the top of the baseplate",
                      cite_ids=(dl,), unit="lbf")
        w_D_int = D_int = None
    else:
        # The intermediate rail frames into the side of the post below the
        # rail to post weld, so its dead load reaches D at the post but not
        # Check 3's D (docs/plans/slice-4.md, where the dead load goes).
        same = " (same section as the top rail)" if inter is rail else ""
        w_D_int = sh.given("w_D_int", 'w_(D,"int")', inter.W, f"Intermediate rail self-weight: {inter.label}{same}, "
                           f"tabulated W = {inter.W.m_as('lbf/ft'):g} lb/ft", inter.source)
        D_int = sh.line("D_int", 'D_"int"', w_D_int * s, "Intermediate rail dead load delivered to the post",
                        cite_ids=(dl,), unit="lbf")
        P_D = sh.line("P_D", "P_D", D_rail + D_int + D_post, "D at the post: axial dead load at the top of the baseplate",
                      cite_ids=(dl,), unit="lbf")
        w_D_int, D_int = w_D_int.value, D_int.value
    return Loading(P=P.value, w_L=w_L, w_D=w_D.value, L_post=L_post.value, D_rail=D_rail.value, P_D=P_D.value,
                   exempt=ld.uniform_exempt, exemption_statement=ld.exemption_statement, lines=sh.lines,
                   derived_lengths=[L_post_line], w_D_int=w_D_int, D_int=D_int, P_c=P_c, D_post=D_post.value)


def combo_text(entry: Entry, axes: dict[str, str] | None = None, joiner: str = " + ") -> str:
    """Combination label generated from the factors the expression uses: '0.6D + 1.0L'.

    With ``axes`` ({"D": "vertical", "L": "horizontal"}), each term carries its axis.
    """
    terms = []
    for load, factor in entry.value.items():
        term = f"{float(factor)!r}{load}"
        terms.append(f"{term} {axes[load]}" if axes else term)
    return joiner.join(terms)


def exempt_case(registry: Registry, direction: Direction, case_type: type[Case] = Case) -> Case:
    """The distributed-load row when the engineer exempts the uniform load:
    listed in the envelope, not checked. Every check builds it here."""
    exemption = registry.get("asce7.guard.uniform.exemption.intro")
    return case_type(direction, DISTRIBUTED, "exempt", remark=f"Uniform load not considered ({exemption.cite})")
