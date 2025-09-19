"""Development-time validations for the Prismalia project."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

CONFLICT_START_PREFIX = "<<<<<<< "
CONFLICT_END_PREFIX = ">>>>>>> "
CONFLICT_MID_LINE = "======="


def _iter_candidate_files(root: Path) -> Iterable[Path]:
    """Yield text-like files that should not contain merge markers."""

    ignored_dirs = {
        ".git",
        "__pycache__",
        ".venv",
        "env",
        "venv",
        "assets",
    }
    allowed_suffixes = {
        ".py",
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
    }

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in allowed_suffixes:
            continue
        yield path


def ensure_no_merge_conflicts() -> None:
    """Raise an error if conflict markers are present in source files.

    The check can be disabled by setting the ``PRISMALIA_SKIP_CONFLICT_CHECK``
    environment variable to any non-empty value. This makes it easy to bypass
    the guard in constrained environments while keeping the default behaviour
    safe for developers.
    """

    if os.environ.get("PRISMALIA_SKIP_CONFLICT_CHECK"):
        return

    root = Path(__file__).resolve().parents[1]
    offending: list[str] = []
    for file_path in _iter_candidate_files(root):
        try:
            with file_path.open(encoding="utf-8") as handle:
                if _file_contains_conflict_marker(handle):
                    offending.append(str(file_path.relative_to(root)))
        except UnicodeDecodeError:
            with file_path.open(encoding="utf-8", errors="ignore") as handle:
                if _file_contains_conflict_marker(handle):
                    offending.append(str(file_path.relative_to(root)))

    if offending:
        joined = "\n - ".join(offending)
        raise RuntimeError(
            "Merge conflict markers detected in the repository:\n - " + joined
        )


def _file_contains_conflict_marker(lines: Iterable[str]) -> bool:
    """Return ``True`` if any Git conflict markers are present in ``lines``."""

    for raw_line in lines:
        stripped = raw_line.rstrip("\n\r")
        if stripped.startswith(CONFLICT_START_PREFIX):
            return True
        if stripped.startswith(CONFLICT_END_PREFIX):
            return True
        if stripped.strip() == CONFLICT_MID_LINE:
            return True
    return False

