from __future__ import annotations

"""
Configuration manager
Loads settings from .env and provides typed access.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Immutable configuration object."""

    # LLM
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))

    # GitHub
    github_token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    github_repo: str = field(default_factory=lambda: os.getenv("GITHUB_REPO", ""))

    # System
    max_fix_retries: int = field(
        default_factory=lambda: int(os.getenv("MAX_FIX_RETRIES", "3"))
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    workspace_dir: str = field(
        default_factory=lambda: os.getenv("WORKSPACE_DIR", "./workspace")
    )

    def validate(self) -> list[str]:
        """Return list of missing required config values."""
        issues = []
        if not self.openai_api_key and "ollama" not in self.llm_model:
            issues.append("OPENAI_API_KEY is required for non-Ollama models")
        if not self.github_token:
            issues.append("GITHUB_TOKEN is required for PR creation")
        if not self.github_repo:
            issues.append("GITHUB_REPO is required (format: owner/repo)")
        return issues


# Singleton
cfg = Config()
