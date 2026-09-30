"""What code and registry a calc ran with, for the footer on every page.

A printed calc must trace to exact code. The footer shows the git commit of
the tool and of the registry file, and "uncommitted changes" beside either
one when the working tree differs from that commit.
"""

import subprocess
from dataclasses import dataclass
from importlib.metadata import version as _pkg_version
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CODE_PATHS = ("src", "data", "pyproject.toml", "uv.lock")
REGISTRY_PATHS = ("registry",)


@dataclass(frozen=True)
class Stamp:
    tool_version: str
    code_commit: str
    code_dirty: bool
    registry_commit: str
    registry_dirty: bool

    def footer_parts(self) -> tuple[str, str]:
        code = f"Tool {self.tool_version} ({self.code_commit})"
        if self.code_dirty:
            code += " uncommitted changes"
        reg = f"Registry {self.registry_commit}"
        if self.registry_dirty:
            reg += " uncommitted changes"
        return code, reg


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args], cwd=REPO, capture_output=True, text=True, timeout=10, check=True
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip()


def _dirty(paths) -> bool:
    out = _git("status", "--porcelain", "--", *paths)
    # If git can't answer, don't claim the tree is clean.
    return True if out is None else bool(out)


def stamp() -> Stamp:
    return Stamp(
        tool_version=_pkg_version("handrail"),
        code_commit=_git("rev-parse", "--short", "HEAD") or "unknown commit",
        code_dirty=_dirty(CODE_PATHS),
        registry_commit=_git("log", "-1", "--format=%h", "--", "registry/code-values.toml") or "unknown commit",
        registry_dirty=_dirty(REGISTRY_PATHS),
    )
