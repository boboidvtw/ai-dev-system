from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.coordinator import TeamCoordinator
from agents.dev_agent import DevAgent
from agents.pipeline_models import PipelineResult
from tools.rag_engine import RAGEngine
from tools.github_tool import GitHubTool

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_server")

app = FastAPI(title="AI Engineer Dashboard")

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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/run")
async def run_task(req: TaskRequest):
    if active_task["status"] == "running":
        raise HTTPException(status_code=400, detail="A task is already running")
    
    # Run in background
    asyncio.create_task(execute_pipeline_task(req))
    return {"message": "Task started"}

async def execute_pipeline_task(req: TaskRequest):
    global active_task
    active_task = {
        "status": "running",
        "logs": ["Starting pipeline...", "Initializing RAG engine..."],
        "result": None
    }
    
    try:
        # Step 0: RAG
        rag = RAGEngine()
        active_task["logs"].append("Indexing repository...")
        rag.index_repo(".")
        context = rag.query(req.task)
        active_task["logs"].append("RAG indexing complete.")
        
        if req.use_multi_agent:
            active_task["logs"].append("Team Coordinator taking over (PM, Dev, QA)...")
            coordinator = TeamCoordinator()
            # We need to wrap the blocking calls or make them async
            # For this MVP, we run synchronously in the async task
            result = coordinator.run_collaborative_workflow(req.task, context=context)
        else:
            active_task["logs"].append("Single Dev Agent starting...")
            agent = DevAgent()
            result = agent.run_full_pipeline(req.task, context=context)
            
        active_task["result"] = result
        active_task["status"] = "success" if result.success else "failed"
        active_task["logs"].append("Pipeline complete!")
        
    except Exception as e:
        active_task["status"] = "error"
        active_task["logs"].append(f"ERROR: {str(e)}")
        logger.error(f"Pipeline error: {e}")

@app.get("/api/status")
async def get_status():
    return active_task

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
