"""Hand-calc test cases (docs/brief/verification.md).

Each tests/cases/case-NN.toml holds a project's inputs and the engineer's
hand-calculated values. Every hand value must be within 0.5% (relative) of
the tool's value. A "pending" value is skipped, and the skip message never
shows the tool's value, so the hand calc stays independent.

A case records whole groups of values ([hand.section], [hand.check1],
[hand.post], [hand.check5], ...). Every value in a group the case records
must have a hand key; a group the case leaves out is not checked (test
case 1 records no post values, and cases 2 and 3 no rail values).

Text values (which equation governed, the controlling direction) are
compared as text; every other value must be a number.

A failure here is a CLAUDE.md rule 2 stop: do not change the tool (or the
hand value) until we know which one is wrong.
"""

import tomllib
from pathlib import Path

import pytest

from handrail import checks, project
from handrail.checks import CONCENTRATED
from handrail.registry import Registry

CASES = sorted((Path(__file__).parent / "cases").glob("case-*.toml"))
TOLERANCE = 0.005
PENDING = "pending"


def _load(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def _run(path):
    raw = _load(path)
    return raw["hand"], checks.run(project.from_dict(raw), Registry())


def _case_key(c) -> str:
    return f"{c.direction.lower()}_{c.load_type.lower()}"


def _line_value(lines, symbol):
    return next(ln.value for ln in lines if ln.symbol == symbol and ln.kind == "value")


def _check(res, number):
    return next(c for c in res.checks if c.number == number)


def _case(chk, direction, load_type=CONCENTRATED):
    return next(c for c in chk.checked if c.direction == direction and c.load_type == load_type)


def _equation(text: str) -> str:
    """The equation a case used, as a hand calc names it: 'Eq. H1-1b' -> 'H1-1b',
    'Pr/Pc (Ch. E)' -> 'Pr/Pc'."""
    return text.removeprefix("Eq. ").split(" (")[0]


def _post_values(res):
    p, ld = res.post, res.loading
    c5, c6 = _check(res, 5), _check(res, 6)
    # Capacities, read from the printed lines of the case that prints them.
    down, out = _case(c5, "Downward").lines, _case(c5, "Outward").lines
    branch = next(ln.text for ln in down if ln.kind == "decision" and "buckling: Eq." in (ln.text or ""))
    v = {
        "post.D_in": p.OD.m_as("inch"),
        "post.tdes_in": p.tdes.m_as("inch"),
        "post.A_in2": p.A.m_as("in^2"),
        "post.W_plf": p.W.m_as("lbf/ft"),
        "post.I_in4": p.I.m_as("in^4"),
        "post.S_in3": p.S.m_as("in^3"),
        "post.Z_in3": p.Z.m_as("in^3"),
        "post.r_in": p.r.m_as("inch"),
        "post.D_t": p.D_t,
        "post.D_post_lb": _line_value(ld.lines, 'D_"post"').m_as("lbf"),
        "post.P_D_lb": ld.P_D.m_as("lbf"),
        "check5.Lc_in": _line_value(down, "L_c").m_as("inch"),
        "check5.Lc_over_r": _line_value(down, "frac(L_c, r)"),
        "check5.Fe_ksi": _line_value(down, "F_e").m_as("ksi"),
        "check5.Fcr_ksi": _line_value(down, 'F_"cr"').m_as("ksi"),
        "check5.Fcr_equation": branch.split("Eq. ")[1],
        "check5.Pn_lb": _line_value(down, "P_n").m_as("lbf"),
        "check5.Pc_lb": _line_value(down, "P_c").m_as("lbf"),
        "check5.Pt_lb": _case(c5, "Upward").P_allow.m_as("lbf"),
        "check5.Mn_lbin": _line_value(out, "M_n").m_as("lbf*inch"),
        "check5.Mc_lbin": _line_value(out, "M_c").m_as("lbf*inch"),
    }
    for c in c5.checked:
        k = _case_key(c)
        v[f"check5.Pr_lb.{k}"] = c.Pr.m_as("lbf")
        v[f"check5.equation.{k}"] = _equation(c.equation)
        v[f"check5.ratio.{k}"] = c.ratio
        if c.Mr is not None:
            v[f"check5.Mr_lbin.{k}"] = c.Mr.m_as("lbf*inch")
            v[f"check5.alpha_Pr_over_Pe.{k}"] = c.second_order
    if not c6.bypassed:
        v["check6.Delta_allow_in"] = c6.controlling.capacity.m_as("inch")
        for c in c6.checked:
            v[f"check6.deflection_in.{_case_key(c)}"] = c.demand.m_as("inch")
            v[f"check6.ratio.{_case_key(c)}"] = c.ratio
    return v


def tool_values(res):
    """Tool values keyed like the [hand] tables, in the same units."""
    r = res.rail
    c1, c2 = _check(res, 1), _check(res, 2)
    v = {
        "section.D_in": r.OD.m_as("inch"),
        "section.tdes_in": r.tdes.m_as("inch"),
        "section.I_in4": r.I.m_as("in^4"),
        "section.S_in3": r.S.m_as("in^3"),
        "section.Z_in3": r.Z.m_as("in^3"),
        "section.D_t": r.D_t,
        "section.w_D_plf": res.loading.w_D.m_as("lbf/ft"),
        # Read from the controlling case's printed lines: compare what the PDF shows.
        "check1.Mn_lbin": _line_value(c1.controlling.lines, "M_n").m_as("lbf*inch"),
        "check1.Mn_over_Omega_lbin": _line_value(c1.controlling.lines, "frac(M_n, Omega_b)").m_as("lbf*inch"),
    }
    for c in c1.checked:
        v[f"check1.moment_lbin.{_case_key(c)}"] = c.demand.m_as("lbf*inch")
        v[f"check1.ratio.{_case_key(c)}"] = c.ratio
    if not c2.bypassed:
        v["check2.Delta_allow_in"] = c2.controlling.capacity.m_as("inch")
        for c in c2.checked:
            v[f"check2.deflection_in.{_case_key(c)}"] = c.demand.m_as("inch")
            v[f"check2.ratio.{_case_key(c)}"] = c.ratio
    v.update(_post_values(res))
    return v


CONTROLLING = {f"check{n}.controlling": n for n in (1, 2, 5, 6)}
TEXT_KEYS = ("controlling", "equation", "Fcr_equation")


def _is_text(key: str) -> bool:
    return any(part in TEXT_KEYS for part in key.split("."))


def _flatten(d, prefix=""):
    for k, val in d.items():
        key = f"{prefix}{k}"
        if isinstance(val, dict):
            yield from _flatten(val, key + ".")
        else:
            yield key, val


def _params():
    for path in CASES:
        for key, _ in _flatten(_load(path)["hand"]):
            yield pytest.param(path, key, id=f"{path.stem}:{key}")


@pytest.fixture(scope="module")
def runs():
    cache = {}

    def get(path):
        if path not in cache:
            cache[path] = _run(path)
        return cache[path]

    return get


@pytest.mark.parametrize("path, key", list(_params()))
def test_hand_value(runs, path, key):
    hand_raw, res = runs(path)
    hand = dict(_flatten(hand_raw))[key]
    if hand == PENDING:
        pytest.skip("hand value pending")
    compare(path, key, hand, res)


def compare(path, key, hand, res):
    """Assert one hand value against the tool (raises AssertionError on a rule 2 stop)."""
    if key in CONTROLLING:
        chk = _check(res, CONTROLLING[key])
        ctrl = chk.controlling
        # Outward, inward (and, for the post, longitudinal) tie exactly for a round
        # section: accept any case tied with the controlling one.
        tied = {c.label.lower() for c in chk.checked if abs(c.ratio - ctrl.ratio) <= 1e-9 * ctrl.ratio}
        assert hand.strip().lower() in tied, (
            f"RULE 2 STOP. {path.name} {key}: hand = {hand!r}, tool = {sorted(tied)}"
        )
        return

    if _is_text(key):
        tool = tool_values(res)[key]
        assert isinstance(hand, str) and hand.strip().lower() == tool.lower(), (
            f"RULE 2 STOP. {path.name} {key}: hand = {hand!r}, tool = {tool!r}"
        )
        return

    if not isinstance(hand, (int, float)):
        pytest.fail(f"{path.name} {key} = {hand!r}: a hand value must be a bare number "
                    f"(no quotes; quotes make it text), or \"{PENDING}\"")
    tool = tool_values(res)[key]
    rel = abs(tool - hand) / abs(hand)
    assert rel <= TOLERANCE, (
        f"RULE 2 STOP. {path.name} {key}: hand = {hand:g}, tool = {tool:.6g}, "
        f"difference {rel:.2%} > 0.5%. Do not change the tool until we know which is wrong."
    )


def assert_hand_keys_match(path, hand_raw, res):
    """Every [hand] key names a tool value, and every tool value in a group the
    case records has a [hand] key.

    The second half matters: a deleted hand value must not silently stop
    being tested. Each such tool value needs a hand key, as a number or "pending".
    """
    groups = set(hand_raw)
    tool = {k for k in set(tool_values(res)) | set(CONTROLLING) if k.split(".")[0] in groups}
    hand = {key for key, _ in _flatten(hand_raw)}
    unknown = sorted(hand - tool)
    assert not unknown, f"{path.name}: [hand] keys that match no tool value: {unknown}"
    missing = sorted(tool - hand)
    assert not missing, f"{path.name}: tool values with no [hand] key: {missing}"


@pytest.mark.parametrize("path", CASES, ids=[p.stem for p in CASES])
def test_hand_keys_and_tool_values_match_both_ways(runs, path):
    hand_raw, res = runs(path)
    assert_hand_keys_match(path, hand_raw, res)


def test_comparison_machinery_catches_a_mismatch():
    """Self-test on the dev section (Pipe2STD, 6'-0"), not a hand case: a right
    value passes, a value 1% off fails with the rule 2 message."""
    raw = {"project": {"name": "self-test"},
           "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
           "top_rail": {"section": "Pipe2STD"}, "post": {"section": "Pipe2STD"}}
    res = checks.run(project.from_dict(raw), Registry())
    good = tool_values(res)["check1.ratio.downward_concentrated"]
    compare(Path("self-test"), "check1.ratio.downward_concentrated", good * 1.004, res)
    with pytest.raises(AssertionError, match="RULE 2 STOP"):
        compare(Path("self-test"), "check1.ratio.downward_concentrated", good * 1.01, res)
    with pytest.raises(AssertionError, match="RULE 2 STOP"):
        compare(Path("self-test"), "check2.controlling", "upward, distributed", res)


def test_a_deleted_hand_value_is_caught():
    """Self-test of the real key check, not a copy of it."""
    case = CASES[0]
    raw = _load(case)
    res = checks.run(project.from_dict(raw), Registry())
    assert_hand_keys_match(case, raw["hand"], res)  # the intact file passes
    del raw["hand"]["check1"]["ratio"]["upward_distributed"]
    with pytest.raises(AssertionError, match=r"no \[hand\] key: \['check1.ratio.upward_distributed'\]"):
        assert_hand_keys_match(case, raw["hand"], res)


def test_an_unknown_hand_key_is_caught():
    case = CASES[0]
    raw = _load(case)
    res = checks.run(project.from_dict(raw), Registry())
    raw["hand"]["check1"]["ratio"]["sideways_concentrated"] = 0.5
    with pytest.raises(AssertionError, match=r"match no tool value: \['check1.ratio.sideways_concentrated'\]"):
        assert_hand_keys_match(case, raw["hand"], res)


def _dev_post_run():
    raw = {"project": {"name": "self-test"},
           "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
           "top_rail": {"section": "Pipe2STD"}, "post": {"section": "Pipe2STD"}}
    return checks.run(project.from_dict(raw), Registry())


def test_post_comparisons_catch_a_mismatch():
    """Self-test on the dev section (Pipe2STD post), not a hand case: numbers,
    equation names and the controlling direction all stop on a mismatch."""
    res = _dev_post_run()
    tool = tool_values(res)
    ratio = tool["check5.ratio.outward_concentrated"]
    compare(Path("self-test"), "check5.ratio.outward_concentrated", ratio * 1.004, res)
    with pytest.raises(AssertionError, match="RULE 2 STOP"):
        compare(Path("self-test"), "check5.ratio.outward_concentrated", ratio * 1.01, res)
    eq = tool["check5.equation.outward_concentrated"]
    compare(Path("self-test"), "check5.equation.outward_concentrated", eq.upper(), res)
    wrong = "H1-1a" if eq == "H1-1b" else "H1-1b"
    with pytest.raises(AssertionError, match="RULE 2 STOP"):
        compare(Path("self-test"), "check5.equation.outward_concentrated", wrong, res)
    with pytest.raises(AssertionError, match="RULE 2 STOP"):
        compare(Path("self-test"), "check5.controlling", "upward, concentrated", res)


def test_a_group_a_case_records_must_be_complete():
    res = _dev_post_run()
    hand = {"check6": {"Delta_allow_in": 1.0, "controlling": "x",
                       "deflection_in": {}, "ratio": {}}}
    with pytest.raises(AssertionError, match=r"no \[hand\] key: \['check6.deflection_in.inward_concentrated'"):
        assert_hand_keys_match(Path("self-test"), hand, res)
