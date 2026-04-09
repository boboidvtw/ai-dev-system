"""
Test Runner — Executes pytest and captures structured results.
"""

import logging
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Structured test execution result."""

    passed: bool
    stdout: str
    stderr: str
    return_code: int

    @property
    def error_log(self) -> str:
        """Combined output for debugging."""
        return f"{self.stdout}\n{self.stderr}".strip()


def run_tests(
    test_path: str = "tests/",
    working_dir: str = ".",
    verbose: bool = True,
) -> TestResult:
    """
    Execute pytest and return structured result.

    Args:
        test_path: Path to test file or directory.
        working_dir: Working directory for subprocess.
        verbose: Whether to use pytest -v flag.

    Returns:
        TestResult with pass/fail status and output.
    """
    cmd = ["python", "-m", "pytest", test_path]
    if verbose:
        cmd.append("-v")

    logger.info(f"Running tests: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )

        test_result = TestResult(
            passed=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
            return_code=result.returncode,
        )

        if test_result.passed:
            logger.info("✅ All tests passed")
        else:
            logger.warning(f"❌ Tests failed (exit code {result.returncode})")
            logger.debug(f"Error output:\n{test_result.error_log[:500]}")

        return test_result

    except subprocess.TimeoutExpired:
        logger.error("Tests timed out after 120s")
        return TestResult(
            passed=False,
            stdout="",
            stderr="Test execution timed out after 120 seconds",
            return_code=-1,
        )
    except FileNotFoundError:
        logger.error("pytest not found — is it installed?")
        return TestResult(
            passed=False,
            stdout="",
            stderr="pytest not found. Install with: pip install pytest",
            return_code=-1,
        )
