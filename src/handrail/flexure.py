"""Flexural capacity of a round hollow section (AISC 360-22 §F8), computed
once per member and shared by every case that uses it: Check 1 (the top
rail), Check 4a (the intermediate rail) and Check 5 (the post).
"""

from __future__ import annotations

from dataclasses import dataclass

from handrail.calc import Line, Sheet, Sym, chain, compare, fmt_sig, minimum, mtext
from handrail.errors import SectionStop
from handrail.materials import yield_stress
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
