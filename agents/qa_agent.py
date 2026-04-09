from __future__ import annotations

"""
QA Agent — The quality gatekeeper.
Focuses on Step 4: Testing, edge-case verification, and robustness.
"""

import logging
from dataclasses import dataclass

import litellm
from agents.pipeline_models import Implementation
from agents.prompts import MASTER_IDENTITY, STEP4_TESTS
from config import cfg

logger = logging.getLogger(__name__)

QA_PROMPT_EXTENSION = """
As a QA Agent, your goal is to BREAK the code. You are malicious toward bugs.

Your priorities:
1. Security: Look for injection, overflow, and auth bypass.
2. Stability: Test null values, empty strings, and massive inputs.
3. Correctness: Ensure the business logic matches the PM's requirements exactly.
"""

class QAAgent:
    def __init__(self, model: str | None = None):
        self.model = model or cfg.llm_model
        self.system_prompt = f"{MASTER_IDENTITY}\n{STEP4_TESTS}\n{QA_PROMPT_EXTENSION}"

    def generate_test_suite(self, task: str, understanding: Any, implementation: Implementation) -> Implementation:
        logger.info("QA Agent generating adversarial test suite...")
        
        impl_code = "\n\n".join(f"### FILE: {f.path} ###\n{f.content}" for f in implementation.files)
        
        user_msg = (
            f"Task: {task}\n\n"
            f"Requirements & Edge Cases:\n{understanding}\n\n"
            f"Code to Verify:\n{impl_code}"
        )

        response = litellm.completion(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.2
        )
        
        return Implementation.from_raw(response.choices[0].message.content.strip())
