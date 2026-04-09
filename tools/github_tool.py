from __future__ import annotations

"""
GitHub Tool — Handles git operations and PR creation.

Supports two modes:
1. CLI mode: Uses `git` + `gh` CLI (simpler, good for MVP)
2. API mode: Uses PyGithub (more robust, better for CI/CD)
"""

import logging
import subprocess
from pathlib import Path

from github import Github, GithubException

from config import cfg

logger = logging.getLogger(__name__)


class GitHubTool:
    """Manages git operations and GitHub PR lifecycle."""

    def __init__(self, repo_path: str | None = None):
        self.repo_path = repo_path or cfg.workspace_dir
        self._github: Github | None = None

    @property
    def github(self) -> Github:
        """Lazy-init GitHub API client."""
        if self._github is None:
            if not cfg.github_token:
                raise ValueError("GITHUB_TOKEN is not set")
            self._github = Github(cfg.github_token)
        return self._github

    def _run_git(self, *args: str) -> subprocess.CompletedProcess:
        """Run a git command in the workspace directory."""
        cmd = ["git", *args]
        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            logger.error(f"Git command failed: {result.stderr}")
        return result

    def create_branch(self, branch_name: str) -> bool:
        """Create and checkout a new branch."""
        logger.info(f"Creating branch: {branch_name}")
        result = self._run_git("checkout", "-b", branch_name)
        if result.returncode != 0:
            # Branch might already exist — try switching
            result = self._run_git("checkout", branch_name)
        return result.returncode == 0

    def commit_changes(self, message: str, files: list[str] | None = None) -> bool:
        """Stage and commit changes."""
        if files:
            for f in files:
                self._run_git("add", f)
        else:
            self._run_git("add", "-A")

        result = self._run_git("commit", "-m", message)
        if result.returncode == 0:
            logger.info(f"Committed: {message}")
        return result.returncode == 0

    def push_branch(self, branch_name: str) -> bool:
        """Push branch to remote."""
        logger.info(f"Pushing branch: {branch_name}")
        result = self._run_git("push", "-u", "origin", branch_name)
        return result.returncode == 0

    def get_issue(self, issue_number: int) -> tuple[str, str, list[str]]:
        """
        Fetch issue details.
        
        Returns:
            Tuple of (title, body, labels)
        """
        try:
            repo = self.github.get_repo(cfg.github_repo)
            issue = repo.get_issue(number=issue_number)
            labels = [l.name for l in issue.labels]
            logger.info(f"Fetched Issue #{issue_number}: {issue.title}")
            return issue.title, issue.body, labels
        except GithubException as e:
            logger.error(f"Failed to fetch issue #{issue_number}: {e}")
            raise

    def list_open_issues(self) -> list[tuple[int, str]]:
        """List open issues in the repository."""
        try:
            repo = self.github.get_repo(cfg.github_repo)
            issues = repo.get_issues(state="open")
            return [(i.number, i.title) for i in issues if not i.pull_request]
        except GithubException as e:
            logger.error(f"Failed to list issues: {e}")
            return []

    def create_pr(
        self,
        title: str,
        body: str,
        branch_name: str,
        base: str = "main",
        linked_issue: int | None = None,
    ) -> str | None:
        """
        Create a Pull Request via GitHub API.

        Returns:
            PR URL if successful, None otherwise.
        """
        if linked_issue:
            body += f"\n\nCloses #{linked_issue}"
            
        logger.info(f"Creating PR: {title}")

        try:
            repo = self.github.get_repo(cfg.github_repo)
            pr = repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=base,
            )
            logger.info(f"PR created: {pr.html_url}")
            return pr.html_url

        except GithubException as e:
            logger.error(f"Failed to create PR: {e}")
            return None

    def full_workflow(
        self,
        branch_name: str,
        commit_message: str,
        pr_title: str,
        pr_body: str,
        files: list[str] | None = None,
        linked_issue: int | None = None,
    ) -> str | None:
        """
        Complete workflow: branch → commit → push → PR.

        Returns:
            PR URL if successful, None otherwise.
        """
        if not self.create_branch(branch_name):
            return None
        if not self.commit_changes(commit_message, files):
            return None
        if not self.push_branch(branch_name):
            return None
        return self.create_pr(pr_title, pr_body, branch_name, linked_issue=linked_issue)
