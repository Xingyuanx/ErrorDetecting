/**
 * 演示数据文件
 * 为各个页面提供模拟数据以展示功能
 */

// 演示数据管理器
class DemoDataManager {
    constructor() {
        this.initData();
    }

    // 初始化所有演示数据
    initData() {
        this.dashboardData = this.generateDashboardData();
        this.clusterData = this.generateClusterData();
        this.faultData = this.generateFaultData();
        this.logData = this.generateLogData();
        this.chartData = this.generateChartData();
    }

    // 生成仪表板数据
    generateDashboardData() {
        return {
            stats: {
                onlineNodes: 12,
                activeAlerts: 3,
                avgCpuUsage: 68,
                avgMemoryUsage: 45
            },
            recentAlerts: [
                {
                    id: 1,
                    title: 'CPU使用率过高',
                    node: 'node-01',
                    level: 'warning',
                    time: '2024-01-15 14:30:00'
                },
                {
                    id: 2,
                    title: '磁盘空间不足',
                    node: 'node-03',
                    level: 'error',
                    time: '2024-01-15 14:25:00'
                },
                {
                    id: 3,
                    title: '网络连接异常',
                    node: 'node-07',
                    level: 'warning',
                    time: '2024-01-15 14:20:00'
                }
            ]
        };
    }

    // 生成集群数据
    generateClusterData() {
        const nodes = [];
        const statuses = ['online', 'warning', 'offline'];
        const nodeTypes = ['master', 'worker', 'storage'];
        
        for (let i = 1; i <= 12; i++) {
            const nodeId = `node-${i.toString().padStart(2, '0')}`;
            const status = statuses[Math.floor(Math.random() * statuses.length)];
            
            nodes.push({
                id: nodeId,
                name: `节点 ${i}`,
                ip: `192.168.1.${100 + i}`,
                type: nodeTypes[Math.floor(Math.random() * nodeTypes.length)],
                status: status,
                cpu: Math.floor(Math.random() * 100),
                memory: Math.floor(Math.random() * 100),
                disk: Math.floor(Math.random() * 100),
                network: Math.floor(Math.random() * 1000),
                uptime: Math.floor(Math.random() * 30) + 1,
                lastUpdate: new Date(Date.now() - Math.random() * 300000).toLocaleString('zh-CN')
            });
        }

        return {
            overview: {
                total: nodes.length,
                online: nodes.filter(n => n.status === 'online').length,
                warning: nodes.filter(n => n.status === 'warning').length,
                offline: nodes.filter(n => n.status === 'offline').length,
                avgCpu: Math.floor(nodes.reduce((sum, n) => sum + n.cpu, 0) / nodes.length),
                cpuTrend: '+2.3%'
            },
            nodes: nodes
        };
    }

    // 生成故障数据
    generateFaultData() {
        const faults = [];
        const levels = ['critical', 'high', 'medium', 'low'];
        const types = ['hardware', 'software', 'network', 'security'];
        const statuses = ['open', 'in_progress', 'resolved', 'closed'];
        const assignees = ['张三', '李四', '王五', '赵六', '钱七'];

        for (let i = 1; i <= 50; i++) {
            const faultId = `F${Date.now().toString().slice(-6)}${i.toString().padStart(2, '0')}`;
            const level = levels[Math.floor(Math.random() * levels.length)];
            const type = types[Math.floor(Math.random() * types.length)];
            const status = statuses[Math.floor(Math.random() * statuses.length)];
            
            faults.push({
                id: faultId,
                title: this.generateFaultTitle(type),
                description: this.generateFaultDescription(type),
                level: level,
                type: type,
                status: status,
                assignee: assignees[Math.floor(Math.random() * assignees.length)],
                reporter: assignees[Math.floor(Math.random() * assignees.length)],
                node: `node-${Math.floor(Math.random() * 12) + 1}`,
                createdAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toLocaleString('zh-CN'),
                updatedAt: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toLocaleString('zh-CN'),
                resolvedAt: status === 'resolved' ? new Date(Date.now() - Math.random() * 12 * 60 * 60 * 1000).toLocaleString('zh-CN') : null
            });
        }

        return {
            overview: {
                total: faults.length,
                critical: faults.filter(f => f.level === 'critical').length,
                high: faults.filter(f => f.level === 'high').length,
                medium: faults.filter(f => f.level === 'medium').length,
                resolved: faults.filter(f => f.status === 'resolved').length
            },
            faults: faults
        };
    }

    // 生成日志数据
    generateLogData() {
        const logs = [];
        const levels = ['ERROR', 'WARN', 'INFO', 'DEBUG'];
        const services = ['api-gateway', 'user-service', 'order-service', 'payment-service', 'notification-service'];
        const hosts = ['host-01', 'host-02', 'host-03', 'host-04', 'host-05'];

        for (let i = 1; i <= 200; i++) {
            const level = levels[Math.floor(Math.random() * levels.length)];
            const service = services[Math.floor(Math.random() * services.length)];
            const host = hosts[Math.floor(Math.random() * hosts.length)];
            
            logs.push({
                id: i,
                timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
                level: level,
                service: service,
                host: host,
                message: this.generateLogMessage(level, service),
                details: this.generateLogDetails(level, service),
                userId: Math.random() > 0.7 ? `user_${Math.floor(Math.random() * 1000)}` : null,
                requestId: `req_${Math.random().toString(36).substr(2, 9)}`,
                ip: `192.168.1.${Math.floor(Math.random() * 255)}`
            });
        }

        return {
            overview: {
                total: logs.length,
                error: logs.filter(l => l.level === 'ERROR').length,
                warn: logs.filter(l => l.level === 'WARN').length,
                info: logs.filter(l => l.level === 'INFO').length,
                availability: '99.8%'
            },
            logs: logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        };
    }

    // 生成图表数据
    generateChartData() {
        return {
            // 性能趋势数据
            performanceTrend: DataGenerator.generateTimeSeriesData(24, 3),
            
            // CPU使用率数据
            cpuUsage: DataGenerator.generateTimeSeriesData(12, 1),
            
            // 内存使用率数据
            memoryUsage: DataGenerator.generateTimeSeriesData(12, 1),
            
            // 故障分布数据
            faultDistribution: DataGenerator.generatePieData(['硬件故障', '软件故障', '网络故障', '安全故障']),
            
            // 日志级别分布
            logLevelDistribution: DataGenerator.generatePieData(['ERROR', 'WARN', 'INFO', 'DEBUG']),
            
            // 服务日志分布
            serviceLogDistribution: DataGenerator.generateBarData(['api-gateway', 'user-service', 'order-service', 'payment-service'])
        };
    }

    // 生成故障标题
    generateFaultTitle(type) {
        const titles = {
            hardware: ['CPU温度过高', '内存故障', '硬盘损坏', '网卡故障', '电源异常'],
            software: ['应用程序崩溃', '服务无响应', '数据库连接失败', '配置错误', '版本冲突'],
            network: ['网络连接中断', '带宽不足', 'DNS解析失败', '路由异常', '防火墙阻断'],
            security: ['异常登录尝试', '权限提升攻击', '恶意文件检测', 'SQL注入尝试', '暴力破解']
        };
        
        const typeTitle = titles[type] || titles.software;
        return typeTitle[Math.floor(Math.random() * typeTitle.length)];
    }

    // 生成故障描述
    generateFaultDescription(type) {
        const descriptions = {
            hardware: '硬件设备出现异常，可能影响系统正常运行',
            software: '软件服务出现问题，需要及时处理以避免业务中断',
            network: '网络连接出现异常，可能影响服务间通信',
            security: '检测到安全威胁，需要立即采取防护措施'
        };
        
        return descriptions[type] || descriptions.software;
    }

    // 生成日志消息
    generateLogMessage(level, service) {
        const messages = {
            ERROR: [
                'Database connection failed',
                'Authentication failed for user',
                'Service timeout occurred',
                'Invalid request format',
                'Internal server error'
            ],
            WARN: [
                'High memory usage detected',
                'Slow query performance',
                'Rate limit approaching',
                'Cache miss ratio high',
                'Deprecated API usage'
            ],
            INFO: [
                'User login successful',
                'Request processed successfully',
                'Service started',
                'Configuration updated',
                'Backup completed'
            ],
            DEBUG: [
                'Processing request',
                'Cache hit',
                'Validation passed',
                'Query executed',
                'Response sent'
            ]
        };
        
        const levelMessages = messages[level] || messages.INFO;
        return `[${service}] ${levelMessages[Math.floor(Math.random() * levelMessages.length)]}`;
    }

    // 生成日志详情
    generateLogDetails(level, service) {
        return `详细信息: ${service} 服务在处理请求时出现 ${level} 级别的事件。请查看相关日志以获取更多信息。`;
    }

    // 获取仪表板数据
    getDashboardData() {
        return this.dashboardData;
    }

    // 获取集群数据
    getClusterData() {
        return this.clusterData;
    }

    // 获取故障数据
    getFaultData() {
        return this.faultData;
    }

    // 获取日志数据
    getLogData() {
        return this.logData;
    }

    // 获取图表数据
    getChartData() {
        return this.chartData;
    }

    // 模拟实时数据更新
    getRealtimeData() {
        const now = new Date();
        return {
            timestamp: now.toLocaleTimeString('zh-CN'),
            cpu: Math.floor(Math.random() * 100),
            memory: Math.floor(Math.random() * 100),
            network: Math.floor(Math.random() * 1000),
            activeConnections: Math.floor(Math.random() * 500)
        };
    }

    // 搜索故障
    searchFaults(query, filters = {}) {
        let results = [...this.faultData.faults];

        // 文本搜索
        if (query) {
            results = results.filter(fault => 
                fault.title.toLowerCase().includes(query.toLowerCase()) ||
                fault.description.toLowerCase().includes(query.toLowerCase()) ||
                fault.id.toLowerCase().includes(query.toLowerCase())
            );
        }

        // 级别筛选
        if (filters.level) {
            results = results.filter(fault => fault.level === filters.level);
        }

        // 状态筛选
        if (filters.status) {
            results = results.filter(fault => fault.status === filters.status);
        }

        // 类型筛选
        if (filters.type) {
            results = results.filter(fault => fault.type === filters.type);
        }

        return results;
    }

    // 搜索日志
    searchLogs(query, filters = {}) {
        let results = [...this.logData.logs];

        // 文本搜索
        if (query) {
            results = results.filter(log => 
                log.message.toLowerCase().includes(query.toLowerCase()) ||
                log.service.toLowerCase().includes(query.toLowerCase())
            );
        }

        // 级别筛选
        if (filters.level) {
            results = results.filter(log => log.level === filters.level);
        }

        // 服务筛选
        if (filters.service) {
            results = results.filter(log => log.service === filters.service);
        }

        // 主机筛选
        if (filters.host) {
            results = results.filter(log => log.host === filters.host);
        }

        // 时间范围筛选
        if (filters.startTime && filters.endTime) {
            const start = new Date(filters.startTime);
            const end = new Date(filters.endTime);
            results = results.filter(log => {
                const logTime = new Date(log.timestamp);
                return logTime >= start && logTime <= end;
            });
        }

        return results;
    }
}

// 创建全局实例
const demoData = new DemoDataManager();

// 导出到全局
window.DemoDataManager = DemoDataManager;
window.demoData = demoData;

console.log('演示数据管理器已加载');