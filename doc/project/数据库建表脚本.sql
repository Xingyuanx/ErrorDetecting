-- =====================================================
-- 故障检测系统数据库建表脚本 (简化版)
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4
-- 创建时间: 2025年
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
    KEY idx_status (status),
    KEY idx_created_at (created_at)
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
    KEY idx_execution_status (execution_status)
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
    health_score INT DEFAULT 100 COMMENT '健康评分(0-100)',
    last_heartbeat TIMESTAMP COMMENT '最后心跳时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_node_id (node_id),
    KEY idx_node_status (node_status),
    KEY idx_last_heartbeat (last_heartbeat)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='集群状态表';

-- 1.4 系统日志表
DROP TABLE IF EXISTS system_logs;
CREATE TABLE system_logs (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    log_id VARCHAR(32) NOT NULL COMMENT '日志唯一标识',
    fault_id VARCHAR(32) COMMENT '关联故障ID',
    timestamp TIMESTAMP NOT NULL COMMENT '日志时间戳',
    host VARCHAR(100) NOT NULL COMMENT '主机名',
    service VARCHAR(50) NOT NULL COMMENT '服务名',
    log_level ENUM('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL') NOT NULL COMMENT '日志级别',
    message LONGTEXT NOT NULL COMMENT '日志消息',
    exception LONGTEXT COMMENT '异常堆栈',
    raw_log LONGTEXT COMMENT '原始日志内容',
    processed BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已处理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_log_id (log_id),
    KEY idx_fault_id (fault_id),
    KEY idx_timestamp (timestamp),
    KEY idx_log_level (log_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志表';

-- =====================================================
-- 2. 配置管理与用户表
-- =====================================================

-- 2.1 应用统一配置表
DROP TABLE IF EXISTS app_configurations;
CREATE TABLE app_configurations (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    config_type ENUM('system', 'alert_rule', 'notification', 'llm') NOT NULL COMMENT '配置类型',
    config_key VARCHAR(100) NOT NULL COMMENT '配置键, 如规则名、系统参数名',
    config_value JSON NOT NULL COMMENT '配置值 (JSON格式)',
    description VARCHAR(500) COMMENT '配置描述',
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_config_type_key (config_type, config_key),
    KEY idx_is_enabled (is_enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='应用统一配置表';

-- 2.2 用户表
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    full_name VARCHAR(100) NOT NULL COMMENT '姓名',
    role ENUM('admin', 'operator', 'viewer') NOT NULL DEFAULT 'operator' COMMENT '角色',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 2.3 操作审计表
DROP TABLE IF EXISTS audit_logs;
CREATE TABLE audit_logs (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    action VARCHAR(100) NOT NULL COMMENT '操作动作',
    resource_type VARCHAR(50) NOT NULL COMMENT '资源类型',
    resource_id VARCHAR(100) COMMENT '资源ID',
    ip_address VARCHAR(15) NOT NULL COMMENT 'IP地址',
    request_data JSON COMMENT '请求数据',
    response_status INT COMMENT '响应状态码',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    PRIMARY KEY (id),
    KEY idx_user_id (user_id),
    KEY idx_action (action),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作审计表';

-- =====================================================
-- 3. 扩展表
-- =====================================================

-- 3.1 修复脚本模板表
DROP TABLE IF EXISTS repair_templates;
CREATE TABLE repair_templates (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    template_name VARCHAR(100) NOT NULL COMMENT '模板名称',
    fault_type VARCHAR(50) NOT NULL COMMENT '适用故障类型',
    script_content TEXT NOT NULL COMMENT '脚本内容',
    risk_level ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium' COMMENT '风险级别',
    description TEXT COMMENT '模板描述',
    parameters JSON COMMENT '参数定义',
    created_by VARCHAR(50) COMMENT '创建人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_template_name (template_name),
    KEY idx_fault_type (fault_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='修复脚本模板表';

-- =====================================================
-- 4. 外键约束
-- =====================================================

-- 执行日志表关联故障记录表
ALTER TABLE exec_logs 
ADD CONSTRAINT fk_exec_logs_fault_id 
FOREIGN KEY (fault_id) REFERENCES fault_records(fault_id) 
ON DELETE CASCADE ON UPDATE CASCADE;

-- 系统日志表关联故障记录表
ALTER TABLE system_logs
ADD CONSTRAINT fk_system_logs_fault_id
FOREIGN KEY (fault_id) REFERENCES fault_records(fault_id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- 审计日志表关联用户表
ALTER TABLE audit_logs 
ADD CONSTRAINT fk_audit_logs_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) 
ON DELETE SET NULL ON UPDATE CASCADE;

-- =====================================================
-- 5. 初始化数据
-- =====================================================

-- 插入默认系统配置
INSERT INTO app_configurations (config_type, config_key, config_value, description, is_enabled) VALUES
('system', 'system.name', '{"value": "故障检测系统"}', '系统名称', TRUE),
('system', 'log.retention.days', '{"value": 90}', '日志保留天数', TRUE),
('system', 'repair.auto.enabled', '{"value": false}', '是否启用自动修复', TRUE),
('llm', 'api.timeout', '{"value": 30}', 'LLM API超时时间(秒)', TRUE);

-- 插入默认告警规则
INSERT INTO app_configurations (config_type, config_key, config_value, description, is_enabled) VALUES
('alert_rule', 'CPU使用率过高', '{"metric": "cpu_usage", "condition": ">", "threshold": 85, "severity": "high"}', 'CPU使用率超过85%时触发告警', TRUE),
('alert_rule', '内存使用率过高', '{"metric": "memory_usage", "condition": ">", "threshold": 90, "severity": "high"}', '内存使用率超过90%时触发告警', TRUE),
('alert_rule', '节点离线', '{"metric": "node_status", "condition": "=", "value": "offline", "severity": "critical"}', '节点离线时触发告警', TRUE);

-- 插入默认通知配置
INSERT INTO app_configurations (config_type, config_key, config_value, description, is_enabled) VALUES
('notification', '默认邮件通知', '{"type": "email", "triggers": ["high", "critical"], "recipients": ["admin@example.com"]}', '向管理员发送高危和严重故障的邮件通知', TRUE);

-- 插入默认管理员用户 (密码: admin123)
INSERT INTO users (username, email, password_hash, full_name, role, is_active) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', '系统管理员', 'admin', TRUE);

-- 插入修复脚本模板
INSERT INTO repair_templates (template_name, fault_type, script_content, risk_level, description, parameters) VALUES
('重启DataNode服务', 'DataNode离线', 'sudo systemctl restart hadoop-hdfs-datanode', 'medium', '重启DataNode服务以恢复连接', '{"node_id": "string"}'),
('清理临时文件', '磁盘空间不足', 'sudo rm -rf /tmp/hadoop-*', 'low', '清理Hadoop临时文件', '{"node_id": "string", "path": "string"}');

-- =====================================================
-- 脚本执行完成
-- =====================================================

SELECT 'Database schema simplified and created successfully!' as message;