let currentFilename = null;
let currentQuerySpec = null;
let currentMode = 'simple';

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        document.getElementById('llm-model').value = config.llm.model;
        document.getElementById('indexer-type').value = config.indexer.type;
        document.getElementById('top-papers').value = config.search.top_papers;
    } catch (error) {
        showStatus('Failed to load configuration', 'error');
    }
}

async function saveConfig() {
    try {
        const config = {
            llm_model: document.getElementById('llm-model').value,
            indexer_type: document.getElementById('indexer-type').value,
            top_papers: parseInt(document.getElementById('top-papers').value)
        };
        
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            showStatus('Configuration saved successfully', 'success');
        } else {
            showStatus('Failed to save configuration', 'error');
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    }
}

async function generateReport() {
    const topic = document.getElementById('topic').value.trim();
    
    if (!topic) {
        showStatus('Please enter a research topic', 'error');
        return;
    }
    
    const generateBtn = document.getElementById('generate-btn');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner"></span> Generating...';
    
    showStatus('Searching and processing papers...', 'info');
    document.getElementById('results').classList.add('hidden');
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                llm_model: document.getElementById('llm-model').value,
                indexer_type: document.getElementById('indexer-type').value,
                top_papers: parseInt(document.getElementById('top-papers').value)
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentFilename = data.filename;
            displayResults(data.papers);
            showStatus('Report generated successfully!', 'success');
        } else {
            showStatus('Error: ' + data.detail, 'error');
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = 'Generate Report';
    }
}

function displayResults(papers) {
    const papersList = document.getElementById('papers-list');
    papersList.innerHTML = '<h3 style="margin-bottom: 1rem; color: #667eea;">Source Papers:</h3>';
    
    papers.forEach((paper, index) => {
        const paperDiv = document.createElement('div');
        paperDiv.className = 'paper-item';
        paperDiv.innerHTML = `
            <div class="paper-title">${index + 1}. ${paper.title}</div>
            <div class="paper-id">arXiv:${paper.arxiv_id}</div>
        `;
        papersList.appendChild(paperDiv);
    });
    
    document.getElementById('results').classList.remove('hidden');
}

function downloadReport() {
    if (currentFilename) {
        window.location.href = `/api/download/${currentFilename}`;
    }
}

function showStatus(message, type) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status ${type}`;
    status.classList.remove('hidden');
    
    if (type === 'success') {
        setTimeout(() => {
            status.classList.add('hidden');
        }, 5000);
    }
}

async function processQuery() {
    const query = document.getElementById('advanced-query').value.trim();
    
    if (!query) {
        showStatus('Please enter your requirements', 'error');
        return;
    }
    
    const processBtn = document.getElementById('process-query-btn');
    processBtn.disabled = true;
    processBtn.innerHTML = '<span class="spinner"></span> Processing...';
    
    try {
        const response = await fetch('/api/process-query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentQuerySpec = data;
            displayQuerySpec(data);
            document.getElementById('generate-advanced-btn').classList.remove('hidden');
            showStatus('Query processed successfully!', 'success');
        } else {
            showStatus('Error: ' + data.detail, 'error');
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    } finally {
        processBtn.disabled = false;
        processBtn.innerHTML = 'Process Query';
    }
}

function displayQuerySpec(spec) {
    const querySpecDiv = document.getElementById('query-spec');
    querySpecDiv.innerHTML = `
        <h3>📋 Processed Query Specification</h3>
        <div class="spec-item">
            <div class="spec-label">Search Query:</div>
            <div class="spec-value">${spec.search_query}</div>
        </div>
        <div class="spec-item">
            <div class="spec-label">Themes to Emphasize:</div>
            <ul>${spec.themes.map(t => `<li>${t}</li>`).join('')}</ul>
        </div>
        <div class="spec-item">
            <div class="spec-label">Report Structure:</div>
            <ul>${spec.structure.map(s => `<li>${s}</li>`).join('')}</ul>
        </div>
        ${spec.special_requirements ? `
        <div class="spec-item">
            <div class="spec-label">Special Requirements:</div>
            <div class="spec-value">${spec.special_requirements}</div>
        </div>` : ''}
    `;
    querySpecDiv.classList.remove('hidden');
}

async function generateAdvancedReport() {
    if (!currentQuerySpec) {
        showStatus('Please process your query first', 'error');
        return;
    }
    
    const generateBtn = document.getElementById('generate-advanced-btn');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner"></span> Generating...';
    
    showStatus('Searching and processing papers...', 'info');
    document.getElementById('results').classList.add('hidden');
    
    try {
        const response = await fetch('/api/generate-advanced', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_query: document.getElementById('advanced-query').value
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentFilename = data.filename;
            displayResults(data.papers);
            showStatus('Report generated successfully!', 'success');
        } else {
            showStatus('Error: ' + data.detail, 'error');
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = 'Generate Report';
    }
}

function switchMode(mode) {
    currentMode = mode;
    
    document.getElementById('simple-mode-btn').classList.toggle('active', mode === 'simple');
    document.getElementById('advanced-mode-btn').classList.toggle('active', mode === 'advanced');
    
    document.getElementById('simple-mode').classList.toggle('hidden', mode !== 'simple');
    document.getElementById('advanced-mode').classList.toggle('hidden', mode !== 'advanced');
    
    document.getElementById('results').classList.add('hidden');
    document.getElementById('status').classList.add('hidden');
}

document.getElementById('simple-mode-btn').addEventListener('click', () => switchMode('simple'));
document.getElementById('advanced-mode-btn').addEventListener('click', () => switchMode('advanced'));

document.getElementById('save-config').addEventListener('click', saveConfig);
document.getElementById('generate-btn').addEventListener('click', generateReport);
document.getElementById('process-query-btn').addEventListener('click', processQuery);
document.getElementById('generate-advanced-btn').addEventListener('click', generateAdvancedReport);
document.getElementById('download-btn').addEventListener('click', downloadReport);

document.getElementById('topic').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        generateReport();
    }
});

loadConfig();
