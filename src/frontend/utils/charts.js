/**
 * 图表管理工具类
 * 负责初始化和管理 ECharts 图表实例
 */
class ChartManager {
    constructor() {
        this.charts = new Map(); // 存储图表实例
        this.init();
    }

    /**
     * 初始化所有图表
     */
    init() {
        // 等待 DOM 加载完成后初始化图表
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initAllCharts();
            });
        } else {
            this.initAllCharts();
        }
    }

    /**
     * 初始化所有图表
     */
    initAllCharts() {
        this.initCpuChart();
        this.initMemoryChart();
        
        // 监听窗口大小变化，自动调整图表大小
        window.addEventListener('resize', () => {
            this.resizeAllCharts();
        });
    }

    /**
     * 初始化 CPU 使用率趋势图
     */
    initCpuChart() {
        const chartElement = document.getElementById('cpuChart');
        if (!chartElement) return;

        const chart = echarts.init(chartElement);
        
        // CPU 使用率图表配置
        const option = {
            title: {
                text: 'CPU 使用率 (%)',
                textStyle: {
                    fontSize: 14,
                    fontWeight: 'normal',
                    color: '#374151'
                }
            },
            tooltip: {
                trigger: 'axis',
                formatter: function(params) {
                    const data = params[0];
                    return `${data.name}<br/>CPU 使用率: ${data.value}%`;
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
                axisLine: {
                    lineStyle: {
                        color: '#E5E7EB'
                    }
                },
                axisLabel: {
                    color: '#6B7280'
                }
            },
            yAxis: {
                type: 'value',
                min: 0,
                max: 100,
                axisLine: {
                    lineStyle: {
                        color: '#E5E7EB'
                    }
                },
                axisLabel: {
                    color: '#6B7280',
                    formatter: '{value}%'
                },
                splitLine: {
                    lineStyle: {
                        color: '#F3F4F6'
                    }
                }
            },
            series: [{
                name: 'CPU 使用率',
                type: 'line',
                smooth: true,
                data: [20, 35, 45, 60, 55, 40, 30],
                lineStyle: {
                    color: '#3B82F6',
                    width: 2
                },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [{
                            offset: 0,
                            color: 'rgba(59, 130, 246, 0.3)'
                        }, {
                            offset: 1,
                            color: 'rgba(59, 130, 246, 0.05)'
                        }]
                    }
                },
                itemStyle: {
                    color: '#3B82F6'
                }
            }]
        };

        chart.setOption(option);
        this.charts.set('cpu', chart);
    }

    /**
     * 初始化内存使用情况图
     */
    initMemoryChart() {
        const chartElement = document.getElementById('memoryChart');
        if (!chartElement) return;

        const chart = echarts.init(chartElement);
        
        // 内存使用情况图表配置
        const option = {
            title: {
                text: '内存使用情况',
                textStyle: {
                    fontSize: 14,
                    fontWeight: 'normal',
                    color: '#374151'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: function(params) {
                    return `${params.name}<br/>使用量: ${params.value} GB (${params.percent}%)`;
                }
            },
            legend: {
                orient: 'horizontal',
                bottom: '0%',
                textStyle: {
                    color: '#6B7280'
                }
            },
            series: [{
                name: '内存使用',
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['50%', '45%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 4,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false,
                    position: 'center'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: '16',
                        fontWeight: 'bold',
                        color: '#374151'
                    }
                },
                labelLine: {
                    show: false
                },
                data: [
                    {
                        value: 8.5,
                        name: '已使用',
                        itemStyle: {
                            color: '#EF4444'
                        }
                    },
                    {
                        value: 15.5,
                        name: '可用',
                        itemStyle: {
                            color: '#10B981'
                        }
                    }
                ]
            }]
        };

        chart.setOption(option);
        this.charts.set('memory', chart);
    }

    /**
     * 调整所有图表大小
     */
    resizeAllCharts() {
        this.charts.forEach(chart => {
            chart.resize();
        });
    }

    /**
     * 更新 CPU 图表数据
     * @param {Array} data - 新的数据数组
     */
    updateCpuChart(data) {
        const chart = this.charts.get('cpu');
        if (chart && data) {
            chart.setOption({
                series: [{
                    data: data
                }]
            });
        }
    }

    /**
     * 更新内存图表数据
     * @param {Object} data - 内存使用数据 {used: number, available: number}
     */
    updateMemoryChart(data) {
        const chart = this.charts.get('memory');
        if (chart && data) {
            chart.setOption({
                series: [{
                    data: [
                        {
                            value: data.used,
                            name: '已使用',
                            itemStyle: {
                                color: '#EF4444'
                            }
                        },
                        {
                            value: data.available,
                            name: '可用',
                            itemStyle: {
                                color: '#10B981'
                            }
                        }
                    ]
                }]
            });
        }
    }

    /**
     * 销毁所有图表实例
     */
    dispose() {
        this.charts.forEach(chart => {
            chart.dispose();
        });
        this.charts.clear();
    }
}

// 创建全局图表管理器实例
window.chartManager = new ChartManager();