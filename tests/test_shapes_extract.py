"""The derived pipe file matches the unmodified AISC Shapes Database row for row."""

import tomllib

import pytest

from handrail import shapes
from handrail.shapes_extract import (
    EMPTY,
    PIPE_COLUMNS,
    PIPE_TOML,
    XLSX,
    read_rows,
    render_pipe_toml,
    sha256,
)


@pytest.fixture(scope="module")
def derived():
    with open(PIPE_TOML, "rb") as f:
        return tomllib.load(f)


@pytest.fixture(scope="module")
def original():
    return read_rows("PIPE")


def test_derived_file_names_the_workbook_it_came_from(derived):
    assert derived["source_sha256"] == sha256(XLSX)


def test_row_for_row(derived, original):
    header, rows = original
    labels = [r[header.index("AISC_Manual_Label")] for r in rows]
    # Same shapes, same order, none missing or extra
    assert list(derived["shape"]) == labels
    for row in rows:
        entry = derived["shape"][row[header.index("AISC_Manual_Label")]]
        for name in PIPE_COLUMNS:
            assert entry[name] == row[header.index(name)], (entry["AISC_Manual_Label"], name)


def test_no_populated_imperial_column_is_left_behind(original):
    header, rows = original
    skipped = [i for i, name in enumerate(header) if name not in PIPE_COLUMNS and name != "Type"]
    for row in rows:
        for i in skipped:
            assert row[i] in (EMPTY, None), (row[2], header[i], row[i])


def test_committed_file_is_current_output_of_the_script():
    assert PIPE_TOML.read_text(encoding="utf-8") == render_pipe_toml()


def test_lookup_returns_published_values_with_units():
    p = shapes.pipe("Pipe1-1/2Std")  # case-insensitive
    assert p.label == "Pipe1-1/2STD"
    assert p.W.m_as("lbf/ft") == 2.72
    assert p.OD.m_as("in") == 1.9
    assert p.tdes.m_as("in") == 0.135
    assert p.I.m_as("in^4") == 0.293
    assert p.S.m_as("in^3") == 0.309
    assert p.Z.m_as("in^3") == 0.421
    assert p.D_t == 14.1


def test_unknown_designation_is_named():
    with pytest.raises(shapes.ShapeNotFound, match="Pipe99STD"):
        shapes.pipe("Pipe99STD")
