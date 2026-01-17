/**
 * ECharts 图表配置模块
 * 提供各种金融图表的配置工厂函数
 */

(function() {
    'use strict';

    // 存储所有图表实例，用于主题切换时重新渲染
    window.echartsInstances = [];

    /**
     * 获取当前主题的颜色配置
     */
    function getThemeColors() {
        const root = document.documentElement;
        const style = getComputedStyle(root);

        return {
            textColor: style.getPropertyValue('--text-primary').trim(),
            textSecondary: style.getPropertyValue('--text-secondary').trim(),
            gridColor: style.getPropertyValue('--chart-grid').trim(),
            axisColor: style.getPropertyValue('--chart-axis').trim(),
            colorUp: style.getPropertyValue('--color-up').trim(),
            colorDown: style.getPropertyValue('--color-down').trim(),
            colorPrimary: style.getPropertyValue('--color-primary').trim(),
            colorWarning: style.getPropertyValue('--color-warning').trim()
        };
    }

    const Charts = {
        /**
         * 创建 K线图（蜡烛图）
         * @param {string} containerId - 容器 ID
         * @param {Object} data - 数据对象
         * @returns {Object} ECharts 实例
         */
        createCandlestickChart: function(containerId, data) {
            const colors = getThemeColors();
            const container = document.getElementById(containerId);
            if (!container) return null;

            const chart = echarts.init(container);

            // 准备数据
            const dates = data.map(d => d.date);
            const values = data.map(d => [d.open, d.close, d.low, d.high]);
            const volumes = data.map(d => d.volume);

            const option = {
                backgroundColor: 'transparent',
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'cross' },
                    backgroundColor: 'rgba(50, 50, 50, 0.9)',
                    borderColor: colors.gridColor,
                    textStyle: { color: colors.textColor }
                },
                legend: {
                    data: ['日K', '成交量'],
                    textStyle: { color: colors.textColor }
                },
                grid: [
                    { left: '10%', right: '10%', height: '50%' },
                    { left: '10%', right: '10%', top: '70%', height: '15%' }
                ],
                xAxis: [
                    {
                        type: 'category',
                        data: dates,
                        scale: true,
                        boundaryGap: false,
                        axisLine: { lineStyle: { color: colors.axisColor } },
                        axisLabel: { color: colors.textSecondary },
                        splitLine: { show: false },
                        min: 'dataMin',
                        max: 'dataMax'
                    },
                    {
                        type: 'category',
                        gridIndex: 1,
                        data: dates,
                        axisLabel: { show: false }
                    }
                ],
                yAxis: [
                    {
                        scale: true,
                        splitLine: { lineStyle: { color: colors.gridColor } },
                        axisLabel: { color: colors.textSecondary }
                    },
                    {
                        scale: true,
                        gridIndex: 1,
                        splitNumber: 2,
                        axisLabel: { show: false },
                        axisLine: { show: false },
                        axisTick: { show: false },
                        splitLine: { show: false }
                    }
                ],
                series: [
                    {
                        name: '日K',
                        type: 'candlestick',
                        data: values,
                        itemStyle: {
                            color: colors.colorUp,
                            color0: colors.colorDown,
                            borderColor: colors.colorUp,
                            borderColor0: colors.colorDown
                        }
                    },
                    {
                        name: '成交量',
                        type: 'bar',
                        xAxisIndex: 1,
                        yAxisIndex: 1,
                        data: volumes,
                        itemStyle: {
                            color: function(params) {
                                const dataIndex = params.dataIndex;
                                return values[dataIndex][1] > values[dataIndex][0] ?
                                    colors.colorUp : colors.colorDown;
                            }
                        }
                    }
                ]
            };

            chart.setOption(option);
            window.echartsInstances.push(chart);

            // 响应式
            window.addEventListener('resize', () => chart.resize());

            return chart;
        },

        /**
         * 创建仪表盘图表（RSI、情绪分析）
         * @param {string} containerId - 容器 ID
         * @param {number} value - 数值 (0-100)
         * @param {string} title - 标题
         * @returns {Object} ECharts 实例
         */
        createGaugeChart: function(containerId, value, title) {
            const colors = getThemeColors();
            const container = document.getElementById(containerId);
            if (!container) return null;

            const chart = echarts.init(container);

            const option = {
                backgroundColor: 'transparent',
                series: [{
                    type: 'gauge',
                    startAngle: 180,
                    endAngle: 0,
                    min: 0,
                    max: 100,
                    splitNumber: 10,
                    axisLine: {
                        lineStyle: {
                            width: 20,
                            color: [
                                [0.3, colors.colorDown],
                                [0.7, colors.colorWarning],
                                [1, colors.colorUp]
                            ]
                        }
                    },
                    pointer: {
                        itemStyle: { color: 'auto' }
                    },
                    axisTick: {
                        distance: -20,
                        length: 5,
                        lineStyle: { color: '#fff', width: 1 }
                    },
                    splitLine: {
                        distance: -20,
                        length: 20,
                        lineStyle: { color: '#fff', width: 2 }
                    },
                    axisLabel: {
                        color: colors.textSecondary,
                        distance: 25,
                        fontSize: 12
                    },
                    detail: {
                        valueAnimation: true,
                        formatter: '{value}',
                        color: colors.textColor,
                        fontSize: 30,
                        offsetCenter: [0, '0%']
                    },
                    title: {
                        show: true,
                        offsetCenter: [0, '80%'],
                        fontSize: 16,
                        color: colors.textColor
                    },
                    data: [{ value: value, name: title }]
                }]
            };

            chart.setOption(option);
            window.echartsInstances.push(chart);

            window.addEventListener('resize', () => chart.resize());

            return chart;
        },

        /**
         * 创建柱状图（机会评分排行）
         * @param {string} containerId - 容器 ID
         * @param {Object} data - 数据对象 {tickers: [], scores: []}
         * @returns {Object} ECharts 实例
         */
        createBarChart: function(containerId, data) {
            const colors = getThemeColors();
            const container = document.getElementById(containerId);
            if (!container) return null;

            const chart = echarts.init(container);

            const option = {
                backgroundColor: 'transparent',
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'shadow' },
                    backgroundColor: 'rgba(50, 50, 50, 0.9)',
                    borderColor: colors.gridColor,
                    textStyle: { color: colors.textColor }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: data.tickers,
                    axisLabel: { color: colors.textSecondary },
                    axisLine: { lineStyle: { color: colors.axisColor } }
                },
                yAxis: {
                    type: 'value',
                    name: '机会评分',
                    nameTextStyle: { color: colors.textSecondary },
                    axisLabel: { color: colors.textSecondary },
                    splitLine: { lineStyle: { color: colors.gridColor } }
                },
                series: [{
                    name: '评分',
                    type: 'bar',
                    data: data.scores,
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: colors.colorUp },
                            { offset: 1, color: colors.colorPrimary }
                        ])
                    },
                    label: {
                        show: true,
                        position: 'top',
                        color: colors.textSecondary
                    }
                }]
            };

            chart.setOption(option);
            window.echartsInstances.push(chart);

            window.addEventListener('resize', () => chart.resize());

            return chart;
        },

        /**
         * 创建饼图（行业分布）
         * @param {string} containerId - 容器 ID
         * @param {Object} data - 数据对象 {name: count}
         * @returns {Object} ECharts 实例
         */
        createPieChart: function(containerId, data) {
            const colors = getThemeColors();
            const container = document.getElementById(containerId);
            if (!container) return null;

            const chart = echarts.init(container);

            // 转换数据格式
            const pieData = Object.entries(data).map(([name, value]) => ({
                name, value
            }));

            const option = {
                backgroundColor: 'transparent',
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c} ({d}%)',
                    backgroundColor: 'rgba(50, 50, 50, 0.9)',
                    borderColor: colors.gridColor,
                    textStyle: { color: colors.textColor }
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    textStyle: { color: colors.textColor }
                },
                series: [{
                    type: 'pie',
                    radius: '60%',
                    data: pieData,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    },
                    label: {
                        color: colors.textSecondary
                    }
                }]
            };

            chart.setOption(option);
            window.echartsInstances.push(chart);

            window.addEventListener('resize', () => chart.resize());

            return chart;
        },

        /**
         * 销毁所有图表实例
         */
        disposeAll: function() {
            window.echartsInstances.forEach(chart => {
                if (chart && !chart.isDisposed()) {
                    chart.dispose();
                }
            });
            window.echartsInstances = [];
        }
    };

    // 导出到全局作用域
    window.Charts = Charts;
})();
