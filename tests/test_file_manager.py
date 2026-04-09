"""
Tests for file_manager utilities.
"""

import tempfile
from pathlib import Path

from tools.file_manager import backup_file, read_file, write_file
import pytest


class TestFileManager:

    def test_write_and_read(self, tmp_path):
        filepath = str(tmp_path / "test.py")
        write_file(filepath, "print('hello')")
        content = read_file(filepath)
        assert content == "print('hello')"

    def test_write_creates_parents(self, tmp_path):
        filepath = str(tmp_path / "deep" / "nested" / "dir" / "file.py")
        write_file(filepath, "code here")
        assert Path(filepath).exists()
        assert read_file(filepath) == "code here"

    def test_read_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/path/file.py")

    def test_backup_file(self, tmp_path):
        filepath = str(tmp_path / "original.py")
        write_file(filepath, "original content")

        backup_path = backup_file(filepath)
        assert backup_path is not None
        assert Path(backup_path).exists()
        assert read_file(backup_path) == "original content"
        assert backup_path.endswith(".py.bak")

    def test_backup_nonexistent_returns_none(self):
        result = backup_file("/nonexistent/file.py")
        assert result is None
