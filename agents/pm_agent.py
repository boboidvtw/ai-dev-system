from __future__ import annotations

"""
PM Agent — The product manager of the team.
Focuses on Step 1: Requirements analysis, task breakdown, and gap identification.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

import litellm
from agents.pipeline_models import ProblemUnderstanding
from agents.prompts import MASTER_IDENTITY, STEP1_UNDERSTAND
from config import cfg

logger = logging.getLogger(__name__)

PM_PROMPT_EXTENSION = """
As a PM Agent, your primary responsibility is to ensure the engineering team has 
ZERO ambiguity. You are the defender of the product vision.

When analyzing tasks:
1. Break down complex tasks into manageable sub-tasks.
2. Anticipate user needs and suggest sensible defaults.
3. Be skeptical — if a requirement is vague, demand clarification.
"""

class PMAgent:
    def __init__(self, model: str | None = None):
        self.model = model or cfg.llm_model
        self.system_prompt = f"{MASTER_IDENTITY}\n{STEP1_UNDERSTAND}\n{PM_PROMPT_EXTENSION}"

    def analyze_task(self, task: str, context: str = "") -> ProblemUnderstanding:
        logger.info(f"PM Agent analyzing task: {task[:50]}...")
        
        user_msg = f"Task: {task}"
        if context:
            user_msg += f"\n\nContext:\n{context}"

        response = litellm.completion(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.3
        )
        
        raw = response.choices[0].message.content.strip()
        # Simple extraction logic (already in ProblemUnderstanding)
        return ProblemUnderstanding.from_json(raw)
