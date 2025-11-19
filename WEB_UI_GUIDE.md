# Composer AI - Web UI

## ✅ Project Successfully Restructured!

### New Structure:
```
paper-producer/
├── app.py                    # FastAPI web server
├── frontend/                 # UI files
│   ├── templates/
│   │   └── index.html       # Main page
│   └── static/
│       ├── style.css        # Styling
│       └── app.js           # JavaScript
├── backend/                  # All backend logic
│   ├── config.yaml          # Configuration
│   ├── *.py                 # All Python modules
└── data/                     # Data storage
    ├── papers/              # Downloaded PDFs
    └── outputs/             # Generated reports
```

### How to Use:

**Start the Web UI:**
```bash
./start.sh
```
Or manually:
```bash
PYTHONPATH=/home/oem/code/paper-producer /home/oem/code/paper-producer/.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Access the UI:**
Open http://localhost:8000 in your browser

### Features:

✓ Clean, modern web interface
✓ Configure LLM model, indexer type, and search parameters via dropdowns
✓ Enter research topic and generate reports with one click
✓ Real-time status updates
✓ View source papers used in the report
✓ Download generated PDF directly from browser
✓ Separated frontend and backend architecture
✓ RESTful API for future integrations

### API Endpoints:

- `GET /` - Main UI page
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `POST /api/generate` - Generate report
- `GET /api/download/{filename}` - Download PDF
- `GET /api/models` - Get available models

The web server is now running on http://localhost:8000!
