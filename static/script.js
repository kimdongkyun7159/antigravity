// Error Analyzer - Modern JavaScript

// DOM Elements
const codeInput = document.getElementById('codeInput');
const fileInput = document.getElementById('fileInput');
const fileUpload = document.getElementById('fileUpload');
const fileName = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const executeCode = document.getElementById('executeCode');
const saveHistory = document.getElementById('saveHistory');
const lineCount = document.getElementById('lineCount');
const totalErrors = document.getElementById('totalErrors');

// Sections
const progressSection = document.getElementById('progressSection');
const progressText = document.getElementById('progressText');
const progressFill = document.getElementById('progressFill');
const resultSection = document.getElementById('resultSection');
const resultContent = document.getElementById('resultContent');
const errorSection = document.getElementById('errorSection');
const errorDetails = document.getElementById('errorDetails');
const solutionsSection = document.getElementById('solutionsSection');
const solutionsList = document.getElementById('solutionsList');
const similarSection = document.getElementById('similarSection');
const similarList = document.getElementById('similarList');

// State
let currentCode = '';
let currentFileType = 'python';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadStatistics();
    updateLineCount();
});

// Event Listeners
function setupEventListeners() {
    // Toggle buttons
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');

            const mode = e.target.dataset.mode;
            document.getElementById('textMode').classList.toggle('hidden', mode !== 'text');
            document.getElementById('fileMode').classList.toggle('hidden', mode !== 'file');
        });
    });

    // Code input
    codeInput.addEventListener('input', updateLineCount);

    // File upload
    fileUpload.addEventListener('click', () => fileInput.click());
    fileUpload.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUpload.style.borderColor = 'var(--primary)';
    });
    fileUpload.addEventListener('dragleave', () => {
        fileUpload.style.borderColor = '';
    });
    fileUpload.addEventListener('drop', handleFileDrop);
    fileInput.addEventListener('change', handleFileSelect);

    // Analyze button
    analyzeBtn.addEventListener('click', analyzeCode);
}

// Update line count
function updateLineCount() {
    const lines = codeInput.value.split('\n').length;
    lineCount.textContent = `${lines} ${lines === 1 ? 'line' : 'lines'}`;
}

// File handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        loadFile(file);
    }
}

function handleFileDrop(e) {
    e.preventDefault();
    fileUpload.style.borderColor = '';

    const file = e.dataTransfer.files[0];
    if (file) {
        loadFile(file);
    }
}

function loadFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        currentCode = e.target.result;
        codeInput.value = currentCode;
        fileName.textContent = file.name;
        fileName.classList.remove('hidden');
        updateLineCount();
    };
    reader.readAsText(file);
}

// Main analysis function
async function analyzeCode() {
    const code = codeInput.value.trim();

    if (!code) {
        showError('코드를 입력해주세요');
        return;
    }

    hideAllSections();
    showProgress('코드 분석 시작...');
    analyzeBtn.disabled = true;

    try {
        // API 호출
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                file_type: currentFileType,
                execute: executeCode.checked
            })
        });

        const data = await response.json();

        if (!data.success) {
            showError(data.error || '분석 실패');
            return;
        }

        // 결과 표시
        displayResults(data);

    } catch (error) {
        showError('서버 연결 실패: ' + error.message);
    } finally {
        hideProgress();
        analyzeBtn.disabled = false;
    }
}

// Display results
function displayResults(data) {
    const analysis = data.analysis;

    // 1. Validation results
    if (analysis.validation) {
        const syntax = analysis.validation.syntax;

        if (!syntax.valid) {
            showSyntaxError(syntax);
            return;
        }

        // Check imports
        if (analysis.validation.imports) {
            const missing = analysis.validation.imports.availability.missing;
            if (missing.length > 0) {
                showImportErrors(missing);
            }
        }
    }

    // 2. Execution results
    if (analysis.execution) {
        const exec = analysis.execution;

        if (exec.success) {
            showSuccess(exec);
        } else {
            // 에러 분석 표시
            if (analysis.error_analysis) {
                showErrorAnalysis(analysis.error_analysis, exec);

                // 유사 에러 표시
                if (analysis.similar_errors && analysis.similar_errors.length > 0) {
                    showSimilarErrors(analysis.similar_errors);
                }
            } else {
                showExecutionError(exec);
            }
        }
    } else {
        showValidationSuccess();
    }
}

// Display functions
function showSyntaxError(syntax) {
    errorSection.classList.remove('hidden');
    errorDetails.innerHTML = `
        <div class="error-item">
            <div class="error-header">
                <span class="error-type">${syntax.error_type}</span>
                ${syntax.line ? `<span class="error-line">Line ${syntax.line}</span>` : ''}
            </div>
            <div class="error-message">${escapeHtml(syntax.error)}</div>
            ${syntax.text ? `<pre class="error-code"><code>${escapeHtml(syntax.text)}</code></pre>` : ''}
        </div>
    `;
}

function showImportErrors(missing) {
    solutionsSection.classList.remove('hidden');
    solutionsList.innerHTML = `
        <div class="solution-item">
            <h4>⚠️ 누락된 패키지</h4>
            <p>다음 패키지들이 설치되지 않았습니다:</p>
            <ul>
                ${missing.map(pkg => `
                    <li>
                        <strong>${pkg}</strong>
                        <button class="btn-copy" onclick="copyToClipboard('pip install ${pkg}')">
                            📋 설치 명령 복사
                        </button>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
}

function showSuccess(exec) {
    resultSection.classList.remove('hidden');
    resultContent.innerHTML = `
        <div class="success-message">
            <h3>✅ 코드 실행 성공!</h3>
            <p>실행 시간: <strong>${exec.execution_time.toFixed(3)}초</strong></p>
            ${exec.stdout ? `
                <div class="output-section">
                    <h4>📤 출력:</h4>
                    <pre><code>${escapeHtml(exec.stdout)}</code></pre>
                </div>
            ` : ''}
        </div>
    `;
}

function showErrorAnalysis(analysis, exec) {
    // 에러 상세
    errorSection.classList.remove('hidden');
    errorDetails.innerHTML = `
        <div class="error-item">
            <div class="error-header">
                <span class="error-type">${analysis.error_type}</span>
                ${analysis.line_number ? `<span class="error-line">Line ${analysis.line_number}</span>` : ''}
                <span class="error-severity severity-${analysis.severity}">${analysis.severity}</span>
            </div>
            <div class="error-message">${escapeHtml(analysis.error_message)}</div>
            <div class="error-description">
                <strong>📖 설명:</strong> ${analysis.description}
            </div>
        </div>
    `;

    // 해결책
    if (analysis.solutions) {
        solutionsSection.classList.remove('hidden');
        solutionsList.innerHTML = analysis.solutions.map((solution, i) => `
            <div class="solution-item">
                <div class="solution-number">${i + 1}</div>
                <div class="solution-content">
                    <p>${solution}</p>
                    ${solution.includes('pip install') ? `
                        <button class="btn-copy" onclick="copyToClipboard('${solution}')">
                            📋 복사
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    // 통계 업데이트
    loadStatistics();
}

function showExecutionError(exec) {
    errorSection.classList.remove('hidden');
    errorDetails.innerHTML = `
        <div class="error-item">
            <div class="error-message">실행 실패</div>
            <pre><code>${escapeHtml(exec.stderr)}</code></pre>
        </div>
    `;
}

function showValidationSuccess() {
    resultSection.classList.remove('hidden');
    resultContent.innerHTML = `
        <div class="success-message">
            <h3>✅ 코드 검증 성공!</h3>
            <p>Syntax 오류가 없으며 모든 import가 유효합니다.</p>
        </div>
    `;
}

// Progress
function showProgress(message) {
    progressSection.classList.remove('hidden');
    progressText.textContent = message;
    progressFill.style.width = '0%';

    // Animate
    setTimeout(() => progressFill.style.width = '30%', 100);
    setTimeout(() => progressFill.style.width = '60%', 500);
    setTimeout(() => progressFill.style.width = '90%', 1000);
}

function hideProgress() {
    progressSection.classList.add('hidden');
    progressFill.style.width = '100%';
}

function showError(message) {
    errorSection.classList.remove('hidden');
    errorDetails.innerHTML = `
        <div class="error-item">
            <div class="error-message">${escapeHtml(message)}</div>
        </div>
    `;
}

function hideAllSections() {
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    solutionsSection.classList.add('hidden');
    similarSection.classList.add('hidden');
}

// Statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();

        if (data.success && data.statistics) {
            totalErrors.textContent = data.statistics.total_errors || 0;
        }
    } catch (error) {
        console.error('통계 로딩 실패:', error);
        totalErrors.textContent = '0';
    }
}

// Utilities
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show toast
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = '📋 복사됨!';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    });
}

// Similar errors display
function showSimilarErrors(similarErrors) {
    similarSection.classList.remove('hidden');
    similarList.innerHTML = similarErrors.map(error => {
        const date = new Date(error.timestamp).toLocaleString('ko-KR');
        return `
            <div class="similar-error-item">
                <div class="error-header">
                    <span class="error-badge">${error.error_type}</span>
                    <span class="error-timestamp">${date}</span>
                </div>
                <div class="error-message">${escapeHtml(error.error_message)}</div>
                <div class="error-description">${error.description}</div>
                ${error.occurrence_count > 1 ? `
                    <div class="error-frequency">🔄 ${error.occurrence_count}번 발생</div>
                ` : ''}
            </div>
        `;
    }).join('');
}
