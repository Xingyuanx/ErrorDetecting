-- =====================================================
-- 故障检测系统数据库建表脚本
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4
-- 创建时间: 2024年
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS hadoop_fault_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE hadoop_fault_db;

-- =====================================================
-- 1. 核心业务表
-- =====================================================

-- 1.1 故障记录表
DROP TABLE IF EXISTS fault_records;
CREATE TABLE fault_records (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    fault_id VARCHAR(32) NOT NULL COMMENT '故障唯一标识',
    fault_type VARCHAR(50) NOT NULL COMMENT '故障类型',
    fault_level ENUM('low', 'medium', 'high', 'critical') NOT NULL DEFAULT 'medium' COMMENT '故障级别',
    title VARCHAR(200) NOT NULL COMMENT '故障标题',
    description TEXT COMMENT '故障详细描述',
    affected_nodes JSON COMMENT '受影响的节点列表',
    source_logs JSON COMMENT '相关日志ID列表',
    root_cause TEXT COMMENT '根本原因分析',
    repair_suggestion TEXT COMMENT '修复建议',
    status ENUM('detected', 'analyzing', 'repairing', 'resolved', 'failed') NOT NULL DEFAULT 'detected' COMMENT '状态',
    assignee VARCHAR(50) COMMENT '负责人',
    reporter VARCHAR(50) DEFAULT 'system' COMMENT '报告人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    resolved_at TIMESTAMP NULL COMMENT '解决时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_fault_id (fault_id),
    KEY idx_fault_type (fault_type),
    KEY idx_fault_level (fault_level),
    KEY idx_status (status),
    KEY idx_created_at (created_at),
    KEY idx_assignee (assignee)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='故障记录表';

-- 1.2 执行日志表
DROP TABLE IF EXISTS exec_logs;
CREATE TABLE exec_logs (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    exec_id VARCHAR(32) NOT NULL COMMENT '执行唯一标识',
    fault_id VARCHAR(32) NOT NULL COMMENT '关联故障ID',
    command_type VARCHAR(50) NOT NULL COMMENT '命令类型',
    script_path VARCHAR(255) COMMENT '脚本路径',
    command_content TEXT NOT NULL COMMENT '执行的命令内容',
    target_nodes JSON COMMENT '目标执行节点',
    risk_level ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium' COMMENT '风险级别',
    execution_status ENUM('pending', 'running', 'success', 'failed', 'timeout') NOT NULL DEFAULT 'pending' COMMENT '执行状态',
    start_time TIMESTAMP NULL COMMENT '开始执行时间',
    end_time TIMESTAMP NULL COMMENT '结束执行时间',
    duration INT COMMENT '执行时长(秒)',
    stdout_log LONGTEXT COMMENT '标准输出日志',
    stderr_log LONGTEXT COMMENT '错误输出日志',
    exit_code INT COMMENT '退出码',
    operator VARCHAR(50) DEFAULT 'system' COMMENT '操作人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_exec_id (exec_id),
    KEY idx_fault_id (fault_id),
    KEY idx_execution_status (execution_status),
    KEY idx_start_time (start_time),
    KEY idx_operator (operator)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行日志表';

-- 1.3 集群状态表
DROP TABLE IF EXISTS cluster_status;
CREATE TABLE cluster_status (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    node_id VARCHAR(50) NOT NULL COMMENT '节点标识',
    node_name VARCHAR(100) NOT NULL COMMENT '节点名称',
    ip_address VARCHAR(15) NOT NULL COMMENT 'IP地址',
    node_role ENUM('NameNode', 'DataNode', 'ResourceManager', 'NodeManager') NOT NULL COMMENT '节点角色',
    node_status ENUM('online', 'offline', 'maintenance', 'unknown') NOT NULL DEFAULT 'unknown' COMMENT '节点状态',
    cpu_usage DECIMAL(5,2) COMMENT 'CPU使用率(%)',
    memory_usage DECIMAL(5,2) COMMENT '内存使用率(%)',
    disk_usage DECIMAL(5,2) COMMENT '磁盘使用率(%)',
    network_io BIGINT COMMENT '网络IO(bytes/s)',
    disk_io BIGINT COMMENT '磁盘IO(bytes/s)',
    load_average DECIMAL(5,2) COMMENT '系统负载',
    uptime BIGINT COMMENT '运行时间(秒)',
    last_heartbeat TIMESTAMP COMMENT '最后心跳时间',
    health_score INT DEFAULT 100 COMMENT '健康评分(0-100)',
    alerts_count INT NOT NULL DEFAULT 0 COMMENT '告警数量',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_node_id (node_id),
    KEY idx_node_role (node_role),
    KEY idx_node_status (node_status),
    KEY idx_last_heartbeat (last_heartbeat),
    KEY idx_health_score (health_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='集群状态表';

-- 1.4 系统日志表
DROP TABLE IF EXISTS system_logs;
CREATE TABLE system_logs (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    log_id VARCHAR(32) NOT NULL COMMENT '日志唯一标识',
    timestamp TIMESTAMP NOT NULL COMMENT '日志时间戳',
    host VARCHAR(100) NOT NULL COMMENT '主机名',
    ip_address VARCHAR(15) NOT NULL COMMENT 'IP地址',
    service VARCHAR(50) NOT NULL COMMENT '服务名',
    component VARCHAR(50) COMMENT '组件名',
    log_level ENUM('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL') NOT NULL COMMENT '日志级别',
    thread VARCHAR(100) COMMENT '线程名',
    logger VARCHAR(200) COMMENT 'Logger名称',
    message LONGTEXT NOT NULL COMMENT '日志消息',
    exception LONGTEXT COMMENT '异常堆栈',
    raw_log LONGTEXT COMMENT '原始日志内容',
    tags JSON COMMENT '标签信息',
    processed BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已处理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_log_id (log_id),
    KEY idx_timestamp (timestamp),
    KEY idx_host (host),
    KEY idx_service (service),
    KEY idx_log_level (log_level),
    KEY idx_processed (processed),
    KEY idx_timestamp_level (timestamp, log_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志表';

-- =====================================================
-- 2. 配置管理表
-- =====================================================

-- 2.1 系统配置表
DROP TABLE IF EXISTS system_configs;
CREATE TABLE system_configs (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    config_key VARCHAR(100) NOT NULL COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_type VARCHAR(20) NOT NULL DEFAULT 'string' COMMENT '配置类型',
    category VARCHAR(50) NOT NULL COMMENT '配置分类',
    description VARCHAR(500) COMMENT '配置描述',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_config_key (config_key),
    KEY idx_category (category),
    KEY idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 2.2 告警规则表
DROP TABLE IF EXISTS alert_rules;
CREATE TABLE alert_rules (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    rule_name VARCHAR(100) NOT NULL COMMENT '规则名称',
    rule_type VARCHAR(50) NOT NULL COMMENT '规则类型',
    metric_name VARCHAR(100) NOT NULL COMMENT '监控指标名',
    condition_expr TEXT NOT NULL COMMENT '条件表达式',
    threshold_value DECIMAL(10,2) COMMENT '阈值',
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL DEFAULT 'medium' COMMENT '严重级别',
    description TEXT COMMENT '规则描述',
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    KEY idx_rule_type (rule_type),
    KEY idx_metric_name (metric_name),
    KEY idx_severity (severity),
    KEY idx_is_enabled (is_enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='告警规则表';

-- =====================================================
-- 3. 用户管理表
-- =====================================================

-- 3.1 用户表
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    full_name VARCHAR(100) NOT NULL COMMENT '姓名',
    role ENUM('admin', 'operator', 'viewer') NOT NULL DEFAULT 'operator' COMMENT '角色',
    department VARCHAR(100) COMMENT '部门',
    phone VARCHAR(20) COMMENT '电话',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email),
    KEY idx_role (role),
    KEY idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 3.2 操作审计表
DROP TABLE IF EXISTS audit_logs;
CREATE TABLE audit_logs (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    action VARCHAR(100) NOT NULL COMMENT '操作动作',
    resource_type VARCHAR(50) NOT NULL COMMENT '资源类型',
    resource_id VARCHAR(100) COMMENT '资源ID',
    ip_address VARCHAR(15) NOT NULL COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    request_data JSON COMMENT '请求数据',
    response_status INT COMMENT '响应状态码',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    PRIMARY KEY (id),
    KEY idx_user_id (user_id),
    KEY idx_username (username),
    KEY idx_action (action),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作审计表';

-- =====================================================
-- 4. 扩展表
-- =====================================================

-- 4.1 修复脚本模板表
DROP TABLE IF EXISTS repair_templates;
CREATE TABLE repair_templates (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    template_name VARCHAR(100) NOT NULL COMMENT '模板名称',
    fault_type VARCHAR(50) NOT NULL COMMENT '适用故障类型',
    script_content TEXT NOT NULL COMMENT '脚本内容',
    risk_level ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium' COMMENT '风险级别',
    description TEXT COMMENT '模板描述',
    parameters JSON COMMENT '参数定义',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    created_by VARCHAR(50) COMMENT '创建人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    KEY idx_fault_type (fault_type),
    KEY idx_risk_level (risk_level),
    KEY idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='修复脚本模板表';

-- 4.2 通知配置表
DROP TABLE IF EXISTS notification_configs;
CREATE TABLE notification_configs (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    config_name VARCHAR(100) NOT NULL COMMENT '配置名称',
    notification_type ENUM('email', 'sms', 'webhook', 'dingtalk') NOT NULL COMMENT '通知类型',
    trigger_conditions JSON NOT NULL COMMENT '触发条件',
    recipients JSON NOT NULL COMMENT '接收人列表',
    template_content TEXT COMMENT '通知模板',
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    KEY idx_notification_type (notification_type),
    KEY idx_is_enabled (is_enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知配置表';

-- =====================================================
-- 5. 外键约束
-- =====================================================

-- 执行日志表关联故障记录表
ALTER TABLE exec_logs 
ADD CONSTRAINT fk_exec_logs_fault_id 
FOREIGN KEY (fault_id) REFERENCES fault_records(fault_id) 
ON DELETE CASCADE ON UPDATE CASCADE;

-- 审计日志表关联用户表
ALTER TABLE audit_logs 
ADD CONSTRAINT fk_audit_logs_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) 
ON DELETE SET NULL ON UPDATE CASCADE;

-- =====================================================
-- 6. 初始化数据
-- =====================================================

-- 插入默认系统配置
INSERT INTO system_configs (config_key, config_value, config_type, category, description) VALUES
('system.name', '故障检测系统', 'string', 'system', '系统名称'),
('log.retention.days', '90', 'int', 'log', '日志保留天数'),
('alert.email.enabled', 'true', 'boolean', 'alert', '是否启用邮件告警'),
('repair.auto.enabled', 'false', 'boolean', 'repair', '是否启用自动修复'),
('cluster.check.interval', '300', 'int', 'cluster', '集群检查间隔(秒)'),
('llm.api.timeout', '30', 'int', 'llm', 'LLM API超时时间(秒)'),
('repair.max.concurrent', '3', 'int', 'repair', '最大并发修复数量');

-- 插入默认告警规则
INSERT INTO alert_rules (rule_name, rule_type, metric_name, condition_expr, threshold_value, severity, description, is_enabled) VALUES
('CPU使用率过高', 'threshold', 'cpu_usage', 'cpu_usage > threshold_value', 85.00, 'high', 'CPU使用率超过85%时触发告警', TRUE),
('内存使用率过高', 'threshold', 'memory_usage', 'memory_usage > threshold_value', 90.00, 'high', '内存使用率超过90%时触发告警', TRUE),
('磁盘使用率过高', 'threshold', 'disk_usage', 'disk_usage > threshold_value', 85.00, 'medium', '磁盘使用率超过85%时触发告警', TRUE),
('节点离线', 'pattern', 'node_status', 'node_status = "offline"', NULL, 'critical', '节点离线时触发告警', TRUE),
('DataNode心跳异常', 'pattern', 'last_heartbeat', 'TIMESTAMPDIFF(MINUTE, last_heartbeat, NOW()) > 5', NULL, 'high', 'DataNode超过5分钟无心跳时触发告警', TRUE);

-- 插入默认管理员用户 (密码: admin123)
INSERT INTO users (username, email, password_hash, full_name, role, department, is_active) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', '系统管理员', 'admin', 'IT部门', TRUE),
('operator', 'operator@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', '运维工程师', 'operator', 'IT部门', TRUE);

-- 插入修复脚本模板
INSERT INTO repair_templates (template_name, fault_type, script_content, risk_level, description, parameters) VALUES
('重启DataNode服务', 'DataNode离线', 'sudo systemctl restart hadoop-hdfs-datanode', 'medium', '重启DataNode服务以恢复连接', '{"node_id": "string"}'),
('清理临时文件', '磁盘空间不足', 'sudo rm -rf /tmp/hadoop-* && sudo rm -rf /var/log/hadoop/*.log.* && sudo hdfs dfsadmin -refreshNodes', 'low', '清理Hadoop临时文件和旧日志', '{"node_id": "string", "cleanup_path": "string"}'),
('重启NameNode服务', 'NameNode异常', 'sudo systemctl stop hadoop-hdfs-namenode && sleep 10 && sudo systemctl start hadoop-hdfs-namenode', 'high', '重启NameNode服务，高风险操作', '{"backup_required": "boolean"}');

-- =====================================================
-- 7. 视图定义
-- =====================================================

-- 故障统计视图
CREATE OR REPLACE VIEW v_fault_statistics AS
SELECT 
    DATE(created_at) as fault_date,
    fault_level,
    fault_type,
    status,
    COUNT(*) as fault_count,
    AVG(CASE WHEN resolved_at IS NOT NULL 
        THEN TIMESTAMPDIFF(MINUTE, created_at, resolved_at) 
        ELSE NULL END) as avg_resolution_time_minutes
FROM fault_records 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(created_at), fault_level, fault_type, status;

-- 集群健康度视图
CREATE OR REPLACE VIEW v_cluster_health AS
SELECT 
    node_role,
    COUNT(*) as total_nodes,
    SUM(CASE WHEN node_status = 'online' THEN 1 ELSE 0 END) as online_nodes,
    AVG(cpu_usage) as avg_cpu_usage,
    AVG(memory_usage) as avg_memory_usage,
    AVG(disk_usage) as avg_disk_usage,
    AVG(health_score) as avg_health_score
FROM cluster_status 
GROUP BY node_role;

-- 执行成功率视图
CREATE OR REPLACE VIEW v_execution_success_rate AS
SELECT 
    DATE(created_at) as exec_date,
    command_type,
    COUNT(*) as total_executions,
    SUM(CASE WHEN execution_status = 'success' THEN 1 ELSE 0 END) as successful_executions,
    ROUND(SUM(CASE WHEN execution_status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM exec_logs 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(created_at), command_type;

-- =====================================================
-- 8. 存储过程
-- =====================================================

DELIMITER //

-- 创建故障记录的存储过程
CREATE PROCEDURE sp_create_fault_record(
    IN p_fault_type VARCHAR(50),
    IN p_fault_level ENUM('low', 'medium', 'high', 'critical'),
    IN p_title VARCHAR(200),
    IN p_description TEXT,
    IN p_affected_nodes JSON,
    IN p_source_logs JSON,
    OUT p_fault_id VARCHAR(32)
)
BEGIN
    DECLARE v_fault_id VARCHAR(32);
    
    -- 生成故障ID
    SET v_fault_id = CONCAT('FLT-', DATE_FORMAT(NOW(), '%Y%m%d'), '-', LPAD(FLOOR(RAND() * 10000), 4, '0'));
    
    -- 插入故障记录
    INSERT INTO fault_records (
        fault_id, fault_type, fault_level, title, description, 
        affected_nodes, source_logs, status, reporter
    ) VALUES (
        v_fault_id, p_fault_type, p_fault_level, p_title, p_description,
        p_affected_nodes, p_source_logs, 'detected', 'system'
    );
    
    SET p_fault_id = v_fault_id;
END //

-- 更新集群状态的存储过程
CREATE PROCEDURE sp_update_cluster_status(
    IN p_node_id VARCHAR(50),
    IN p_node_name VARCHAR(100),
    IN p_ip_address VARCHAR(15),
    IN p_node_role ENUM('NameNode', 'DataNode', 'ResourceManager', 'NodeManager'),
    IN p_node_status ENUM('online', 'offline', 'maintenance', 'unknown'),
    IN p_cpu_usage DECIMAL(5,2),
    IN p_memory_usage DECIMAL(5,2),
    IN p_disk_usage DECIMAL(5,2),
    IN p_health_score INT
)
BEGIN
    INSERT INTO cluster_status (
        node_id, node_name, ip_address, node_role, node_status,
        cpu_usage, memory_usage, disk_usage, health_score, last_heartbeat
    ) VALUES (
        p_node_id, p_node_name, p_ip_address, p_node_role, p_node_status,
        p_cpu_usage, p_memory_usage, p_disk_usage, p_health_score, NOW()
    )
    ON DUPLICATE KEY UPDATE
        node_name = p_node_name,
        ip_address = p_ip_address,
        node_role = p_node_role,
        node_status = p_node_status,
        cpu_usage = p_cpu_usage,
        memory_usage = p_memory_usage,
        disk_usage = p_disk_usage,
        health_score = p_health_score,
        last_heartbeat = NOW(),
        updated_at = NOW();
END //

DELIMITER ;

-- =====================================================
-- 9. 触发器
-- =====================================================

DELIMITER //

-- 故障记录状态变更触发器
CREATE TRIGGER tr_fault_status_change 
AFTER UPDATE ON fault_records
FOR EACH ROW
BEGIN
    -- 当故障状态变为已解决时，记录解决时间
    IF NEW.status = 'resolved' AND OLD.status != 'resolved' THEN
        UPDATE fault_records 
        SET resolved_at = NOW() 
        WHERE id = NEW.id;
    END IF;
    
    -- 记录审计日志
    INSERT INTO audit_logs (
        username, action, resource_type, resource_id, 
        ip_address, request_data
    ) VALUES (
        COALESCE(NEW.assignee, 'system'), 
        'UPDATE_FAULT_STATUS', 
        'fault_record', 
        NEW.fault_id,
        '127.0.0.1',
        JSON_OBJECT('old_status', OLD.status, 'new_status', NEW.status)
    );
END //

DELIMITER ;

-- =====================================================
-- 脚本执行完成
-- =====================================================

SELECT 'Database schema created successfully!' as message;