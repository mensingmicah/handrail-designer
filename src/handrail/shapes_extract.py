"""Extract shape rows from the unmodified AISC Shapes Database into TOML.

Run from the repo root:

    uv run python -m handrail.shapes_extract

The derived file (data/shapes-pipe.toml) is generated, never hand-edited.
tests/test_shapes_extract.py re-reads the original .xlsx and confirms the
derived file matches it row for row.
"""

import hashlib
import json
from pathlib import Path

import openpyxl

REPO = Path(__file__).resolve().parents[2]
XLSX = REPO / "data" / "aisc-shapes-database-v16.0.xlsx"
SHEET = "Database v16.0"
IMPERIAL_COLUMNS = 84  # columns 0-83 are US customary; 84 on repeat in SI
EMPTY = "–"  # the database's marker for "not applicable" (an en dash)

# Columns extracted for PIPE, with units from the database Readme sheet.
PIPE_COLUMNS = {
    "EDI_Std_Nomenclature": "",
    "AISC_Manual_Label": "",
    "W": "lbf/ft",
    "A": "in^2",
    "OD": "in",
    "ID": "in",
    "tnom": "in",
    "tdes": "in",
    "D/t": "",
    "Ix": "in^4",
    "Zx": "in^3",
    "Sx": "in^3",
    "rx": "in",
    "Iy": "in^4",
    "Zy": "in^3",
    "Sy": "in^3",
    "ry": "in",
    "J": "in^4",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(shape_type: str) -> tuple[list[str], list[tuple]]:
    """Return the imperial header and every row of one shape type, in file order."""
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    try:
        rows = wb[SHEET].iter_rows(values_only=True)
        header = list(next(rows))[:IMPERIAL_COLUMNS]
        body = [r[:IMPERIAL_COLUMNS] for r in rows if r[0] == shape_type]
    finally:
        wb.close()
    return header, body


def _toml_value(v) -> str:
    if isinstance(v, bool):
        raise TypeError("unexpected boolean in shapes database")
    if isinstance(v, (int, float)):
        return repr(v)  # repr round-trips a float exactly
    return json.dumps(v, ensure_ascii=False)  # a TOML basic string


def render_pipe_toml() -> str:
    header, rows = read_rows("PIPE")
    col = {name: header.index(name) for name in PIPE_COLUMNS}
    lines = [
        "# GENERATED FILE. Do not edit by hand.",
        "# Produced by: uv run python -m handrail.shapes_extract",
        f"# Source: data/{XLSX.name}, sheet '{SHEET}', rows with Type = PIPE,",
        "# US customary columns only, values exactly as stored in the workbook.",
        f"# Source SHA-256: {sha256(XLSX)}",
        "",
        f'source_file = "{XLSX.name}"',
        f'source_sha256 = "{sha256(XLSX)}"',
        "",
        "[units]",
    ]
    lines += [f"{json.dumps(k)} = {json.dumps(u)}" for k, u in PIPE_COLUMNS.items() if u]
    for row in rows:
        label = row[col["AISC_Manual_Label"]]
        lines.append("")
        lines.append(f"[shape.{json.dumps(label)}]")
        for name in PIPE_COLUMNS:
            lines.append(f"{json.dumps(name)} = {_toml_value(row[col[name]])}")
    return "\n".join(lines) + "\n"


PIPE_TOML = REPO / "data" / "shapes-pipe.toml"


def main() -> None:
    PIPE_TOML.write_text(render_pipe_toml(), encoding="utf-8", newline="\n")
    print(f"wrote {PIPE_TOML.relative_to(REPO)}")


if __name__ == "__main__":
    main()
