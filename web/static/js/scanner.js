/**
 * 市场扫描页面逻辑
 */

let currentScanData = null;

async function startScan() {
    const resultContainer = document.getElementById('scan-result');

    // 获取筛选条件
    const filters = {
        index: document.getElementById('filter-index').value,
        maxPE: parseFloat(document.getElementById('filter-pe').value),
        maxPEG: parseFloat(document.getElementById('filter-peg').value),
        limit: parseInt(document.getElementById('filter-limit').value)
    };

    // 显示加载状态
    Utils.showLoading(resultContainer);

    try {
        // 调用 API
        const response = await API.marketScan(filters);
        currentScanData = response.data;

        // 渲染结果
        renderScanResult(currentScanData);

    } catch (error) {
        Utils.showError(resultContainer, `扫描失败: ${error.message}`);
    }
}

function renderScanResult(data) {
    const resultContainer = document.getElementById('scan-result');

    if (!data.opportunities || data.opportunities.length === 0) {
        resultContainer.innerHTML = `
            <div class="card">
                <div class="card-body text-center">
                    <p style="font-size: 1.25rem; color: var(--text-muted);">
                        未找到符合条件的股票
                    </p>
                </div>
            </div>
        `;
        return;
    }

    const html = `
        <!-- 统计信息 -->
        <div class="stats-container">
            <div class="stat-item">
                <div class="stat-value">${data.total_scanned}</div>
                <div class="stat-label">扫描股票数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${data.opportunities.length}</div>
                <div class="stat-label">机会股票</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${Object.keys(data.statistics.sector_distribution || {}).length}</div>
                <div class="stat-label">涉及行业</div>
            </div>
        </div>

        <!-- 结果表格 -->
        <div class="card">
            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                <span>扫描结果</span>
                <button class="btn btn-secondary" onclick="exportScanCSV()" style="padding: 0.5rem 1rem;">
                    导出 CSV
                </button>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>代码</th>
                            <th>价格</th>
                            <th>评分</th>
                            <th>PE</th>
                            <th>PEG</th>
                            <th>PB</th>
                            <th>行业</th>
                            <th>技术信号</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.opportunities.map(stock => `
                            <tr>
                                <td>
                                    <a href="/analyze/${stock.ticker}"
                                       style="color: var(--color-primary); font-weight: 600; text-decoration: none;">
                                        ${stock.ticker}
                                    </a>
                                </td>
                                <td>${Utils.formatPrice(stock.price)}</td>
                                <td>
                                    <span style="font-weight: 600; color: var(--color-success);">
                                        ${stock.opportunity_score}
                                    </span>
                                </td>
                                <td>${Utils.formatNumber(stock.pe)}</td>
                                <td>${Utils.formatNumber(stock.peg)}</td>
                                <td>${Utils.formatNumber(stock.pb)}</td>
                                <td style="font-size: 0.875rem; color: var(--text-muted);">
                                    ${stock.sector || 'N/A'}
                                </td>
                                <td>
                                    <span class="metric-signal signal-${getSignalClass(stock.tech_signal)}">
                                        ${stock.tech_signal || 'N/A'}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 行业分布 -->
        ${Object.keys(data.statistics.sector_distribution || {}).length > 0 ? `
            <div class="card">
                <div class="card-header">行业分布</div>
                <div id="sector-chart" class="chart-container chart-small"></div>
            </div>
        ` : ''}
    `;

    resultContainer.innerHTML = html;

    // 渲染图表
    setTimeout(() => {
        if (data.statistics.sector_distribution) {
            Charts.createPieChart('sector-chart', data.statistics.sector_distribution);
        }
    }, 100);
}

function getSignalClass(signal) {
    const signalLower = (signal || '').toLowerCase();
    if (signalLower.includes('buy') || signalLower.includes('positive')) {
        return 'buy';
    }
    if (signalLower.includes('sell') || signalLower.includes('negative')) {
        return 'sell';
    }
    return 'neutral';
}

function exportScanCSV() {
    if (!currentScanData || !currentScanData.opportunities) {
        alert('没有数据可导出');
        return;
    }

    const csvData = currentScanData.opportunities.map(stock => ({
        '代码': stock.ticker,
        '价格': stock.price,
        '机会评分': stock.opportunity_score,
        'PE': stock.pe,
        'PEG': stock.peg,
        'PB': stock.pb,
        '市值': stock.market_cap,
        '行业': stock.sector,
        '细分行业': stock.industry,
        '技术信号': stock.tech_signal
    }));

    Utils.exportToCSV(csvData, 'market_scan.csv');
}
