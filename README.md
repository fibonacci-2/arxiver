# Paper Producer 📄

**Advanced RAG system for generating comprehensive research reports from ArXiv papers with an intelligent web interface.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 Features

### Core Capabilities
- **🤖 Two-Level Query Processing**: Natural language input → LLM analyzes requirements → Optimized ArXiv search
- **🔍 Multi-Paper Synthesis**: Retrieval-Augmented Generation across 20+ papers simultaneously
- **📊 4 Indexer Options**: Vector (semantic), BM25 (probabilistic), TF-IDF (statistical), Inverted (keyword)
- **📑 Academic LaTeX Output**: Professional reports with citations, bibliography, and abstract
- **🎨 Clean Web UI**: Three-column layout with real-time progress tracking and PDF preview
- **⚙️ Configurable Pipeline**: YAML-based configuration with runtime parameter override

### Advanced Features
- **Smart Paper Ranking**: Embedding-based relevance scoring
- **Incremental Progress Display**: Real-time paper fetching and processing logs
- **Graceful Error Handling**: Continues on individual paper failures
- **Citation Management**: Automatic `\cite{}` insertion and bibliography generation
- **ArXiv ID Normalization**: Handles all formats (versioned, categorized, modern)

---

## 📐 System Overview

![System Architecture](system-overview.pdf)

[📄 View Full System Overview (PDF)](./system-overview.pdf)

### Pipeline Flow

```
User Query (Natural Language)
    ↓
[1. Query Processor] → LLM analyzes → Structured JSON spec
    ↓
[2. Searcher] → ArXiv API → Papers with metadata
    ↓
[2. Ranker] → Embedding similarity → Top 20 papers
    ↓
[3. Fetcher] → Download PDFs → Local storage
    ↓
[3. Extractor] → PyPDF2 → Full text + metadata
    ↓
[4. Indexer] → Chunk + Index → Retrieval database
    ↓
[4. RAG Retrieval] → Top 10 relevant chunks → LLM context
    ↓
[4. Synthesizer] → LLM generation → LaTeX report
    ↓
[5. Report Generator] → pdflatex → Final PDF
    ↓
Preview + Download
```

**Configuration drives all stages:**
```yaml
embeddings: text-embedding-3-small
indexer: vector/bm25/tfidf/inverted
llm: gpt-4o-mini (temp: 0)
search: max=10, top_papers=20
chunks: size=1000, overlap=200
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key
- LaTeX distribution (for PDF compilation)

### Installation

```bash
# Clone repository
git clone https://github.com/fibonacci-2/arxiver.git
cd arxiver

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Install LaTeX (for PDF generation)

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra
```

**macOS:**
```bash
brew install --cask mactex
```

**Windows:**
Download and install [MiKTeX](https://miktex.org/download)

### Run the Application

```bash
# Start the web server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience script
./start.sh
```

Open **http://localhost:8000** in your browser.

---

## 🎮 Usage

### Web UI (Recommended)

1. **Enter your research requirements** in natural language:
   ```
   "Find recent papers on transformer attention mechanisms, 
   focusing on efficiency improvements and architectural innovations"
   ```

2. **Click "Analyze Query"**: LLM processes your request and shows structured query spec

3. **Click "Generate Report"**: 
   - Searches ArXiv
   - Ranks papers by relevance
   - Downloads and extracts content
   - Generates comprehensive report with citations

4. **Preview and Download**: View report in browser or download PDF

### Configuration Options (Web UI)

- **LLM Model**: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`
- **Indexer Type**: 
  - `vector` - Semantic search (ChromaDB + embeddings)
  - `bm25` - Probabilistic ranking (best for keywords)
  - `tfidf` - Statistical term weighting (fast, local)
  - `inverted` - Classic keyword index
- **Embedding Model**: `text-embedding-3-small`, `text-embedding-3-large`
- **Papers to Fetch**: 10-50 papers (default: 20)

---

## ⚙️ Configuration

### Main Config File: `backend/config.yaml`

```yaml
embeddings:
  model: text-embedding-3-small  # or text-embedding-3-large

indexer:
  type: vector                   # vector, bm25, tfidf, inverted
  chunk_size: 1000               # Characters per chunk
  chunk_overlap: 200             # Overlap between chunks
  top_k: 10                      # Chunks to retrieve for LLM context

llm:
  model: gpt-4o-mini             # gpt-4o-mini, gpt-4o, gpt-4-turbo
  temperature: 0                 # 0 = deterministic, 0.7 for query processing

search:
  max_results: 10                # Initial ArXiv search results
  top_papers: 20                 # Papers to process after ranking

output:
  format: latex                  # Output format
```

### Indexer Comparison

| Indexer | Speed | Semantic | Cost | Best For |
|---------|-------|----------|------|----------|
| **vector** | Slow | ✅ Yes | $$ (API) | Natural language queries |
| **bm25** | Fast | ❌ No | Free | Keyword searches |
| **tfidf** | Very Fast | ❌ No | Free | Technical terms, large collections |
| **inverted** | Fastest | ❌ No | Free | Exact term matching |

### Environment Variables: `.env`

```bash
OPENAI_API_KEY=sk-...        # Required: Your OpenAI API key
```

---

## 📁 Project Structure

```
paper-producer/
├── app.py                       # FastAPI application & REST API
│
├── frontend/                    # Web UI (Vanilla JS)
│   ├── templates/
│   │   └── index.html          # Three-column layout
│   └── static/
│       ├── style.css           # Minimal GitHub-inspired design
│       └── app.js              # State management & API calls
│
├── backend/                     # Core RAG pipeline
│   ├── config.yaml             # System configuration
│   ├── config_loader.py        # Singleton config manager
│   │
│   ├── query_processor.py      # LLM query analysis
│   ├── searcher.py             # ArXiv API client
│   ├── ranker.py               # Embedding-based paper ranking
│   │
│   ├── fetcher.py              # PDF download from ArXiv
│   ├── extractor.py            # Text extraction (PyPDF2)
│   │
│   ├── indexers.py             # 4 indexer implementations
│   │   ├── VectorIndexer       # ChromaDB + OpenAI embeddings
│   │   ├── BM25Indexer         # Okapi BM25 ranking
│   │   ├── TFIDFIndexer        # scikit-learn TF-IDF
│   │   └── InvertedIndexer     # Classic inverted index
│   │
│   ├── multi_summarizer.py     # Multi-paper RAG synthesis
│   ├── report_generator.py     # LaTeX compilation (pdflatex)
│   │
│   └── logger.py               # Rich console logging
│
├── data/                        # Generated data (gitignored)
│   ├── papers/                 # Downloaded ArXiv PDFs
│   └── reports/                # Generated report PDFs
│
├── chroma_db_multi/            # ChromaDB vector store (if using vector indexer)
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── start.sh                   # Convenience startup script
└── system-overview.pdf        # Architecture documentation
```

---

## 🔧 API Endpoints

### REST API (FastAPI)

```
GET  /                          Serve web UI
GET  /api/config                Get current configuration
POST /api/config                Update configuration
POST /api/process-query         Analyze user query with LLM
POST /api/generate-advanced     Generate multi-paper report
GET  /api/download/{filename}   Download generated PDF
```

### Example: Process Query

```bash
curl -X POST http://localhost:8000/api/process-query \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Find papers about BERT fine-tuning"}'

# Returns:
{
  "search_query": "BERT fine-tuning transfer learning",
  "themes": ["pre-training", "downstream tasks", "hyperparameters"],
  "structure": ["Introduction", "Methodology", "Results"],
  "special_requirements": "Focus on NLP tasks"
}
```

---

## 🧠 How It Works

### Stage 1: Query Intelligence
- User provides natural language requirements
- LLM (gpt-4o-mini, temp=0.7) extracts:
  - Optimized ArXiv search query
  - Research themes to emphasize
  - Report structure
  - Special requirements

### Stage 2: Paper Discovery
- **Search**: ArXiv API with optimized query
- **Rank**: Cosine similarity between query embedding and paper abstracts
- **Select**: Top N papers (configurable, default 20)

### Stage 3: Content Acquisition
- **Fetch**: Download PDFs from ArXiv (parallel with error tracking)
- **Extract**: PyPDF2 extracts text + preserves metadata

### Stage 4: RAG Processing
- **Index**: Text split into chunks (1000 chars, 200 overlap)
- **Retrieve**: Top 10 most relevant chunks across all papers
- **Synthesize**: LLM generates LaTeX report with:
  - Abstract (150-200 words)
  - Structured sections
  - `\cite{paperN}` citations throughout
  - Focus on user-specified themes

### Stage 5: Report Generation
- Wraps content in LaTeX document structure
- Generates `\begin{thebibliography}` with `\bibitem` entries
- Compiles with pdflatex (runs twice for citation resolution)
- Returns PDF + preview text

---

## 🎨 UI Features

- **Three-Column Layout**:
  - Left: Configuration & query input
  - Middle: Papers list & progress logs
  - Right: Report preview with PDF tools
  
- **State Management**:
  - Single button: "Analyze Query" → "Generate Report" → "New Query"
  - Auto-reset on query text change
  
- **Real-Time Updates**:
  - Incremental paper display (100ms fade-in)
  - Detailed progress logging
  - Status indicators

- **Minimal Design System**:
  - GitHub-inspired color palette
  - Consistent 1px borders, 4px radius
  - Clean typography (0.875rem base)

---

## 🛠️ Development

### Run in Development Mode

```bash
uvicorn app:app --reload --log-level debug
```

### Project Dependencies

```
fastapi              # Web framework
uvicorn              # ASGI server
langchain            # LLM orchestration
langchain-openai     # OpenAI integration
langchain-community  # ChromaDB integration
chromadb             # Vector database
openai               # OpenAI API client
arxiv                # ArXiv API client
pypdf2               # PDF text extraction
scikit-learn         # TF-IDF vectorization
rank-bm25            # BM25 implementation
pyyaml               # Config management
python-dotenv        # Environment variables
rich                 # Console logging
```

---

## 📝 Examples

### Example Query Inputs

```
"Analyze recent developments in multi-modal transformers 
 with emphasis on vision-language models"

"Find papers about federated learning privacy techniques, 
 comparing differential privacy approaches"

"Survey of graph neural networks for molecular property prediction, 
 focusing on pharmaceutical applications"
```

### Example Output Structure

```latex
\begin{abstract}
This report synthesizes findings from 20 recent papers...
\end{abstract}

\section{Introduction}
Transformers have revolutionized NLP \cite{paper1}...

\section{Methodology Comparison}
Self-attention mechanisms \cite{paper1,paper3} differ from...

\begin{thebibliography}{99}
\bibitem{paper1} Vaswani et al., "Attention Is All You Need", arXiv:1706.03762
\bibitem{paper2} Devlin et al., "BERT: Pre-training...", arXiv:1810.04805
...
\end{thebibliography}
```

---

## 🐛 Troubleshooting

**LaTeX compilation fails:**
```bash
# Ensure LaTeX is installed
pdflatex --version

# Check logs in data/reports/
```

**ChromaDB errors (vector indexer):**
```bash
# Clear database and rebuild
rm -rf chroma_db_multi/
```

**OpenAI API rate limits:**
- Reduce `top_papers` in config
- Use `tfidf` or `bm25` indexer (no embedding API calls)

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

## 📧 Contact

Project maintained by [fibonacci-2](https://github.com/fibonacci-2)

Repository: [arxiver](https://github.com/fibonacci-2/arxiver)

