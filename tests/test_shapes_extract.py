"""Each derived shapes file matches the unmodified AISC Shapes Database row for row.

Three derived files: the PIPE rows (slice 1), the round HSS rows (slice 5,
step 3) and the rectangular and square HSS rows (slice 6, step 1). The same
four tests run on each.
"""

import tomllib

import pytest

from handrail import shapes
from handrail.shapes import PIPE, RECT_HSS, ROUND_HSS
from handrail.shapes_extract import EMPTY, EXTRACTS, XLSX, render_pipe_toml, render_toml, sha256
from handrail.shapes_extract import PIPE as PIPE_EXTRACT


@pytest.fixture(scope="module", params=EXTRACTS, ids=lambda e: e.toml.stem)
def extract(request):
    return request.param


@pytest.fixture(scope="module")
def derived(extract):
    with open(extract.toml, "rb") as f:
        return tomllib.load(f)


@pytest.fixture(scope="module")
def original(extract):
    return extract.rows()


def test_derived_file_names_the_workbook_it_came_from(derived):
    assert derived["source_sha256"] == sha256(XLSX)


def test_row_for_row(extract, derived, original):
    header, rows = original
    labels = [r[header.index("AISC_Manual_Label")] for r in rows]
    # Same shapes, same order, none missing or extra
    assert list(derived["shape"]) == labels
    for row in rows:
        entry = derived["shape"][row[header.index("AISC_Manual_Label")]]
        for name in extract.columns:
            assert entry[name] == row[header.index(name)], (entry["AISC_Manual_Label"], name)


def test_no_populated_imperial_column_is_left_behind(extract, original):
    header, rows = original
    skipped = [i for i, name in enumerate(header) if name not in extract.columns and name != "Type"]
    for row in rows:
        for i in skipped:
            assert row[i] in (EMPTY, None), (row[2], header[i], row[i])


def test_committed_file_is_current_output_of_the_script(extract):
    assert extract.toml.read_text(encoding="utf-8") == render_toml(extract)


def test_the_pipe_file_is_unchanged_by_the_shared_renderer():
    assert render_pipe_toml() == render_toml(PIPE_EXTRACT)


def test_round_hss_rows_are_the_hss_rows_with_an_outside_diameter():
    """The workbook lists rectangular and round HSS under one Type. The
    brief counts 189 round rows, 61 of them with the OD column rounded away
    from the designation's diameter (checks.md, S5-4)."""
    labels = shapes.labels(ROUND_HSS)
    assert len(labels) == 189 and len(set(labels)) == 189
    rounded = [lb for lb in labels if shapes.section(lb).OD.m_as("inch") != float(lb[3:].split("X")[0])]
    assert len(rounded) == 61
    assert not set(labels) & set(shapes.labels(PIPE))  # one designation, one section


def test_lookup_returns_published_values_with_units():
    p = shapes.section("Pipe1-1/2Std")  # case-insensitive
    assert p.label == "Pipe1-1/2STD" and p.family == PIPE
    assert p.W.m_as("lbf/ft") == 2.72
    assert p.OD.m_as("in") == 1.9
    assert p.tdes.m_as("in") == 0.135
    assert p.I.m_as("in^4") == 0.293
    assert p.S.m_as("in^3") == 0.309
    assert p.Z.m_as("in^3") == 0.421
    assert p.D_t == 14.1


def test_lookup_finds_a_round_hss_and_uses_its_published_od():
    """S5-4: the OD is the database's, 2.38 in, not the designation's 2.375."""
    s = shapes.section("hss2.375x0.125")
    assert s.label == "HSS2.375X0.125" and s.family == ROUND_HSS and s.source == shapes.DB
    assert s.OD.m_as("in") == 2.38
    assert (s.tnom.m_as("in"), s.tdes.m_as("in"), s.D_t) == (0.125, 0.116, 20.5)
    assert (s.W.m_as("lbf/ft"), s.A.m_as("in^2")) == (3.01, 0.823)
    assert (s.I.m_as("in^4"), s.S.m_as("in^3"), s.Z.m_as("in^3"), s.r.m_as("in")) == (0.527, 0.443, 0.592, 0.8)


def test_every_round_hss_has_the_same_properties_about_both_axes():
    for label in shapes.labels(ROUND_HSS):
        s = shapes.section(label)
        assert s.x == s.y, label


def _inches(text: str) -> float:
    """A designation's dimension as a number: "2-1/2" is 2.5, "1/8" is 0.125."""
    whole, _, frac = text.rpartition("-") if "/" in text else (text, "", "")
    if not frac:
        return float(whole)
    num, den = frac.split("/")
    return (float(whole) if whole else 0.0) + float(num) / float(den)


def test_rectangular_hss_rows_are_the_hss_rows_without_an_outside_diameter():
    """The brief counts 525 rectangular rows, 126 of them square, every one
    listed with Ht >= B and x the strong axis (inputs.md, S6-2), and with
    Ht and B stored exactly as the designation reads (welds.md, S6-9), so
    the width comparisons at a rectangular member need no tolerance."""
    labels = shapes.labels(RECT_HSS)
    assert len(labels) == 525 and len(set(labels)) == 525
    assert not set(labels) & (set(shapes.labels(ROUND_HSS)) | set(shapes.labels(PIPE)))
    square = 0
    for label in labels:
        s = shapes.section(label)
        H, B = s.rect.H.m_as("inch"), s.rect.B.m_as("inch")
        assert H >= B, label
        assert s.x.I >= s.y.I and s.x.Z >= s.y.Z, label
        h_text, b_text, _ = label.removeprefix("HSS").split("X")
        assert (H, B) == (_inches(h_text), _inches(b_text)), label
        square += s.rect.square
        assert s.rect.square == (s.x == s.y), label
    assert square == 126


def test_lookup_finds_a_rectangular_hss_with_its_published_values():
    s = shapes.section("hss4x2x1/8")
    assert s.label == "HSS4X2X1/8" and s.family == RECT_HSS and s.source == shapes.DB
    r = s.rect
    assert (r.H.m_as("in"), r.B.m_as("in"), r.b_t, r.h_t, r.J.m_as("in^4")) == (4, 2, 14.2, 31.5, 2.2)
    assert not r.square and not s.is_round
    assert (s.tnom.m_as("in"), s.tdes.m_as("in")) == (0.125, 0.116)
    assert (s.W.m_as("lbf/ft"), s.A.m_as("in^2")) == (4.75, 1.3)
    assert (s.x.I.m_as("in^4"), s.x.S.m_as("in^3"), s.x.Z.m_as("in^3"), s.x.r.m_as("in")) == (2.65, 1.32, 1.66, 1.43)
    assert (s.y.I.m_as("in^4"), s.y.S.m_as("in^3"), s.y.Z.m_as("in^3"), s.y.r.m_as("in")) == (0.898, 0.898, 1.02, 0.83)


def test_a_square_hss_is_of_the_rectangular_family():
    s = shapes.section("HSS2X2X1/8")
    assert s.family == RECT_HSS and s.rect.square and s.x == s.y


def test_each_outline_refuses_the_other_outlines_values():
    """A check written for a round section must never compute on a
    rectangular one's numbers, or the reverse: the value is refused, not
    defaulted."""
    with pytest.raises(TypeError, match="HSS2X2X1/8 .rectangular HSS. is not a round section"):
        _ = shapes.section("HSS2X2X1/8").OD
    with pytest.raises(TypeError, match="is not a round section"):
        _ = shapes.section("HSS2X2X1/8").D_t
    with pytest.raises(TypeError, match="Pipe2STD .AISC pipe. is not a rectangular section"):
        _ = shapes.section("Pipe2STD").rect
    assert shapes.section("Pipe2STD").is_round


def test_one_row_lists_its_nominal_wall_to_three_decimals():
    """A database finding (checks.md, S6-14 item 9; data/README.md):
    HSS1-1/2X1-1/2X3/16 lists t_nom = 0.188 in where every other 3/16 in row
    lists 0.1875 in. It is used as published (S5-4)."""
    odd = [lb for lb in shapes.labels(RECT_HSS)
           if lb.endswith("X3/16") and shapes.section(lb).tnom.m_as("inch") != 0.1875]
    assert odd == ["HSS1-1/2X1-1/2X3/16"]
    assert shapes.section(odd[0]).tnom.m_as("inch") == 0.188


def test_unknown_designation_is_named():
    with pytest.raises(shapes.ShapeNotFound, match="'Pipe99STD' is not an AISC pipe or round HSS in"):
        shapes.section("Pipe99STD")
