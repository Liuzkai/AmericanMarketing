/**
 * API 客户端模块
 * 封装所有与后端 API 的通信
 */

(function() {
    'use strict';

    const API_BASE_URL = window.location.origin + '/api/v1';

    /**
     * 通用 API 请求函数
     */
    async function apiRequest(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;

        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * API 客户端对象
     */
    const API = {
        /**
         * 获取股票分析数据
         * @param {string} ticker - 股票代码
         * @returns {Promise<Object>} 分析结果
         */
        analyzeStock: async function(ticker) {
            return await apiRequest(`/stock/${ticker.toUpperCase()}/analyze`);
        },

        /**
         * 获取快速报价
         * @param {string} ticker - 股票代码
         * @returns {Promise<Object>} 报价数据
         */
        getQuote: async function(ticker) {
            return await apiRequest(`/stock/${ticker.toUpperCase()}/quote`);
        },

        /**
         * 市场扫描
         * @param {Object} filters - 筛选条件
         * @returns {Promise<Object>} 扫描结果
         */
        marketScan: async function(filters = {}) {
            const params = new URLSearchParams();

            if (filters.index) params.append('index', filters.index);
            if (filters.maxPE) params.append('max_pe', filters.maxPE);
            if (filters.maxPEG) params.append('max_peg', filters.maxPEG);
            if (filters.limit) params.append('limit', filters.limit);

            const queryString = params.toString();
            const endpoint = `/market/scan${queryString ? '?' + queryString : ''}`;

            return await apiRequest(endpoint);
        },

        /**
         * 健康检查
         * @returns {Promise<Object>}
         */
        healthCheck: async function() {
            return await apiRequest('/health');
        }
    };

    /**
     * 工具函数
     */
    const Utils = {
        /**
         * 格式化数字
         * @param {number} value - 数值
         * @param {number} decimals - 小数位数
         * @returns {string}
         */
        formatNumber: function(value, decimals = 2) {
            if (value === null || value === undefined || isNaN(value)) {
                return 'N/A';
            }
            return Number(value).toFixed(decimals);
        },

        /**
         * 格式化百分比
         * @param {number} value - 数值
         * @param {number} decimals - 小数位数
         * @returns {string}
         */
        formatPercent: function(value, decimals = 2) {
            if (value === null || value === undefined || isNaN(value)) {
                return 'N/A';
            }
            return `${Number(value).toFixed(decimals)}%`;
        },

        /**
         * 格式化价格
         * @param {number} value - 价格
         * @returns {string}
         */
        formatPrice: function(value) {
            if (value === null || value === undefined || isNaN(value)) {
                return 'N/A';
            }
            return `$${Number(value).toFixed(2)}`;
        },

        /**
         * 格式化市值
         * @param {string|number} value - 市值
         * @returns {string}
         */
        formatMarketCap: function(value) {
            if (!value || value === 'N/A') return 'N/A';

            if (typeof value === 'string') {
                return value;
            }

            // 如果是数字，转换为 B/M/T 格式
            const num = Number(value);
            if (num >= 1e12) {
                return `$${(num / 1e12).toFixed(2)}T`;
            } else if (num >= 1e9) {
                return `$${(num / 1e9).toFixed(2)}B`;
            } else if (num >= 1e6) {
                return `$${(num / 1e6).toFixed(2)}M`;
            }
            return `$${num.toFixed(2)}`;
        },

        /**
         * 获取变化的 CSS 类名
         * @param {number} value - 变化值
         * @returns {string}
         */
        getChangeClass: function(value) {
            if (value > 0) return 'text-up';
            if (value < 0) return 'text-down';
            return '';
        },

        /**
         * 获取变化的符号
         * @param {number} value - 变化值
         * @returns {string}
         */
        getChangeSymbol: function(value) {
            if (value > 0) return '↑';
            if (value < 0) return '↓';
            return '';
        },

        /**
         * 显示加载状态
         * @param {HTMLElement} element - 目标元素
         */
        showLoading: function(element) {
            if (!element) return;
            element.innerHTML = `
                <div class="loading-container">
                    <div class="loading"></div>
                    <span style="margin-left: 1rem; color: var(--text-muted);">加载中...</span>
                </div>
            `;
        },

        /**
         * 显示错误信息
         * @param {HTMLElement} element - 目标元素
         * @param {string} message - 错误信息
         */
        showError: function(element, message) {
            if (!element) return;
            element.innerHTML = `
                <div class="card" style="background-color: rgba(255, 71, 87, 0.1); border-color: var(--color-down);">
                    <div class="card-body" style="color: var(--color-down); text-align: center;">
                        <p style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚠️ 错误</p>
                        <p>${message}</p>
                    </div>
                </div>
            `;
        },

        /**
         * 导出为 CSV
         * @param {Array} data - 数据数组
         * @param {string} filename - 文件名
         */
        exportToCSV: function(data, filename = 'export.csv') {
            if (!data || data.length === 0) {
                alert('没有数据可导出');
                return;
            }

            // 获取列名
            const headers = Object.keys(data[0]);

            // 构建 CSV 内容
            let csv = headers.join(',') + '\n';

            data.forEach(row => {
                const values = headers.map(header => {
                    const value = row[header];
                    // 处理包含逗号或换行符的值
                    if (typeof value === 'string' && (value.includes(',') || value.includes('\n'))) {
                        return `"${value.replace(/"/g, '""')}"`;
                    }
                    return value;
                });
                csv += values.join(',') + '\n';
            });

            // 创建下载链接
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);

            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },

        /**
         * 导出为 JSON
         * @param {Object|Array} data - 数据
         * @param {string} filename - 文件名
         */
        exportToJSON: function(data, filename = 'export.json') {
            if (!data) {
                alert('没有数据可导出');
                return;
            }

            const json = JSON.stringify(data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);

            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },

        /**
         * 防抖函数
         * @param {Function} func - 要防抖的函数
         * @param {number} wait - 等待时间（毫秒）
         * @returns {Function}
         */
        debounce: function(func, wait = 300) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    };

    // 导出到全局作用域
    window.API = API;
    window.Utils = Utils;
})();
