from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from backend.config_loader import config
from backend.searcher import search_papers
from backend.ranker import rank_papers
from backend.fetcher import fetch_paper
from backend.extractor import extract_text
from backend.multi_summarizer import summarize_multiple_papers
from backend.report_generator import generate_report_pdf

app = FastAPI(title="Paper Producer")

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

class GenerateRequest(BaseModel):
    topic: str
    llm_model: Optional[str] = None
    indexer_type: Optional[str] = None
    top_papers: Optional[int] = None

class ConfigUpdate(BaseModel):
    llm_model: Optional[str] = None
    indexer_type: Optional[str] = None
    embedding_model: Optional[str] = None
    top_papers: Optional[int] = None
    max_results: Optional[int] = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("frontend/templates/index.html", "r") as f:
        return f.read()

@app.get("/api/config")
async def get_config():
    return {
        "llm": config.data["llm"],
        "embeddings": config.data["embeddings"],
        "indexer": config.data["indexer"],
        "search": config.data["search"],
        "output": config.data["output"]
    }

@app.post("/api/config")
async def update_config(updates: ConfigUpdate):
    config_updates = {}
    
    if updates.llm_model:
        config_updates["llm"] = {"model": updates.llm_model}
    if updates.indexer_type:
        config_updates["indexer"] = {"type": updates.indexer_type}
    if updates.embedding_model:
        config_updates["embeddings"] = {"model": updates.embedding_model}
    if updates.top_papers:
        config_updates["search"] = {"top_papers": updates.top_papers}
    if updates.max_results:
        if "search" not in config_updates:
            config_updates["search"] = {}
        config_updates["search"]["max_results"] = updates.max_results
    
    config.update(config_updates)
    return {"status": "success", "config": config.data}

@app.post("/api/generate")
async def generate_report(request: GenerateRequest, background_tasks: BackgroundTasks):
    try:
        topic = request.topic
        
        if request.llm_model or request.indexer_type or request.top_papers:
            updates = {}
            if request.llm_model:
                updates["llm"] = {"model": request.llm_model}
            if request.indexer_type:
                updates["indexer"] = {"type": request.indexer_type}
            if request.top_papers:
                updates["search"] = {"top_papers": request.top_papers}
            config.update(updates)
        
        os.makedirs("data/papers", exist_ok=True)
        os.makedirs("data/outputs", exist_ok=True)
        
        papers = search_papers(topic)
        top_papers = rank_papers(papers, topic)
        
        papers_data = []
        for paper in top_papers:
            arxiv_id = paper['arxiv_id']
            pdf_path = fetch_paper(arxiv_id)
            text, metadata = extract_text(pdf_path)
            papers_data.append({
                'text': text,
                'metadata': metadata
            })
        
        report = summarize_multiple_papers(papers_data, topic)
        
        topic_slug = topic.replace(' ', '_')[:50]
        output_filename = f"{topic_slug}_report.pdf"
        output_path = f"data/outputs/{output_filename}"
        generate_report_pdf(report, top_papers, topic, output_path)
        
        return {
            "status": "success",
            "filename": output_filename,
            "papers": [{"title": p["title"], "arxiv_id": p["arxiv_id"]} for p in top_papers]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = f"data/outputs/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.get("/api/models")
async def get_models():
    return {
        "llm_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "indexer_types": ["vector", "bm25", "tfidf", "inverted"],
        "embedding_models": ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
    }
