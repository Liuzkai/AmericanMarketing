/**
 * 主题切换功能
 * 支持深色/浅色模式切换，并持久化到 localStorage
 */

(function() {
    'use strict';

    // 从 localStorage 读取主题设置，默认为深色模式
    const currentTheme = localStorage.getItem('theme') || 'dark';

    // 应用主题
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);

        // 更新所有 ECharts 实例（如果存在）
        if (typeof window.echartsInstances !== 'undefined') {
            updateChartsTheme(theme);
        }
    }

    // 更新图表主题
    function updateChartsTheme(theme) {
        const isDark = theme === 'dark';

        // 获取 CSS 变量
        const root = document.documentElement;
        const style = getComputedStyle(root);

        window.chartColors = {
            textColor: style.getPropertyValue('--chart-text').trim(),
            gridColor: style.getPropertyValue('--chart-grid').trim(),
            axisColor: style.getPropertyValue('--chart-axis').trim(),
            colorUp: style.getPropertyValue('--color-up').trim(),
            colorDown: style.getPropertyValue('--color-down').trim(),
            colorPrimary: style.getPropertyValue('--color-primary').trim()
        };

        // 重新渲染所有图表
        if (window.echartsInstances) {
            window.echartsInstances.forEach(chart => {
                if (chart && !chart.isDisposed()) {
                    const option = chart.getOption();
                    // 更新颜色配置
                    updateChartColors(option);
                    chart.setOption(option, true);
                }
            });
        }
    }

    // 更新图表配色
    function updateChartColors(option) {
        // 这个函数会在 charts.js 中被更详细实现
        // 这里只是占位符
    }

    // 初始化页面时应用主题
    applyTheme(currentTheme);

    // 等待 DOM 加载完成
    document.addEventListener('DOMContentLoaded', function() {
        const themeToggle = document.getElementById('theme-toggle');

        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                applyTheme(newTheme);
            });
        }
    });

    // 导出函数供其他模块使用
    window.themeManager = {
        getCurrentTheme: () => document.documentElement.getAttribute('data-theme'),
        applyTheme: applyTheme
    };
})();
