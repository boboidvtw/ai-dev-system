from __future__ import annotations

"""
AI Dev System — Orchestrator (main.py)

Structured 5-Step Engineering Pipeline:
  Step 1: Problem Understanding — clarify, question, identify edge cases
  Step 2: Solution Design — architecture, complexity analysis
  Step 3: Implementation — production-quality code
  Step 4: Test Cases — comprehensive edge-case coverage
  Step 5: Optimization — self-review & final verdict

Post-pipeline:
  - Write code + tests to filesystem
  - Execute tests
  - Auto-fix loop (up to N retries)
  - Git branch + commit + push + PR
"""

import argparse
import logging
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from agents.dev_agent import DevAgent
from agents.pipeline_models import PipelineResult
from config import cfg
from tools.file_manager import backup_file, read_file, write_file
from tools.github_tool import GitHubTool
from tools.test_runner import run_tests
from tools.rag_engine import RAGEngine

console = Console()


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging with Rich."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )


def slugify(text: str) -> str:
    """Convert text to git-branch-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug[:50].strip("-")


def display_step1(result: PipelineResult) -> None:
    """Display Problem Understanding results."""
    u = result.understanding
    if not u:
        return

    table = Table(title="Step 1: Problem Understanding", show_header=False, padding=(0, 2))
    table.add_column("Key", style="cyan", width=20)
    table.add_column("Value", style="white")

    table.add_row("Summary", u.summary)
    table.add_row("Confidence", f"{'🟢' if u.confidence >= 0.7 else '🟡'} {u.confidence:.0%}")
    table.add_row("Language", u.language)
    table.add_row("Requirements", "\n".join(f"• {r}" for r in u.requirements) or "—")
    table.add_row("Assumptions", "\n".join(f"• {a}" for a in u.assumptions) or "—")
    table.add_row("Edge Cases", "\n".join(f"• {e}" for e in u.edge_cases) or "—")

    if u.clarifying_questions:
        table.add_row(
            "[bold yellow]⚠️ Questions[/bold yellow]",
            "\n".join(f"[yellow]• {q}[/yellow]" for q in u.clarifying_questions),
        )

    console.print(table)
    console.print()


def display_step2(result: PipelineResult) -> None:
    """Display Solution Design results."""
    d = result.design
    if not d:
        return

    table = Table(title="Step 2: Solution Design", show_header=False, padding=(0, 2))
    table.add_column("Key", style="cyan", width=20)
    table.add_column("Value", style="white")

    table.add_row("Approach", d.approach)
    if d.complexity:
        table.add_row("Time Complexity", d.complexity.get("time", "?"))
        table.add_row("Space Complexity", d.complexity.get("space", "?"))
    if d.data_structures:
        table.add_row("Data Structures", ", ".join(d.data_structures))
    if d.dependencies:
        table.add_row("Dependencies", ", ".join(d.dependencies))
    if d.risks:
        table.add_row("[yellow]Risks[/yellow]", "\n".join(f"• {r}" for r in d.risks))

    console.print(table)
    console.print()


def display_step5(result: PipelineResult) -> None:
    """Display Optimization Review results."""
    r = result.review
    if not r:
        return

    verdict_style = {
        "ship": "[bold green]✅ SHIP",
        "needs_fixes": "[bold yellow]⚠️ NEEDS FIXES",
        "major_rework": "[bold red]❌ MAJOR REWORK",
    }

    table = Table(title="Step 5: Optimization Review", show_header=False, padding=(0, 2))
    table.add_column("Key", style="cyan", width=20)
    table.add_column("Value", style="white")

    table.add_row("Quality Score", f"{r.code_quality_score}/10")
    table.add_row("Verdict", verdict_style.get(r.final_verdict, r.final_verdict))

    if r.issues_found:
        issues_text = "\n".join(
            f"[{'red' if i.get('severity') == 'critical' else 'yellow'}]"
            f"[{i.get('severity', '?')}] {i.get('description', '')}[/]"
            for i in r.issues_found
        )
        table.add_row("Issues", issues_text)

    if r.optimizations:
        opts_text = "\n".join(
            f"[{i.get('impact', 'medium')}] {i.get('description', '')}"
            for i in r.optimizations
        )
        table.add_row("Optimizations", opts_text)

    console.print(table)
    console.print()


def run_pipeline(
    task: str,
    target_file: str,
    test_path: str = "tests/",
    skip_pr: bool = False,
    skip_review: bool = False,
    dry_run: bool = False,
    report_path: str | None = None,
    interactive: bool = False,
    rag_context: str = "",
) -> bool:
    """
    Execute the full AI engineering pipeline.

    Args:
        task: Natural language task description.
        target_file: File to create/modify.
        test_path: Path to test file or directory.
        skip_pr: If True, skip PR creation.
        skip_review: If True, skip Step 5.
        dry_run: If True, don't write files or push.
        report_path: If set, save engineering report to this path.
        interactive: If True, pause on low-confidence for user input.
        rag_context: Context retrieved from RAG.

    Returns:
        True if pipeline completed successfully.
    """
    logger = logging.getLogger("pipeline")

    console.print(Panel(
        f"[bold cyan]🤖 AI Software Engineer — 5-Step Pipeline[/bold cyan]\n\n"
        f"[yellow]Task:[/yellow]  {task}\n"
        f"[yellow]File:[/yellow]  {target_file}\n"
        f"[yellow]Model:[/yellow] {cfg.llm_model}",
        title="Pipeline Start",
        border_style="cyan",
    ))

    # --- Read existing code (context) ---
    context = rag_context
    try:
        existing_code = read_file(target_file)
        context += f"\n\n--- Existing File Content ({target_file}) ---\n{existing_code}"
        logger.info(f"Read existing file: {target_file} ({len(existing_code)} chars)")
    except FileNotFoundError:
        logger.info(f"Target file not found — will create new: {target_file}")

    # ─── Execute 5-Step Pipeline ───
    dev = DevAgent()

    console.print("\n[bold blue]━━━ Running 5-Step Engineering Pipeline ━━━[/bold blue]\n")
    pipeline_result = dev.run_full_pipeline(task, context, skip_review=skip_review)

    if not pipeline_result.success:
        console.print(f"[bold red]Pipeline failed: {pipeline_result.error}[/bold red]")
        return False

    # ─── Display Step Results ───
    display_step1(pipeline_result)

    # Interactive mode: pause if low confidence
    if (
        interactive
        and pipeline_result.understanding
        and pipeline_result.understanding.needs_clarification
    ):
        console.print(
            "[bold yellow]⚠️ Low confidence — review questions above. "
            "Press Enter to continue or Ctrl+C to abort.[/bold yellow]"
        )
        try:
            input()
        except KeyboardInterrupt:
            console.print("\n[dim]Aborted by user.[/dim]")
            return False

    display_step2(pipeline_result)

    # ─── Step 3: Write Implementation ───
    impl = pipeline_result.implementation
    if not impl or not impl.files:
        console.print("[bold red]No implementation generated[/bold red]")
        return False

    console.print(Panel(
        "\n".join(f"📄 {f.path} ({len(f.content)} chars)" for f in impl.files),
        title="Step 3: Implementation — Files Generated",
        border_style="green",
    ))

    # Set default path for single-file output
    if len(impl.files) == 1 and impl.files[0].path == "output.py":
        impl.files[0].path = target_file

    if not dry_run:
        for f in impl.files:
            if Path(f.path).exists() and f.path == target_file:
                backup_file(f.path)
            write_file(f.path, f.content)
            console.print(f"  [green]✅ Written: {f.path}[/green]")
    else:
        for f in impl.files:
            console.print(Panel(f.content, title=f"[dim]{f.path}[/dim]", border_style="blue"))

    # ─── Step 4: Write Tests ───
    test_impl = pipeline_result.test_code
    if test_impl and test_impl.files:
        console.print(Panel(
            "\n".join(f"🧪 {f.path}" for f in test_impl.files),
            title="Step 4: Test Cases — Files Generated",
            border_style="yellow",
        ))
        if not dry_run:
            for f in test_impl.files:
                write_file(f.path, f.content)
                console.print(f"  [green]✅ Written: {f.path}[/green]")

    # ─── Step 5: Display Review ───
    display_step5(pipeline_result)

    # ─── Run Tests + Auto-Fix Loop ───
    if dry_run:
        console.print("[dim]Dry run — skipping test execution[/dim]")
    else:
        max_retries = cfg.max_fix_retries
        for attempt in range(1, max_retries + 1):
            console.print(
                f"\n[bold yellow]🧪 Running tests "
                f"(attempt {attempt}/{max_retries})...[/bold yellow]"
            )

            result = run_tests(test_path=test_path, working_dir=cfg.workspace_dir)

            if result.passed:
                console.print("[bold green]✅ All tests passed![/bold green]")
                break

            console.print(f"[red]❌ Tests failed (attempt {attempt})[/red]")
            logger.debug(f"Error output:\n{result.error_log[:1000]}")

            if attempt < max_retries:
                console.print("[yellow]🔧 AI auto-fix in progress...[/yellow]")
                # Fix each implementation file
                for f in impl.files:
                    current_code = read_file(f.path)
                    fixed_code = dev.fix_code(current_code, result.error_log, task)
                    write_file(f.path, fixed_code)
                console.print("[green]✅ Fixed code written[/green]")
            else:
                console.print("[bold red]💥 Max retries reached — giving up[/bold red]")
                # Still save report
                if report_path:
                    pipeline_result.success = False
                    pipeline_result.error = f"Tests failed after {max_retries} attempts"
                    write_file(report_path, pipeline_result.to_report())
                return False

    # ─── Save Engineering Report ───
    if report_path:
        write_file(report_path, pipeline_result.to_report())
        console.print(f"[dim]📝 Report saved: {report_path}[/dim]")

    # ─── Create PR ───
    if skip_pr or dry_run:
        console.print("[dim]Skipping PR creation[/dim]")
        console.print(Panel("[bold green]✅ Pipeline complete![/bold green]",
                            border_style="green"))
        return True

    console.print("\n[bold cyan]📤 Creating Pull Request...[/bold cyan]")
    github = GitHubTool(repo_path=cfg.workspace_dir)
    branch_name = f"ai-eng/{slugify(task)}-{uuid.uuid4().hex[:6]}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build PR body from pipeline result
    pr_body_parts = [
        "## 🤖 AI Software Engineer — Automated Delivery\n",
        f"**Task:** {task}",
        f"**Model:** `{cfg.llm_model}`",
        f"**Timestamp:** {timestamp}",
    ]
    if pipeline_result.review:
        pr_body_parts.append(
            f"**Quality Score:** {pipeline_result.review.code_quality_score}/10"
        )
        pr_body_parts.append(
            f"**Verdict:** {pipeline_result.review.final_verdict}"
        )
    pr_body_parts.append("\n---\n_Generated by the 5-Step AI Engineering Pipeline._")

    all_files = [f.path for f in impl.files]
    if test_impl:
        all_files += [f.path for f in test_impl.files]

    pr_url = github.full_workflow(
        branch_name=branch_name,
        commit_message=f"feat: {task}",
        pr_title=f"🤖 AI Engineer: {task}",
        pr_body="\n".join(pr_body_parts),
        files=all_files,
    )

    if pr_url:
        console.print(Panel(
            f"[bold green]🎉 PR created:[/bold green]\n{pr_url}",
            title="Success",
            border_style="green",
        ))
        return True
    else:
        console.print("[bold red]Failed to create PR[/bold red]")
        return False


def cli():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="🤖 AI Software Engineer — 5-Step Engineering Pipeline",
    )
    parser.add_argument("task", help="Task description (what to build/fix)")
    parser.add_argument("file", help="Target file to create/modify")
    parser.add_argument(
        "--test-path", default="tests/", help="Path to tests (default: tests/)"
    )
    parser.add_argument("--skip-pr", action="store_true", help="Skip PR creation")
    parser.add_argument("--skip-review", action="store_true", help="Skip Step 5 optimization")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--report", default=None, help="Save engineering report to file")
    parser.add_argument("--interactive", action="store_true", help="Pause on low confidence")
    parser.add_argument("--log-level", default=None, help="DEBUG/INFO/WARNING")

    args = parser.parse_args()
    setup_logging(args.log_level or cfg.log_level)
    logger = logging.getLogger("pipeline")

    # --- Step 0: RAG Context ---
    rag_context = ""
    try:
        with console.status("[bold magenta]🧠 Indexing repository (RAG)..."):
            rag = RAGEngine()
            rag.index_repo(".")
            rag_context = rag.query(args.task)
            logger.info("RAG context retrieved successfully")
    except Exception as e:
        logger.warning(f"RAG failed (falling back to no-context): {e}")

    success = run_pipeline(
        task=args.task,
        target_file=args.file,
        test_path=args.test_path,
        skip_pr=args.skip_pr,
        skip_review=args.skip_review,
        dry_run=args.dry_run,
        report_path=args.report,
        interactive=args.interactive,
        rag_context=rag_context,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    cli()
