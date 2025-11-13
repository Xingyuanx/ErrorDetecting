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
    affected_clusters JSON COMMENT '受影响的集群列表',
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

-- 1.3 节点信息表 (原 cluster_status 表，优化后)
DROP TABLE IF EXISTS nodes;
CREATE TABLE nodes (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    uuid VARCHAR(36) NOT NULL COMMENT '节点唯一标识UUID',
    cluster_id BIGINT NOT NULL COMMENT '所属集群ID',
    hostname VARCHAR(100) NOT NULL COMMENT '节点主机名',
    ip_address VARCHAR(45) NOT NULL COMMENT '节点IP地址',
    status ENUM('healthy', 'unhealthy', 'warning', 'unknown') NOT NULL DEFAULT 'unknown' COMMENT '节点健康状态',
    cpu_usage DECIMAL(5, 2) COMMENT 'CPU使用率 (%)',
    memory_usage DECIMAL(5, 2) COMMENT '内存使用率 (%)',
    disk_usage DECIMAL(5, 2) COMMENT '磁盘使用率 (%)',
    last_heartbeat TIMESTAMP COMMENT '最后心跳时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (id),
    UNIQUE KEY uk_uuid (uuid),
    KEY idx_cluster_id (cluster_id),
    UNIQUE KEY uk_cluster_hostname (cluster_id, hostname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='节点信息表';

-- 1.4 集群-节点关系表（一对多：一个节点只属于一个集群）
DROP TABLE IF EXISTS cluster_node_mapping;
CREATE TABLE cluster_node_mapping (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    cluster_id BIGINT NOT NULL COMMENT '集群ID',
    node_id BIGINT NOT NULL COMMENT '节点ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (id),
    UNIQUE KEY uk_node_id (node_id),
    UNIQUE KEY uk_cluster_node (cluster_id, node_id),
    KEY idx_cluster_id (cluster_id),
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='集群-节点关系表：节点唯一绑定至一个集群';

-- 1.4 系统日志表
DROP TABLE IF EXISTS system_logs;
CREATE TABLE system_logs (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    log_id VARCHAR(32) NOT NULL COMMENT '日志唯一标识',
    fault_id VARCHAR(32) COMMENT '关联故障ID',
    cluster_id BIGINT COMMENT '关联集群ID',
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
    KEY idx_cluster_id (cluster_id),
    KEY idx_timestamp (timestamp),
    KEY idx_log_level (log_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志表';

-- =====================================================
-- 2. 配置管理与用户表
-- =====================================================

-- 2.1 集群信息表 (优化后)
DROP TABLE IF EXISTS clusters;
CREATE TABLE clusters (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    uuid VARCHAR(36) NOT NULL COMMENT '集群唯一标识UUID',
    name VARCHAR(100) NOT NULL COMMENT '集群名称',
    type VARCHAR(50) NOT NULL COMMENT '集群类型 (e.g., Hadoop, Kubernetes)',
    node_count INT DEFAULT 0 COMMENT '集群节点数量',
    health_status ENUM('healthy', 'warning', 'error', 'unknown') NOT NULL DEFAULT 'unknown' COMMENT '集群健康状态',
    description TEXT COMMENT '集群描述',
    config_info JSON COMMENT '集群配置信息 (e.g., NameNode地址)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_uuid (uuid),
    UNIQUE KEY uk_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='集群信息表';

-- 2.2 角色表
DROP TABLE IF EXISTS roles;
CREATE TABLE roles (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    role_name VARCHAR(50) NOT NULL COMMENT '角色名称',
    role_key VARCHAR(50) NOT NULL COMMENT '角色唯一标识',
    description VARCHAR(255) COMMENT '角色描述',
    is_system_role BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否为系统内置角色',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_role_key (role_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 2.3 权限表
DROP TABLE IF EXISTS permissions;
CREATE TABLE permissions (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    permission_name VARCHAR(100) NOT NULL COMMENT '权限名称',
    permission_key VARCHAR(100) NOT NULL COMMENT '权限唯一标识',
    description VARCHAR(255) COMMENT '权限描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_permission_key (permission_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';

-- 2.4 角色-权限映射表
DROP TABLE IF EXISTS role_permission_mapping;
CREATE TABLE role_permission_mapping (
    role_id BIGINT NOT NULL COMMENT '角色ID',
    permission_id BIGINT NOT NULL COMMENT '权限ID',
    
    PRIMARY KEY (role_id, permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色-权限映射表';

-- 2.5 用户-角色映射表
DROP TABLE IF EXISTS user_role_mapping;
CREATE TABLE user_role_mapping (
    user_id BIGINT NOT NULL COMMENT '用户ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    
    PRIMARY KEY (user_id, role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户-角色映射表';

-- 2.6 用户与集群映射表
DROP TABLE IF EXISTS user_cluster_mapping;
CREATE TABLE user_cluster_mapping (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    cluster_id BIGINT NOT NULL COMMENT '集群ID',
    role_id BIGINT NOT NULL COMMENT '用户在该集群的角色ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_cluster (user_id, cluster_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户与集群映射表';

-- 2.7 应用统一配置表
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

-- 2.8 用户表
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    full_name VARCHAR(100) NOT NULL COMMENT '姓名',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 2.9 操作审计表
DROP TABLE IF EXISTS audit_logs;
CREATE TABLE audit_logs (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT COMMENT '用户ID',
    cluster_id BIGINT COMMENT '集群ID',
    role_id BIGINT COMMENT '角色ID',
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
    KEY idx_cluster_id (cluster_id),
    KEY idx_role_id (role_id),
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

-- 故障记录表关联集群
ALTER TABLE fault_records
ADD COLUMN cluster_id BIGINT COMMENT '关联集群ID' AFTER fault_id; 
-- 外键约束将在所有表创建后统一添加
-- ADD CONSTRAINT fk_fault_records_cluster_id
-- FOREIGN KEY (cluster_id) REFERENCES clusters(id)
-- ON DELETE SET NULL ON UPDATE CASCADE;

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

-- 节点与集群外键约束（在所有表创建后统一添加）
ALTER TABLE nodes
ADD CONSTRAINT fk_nodes_cluster
FOREIGN KEY (cluster_id) REFERENCES clusters(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- 集群-节点关系表外键约束
ALTER TABLE cluster_node_mapping
ADD CONSTRAINT fk_cnm_cluster
FOREIGN KEY (cluster_id) REFERENCES clusters(id)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE cluster_node_mapping
ADD CONSTRAINT fk_cnm_node
FOREIGN KEY (node_id) REFERENCES nodes(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- 系统日志表关联集群
ALTER TABLE system_logs
ADD CONSTRAINT fk_system_logs_cluster_id
FOREIGN KEY (cluster_id) REFERENCES clusters(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- 节点信息表关联集群 (外键已在CREATE TABLE中定义)
-- ALTER TABLE nodes ADD CONSTRAINT fk_nodes_cluster FOREIGN KEY (cluster_id) REFERENCES clusters(id) ON DELETE CASCADE ON UPDATE CASCADE;

-- 角色-权限映射表关联
ALTER TABLE role_permission_mapping
ADD CONSTRAINT fk_rp_mapping_role_id
FOREIGN KEY (role_id) REFERENCES roles(id)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE role_permission_mapping
ADD CONSTRAINT fk_rp_mapping_permission_id
FOREIGN KEY (permission_id) REFERENCES permissions(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- 用户-角色映射表关联
ALTER TABLE user_role_mapping
ADD CONSTRAINT fk_ur_mapping_user_id
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE user_role_mapping
ADD CONSTRAINT fk_ur_mapping_role_id
FOREIGN KEY (role_id) REFERENCES roles(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- 用户与集群映射表关联
ALTER TABLE user_cluster_mapping
ADD CONSTRAINT fk_mapping_user_id
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE user_cluster_mapping
ADD CONSTRAINT fk_mapping_cluster_id
FOREIGN KEY (cluster_id) REFERENCES clusters(id)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE user_cluster_mapping
ADD CONSTRAINT fk_mapping_role_id
FOREIGN KEY (role_id) REFERENCES roles(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- 审计日志表关联用户表
ALTER TABLE audit_logs 
ADD CONSTRAINT fk_audit_logs_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) 
ON DELETE SET NULL ON UPDATE CASCADE;

-- 审计日志表关联集群
ALTER TABLE audit_logs
ADD CONSTRAINT fk_audit_logs_cluster_id
FOREIGN KEY (cluster_id) REFERENCES clusters(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- 审计日志表关联角色
ALTER TABLE audit_logs
ADD CONSTRAINT fk_audit_logs_role_id
FOREIGN KEY (role_id) REFERENCES roles(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- =====================================================
-- 5. 初始化数据
-- =====================================================

-- 插入默认集群
INSERT INTO clusters (uuid, name, type, description, config_info) VALUES
('a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Hadoop主集群', 'Hadoop', '生产环境主Hadoop集群', '{"namenode_uri": "hdfs://nn1.hadoop.prod:8020"}'),
('b2c3d4e5-f6a7-8901-2345-67890abcdef1', 'Hadoop测试集群', 'Hadoop', '用于测试的Hadoop集群', '{"namenode_uri": "hdfs://nn.hadoop.test:8020"}');

-- 插入默认系统角色
INSERT INTO roles (role_name, role_key, description, is_system_role) VALUES
('超级管理员', 'super_admin', '拥有系统所有权限', TRUE),
('集群管理员', 'cluster_admin', '管理指定集群的所有功能', TRUE),
('普通操作员', 'operator', '执行常规操作，如查看和执行修复任务', TRUE),
('只读观察员', 'viewer', '只能查看数据，不能进行任何修改操作', TRUE);

-- 插入默认权限
INSERT INTO permissions (permission_name, permission_key, description) VALUES
-- 用户管理
('查看用户', 'user:read', '查看用户列表和详情'),
('创建用户', 'user:create', '创建新用户'),
('编辑用户', 'user:update', '修改用户信息'),
('删除用户', 'user:delete', '删除用户'),
-- 角色管理
('查看角色', 'role:read', '查看角色列表和详情'),
('创建角色', 'role:create', '创建自定义角色'),
('编辑角色', 'role:update', '修改角色信息'),
('删除角色', 'role:delete', '删除自定义角色'),
('分配权限', 'role:assign_permissions', '为角色分配权限'),
-- 集群管理
('查看集群', 'cluster:read', '查看集群列表和状态'),
('添加集群', 'cluster:create', '添加新集群'),
('编辑集群', 'cluster:update', '修改集群配置'),
('删除集群', 'cluster:delete', '删除集群'),
-- 故障管理
('查看故障', 'fault:read', '查看故障记录'),
('分析故障', 'fault:analyze', '执行故障分析'),
('修复故障', 'fault:repair', '执行修复操作'),
-- 日志审计
('查看系统日志', 'log:read', '查看系统运行日志'),
('查看审计日志', 'audit:read', '查看用户操作审计');

-- 为系统角色分配权限
-- 超级管理员拥有所有权限
INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.role_key = 'super_admin';

-- 集群管理员权限
INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.role_key = 'cluster_admin' AND p.permission_key IN (
    'cluster:read', 'cluster:update',
    'fault:read', 'fault:analyze', 'fault:repair',
    'log:read'
);

-- 普通操作员权限
INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.role_key = 'operator' AND p.permission_key IN (
    'fault:read', 'fault:repair', 'log:read'
);

-- 只读观察员权限
INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.role_key = 'viewer' AND p.permission_key IN (
    'user:read', 'role:read', 'cluster:read', 'fault:read', 'log:read', 'audit:read'
);

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
INSERT INTO users (username, email, password_hash, full_name, is_active) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', '系统管理员', TRUE);

-- 为管理员分配全局角色
INSERT INTO user_role_mapping (user_id, role_id)
SELECT u.id, r.id
FROM users u, roles r
WHERE u.username = 'admin' AND r.role_key = 'super_admin';

-- 插入用户与集群的映射关系
INSERT INTO user_cluster_mapping (user_id, cluster_id, role_id)
SELECT u.id, c.id, r.id
FROM users u, clusters c, roles r
WHERE u.username = 'admin' AND c.name = 'Hadoop主集群' AND r.role_key = 'cluster_admin';

INSERT INTO user_cluster_mapping (user_id, cluster_id, role_id)
SELECT u.id, c.id, r.id
FROM users u, clusters c, roles r
WHERE u.username = 'admin' AND c.name = 'Hadoop测试集群' AND r.role_key = 'cluster_admin';

-- =====================================================
-- 触发器：数据一致性校验、关联同步、操作日志记录
-- 覆盖表：nodes、cluster_node_mapping、fault_records（并对clusters做节点计数聚合）
-- 设计原则：
-- 1) BEFORE 阶段进行有效性校验与变更合法性检查；
-- 2) AFTER 阶段进行关联数据同步与操作日志记录；
-- 3) DELETE 阶段维护一致性与日志记录；
-- 4) 使用最小化逻辑，依赖唯一与外键约束，避免全表扫描；
-- 5) 所有触发器均带有详细注释，便于维护与排障。
-- =====================================================

DELIMITER $$

-- -------------------------------
-- nodes 表触发器
-- -------------------------------

-- BEFORE INSERT：基本有效性校验
DROP TRIGGER IF EXISTS tr_nodes_bi;
CREATE TRIGGER tr_nodes_bi BEFORE INSERT ON nodes
FOR EACH ROW
BEGIN
  -- 数据有效性验证
  IF NEW.hostname IS NULL OR NEW.hostname = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'nodes.hostname 不能为空';
  END IF;
  IF NEW.ip_address IS NULL OR NEW.ip_address = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'nodes.ip_address 不能为空';
  END IF;
END$$

-- BEFORE UPDATE：变更合法性校验
DROP TRIGGER IF EXISTS tr_nodes_bu;
CREATE TRIGGER tr_nodes_bu BEFORE UPDATE ON nodes
FOR EACH ROW
BEGIN
  -- 数据有效性验证
  IF NEW.hostname IS NULL OR NEW.hostname = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'nodes.hostname 不能为空';
  END IF;
  IF NEW.ip_address IS NULL OR NEW.ip_address = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'nodes.ip_address 不能为空';
  END IF;
END$$

-- AFTER INSERT：同步映射 + 更新集群计数 + 操作日志
DROP TRIGGER IF EXISTS tr_nodes_ai;
CREATE TRIGGER tr_nodes_ai AFTER INSERT ON nodes
FOR EACH ROW
BEGIN
  -- 关联数据同步
  IF NEW.cluster_id IS NOT NULL THEN
    INSERT INTO cluster_node_mapping (cluster_id, node_id)
    VALUES (NEW.cluster_id, NEW.id)
    ON DUPLICATE KEY UPDATE cluster_id = VALUES(cluster_id), updated_at = CURRENT_TIMESTAMP;
    -- 更新集群节点计数（增）
    UPDATE clusters SET node_count = node_count + 1 WHERE id = NEW.cluster_id;
  END IF;

  -- 操作日志记录
  INSERT INTO system_logs (log_id, fault_id, cluster_id, timestamp, host, service, log_level, message)
  VALUES (REPLACE(UUID(), '-', ''), NULL, NEW.cluster_id, NOW(), NEW.hostname, 'db_trigger', 'INFO', CONCAT('Nodes INSERT: id=', NEW.id, ', cluster=', NEW.cluster_id));
END$$

-- AFTER UPDATE：若归属集群变化，同步映射与计数 + 操作日志
DROP TRIGGER IF EXISTS tr_nodes_au;
CREATE TRIGGER tr_nodes_au AFTER UPDATE ON nodes
FOR EACH ROW
BEGIN
  IF (NEW.cluster_id <> OLD.cluster_id) THEN
    INSERT INTO cluster_node_mapping (cluster_id, node_id)
    VALUES (NEW.cluster_id, NEW.id)
    ON DUPLICATE KEY UPDATE cluster_id = VALUES(cluster_id), updated_at = CURRENT_TIMESTAMP;
    -- 更新计数：旧集群减，新集群加
    IF OLD.cluster_id IS NOT NULL THEN
      UPDATE clusters SET node_count = GREATEST(node_count - 1, 0) WHERE id = OLD.cluster_id;
    END IF;
    IF NEW.cluster_id IS NOT NULL THEN
      UPDATE clusters SET node_count = node_count + 1 WHERE id = NEW.cluster_id;
    END IF;
  END IF;

  -- 操作日志记录
  INSERT INTO system_logs (log_id, fault_id, cluster_id, timestamp, host, service, log_level, message)
  VALUES (REPLACE(UUID(), '-', ''), NULL, NEW.cluster_id, NOW(), NEW.hostname, 'db_trigger', 'INFO', CONCAT('Nodes UPDATE: id=', NEW.id, ', cluster=', NEW.cluster_id));
END$$

-- AFTER DELETE：维护集群计数 + 操作日志
DROP TRIGGER IF EXISTS tr_nodes_ad;
CREATE TRIGGER tr_nodes_ad AFTER DELETE ON nodes
FOR EACH ROW
BEGIN
  IF OLD.cluster_id IS NOT NULL THEN
    UPDATE clusters SET node_count = GREATEST(node_count - 1, 0) WHERE id = OLD.cluster_id;
  END IF;

  INSERT INTO system_logs (log_id, fault_id, cluster_id, timestamp, host, service, log_level, message)
  VALUES (REPLACE(UUID(), '-', ''), NULL, OLD.cluster_id, NOW(), OLD.hostname, 'db_trigger', 'INFO', CONCAT('Nodes DELETE: id=', OLD.id, ', cluster=', OLD.cluster_id));
END$$

-- -------------------------------
-- cluster_node_mapping 表触发器
-- -------------------------------

-- BEFORE INSERT：有效性与唯一性提示（依赖唯一约束）
DROP TRIGGER IF EXISTS tr_cnm_bi;
CREATE TRIGGER tr_cnm_bi BEFORE INSERT ON cluster_node_mapping
FOR EACH ROW
BEGIN
  IF NEW.cluster_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'cluster_node_mapping.cluster_id 不能为空';
  END IF;
  IF NEW.node_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'cluster_node_mapping.node_id 不能为空';
  END IF;
  -- 若节点已绑定其它集群，阻止插入，提示使用 UPDATE 修改归属
  IF EXISTS (SELECT 1 FROM cluster_node_mapping WHERE node_id = NEW.node_id AND cluster_id <> NEW.cluster_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '节点已绑定其它集群，请使用UPDATE修改归属';
  END IF;
END$$

-- AFTER INSERT：同步 nodes.cluster_id + 日志
DROP TRIGGER IF EXISTS tr_cnm_ai;
CREATE TRIGGER tr_cnm_ai AFTER INSERT ON cluster_node_mapping
FOR EACH ROW
BEGIN
  UPDATE nodes n SET n.cluster_id = NEW.cluster_id WHERE n.id = NEW.node_id;
  INSERT INTO system_logs (log_id, fault_id, cluster_id, timestamp, host, service, log_level, message)
  VALUES (REPLACE(UUID(), '-', ''), NULL, NEW.cluster_id, NOW(), 'db', 'db_trigger', 'INFO', CONCAT('CNM INSERT: node_id=', NEW.node_id, ', cluster=', NEW.cluster_id));
END$$

-- BEFORE UPDATE：有效性校验
DROP TRIGGER IF EXISTS tr_cnm_bu;
CREATE TRIGGER tr_cnm_bu BEFORE UPDATE ON cluster_node_mapping
FOR EACH ROW
BEGIN
  IF NEW.cluster_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'cluster_node_mapping.cluster_id 不能为空';
  END IF;
END$$

-- AFTER UPDATE：同步 nodes.cluster_id + 日志
DROP TRIGGER IF EXISTS tr_cnm_au;
CREATE TRIGGER tr_cnm_au AFTER UPDATE ON cluster_node_mapping
FOR EACH ROW
BEGIN
  UPDATE nodes n SET n.cluster_id = NEW.cluster_id WHERE n.id = NEW.node_id;
  INSERT INTO system_logs (log_id, fault_id, cluster_id, timestamp, host, service, log_level, message)
  VALUES (REPLACE(UUID(), '-', ''), NULL, NEW.cluster_id, NOW(), 'db', 'db_trigger', 'INFO', CONCAT('CNM UPDATE: node_id=', NEW.node_id, ', cluster=', NEW.cluster_id));
END$$

-- AFTER DELETE：解除 nodes.cluster_id + 日志
DROP TRIGGER IF EXISTS tr_cnm_ad;
CREATE TRIGGER tr_cnm_ad AFTER DELETE ON cluster_node_mapping
FOR EACH ROW
BEGIN
  UPDATE nodes n SET n.cluster_id = NULL WHERE n.id = OLD.node_id AND n.cluster_id = OLD.cluster_id;
  INSERT INTO system_logs (log_id, fault_id, cluster_id, timestamp, host, service, log_level, message)
  VALUES (REPLACE(UUID(), '-', ''), NULL, OLD.cluster_id, NOW(), 'db', 'db_trigger', 'INFO', CONCAT('CNM DELETE: node_id=', OLD.node_id, ', cluster=', OLD.cluster_id));
END$$

-- -------------------------------
-- fault_records 表触发器
-- -------------------------------

-- BEFORE INSERT：JSON有效性验证
DROP TRIGGER IF EXISTS tr_fault_bi;
CREATE TRIGGER tr_fault_bi BEFORE INSERT ON fault_records
FOR EACH ROW
BEGIN
  IF NEW.affected_nodes IS NOT NULL AND JSON_VALID(NEW.affected_nodes) = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'fault_records.affected_nodes 必须为合法JSON';
  END IF;
  IF NEW.affected_clusters IS NOT NULL AND JSON_VALID(NEW.affected_clusters) = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'fault_records.affected_clusters 必须为合法JSON';
  END IF;
END$$

-- BEFORE UPDATE：JSON有效性校验
DROP TRIGGER IF EXISTS tr_fault_bu;
CREATE TRIGGER tr_fault_bu BEFORE UPDATE ON fault_records
FOR EACH ROW
BEGIN
  IF NEW.affected_nodes IS NOT NULL AND JSON_VALID(NEW.affected_nodes) = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'fault_records.affected_nodes 必须为合法JSON';
  END IF;
  IF NEW.affected_clusters IS NOT NULL AND JSON_VALID(NEW.affected_clusters) = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'fault_records.affected_clusters 必须为合法JSON';
  END IF;
END$$

-- AFTER INSERT：记录操作日志
DROP TRIGGER IF EXISTS tr_fault_ai;
CREATE TRIGGER tr_fault_ai AFTER INSERT ON fault_records
FOR EACH ROW
BEGIN
  INSERT INTO system_logs (log_id, fault_id, cluster_id, timestamp, host, service, log_level, message)
  VALUES (REPLACE(UUID(), '-', ''), NEW.fault_id, NULL, NOW(), 'db', 'db_trigger', 'INFO', CONCAT('Fault INSERT: fault_id=', NEW.fault_id, ', level=', NEW.fault_level));
END$$

-- AFTER UPDATE：记录操作日志
DROP TRIGGER IF EXISTS tr_fault_au;
CREATE TRIGGER tr_fault_au AFTER UPDATE ON fault_records
FOR EACH ROW
BEGIN
  INSERT INTO system_logs (log_id, fault_id, cluster_id, timestamp, host, service, log_level, message)
  VALUES (REPLACE(UUID(), '-', ''), NEW.fault_id, NULL, NOW(), 'db', 'db_trigger', 'INFO', CONCAT('Fault UPDATE: fault_id=', NEW.fault_id, ', status=', NEW.status));
END$$

-- AFTER DELETE：记录操作日志
DROP TRIGGER IF EXISTS tr_fault_ad;
CREATE TRIGGER tr_fault_ad AFTER DELETE ON fault_records
FOR EACH ROW
BEGIN
  INSERT INTO system_logs (log_id, fault_id, cluster_id, timestamp, host, service, log_level, message)
  VALUES (REPLACE(UUID(), '-', ''), OLD.fault_id, NULL, NOW(), 'db', 'db_trigger', 'INFO', CONCAT('Fault DELETE: fault_id=', OLD.fault_id));
END$$

DELIMITER ;

-- 插入修复脚本模板
INSERT INTO repair_templates (template_name, fault_type, script_content, risk_level, description, parameters) VALUES
('重启DataNode服务', 'DataNode离线', 'sudo systemctl restart hadoop-hdfs-datanode', 'medium', '重启DataNode服务以恢复连接', '{"node_id": "string"}'),
('清理临时文件', '磁盘空间不足', 'sudo rm -rf /tmp/hadoop-*', 'low', '清理Hadoop临时文件', '{"node_id": "string", "path": "string"}');

-- =====================================================
-- 脚本执行完成
-- =====================================================

SELECT 'Database schema simplified and created successfully!' as message;