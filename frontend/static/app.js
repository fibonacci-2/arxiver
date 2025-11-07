let currentFilename = null;
let currentQuerySpec = null;

function addLog(message, type = 'info') {
    const logsBox = document.getElementById('logs');
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span>${message}`;
    logsBox.appendChild(logEntry);
    logsBox.scrollTop = logsBox.scrollHeight;
}

function clearLogs() {
    document.getElementById('logs').innerHTML = '';
}

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        document.getElementById('llm-model').value = config.llm.model;
        document.getElementById('embedding-model').value = config.embeddings.model;
        document.getElementById('indexer-type').value = config.indexer.type;
        document.getElementById('top-papers').value = config.search.top_papers;
    } catch (error) {
        addLog('Failed to load configuration', 'error');
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
    const query = document.getElementById('user-query').value.trim();
    
    if (!query) {
        showStatus('Please enter your requirements', 'error');
        return;
    }
    
    clearLogs();
    const processBtn = document.getElementById('process-query-btn');
    processBtn.disabled = true;
    processBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
    
    addLog('🔍 Analyzing query requirements...', 'info');
    
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
            document.getElementById('generate-btn').classList.remove('hidden');
            addLog('✅ Query processed successfully!', 'success');
            addLog(`📊 Search query: "${data.search_query}"`, 'info');
            addLog(`📝 ${data.themes.length} themes identified`, 'info');
            showStatus('Query analyzed successfully!', 'success');
        } else {
            addLog(`❌ Error: ${data.detail}`, 'error');
            showStatus('Error: ' + data.detail, 'error');
        }
    } catch (error) {
        addLog(`❌ Error: ${error.message}`, 'error');
        showStatus('Error: ' + error.message, 'error');
    } finally {
        processBtn.disabled = false;
        processBtn.innerHTML = 'Analyze Query';
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

async function generateReport() {
    if (!currentQuerySpec) {
        showStatus('Please analyze your query first', 'error');
        addLog('⚠️ Please analyze your query first', 'warning');
        return;
    }
    
    const generateBtn = document.getElementById('generate-btn');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner"></span> Generating...';
    
    showStatus('Searching and processing papers...', 'info');
    document.getElementById('results').classList.add('hidden');
    
    addLog('🔎 Searching ArXiv for relevant papers...', 'info');
    
    try {
        // Get current config values
        const llmModel = document.getElementById('llm-model').value;
        const embeddingModel = document.getElementById('embedding-model').value;
        const indexerType = document.getElementById('indexer-type').value;
        const topPapers = parseInt(document.getElementById('top-papers').value);
        
        const response = await fetch('/api/generate-advanced', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_query: document.getElementById('user-query').value,
                llm_model: llmModel,
                embedding_model: embeddingModel,
                indexer_type: indexerType,
                top_papers: topPapers
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentFilename = data.filename;
            addLog(`✅ Found ${data.papers.length} papers`, 'success');
            addLog('📄 Generating report with LaTeX...', 'info');
            displayResults(data.papers);
            addLog('🎉 Report generated successfully!', 'success');
            addLog(`💾 Saved as: ${data.filename}`, 'info');
            showStatus('Report generated successfully!', 'success');
            
            if (data.warnings && data.warnings.length > 0) {
                data.warnings.forEach(warning => {
                    addLog(`⚠️ ${warning}`, 'warning');
                });
            }
        } else {
            addLog(`❌ Error: ${data.detail}`, 'error');
            showStatus('Error: ' + data.detail, 'error');
        }
    } catch (error) {
        addLog(`❌ Error: ${error.message}`, 'error');
        showStatus('Error: ' + error.message, 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = 'Generate Report';
    }
}

document.getElementById('process-query-btn').addEventListener('click', processQuery);
document.getElementById('generate-btn').addEventListener('click', generateReport);
document.getElementById('download-btn').addEventListener('click', downloadReport);

loadConfig();
