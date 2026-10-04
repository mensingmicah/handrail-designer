"""Test cases (docs/brief/verification.md, ADR 0004).

Each tests/cases/case-NN.toml holds a project's inputs, the values the tool
is compared against, and a [verification] table that declares its kind and
the groups of tool values it covers ([hand.section], [hand.check1],
[hand.post], [hand.check5], ...):

    [verification]
    kind = "full-hand"            # or "independent-calc"
    covers = ["section", "check1", "check2"]

- Full-hand case (test case 1): every tool value in the covered groups has
  a [hand] key, and every [hand] key names one.
- Independent-calc case (test case 2 on): the independent calc's values
  are in tests/cases/independent/case-NN.toml ([provenance] and
  [independent]), with every covered tool value keyed there, both ways.
  [hand] holds Micah's governing-case values, a subset: for each check the
  case covers, at least checkN.controlling and one value of that check.
  tests/independent_template.py creates the independent file with every
  key "pending" (names only).

Every hand and independent value must be within 0.5% (relative) of the
tool's value. A "pending" value is skipped, and the skip message never
shows the tool's value, so neither calc sees the tool. Text values (which
equation governed, the controlling direction) are compared as text; every
other value must be a number.

A failure here is a CLAUDE.md rule 2 stop: do not change the tool, the hand
value or the independent value until we know which one is wrong.
"""

import datetime
import tomllib
from pathlib import Path

import pytest

from handrail import checks, project
from handrail.checks import CONCENTRATED
from handrail.registry import Registry

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "tests" / "cases"
INDEPENDENT_DIR = CASES_DIR / "independent"
CASES = sorted(CASES_DIR.glob("case-*.toml"))
TOLERANCE = 0.005
PENDING = "pending"
FULL_HAND, INDEPENDENT_CALC = "full-hand", "independent-calc"
KINDS = (FULL_HAND, INDEPENDENT_CALC)
PROVENANCE = ("calc", "written_on", "model", "commit")
SOURCE_NAMES = {"hand": "hand calc", "independent": "independent calc"}


def _load(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def run_case(path):
    raw = _load(path)
    return raw, checks.run(project.from_dict(raw), Registry())


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
CHECK_GROUPS = {key.split(".")[0] for key in CONTROLLING}
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


def kind(raw):
    return raw.get("verification", {}).get("kind")


def independent_path(case: Path) -> Path:
    return INDEPENDENT_DIR / case.name


def expected_keys(raw, res) -> list[str]:
    """Every tool value in the groups the case covers, in the tool's order."""
    covers = raw["verification"]["covers"]
    return [k for k in [*tool_values(res), *CONTROLLING] if k.split(".")[0] in covers]


def _sources(path):
    """(source, values) for each set of recorded values the case has."""
    raw = _load(path)
    yield "hand", raw.get("hand", {})
    ind = independent_path(path)
    if kind(raw) == INDEPENDENT_CALC and ind.is_file():
        yield "independent", _load(ind).get("independent", {})


def _params():
    for path in CASES:
        for source, values in _sources(path):
            for key, _ in _flatten(values):
                yield pytest.param(path, source, key, id=f"{path.stem}:{source}:{key}")


@pytest.fixture(scope="module")
def runs():
    cache = {}

    def get(path):
        if path not in cache:
            cache[path] = run_case(path)
        return cache[path]

    return get


@pytest.mark.parametrize("path, source, key", list(_params()))
def test_recorded_value(runs, path, source, key):
    _, res = runs(path)
    value = dict(_flatten(dict(_sources(path))[source]))[key]
    if value == PENDING:
        pytest.skip(f"{source} value pending")
    compare(path, key, value, res, source)


def compare(path, key, value, res, source="hand"):
    """Assert one recorded value against the tool (raises AssertionError on a
    rule 2 stop). source is "hand" or "independent", and the message names it."""
    stop = f"RULE 2 STOP. {path.name} {key}: the {SOURCE_NAMES[source]} disagrees with the tool."
    if key in CONTROLLING:
        chk = _check(res, CONTROLLING[key])
        ctrl = chk.controlling
        # Outward, inward (and, for the post, longitudinal) tie exactly for a round
        # section: accept any case tied with the controlling one.
        tied = {c.label.lower() for c in chk.checked if abs(c.ratio - ctrl.ratio) <= 1e-9 * ctrl.ratio}
        assert isinstance(value, str) and value.strip().lower() in tied, (
            f"{stop} {source} = {value!r}, tool = {sorted(tied)}"
        )
        return

    if _is_text(key):
        tool = tool_values(res)[key]
        assert isinstance(value, str) and value.strip().lower() == tool.lower(), (
            f"{stop} {source} = {value!r}, tool = {tool!r}"
        )
        return

    if not isinstance(value, (int, float)):
        pytest.fail(f"{path.name} {key} = {value!r}: a {source} value must be a bare number "
                    f"(no quotes; quotes make it text), or \"{PENDING}\"")
    tool = tool_values(res)[key]
    rel = abs(tool - value) / abs(value)
    assert rel <= TOLERANCE, (
        f"{stop} {source} = {value:g}, tool = {tool:.6g}, difference {rel:.2%} > 0.5%. "
        f"Do not change the tool or the {source} value until we know which is wrong."
    )


def assert_keys_match(path, source, values, expected):
    """Every key names a tool value the case covers, and every tool value the
    case covers has a key.

    The second half matters: a deleted value must not silently stop being
    tested. Each such tool value needs a key, as a value or "pending".
    """
    keys = {key for key, _ in _flatten(values)}
    unknown = sorted(keys - set(expected))
    assert not unknown, f"{path.name}: [{source}] keys that match no tool value the case covers: {unknown}"
    missing = sorted(set(expected) - keys)
    assert not missing, f"{path.name}: tool values with no [{source}] key: {missing}"


def assert_hand_subset(path, raw, expected):
    """An independent-calc case's [hand]: Micah's governing-case values, a
    subset of the tool values the case covers."""
    hand = {key for key, _ in _flatten(raw.get("hand", {}))}
    unknown = sorted(hand - set(expected))
    assert not unknown, f"{path.name}: [hand] keys that match no tool value the case covers: {unknown}"
    for group in raw["verification"]["covers"]:
        if group not in CHECK_GROUPS:
            continue
        assert f"{group}.controlling" in hand, (
            f"{path.name}: [hand] has no {group}.controlling; the governing case "
            f"is required for each check the case covers"
        )
        assert any(k.startswith(f"{group}.") and k != f"{group}.controlling" for k in hand), (
            f"{path.name}: [hand] has no {group} value besides controlling; record at "
            f"least the governing ratio (or deflection)"
        )


def assert_provenance(path, ind_raw):
    """[provenance] is filled once any independent value is recorded."""
    if all(v == PENDING for _, v in _flatten(ind_raw.get("independent", {}))):
        return
    prov = ind_raw.get("provenance", {})
    unfilled = [f for f in PROVENANCE if prov.get(f, PENDING) in (PENDING, "")]
    assert not unfilled, f"{path.name}: independent values recorded, [provenance] not filled: {unfilled}"
    assert isinstance(prov["written_on"], datetime.date), (
        f"{path.name}: [provenance] written_on must be a TOML date without quotes, e.g. 2026-10-03"
    )
    assert (ROOT / prov["calc"]).is_file(), f"{path.name}: [provenance] calc {prov['calc']!r} is not a file"


def check_case(path, raw, res, ind_raw=None):
    """The structure of one test case, by its declared kind. ind_raw is the
    independent values file, read from disk when not given."""
    k = kind(raw)
    assert k in KINDS, f"{path.name}: [verification] kind must be one of {KINDS}, not {k!r}"
    covers = raw["verification"].get("covers")
    groups = {key.split(".")[0] for key in tool_values(res)} | CHECK_GROUPS
    assert covers and set(covers) <= groups, (
        f"{path.name}: [verification] covers must list groups from {sorted(groups)}, not {covers!r}"
    )
    expected = expected_keys(raw, res)
    if k == FULL_HAND:
        assert_keys_match(path, "hand", raw.get("hand", {}), expected)
        return
    if ind_raw is None:
        ind = independent_path(path)
        assert ind.is_file(), (
            f"{path.name}: no {ind.relative_to(ROOT).as_posix()}; create it with "
            f"uv run python tests/independent_template.py {path.stem}"
        )
        ind_raw = _load(ind)
    assert_keys_match(path, "independent", ind_raw.get("independent", {}), expected)
    assert_hand_subset(path, raw, expected)
    assert_provenance(path, ind_raw)


@pytest.mark.parametrize("path", CASES, ids=[p.stem for p in CASES])
def test_case_keys_match_the_tool(runs, path):
    raw, res = runs(path)
    check_case(path, raw, res)


def render_template(case: Path, keys) -> str:
    """The independent values file for a case, every key "pending". Names
    only: it takes key names, never a value."""
    tables = {}
    for key in keys:
        parent, leaf = key.rsplit(".", 1)
        tables.setdefault(parent, []).append(leaf)
    out = [
        f"# Independent-calc values for {case.stem} (docs/brief/verification.md).",
        "#",
        "# Generated by tests/independent_template.py: every value the test",
        "# compares, each \"pending\". The independent calc",
        "# (.claude/skills/independent-calc/SKILL.md) replaces each \"pending\" with",
        "# its own value, in the unit the key's suffix names, and fills",
        "# [provenance]. Tool output never fills a value here (CLAUDE.md rule 5).",
        "# Forces are positive magnitudes; the case name gives the sense (an",
        "# upward P_r is tension, recorded as a positive number).",
        "",
        "[provenance]",
        f'calc = "{PENDING}"           # "tests/cases/independent/{case.stem}.md"',
        f'written_on = "{PENDING}"     # a TOML date, no quotes, e.g. 2026-10-03',
        f'model = "{PENDING}"          # model id',
        f'commit = "{PENDING}"         # the commit the calc ran on',
    ]
    for parent, leaves in tables.items():
        out += ["", f"[independent.{parent}]"]
        for leaf in leaves:
            hint = "  # text, in quotes" if _is_text(f"{parent}.{leaf}") else ""
            out.append(f'{leaf} = "{PENDING}"{hint}')
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# Self-tests of the machinery above
# ---------------------------------------------------------------------------

def _dev_run():
    """The dev section (Pipe2STD rail and post, 6'-0"), not a test case."""
    raw = {"project": {"name": "self-test"},
           "geometry": {"span": "6'-0\"", "post_height": 42, "baseplate_thickness": "1/2"},
           "top_rail": {"section": "Pipe2STD"}, "post": {"section": "Pipe2STD"}}
    return checks.run(project.from_dict(raw), Registry())


def test_comparison_machinery_catches_a_mismatch():
    """A right value passes; a value 1% off fails with the rule 2 message
    naming its source."""
    res = _dev_run()
    key = "check1.ratio.downward_concentrated"
    good = tool_values(res)[key]
    for source in ("hand", "independent"):
        compare(Path("self-test"), key, good * 1.004, res, source)
        with pytest.raises(AssertionError, match=f"RULE 2 STOP.*the {SOURCE_NAMES[source]} disagrees.*{source} = "):
            compare(Path("self-test"), key, good * 1.01, res, source)
    with pytest.raises(AssertionError, match="RULE 2 STOP"):
        compare(Path("self-test"), "check2.controlling", "upward, distributed", res)


def test_post_comparisons_catch_a_mismatch():
    """Numbers, equation names and the controlling direction all stop on a
    mismatch."""
    res = _dev_run()
    tool = tool_values(res)
    ratio = tool["check5.ratio.outward_concentrated"]
    compare(Path("self-test"), "check5.ratio.outward_concentrated", ratio * 1.004, res)
    with pytest.raises(AssertionError, match="RULE 2 STOP"):
        compare(Path("self-test"), "check5.ratio.outward_concentrated", ratio * 1.01, res)
    eq = tool["check5.equation.outward_concentrated"]
    compare(Path("self-test"), "check5.equation.outward_concentrated", eq.upper(), res)
    wrong = "H1-1a" if eq == "H1-1b" else "H1-1b"
    with pytest.raises(AssertionError, match="RULE 2 STOP"):
        compare(Path("self-test"), "check5.equation.outward_concentrated", wrong, res, "independent")
    with pytest.raises(AssertionError, match="RULE 2 STOP"):
        compare(Path("self-test"), "check5.controlling", "upward, concentrated", res, "independent")


def _case_file(name):
    return next(p for p in CASES if p.name == name)


def test_full_hand_case_1_must_be_complete(runs):
    """The full-hand rule on the real case 1, not a copy of it: the intact
    file passes; a deleted value, a deleted group or an unknown key fails."""
    case = _case_file("case-01.toml")
    raw, res = runs(case)
    assert kind(raw) == FULL_HAND
    check_case(case, raw, res)

    deleted = _load(case)
    del deleted["hand"]["check1"]["ratio"]["upward_distributed"]
    with pytest.raises(AssertionError, match=r"no \[hand\] key: \['check1.ratio.upward_distributed'\]"):
        check_case(case, deleted, res)

    group = _load(case)
    del group["hand"]["check2"]
    with pytest.raises(AssertionError, match=r"no \[hand\] key: \['check2.Delta_allow_in'"):
        check_case(case, group, res)

    unknown = _load(case)
    unknown["hand"]["check1"]["ratio"]["sideways_concentrated"] = 0.5
    with pytest.raises(AssertionError, match=r"match no tool value the case covers: \['check1.ratio.sideways_concentrated'\]"):
        check_case(case, unknown, res)


def test_a_case_must_declare_its_kind_and_groups(runs):
    case = _case_file("case-01.toml")
    _, res = runs(case)
    raw = _load(case)
    raw["verification"]["kind"] = "hand"
    with pytest.raises(AssertionError, match="kind must be one of"):
        check_case(case, raw, res)
    raw = _load(case)
    raw["verification"]["covers"] = ["check9"]
    with pytest.raises(AssertionError, match="covers must list groups"):
        check_case(case, raw, res)


def test_independent_case_keys_are_checked_both_ways(runs):
    """On the real case 2 and its independent file: a deleted or unknown
    independent key fails."""
    case = _case_file("case-02.toml")
    raw, res = runs(case)
    assert kind(raw) == INDEPENDENT_CALC
    ind = _load(independent_path(case))
    check_case(case, raw, res, ind)

    del ind["independent"]["check5"]["ratio"]["upward_distributed"]
    with pytest.raises(AssertionError, match=r"no \[independent\] key: \['check5.ratio.upward_distributed'\]"):
        check_case(case, raw, res, ind)

    ind = _load(independent_path(case))
    ind["independent"]["check5"]["ratio"]["sideways_concentrated"] = "pending"
    with pytest.raises(AssertionError, match=r"\[independent\] keys that match no tool value the case covers"):
        check_case(case, raw, res, ind)


def test_the_hand_subset_needs_the_governing_case(runs):
    case = _case_file("case-02.toml")
    raw, res = runs(case)
    ind = _load(independent_path(case))

    no_ctrl = _load(case)
    del no_ctrl["hand"]["check5"]["controlling"]
    with pytest.raises(AssertionError, match=r"\[hand\] has no check5.controlling"):
        check_case(case, no_ctrl, res, ind)

    only_ctrl = {"check5": {"controlling": "pending"}, "check6": raw["hand"]["check6"]}
    with pytest.raises(AssertionError, match=r"\[hand\] has no check5 value besides controlling"):
        check_case(case, {**raw, "hand": only_ctrl}, res, ind)

    outside = _load(case)
    outside["hand"]["check1"] = {"controlling": "pending"}
    with pytest.raises(AssertionError, match=r"\[hand\] keys that match no tool value the case covers: \['check1.controlling'\]"):
        check_case(case, outside, res, ind)


def test_provenance_is_required_once_a_value_is_recorded(runs):
    """Structure only: the placeholder 1.0 is never compared to the tool."""
    case = _case_file("case-02.toml")
    raw, res = runs(case)
    ind = _load(independent_path(case))
    ind["independent"]["post"]["D_in"] = 1.0
    with pytest.raises(AssertionError, match=r"\[provenance\] not filled: \['calc', 'written_on', 'model', 'commit'\]"):
        check_case(case, raw, res, ind)
    ind["provenance"] = {"calc": "tests/cases/case-02.toml", "written_on": "2026-10-03",
                         "model": "self-test", "commit": "0000000"}
    with pytest.raises(AssertionError, match="written_on must be a TOML date"):
        check_case(case, raw, res, ind)
    ind["provenance"]["written_on"] = datetime.date(2026, 10, 3)
    check_case(case, raw, res, ind)
    ind["provenance"]["calc"] = "tests/cases/independent/no-such-calc.md"
    with pytest.raises(AssertionError, match="is not a file"):
        check_case(case, raw, res, ind)


def test_template_has_every_key_and_no_value(runs):
    case = _case_file("case-02.toml")
    raw, res = runs(case)
    keys = expected_keys(raw, res)
    parsed = tomllib.loads(render_template(case, keys))
    assert {k for k, _ in _flatten(parsed["independent"])} == set(keys)
    assert {v for _, v in _flatten(parsed)} == {PENDING}
    assert set(parsed["provenance"]) == set(PROVENANCE)
