"""Flexural capacity, shared by every case that uses it: Check 1 (the top
rail), Check 4a (the intermediate rail) and Check 5 (the post).

A round hollow section follows AISC 360-22 §F8: one capacity, computed once
per member (``flexural_capacity``).

A rectangular or square hollow section follows §F7 about the axis being
bent (S6-4): the lowest of yielding, flange local buckling, web local
buckling and lateral-torsional buckling. Each axis has its own flange, its
own web and its own strength, and the lateral-torsional strength takes Cb
from the load case's own moment diagram, so it is computed for the case
(``rect_limits`` once per case, then ``rect_axis_capacity`` per axis bent).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from handrail.calc import Line, Sheet, Sym, chain, compare, fmt_quantity_plain, fmt_sig, minimum, mtext, sqrt
from handrail.errors import SectionStop
from handrail.materials import yield_stress
from handrail.orientation import X, Y
from handrail.registry import Registry
from handrail.shapes import PIPE, ROUND_TUBE, Section
from handrail.stops import Stop


@dataclass
class Capacity:
    """Allowable flexural strength, computed once and shared by every case."""

    allow: Sym          # M_n/Omega_b, as a symbol the demand lines divide by
    lines: list[Line]   # printed at the head of the controlling case
    flags: list[str]


# The grade of pipe: a custom round tube in it is pipe too (S5-14).
PIPE_GRADE = "A53 Gr B"


def designed_as_round_hss(sec: Section, grade: str) -> bool:
    """Whether the section is pipe designed under the round HSS provisions,
    which the calc says on a line of its own: an AISC pipe, or a custom
    round tube in the pipe grade. A round HSS, or a custom tube in an HSS
    grade, is round HSS and prints no such line (S5-14)."""
    return sec.family == PIPE or (sec.family == ROUND_TUBE and grade == PIPE_GRADE)


def flexural_capacity(registry: Registry, rail: Section, grade: str) -> Capacity:
    """Classify the section and compute M_n/Omega_b. Raises SectionStop.

    Every coefficient and citation in the printed lines and the stop
    messages is read from its registry entry (CLAUDE.md rule 1).
    """
    sh = Sheet(registry)
    app = registry.get("aisc360.F8.applicability")
    lp_e = registry.get("aisc360.B4.1b.round_hss.lambda_p")
    lr_e = registry.get("aisc360.B4.1b.round_hss.lambda_r")

    if designed_as_round_hss(rail, grade):
        sh.decision(
            mtext(f"{rail.label}, {grade}"), "Designed as round HSS",
            "Pipe is designed under the round HSS provisions",
            cite_ids=("aisc360.pipe_as_round_hss",),
        )
    Fy = yield_stress(registry, grade, rail).line(sh, "F_y", "F_y")
    E = sh.code_value("E", "E", "material.steel.E", "Modulus of elasticity")
    lam = sh.given("lambda", "lambda", rail.D_t, f"lambda = D/t, {rail.how} (design wall)", rail.source)
    lim = sh.line("lambda_lim", "lambda_\"lim\"", sh.coeff(app.id) * E / Fy, "Applicability limit on D/t")
    lp = sh.line("lambda_p", "lambda_p", sh.coeff(lp_e.id) * E / Fy, "Compact limit, round HSS in flexure")
    lr = sh.line("lambda_r", "lambda_r", sh.coeff(lr_e.id) * E / Fy, "Noncompact limit, round HSS in flexure")

    # Each comparison is evaluated once; its stop, its branch and its printed
    # decision line all come from that evaluation (ADR 0002).
    D_t, name = rail.ratio_text(rail.D_t), rail.label
    lam_t = lam.stated(rail.ratio_text)
    applies = compare(lam_t, "<", lim.stated(fmt_sig))
    if not applies:
        raise SectionStop(
            f"{name}: D/t = {D_t} is not less than the {app.cite} limit "
            f"{app.value}E/Fy = {fmt_sig(lim.value)}. The tool does not check this section.",
            stop=Stop.SECTION_BEYOND_F8_LIMIT
        )
    slender = compare(lam_t, ">", lr.stated(fmt_sig))
    if slender:
        raise SectionStop(
            f"{name}: wall is slender in flexure, D/t = {D_t} {slender.op} lambda_r = {lr_e.value}E/Fy = "
            f"{fmt_sig(lr.value)} ({lr_e.cite}). The tool does not check slender sections.",
            stop=Stop.SECTION_SLENDER_IN_FLEXURE
        )
    sh.decision(applies, "Applies", "Applicability", cite_ids=(app.id,))
    sh.decision(
        mtext("Round HSS"), "Lateral-torsional buckling does not apply",
        "Limit states: yielding and local buckling only; Lb and Cb do not enter",
        cite_ids=("aisc360.F8.no_ltb",),
    )

    Z = sh.given("Z", "Z", rail.Z, "Plastic section modulus", rail.source)
    Mp = sh.line("M_p", "M_p", Fy * Z, "Plastic moment (yielding)", cite_ids=("aisc360.eq.F8-1",),
                 unit="lbf*inch")
    flags = []
    compact = compare(lam_t, "<=", lp.stated(fmt_sig))
    if compact:
        sh.decision(compact, "Compact", "Section classification", cite_ids=("aisc360.B4.1b.classification",))
        sh.decision(mtext("Compact wall"), "Local buckling does not apply",
                    "", cite_ids=("aisc360.F8.nominal_strength",))
        Mn = sh.line("M_n", "M_n", Mp, "Nominal flexural strength", cite_ids=("aisc360.F8.nominal_strength",),
                     unit="lbf*inch")
    else:
        # Fetched only here: Registry.get records every lookup for the DRAFT list,
        # and a compact calc must not list an equation it never used.
        f82 = registry.get("aisc360.eq.F8-2")
        # Not compact, and not slender: lambda_p < lambda <= lambda_r.
        sh.decision(chain(compact.flipped(), slender), "NONCOMPACT", "Section classification: reduced capacity",
                    cite_ids=("aisc360.B4.1b.classification",))
        flags.append(
            f"NONCOMPACT: {name} D/t = {D_t} exceeds lambda_p = {fmt_sig(lp.value)} "
            f"(lambda_r = {fmt_sig(lr.value)}); Mn reduced by local buckling, {f82.cite}."
        )
        S = sh.given("S", "S", rail.S, "Elastic section modulus", rail.source)
        Mlb = sh.line("M_n_LB", "M_(n,\"LB\")", (sh.coeff("aisc360.eq.F8-2.coeff") * E / lam + Fy) * S,
                      "Local buckling, noncompact wall", cite_ids=(f82.id,), unit="lbf*inch")
        Mn = sh.line("M_n", "M_n", minimum(Mp, Mlb), "Lower of yielding and local buckling",
                     cite_ids=("aisc360.F8.nominal_strength",), unit="lbf*inch")
    Om = sh.code_value("Omega_b", "Omega_b", "aisc360.F1.omega_b", "Safety factor for flexure (ASD)")
    Ma = sh.line("M_n_over_Omega_b", "frac(M_n, Omega_b)", Mn / Om, "Allowable flexural strength",
                 cite_ids=("aisc360.eq.B3-2",), unit="lbf*inch")
    return Capacity(allow=Ma, lines=sh.lines, flags=flags)


# ---------------------------------------------------------------------------
# Rectangular and square hollow sections: AISC 360-22 F7, about the axis bent
# ---------------------------------------------------------------------------

F7 = "aisc360.F7.nominal_strength"
CLASSIFICATION = "aisc360.B4.1b.classification"
UNBRACED_LENGTH = "ej.flexure.unbraced_length"


@dataclass
class RectLimits:
    """What both axes of a rectangular section share in one case: Fy, E, the
    Table B4.1b limits for a flange and for a web, and the safety factor."""

    Fy: Sym
    E: Sym
    flange_p: Sym
    flange_r: Sym
    web_p: Sym
    web_r: Sym
    Omega: Sym


@dataclass
class Unbraced:
    """The laterally unbraced length of a member, and how its Cb is found.
    ``Cb`` prints the Cb lines; it is called only where lateral-torsional
    buckling reduces the strength, so a case below Lp prints no Cb."""

    Lb: Sym
    note: str
    Cb: Callable[[Sheet], Sym]


def rect_limits(sh: Sheet, sec: Section, grade: str) -> RectLimits:
    """Fy, E, the wall slenderness limits and Omega_b, printed once per case
    ahead of the axis or axes it bends."""
    registry = sh.registry
    Fy = yield_stress(registry, grade, sec).line(sh, "F_y", "F_y")
    E = sh.code_value("E", "E", "material.steel.E", "Modulus of elasticity")
    b = "aisc360.B4.1b.rect_hss."
    root = sqrt(E / Fy)
    flange_p = sh.line("lambda_pf", 'lambda_"pf"', sh.coeff(b + "flange.lambda_p") * root,
                       "Compact limit, flange of rectangular HSS in flexure")
    flange_r = sh.line("lambda_rf", 'lambda_"rf"', sh.coeff(b + "flange.lambda_r") * root,
                       "Noncompact limit, flange of rectangular HSS in flexure")
    web_p = sh.line("lambda_pw", 'lambda_"pw"', sh.coeff(b + "web.lambda_p") * root,
                    "Compact limit, web of rectangular HSS in flexure")
    web_r = sh.line("lambda_rw", 'lambda_"rw"', sh.coeff(b + "web.lambda_r") * root,
                    "Noncompact limit, web of rectangular HSS in flexure")
    Omega = sh.code_value("Omega_b", "Omega_b", "aisc360.F1.omega_b", "Safety factor for flexure (ASD)")
    return RectLimits(Fy, E, flange_p, flange_r, web_p, web_r, Omega)


def _walls(sec: Section, axis: str):
    """The flange and the web for bending about this axis: each wall's
    width-to-thickness ratio, which ratio of the section it is, and the
    outside dimension of the wall. About x the short walls are the flanges
    and the long walls the webs; about y the reverse."""
    r = sec.rect
    short = (r.b_t, "b/t", r.B)
    long = (r.h_t, "h/t", r.H)
    if axis == X:
        return short, long
    if axis == Y:
        return long, short
    raise ValueError(f"no principal axis {axis!r}; expected one of {X}, {Y}")


def _wall(sh: Sheet, sec: Section, axis: str, part: str, ratio, name: str, wall, lp: Sym, lr: Sym,
          equation: str, Mp: Sym, Fy: Sym, flags: list[str]) -> Sym | None:
    """Classify one wall (the flange or the web) for bending about this axis
    and return its local buckling strength, or None when it is compact and
    the limit state does not apply. A slender wall stops."""
    registry = sh.registry
    letter = part[0]
    lam = sh.given(f"lambda_{letter}_{axis}", f"lambda_{letter}", ratio,
                   f"{part.capitalize()} slenderness about the {axis} axis: {name} of the "
                   f"{fmt_quantity_plain(wall)} walls, {sec.how} (design wall)", sec.source)
    # Each comparison is evaluated once; its stop, its branch and its printed
    # decision line all come from that evaluation (ADR 0002).
    lam_t = lam.stated(sec.ratio_text)
    lr_e = registry.get(f"aisc360.B4.1b.rect_hss.{part}.lambda_r")
    slender = compare(lam_t, ">", lr.stated(fmt_sig))
    if slender:
        raise SectionStop(
            f"{sec.label}: the {part} is slender in flexure about the {axis} axis, {name} = "
            f"{sec.ratio_text(ratio)} {slender.op} lambda_r = {lr_e.value} sqrt(E/Fy) = {fmt_sig(lr.value)} "
            f"({lr_e.cite}). The tool does not check slender sections.",
            stop=Stop.SECTION_SLENDER_IN_FLEXURE
        )
    compact = compare(lam_t, "<=", lp.stated(fmt_sig))
    if compact:
        sh.decision(compact, f"Compact {part}: {part} local buckling does not apply",
                    f"{part.capitalize()} classification, bending about the {axis} axis",
                    cite_ids=(CLASSIFICATION, "aisc360.F7.compact_no_local_buckling"))
        return None
    # Fetched only here: Registry.get records every lookup for the DRAFT list,
    # and a compact wall must not list an equation it never used.
    eq = registry.get(equation)
    sh.decision(chain(compact.flipped(), slender), f"NONCOMPACT {part.upper()}",
                f"{part.capitalize()} classification, bending about the {axis} axis: reduced capacity",
                cite_ids=(CLASSIFICATION,))
    flags.append(
        f"NONCOMPACT: {sec.label} {part}, {name} = {sec.ratio_text(ratio)}, exceeds lambda_p = {fmt_sig(lp.value)} "
        f"(lambda_r = {fmt_sig(lr.value)}) in bending about the {axis} axis; Mn reduced by {part} local buckling, "
        f"{eq.cite}."
    )
    S = sh.given(f"S_{axis}", f"S_{axis}", (sec.x if axis == X else sec.y).S,
                 f"Elastic section modulus about the {axis} axis", sec.source)
    return sh.line(f"M_n_{letter.upper()}LB_{axis}", f'M_("n,{letter.upper()}LB")',
                   Mp - (Mp - Fy * S) * ((lam - lp) / (lr - lp)),
                   f"{part.capitalize()} local buckling, noncompact {part}", cite_ids=(eq.id,), unit="lbf*inch")


def _lateral_torsional(sh: Sheet, lim: RectLimits, sec: Section, axis: str, Mp: Sym, unbraced: Unbraced) -> Sym | None:
    """The lateral-torsional buckling strength for bending about this axis,
    or None where the limit state does not apply: a square section, bending
    about the minor axis, or an unbraced length within Lp."""
    registry = sh.registry
    if axis == Y or sec.rect.square:
        why = "Square section" if sec.rect.square else "Bending about the minor axis"
        sh.decision(mtext(why), "Lateral-torsional buckling does not apply", "",
                    cite_ids=("aisc360.F7.4.no_ltb_note",))
        return None
    Lb = sh.line("L_b", "L_b", unbraced.Lb, unbraced.note, cite_ids=(UNBRACED_LENGTH,), unit="inch")
    ry = sh.given("r_y", "r_y", sec.y.r, "Radius of gyration about the y axis", sec.source)
    J = sh.given("J", "J", sec.rect.J, "Torsional constant", sec.source)
    Ag = sh.given("A_g", "A_g", sec.A, "Gross area", sec.source)
    root = sqrt(J * Ag)
    Lp = sh.line("L_p", "L_p", sh.coeff("aisc360.eq.F7-10.coeff") * lim.E * ry * root / Mp,
                 "Limiting unbraced length for yielding", cite_ids=("aisc360.eq.F7-10",), unit="inch")
    Lb_t = Lb.stated(fmt_quantity_plain)
    within = compare(Lb_t, "<=", Lp.stated(fmt_quantity_plain))
    if within:
        sh.decision(within, "Lateral-torsional buckling does not apply", "",
                    cite_ids=("aisc360.F7.4a.no_ltb_below_Lp",))
        return None
    Sx = sh.given("S_x", "S_x", sec.x.S, "Elastic section modulus about the x axis", sec.source)
    c07 = "aisc360.F7.4.inelastic_coeff"
    Lr = sh.line("L_r", "L_r", sh.coeff("aisc360.eq.F7-11.coeff") * lim.E * ry * root / (sh.coeff(c07) * lim.Fy * Sx),
                 "Limiting unbraced length for inelastic lateral-torsional buckling",
                 cite_ids=("aisc360.eq.F7-11",), unit="inch")
    inelastic = compare(Lb_t, "<=", Lr.stated(fmt_quantity_plain))
    # Each equation entry is fetched only on its own branch, as for Chapter E.
    if inelastic:
        eq = registry.get("aisc360.eq.F7-8")
        sh.decision(chain(within.flipped(), inelastic), f"Inelastic lateral-torsional buckling: {eq.equation_number}", "",
                    cite_ids=(eq.id,))
        Cb = unbraced.Cb(sh)
        return sh.line("M_n_LTB", 'M_("n,LTB")',
                       Cb * (Mp - (Mp - sh.coeff(c07) * lim.Fy * Sx) * ((Lb - Lp) / (Lr - Lp))),
                       "Lateral-torsional buckling", cite_ids=(eq.id,), unit="lbf*inch")
    eq = registry.get("aisc360.eq.F7-9")
    sh.decision(inelastic, f"Elastic lateral-torsional buckling: {eq.equation_number}", "", cite_ids=(eq.id,))
    Cb = unbraced.Cb(sh)
    return sh.line("M_n_LTB", 'M_("n,LTB")',
                   sh.coeff("aisc360.eq.F7-9.coeff") * lim.E * Cb * root / (Lb / ry),
                   "Lateral-torsional buckling", cite_ids=(eq.id,), unit="lbf*inch")


def rect_axis_capacity(sh: Sheet, lim: RectLimits, sec: Section, axis: str, unbraced: Unbraced,
                       flags: list[str]) -> Sym:
    """M_n/Omega_b of a rectangular section about one axis, by AISC 360-22
    F7: the lowest of yielding, flange local buckling, web local buckling
    and lateral-torsional buckling. Its lines go on ``sh``; a noncompact
    wall adds its flag to ``flags``. Raises SectionStop on a slender wall.

    Every coefficient and citation in the printed lines and the stop
    messages is read from its registry entry (CLAUDE.md rule 1).
    """
    (f_ratio, f_name, f_wall), (w_ratio, w_name, w_wall) = _walls(sec, axis)
    props = sec.x if axis == X else sec.y
    Z = sh.given(f"Z_{axis}", f"Z_{axis}", props.Z, f"Plastic section modulus about the {axis} axis", sec.source)
    Mp = sh.line(f"M_p_{axis}", f'M_"p{axis}"', lim.Fy * Z, "Plastic moment (yielding)",
                 cite_ids=("aisc360.eq.F7-1",), unit="lbf*inch")
    states = [(Mp, "yielding")]
    flb = _wall(sh, sec, axis, "flange", f_ratio, f_name, f_wall, lim.flange_p, lim.flange_r,
                "aisc360.eq.F7-2", Mp, lim.Fy, flags)
    if flb is not None:
        states.append((flb, "flange local buckling"))
    wlb = _wall(sh, sec, axis, "web", w_ratio, w_name, w_wall, lim.web_p, lim.web_r,
                "aisc360.eq.F7-6", Mp, lim.Fy, flags)
    if wlb is not None:
        states.append((wlb, "web local buckling"))
    ltb = _lateral_torsional(sh, lim, sec, axis, Mp, unbraced)
    if ltb is not None:
        states.append((ltb, "lateral-torsional buckling"))
    if len(states) == 1:
        Mn = sh.line(f"M_n_{axis}", f'M_"n{axis}"', Mp, f"Nominal flexural strength about the {axis} axis: yielding",
                     cite_ids=(F7,), unit="lbf*inch")
    else:
        names = ", ".join(name for _, name in states[:-1]) + f" and {states[-1][1]}"
        Mn = sh.line(f"M_n_{axis}", f'M_"n{axis}"', minimum(*(m for m, _ in states)),
                     f"Nominal flexural strength about the {axis} axis: the lowest of {names}",
                     cite_ids=(F7,), unit="lbf*inch")
    return sh.line(f"M_c_{axis}", f'M_"c{axis}"', Mn / lim.Omega, f"Allowable flexural strength about the {axis} axis",
                   cite_ids=("aisc360.eq.B3-2",), unit="lbf*inch")
