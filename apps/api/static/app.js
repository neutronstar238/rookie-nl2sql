// NL2SQL Frontend Application - Robust Version
class NL2SQLApp {
    constructor() {
        this.apiBase = '';
        this.currentSessionId = this.generateSessionId();
        console.log('[NL2SQL] App initializing...');
        
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    generateSessionId() {
        return `session_${Math.random().toString(36).substr(2, 9)}`;
    }

    init() {
        console.log('[NL2SQL] DOM loaded, initializing app...');
        this.bindEvents();
        this.loadExamples();
        this.loadStats();
        this.checkHealth();
    }

    safeGetElement(id) {
        const el = document.getElementById(id);
        if (!el) {
            console.warn(`[NL2SQL] Element not found: ${id}`);
        }
        return el;
    }

    bindEvents() {
        const submitBtn = this.safeGetElement('submitBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.executeQuery());
        }

        const queryInput = this.safeGetElement('queryInput');
        if (queryInput) {
            queryInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                    this.executeQuery();
                }
            });
        }

        const sqlHeader = this.safeGetElement('sqlHeader');
        if (sqlHeader) {
            sqlHeader.addEventListener('click', () => {
                sqlHeader.classList.toggle('collapsed');
                const sqlDisplay = this.safeGetElement('sqlDisplay');
                if (sqlDisplay) {
                    sqlDisplay.classList.toggle('collapsed');
                }
            });
        }

        const metadataHeader = this.safeGetElement('metadataHeader');
        if (metadataHeader) {
            metadataHeader.addEventListener('click', () => {
                metadataHeader.classList.toggle('collapsed');
                const metadataDisplay = this.safeGetElement('metadataDisplay');
                if (metadataDisplay) {
                    metadataDisplay.classList.toggle('collapsed');
                }
            });
        }
    }

    async checkHealth() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            if (data.status === 'healthy') {
                this.setStatus('就绪', 'ready');
                console.log('[NL2SQL] Backend healthy');
            }
        } catch (error) {
            console.error('[NL2SQL] Health check failed:', error);
            this.setStatus('服务异常', 'error');
        }
    }

    async loadExamples() {
        const container = this.safeGetElement('examplesContainer');
        if (!container) return;
        
        try {
            const response = await fetch(`${this.apiBase}/api/examples`);
            const data = await response.json();
            
            container.innerHTML = '';
            data.examples.forEach(category => {
                const categoryDiv = document.createElement('div');
                categoryDiv.className = 'example-category';
                
                const title = document.createElement('div');
                title.className = 'example-category-title';
                title.textContent = category.category;
                categoryDiv.appendChild(title);
                
                category.questions.forEach(question => {
                    const questionDiv = document.createElement('div');
                    questionDiv.className = 'example-question';
                    questionDiv.textContent = question;
                    questionDiv.addEventListener('click', () => {
                        const queryInput = this.safeGetElement('queryInput');
                        if (queryInput) {
                            queryInput.value = question;
                            this.executeQuery();
                        }
                    });
                    categoryDiv.appendChild(questionDiv);
                });
                
                container.appendChild(categoryDiv);
            });
        } catch (error) {
            console.error('[NL2SQL] Failed to load examples:', error);
            container.innerHTML = '<p style="color: var(--error-color);">加载示例失败</p>';
        }
    }

    async loadStats() {
        const container = this.safeGetElement('statsContainer');
        if (!container) return;
        
        try {
            const response = await fetch(`${this.apiBase}/api/stats`);
            const data = await response.json();
            
            const grid = document.createElement('div');
            grid.className = 'stats-grid';
            
            const totalCard = document.createElement('div');
            totalCard.className = 'stat-card';
            totalCard.innerHTML = `
                <div class="stat-value">${data.total_tables}</div>
                <div class="stat-label">数据表</div>
            `;
            grid.appendChild(totalCard);
            
            const totalRows = data.tables.reduce((sum, t) => sum + t.row_count, 0);
            const rowsCard = document.createElement('div');
            rowsCard.className = 'stat-card';
            rowsCard.innerHTML = `
                <div class="stat-value">${totalRows.toLocaleString()}</div>
                <div class="stat-label">数据行</div>
            `;
            grid.appendChild(rowsCard);
            
            container.innerHTML = '';
            container.appendChild(grid);
            
            if (data.tables.length > 0) {
                const details = document.createElement('div');
                details.style.marginTop = '15px';
                details.style.fontSize = '0.85em';
                details.style.color = 'var(--text-secondary)';
                details.innerHTML = '<strong>主要数据表：</strong><br>' +
                    data.tables.map(t => `${t.name}: ${t.row_count.toLocaleString()} 行`).join('<br>');
                container.appendChild(details);
            }
        } catch (error) {
            console.error('[NL2SQL] Failed to load stats:', error);
            container.innerHTML = '<p style="color: var(--error-color);">加载统计失败</p>';
        }
    }

    async executeQuery() {
        const queryInput = this.safeGetElement('queryInput');
        if (!queryInput) return;
        
        const question = queryInput.value.trim();
        
        if (!question) {
            alert('请输入查询问题');
            return;
        }

        console.log('[NL2SQL] Executing query:', question);
        this.setLoading(true);
        this.setStatus('查询中...', 'loading');
        
        const welcomeMsg = this.safeGetElement('welcomeMessage');
        const resultsContainer = this.safeGetElement('resultsContainer');
        const errorContainer = this.safeGetElement('errorContainer');
        
        if (welcomeMsg) welcomeMsg.classList.add('hidden');
        if (resultsContainer) resultsContainer.classList.remove('hidden');
        if (errorContainer) errorContainer.classList.add('hidden');

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 90000); // 90 seconds
            
            const apiUrl = `${this.apiBase}/api/query`;
            console.log('[NL2SQL] POST to:', apiUrl);
            
            const startTime = Date.now();
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    session_id: this.currentSessionId
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
            console.log(`[NL2SQL] Response received in ${elapsed}s, status:`, response.status);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[NL2SQL] Response data:', data);
            
            if (data.success) {
                this.displayResults(data);
                this.setStatus('查询成功', 'ready');
            } else {
                this.displayError(data.error || '查询失败，请重试');
                this.setStatus('查询失败', 'error');
            }
        } catch (error) {
            console.error('[NL2SQL] Query failed:', error);
            if (error.name === 'AbortError') {
                this.displayError('查询超时（90秒），服务器响应时间过长。请尝试简化问题或稍后重试。');
                this.setStatus('查询超时', 'error');
            } else {
                this.displayError(`请求失败: ${error.message}\n\n请检查：\n1. 后端服务是否正常运行\n2. 网络连接是否正常\n3. 浏览器控制台是否有更多错误信息`);
                this.setStatus('请求失败', 'error');
            }
        } finally {
            this.setLoading(false);
        }
    }

    displayResults(data) {
        const questionDisplay = this.safeGetElement('questionDisplay');
        if (questionDisplay) {
            questionDisplay.textContent = data.question;
        }

        const answerSection = this.safeGetElement('answerSection');
        const answerDisplay = this.safeGetElement('answerDisplay');
        if (data.answer && answerDisplay) {
            if (answerSection) answerSection.classList.remove('hidden');
            answerDisplay.innerHTML = this.formatAnswer(data.answer);
        } else if (answerSection) {
            answerSection.classList.add('hidden');
        }

        const sqlDisplay = this.safeGetElement('sqlDisplay');
        if (sqlDisplay) {
            sqlDisplay.textContent = data.sql || 'SQL 未生成';
        }

        const dataSection = this.safeGetElement('dataSection');
        const tableWrapper = this.safeGetElement('tableWrapper');
        const rowCount = this.safeGetElement('rowCount');

        if (data.result && data.result.ok && data.result.rows && tableWrapper) {
            if (dataSection) dataSection.classList.remove('hidden');
            if (rowCount) rowCount.textContent = `${data.result.row_count} 行`;
            tableWrapper.innerHTML = this.createTable(data.result);
        } else if (dataSection) {
            dataSection.classList.add('hidden');
        }

        const metadataDisplay = this.safeGetElement('metadataDisplay');
        if (metadataDisplay) {
            metadataDisplay.innerHTML = this.createMetadata(data);
        }

        const resultsContainer = this.safeGetElement('resultsContainer');
        if (resultsContainer) {
            resultsContainer.scrollTop = 0;
        }
    }

    displayError(errorMessage) {
        const resultsContainer = this.safeGetElement('resultsContainer');
        const welcomeMessage = this.safeGetElement('welcomeMessage');
        const errorContainer = this.safeGetElement('errorContainer');
        const errorMessageEl = this.safeGetElement('errorMessage');
        
        if (resultsContainer) resultsContainer.classList.add('hidden');
        if (welcomeMessage) welcomeMessage.classList.add('hidden');
        if (errorContainer) errorContainer.classList.remove('hidden');
        if (errorMessageEl) errorMessageEl.textContent = errorMessage;
    }

    formatAnswer(answer) {
        return answer.replace(/\n/g, '<br>');
    }

    createTable(result) {
        if (!result.rows || result.rows.length === 0) {
            return '<p style="padding: 20px; text-align: center; color: var(--text-secondary);">无数据</p>';
        }

        const columns = result.columns || Object.keys(result.rows[0]);
        
        let html = '<table class="data-table">';
        
        html += '<thead><tr>';
        columns.forEach(col => {
            html += `<th>${this.escapeHtml(col)}</th>`;
        });
        html += '</tr></thead>';
        
        html += '<tbody>';
        result.rows.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                const value = row[col];
                html += `<td>${this.escapeHtml(this.formatValue(value))}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody>';
        
        html += '</table>';
        return html;
    }

    createMetadata(data) {
        const items = [
            { label: 'Trace ID', value: data.trace_id },
            { label: 'Session ID', value: data.session_id },
            { label: '执行时间', value: `${(data.execution_time * 1000).toFixed(0)} ms` },
        ];

        if (data.metadata) {
            if (data.metadata.retry_count > 0) {
                items.push({ label: '重试次数', value: data.metadata.retry_count });
            }
            if (data.metadata.total_llm_tokens) {
                items.push({ label: 'LLM Tokens', value: data.metadata.total_llm_tokens });
            }
        }

        let html = '';
        items.forEach(item => {
            html += `
                <div class="metadata-item">
                    <span class="metadata-label">${item.label}</span>
                    <span class="metadata-value">${this.escapeHtml(String(item.value))}</span>
                </div>
            `;
        });

        return html;
    }

    formatValue(value) {
        if (value === null || value === undefined) {
            return 'NULL';
        }
        if (typeof value === 'number') {
            return value.toLocaleString();
        }
        return String(value);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setLoading(loading) {
        const submitBtn = this.safeGetElement('submitBtn');
        const submitBtnText = this.safeGetElement('submitBtnText');
        const submitBtnLoading = this.safeGetElement('submitBtnLoading');
        
        if (submitBtn) submitBtn.disabled = loading;
        if (loading) {
            if (submitBtnText) submitBtnText.classList.add('hidden');
            if (submitBtnLoading) submitBtnLoading.classList.remove('hidden');
        } else {
            if (submitBtnText) submitBtnText.classList.remove('hidden');
            if (submitBtnLoading) submitBtnLoading.classList.add('hidden');
        }
    }

    setStatus(text, type) {
        const indicator = this.safeGetElement('statusIndicator');
        if (!indicator) return;
        
        const statusText = indicator.querySelector('.status-text');
        if (!statusText) return;
        
        statusText.textContent = text;
        indicator.className = 'status-indicator';
        
        if (type === 'loading') {
            indicator.classList.add('loading');
        }
    }
}

// Initialize app
let app;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        app = new NL2SQLApp();
    });
} else {
    app = new NL2SQLApp();
}
