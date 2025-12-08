\encoding UTF8
-- =====================================================
-- 故障检测系统数据库建表脚本 (PostgreSQL 优化版)
-- 数据库: PostgreSQL 14+
-- 字符集: UTF8
-- 创建时间: 2025年
-- 说明: 参照原始脚本的分段与注释风格进行重构
-- 注意: 请在目标数据库中执行本脚本（不包含 CREATE DATABASE）
-- =====================================================

-- =====================================================
-- 1. 核心业务表
-- =====================================================

-- 1.1 集群信息表
CREATE TABLE IF NOT EXISTS clusters (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,
    node_count INT NOT NULL DEFAULT 0,
    health_status VARCHAR(20) NOT NULL DEFAULT 'unknown',
    description TEXT,
    config_info JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT clusters_health_status_chk CHECK (health_status IN ('healthy','warning','error','unknown'))
);
-- 表与字段注释
COMMENT ON TABLE clusters IS '集群信息表';
COMMENT ON COLUMN clusters.id IS '主键ID';
COMMENT ON COLUMN clusters.uuid IS '集群唯一标识(UUID)';
COMMENT ON COLUMN clusters.name IS '集群名称';
COMMENT ON COLUMN clusters.type IS '集群类型';
COMMENT ON COLUMN clusters.node_count IS '集群节点数量';
COMMENT ON COLUMN clusters.config_info IS '集群配置信息(JSONB)';
COMMENT ON COLUMN clusters.health_status IS '集群健康状态(healthy/warning/error/unknown)';
COMMENT ON COLUMN clusters.description IS '集群描述';
COMMENT ON COLUMN clusters.created_at IS '创建时间';
COMMENT ON COLUMN clusters.updated_at IS '更新时间';

-- 1.2 节点信息表
CREATE TABLE IF NOT EXISTS nodes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE,
    cluster_id BIGINT NOT NULL REFERENCES clusters(id) ON DELETE CASCADE ON UPDATE CASCADE,
    hostname VARCHAR(100) NOT NULL,
    ip_address INET NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'unknown',
    cpu_usage NUMERIC(5,2),
    memory_usage NUMERIC(5,2),
    disk_usage NUMERIC(5,2),
    last_heartbeat TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT nodes_status_chk CHECK (status IN ('healthy','unhealthy','warning','unknown')),
    CONSTRAINT nodes_cpu_chk CHECK (cpu_usage IS NULL OR (cpu_usage >= 0 AND cpu_usage <= 100)),
    CONSTRAINT nodes_mem_chk CHECK (memory_usage IS NULL OR (memory_usage >= 0 AND memory_usage <= 100)),
    CONSTRAINT nodes_disk_chk CHECK (disk_usage IS NULL OR (disk_usage >= 0 AND disk_usage <= 100))
);
-- 表与字段注释
COMMENT ON TABLE nodes IS '节点信息表';
COMMENT ON COLUMN nodes.id IS '主键ID';
COMMENT ON COLUMN nodes.uuid IS '节点唯一标识(UUID)';
COMMENT ON COLUMN nodes.cluster_id IS '所属集群ID';
COMMENT ON COLUMN nodes.hostname IS '节点主机名';
COMMENT ON COLUMN nodes.ip_address IS '节点IP地址(INET, 兼容IPv4/IPv6)';
COMMENT ON COLUMN nodes.status IS '节点健康状态(healthy/unhealthy/warning/unknown)';
COMMENT ON COLUMN nodes.cpu_usage IS 'CPU使用率(%)';
COMMENT ON COLUMN nodes.memory_usage IS '内存使用率(%)';
COMMENT ON COLUMN nodes.disk_usage IS '磁盘使用率(%)';
COMMENT ON COLUMN nodes.last_heartbeat IS '最后心跳时间';
COMMENT ON COLUMN nodes.created_at IS '创建时间';
COMMENT ON COLUMN nodes.updated_at IS '更新时间';
-- 唯一索引：集群内主机名唯一（与 MySQL 的 uk_cluster_hostname 命名保持一致）
CREATE UNIQUE INDEX IF NOT EXISTS uk_cluster_hostname ON nodes(cluster_id, hostname);
CREATE INDEX IF NOT EXISTS idx_nodes_cluster_id ON nodes(cluster_id);
CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes(status);
CREATE INDEX IF NOT EXISTS idx_nodes_last_heartbeat ON nodes(last_heartbeat);
CREATE INDEX IF NOT EXISTS idx_nodes_ip_address ON nodes(ip_address);

-- 1.4 执行日志表
CREATE TABLE IF NOT EXISTS exec_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exec_id VARCHAR(32) NOT NULL UNIQUE,
    fault_id VARCHAR(32) NOT NULL,
    command_type VARCHAR(50) NOT NULL,
    script_path VARCHAR(255),
    command_content TEXT NOT NULL,
    target_nodes JSONB,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'medium',
    execution_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    duration INT,
    stdout_log TEXT,
    stderr_log TEXT,
    exit_code INT,
    operator VARCHAR(50) NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT exec_logs_risk_chk CHECK (risk_level IN ('low','medium','high')),
    CONSTRAINT exec_logs_status_chk CHECK (execution_status IN ('pending','running','success','failed','timeout')),
    CONSTRAINT exec_logs_duration_chk CHECK (duration IS NULL OR duration >= 0)
);
-- 表与字段注释
COMMENT ON TABLE exec_logs IS '执行日志表';
COMMENT ON COLUMN exec_logs.id IS '主键ID';
COMMENT ON COLUMN exec_logs.exec_id IS '执行唯一标识';
COMMENT ON COLUMN exec_logs.fault_id IS '关联故障标识(无外键)';
COMMENT ON COLUMN exec_logs.command_type IS '命令类型';
COMMENT ON COLUMN exec_logs.script_path IS '脚本路径';
COMMENT ON COLUMN exec_logs.command_content IS '执行的命令内容';
COMMENT ON COLUMN exec_logs.stdout_log IS '标准输出日志';
COMMENT ON COLUMN exec_logs.stderr_log IS '错误输出日志';
COMMENT ON COLUMN exec_logs.target_nodes IS '目标执行节点(JSONB)';
COMMENT ON COLUMN exec_logs.risk_level IS '风险级别(low/medium/high)';
COMMENT ON COLUMN exec_logs.execution_status IS '执行状态(pending/running/success/failed/timeout)';
COMMENT ON COLUMN exec_logs.start_time IS '开始执行时间';
COMMENT ON COLUMN exec_logs.end_time IS '结束执行时间';
COMMENT ON COLUMN exec_logs.duration IS '执行时长(秒)';
COMMENT ON COLUMN exec_logs.exit_code IS '退出码';
COMMENT ON COLUMN exec_logs.operator IS '操作人';
COMMENT ON COLUMN exec_logs.created_at IS '创建时间';
COMMENT ON COLUMN exec_logs.updated_at IS '更新时间';
CREATE INDEX IF NOT EXISTS idx_exec_logs_fault_id ON exec_logs(fault_id);
CREATE INDEX IF NOT EXISTS idx_exec_logs_status ON exec_logs(execution_status);
CREATE INDEX IF NOT EXISTS idx_exec_logs_start_time ON exec_logs(start_time);
CREATE INDEX IF NOT EXISTS idx_exec_logs_end_time ON exec_logs(end_time);

-- 1.5 系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    log_id VARCHAR(32) NOT NULL UNIQUE,
    fault_id VARCHAR(32),
    cluster_id BIGINT REFERENCES clusters(id) ON DELETE SET NULL ON UPDATE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    host VARCHAR(100) NOT NULL,
    service VARCHAR(50) NOT NULL,
    source VARCHAR(50),
    log_level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    exception TEXT,
    raw_log TEXT,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT system_logs_level_chk CHECK (log_level IN ('DEBUG','INFO','WARN','ERROR','FATAL'))
);
-- 表与字段注释
COMMENT ON TABLE system_logs IS '系统日志表';
COMMENT ON COLUMN system_logs.log_id IS '日志唯一标识';
COMMENT ON COLUMN system_logs.id IS '主键ID';
COMMENT ON COLUMN system_logs.fault_id IS '关联故障标识(无外键)';
COMMENT ON COLUMN system_logs.cluster_id IS '关联集群ID';
COMMENT ON COLUMN system_logs.timestamp IS '日志时间戳';
COMMENT ON COLUMN system_logs.host IS '主机名';
COMMENT ON COLUMN system_logs.service IS '服务名';
COMMENT ON COLUMN system_logs.source IS '来源';
COMMENT ON COLUMN system_logs.log_level IS '日志级别(DEBUG/INFO/WARN/ERROR/FATAL)';
COMMENT ON COLUMN system_logs.message IS '日志消息';
COMMENT ON COLUMN system_logs.raw_log IS '原始日志内容';
COMMENT ON COLUMN system_logs.processed IS '是否已处理';
COMMENT ON COLUMN system_logs.exception IS '异常堆栈';
COMMENT ON COLUMN system_logs.created_at IS '创建时间';
CREATE INDEX IF NOT EXISTS idx_system_logs_fault_id ON system_logs(fault_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_cluster_id ON system_logs(cluster_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_system_logs_processed ON system_logs(processed);

-- 2.1 角色表
CREATE TABLE IF NOT EXISTS roles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL,
    role_key VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    is_system_role BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- 表注释
COMMENT ON TABLE roles IS '角色表';
COMMENT ON COLUMN roles.id IS '主键ID';
COMMENT ON COLUMN roles.role_name IS '角色名称';
COMMENT ON COLUMN roles.role_key IS '角色唯一标识';
COMMENT ON COLUMN roles.description IS '角色描述';
COMMENT ON COLUMN roles.is_system_role IS '是否为系统内置角色';
COMMENT ON COLUMN roles.created_at IS '创建时间';
COMMENT ON COLUMN roles.updated_at IS '更新时间';

-- 2.2 权限表
CREATE TABLE IF NOT EXISTS permissions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    permission_name VARCHAR(100) NOT NULL,
    permission_key VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- 表注释
COMMENT ON TABLE permissions IS '权限表';
COMMENT ON COLUMN permissions.id IS '主键ID';
COMMENT ON COLUMN permissions.permission_name IS '权限名称';
COMMENT ON COLUMN permissions.permission_key IS '权限唯一标识';
COMMENT ON COLUMN permissions.description IS '权限描述';
COMMENT ON COLUMN permissions.created_at IS '创建时间';

-- 2.3 角色-权限映射表
CREATE TABLE IF NOT EXISTS role_permission_mapping (
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES permissions(id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);
-- 表注释
COMMENT ON TABLE role_permission_mapping IS '角色-权限映射表';
COMMENT ON COLUMN role_permission_mapping.role_id IS '角色ID';
COMMENT ON COLUMN role_permission_mapping.permission_id IS '权限ID';

-- 2.4 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- 表注释
COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.id IS '主键ID';
COMMENT ON COLUMN users.username IS '用户名';
COMMENT ON COLUMN users.email IS '邮箱';
COMMENT ON COLUMN users.password_hash IS '密码哈希';
COMMENT ON COLUMN users.full_name IS '姓名';
COMMENT ON COLUMN users.is_active IS '是否激活';
COMMENT ON COLUMN users.last_login IS '最后登录时间';
COMMENT ON COLUMN users.created_at IS '创建时间';
COMMENT ON COLUMN users.updated_at IS '更新时间';

-- 2.5 用户-角色映射表
CREATE TABLE IF NOT EXISTS user_role_mapping (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (user_id, role_id)
);
-- 表注释
COMMENT ON TABLE user_role_mapping IS '用户-角色映射表';
COMMENT ON COLUMN user_role_mapping.user_id IS '用户ID';
COMMENT ON COLUMN user_role_mapping.role_id IS '角色ID';

-- 2.6 用户与集群映射表
CREATE TABLE IF NOT EXISTS user_cluster_mapping (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    cluster_id BIGINT NOT NULL REFERENCES clusters(id) ON DELETE CASCADE ON UPDATE CASCADE,
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_user_cluster UNIQUE (user_id, cluster_id)
);
-- 表注释
COMMENT ON TABLE user_cluster_mapping IS '用户与集群映射表';
COMMENT ON COLUMN user_cluster_mapping.id IS '主键ID';
COMMENT ON COLUMN user_cluster_mapping.user_id IS '用户ID';
COMMENT ON COLUMN user_cluster_mapping.cluster_id IS '集群ID';
COMMENT ON COLUMN user_cluster_mapping.role_id IS '角色ID';
COMMENT ON COLUMN user_cluster_mapping.created_at IS '创建时间';

-- 2.7 应用统一配置表
CREATE TABLE IF NOT EXISTS app_configurations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    config_type VARCHAR(20) NOT NULL,
    config_key VARCHAR(100) NOT NULL,
    config_value JSONB NOT NULL,
    description VARCHAR(500),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_app_config UNIQUE (config_type, config_key),
    CONSTRAINT app_config_type_chk CHECK (config_type IN ('system','alert_rule','notification','llm'))
);
-- 表与字段注释
COMMENT ON TABLE app_configurations IS '应用统一配置表';
COMMENT ON COLUMN app_configurations.config_value IS '配置值(JSONB)';
COMMENT ON COLUMN app_configurations.id IS '主键ID';
COMMENT ON COLUMN app_configurations.config_type IS '配置类型(system/alert_rule/notification/llm)';
COMMENT ON COLUMN app_configurations.config_key IS '配置键';
COMMENT ON COLUMN app_configurations.description IS '配置描述';
COMMENT ON COLUMN app_configurations.is_enabled IS '是否启用';
COMMENT ON COLUMN app_configurations.created_at IS '创建时间';
COMMENT ON COLUMN app_configurations.updated_at IS '更新时间';
CREATE INDEX IF NOT EXISTS idx_app_config_enabled ON app_configurations(is_enabled);

-- 3.1 修复脚本模板表
CREATE TABLE IF NOT EXISTS repair_templates (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL UNIQUE,
    fault_type VARCHAR(50) NOT NULL,
    script_content TEXT NOT NULL,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'medium',
    description TEXT,
    parameters JSONB,
    created_by VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT repair_templates_risk_chk CHECK (risk_level IN ('low','medium','high'))
);
-- 表与字段注释
COMMENT ON TABLE repair_templates IS '修复脚本模板表';
COMMENT ON COLUMN repair_templates.parameters IS '模板参数定义(JSONB)';
COMMENT ON COLUMN repair_templates.id IS '主键ID';
COMMENT ON COLUMN repair_templates.template_name IS '模板名称';
COMMENT ON COLUMN repair_templates.fault_type IS '适用故障类型';
COMMENT ON COLUMN repair_templates.script_content IS '脚本内容';
COMMENT ON COLUMN repair_templates.risk_level IS '风险级别(low/medium/high)';
COMMENT ON COLUMN repair_templates.description IS '模板描述';
COMMENT ON COLUMN repair_templates.created_by IS '创建人';
COMMENT ON COLUMN repair_templates.created_at IS '创建时间';
COMMENT ON COLUMN repair_templates.updated_at IS '更新时间';
CREATE INDEX IF NOT EXISTS idx_repair_templates_fault_type ON repair_templates(fault_type);

-- 4.1 操作审计表
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    cluster_id BIGINT REFERENCES clusters(id) ON DELETE SET NULL ON UPDATE CASCADE,
    role_id BIGINT REFERENCES roles(id) ON DELETE SET NULL ON UPDATE CASCADE,
    username VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    ip_address INET NOT NULL,
    request_data JSONB,
    response_status INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- 表与字段注释
COMMENT ON TABLE audit_logs IS '操作审计表';
COMMENT ON COLUMN audit_logs.ip_address IS '请求来源IP(INET, 兼容IPv4/IPv6)';
COMMENT ON COLUMN audit_logs.id IS '主键ID';
COMMENT ON COLUMN audit_logs.user_id IS '用户ID';
COMMENT ON COLUMN audit_logs.cluster_id IS '集群ID';
COMMENT ON COLUMN audit_logs.role_id IS '角色ID';
COMMENT ON COLUMN audit_logs.username IS '用户名';
COMMENT ON COLUMN audit_logs.action IS '操作动作';
COMMENT ON COLUMN audit_logs.resource_type IS '资源类型';
COMMENT ON COLUMN audit_logs.resource_id IS '资源ID';
COMMENT ON COLUMN audit_logs.request_data IS '请求数据(JSONB)';
COMMENT ON COLUMN audit_logs.response_status IS '响应状态码';
COMMENT ON COLUMN audit_logs.created_at IS '创建时间';
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_cluster_id ON audit_logs(cluster_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_role_id ON audit_logs(role_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- =====================================================
-- 5. 初始化数据
-- =====================================================

INSERT INTO clusters (uuid, name, type, description, config_info) VALUES
('a1b2c3d4-e5f6-7890-1234-567890abcdef'::uuid, 'Hadoop主集群', 'Hadoop', '生产环境主Hadoop集群', '{"namenode_uri": "hdfs://nn1.hadoop.prod:8020"}'),
('b2c3d4e5-f6a7-8901-2345-67890abcdef1'::uuid, 'Hadoop测试集群', 'Hadoop', '用于测试的Hadoop集群', '{"namenode_uri": "hdfs://nn.hadoop.test:8020"}');

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

INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.role_key = 'super_admin';

INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.role_key = 'cluster_admin' AND p.permission_key IN (
    'cluster:read', 'cluster:update',
    'fault:read', 'fault:analyze', 'fault:repair',
    'log:read'
);

INSERT INTO role_permission_mapping (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.role_key = 'operator' AND p.permission_key IN (
    'fault:read', 'fault:repair', 'log:read'
);

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
SELECT 'PostgreSQL schema created successfully!' AS message;

-- =====================================================
-- 兼容性与差异说明（仅注释，不影响执行）
-- 1) JSONB/INET/UUID 为 PostgreSQL 原生类型；MySQL 脚本对应 JSON/VARCHAR(45)/VARCHAR(36)
-- 2) CHECK 约束在 PostgreSQL 中强制生效；MySQL 8.0 也支持，但历史版本可能忽略
-- 3) 索引创建统一在表后分组声明；与 MySQL 的 KEY/UNIQUE KEY 语法在风格上保持一致
-- 4) 字符集与排序规则：请确保数据库级设置为 ENCODING UTF8，LC_COLLATE/LC_CTYPE 与业务一致
