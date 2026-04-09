from __future__ import annotations

"""
Multi-Agent Coordinator — The Orchestrator.
Manages the collaboration between PM, Dev, and QA agents.
"""

import logging
from dataclasses import dataclass, field

from agents.dev_agent import DevAgent
from agents.pm_agent import PMAgent
from agents.qa_agent import QAAgent
from agents.pipeline_models import PipelineResult

logger = logging.getLogger(__name__)

class TeamCoordinator:
    """
    Orchestrates a specialized team of agents to solve engineering problems.
    """
    def __init__(self, model: str | None = None):
        self.pm = PMAgent(model)
        self.dev = DevAgent(model)
        self.qa = QAAgent(model)
        logger.info("Team Coordinator initialized with PM, Dev, and QA specialists.")

    def run_collaborative_workflow(self, task: str, context: str = "") -> PipelineResult:
        """
        Executes a multi-agent workflow:
        1. PM analyzes and clarifies requirements.
        2. Dev designs the solution.
        3. Dev implements the code.
        4. QA writes the test suite (adversarial).
        5. Dev reviews and optimizes.
        """
        logger.info("Starting Collaborative Multi-Agent Workflow...")
        result = PipelineResult(task=task)

        try:
            # 1. PM Step
            result.understanding = self.pm.analyze_task(task, context)
            
            # 2. & 3. Dev Steps (Design + Implement)
            result.design = self.dev.step2_design(task, result.understanding)
            result.implementation = self.dev.step3_implement(
                task, result.understanding, result.design, context
            )

            # 4. QA Step (Specialized QA Agent)
            result.test_code = self.qa.generate_test_suite(
                task, result.understanding, result.implementation
            )

            # 5. Review Step
            result.review = self.dev.step5_optimize(task, result.implementation)
            
            result.success = True
            logger.info("Multi-agent collaboration successful!")

        except Exception as e:
            result.success = False
            result.error = str(e)
            logger.error(f"Multi-agent workflow failed: {e}")

        return result
