# data/

## aisc-shapes-database-v16.0.xlsx

AISC Shapes Database, Version 16.0, published by the American Institute of
Steel Construction (AISC). It tabulates dimensions and section properties for
standard structural steel shapes.

The file is the original as received from AISC: not modified, converted, or
restructured. Version is taken from the filename and docs/brief/scope.md.

## shapes-pipe.toml (derived)

Generated from the workbook above by `uv run python -m handrail.shapes_extract`.
Never edit it by hand; rerun the script. It holds every PIPE row (US customary
columns only), with each value exactly as stored in the workbook, and records
the workbook's SHA-256. tests/test_shapes_extract.py re-reads the original
workbook and confirms the derived file matches it row for row, that no
populated column was skipped, and that the committed file is the script's
current output.
