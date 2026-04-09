"""
Tests for test_runner module.
"""

from unittest.mock import patch, MagicMock
from tools.test_runner import run_tests


class TestTestRunner:

    @patch("tools.test_runner.subprocess.run")
    def test_passing_tests(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="2 passed",
            stderr="",
        )
        result = run_tests()
        assert result.passed is True
        assert "2 passed" in result.stdout

    @patch("tools.test_runner.subprocess.run")
    def test_failing_tests(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="1 failed",
            stderr="AssertionError",
        )
        result = run_tests()
        assert result.passed is False
        assert "AssertionError" in result.error_log

    @patch("tools.test_runner.subprocess.run")
    def test_timeout(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pytest", timeout=120)
        result = run_tests()
        assert result.passed is False
        assert "timed out" in result.stderr

    @patch("tools.test_runner.subprocess.run")
    def test_pytest_not_installed(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        result = run_tests()
        assert result.passed is False
        assert "not found" in result.stderr
