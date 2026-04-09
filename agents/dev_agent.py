from __future__ import annotations

"""
Dev Agent — Structured 5-Step AI Software Engineer.

Follows a disciplined engineering pipeline:
  Step 1: Problem Understanding — clarify, question, identify edge cases
  Step 2: Solution Design — architecture, complexity, data structures
  Step 3: Implementation — production-quality code
  Step 4: Test Cases — comprehensive tests with edge coverage
  Step 5: Optimization — self-review, suggestions, verdict

Uses litellm for model-agnostic LLM calls.
"""

import json
import logging
from dataclasses import dataclass

import litellm

from agents.pipeline_models import (
    FileOutput,
    Implementation,
    OptimizationReview,
    PipelineResult,
    ProblemUnderstanding,
    SolutionDesign,
)
from agents.prompts import (
    STEP1_UNDERSTAND,
    STEP2_DESIGN,
    STEP3_IMPLEMENT,
    STEP4_TESTS,
    STEP5_OPTIMIZE,
    STEP_FIX,
)
from config import cfg

logger = logging.getLogger(__name__)

# Suppress litellm's verbose logging unless DEBUG
litellm.suppress_debug_info = True


class DevAgent:
    """
    AI Software Engineer Agent — delivers production-grade quality
    through a structured 5-step engineering pipeline.
    """

    def __init__(self, model: str | None = None):
        self.model = model or cfg.llm_model
        logger.info(f"DevAgent initialized with model: {self.model}")

    # ──────────────────────────────────────────
    # Core LLM call
    # ──────────────────────────────────────────

    def _call_llm(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        """
        Make a single LLM call with structured prompts.

        Args:
            system_prompt: Step-specific system prompt.
            user_message: Task + context for this step.
            temperature: Sampling temperature (lower = more deterministic).
            max_tokens: Max output tokens.

        Returns:
            Raw LLM output as string.

        Raises:
            RuntimeError: If LLM call fails.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = litellm.completion(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            result = response.choices[0].message.content.strip()

            # Strip markdown fences if LLM wraps output
            if result.startswith("```"):
                lines = result.split("\n")
                # Remove first and last fence lines
                if lines[-1].strip() == "```":
                    lines = lines[1:-1]
                else:
                    lines = lines[1:]
                result = "\n".join(lines).strip()

            return result

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise RuntimeError(f"LLM call failed: {e}") from e

    # ──────────────────────────────────────────
    # Step 1: Problem Understanding
    # ──────────────────────────────────────────

    def step1_understand(self, task: str, context: str = "") -> ProblemUnderstanding:
        """
        Analyze task requirements, identify gaps, and list edge cases.

        Returns ProblemUnderstanding with confidence score.
        If confidence < 0.7, clarifying_questions will be populated.
        """
        logger.info("Step 1: Problem Understanding...")

        user_msg = f"Task: {task}"
        if context:
            user_msg += f"\n\nExisting code context:\n```\n{context}\n```"

        raw = self._call_llm(
            system_prompt=STEP1_UNDERSTAND,
            user_message=user_msg,
            temperature=0.3,
        )

        result = ProblemUnderstanding.from_json(raw)
        logger.info(
            f"Step 1 complete — confidence: {result.confidence:.0%}, "
            f"edge cases: {len(result.edge_cases)}, "
            f"questions: {len(result.clarifying_questions)}"
        )
        return result

    # ──────────────────────────────────────────
    # Step 2: Solution Design
    # ──────────────────────────────────────────

    def step2_design(
        self,
        task: str,
        understanding: ProblemUnderstanding,
    ) -> SolutionDesign:
        """
        Design architecture, choose algorithms, estimate complexity.
        """
        logger.info("Step 2: Solution Design...")

        user_msg = (
            f"Task: {task}\n\n"
            f"Problem Understanding:\n{json.dumps(understanding.__dict__, indent=2, ensure_ascii=False)}"
        )

        raw = self._call_llm(
            system_prompt=STEP2_DESIGN,
            user_message=user_msg,
            temperature=0.3,
        )

        result = SolutionDesign.from_json(raw)
        logger.info(
            f"Step 2 complete — approach: {result.approach[:60]}, "
            f"complexity: {result.complexity}"
        )
        return result

    # ──────────────────────────────────────────
    # Step 3: Implementation
    # ──────────────────────────────────────────

    def step3_implement(
        self,
        task: str,
        understanding: ProblemUnderstanding,
        design: SolutionDesign,
        context: str = "",
    ) -> Implementation:
        """
        Generate production-quality code based on understanding + design.
        """
        logger.info("Step 3: Implementation...")

        user_msg = (
            f"Task: {task}\n\n"
            f"Problem Understanding:\n{json.dumps(understanding.__dict__, indent=2, ensure_ascii=False)}\n\n"
            f"Solution Design:\n{json.dumps(design.__dict__, indent=2, ensure_ascii=False)}"
        )
        if context:
            user_msg += f"\n\nExisting code to modify:\n```\n{context}\n```"

        raw = self._call_llm(
            system_prompt=STEP3_IMPLEMENT,
            user_message=user_msg,
            temperature=0.15,
            max_tokens=8192,
        )

        result = Implementation.from_raw(raw)
        logger.info(
            f"Step 3 complete — generated {len(result.files)} file(s), "
            f"total {sum(len(f.content) for f in result.files)} chars"
        )
        return result

    # ──────────────────────────────────────────
    # Step 4: Test Cases
    # ──────────────────────────────────────────

    def step4_tests(
        self,
        task: str,
        understanding: ProblemUnderstanding,
        implementation: Implementation,
    ) -> Implementation:
        """
        Generate comprehensive test cases for the implementation.
        """
        logger.info("Step 4: Test Cases...")

        impl_code = "\n\n".join(
            f"### FILE: {f.path} ###\n{f.content}" for f in implementation.files
        )

        user_msg = (
            f"Task: {task}\n\n"
            f"Edge Cases to test:\n"
            + "\n".join(f"- {e}" for e in understanding.edge_cases)
            + f"\n\nImplementation:\n{impl_code}"
        )

        raw = self._call_llm(
            system_prompt=STEP4_TESTS,
            user_message=user_msg,
            temperature=0.2,
            max_tokens=4096,
        )

        result = Implementation.from_raw(raw)
        # Ensure test files go in tests/ directory
        for f in result.files:
            if not f.path.startswith("tests/"):
                f.path = f"tests/{f.path}"
        logger.info(f"Step 4 complete — generated {len(result.files)} test file(s)")
        return result

    # ──────────────────────────────────────────
    # Step 5: Optimization & Review
    # ──────────────────────────────────────────

    def step5_optimize(
        self,
        task: str,
        implementation: Implementation,
    ) -> OptimizationReview:
        """
        Self-review the implementation for quality, performance, and correctness.
        """
        logger.info("Step 5: Optimization & Review...")

        impl_code = "\n\n".join(
            f"### FILE: {f.path} ###\n{f.content}" for f in implementation.files
        )

        user_msg = f"Task: {task}\n\nImplementation to review:\n{impl_code}"

        raw = self._call_llm(
            system_prompt=STEP5_OPTIMIZE,
            user_message=user_msg,
            temperature=0.3,
        )

        result = OptimizationReview.from_json(raw)
        logger.info(
            f"Step 5 complete — quality: {result.code_quality_score}/10, "
            f"verdict: {result.final_verdict}"
        )
        return result

    # ──────────────────────────────────────────
    # Fix Code (retry loop)
    # ──────────────────────────────────────────

    def fix_code(self, code: str, error_log: str, task: str) -> str:
        """
        Fix failing code based on test error output.

        Args:
            code: Current broken code.
            error_log: Test error output.
            task: Original task for context.

        Returns:
            Fixed code as string.
        """
        logger.info("Attempting to fix code based on error log...")

        user_msg = (
            f"Original task: {task}\n\n"
            f"Current code:\n```\n{code}\n```\n\n"
            f"Test error output:\n```\n{error_log}\n```"
        )

        return self._call_llm(
            system_prompt=STEP_FIX,
            user_message=user_msg,
            temperature=0.1,
            max_tokens=8192,
        )

    # ──────────────────────────────────────────
    # Full Pipeline (all 5 steps)
    # ──────────────────────────────────────────

    def run_full_pipeline(
        self,
        task: str,
        context: str = "",
        skip_review: bool = False,
    ) -> PipelineResult:
        """
        Execute the complete 5-step engineering pipeline.

        Args:
            task: Natural language task description.
            context: Existing code context (if modifying).
            skip_review: If True, skip Step 5 optimization review.

        Returns:
            PipelineResult with all step outputs bundled.
        """
        result = PipelineResult(task=task)

        try:
            # Step 1
            result.understanding = self.step1_understand(task, context)

            # If confidence is too low and there are questions, we still proceed
            # but log the warning — the orchestrator can decide to pause
            if result.understanding.needs_clarification:
                logger.warning(
                    f"Low confidence ({result.understanding.confidence:.0%}) — "
                    f"{len(result.understanding.clarifying_questions)} questions pending"
                )

            # Step 2
            result.design = self.step2_design(task, result.understanding)

            # Step 3
            result.implementation = self.step3_implement(
                task, result.understanding, result.design, context
            )

            # Step 4
            result.test_code = self.step4_tests(
                task, result.understanding, result.implementation
            )

            # Step 5 (optional)
            if not skip_review:
                result.review = self.step5_optimize(task, result.implementation)

            result.success = True

        except RuntimeError as e:
            result.error = str(e)
            result.success = False
            logger.error(f"Pipeline failed: {e}")

        return result

    # ──────────────────────────────────────────
    # Backward compat — simple generate_code
    # ──────────────────────────────────────────

    def generate_code(self, task: str, context: str = "") -> str:
        """
        Simple code generation (backward compatible).
        Uses Steps 1-3 internally.
        """
        pipe = self.run_full_pipeline(task, context, skip_review=True)
        if pipe.implementation and pipe.implementation.files:
            return pipe.implementation.files[0].content
        return ""
