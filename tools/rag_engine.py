from __future__ import annotations

"""
RAG Engine — Semantic Code Retrieval
Indexes the codebase and provides relevant context for engineering tasks.
"""

import logging
import os
from typing import Any

import litellm
import chromadb
from chromadb.utils import embedding_functions
from config import cfg

logger = logging.getLogger(__name__)

class LiteLLMEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """Custom embedding function using litellm."""
    def __init__(self, model_name: str):
        self.model_name = model_name

    def __call__(self, input: list[str]) -> list[list[float]]:
        # litellm.embedding returns data in a structured way
        response = litellm.embedding(model=self.model_name, input=input)
        return [item["embedding"] for item in response.data]

class RAGEngine:
    def __init__(self, persist_directory: str = ".rag_cache"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = LiteLLMEmbeddingFunction(cfg.embedding_model)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="codebase",
            embedding_function=self.embedding_fn
        )
        logger.info(f"RAG Engine initialized. Storage: {persist_directory}")

    def index_repo(self, root_dir: str):
        """Scans the repository and adds files to the vector store."""
        logger.info(f"Indexing repository at {root_dir}...")
        
        documents = []
        metadatas = []
        ids = []

        # List of file extensions to include
        include_ext = {".py", ".js", ".ts", ".txt", ".md", ".json", ".yaml"}
        # List of directories to ignore
        exclude_dirs = {".git", "__pycache__", ".rag_cache", "venv", ".venv", "node_modules", "workspace"}

        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in include_ext):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, root_dir)
                    
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if not content.strip():
                                continue
                            
                            # Simple chunking logic: for now, one file = one doc
                            # In a real app, we'd split large files into chunks
                            documents.append(content)
                            metadatas.append({"path": rel_path})
                            ids.append(rel_path)
                    except Exception as e:
                        logger.warning(f"Could not index {rel_path}: {e}")

        if ids:
            # upsert so we update existing files
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(ids)} files.")

    def query(self, task: str, top_k: int = 5) -> str:
        """Retrieves relevant code snippets for a task."""
        logger.info(f"Querying RAG for: {task[:50]}...")
        
        results = self.collection.query(
            query_texts=[task],
            n_results=top_k
        )
        
        context_parts = ["### Relevant Code Context from Repository ###"]
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            context_parts.append(f"--- File: {meta['path']} ---\n{doc}")
            
        return "\n\n".join(context_parts)
