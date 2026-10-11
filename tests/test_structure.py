"""The layout of the calc engine's modules (issue #21, item 5)."""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "handrail"


def test_no_engine_module_imports_another_inside_a_function():
    """checks.py used to import the other checks inside compute(), because
    they imported its result types and a top-level import would have been
    circular. With the result types in results.py and the orchestration in
    engine.py there is no cycle, and an import inside a function would be
    the sign of a new one. (__init__.main imports the command line late on
    purpose, so importing the package stays light.)"""
    hidden = []
    for path in sorted(SRC.glob("*.py")):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(fn):
                module = node.module if isinstance(node, ast.ImportFrom) else None
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else []
                if (module or "").startswith("handrail") or any(n.startswith("handrail") for n in names):
                    hidden.append(f"{path.name}:{node.lineno} in {fn.name}()")
    assert not hidden, f"handrail imports inside a function: {hidden}"


def test_the_result_types_import_no_check_module():
    """results.py is at the bottom of the import order: every check builds on
    it, so it must not import any of them at run time."""
    tree = ast.parse((SRC / "results.py").read_text(encoding="utf-8"))
    checks = {"rail", "intermediate", "post", "welds", "reactions", "engine", "validate", "loading", "flexure"}
    imported = set()
    for node in tree.body:  # top-level imports only; the TYPE_CHECKING block is annotations, not run
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("handrail."):
            imported.add(node.module.split(".")[1])
    assert not imported & checks, imported & checks
