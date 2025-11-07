# Paper Producer

RAG system for generating research reports from ArXiv papers with a clean web UI.

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
