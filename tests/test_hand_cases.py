"""Hand-calc test cases (docs/brief/verification.md).

Each tests/cases/case-NN.toml holds a project's inputs and the engineer's
hand-calculated values. Every hand value must be within 0.5% (relative) of
the tool's value. A "pending" value is skipped, and the skip message never
shows the tool's value, so the hand calc stays independent.

A failure here is a CLAUDE.md rule 2 stop: do not change the tool (or the
hand value) until we know which one is wrong.
"""

import tomllib
from pathlib import Path

import pytest

from handrail import checks, project
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


def tool_values(res):
    """Tool values keyed like the [hand] tables, in the same units."""
    r = res.rail
    c1, c2 = res.checks
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
    return v


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
    if key.endswith("controlling"):
        chk = res.checks[0 if key.startswith("check1") else 1]
        ctrl = chk.controlling
        # Outward and inward tie exactly for a round section: accept any case tied with the controlling one.
        tied = {c.label.lower() for c in chk.checked if abs(c.ratio - ctrl.ratio) <= 1e-9 * ctrl.ratio}
        assert hand.strip().lower() in tied, (
            f"RULE 2 STOP. {path.name} {key}: hand = {hand!r}, tool = {sorted(tied)}"
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
    """Every [hand] key names a tool value, and every tool value has a [hand] key.

    The second half matters: a deleted hand value must not silently stop
    being tested. Each tool value needs a hand key, as a number or "pending".
    """
    tool = set(tool_values(res)) | {"check1.controlling", "check2.controlling"}
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
