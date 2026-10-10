"""The direct scenarios of the second tier of golden snapshots (tests/test_golden.py).

Most second-tier scenarios are project files in tests/golden/extra/. These
twenty are not: each reaches a branch no project file can reach, by calling
one function of the engine with a stand-in. The stand-ins are a section
with a D/t no database section has, a section of a family the tool cannot
enter yet, an artificial dead load, a lowered Fu, and forces given
directly. For these the scenario below is the input, and
tests/golden/extra/direct-<name>.txt is the expected text.

Each returns the Typst source of the calc lines it prints, with any flags
(and, for flexure, the registry entries it read) on the lines after, or the
error class and message when the engine refuses.

Machinery scenarios only. Nothing here is a test case value, and no output
is ever copied into tests/cases/ (CLAUDE.md rule 5).
"""

import dataclasses
from collections.abc import Callable

from handrail import dimensions, engine, flexure, members, post, project, report, shapes, welds
from handrail.calc import Sheet, Sym
from handrail.errors import InputError
from handrail.registry import Registry
from handrail.units import Q_
from handrail.validate import validate

# The project the direct scenarios start from: Pipe2STD rail and post over
# 6'-0", h = 42 in, t_p = 1/2 in, no intermediate rail.
BASE = {
    "project": {"name": "char"},
    "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
    "top_rail": {"section": "Pipe2STD"}, "post": {"section": "Pipe2STD"},
    "welds": {"rail_to_post": "1/8", "post_to_baseplate": "1/4"},
    "baseplate": {"B": 6, "N": 8}, "intermediate_rail": {"none": True},
}
RECTANGULAR = "rectangular HSS"  # a stand-in family: no project can enter one yet


def _project(**tables) -> project.Project:
    """The project, with the grades its file leaves out filled in by shape,
    as the engine does before any check reads one."""
    return members.resolve(project.from_dict({**BASE, **tables}), Registry()).project


def _fake(base: str = "Pipe2STD", **changes) -> shapes.Section:
    return dataclasses.replace(shapes.section(base), **changes)


def _stopped(fn: Callable[[], object]) -> str:
    """The error class and message the engine stops with."""
    try:
        fn()
    except InputError as e:
        return f"{type(e).__name__}: {e}"
    raise AssertionError("the scenario was expected to stop and did not")


def _flexure(D_t: float) -> str:
    """Section F8 capacity of a pipe given this D/t: its lines, flags, and the entries read."""
    reg = Registry()
    cap = flexure.flexural_capacity(reg, _fake(D_t=D_t, label="FakePipe"), "A53 Gr B")
    return report._lines(cap.lines) + "\nFLAGS " + repr(cap.flags) + "\nUSED " + repr([e.id for e in reg.used])


def _compression(D_t: float) -> str:
    """Chapter E capacity of a post given this D/t: its lines and flags."""
    c = post.compression_capacity(Registry(), _project(), _fake(D_t=D_t, label="FakePipe"))
    return report._lines(c.head + c.body) + "\nFLAGS " + repr(c.flags)


def _h1_1a() -> str:
    """Eq. H1-1a, which no realistic guard post reaches: a Pipe8STD post with
    an artificial 40 kip dead load, in two horizontal direction cases."""
    reg = Registry()
    proj = _project(post={"section": "Pipe8STD"})
    p8 = shapes.section("Pipe8STD")
    loading = dataclasses.replace(engine.compute(proj, reg).loading, P_D=Q_(40000, "lbf"))
    cap = post._capacity(reg, proj, p8)
    out = []
    for direction in ("Outward", "Longitudinal"):
        c = post._moment_case(reg, proj, p8, loading, cap, direction, "Concentrated")
        out.append(report._lines(c.lines) + f"\n{c.equation} {c.label} {c.combination!r}")
    return "\n".join(out)


def _directional_increase_on_a_rectangular_post() -> None:
    reg = Registry()
    rect = _fake("Pipe1-1/2STD", family=RECTANGULAR, label="FakeTube")
    welds.directional_increase(Sheet(reg), reg, Sym("f_r", Q_(100, "lbf/inch")), rect)


def _ring_forces(sense: str, P: float, V: float | None, M: float | None) -> str:
    """Forces per inch on a 1/8 in weld ring around Pipe1-1/2STD, in lb and lb-in."""
    reg = Registry()
    rg = welds.ring(reg, shapes.section("Pipe1-1/2STD"), dimensions.parse("1/8"))
    sh = Sheet(reg)
    f = welds.ring_forces(sh, rg, Sym("P", Q_(P, "lbf")), sense,
                          None if V is None else Sym("V", Q_(V, "lbf")),
                          None if M is None else Sym("M", Q_(M, "lbf*inch")))
    return report._lines(rg.lines + sh.lines) + f"\n{f.fiber}"


def _size_limits(t1: float, t2: float, weld: str) -> str:
    """Table J2.4's minimum size for two parts of these thicknesses (inches)."""
    reg = Registry()
    rg = welds.ring(reg, shapes.section("Pipe1-1/2STD"), dimensions.parse(weld))
    parts = (welds.Part("t_1", "t_1", Q_(t1, "inch"), "Part 1", "Input"),
             welds.Part("t_2", "t_2", Q_(t2, "inch"), "Part 2", "Input"))
    limits = welds.size_limits(reg, rg.w, parts)
    return report._lines(limits.lines) + "\n" + limits.failure


def _validate_with_a_rectangular(label: str) -> None:
    """validate() on a three-section guard with the section of this label
    given the stand-in family: a stop cell of a joint's table."""
    real = shapes.section

    def stand_in(designation: str) -> shapes.Section:
        sec = real(designation)
        return dataclasses.replace(sec, family=RECTANGULAR) if sec.label == label else sec

    shapes.section = stand_in
    try:
        validate(_project(post={"section": "Pipe1-1/2STD"},
                          intermediate_rail={"same_as_top_rail": False, "section": "Pipe1-1/4STD"},
                          welds={**BASE["welds"], "intermediate_rail_to_post": "1/8"}), Registry())
    finally:
        shapes.section = real


def _validate_with_a_low_fu() -> None:
    """The post grade's Fu/Fy guard (W5), with a stand-in Fu: 40/35 is below 1.20."""
    reg = Registry()
    fu = reg.entries["material.A53_GrB.Fu"]
    reg.entries[fu.id] = dataclasses.replace(fu, value=40)
    validate(_project(), reg)


DIRECT: dict[str, Callable[[], str]] = {
    # Section F8: compact, exactly at lambda_p, noncompact (Eq. F8-2), and the two stops.
    "direct-flex-compact": lambda: _flexure(20),
    "direct-flex-at-lp": lambda: _flexure(58.0),
    "direct-flex-noncompact": lambda: _flexure(100),
    "direct-flex-slender": lambda: _stopped(lambda: _flexure(300)),
    "direct-flex-beyond": lambda: _stopped(lambda: _flexure(400)),
    # Chapter E classification: nonslender, and the slender stop.
    "direct-comp-ok": lambda: _compression(50),
    "direct-comp-slender": lambda: _stopped(lambda: _compression(100)),
    "direct-h1a": _h1_1a,
    "direct-dir-increase-stop": lambda: _stopped(_directional_increase_on_a_rectangular_post),
    # The weld ring: compression with moment and shear; tension with moment; axial only; no axial force.
    "direct-ring-comp": lambda: _ring_forces("compression", 30, 350, 14525),
    "direct-ring-tension": lambda: _ring_forces("tension", 30, None, 1000),
    "direct-ring-axial": lambda: _ring_forces("compression", 250, None, None),
    "direct-ring-equal": lambda: _ring_forces("compression", 0, 10, 100),
    # Table J2.4: met exactly, below the minimum, and the thickest row.
    "direct-size-ok": lambda: _size_limits(0.135, 0.5, "1/8"),
    "direct-size-ng": lambda: _size_limits(0.3, 0.5, "1/8"),
    "direct-size-thick": lambda: _size_limits(0.8, 1.0, "1/4"),
    # A stop cell of the per-joint tables, for each member in turn; the Fu/Fy guard.
    "direct-w7-rail": lambda: _stopped(lambda: _validate_with_a_rectangular("Pipe2STD")),
    "direct-w7-post": lambda: _stopped(lambda: _validate_with_a_rectangular("Pipe1-1/2STD")),
    "direct-w7-inter": lambda: _stopped(lambda: _validate_with_a_rectangular("Pipe1-1/4STD")),
    "direct-fu-fy": lambda: _stopped(_validate_with_a_low_fu),
}
