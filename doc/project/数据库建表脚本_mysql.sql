-- =====================================================
-- 故障检测系统数据库建表脚本 (MySQL 优化版)
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4
-- 创建时间: 2025年
-- 说明: 参照原始脚本的分段与注释风格进行重构
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS hadoop_fault_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hadoop_fault_db;

-- =====================================================
-- 1. 核心业务表
-- =====================================================

-- 1.1 故障记录表
DROP TABLE IF EXISTS fault_records;
CREATE TABLE fault_records (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    fault_id VARCHAR(32) NOT NULL COMMENT '故障唯一标识',
    cluster_id BIGINT COMMENT '关联集群ID',
    fault_type VARCHAR(50) NOT NULL COMMENT '故障类型',
    fault_level ENUM('low','medium','high','critical') NOT NULL DEFAULT 'medium' COMMENT '故障级别',
    title VARCHAR(200) NOT NULL COMMENT '故障标题',
    description TEXT COMMENT '故障详细描述',
    affected_nodes JSON COMMENT '受影响的节点列表',
    affected_clusters JSON COMMENT '受影响的集群列表',
    root_cause TEXT COMMENT '根本原因分析',
    repair_suggestion TEXT COMMENT '修复建议',
    status ENUM('detected','analyzing','repairing','resolved','failed') NOT NULL DEFAULT 'detected' COMMENT '状态',
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
    risk_level ENUM('low','medium','high') NOT NULL DEFAULT 'medium' COMMENT '风险级别',
    execution_status ENUM('pending','running','success','failed','timeout') NOT NULL DEFAULT 'pending' COMMENT '执行状态',
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
    KEY idx_end_time (end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行日志表';

-- 1.3 节点信息表
DROP TABLE IF EXISTS nodes;
CREATE TABLE nodes (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    uuid VARCHAR(36) NOT NULL COMMENT '节点唯一标识UUID',
    cluster_id BIGINT NOT NULL COMMENT '所属集群ID',
    hostname VARCHAR(100) NOT NULL COMMENT '节点主机名',
    ip_address VARCHAR(45) NOT NULL COMMENT '节点IP地址',
    status ENUM('healthy','unhealthy','warning','unknown') NOT NULL DEFAULT 'unknown' COMMENT '节点健康状态',
    cpu_usage DECIMAL(5,2) COMMENT 'CPU使用率 (%)',
    memory_usage DECIMAL(5,2) COMMENT '内存使用率 (%)',
    disk_usage DECIMAL(5,2) COMMENT '磁盘使用率 (%)',
    last_heartbeat TIMESTAMP COMMENT '最后心跳时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_uuid (uuid),
    KEY idx_cluster_id (cluster_id),
    UNIQUE KEY uk_cluster_hostname (cluster_id, hostname),
    KEY idx_status (status),
    KEY idx_last_heartbeat (last_heartbeat),
    KEY idx_ip_address (ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='节点信息表';

-- 1.4 集群-节点关系表
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
    KEY idx_cluster_id (cluster_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='集群-节点关系表：节点唯一绑定至一个集群';

-- 1.5 系统日志表
DROP TABLE IF EXISTS system_logs;
CREATE TABLE system_logs (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    log_id VARCHAR(32) NOT NULL COMMENT '日志唯一标识',
    fault_id VARCHAR(32) COMMENT '关联故障ID',
    cluster_id BIGINT COMMENT '关联集群ID',
    timestamp TIMESTAMP NOT NULL COMMENT '日志时间戳',
    host VARCHAR(100) NOT NULL COMMENT '主机名',
    service VARCHAR(50) NOT NULL COMMENT '服务名',
    log_level ENUM('DEBUG','INFO','WARN','ERROR','FATAL') NOT NULL COMMENT '日志级别',
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
    KEY idx_log_level (log_level),
    KEY idx_processed (processed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志表';

-- =====================================================
-- 2. 配置管理与用户表
-- =====================================================

-- 2.1 集群信息表
DROP TABLE IF EXISTS clusters;
CREATE TABLE clusters (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    uuid VARCHAR(36) NOT NULL COMMENT '集群唯一标识UUID',
    name VARCHAR(100) NOT NULL COMMENT '集群名称',
    type VARCHAR(50) NOT NULL COMMENT '集群类型',
    node_count INT DEFAULT 0 COMMENT '集群节点数量',
    health_status ENUM('healthy','warning','error','unknown') NOT NULL DEFAULT 'unknown' COMMENT '集群健康状态',
    description TEXT COMMENT '集群描述',
    config_info JSON COMMENT '集群配置信息',
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
    role_id BIGINT NOT NULL COMMENT '角色ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_cluster (user_id, cluster_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户与集群映射表';

-- 2.7 应用统一配置表
DROP TABLE IF EXISTS app_configurations;
CREATE TABLE app_configurations (
    id BIGINT AUTO_INCREMENT COMMENT '主键ID',
    config_type ENUM('system','alert_rule','notification','llm') NOT NULL COMMENT '配置类型',
    config_key VARCHAR(100) NOT NULL COMMENT '配置键',
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
    ip_address VARCHAR(45) NOT NULL COMMENT 'IP地址',
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
    risk_level ENUM('low','medium','high') NOT NULL DEFAULT 'medium' COMMENT '风险级别',
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

ALTER TABLE fault_records ADD CONSTRAINT fk_fault_records_cluster_id FOREIGN KEY (cluster_id) REFERENCES clusters(id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE exec_logs ADD CONSTRAINT fk_exec_logs_fault_id FOREIGN KEY (fault_id) REFERENCES fault_records(fault_id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE system_logs ADD CONSTRAINT fk_system_logs_fault_id FOREIGN KEY (fault_id) REFERENCES fault_records(fault_id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE nodes ADD CONSTRAINT fk_nodes_cluster FOREIGN KEY (cluster_id) REFERENCES clusters(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE cluster_node_mapping ADD CONSTRAINT fk_cnm_cluster FOREIGN KEY (cluster_id) REFERENCES clusters(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE cluster_node_mapping ADD CONSTRAINT fk_cnm_node FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE system_logs ADD CONSTRAINT fk_system_logs_cluster_id FOREIGN KEY (cluster_id) REFERENCES clusters(id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE role_permission_mapping ADD CONSTRAINT fk_rp_mapping_role_id FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE role_permission_mapping ADD CONSTRAINT fk_rp_mapping_permission_id FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE user_role_mapping ADD CONSTRAINT fk_ur_mapping_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE user_role_mapping ADD CONSTRAINT fk_ur_mapping_role_id FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE user_cluster_mapping ADD CONSTRAINT fk_mapping_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE user_cluster_mapping ADD CONSTRAINT fk_mapping_cluster_id FOREIGN KEY (cluster_id) REFERENCES clusters(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE user_cluster_mapping ADD CONSTRAINT fk_mapping_role_id FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE audit_logs ADD CONSTRAINT fk_audit_logs_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE audit_logs ADD CONSTRAINT fk_audit_logs_cluster_id FOREIGN KEY (cluster_id) REFERENCES clusters(id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE audit_logs ADD CONSTRAINT fk_audit_logs_role_id FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL ON UPDATE CASCADE;

-- =====================================================
-- 5. 初始化数据
-- =====================================================

INSERT INTO clusters (uuid, name, type, description, config_info) VALUES
('a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Hadoop主集群', 'Hadoop', '生产环境主Hadoop集群', '{"namenode_uri": "hdfs://nn1.hadoop.prod:8020"}'),
('b2c3d4e5-f6a7-8901-2345-67890abcdef1', 'Hadoop测试集群', 'Hadoop', '用于测试的Hadoop集群', '{"namenode_uri": "hdfs://nn.hadoop.test:8020"}');

INSERT INTO roles (role_name, role_key, description, is_system_role) VALUES
('超级管理员', 'super_admin', '拥有系统所有权限', TRUE),
('集群管理员', 'cluster_admin', '管理指定集群的所有功能', TRUE),
('普通操作员', 'operator', '执行常规操作，如查看和执行修复任务', TRUE),
('只读观察员', 'viewer', '只能查看数据，不能进行任何修改操作', TRUE);

INSERT INTO permissions (permission_name, permission_key, description) VALUES
('查看用户', 'user:read', '查看用户列表和详情'),
('创建用户', 'user:create', '创建新用户'),
('编辑用户', 'user:update', '修改用户信息'),
('删除用户', 'user:delete', '删除用户'),
('查看角色', 'role:read', '查看角色列表和详情'),
('创建角色', 'role:create', '创建自定义角色'),
('编辑角色', 'role:update', '修改角色信息'),
('删除角色', 'role:delete', '删除自定义角色'),
('分配权限', 'role:assign_permissions', '为角色分配权限'),
('查看集群', 'cluster:read', '查看集群列表和状态'),
('添加集群', 'cluster:create', '添加新集群'),
('编辑集群', 'cluster:update', '修改集群配置'),
('删除集群', 'cluster:delete', '删除集群'),
('查看故障', 'fault:read', '查看故障记录'),
('分析故障', 'fault:analyze', '执行故障分析'),
('修复故障', 'fault:repair', '执行修复操作'),
('查看系统日志', 'log:read', '查看系统运行日志'),
('查看审计日志', 'audit:read', '查看用户操作审计');

-- 超级管理员拥有所有权限
INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.role_key = 'super_admin';

-- 集群管理员权限
INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.role_key = 'cluster_admin' AND p.permission_key IN (
    'cluster:read', 'cluster:update',
    'fault:read', 'fault:analyze', 'fault:repair',
    'log:read'
);

-- 普通操作员权限
INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.role_key = 'operator' AND p.permission_key IN (
    'fault:read', 'fault:repair', 'log:read'
);

-- 只读观察员权限
INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.role_key = 'viewer' AND p.permission_key IN (
    'user:read', 'role:read', 'cluster:read', 'fault:read', 'log:read', 'audit:read'
);

INSERT INTO app_configurations (config_type, config_key, config_value, description, is_enabled) VALUES
('system', 'system.name', '{"value": "故障检测系统"}', '系统名称', TRUE),
('system', 'log.retention.days', '{"value": 90}', '日志保留天数', TRUE),
('system', 'repair.auto.enabled', '{"value": false}', '是否启用自动修复', TRUE),
('llm', 'api.timeout', '{"value": 30}', 'LLM API超时时间(秒)', TRUE);

INSERT INTO app_configurations (config_type, config_key, config_value, description, is_enabled) VALUES
('alert_rule', 'CPU使用率过高', '{"metric": "cpu_usage", "condition": ">", "threshold": 85, "severity": "high"}', 'CPU使用率超过85%时触发告警', TRUE),
('alert_rule', '内存使用率过高', '{"metric": "memory_usage", "condition": ">", "threshold": 90, "severity": "high"}', '内存使用率超过90%时触发告警', TRUE),
('alert_rule', '节点离线', '{"metric": "node_status", "condition": "=", "value": "offline", "severity": "critical"}', '节点离线时触发告警', TRUE);

INSERT INTO app_configurations (config_type, config_key, config_value, description, is_enabled) VALUES
('notification', '默认邮件通知', '{"type": "email", "triggers": ["high", "critical"], "recipients": ["admin@example.com"]}', '向管理员发送高危和严重故障的邮件通知', TRUE);

INSERT INTO users (username, email, password_hash, full_name, is_active) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', '系统管理员', TRUE);

INSERT INTO user_role_mapping (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r WHERE u.username = 'admin' AND r.role_key = 'super_admin';

INSERT INTO user_cluster_mapping (user_id, cluster_id, role_id)
SELECT u.id, c.id, r.id FROM users u, clusters c, roles r WHERE u.username = 'admin' AND c.name = 'Hadoop主集群' AND r.role_key = 'cluster_admin';
INSERT INTO user_cluster_mapping (user_id, cluster_id, role_id)
SELECT u.id, c.id, r.id FROM users u, clusters c, roles r WHERE u.username = 'admin' AND c.name = 'Hadoop测试集群' AND r.role_key = 'cluster_admin';

-- =====================================================
-- 脚本执行完成
-- =====================================================
SELECT 'MySQL schema created successfully!' AS message;
