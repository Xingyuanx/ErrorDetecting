--
-- PostgreSQL database dump
--

\restrict x3vbKb2vAIlctC0uebdrXag55BFVsJBRQxqhKA1MdoFQjC3OJ9m4YZLeFNLKBRA

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg13+1)
-- Dumped by pg_dump version 15.15 (Debian 15.15-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: app_configurations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app_configurations (
    id bigint NOT NULL,
    config_type character varying(20) NOT NULL,
    config_key character varying(100) NOT NULL,
    config_value jsonb NOT NULL,
    description character varying(500),
    is_enabled boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT app_config_type_chk CHECK (((config_type)::text = ANY ((ARRAY['system'::character varying, 'alert_rule'::character varying, 'notification'::character varying, 'llm'::character varying])::text[])))
);


ALTER TABLE public.app_configurations OWNER TO postgres;

--
-- Name: TABLE app_configurations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.app_configurations IS '应用统一配置表';


--
-- Name: COLUMN app_configurations.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.id IS '主键ID';


--
-- Name: COLUMN app_configurations.config_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.config_type IS '配置类型(system/alert_rule/notification/llm)';


--
-- Name: COLUMN app_configurations.config_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.config_key IS '配置键';


--
-- Name: COLUMN app_configurations.config_value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.config_value IS '配置值(JSONB)';


--
-- Name: COLUMN app_configurations.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.description IS '配置描述';


--
-- Name: COLUMN app_configurations.is_enabled; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.is_enabled IS '是否启用';


--
-- Name: COLUMN app_configurations.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.created_at IS '创建时间';


--
-- Name: COLUMN app_configurations.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.updated_at IS '更新时间';


--
-- Name: app_configurations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.app_configurations ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.app_configurations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id bigint NOT NULL,
    user_id bigint,
    cluster_id bigint,
    role_id bigint,
    username character varying(50) NOT NULL,
    action character varying(100) NOT NULL,
    resource_type character varying(50) NOT NULL,
    resource_id character varying(100),
    ip_address inet NOT NULL,
    request_data jsonb,
    response_status integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: TABLE audit_logs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.audit_logs IS '操作审计表';


--
-- Name: COLUMN audit_logs.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.id IS '主键ID';


--
-- Name: COLUMN audit_logs.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.user_id IS '用户ID';


--
-- Name: COLUMN audit_logs.cluster_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.cluster_id IS '集群ID';


--
-- Name: COLUMN audit_logs.role_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.role_id IS '角色ID';


--
-- Name: COLUMN audit_logs.username; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.username IS '用户名';


--
-- Name: COLUMN audit_logs.action; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.action IS '操作动作';


--
-- Name: COLUMN audit_logs.resource_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.resource_type IS '资源类型';


--
-- Name: COLUMN audit_logs.resource_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.resource_id IS '资源ID';


--
-- Name: COLUMN audit_logs.ip_address; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.ip_address IS '请求来源IP(INET, 兼容IPv4/IPv6)';


--
-- Name: COLUMN audit_logs.request_data; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.request_data IS '请求数据(JSONB)';


--
-- Name: COLUMN audit_logs.response_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.response_status IS '响应状态码';


--
-- Name: COLUMN audit_logs.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.created_at IS '创建时间';


--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.audit_logs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.audit_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: clusters; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clusters (
    id bigint NOT NULL,
    uuid uuid NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(50) NOT NULL,
    node_count integer DEFAULT 0 NOT NULL,
    health_status character varying(20) DEFAULT 'unknown'::character varying NOT NULL,
    description text,
    config_info jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT clusters_health_status_chk CHECK (((health_status)::text = ANY ((ARRAY['healthy'::character varying, 'warning'::character varying, 'error'::character varying, 'unknown'::character varying])::text[])))
);


ALTER TABLE public.clusters OWNER TO postgres;

--
-- Name: TABLE clusters; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.clusters IS '集群信息表';


--
-- Name: COLUMN clusters.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.id IS '主键ID';


--
-- Name: COLUMN clusters.uuid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.uuid IS '集群唯一标识(UUID)';


--
-- Name: COLUMN clusters.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.name IS '集群名称';


--
-- Name: COLUMN clusters.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.type IS '集群类型';


--
-- Name: COLUMN clusters.node_count; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.node_count IS '集群节点数量';


--
-- Name: COLUMN clusters.health_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.health_status IS '集群健康状态(healthy/warning/error/unknown)';


--
-- Name: COLUMN clusters.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.description IS '集群描述';


--
-- Name: COLUMN clusters.config_info; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.config_info IS '集群配置信息(JSONB)';


--
-- Name: COLUMN clusters.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.created_at IS '创建时间';


--
-- Name: COLUMN clusters.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.updated_at IS '更新时间';


--
-- Name: clusters_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.clusters ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.clusters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: exec_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exec_logs (
    id bigint NOT NULL,
    exec_id character varying(32) NOT NULL,
    fault_id character varying(32) NOT NULL,
    command_type character varying(50) NOT NULL,
    script_path character varying(255),
    command_content text NOT NULL,
    target_nodes jsonb,
    risk_level character varying(20) DEFAULT 'medium'::character varying NOT NULL,
    execution_status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    start_time timestamp with time zone,
    end_time timestamp with time zone,
    duration integer,
    stdout_log text,
    stderr_log text,
    exit_code integer,
    operator character varying(50) DEFAULT 'system'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT exec_logs_duration_chk CHECK (((duration IS NULL) OR (duration >= 0))),
    CONSTRAINT exec_logs_risk_chk CHECK (((risk_level)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying])::text[]))),
    CONSTRAINT exec_logs_status_chk CHECK (((execution_status)::text = ANY ((ARRAY['pending'::character varying, 'running'::character varying, 'success'::character varying, 'failed'::character varying, 'timeout'::character varying])::text[])))
);


ALTER TABLE public.exec_logs OWNER TO postgres;

--
-- Name: TABLE exec_logs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.exec_logs IS '执行日志表';


--
-- Name: COLUMN exec_logs.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.id IS '主键ID';


--
-- Name: COLUMN exec_logs.exec_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.exec_id IS '执行唯一标识';


--
-- Name: COLUMN exec_logs.fault_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.fault_id IS '关联故障标识(无外键)';


--
-- Name: COLUMN exec_logs.command_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.command_type IS '命令类型';


--
-- Name: COLUMN exec_logs.script_path; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.script_path IS '脚本路径';


--
-- Name: COLUMN exec_logs.command_content; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.command_content IS '执行的命令内容';


--
-- Name: COLUMN exec_logs.target_nodes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.target_nodes IS '目标执行节点(JSONB)';


--
-- Name: COLUMN exec_logs.risk_level; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.risk_level IS '风险级别(low/medium/high)';


--
-- Name: COLUMN exec_logs.execution_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.execution_status IS '执行状态(pending/running/success/failed/timeout)';


--
-- Name: COLUMN exec_logs.start_time; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.start_time IS '开始执行时间';


--
-- Name: COLUMN exec_logs.end_time; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.end_time IS '结束执行时间';


--
-- Name: COLUMN exec_logs.duration; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.duration IS '执行时长(秒)';


--
-- Name: COLUMN exec_logs.stdout_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.stdout_log IS '标准输出日志';


--
-- Name: COLUMN exec_logs.stderr_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.stderr_log IS '错误输出日志';


--
-- Name: COLUMN exec_logs.exit_code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.exit_code IS '退出码';


--
-- Name: COLUMN exec_logs.operator; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.operator IS '操作人';


--
-- Name: COLUMN exec_logs.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.created_at IS '创建时间';


--
-- Name: COLUMN exec_logs.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.exec_logs.updated_at IS '更新时间';


--
-- Name: exec_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.exec_logs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.exec_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: nodes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nodes (
    id bigint NOT NULL,
    uuid uuid NOT NULL,
    cluster_id bigint NOT NULL,
    hostname character varying(100) NOT NULL,
    ip_address inet NOT NULL,
    status character varying(20) DEFAULT 'unknown'::character varying NOT NULL,
    cpu_usage numeric(5,2),
    memory_usage numeric(5,2),
    disk_usage numeric(5,2),
    last_heartbeat timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT nodes_cpu_chk CHECK (((cpu_usage IS NULL) OR ((cpu_usage >= (0)::numeric) AND (cpu_usage <= (100)::numeric)))),
    CONSTRAINT nodes_disk_chk CHECK (((disk_usage IS NULL) OR ((disk_usage >= (0)::numeric) AND (disk_usage <= (100)::numeric)))),
    CONSTRAINT nodes_mem_chk CHECK (((memory_usage IS NULL) OR ((memory_usage >= (0)::numeric) AND (memory_usage <= (100)::numeric)))),
    CONSTRAINT nodes_status_chk CHECK (((status)::text = ANY ((ARRAY['healthy'::character varying, 'unhealthy'::character varying, 'warning'::character varying, 'unknown'::character varying])::text[])))
);


ALTER TABLE public.nodes OWNER TO postgres;

--
-- Name: TABLE nodes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.nodes IS '节点信息表';


--
-- Name: COLUMN nodes.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.id IS '主键ID';


--
-- Name: COLUMN nodes.uuid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.uuid IS '节点唯一标识(UUID)';


--
-- Name: COLUMN nodes.cluster_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.cluster_id IS '所属集群ID';


--
-- Name: COLUMN nodes.hostname; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.hostname IS '节点主机名';


--
-- Name: COLUMN nodes.ip_address; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.ip_address IS '节点IP地址(INET, 兼容IPv4/IPv6)';


--
-- Name: COLUMN nodes.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.status IS '节点健康状态(healthy/unhealthy/warning/unknown)';


--
-- Name: COLUMN nodes.cpu_usage; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.cpu_usage IS 'CPU使用率(%)';


--
-- Name: COLUMN nodes.memory_usage; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.memory_usage IS '内存使用率(%)';


--
-- Name: COLUMN nodes.disk_usage; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.disk_usage IS '磁盘使用率(%)';


--
-- Name: COLUMN nodes.last_heartbeat; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.last_heartbeat IS '最后心跳时间';


--
-- Name: COLUMN nodes.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.created_at IS '创建时间';


--
-- Name: COLUMN nodes.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.updated_at IS '更新时间';


--
-- Name: nodes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.nodes ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.nodes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id bigint NOT NULL,
    permission_name character varying(100) NOT NULL,
    permission_key character varying(100) NOT NULL,
    description character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: TABLE permissions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.permissions IS '权限表';


--
-- Name: COLUMN permissions.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.permissions.id IS '主键ID';


--
-- Name: COLUMN permissions.permission_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.permissions.permission_name IS '权限名称';


--
-- Name: COLUMN permissions.permission_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.permissions.permission_key IS '权限唯一标识';


--
-- Name: COLUMN permissions.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.permissions.description IS '权限描述';


--
-- Name: COLUMN permissions.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.permissions.created_at IS '创建时间';


--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.permissions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: repair_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.repair_templates (
    id bigint NOT NULL,
    template_name character varying(100) NOT NULL,
    fault_type character varying(50) NOT NULL,
    script_content text NOT NULL,
    risk_level character varying(20) DEFAULT 'medium'::character varying NOT NULL,
    description text,
    parameters jsonb,
    created_by character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT repair_templates_risk_chk CHECK (((risk_level)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying])::text[])))
);


ALTER TABLE public.repair_templates OWNER TO postgres;

--
-- Name: TABLE repair_templates; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.repair_templates IS '修复脚本模板表';


--
-- Name: COLUMN repair_templates.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.id IS '主键ID';


--
-- Name: COLUMN repair_templates.template_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.template_name IS '模板名称';


--
-- Name: COLUMN repair_templates.fault_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.fault_type IS '适用故障类型';


--
-- Name: COLUMN repair_templates.script_content; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.script_content IS '脚本内容';


--
-- Name: COLUMN repair_templates.risk_level; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.risk_level IS '风险级别(low/medium/high)';


--
-- Name: COLUMN repair_templates.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.description IS '模板描述';


--
-- Name: COLUMN repair_templates.parameters; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.parameters IS '模板参数定义(JSONB)';


--
-- Name: COLUMN repair_templates.created_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.created_by IS '创建人';


--
-- Name: COLUMN repair_templates.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.created_at IS '创建时间';


--
-- Name: COLUMN repair_templates.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.updated_at IS '更新时间';


--
-- Name: repair_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.repair_templates ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.repair_templates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: role_permission_mapping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permission_mapping (
    role_id bigint NOT NULL,
    permission_id bigint NOT NULL
);


ALTER TABLE public.role_permission_mapping OWNER TO postgres;

--
-- Name: TABLE role_permission_mapping; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.role_permission_mapping IS '角色-权限映射表';


--
-- Name: COLUMN role_permission_mapping.role_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.role_permission_mapping.role_id IS '角色ID';


--
-- Name: COLUMN role_permission_mapping.permission_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.role_permission_mapping.permission_id IS '权限ID';


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id bigint NOT NULL,
    role_name character varying(50) NOT NULL,
    role_key character varying(50) NOT NULL,
    description character varying(255),
    is_system_role boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: TABLE roles; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.roles IS '角色表';


--
-- Name: COLUMN roles.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.id IS '主键ID';


--
-- Name: COLUMN roles.role_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.role_name IS '角色名称';


--
-- Name: COLUMN roles.role_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.role_key IS '角色唯一标识';


--
-- Name: COLUMN roles.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.description IS '角色描述';


--
-- Name: COLUMN roles.is_system_role; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.is_system_role IS '是否为系统内置角色';


--
-- Name: COLUMN roles.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.created_at IS '创建时间';


--
-- Name: COLUMN roles.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.updated_at IS '更新时间';


--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.roles ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: system_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_logs (
    id bigint NOT NULL,
    log_id character varying(32) NOT NULL,
    fault_id character varying(32),
    cluster_id bigint,
    "timestamp" timestamp with time zone NOT NULL,
    host character varying(100) NOT NULL,
    service character varying(50) NOT NULL,
    source character varying(50),
    log_level character varying(10) NOT NULL,
    message text NOT NULL,
    exception text,
    raw_log text,
    processed boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT system_logs_level_chk CHECK (((log_level)::text = ANY ((ARRAY['DEBUG'::character varying, 'INFO'::character varying, 'WARN'::character varying, 'ERROR'::character varying, 'FATAL'::character varying])::text[])))
);


ALTER TABLE public.system_logs OWNER TO postgres;

--
-- Name: TABLE system_logs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.system_logs IS '系统日志表';


--
-- Name: COLUMN system_logs.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.id IS '主键ID';


--
-- Name: COLUMN system_logs.log_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.log_id IS '日志唯一标识';


--
-- Name: COLUMN system_logs.fault_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.fault_id IS '关联故障标识(无外键)';


--
-- Name: COLUMN system_logs.cluster_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.cluster_id IS '关联集群ID';


--
-- Name: COLUMN system_logs."timestamp"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs."timestamp" IS '日志时间戳';


--
-- Name: COLUMN system_logs.host; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.host IS '主机名';


--
-- Name: COLUMN system_logs.service; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.service IS '服务名';


--
-- Name: COLUMN system_logs.source; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.source IS '来源';


--
-- Name: COLUMN system_logs.log_level; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.log_level IS '日志级别(DEBUG/INFO/WARN/ERROR/FATAL)';


--
-- Name: COLUMN system_logs.message; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.message IS '日志消息';


--
-- Name: COLUMN system_logs.exception; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.exception IS '异常堆栈';


--
-- Name: COLUMN system_logs.raw_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.raw_log IS '原始日志内容';


--
-- Name: COLUMN system_logs.processed; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.processed IS '是否已处理';


--
-- Name: COLUMN system_logs.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.system_logs.created_at IS '创建时间';


--
-- Name: system_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.system_logs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.system_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: user_cluster_mapping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_cluster_mapping (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    cluster_id bigint NOT NULL,
    role_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_cluster_mapping OWNER TO postgres;

--
-- Name: TABLE user_cluster_mapping; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.user_cluster_mapping IS '用户与集群映射表';


--
-- Name: COLUMN user_cluster_mapping.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_cluster_mapping.id IS '主键ID';


--
-- Name: COLUMN user_cluster_mapping.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_cluster_mapping.user_id IS '用户ID';


--
-- Name: COLUMN user_cluster_mapping.cluster_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_cluster_mapping.cluster_id IS '集群ID';


--
-- Name: COLUMN user_cluster_mapping.role_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_cluster_mapping.role_id IS '角色ID';


--
-- Name: COLUMN user_cluster_mapping.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_cluster_mapping.created_at IS '创建时间';


--
-- Name: user_cluster_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.user_cluster_mapping ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.user_cluster_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: user_role_mapping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_role_mapping (
    user_id bigint NOT NULL,
    role_id bigint NOT NULL
);


ALTER TABLE public.user_role_mapping OWNER TO postgres;

--
-- Name: TABLE user_role_mapping; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.user_role_mapping IS '用户-角色映射表';


--
-- Name: COLUMN user_role_mapping.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_role_mapping.user_id IS '用户ID';


--
-- Name: COLUMN user_role_mapping.role_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_role_mapping.role_id IS '角色ID';


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(100) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    last_login timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.users IS '用户表';


--
-- Name: COLUMN users.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.id IS '主键ID';


--
-- Name: COLUMN users.username; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.username IS '用户名';


--
-- Name: COLUMN users.email; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.email IS '邮箱';


--
-- Name: COLUMN users.password_hash; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.password_hash IS '密码哈希';


--
-- Name: COLUMN users.full_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.full_name IS '姓名';


--
-- Name: COLUMN users.is_active; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.is_active IS '是否激活';


--
-- Name: COLUMN users.last_login; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.last_login IS '最后登录时间';


--
-- Name: COLUMN users.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.created_at IS '创建时间';


--
-- Name: COLUMN users.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.updated_at IS '更新时间';


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: app_configurations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.app_configurations (id, config_type, config_key, config_value, description, is_enabled, created_at, updated_at) FROM stdin;
1	system	system.name	{"value": "故障检测系统"}	系统名称	t	2025-12-12 02:42:15.555003+00	2025-12-12 02:42:15.555003+00
2	system	log.retention.days	{"value": 90}	日志保留天数	t	2025-12-12 02:42:15.555003+00	2025-12-12 02:42:15.555003+00
3	system	repair.auto.enabled	{"value": false}	是否启用自动修复	t	2025-12-12 02:42:15.555003+00	2025-12-12 02:42:15.555003+00
4	llm	api.timeout	{"value": 30}	LLM API超时时间(秒)	t	2025-12-12 02:42:15.555003+00	2025-12-12 02:42:15.555003+00
5	alert_rule	CPU使用率过高	{"metric": "cpu_usage", "severity": "high", "condition": ">", "threshold": 85}	CPU使用率超过85%时触发告警	t	2025-12-12 02:42:15.555835+00	2025-12-12 02:42:15.555835+00
6	alert_rule	内存使用率过高	{"metric": "memory_usage", "severity": "high", "condition": ">", "threshold": 90}	内存使用率超过90%时触发告警	t	2025-12-12 02:42:15.555835+00	2025-12-12 02:42:15.555835+00
7	alert_rule	节点离线	{"value": "offline", "metric": "node_status", "severity": "critical", "condition": "="}	节点离线时触发告警	t	2025-12-12 02:42:15.555835+00	2025-12-12 02:42:15.555835+00
8	notification	默认邮件通知	{"type": "email", "triggers": ["high", "critical"], "recipients": ["admin@example.com"]}	向管理员发送高危和严重故障的邮件通知	t	2025-12-12 02:42:15.556355+00	2025-12-12 02:42:15.556355+00
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, user_id, cluster_id, role_id, username, action, resource_type, resource_id, ip_address, request_data, response_status, created_at) FROM stdin;
\.


--
-- Data for Name: clusters; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clusters (id, uuid, name, type, node_count, health_status, description, config_info, created_at, updated_at) FROM stdin;
1	a1b2c3d4-e5f6-7890-1234-567890abcdef	Hadoop主集群	Hadoop	0	unknown	生产环境主Hadoop集群	{"namenode_uri": "hdfs://nn1.hadoop.prod:8020"}	2025-12-12 02:42:15.548794+00	2025-12-12 02:42:15.548794+00
2	b2c3d4e5-f6a7-8901-2345-67890abcdef1	Hadoop测试集群	Hadoop	0	unknown	用于测试的Hadoop集群	{"namenode_uri": "hdfs://nn.hadoop.test:8020"}	2025-12-12 02:42:15.548794+00	2025-12-12 02:42:15.548794+00
\.


--
-- Data for Name: exec_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exec_logs (id, exec_id, fault_id, command_type, script_path, command_content, target_nodes, risk_level, execution_status, start_time, end_time, duration, stdout_log, stderr_log, exit_code, operator, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nodes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nodes (id, uuid, cluster_id, hostname, ip_address, status, cpu_usage, memory_usage, disk_usage, last_heartbeat, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (id, permission_name, permission_key, description, created_at) FROM stdin;
19	用户管理	user:manage	用户的创建、修改、删除与查询	2025-12-14 07:35:24.029806+00
20	角色分配	role:assign	为用户分配角色	2025-12-14 07:35:24.072852+00
21	权限策略管理	policy:manage	维护权限策略与分配	2025-12-14 07:35:24.126385+00
22	审计日志管理	audit:manage	审计日志的查询与清理管理	2025-12-14 07:35:24.167929+00
23	集群列表查看	cluster:list:read	查看集群列表与状态	2025-12-14 07:35:24.209617+00
24	集群列表管理	cluster:list:manage	新增/修改/删除集群	2025-12-14 07:35:24.265104+00
25	日志查询	log:query	查询系统或业务日志	2025-12-14 07:35:24.307086+00
26	日志管理	log:manage	日志清理、归档或删除	2025-12-14 07:35:24.357143+00
27	故障诊断	fault:diagnose	执行故障分析操作	2025-12-14 07:35:24.399563+00
28	执行日志查看	exec_log:read	查看执行日志记录	2025-12-14 07:35:24.454338+00
29	执行日志管理	exec_log:manage	管理执行日志（例如删除）	2025-12-14 07:35:24.496722+00
30	系统配置	system:config	系统配置与参数维护	2025-12-14 07:35:24.554589+00
\.


--
-- Data for Name: repair_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.repair_templates (id, template_name, fault_type, script_content, risk_level, description, parameters, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: role_permission_mapping; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permission_mapping (role_id, permission_id) FROM stdin;
7	19
7	20
7	21
7	22
7	23
7	24
7	25
7	26
7	27
7	28
7	29
7	30
8	23
8	24
8	25
8	26
8	27
8	28
8	29
10	23
10	25
10	26
10	28
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, role_name, role_key, description, is_system_role, created_at, updated_at) FROM stdin;
7	管理员	admin	拥有所有权限	t	2025-12-14 07:33:23.611365+00	2025-12-14 07:33:23.611365+00
8	操作员	operator	除系统管理外的操作权限	t	2025-12-14 07:33:23.653257+00	2025-12-14 07:33:23.653257+00
10	观察员	observer	基于操作员的只读子集	t	2025-12-14 07:34:28.548724+00	2025-12-14 07:34:28.548724+00
\.


--
-- Data for Name: system_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_logs (id, log_id, fault_id, cluster_id, "timestamp", host, service, source, log_level, message, exception, raw_log, processed, created_at) FROM stdin;
\.


--
-- Data for Name: user_cluster_mapping; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_cluster_mapping (id, user_id, cluster_id, role_id, created_at) FROM stdin;
\.


--
-- Data for Name: user_role_mapping; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_role_mapping (user_id, role_id) FROM stdin;
4	7
3	7
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, full_name, is_active, last_login, created_at, updated_at) FROM stdin;
4	bdmin	bdmin@qq.com	$2b$12$.jKVn3UqH/w0Ajdi01aqY.K70z8QEtLlgL45u883hKp2sWREYG4Om	bdmin	t	2025-12-12 07:47:22.734564+00	2025-12-12 07:15:29.72108+00	2025-12-12 07:47:22.734564+00
3	admin	admin@qq.com	$2b$12$F85LDEh5BP3G9VY9q/ALh.YpRNn.ob5fZM3fcfu.8G/B/WNgeBZPS	admin	t	2025-12-12 07:47:31.178442+00	2025-12-12 06:58:05.785083+00	2025-12-12 07:47:31.178442+00
\.


--
-- Name: app_configurations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.app_configurations_id_seq', 9, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 1, false);


--
-- Name: clusters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clusters_id_seq', 2, true);


--
-- Name: exec_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exec_logs_id_seq', 1, false);


--
-- Name: nodes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nodes_id_seq', 1, false);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permissions_id_seq', 30, true);


--
-- Name: repair_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.repair_templates_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 10, true);


--
-- Name: system_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_logs_id_seq', 1, false);


--
-- Name: user_cluster_mapping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_cluster_mapping_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 4, true);


--
-- Name: app_configurations app_configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_configurations
    ADD CONSTRAINT app_configurations_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: clusters clusters_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clusters
    ADD CONSTRAINT clusters_name_key UNIQUE (name);


--
-- Name: clusters clusters_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clusters
    ADD CONSTRAINT clusters_pkey PRIMARY KEY (id);


--
-- Name: clusters clusters_uuid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clusters
    ADD CONSTRAINT clusters_uuid_key UNIQUE (uuid);


--
-- Name: exec_logs exec_logs_exec_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exec_logs
    ADD CONSTRAINT exec_logs_exec_id_key UNIQUE (exec_id);


--
-- Name: exec_logs exec_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exec_logs
    ADD CONSTRAINT exec_logs_pkey PRIMARY KEY (id);


--
-- Name: nodes nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_pkey PRIMARY KEY (id);


--
-- Name: nodes nodes_uuid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_uuid_key UNIQUE (uuid);


--
-- Name: permissions permissions_permission_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_permission_key_key UNIQUE (permission_key);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: repair_templates repair_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_templates
    ADD CONSTRAINT repair_templates_pkey PRIMARY KEY (id);


--
-- Name: repair_templates repair_templates_template_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_templates
    ADD CONSTRAINT repair_templates_template_name_key UNIQUE (template_name);


--
-- Name: role_permission_mapping role_permission_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permission_mapping
    ADD CONSTRAINT role_permission_mapping_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: roles roles_role_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_role_key_key UNIQUE (role_key);


--
-- Name: system_logs system_logs_log_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_logs
    ADD CONSTRAINT system_logs_log_id_key UNIQUE (log_id);


--
-- Name: system_logs system_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_logs
    ADD CONSTRAINT system_logs_pkey PRIMARY KEY (id);


--
-- Name: app_configurations uk_app_config; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_configurations
    ADD CONSTRAINT uk_app_config UNIQUE (config_type, config_key);


--
-- Name: user_cluster_mapping uk_user_cluster; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_cluster_mapping
    ADD CONSTRAINT uk_user_cluster UNIQUE (user_id, cluster_id);


--
-- Name: user_cluster_mapping user_cluster_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_cluster_mapping
    ADD CONSTRAINT user_cluster_mapping_pkey PRIMARY KEY (id);


--
-- Name: user_role_mapping user_role_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT user_role_mapping_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_app_config_enabled; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_app_config_enabled ON public.app_configurations USING btree (is_enabled);


--
-- Name: idx_audit_logs_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: idx_audit_logs_cluster_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_cluster_id ON public.audit_logs USING btree (cluster_id);


--
-- Name: idx_audit_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: idx_audit_logs_role_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_role_id ON public.audit_logs USING btree (role_id);


--
-- Name: idx_audit_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- Name: idx_exec_logs_end_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exec_logs_end_time ON public.exec_logs USING btree (end_time);


--
-- Name: idx_exec_logs_fault_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exec_logs_fault_id ON public.exec_logs USING btree (fault_id);


--
-- Name: idx_exec_logs_start_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exec_logs_start_time ON public.exec_logs USING btree (start_time);


--
-- Name: idx_exec_logs_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exec_logs_status ON public.exec_logs USING btree (execution_status);


--
-- Name: idx_nodes_cluster_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nodes_cluster_id ON public.nodes USING btree (cluster_id);


--
-- Name: idx_nodes_ip_address; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nodes_ip_address ON public.nodes USING btree (ip_address);


--
-- Name: idx_nodes_last_heartbeat; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nodes_last_heartbeat ON public.nodes USING btree (last_heartbeat);


--
-- Name: idx_nodes_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nodes_status ON public.nodes USING btree (status);


--
-- Name: idx_repair_templates_fault_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_repair_templates_fault_type ON public.repair_templates USING btree (fault_type);


--
-- Name: idx_system_logs_cluster_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_logs_cluster_id ON public.system_logs USING btree (cluster_id);


--
-- Name: idx_system_logs_fault_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_logs_fault_id ON public.system_logs USING btree (fault_id);


--
-- Name: idx_system_logs_level; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_logs_level ON public.system_logs USING btree (log_level);


--
-- Name: idx_system_logs_processed; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_logs_processed ON public.system_logs USING btree (processed);


--
-- Name: idx_system_logs_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_logs_timestamp ON public.system_logs USING btree ("timestamp");


--
-- Name: uk_cluster_hostname; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uk_cluster_hostname ON public.nodes USING btree (cluster_id, hostname);


--
-- Name: audit_logs audit_logs_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.clusters(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: audit_logs audit_logs_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: nodes nodes_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.clusters(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: role_permission_mapping role_permission_mapping_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permission_mapping
    ADD CONSTRAINT role_permission_mapping_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: role_permission_mapping role_permission_mapping_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permission_mapping
    ADD CONSTRAINT role_permission_mapping_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: system_logs system_logs_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_logs
    ADD CONSTRAINT system_logs_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.clusters(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: user_cluster_mapping user_cluster_mapping_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_cluster_mapping
    ADD CONSTRAINT user_cluster_mapping_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.clusters(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_cluster_mapping user_cluster_mapping_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_cluster_mapping
    ADD CONSTRAINT user_cluster_mapping_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_cluster_mapping user_cluster_mapping_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_cluster_mapping
    ADD CONSTRAINT user_cluster_mapping_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_role_mapping user_role_mapping_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT user_role_mapping_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_role_mapping user_role_mapping_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT user_role_mapping_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO echo;


--
-- Name: TABLE app_configurations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.app_configurations TO echo;


--
-- Name: SEQUENCE app_configurations_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.app_configurations_id_seq TO echo;


--
-- Name: TABLE audit_logs; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.audit_logs TO echo;


--
-- Name: SEQUENCE audit_logs_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.audit_logs_id_seq TO echo;


--
-- Name: TABLE clusters; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.clusters TO echo;


--
-- Name: SEQUENCE clusters_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.clusters_id_seq TO echo;


--
-- Name: TABLE exec_logs; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.exec_logs TO echo;


--
-- Name: SEQUENCE exec_logs_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.exec_logs_id_seq TO echo;


--
-- Name: TABLE nodes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.nodes TO echo;


--
-- Name: SEQUENCE nodes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.nodes_id_seq TO echo;


--
-- Name: TABLE permissions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.permissions TO echo;


--
-- Name: SEQUENCE permissions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.permissions_id_seq TO echo;


--
-- Name: TABLE repair_templates; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.repair_templates TO echo;


--
-- Name: SEQUENCE repair_templates_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.repair_templates_id_seq TO echo;


--
-- Name: TABLE role_permission_mapping; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.role_permission_mapping TO echo;


--
-- Name: TABLE roles; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.roles TO echo;


--
-- Name: SEQUENCE roles_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.roles_id_seq TO echo;


--
-- Name: TABLE system_logs; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.system_logs TO echo;


--
-- Name: SEQUENCE system_logs_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.system_logs_id_seq TO echo;


--
-- Name: TABLE user_cluster_mapping; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.user_cluster_mapping TO echo;


--
-- Name: SEQUENCE user_cluster_mapping_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.user_cluster_mapping_id_seq TO echo;


--
-- Name: TABLE user_role_mapping; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.user_role_mapping TO echo;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.users TO echo;


--
-- Name: SEQUENCE users_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.users_id_seq TO echo;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES  TO echo;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES  TO echo;


--
-- PostgreSQL database dump complete
--

\unrestrict x3vbKb2vAIlctC0uebdrXag55BFVsJBRQxqhKA1MdoFQjC3OJ9m4YZLeFNLKBRA

