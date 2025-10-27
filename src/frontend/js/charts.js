/**
 * 图表组件库
 * 基于Chart.js实现各种数据可视化图表
 */

// 图表基础配置
const ChartConfig = {
    // 默认颜色主题
    colors: {
        primary: '#3b82f6',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#06b6d4',
        secondary: '#6b7280'
    },
    
    // 图表默认配置
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: '#374151',
                borderWidth: 1,
                cornerRadius: 8,
                displayColors: true
            }
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(156, 163, 175, 0.1)'
                },
                ticks: {
                    color: '#6b7280'
                }
            },
            y: {
                grid: {
                    color: 'rgba(156, 163, 175, 0.1)'
                },
                ticks: {
                    color: '#6b7280'
                }
            }
        }
    }
};

// 线性图表组件
class LineChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.options = { ...ChartConfig.defaultOptions, ...options };
        this.chart = null;
        this.data = {
            labels: [],
            datasets: []
        };
    }

    // 初始化图表
    init(data, options = {}) {
        this.data = data;
        const config = {
            type: 'line',
            data: this.data,
            options: { ...this.options, ...options }
        };

        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new Chart(this.ctx, config);
        return this;
    }

    // 更新数据
    updateData(newData) {
        if (this.chart) {
            this.chart.data = newData;
            this.chart.update();
        }
        return this;
    }

    // 添加数据点
    addDataPoint(label, values) {
        if (this.chart) {
            this.chart.data.labels.push(label);
            values.forEach((value, index) => {
                if (this.chart.data.datasets[index]) {
                    this.chart.data.datasets[index].data.push(value);
                }
            });
            this.chart.update();
        }
        return this;
    }

    // 销毁图表
    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// 柱状图组件
class BarChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.options = { ...ChartConfig.defaultOptions, ...options };
        this.chart = null;
    }

    init(data, options = {}) {
        const config = {
            type: 'bar',
            data: data,
            options: { ...this.options, ...options }
        };

        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new Chart(this.ctx, config);
        return this;
    }

    updateData(newData) {
        if (this.chart) {
            this.chart.data = newData;
            this.chart.update();
        }
        return this;
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// 饼图组件
class PieChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.options = { 
            ...ChartConfig.defaultOptions, 
            ...options,
            scales: undefined // 饼图不需要坐标轴
        };
        this.chart = null;
    }

    init(data, options = {}) {
        const config = {
            type: 'pie',
            data: data,
            options: { ...this.options, ...options }
        };

        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new Chart(this.ctx, config);
        return this;
    }

    updateData(newData) {
        if (this.chart) {
            this.chart.data = newData;
            this.chart.update();
        }
        return this;
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// 环形图组件
class DoughnutChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.options = { 
            ...ChartConfig.defaultOptions, 
            ...options,
            scales: undefined // 环形图不需要坐标轴
        };
        this.chart = null;
    }

    init(data, options = {}) {
        const config = {
            type: 'doughnut',
            data: data,
            options: { ...this.options, ...options }
        };

        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new Chart(this.ctx, config);
        return this;
    }

    updateData(newData) {
        if (this.chart) {
            this.chart.data = newData;
            this.chart.update();
        }
        return this;
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// 实时图表组件（用于监控数据）
class RealTimeChart extends LineChart {
    constructor(canvasId, options = {}) {
        super(canvasId, options);
        this.maxDataPoints = options.maxDataPoints || 50;
        this.updateInterval = options.updateInterval || 5000;
        this.isRunning = false;
        this.intervalId = null;
    }

    // 开始实时更新
    start(dataCallback) {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.intervalId = setInterval(() => {
            if (typeof dataCallback === 'function') {
                const newData = dataCallback();
                this.addRealTimeData(newData);
            }
        }, this.updateInterval);
    }

    // 停止实时更新
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.isRunning = false;
    }

    // 添加实时数据
    addRealTimeData(data) {
        if (!this.chart) return;

        const { label, values } = data;
        
        // 添加新数据点
        this.chart.data.labels.push(label);
        values.forEach((value, index) => {
            if (this.chart.data.datasets[index]) {
                this.chart.data.datasets[index].data.push(value);
            }
        });

        // 限制数据点数量
        if (this.chart.data.labels.length > this.maxDataPoints) {
            this.chart.data.labels.shift();
            this.chart.data.datasets.forEach(dataset => {
                dataset.data.shift();
            });
        }

        this.chart.update('none'); // 无动画更新，提高性能
    }

    destroy() {
        this.stop();
        super.destroy();
    }
}

// 图表工厂类
class ChartFactory {
    static createLineChart(canvasId, data, options = {}) {
        const chart = new LineChart(canvasId, options);
        return chart.init(data, options);
    }

    static createBarChart(canvasId, data, options = {}) {
        const chart = new BarChart(canvasId, options);
        return chart.init(data, options);
    }

    static createPieChart(canvasId, data, options = {}) {
        const chart = new PieChart(canvasId, options);
        return chart.init(data, options);
    }

    static createDoughnutChart(canvasId, data, options = {}) {
        const chart = new DoughnutChart(canvasId, options);
        return chart.init(data, options);
    }

    static createRealTimeChart(canvasId, data, options = {}) {
        const chart = new RealTimeChart(canvasId, options);
        return chart.init(data, options);
    }
}

// 数据生成器（用于演示）
class DataGenerator {
    // 生成时间序列数据
    static generateTimeSeriesData(hours = 24, datasets = 1) {
        const labels = [];
        const now = new Date();
        
        for (let i = hours - 1; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            labels.push(time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }));
        }

        const datasetsArray = [];
        const colors = [
            ChartConfig.colors.primary,
            ChartConfig.colors.success,
            ChartConfig.colors.warning,
            ChartConfig.colors.danger
        ];

        for (let i = 0; i < datasets; i++) {
            datasetsArray.push({
                label: `数据集 ${i + 1}`,
                data: Array.from({ length: hours }, () => Math.floor(Math.random() * 100)),
                borderColor: colors[i % colors.length],
                backgroundColor: colors[i % colors.length] + '20',
                fill: false,
                tension: 0.4
            });
        }

        return { labels, datasets: datasetsArray };
    }

    // 生成饼图数据
    static generatePieData(categories) {
        const colors = [
            ChartConfig.colors.primary,
            ChartConfig.colors.success,
            ChartConfig.colors.warning,
            ChartConfig.colors.danger,
            ChartConfig.colors.info,
            ChartConfig.colors.secondary
        ];

        return {
            labels: categories,
            datasets: [{
                data: categories.map(() => Math.floor(Math.random() * 100) + 10),
                backgroundColor: colors.slice(0, categories.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        };
    }

    // 生成柱状图数据
    static generateBarData(categories, datasets = 1) {
        const colors = [
            ChartConfig.colors.primary,
            ChartConfig.colors.success,
            ChartConfig.colors.warning,
            ChartConfig.colors.danger
        ];

        const datasetsArray = [];
        for (let i = 0; i < datasets; i++) {
            datasetsArray.push({
                label: `数据集 ${i + 1}`,
                data: categories.map(() => Math.floor(Math.random() * 100)),
                backgroundColor: colors[i % colors.length],
                borderColor: colors[i % colors.length],
                borderWidth: 1
            });
        }

        return {
            labels: categories,
            datasets: datasetsArray
        };
    }
}

// 导出到全局
window.ChartConfig = ChartConfig;
window.LineChart = LineChart;
window.BarChart = BarChart;
window.PieChart = PieChart;
window.DoughnutChart = DoughnutChart;
window.RealTimeChart = RealTimeChart;
window.ChartFactory = ChartFactory;
window.DataGenerator = DataGenerator;

console.log('图表组件库已加载');