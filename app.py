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

@app.post("/api/process-query")
async def process_query(request: dict):
    try:
        from backend.query_processor import process_user_query
        user_input = request.get("query", "")
        
        if not user_input:
            raise HTTPException(status_code=400, detail="Query is required")
        
        query_spec = process_user_query(user_input)
        return query_spec
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/generate-advanced")
async def generate_advanced_report(request: dict):
    try:
        from backend.query_processor import process_user_query
        
        user_query = request.get("user_query", "")
        if not user_query:
            raise HTTPException(status_code=400, detail="User query is required")
        
        # Apply runtime config updates if provided
        if request.get("llm_model"):
            config.update({"llm": {"model": request["llm_model"]}})
        if request.get("embedding_model"):
            config.update({"embeddings": {"model": request["embedding_model"]}})
        if request.get("indexer_type"):
            config.update({"indexer": {"type": request["indexer_type"]}})
        if request.get("top_papers"):
            config.update({"search": {"top_papers": request["top_papers"]}})
        
        query_spec = process_user_query(user_query)
        
        search_query = query_spec.get("search_query", user_query)
        
        os.makedirs("data/papers", exist_ok=True)
        os.makedirs("data/outputs", exist_ok=True)
        
        papers = search_papers(search_query)
        
        if not papers:
            raise HTTPException(status_code=404, detail=f"No papers found for query: {search_query}")
        
        # Get top_papers from config (which may have been updated above)
        top_n = config.get("search", "top_papers")
        top_papers = rank_papers(papers, search_query)[:top_n]
        
        # Return progress info including all papers and their status
        progress_info = {
            "total_papers": len(top_papers),
            "papers_list": [{"title": p["title"], "arxiv_id": p["arxiv_id"]} for p in top_papers]
        }
        
        papers_data = []
        errors = []
        processed_papers = []
        
        for idx, paper in enumerate(top_papers, 1):
            arxiv_id = paper['arxiv_id']
            try:
                pdf_path = fetch_paper(arxiv_id)
                text, metadata = extract_text(pdf_path)
                papers_data.append({
                    'text': text,
                    'metadata': metadata
                })
                processed_papers.append({
                    "index": idx,
                    "title": paper["title"],
                    "arxiv_id": arxiv_id,
                    "status": "success"
                })
            except Exception as e:
                error_msg = f"Failed to process {arxiv_id}: {str(e)}"
                errors.append(error_msg)
                processed_papers.append({
                    "index": idx,
                    "title": paper["title"],
                    "arxiv_id": arxiv_id,
                    "status": "error",
                    "error": str(e)
                })
                continue
        
        if not papers_data:
            raise HTTPException(status_code=500, detail=f"Failed to fetch any papers. Errors: {'; '.join(errors)}")
        
        report = summarize_multiple_papers(papers_data, search_query, query_spec)
        
        topic_slug = search_query.replace(' ', '_')[:50]
        output_filename = f"{topic_slug}_report.pdf"
        output_path = f"data/outputs/{output_filename}"
        generate_report_pdf(report, top_papers, search_query, output_path)
        
        # Create a text preview by removing LaTeX commands
        import re
        preview = report
        preview = re.sub(r'\\begin\{abstract\}', '', preview)
        preview = re.sub(r'\\end\{abstract\}', '', preview)
        preview = re.sub(r'\\section\{([^}]+)\}', r'\n\n═══ \1 ═══\n', preview)
        preview = re.sub(r'\\subsection\{([^}]+)\}', r'\n── \1 ──\n', preview)
        preview = re.sub(r'\\cite\{([^}]+)\}', r'[\1]', preview)
        preview = re.sub(r'\\textbf\{([^}]+)\}', r'\1', preview)
        preview = re.sub(r'\\textit\{([^}]+)\}', r'\1', preview)
        preview = re.sub(r'\\[a-zA-Z]+\{([^}]+)\}', r'\1', preview)
        preview = re.sub(r'\\[a-zA-Z]+', '', preview)
        preview = preview.strip()
        
        return {
            "status": "success",
            "filename": output_filename,
            "papers": [{"title": p["title"], "arxiv_id": p["arxiv_id"]} for p in top_papers],
            "processed_papers": processed_papers,
            "query_spec": query_spec,
            "report_preview": preview[:8000],  # Limit preview size
            "warnings": errors if errors else None,
            "progress_info": progress_info
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        detail = f"{str(e)}\n\nTraceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=detail)

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
