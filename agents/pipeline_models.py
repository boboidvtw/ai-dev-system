from __future__ import annotations

"""
Engineering Pipeline — the structured 5-step output model.

Represents each step's result as typed dataclasses for
traceability & structured logging.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ProblemUnderstanding:
    """Step 1 output — structured understanding of the task."""

    summary: str = ""
    requirements: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    clarifying_questions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    input_output: dict[str, str] = field(default_factory=dict)
    edge_cases: list[str] = field(default_factory=list)
    language: str = "python"
    confidence: float = 0.0

    @property
    def needs_clarification(self) -> bool:
        return self.confidence < 0.7 or len(self.clarifying_questions) > 0

    @classmethod
    def from_json(cls, raw: str) -> ProblemUnderstanding:
        """Parse LLM JSON output into structured object."""
        try:
            data = json.loads(raw)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse Step 1 output: {e}")
            return cls(summary=raw[:200], confidence=0.3)


@dataclass
class SolutionDesign:
    """Step 2 output — architecture and approach."""

    approach: str = ""
    architecture: dict[str, Any] = field(default_factory=dict)
    data_structures: list[str] = field(default_factory=list)
    algorithms: list[str] = field(default_factory=list)
    complexity: dict[str, str] = field(default_factory=dict)
    files_to_create_or_modify: list[dict[str, str]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    @classmethod
    def from_json(cls, raw: str) -> SolutionDesign:
        try:
            data = json.loads(raw)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse Step 2 output: {e}")
            return cls(approach=raw[:200])


@dataclass
class FileOutput:
    """A single output file from Step 3."""

    path: str
    content: str


@dataclass
class Implementation:
    """Step 3 output — the actual code files."""

    files: list[FileOutput] = field(default_factory=list)
    raw_output: str = ""

    @classmethod
    def from_raw(cls, raw: str) -> Implementation:
        """Parse multi-file output separated by ### FILE: path ###."""
        files: list[FileOutput] = []
        current_path: str | None = None
        current_lines: list[str] = []

        for line in raw.split("\n"):
            stripped = line.strip()
            if stripped.startswith("### FILE:") and stripped.endswith("###"):
                # Save previous file
                if current_path:
                    files.append(FileOutput(
                        path=current_path,
                        content="\n".join(current_lines).strip(),
                    ))
                # Start new file
                current_path = stripped.replace("### FILE:", "").replace("###", "").strip()
                current_lines = []
            else:
                current_lines.append(line)

        # Save last file
        if current_path:
            files.append(FileOutput(
                path=current_path,
                content="\n".join(current_lines).strip(),
            ))
        elif raw.strip():
            # Single file output (no ### FILE: header)
            files.append(FileOutput(path="output.py", content=raw.strip()))

        return cls(files=files, raw_output=raw)


@dataclass
class OptimizationReview:
    """Step 5 output — review and optimization suggestions."""

    code_quality_score: int = 0
    issues_found: list[dict[str, str]] = field(default_factory=list)
    optimizations: list[dict[str, str]] = field(default_factory=list)
    architecture_suggestions: list[str] = field(default_factory=list)
    alternative_approaches: list[str] = field(default_factory=list)
    final_verdict: str = "needs_fixes"

    @property
    def is_shippable(self) -> bool:
        return self.final_verdict == "ship"

    @classmethod
    def from_json(cls, raw: str) -> OptimizationReview:
        try:
            data = json.loads(raw)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse Step 5 output: {e}")
            return cls(code_quality_score=5, final_verdict="needs_fixes")


@dataclass
class PipelineResult:
    """Complete pipeline output — all 5 steps bundled."""

    task: str
    understanding: ProblemUnderstanding | None = None
    design: SolutionDesign | None = None
    implementation: Implementation | None = None
    test_code: Implementation | None = None
    review: OptimizationReview | None = None
    success: bool = False
    error: str | None = None

    def to_report(self) -> str:
        """Generate human-readable engineering report."""
        sections: list[str] = [f"# 🤖 AI Engineering Report\n\n**Task:** {self.task}\n"]

        if self.understanding:
            u = self.understanding
            sections.append("## Step 1: Problem Understanding")
            sections.append(f"**Summary:** {u.summary}")
            sections.append(f"**Confidence:** {u.confidence:.0%}")
            if u.requirements:
                sections.append("**Requirements:**\n" + "\n".join(f"- {r}" for r in u.requirements))
            if u.assumptions:
                sections.append("**Assumptions:**\n" + "\n".join(f"- {a}" for a in u.assumptions))
            if u.edge_cases:
                sections.append("**Edge Cases:**\n" + "\n".join(f"- {e}" for e in u.edge_cases))
            if u.clarifying_questions:
                sections.append("**⚠️ Clarifying Questions:**\n" + "\n".join(f"- {q}" for q in u.clarifying_questions))

        if self.design:
            d = self.design
            sections.append("\n## Step 2: Solution Design")
            sections.append(f"**Approach:** {d.approach}")
            if d.complexity:
                sections.append(f"**Complexity:** Time={d.complexity.get('time', '?')}, Space={d.complexity.get('space', '?')}")
            if d.risks:
                sections.append("**Risks:**\n" + "\n".join(f"- {r}" for r in d.risks))

        if self.implementation:
            sections.append("\n## Step 3: Implementation")
            for f in self.implementation.files:
                sections.append(f"**File:** `{f.path}` ({len(f.content)} chars)")

        if self.test_code:
            sections.append("\n## Step 4: Test Cases")
            for f in self.test_code.files:
                sections.append(f"**File:** `{f.path}` ({len(f.content)} chars)")

        if self.review:
            r = self.review
            sections.append("\n## Step 5: Optimization Review")
            sections.append(f"**Quality Score:** {r.code_quality_score}/10")
            sections.append(f"**Verdict:** {r.final_verdict}")
            if r.issues_found:
                sections.append("**Issues:**\n" + "\n".join(
                    f"- [{i.get('severity', '?')}] {i.get('description', '')}" for i in r.issues_found
                ))

        sections.append(f"\n---\n**Result:** {'✅ SUCCESS' if self.success else '❌ FAILED'}")
        if self.error:
            sections.append(f"**Error:** {self.error}")

        return "\n\n".join(sections)
