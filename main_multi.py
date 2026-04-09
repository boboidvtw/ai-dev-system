from __future__ import annotations

"""
AI Dev System — Multi-Agent CLI

Usage:
  python3 main_multi.py "Task description" target_file.py
"""

import argparse
import logging
import sys
from rich.console import Console
from rich.panel import Panel

from agents.coordinator import TeamCoordinator
from config import cfg

console = Console()

def main():
    parser = argparse.ArgumentParser(description="🤖 AI Multi-Agent Engineering Team")
    parser.add_argument("task", help="Engineering task")
    parser.add_argument("file", help="Target file")
    
    args = parser.parse_args()
    
    # Simple logging setup
    logging.basicConfig(level=logging.INFO)
    
    console.print(Panel(
        f"[bold blue]👥 Multi-Agent Engineering Team[/bold blue]\n\n"
        f"PM, Dev, and QA agents are collaborating on:\n"
        f"'{args.task}'",
        title="Session Start"
    ))

    coordinator = TeamCoordinator()
    result = coordinator.run_collaborative_workflow(args.task)

    if result.success:
        console.print("[bold green]✅ Team collaboration complete![/bold green]")
        console.print(f"Implementation: {len(result.implementation.files)} files")
        console.print(f"Test Suite: {len(result.test_code.files)} files")
        
        # Save report logic could go here
    else:
        console.print(f"[bold red]❌ Collaboration failed: {result.error}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
