from __future__ import annotations

"""
AI Dev System — Multi-Agent CLI

Usage:
  python3 main_multi.py "Task description" target_file.py
"""

import argparse
import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from agents.coordinator import TeamCoordinator
from tools.rag_engine import RAGEngine
from tools.file_manager import write_file, backup_file
from config import cfg

console = Console()
logger = logging.getLogger(__name__)

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

    # --- Step 0: RAG Context ---
    rag_context = ""
    try:
        with console.status("[bold magenta]🧠 Team indexing repository (RAG)..."):
            rag = RAGEngine()
            rag.index_repo(".")
            rag_context = rag.query(args.task)
    except Exception as e:
        logger.warning(f"RAG failed: {e}")

    coordinator = TeamCoordinator()
    result = coordinator.run_collaborative_workflow(args.task, context=rag_context)

    if result.success:
        console.print("[bold green]✅ Team collaboration complete![/bold green]")
        
        # --- Write files ---
        for f in result.implementation.files:
            # Handle default path
            if f.path == "output.py":
                f.path = args.file
            
            if Path(f.path).exists():
                backup_file(f.path)
            write_file(f.path, f.content)
            console.print(f"  [green]✅ Written Implementation: {f.path}[/green]")

        for f in result.test_code.files:
            write_file(f.path, f.content)
            console.print(f"  [green]✅ Written QA Tests: {f.path}[/green]")
            
    else:
        console.print(f"[bold red]❌ Collaboration failed: {result.error}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
