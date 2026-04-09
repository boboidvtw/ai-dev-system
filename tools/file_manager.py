from __future__ import annotations

"""
File Manager — Handles reading/writing code files in the workspace.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def read_file(filepath: str) -> str:
    """Read file content as string."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    content = path.read_text(encoding="utf-8")
    logger.debug(f"Read {len(content)} chars from {filepath}")
    return content


def write_file(filepath: str, content: str) -> None:
    """Write content to file, creating parent directories if needed."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    logger.info(f"Wrote {len(content)} chars to {filepath}")


def backup_file(filepath: str) -> str | None:
    """Create a .bak backup of a file before modification."""
    path = Path(filepath)
    if not path.exists():
        return None
    backup_path = path.with_suffix(path.suffix + ".bak")
    backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    logger.info(f"Backup created: {backup_path}")
    return str(backup_path)
