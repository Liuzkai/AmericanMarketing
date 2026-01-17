/**
 * 股票分析页面逻辑
 */

let currentAnalysisData = null;

async function analyzeStock() {
    const ticker = document.getElementById('ticker-input').value.trim().toUpperCase();
    const resultContainer = document.getElementById('analysis-result');

    if (!ticker) {
        alert('请输入股票代码');
        return;
    }

    // 显示加载状态
    Utils.showLoading(resultContainer);

    // 隐藏导出按钮
    document.getElementById('export-buttons').style.display = 'none';

    try {
        // 调用 API
        const response = await API.analyzeStock(ticker);
        currentAnalysisData = response.data;

        // 渲染结果
        renderAnalysis(currentAnalysisData);

        // 显示导出按钮
        document.getElementById('export-buttons').style.display = 'flex';

        // 更新 URL
        window.history.pushState({}, '', `/analyze/${ticker}`);

    } catch (error) {
        Utils.showError(resultContainer, `分析失败: ${error.message}`);
    }
}

function renderAnalysis(data) {
    const resultContainer = document.getElementById('analysis-result');

    const html = `
        <!-- 价格展示 -->
        <div class="price-display">
            <h2 style="margin-bottom: 1rem;">${data.ticker}</h2>
            <div class="price-main ${Utils.getChangeClass(data.price_change)}">
                ${Utils.formatPrice(data.current_price)}
            </div>
            <div class="price-change ${Utils.getChangeClass(data.price_change)}">
                ${Utils.getChangeSymbol(data.price_change)}
                ${Utils.formatPrice(Math.abs(data.price_change))}
                (${Utils.formatPercent(Math.abs(data.price_change_percent))})
            </div>
        </div>

        <!-- K线图 -->
        <div class="card">
            <div class="card-header">价格走势</div>
            <div id="price-chart" class="chart-container"></div>
        </div>

        <!-- 技术指标 -->
        <div class="card">
            <div class="card-header">技术指标</div>
            <div class="grid-4">
                <div class="metric-card">
                    <div class="metric-label">RSI</div>
                    <div class="metric-value">${Utils.formatNumber(data.technical_indicators.rsi.value)}</div>
                    <div class="metric-signal signal-${getSignalClass(data.technical_indicators.rsi.signal)}">
                        ${data.technical_indicators.rsi.signal}
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">MACD</div>
                    <div class="metric-value">${Utils.formatNumber(data.technical_indicators.macd.value)}</div>
                    <div class="metric-signal signal-${getSignalClass(data.technical_indicators.macd.trend)}">
                        ${data.technical_indicators.macd.trend}
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">布林带</div>
                    <div class="metric-value">${Utils.formatPrice(data.technical_indicators.bollinger_bands.middle)}</div>
                    <div class="metric-signal signal-${getSignalClass(data.technical_indicators.bollinger_bands.signal)}">
                        ${data.technical_indicators.bollinger_bands.signal}
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">总体信号</div>
                    <div class="metric-value">${data.technical_indicators.overall_signal}</div>
                    <div class="metric-signal signal-${getSignalClass(data.technical_indicators.overall_signal)}">
                        ${data.technical_indicators.ma_signal}
                    </div>
                </div>
            </div>
        </div>

        <!-- 财务指标和情绪分析 -->
        <div class="grid-2">
            <div class="card">
                <div class="card-header">财务指标</div>
                <table>
                    <tr>
                        <td>市盈率 (PE)</td>
                        <td style="text-align: right; font-weight: 600;">${Utils.formatNumber(data.financial_metrics.pe_ratio)}</td>
                    </tr>
                    <tr>
                        <td>市净率 (PB)</td>
                        <td style="text-align: right; font-weight: 600;">${Utils.formatNumber(data.financial_metrics.pb_ratio)}</td>
                    </tr>
                    <tr>
                        <td>净资产收益率 (ROE)</td>
                        <td style="text-align: right; font-weight: 600;">${Utils.formatPercent(data.financial_metrics.roe)}</td>
                    </tr>
                    <tr>
                        <td>营收增长</td>
                        <td style="text-align: right; font-weight: 600;">${Utils.formatPercent(data.financial_metrics.revenue_growth)}</td>
                    </tr>
                </table>
            </div>

            <div class="card">
                <div class="card-header">新闻情绪分析</div>
                <div id="sentiment-gauge" class="chart-container chart-small"></div>
                <div class="text-center mt-2">
                    <span style="font-size: 1.25rem; font-weight: 600; color: var(--color-primary);">
                        ${data.sentiment.overall_sentiment}
                    </span>
                    <p class="text-muted mt-1">
                        正面: ${data.sentiment.distribution.positive || 0} |
                        中性: ${data.sentiment.distribution.neutral || 0} |
                        负面: ${data.sentiment.distribution.negative || 0}
                    </p>
                </div>
            </div>
        </div>

        <!-- 投资建议 -->
        <div class="recommendation-card">
            <div class="recommendation-title">投资建议</div>
            <div class="recommendation-score">${data.recommendation.score} 分</div>
            <h3 style="font-size: 1.5rem; margin-bottom: 1rem; color: var(--color-primary);">
                ${data.recommendation.action}
            </h3>
            <ul class="recommendation-reasons">
                ${data.recommendation.reasons.map(reason => `<li>${reason}</li>`).join('')}
            </ul>
        </div>

        <!-- 相关新闻 -->
        <div class="card">
            <div class="card-header">相关新闻</div>
            <ul class="news-list">
                ${data.news.map(news => `
                    <li class="news-item">
                        <div class="news-title">${news.title}</div>
                        <div class="news-meta">${news.publisher} - ${news.published || '最近'}</div>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;

    resultContainer.innerHTML = html;

    // 渲染图表
    setTimeout(() => {
        renderCharts(data);
    }, 100);
}

function renderCharts(data) {
    // 渲染 K线图
    if (data.price_history && data.price_history.length > 0) {
        Charts.createCandlestickChart('price-chart', data.price_history);
    }

    // 渲染情绪仪表盘
    const sentimentValue = ((data.sentiment.average_polarity + 1) / 2) * 100; // 转换为 0-100
    Charts.createGaugeChart('sentiment-gauge', sentimentValue, '情绪指数');
}

function getSignalClass(signal) {
    const signalLower = (signal || '').toLowerCase();
    if (signalLower.includes('buy') || signalLower.includes('bullish') || signalLower.includes('positive')) {
        return 'buy';
    }
    if (signalLower.includes('sell') || signalLower.includes('bearish') || signalLower.includes('negative')) {
        return 'sell';
    }
    return 'neutral';
}

function exportCSV() {
    if (!currentAnalysisData) {
        alert('没有数据可导出');
        return;
    }

    const ticker = currentAnalysisData.ticker;
    const csvData = [
        {
            '股票代码': ticker,
            '当前价格': currentAnalysisData.current_price,
            '涨跌额': currentAnalysisData.price_change,
            '涨跌幅': currentAnalysisData.price_change_percent + '%',
            'RSI': currentAnalysisData.technical_indicators.rsi.value,
            'MACD': currentAnalysisData.technical_indicators.macd.value,
            '技术信号': currentAnalysisData.technical_indicators.overall_signal,
            'PE': currentAnalysisData.financial_metrics.pe_ratio,
            'PB': currentAnalysisData.financial_metrics.pb_ratio,
            'ROE': currentAnalysisData.financial_metrics.roe,
            '情绪评分': currentAnalysisData.sentiment.average_polarity,
            '投资建议': currentAnalysisData.recommendation.action,
            '推荐评分': currentAnalysisData.recommendation.score
        }
    ];

    Utils.exportToCSV(csvData, `${ticker}_analysis.csv`);
}

function exportJSON() {
    if (!currentAnalysisData) {
        alert('没有数据可导出');
        return;
    }

    Utils.exportToJSON(currentAnalysisData, `${currentAnalysisData.ticker}_analysis.json`);
}
