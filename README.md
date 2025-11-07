# Paper Producer

RAG system for generating research reports from ArXiv papers.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your OpenAI API key.

## Usage

### Single Paper Summary
```bash
python main.py 2301.07041
```

### Multi-Paper Research Report
```bash
python main_multi.py "transformer models in NLP"
```

Output PDFs will be in `outputs/` directory.

## Architecture

**Single Paper Mode:**
- `main.py` → Entry point for single paper
- `fetcher.py` → Download paper from ArXiv
- `extractor.py` → Extract text from PDF
- `summarizer.py` → RAG-based summarization
- `generator.py` → Generate summary PDF

**Multi-Paper Mode:**
- `main_multi.py` → Entry point for multi-paper reports
- `searcher.py` → Search ArXiv by topic
- `ranker.py` → Rank papers by relevance using embeddings
- `multi_summarizer.py` → Multi-document RAG synthesis
- `report_generator.py` → Generate comprehensive report PDF
