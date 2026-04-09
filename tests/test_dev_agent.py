from __future__ import annotations

"""
Tests for the 5-Step DevAgent pipeline.
All LLM calls are mocked — no real API usage.
"""

import json

import pytest
from unittest.mock import patch, MagicMock

from agents.dev_agent import DevAgent
from agents.pipeline_models import (
    Implementation,
    OptimizationReview,
    PipelineResult,
    ProblemUnderstanding,
    SolutionDesign,
)


# ──────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────

MOCK_STEP1_OUTPUT = json.dumps({
    "summary": "Fix user login validation",
    "requirements": ["validate email format", "check password length"],
    "assumptions": ["using email as username"],
    "clarifying_questions": [],
    "constraints": ["must be backward compatible"],
    "input_output": {"inputs": "email, password", "outputs": "bool"},
    "edge_cases": ["empty email", "SQL injection", "unicode chars"],
    "language": "python",
    "confidence": 0.9,
})

MOCK_STEP2_OUTPUT = json.dumps({
    "approach": "Add input validation before auth check",
    "architecture": {"components": ["validator", "auth"], "data_flow": "input→validate→auth"},
    "data_structures": ["str"],
    "algorithms": ["regex matching"],
    "complexity": {"time": "O(n)", "space": "O(1)"},
    "files_to_create_or_modify": [{"path": "auth.py", "action": "modify"}],
    "dependencies": [],
    "risks": ["breaking existing login flow"],
})

MOCK_STEP3_OUTPUT = """### FILE: auth.py ###
import re

def validate_email(email: str) -> bool:
    if not email:
        raise ValueError("Email cannot be empty")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def login(email: str, password: str) -> bool:
    if not validate_email(email):
        return False
    if len(password) < 8:
        return False
    return True
"""

MOCK_STEP4_OUTPUT = """### FILE: tests/test_auth.py ###
import pytest
from auth import validate_email, login

def test_valid_email():
    assert validate_email("user@example.com") is True

def test_empty_email_raises():
    with pytest.raises(ValueError):
        validate_email("")
"""

MOCK_STEP5_OUTPUT = json.dumps({
    "code_quality_score": 8,
    "issues_found": [{"severity": "info", "description": "Could use pydantic for validation"}],
    "optimizations": [{"type": "readability", "description": "Add docstrings", "impact": "low"}],
    "architecture_suggestions": ["Consider using a validation library"],
    "alternative_approaches": ["pydantic EmailStr"],
    "final_verdict": "ship",
})


def _mock_completion(content: str):
    """Create a mock litellm completion response."""
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content=content))]
    return mock_resp


# ──────────────────────────────────────────
# Step 1 Tests
# ──────────────────────────────────────────

class TestStep1Understand:

    @patch("agents.dev_agent.litellm.completion")
    def test_basic_understanding(self, mock_llm):
        mock_llm.return_value = _mock_completion(MOCK_STEP1_OUTPUT)
        agent = DevAgent(model="test")
        result = agent.step1_understand("fix login bug")

        assert result.confidence == 0.9
        assert not result.needs_clarification
        assert "empty email" in result.edge_cases
        assert result.language == "python"

    @patch("agents.dev_agent.litellm.completion")
    def test_low_confidence_triggers_questions(self, mock_llm):
        low_conf = json.dumps({
            "summary": "unclear task",
            "requirements": [],
            "assumptions": [],
            "clarifying_questions": ["What framework?", "Which database?"],
            "constraints": [],
            "input_output": {},
            "edge_cases": [],
            "language": "python",
            "confidence": 0.4,
        })
        mock_llm.return_value = _mock_completion(low_conf)
        agent = DevAgent(model="test")
        result = agent.step1_understand("do something")

        assert result.needs_clarification
        assert len(result.clarifying_questions) == 2

    def test_parse_invalid_json_gracefully(self):
        result = ProblemUnderstanding.from_json("not valid json at all")
        assert result.confidence == 0.3  # Fallback


# ──────────────────────────────────────────
# Step 2 Tests
# ──────────────────────────────────────────

class TestStep2Design:

    @patch("agents.dev_agent.litellm.completion")
    def test_design_output(self, mock_llm):
        mock_llm.return_value = _mock_completion(MOCK_STEP2_OUTPUT)
        agent = DevAgent(model="test")
        understanding = ProblemUnderstanding(summary="test", confidence=0.9)
        result = agent.step2_design("fix login", understanding)

        assert "validation" in result.approach.lower()
        assert result.complexity["time"] == "O(n)"


# ──────────────────────────────────────────
# Step 3 Tests
# ──────────────────────────────────────────

class TestStep3Implement:

    @patch("agents.dev_agent.litellm.completion")
    def test_multi_file_parsing(self, mock_llm):
        mock_llm.return_value = _mock_completion(MOCK_STEP3_OUTPUT)
        agent = DevAgent(model="test")
        understanding = ProblemUnderstanding(summary="test", confidence=0.9)
        design = SolutionDesign(approach="test")
        result = agent.step3_implement("fix login", understanding, design)

        assert len(result.files) == 1
        assert result.files[0].path == "auth.py"
        assert "validate_email" in result.files[0].content

    def test_single_file_fallback(self):
        """If no ### FILE: header, treat as single file."""
        result = Implementation.from_raw("def hello():\n    return 'hi'")
        assert len(result.files) == 1
        assert result.files[0].path == "output.py"


# ──────────────────────────────────────────
# Step 4 Tests
# ──────────────────────────────────────────

class TestStep4Tests:

    @patch("agents.dev_agent.litellm.completion")
    def test_test_generation(self, mock_llm):
        mock_llm.return_value = _mock_completion(MOCK_STEP4_OUTPUT)
        agent = DevAgent(model="test")
        understanding = ProblemUnderstanding(
            summary="test", edge_cases=["empty email"], confidence=0.9
        )
        impl = Implementation.from_raw(MOCK_STEP3_OUTPUT)
        result = agent.step4_tests("fix login", understanding, impl)

        assert len(result.files) >= 1
        # Should be in tests/ directory
        assert all(f.path.startswith("tests/") for f in result.files)


# ──────────────────────────────────────────
# Step 5 Tests
# ──────────────────────────────────────────

class TestStep5Optimize:

    @patch("agents.dev_agent.litellm.completion")
    def test_review_output(self, mock_llm):
        mock_llm.return_value = _mock_completion(MOCK_STEP5_OUTPUT)
        agent = DevAgent(model="test")
        impl = Implementation.from_raw(MOCK_STEP3_OUTPUT)
        result = agent.step5_optimize("fix login", impl)

        assert result.code_quality_score == 8
        assert result.is_shippable
        assert result.final_verdict == "ship"

    def test_non_shippable_verdict(self):
        result = OptimizationReview(final_verdict="needs_fixes")
        assert not result.is_shippable


# ──────────────────────────────────────────
# Full Pipeline Tests
# ──────────────────────────────────────────

class TestFullPipeline:

    @patch("agents.dev_agent.litellm.completion")
    def test_full_pipeline_success(self, mock_llm):
        """Test all 5 steps run to completion."""
        mock_llm.side_effect = [
            _mock_completion(MOCK_STEP1_OUTPUT),
            _mock_completion(MOCK_STEP2_OUTPUT),
            _mock_completion(MOCK_STEP3_OUTPUT),
            _mock_completion(MOCK_STEP4_OUTPUT),
            _mock_completion(MOCK_STEP5_OUTPUT),
        ]
        agent = DevAgent(model="test")
        result = agent.run_full_pipeline("fix login bug")

        assert result.success
        assert result.understanding is not None
        assert result.design is not None
        assert result.implementation is not None
        assert result.test_code is not None
        assert result.review is not None

    @patch("agents.dev_agent.litellm.completion")
    def test_pipeline_skip_review(self, mock_llm):
        """Test pipeline with Step 5 skipped."""
        mock_llm.side_effect = [
            _mock_completion(MOCK_STEP1_OUTPUT),
            _mock_completion(MOCK_STEP2_OUTPUT),
            _mock_completion(MOCK_STEP3_OUTPUT),
            _mock_completion(MOCK_STEP4_OUTPUT),
        ]
        agent = DevAgent(model="test")
        result = agent.run_full_pipeline("fix login", skip_review=True)

        assert result.success
        assert result.review is None  # Skipped

    @patch("agents.dev_agent.litellm.completion")
    def test_pipeline_llm_failure(self, mock_llm):
        """Test pipeline handles LLM errors gracefully."""
        mock_llm.side_effect = Exception("API rate limit exceeded")
        agent = DevAgent(model="test")
        result = agent.run_full_pipeline("fix login")

        assert not result.success
        assert "rate limit" in result.error.lower()

    @patch("agents.dev_agent.litellm.completion")
    def test_generate_code_backward_compat(self, mock_llm):
        """Test generate_code() backward compatibility."""
        mock_llm.side_effect = [
            _mock_completion(MOCK_STEP1_OUTPUT),
            _mock_completion(MOCK_STEP2_OUTPUT),
            _mock_completion(MOCK_STEP3_OUTPUT),
            _mock_completion(MOCK_STEP4_OUTPUT),
        ]
        agent = DevAgent(model="test")
        code = agent.generate_code("fix login")

        assert "validate_email" in code

    def test_pipeline_report_generation(self):
        """Test report generation from pipeline result."""
        result = PipelineResult(
            task="fix login",
            understanding=ProblemUnderstanding(
                summary="Fix login validation",
                confidence=0.9,
                edge_cases=["empty email"],
            ),
            success=True,
        )
        report = result.to_report()
        assert "Fix login validation" in report
        assert "SUCCESS" in report
