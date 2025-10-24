#!/usr/bin/env python3
"""
RAG Server - Retrieval-Augmented Generation Server
Author: AI Assistant
Created: 2025-10-24T16:26:57
Purpose: Provide RAG capabilities via HTTP API
"""

import os
import sys
import time
import hashlib
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add the essence-of-AI-engineering to Python path
sys.path.insert(0, '/林生的奇思妙想/essence-of-AI-engineering')

from rag.rag_base.chunk_tool import IterChunks
from rag.rag_base.rag_core import prepare_data, build_prompt, call_llm
from rag.rag_base.rag_base import embed_chunk, summarize_chunk
from rag.rag_base.db_tool import DBClient
from rag.rag_base.log_tool import logger

# Server configuration
BIRTH_TIME = "2025-10-24T16:26:57"
PORT = 8010
HOST = "0.0.0.0"
DATABASE_PATH = "/林生的奇思妙想/rag/rag_database"

# Initialize FastAPI app
app = FastAPI(
    title="RAG Server",
    description="Retrieval-Augmented Generation Server",
    version="1.0.0"
)

# Global variables
db_client = None

class DataPreparationRequest(BaseModel):
    file_path: str
    db_name: str
    chunk_size: int = 1000
    separators: Optional[List[str]] = None
    enable_abstract: bool = True

class QueryRequest(BaseModel):
    question: str
    db_name: str
    raw_top_k: int = 5
    abstract_top_k: int = 50
    enable_abstract: bool = True

class EmbeddingRequest(BaseModel):
    text: str

class SummaryRequest(BaseModel):
    text: str
    model_name: str = "eboafour1/bertsum"
    ratio: float = 0.3

class HealthResponse(BaseModel):
    status: str
    birth_time: str
    uptime: float

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    text_length: int

class SummaryResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float

class QueryResponse(BaseModel):
    answer: str
    raw_results_count: int
    abstract_results_count: int
    prompt_length: int
    estimated_tokens: int
    processing_time: Dict[str, float]

@app.on_event("startup")
async def startup_event():
    """Initialize database client on startup"""
    global db_client
    try:
        db_client = DBClient({"protocol": "file", "path": DATABASE_PATH})
        logger.info(f"RAG Server started at {BIRTH_TIME}")
        logger.info(f"Database initialized at {DATABASE_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "RAG Server is running", "birth_time": BIRTH_TIME}

@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    current_time = datetime.now()
    birth_time = datetime.fromisoformat(BIRTH_TIME)
    uptime = (current_time - birth_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        birth_time=BIRTH_TIME,
        uptime=round(uptime, 3)
    )

@app.post("/embedding")
async def get_embedding(request: EmbeddingRequest) -> EmbeddingResponse:
    """Get embedding for text"""
    start_time = time.time()
    
    try:
        embedding = embed_chunk(request.text)
        processing_time = time.time() - start_time
        
        logger.info(f"Embedding generated: text_length={len(request.text)}, time={processing_time:.3f}s")
        
        return EmbeddingResponse(
            embedding=embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
            text_length=len(request.text)
        )
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

@app.post("/summarize")
async def summarize_text(request: SummaryRequest) -> SummaryResponse:
    """Summarize text"""
    start_time = time.time()
    
    try:
        summary = summarize_chunk(request.text, request.model_name, ratio=request.ratio)
        processing_time = time.time() - start_time
        
        original_length = len(request.text)
        summary_length = len(summary)
        compression_ratio = summary_length / original_length if original_length > 0 else 0
        
        logger.info(f"Summary generated: original={original_length}, summary={summary_length}, ratio={compression_ratio:.3f}, time={processing_time:.3f}s")
        
        return SummaryResponse(
            summary=summary,
            original_length=original_length,
            summary_length=summary_length,
            compression_ratio=round(compression_ratio, 3)
        )
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@app.post("/prepare_data")
async def prepare_data_endpoint(request: DataPreparationRequest):
    """Prepare data for RAG"""
    start_time = time.time()
    
    try:
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        result = prepare_data(
            file_path=request.file_path,
            db_name=request.db_name,
            chunk_size=request.chunk_size,
            separators=request.separators,
            enable_abstract=request.enable_abstract,
            db_client=db_client
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Data preparation completed: {result}, time={processing_time:.3f}s")
        
        return {
            "status": "success",
            "chunk_count": result["chunk_count"],
            "processing_time": round(processing_time, 3)
        }
    except Exception as e:
        logger.error(f"Data preparation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Data preparation failed: {str(e)}")

@app.post("/query")
async def query_rag(request: QueryRequest) -> QueryResponse:
    """Query RAG system"""
    start_time = time.time()
    processing_times = {}
    
    try:
        # Step 1: Embed question
        step_start = time.time()
        question_embedding = embed_chunk(request.question)
        processing_times["embedding"] = time.time() - step_start
        
        # Step 2: Retrieve from vector database
        step_start = time.time()
        raw_collection = f"{request.db_name}_raw"
        abstract_collection = f"{request.db_name}_abstract"
        
        # Retrieve raw chunks
        raw_results = db_client.get_collection(raw_collection).query(
            query_embeddings=[question_embedding],
            n_results=request.raw_top_k
        )
        
        raw_documents = raw_results['documents'][0] if raw_results['documents'] else []
        raw_distances = raw_results['distances'][0] if raw_results['distances'] else []
        
        # Retrieve abstract chunks if enabled
        abstract_documents = []
        abstract_distances = []
        
        if request.enable_abstract:
            abstract_results = db_client.get_collection(abstract_collection).query(
                query_embeddings=[question_embedding],
                n_results=request.abstract_top_k
            )
            abstract_documents = abstract_results['documents'][0] if abstract_results['documents'] else []
            abstract_distances = abstract_results['distances'][0] if abstract_results['distances'] else []
        
        processing_times["retrieval"] = time.time() - step_start
        
        # Step 3: Build prompt
        step_start = time.time()
        raw_pairs = list(zip(raw_documents, raw_distances))
        abstract_pairs = list(zip(abstract_documents, abstract_distances))
        
        prompt = build_prompt(request.question, raw_pairs, abstract_pairs)
        processing_times["prompt_building"] = time.time() - step_start
        
        # Step 4: Call LLM
        step_start = time.time()
        answer = call_llm(prompt)
        processing_times["llm_generation"] = time.time() - step_start
        
        # Calculate total time
        processing_times["total"] = time.time() - start_time
        
        # Round all times to 3 decimal places
        for key in processing_times:
            processing_times[key] = round(processing_times[key], 3)
        
        # Estimate token count (rough estimation: 1 token ≈ 4 characters for Chinese)
        estimated_tokens = len(prompt) // 4
        
        logger.info(f"Query processed: question_length={len(request.question)}, prompt_length={len(prompt)}, tokens={estimated_tokens}, time={processing_times['total']}s")
        
        return QueryResponse(
            answer=answer,
            raw_results_count=len(raw_documents),
            abstract_results_count=len(abstract_documents),
            prompt_length=len(prompt),
            estimated_tokens=estimated_tokens,
            processing_time=processing_times
        )
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/shutdown")
async def shutdown():
    """Shutdown the server"""
    logger.info("Shutdown request received")
    
    # In a real implementation, you would use a more graceful shutdown method
    # For now, we'll just log and return a message
    return {"message": "Server shutdown initiated", "status": "shutting_down"}

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")