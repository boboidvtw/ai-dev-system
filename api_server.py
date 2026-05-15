import asyncio
import json
import logging
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.coordinator import TeamCoordinator
from agents.dev_agent import DevAgent
from agents.pipeline_models import PipelineResult
from tools.rag_engine import RAGEngine
from tools.github_tool import GitHubTool
from tools.file_manager import write_file, backup_file
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_server")

app = FastAPI(title="AI Engineer Dashboard")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for active task
active_task = {
    "status": "idle",
    "logs": [],
    "result": None
}

class TaskRequest(BaseModel):
    task: str
    target_file: str
    use_multi_agent: bool = True

@app.get("/api/issues")
async def get_issues():
    try:
        gh = GitHubTool()
        return gh.list_open_issues()
    except Exception as e:
        logger.error(f"Failed to fetch issues: {e}")
        return []

@app.post("/api/run")
async def run_task(req: TaskRequest):
    if active_task["status"] == "running":
        raise HTTPException(status_code=400, detail="A task is already running")
    
    # Run in background without blocking the main event loop
    asyncio.create_task(run_pipeline_in_thread(req))
    return {"message": "Task started"}

def sync_execute_pipeline(req: TaskRequest):
    """Heavy synchronous pipeline logic."""
    global active_task
    try:
        # Step 0: RAG
        rag = RAGEngine()
        active_task["logs"].append("Indexing repository (RAG)...")
        rag.index_repo(".")
        context = rag.query(req.task)
        active_task["logs"].append("RAG context retrieved.")
        
        if req.use_multi_agent:
            active_task["logs"].append("Team Coordinator active (PM/Dev/QA)...")
            coordinator = TeamCoordinator()
            result = coordinator.run_collaborative_workflow(req.task, context=context)
        else:
            active_task["logs"].append("Single Dev Agent active...")
            agent = DevAgent()
            result = agent.run_full_pipeline(req.task, context=context)
            
        active_task["result"] = result
        active_task["status"] = "success" if result.success else "failed"

        # --- Save files to disk ---
        if result.success:
            active_task["logs"].append("Saving generated files to disk...")
            for f in result.implementation.files:
                # Use user-specified path if the agent returned 'output.py'
                target_path = req.target_file if f.path == "output.py" else f.path
                if Path(target_path).exists():
                    backup_file(target_path)
                write_file(target_path, f.content)
                active_task["logs"].append(f"Saved implementation: {target_path}")

            for f in result.test_code.files:
                write_file(f.path, f.content)
                active_task["logs"].append(f"Saved test suite: {f.path}")

        active_task["logs"].append(f"Pipeline finished with status: {active_task['status']}")
        
    except Exception as e:
        active_task["status"] = "error"
        active_task["logs"].append(f"SYSTEM ERROR: {str(e)}")
        logger.error(f"Critical error in pipeline thread: {e}")

async def run_pipeline_in_thread(req: TaskRequest):
    global active_task
    active_task = {
        "status": "running",
        "logs": [f"Task received: {req.task}"],
        "result": None
    }
    # Run the heavy synchronous pipeline in a separate thread
    await asyncio.to_thread(sync_execute_pipeline, req)

@app.get("/api/status")
async def get_status():
    return active_task

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
