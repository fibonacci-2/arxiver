# Paper Producer

RAG system for generating research reports from ArXiv papers with a clean web UI.

# System Overview
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INPUT                                  │
│                  "Find papers about transformers..."                 │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1: QUERY INTELLIGENCE (query_processor.py)                   │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  LLM (gpt-4o-mini, temp=0.7)                           │         │
│  │  → Extracts: search_query, themes, structure           │         │
│  └────────────────────────────────────────────────────────┘         │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ query_spec (JSON)
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 2: PAPER DISCOVERY                                           │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  2a. SEARCH (searcher.py)                              │         │
│  │      ArXiv API → 10 papers                             │         │
│  └────────────────────┬───────────────────────────────────┘         │
│                       │ papers with metadata                        │
│                       ↓                                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  2b. RANK (ranker.py)                                  │         │
│  │      Embeddings + Cosine Similarity → Top 20 papers    │         │
│  └────────────────────────────────────────────────────────┘         │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ ranked_papers[]
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 3: CONTENT ACQUISITION (Loop for each paper)                 │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  3a. FETCH (fetcher.py)                                │         │
│  │      Download PDF → data/papers/                       │         │
│  └────────────────────┬───────────────────────────────────┘         │
│                       │ pdf_path                                    │
│                       ↓                                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  3b. EXTRACT (extractor.py)                            │         │
│  │      PyPDF2 → full_text + metadata                     │         │
│  └────────────────────────────────────────────────────────┘         │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ papers_data[]
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 4: RAG PROCESSING                                            │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  4a. INDEX (indexers.py)                               │         │
│  │      Text Splitter (1000/200) → Chunks                 │         │
│  │      ┌──────────────────────────────────────┐          │         │
│  │      │ TF-IDF / BM25 / Vector / Inverted    │          │         │
│  │      └──────────────────────────────────────┘          │         │
│  └────────────────────┬───────────────────────────────────┘         │
│                       │ indexed chunks                              │
│                       ↓                                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  4b. RETRIEVE                                           │         │
│  │      Query → Top 10 relevant chunks                    │         │
│  └────────────────────┬───────────────────────────────────┘         │
│                       │ context                                     │
│                       ↓                                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  4c. SYNTHESIZE (multi_summarizer.py)                  │         │
│  │      LLM (gpt-4o-mini, temp=0)                         │         │
│  │      Context + Query Spec → LaTeX + \cite{}            │         │
│  └────────────────────────────────────────────────────────┘         │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ latex_content
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 5: REPORT GENERATION (report_generator.py)                   │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  LaTeX Wrapper + Bibliography                          │         │
│  │  → pdflatex (2x) → PDF                                 │         │
│  └────────────────────────────────────────────────────────┘         │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ report.pdf
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      OUTPUT                                          │
│  Preview Panel (LaTeX → Text) + Download Button                     │
└─────────────────────────────────────────────────────────────────────┘


CONFIG (config.yaml) ──→ All Stages
         ↓
    - LLM: gpt-4o-mini
    - Embeddings: text-embedding-3-small  
    - Indexer: tfidf
    - Search: max=10, top_papers=20
    - Chunks: size=1000, overlap=200
    
## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your OpenAI API key.

Install LaTeX for PDF generation:
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra
```

## Usage

### Web UI (Recommended)
```bash
uvicorn app:app --reload
```
Open http://localhost:8000 in your browser.

### Command Line

**Single Paper Summary:**
```bash
python main.py 2301.07041
```

**Multi-Paper Research Report:**
```bash
python main_multi.py "transformer models in NLP"
```

Output PDFs will be in `data/outputs/` directory.

## Project Structure

```
paper-producer/
├── app.py                    # FastAPI web application
├── frontend/
│   ├── templates/
│   │   └── index.html       # Main UI page
│   └── static/
│       ├── style.css        # Styling
│       └── app.js           # Frontend logic
├── backend/
│   ├── config.yaml          # Configuration
│   ├── config_loader.py     # Config management
│   ├── searcher.py          # ArXiv search
│   ├── ranker.py            # Paper ranking
│   ├── fetcher.py           # PDF download
│   ├── extractor.py         # Text extraction
│   ├── summarizer.py        # Single paper RAG
│   ├── multi_summarizer.py  # Multi-paper RAG
│   ├── generator.py         # PDF generation
│   ├── report_generator.py  # LaTeX report generation
│   ├── indexers.py          # Vector/BM25/TF-IDF/Inverted
│   └── logger.py            # Pretty logging
├── data/
│   ├── papers/              # Downloaded PDFs
│   └── outputs/             # Generated reports
└── main.py / main_multi.py  # CLI entry points
```

## Configuration

Edit `backend/config.yaml` or use the web UI:

- **LLM Model**: gpt-4o-mini, gpt-4o, gpt-4-turbo
- **Indexer**: vector, bm25, tfidf, inverted
- **Embedding Model**: text-embedding-3-small, text-embedding-3-large
- **Search Parameters**: max_results, top_papers

