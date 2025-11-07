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



function displayPapers(papers) {
    const papersList = document.getElementById('papers-list');
    papersList.innerHTML = '';
    
    papers.forEach((paper, index) => {
        const paperDiv = document.createElement('div');
        paperDiv.className = 'paper-item';
        paperDiv.innerHTML = `
            <div class="paper-title">${index + 1}. ${paper.title}</div>
            <div class="paper-id">arXiv:${paper.arxiv_id}</div>
        `;
        papersList.appendChild(paperDiv);
    });
}

function displayReportPreview(content, topic) {
    const preview = document.getElementById('report-preview');
    const titleText = document.getElementById('preview-title-text');
    
    // Update header title
    titleText.textContent = topic.length > 50 ? topic.substring(0, 50) + '...' : topic;
    
    // Update preview content
    preview.innerHTML = `
        <div class="report-content">
            <h1>${topic}</h1>
            <div class="preview-note" style="background: #e8f4fd; padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem; border-left: 4px solid #667eea;">
                <strong>📄 Preview:</strong> This is a text preview of the generated report. Download the PDF for the full formatted version with proper citations and bibliography.
            </div>
            <div style="white-space: pre-wrap; font-family: inherit;">${content}</div>
        </div>
    `;
    
    // Show download button in header
    document.getElementById('download-btn').classList.remove('hidden');
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

async function handleAction() {
    const actionBtn = document.getElementById('action-btn');
    const state = actionBtn.dataset.state;
    
    if (state === 'analyze') {
        await processQuery();
    } else if (state === 'generate') {
        await generateReport();
    }
}

async function processQuery() {
    const query = document.getElementById('user-query').value.trim();
    
    if (!query) {
        showStatus('Please enter your requirements', 'error');
        return;
    }
    
    clearLogs();
    const actionBtn = document.getElementById('action-btn');
    actionBtn.disabled = true;
    actionBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
    
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
            addLog('✅ Query processed successfully!', 'success');
            addLog(`📊 Search query: "${data.search_query}"`, 'info');
            addLog(`📝 ${data.themes.length} themes identified`, 'info');
            showStatus('Query analyzed successfully!', 'success');
            
            // Change button to generate state
            actionBtn.dataset.state = 'generate';
            actionBtn.innerHTML = 'Generate Report';
            actionBtn.classList.remove('btn-secondary');
            actionBtn.classList.add('btn-primary');
        } else {
            addLog(`❌ Error: ${data.detail}`, 'error');
            showStatus('Error: ' + data.detail, 'error');
        }
    } catch (error) {
        addLog(`❌ Error: ${error.message}`, 'error');
        showStatus('Error: ' + error.message, 'error');
    } finally {
        actionBtn.disabled = false;
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
    
    const actionBtn = document.getElementById('action-btn');
    actionBtn.disabled = true;
    actionBtn.innerHTML = '<span class="spinner"></span> Generating...';
    
    showStatus('Searching and processing papers...', 'info');
    
    addLog('🔎 Searching ArXiv for relevant papers...', 'info');
    addLog(`📊 Query: "${currentQuerySpec.search_query}"`, 'info');
    
    try {
        // Get current config values
        const llmModel = document.getElementById('llm-model').value;
        const embeddingModel = document.getElementById('embedding-model').value;
        const indexerType = document.getElementById('indexer-type').value;
        const topPapers = parseInt(document.getElementById('top-papers').value);
        
        addLog(`⚙️ Using ${llmModel} with ${embeddingModel}`, 'info');
        addLog(`🔧 Indexer: ${indexerType}, Top papers: ${topPapers}`, 'info');
        
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
            
            // Log search results
            addLog(`✅ Found ${data.papers.length} relevant papers`, 'success');
            addLog('📑 Ranking papers by relevance...', 'info');
            
            // Display papers incrementally with progress
            if (data.processed_papers) {
                addLog(`📥 Fetching and processing ${data.processed_papers.length} papers...`, 'info');
                
                // Simulate incremental display (since we get all at once from backend)
                data.papers.forEach((paper, index) => {
                    setTimeout(() => {
                        // Update papers list incrementally
                        addPaperToList(paper, index + 1);
                        
                        // Log each paper fetch
                        const processedInfo = data.processed_papers[index];
                        if (processedInfo && processedInfo.status === 'success') {
                            addLog(`✓ [${index + 1}/${data.papers.length}] ${paper.title.substring(0, 60)}...`, 'success');
                        } else if (processedInfo && processedInfo.status === 'error') {
                            addLog(`✗ [${index + 1}/${data.papers.length}] Failed: ${paper.title.substring(0, 50)}...`, 'error');
                        }
                    }, index * 100); // Stagger the display
                });
            } else {
                displayPapers(data.papers);
            }
            
            // Wait for paper display to complete, then continue
            setTimeout(() => {
                addLog('📝 Extracting text from PDFs...', 'info');
                addLog(`🔍 Creating ${indexerType} index...`, 'info');
                addLog('🧠 Chunking documents for RAG...', 'info');
                
                if (data.warnings && data.warnings.length > 0) {
                    data.warnings.forEach(warning => {
                        addLog(`⚠️ ${warning}`, 'warning');
                    });
                }
                
                addLog('✍️ Generating report with LLM...', 'info');
                addLog('📄 Compiling LaTeX document...', 'info');
                addLog('📚 Adding bibliography and citations...', 'info');
                
                // Display report preview
                if (data.report_preview) {
                    displayReportPreview(data.report_preview, currentQuerySpec.search_query);
                }
                
                addLog('✅ PDF generated successfully!', 'success');
                addLog(`💾 Saved as: ${data.filename}`, 'success');
                addLog('🎉 Report generation complete!', 'success');
                showStatus('Report generated successfully!', 'success');
                
                // Reset button to analyze state for new query
                actionBtn.dataset.state = 'analyze';
                actionBtn.innerHTML = 'New Query';
            }, data.papers.length * 100 + 500);
        } else {
            addLog(`❌ Error: ${data.detail}`, 'error');
            showStatus('Error: ' + data.detail, 'error');
            // Keep button in generate state to allow retry
            actionBtn.innerHTML = 'Retry Generation';
        }
    } catch (error) {
        addLog(`❌ Error: ${error.message}`, 'error');
        showStatus('Error: ' + error.message, 'error');
        // Keep button in generate state to allow retry
        actionBtn.innerHTML = 'Retry Generation';
    } finally {
        actionBtn.disabled = false;
    }
}

function addPaperToList(paper, index) {
    const papersList = document.getElementById('papers-list');
    
    // Clear empty state on first paper
    if (index === 1) {
        papersList.innerHTML = '';
    }
    
    const paperDiv = document.createElement('div');
    paperDiv.className = 'paper-item';
    paperDiv.style.opacity = '0';
    paperDiv.innerHTML = `
        <div class="paper-title">${index}. ${paper.title}</div>
        <div class="paper-id">arXiv:${paper.arxiv_id}</div>
    `;
    papersList.appendChild(paperDiv);
    
    // Fade in animation
    setTimeout(() => {
        paperDiv.style.transition = 'opacity 0.3s';
        paperDiv.style.opacity = '1';
    }, 10);
    
    // Auto scroll to show new paper
    papersList.scrollTop = papersList.scrollHeight;
}

document.getElementById('action-btn').addEventListener('click', handleAction);
document.getElementById('download-btn').addEventListener('click', downloadReport);

// Reset button when query text changes
document.getElementById('user-query').addEventListener('input', function() {
    const actionBtn = document.getElementById('action-btn');
    if (actionBtn.dataset.state === 'generate' || actionBtn.innerHTML === 'New Query') {
        actionBtn.dataset.state = 'analyze';
        actionBtn.innerHTML = 'Analyze Query';
        document.getElementById('query-spec').classList.add('hidden');
        currentQuerySpec = null;
    }
});

loadConfig();
