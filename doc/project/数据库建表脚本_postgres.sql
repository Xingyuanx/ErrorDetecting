-- ==================================================
-- 数据库建表脚本 (PostgreSQL)
-- 生成日期: 2025-12-30
-- 数据库: hadoop_fault_db
-- ==================================================

-- --------------------------------------------------
-- 1. 架构与扩展
-- --------------------------------------------------
--
-- Name: metric_helpers; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA metric_helpers;;
--
-- Name: user_management; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA user_management;;
--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;;
--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';;
--
-- Name: pg_stat_kcache; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_kcache WITH SCHEMA public;;
--
-- Name: EXTENSION pg_stat_kcache; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_kcache IS 'Kernel statistics gathering';;
--
-- Name: set_user; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS set_user WITH SCHEMA public;;
--
-- Name: EXTENSION set_user; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION set_user IS 'similar to SET ROLE but with added logging';;
--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;;
--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';;


-- --------------------------------------------------
-- 2. 自定义函数
-- --------------------------------------------------
--
-- Name: get_btree_bloat_approx(); Type: FUNCTION; Schema: metric_helpers; Owner: postgres
--

CREATE FUNCTION metric_helpers.get_btree_bloat_approx(OUT i_database name, OUT i_schema_name name, OUT i_table_name name, OUT i_index_name name, OUT i_real_size numeric, OUT i_extra_size numeric, OUT i_extra_ratio double precision, OUT i_fill_factor integer, OUT i_bloat_size double precision, OUT i_bloat_ratio double precision, OUT i_is_na boolean) RETURNS SETOF record
    LANGUAGE sql IMMUTABLE STRICT SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $$
SELECT current_database(), nspname AS schemaname, tblname, idxname, bs*(relpages)::bigint AS real_size,
  bs*(relpages-est_pages)::bigint AS extra_size,
  100 * (relpages-est_pages)::float / relpages AS extra_ratio,
  fillfactor,
  CASE WHEN relpages > est_pages_ff
    THEN bs*(relpages-est_pages_ff)
    ELSE 0
  END AS bloat_size,
  100 * (relpages-est_pages_ff)::float / relpages AS bloat_ratio,
  is_na
  -- , 100-(pst).avg_leaf_density AS pst_avg_bloat, est_pages, index_tuple_hdr_bm, maxalign, pagehdr, nulldatawidth, nulldatahdrwidth, reltuples, relpages -- (DEBUG INFO)
FROM (
  SELECT coalesce(1 +
         ceil(reltuples/floor((bs-pageopqdata-pagehdr)/(4+nulldatahdrwidth)::float)), 0 -- ItemIdData size + computed avg size of a tuple (nulldatahdrwidth)
      ) AS est_pages,
      coalesce(1 +
         ceil(reltuples/floor((bs-pageopqdata-pagehdr)*fillfactor/(100*(4+nulldatahdrwidth)::float))), 0
      ) AS est_pages_ff,
      bs, nspname, tblname, idxname, relpages, fillfactor, is_na
      -- , pgstatindex(idxoid) AS pst, index_tuple_hdr_bm, maxalign, pagehdr, nulldatawidth, nulldatahdrwidth, reltuples -- (DEBUG INFO)
  FROM (
      SELECT maxalign, bs, nspname, tblname, idxname, reltuples, relpages, idxoid, fillfactor,
            ( index_tuple_hdr_bm +
                maxalign - CASE -- Add padding to the index tuple header to align on MAXALIGN
                  WHEN index_tuple_hdr_bm%maxalign = 0 THEN maxalign
                  ELSE index_tuple_hdr_bm%maxalign
                END
              + nulldatawidth + maxalign - CASE -- Add padding to the data to align on MAXALIGN
                  WHEN nulldatawidth = 0 THEN 0
                  WHEN nulldatawidth::integer%maxalign = 0 THEN maxalign
                  ELSE nulldatawidth::integer%maxalign
                END
            )::numeric AS nulldatahdrwidth, pagehdr, pageopqdata, is_na
            -- , index_tuple_hdr_bm, nulldatawidth -- (DEBUG INFO)
      FROM (
          SELECT n.nspname, ct.relname AS tblname, i.idxname, i.reltuples, i.relpages,
              i.idxoid, i.fillfactor, current_setting('block_size')::numeric AS bs,
              CASE -- MAXALIGN: 4 on 32bits, 8 on 64bits (and mingw32 ?)
                WHEN version() ~ 'mingw32' OR version() ~ '64-bit|x86_64|ppc64|ia64|amd64' THEN 8
                ELSE 4
              END AS maxalign,
              /* per page header, fixed size: 20 for 7.X, 24 for others */
              24 AS pagehdr,
              /* per page btree opaque data */
              16 AS pageopqdata,
              /* per tuple header: add IndexAttributeBitMapData if some cols are null-able */
              CASE WHEN max(coalesce(s.stanullfrac,0)) = 0
                  THEN 2 -- IndexTupleData size
                  ELSE 2 + (( 32 + 8 - 1 ) / 8) -- IndexTupleData size + IndexAttributeBitMapData size ( max num filed per index + 8 - 1 /8)
              END AS index_tuple_hdr_bm,
              /* data len: we remove null values save space using it fractionnal part from stats */
              sum( (1-coalesce(s.stanullfrac, 0)) * coalesce(s.stawidth, 1024)) AS nulldatawidth,
              max( CASE WHEN a.atttypid = 'pg_catalog.name'::regtype THEN 1 ELSE 0 END ) > 0 AS is_na
          FROM (
              SELECT idxname, reltuples, relpages, tbloid, idxoid, fillfactor,
                  CASE WHEN indkey[i]=0 THEN idxoid ELSE tbloid END AS att_rel,
                  CASE WHEN indkey[i]=0 THEN i ELSE indkey[i] END AS att_pos
              FROM (
                  SELECT idxname, reltuples, relpages, tbloid, idxoid, fillfactor, indkey, generate_series(1,indnatts) AS i
                  FROM (
                      SELECT ci.relname AS idxname, ci.reltuples, ci.relpages, i.indrelid AS tbloid,
                          i.indexrelid AS idxoid,
                          coalesce(substring(
                              array_to_string(ci.reloptions, ' ')
                              from 'fillfactor=([0-9]+)')::smallint, 90) AS fillfactor,
                          i.indnatts,
                          string_to_array(textin(int2vectorout(i.indkey)),' ')::int[] AS indkey
                      FROM pg_index i
                      JOIN pg_class ci ON ci.oid=i.indexrelid
                      WHERE ci.relam=(SELECT oid FROM pg_am WHERE amname = 'btree')
                        AND ci.relpages > 0
                  ) AS idx_data
              ) AS idx_data_cross
          ) i
          JOIN pg_attribute a ON a.attrelid = i.att_rel
                             AND a.attnum = i.att_pos
          JOIN pg_statistic s ON s.starelid = i.att_rel
                             AND s.staattnum = i.att_pos
          JOIN pg_class ct ON ct.oid = i.tbloid
          JOIN pg_namespace n ON ct.relnamespace = n.oid
          GROUP BY 1,2,3,4,5,6,7,8,9,10
      ) AS rows_data_stats
  ) AS rows_hdr_pdg_stats
) AS relation_stats;;
--
-- Name: get_nearly_exhausted_sequences(double precision); Type: FUNCTION; Schema: metric_helpers; Owner: postgres
--

CREATE FUNCTION metric_helpers.get_nearly_exhausted_sequences(threshold double precision, OUT schemaname name, OUT sequencename name, OUT seq_percent_used numeric) RETURNS SETOF record
    LANGUAGE sql STRICT SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $$
SELECT *
FROM (
  SELECT 
    schemaname,
    sequencename,
    round(abs(
      ceil((abs(last_value::numeric - start_value) + 1) / increment_by) / 
        floor((CASE WHEN increment_by > 0
                    THEN (max_value::numeric - start_value)
                    ELSE (start_value::numeric - min_value)
                    END + 1) / increment_by
              ) * 100 
      ), 
    2) AS seq_percent_used
  FROM pg_sequences
  WHERE NOT CYCLE AND last_value IS NOT NULL
) AS s
WHERE seq_percent_used >= threshold;;
--
-- Name: get_table_bloat_approx(); Type: FUNCTION; Schema: metric_helpers; Owner: postgres
--

CREATE FUNCTION metric_helpers.get_table_bloat_approx(OUT t_database name, OUT t_schema_name name, OUT t_table_name name, OUT t_real_size numeric, OUT t_extra_size double precision, OUT t_extra_ratio double precision, OUT t_fill_factor integer, OUT t_bloat_size double precision, OUT t_bloat_ratio double precision, OUT t_is_na boolean) RETURNS SETOF record
    LANGUAGE sql IMMUTABLE STRICT SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $$
SELECT
  current_database(),
  schemaname,
  tblname,
  (bs*tblpages) AS real_size,
  ((tblpages-est_tblpages)*bs) AS extra_size,
  CASE WHEN tblpages - est_tblpages > 0
    THEN 100 * (tblpages - est_tblpages)/tblpages::float
    ELSE 0
  END AS extra_ratio,
  fillfactor,
  CASE WHEN tblpages - est_tblpages_ff > 0
    THEN (tblpages-est_tblpages_ff)*bs
    ELSE 0
  END AS bloat_size,
  CASE WHEN tblpages - est_tblpages_ff > 0
    THEN 100 * (tblpages - est_tblpages_ff)/tblpages::float
    ELSE 0
  END AS bloat_ratio,
  is_na
FROM (
  SELECT ceil( reltuples / ( (bs-page_hdr)/tpl_size ) ) + ceil( toasttuples / 4 ) AS est_tblpages,
    ceil( reltuples / ( (bs-page_hdr)*fillfactor/(tpl_size*100) ) ) + ceil( toasttuples / 4 ) AS est_tblpages_ff,
    tblpages, fillfactor, bs, tblid, schemaname, tblname, heappages, toastpages, is_na
    -- , tpl_hdr_size, tpl_data_size, pgstattuple(tblid) AS pst -- (DEBUG INFO)
  FROM (
    SELECT
      ( 4 + tpl_hdr_size + tpl_data_size + (2*ma)
        - CASE WHEN tpl_hdr_size%ma = 0 THEN ma ELSE tpl_hdr_size%ma END
        - CASE WHEN ceil(tpl_data_size)::int%ma = 0 THEN ma ELSE ceil(tpl_data_size)::int%ma END
      ) AS tpl_size, bs - page_hdr AS size_per_block, (heappages + toastpages) AS tblpages, heappages,
      toastpages, reltuples, toasttuples, bs, page_hdr, tblid, schemaname, tblname, fillfactor, is_na
      -- , tpl_hdr_size, tpl_data_size
    FROM (
      SELECT
        tbl.oid AS tblid, ns.nspname AS schemaname, tbl.relname AS tblname, tbl.reltuples,
        tbl.relpages AS heappages, coalesce(toast.relpages, 0) AS toastpages,
        coalesce(toast.reltuples, 0) AS toasttuples,
        coalesce(substring(
          array_to_string(tbl.reloptions, ' ')
          FROM 'fillfactor=([0-9]+)')::smallint, 100) AS fillfactor,
        current_setting('block_size')::numeric AS bs,
        CASE WHEN version()~'mingw32' OR version()~'64-bit|x86_64|ppc64|ia64|amd64' THEN 8 ELSE 4 END AS ma,
        24 AS page_hdr,
        23 + CASE WHEN MAX(coalesce(s.null_frac,0)) > 0 THEN ( 7 + count(s.attname) ) / 8 ELSE 0::int END
           + CASE WHEN bool_or(att.attname = 'oid' and att.attnum < 0) THEN 4 ELSE 0 END AS tpl_hdr_size,
        sum( (1-coalesce(s.null_frac, 0)) * coalesce(s.avg_width, 0) ) AS tpl_data_size,
        bool_or(att.atttypid = 'pg_catalog.name'::regtype)
          OR sum(CASE WHEN att.attnum > 0 THEN 1 ELSE 0 END) <> count(s.attname) AS is_na
      FROM pg_attribute AS att
        JOIN pg_class AS tbl ON att.attrelid = tbl.oid
        JOIN pg_namespace AS ns ON ns.oid = tbl.relnamespace
        LEFT JOIN pg_stats AS s ON s.schemaname=ns.nspname
          AND s.tablename = tbl.relname AND s.inherited=false AND s.attname=att.attname
        LEFT JOIN pg_class AS toast ON tbl.reltoastrelid = toast.oid
      WHERE NOT att.attisdropped
        AND tbl.relkind = 'r'
      GROUP BY 1,2,3,4,5,6,7,8,9,10
      ORDER BY 2,3
    ) AS s
  ) AS s2
) AS s3 WHERE schemaname NOT LIKE 'information_schema';;
--
-- Name: pg_stat_statements(boolean); Type: FUNCTION; Schema: metric_helpers; Owner: postgres
--

CREATE FUNCTION metric_helpers.pg_stat_statements(showtext boolean) RETURNS SETOF public.pg_stat_statements
    LANGUAGE sql IMMUTABLE STRICT SECURITY DEFINER
    AS $$
  SELECT * FROM public.pg_stat_statements(showtext);;
--
-- Name: update_cluster_node_count(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_cluster_node_count() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- 处理 INSERT/UPDATE 操作（NEW 代表新数据）
    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        UPDATE clusters
        SET 
            node_count = (SELECT COUNT(*) FROM nodes WHERE nodes.cluster_id = NEW.cluster_id),
            updated_at = NOW()
        WHERE clusters.id = NEW.cluster_id;;
--
-- Name: create_application_user(text); Type: FUNCTION; Schema: user_management; Owner: postgres
--

CREATE FUNCTION user_management.create_application_user(username text) RETURNS text
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $_$
DECLARE
    pw text;;
--
-- Name: create_application_user_or_change_password(text, text); Type: FUNCTION; Schema: user_management; Owner: postgres
--

CREATE FUNCTION user_management.create_application_user_or_change_password(username text, password text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $_$
BEGIN
    PERFORM 1 FROM pg_roles WHERE rolname = username;;
--
-- Name: create_role(text); Type: FUNCTION; Schema: user_management; Owner: postgres
--

CREATE FUNCTION user_management.create_role(rolename text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $_$
BEGIN
    -- set ADMIN to the admin user, so every member of admin can GRANT these roles to each other
    EXECUTE format($$ CREATE ROLE %I WITH ADMIN admin $$, rolename);;
--
-- Name: create_user(text); Type: FUNCTION; Schema: user_management; Owner: postgres
--

CREATE FUNCTION user_management.create_user(username text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $_$
BEGIN
    EXECUTE format($$ CREATE USER %I IN ROLE zalandos, admin $$, username);;
--
-- Name: drop_role(text); Type: FUNCTION; Schema: user_management; Owner: postgres
--

CREATE FUNCTION user_management.drop_role(username text) RETURNS void
    LANGUAGE sql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $$
SELECT user_management.drop_user(username);;
--
-- Name: drop_user(text); Type: FUNCTION; Schema: user_management; Owner: postgres
--

CREATE FUNCTION user_management.drop_user(username text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $_$
BEGIN
    EXECUTE format($$ DROP ROLE %I $$, username);;
--
-- Name: random_password(integer); Type: FUNCTION; Schema: user_management; Owner: postgres
--

CREATE FUNCTION user_management.random_password(length integer) RETURNS text
    LANGUAGE sql
    SET search_path TO 'pg_catalog'
    AS $$
WITH chars (c) AS (
    SELECT chr(33)
    UNION ALL
    SELECT chr(i) FROM generate_series (35, 38) AS t (i)
    UNION ALL
    SELECT chr(i) FROM generate_series (42, 90) AS t (i)
    UNION ALL
    SELECT chr(i) FROM generate_series (97, 122) AS t (i)
),
bricks (b) AS (
    -- build a pool of chars (the size will be the number of chars above times length)
    -- and shuffle it
    SELECT c FROM chars, generate_series(1, length) ORDER BY random()
)
SELECT substr(string_agg(b, ''), 1, length) FROM bricks;;
--
-- Name: revoke_admin(text); Type: FUNCTION; Schema: user_management; Owner: postgres
--

CREATE FUNCTION user_management.revoke_admin(username text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $_$
BEGIN
    EXECUTE format($$ REVOKE admin FROM %I $$, username);;
--
-- Name: terminate_backend(integer); Type: FUNCTION; Schema: user_management; Owner: postgres
--

CREATE FUNCTION user_management.terminate_backend(pid integer) RETURNS boolean
    LANGUAGE sql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $$
SELECT pg_terminate_backend(pid);;


-- --------------------------------------------------
-- 3. 数据表定义 (字段/约束/索引/注释)
-- --------------------------------------------------

-- ==================================================
-- 表名: app_configurations
-- ==================================================
-- [结构] 创建表
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
    CONSTRAINT app_config_type_chk CHECK (((config_type)::text = ANY (ARRAY[('system'::character varying)::text, ('alert_rule'::character varying)::text, ('notification'::character varying)::text, ('llm'::character varying)::text])))
);;

-- [约束] 主键
--
-- Name: app_configurations app_configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_configurations
    ADD CONSTRAINT app_configurations_pkey PRIMARY KEY (id);;

-- [约束] 其他约束
--
-- Name: app_configurations uk_app_config; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_configurations
    ADD CONSTRAINT uk_app_config UNIQUE (config_type, config_key);;

-- [索引] 索引定义
--
-- Name: idx_app_config_enabled; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_app_config_enabled ON public.app_configurations USING btree (is_enabled);;

-- [注释] 字段说明
--
-- Name: COLUMN app_configurations.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.id IS '主键ID';;
--
-- Name: COLUMN app_configurations.config_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.config_type IS '配置类型(system/alert_rule/notification/llm)';;
--
-- Name: COLUMN app_configurations.config_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.config_key IS '配置键';;
--
-- Name: COLUMN app_configurations.config_value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.config_value IS '配置值(JSONB)';;
--
-- Name: COLUMN app_configurations.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.description IS '配置描述';;
--
-- Name: COLUMN app_configurations.is_enabled; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.is_enabled IS '是否启用';;
--
-- Name: COLUMN app_configurations.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.created_at IS '创建时间';;
--
-- Name: COLUMN app_configurations.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_configurations.updated_at IS '更新时间';;



-- ==================================================
-- 表名: chat_messages
-- ==================================================
-- [结构] 创建表
--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_messages (
    id integer NOT NULL,
    session_id character varying NOT NULL,
    role character varying NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone,
    reasoning text,
    username character varying(64)
);;

-- [约束] 主键
--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);;

-- [索引] 索引定义
--
-- Name: ix_chat_messages_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_messages_id ON public.chat_messages USING btree (id);;

-- [约束] 外键关联
--
-- Name: chat_messages chat_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id);;



-- ==================================================
-- 表名: chat_sessions
-- ==================================================
-- [结构] 创建表
--
-- Name: chat_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_sessions (
    id character varying NOT NULL,
    user_id integer,
    title character varying,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);;

-- [约束] 主键
--
-- Name: chat_sessions chat_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_pkey PRIMARY KEY (id);;

-- [索引] 索引定义
--
-- Name: ix_chat_sessions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_sessions_id ON public.chat_sessions USING btree (id);;
--
-- Name: ix_chat_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_sessions_user_id ON public.chat_sessions USING btree (user_id);;



-- ==================================================
-- 表名: cluster_metrics
-- ==================================================
-- [结构] 创建表
--
-- Name: cluster_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cluster_metrics (
    id integer NOT NULL,
    cluster_id integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    cpu_avg double precision,
    mem_used_avg double precision,
    mem_free_avg double precision
);;

-- [约束] 主键
--
-- Name: cluster_metrics cluster_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cluster_metrics
    ADD CONSTRAINT cluster_metrics_pkey PRIMARY KEY (id);;

-- [索引] 索引定义
--
-- Name: ix_cluster_metrics_cluster_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cluster_metrics_cluster_id ON public.cluster_metrics USING btree (cluster_id);;
--
-- Name: ix_cluster_metrics_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cluster_metrics_timestamp ON public.cluster_metrics USING btree ("timestamp");;



-- ==================================================
-- 表名: clusters
-- ==================================================
-- [结构] 创建表
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
    namenode_ip inet,
    namenode_psw character varying(255),
    rm_ip inet,
    rm_psw character varying(255),
    CONSTRAINT clusters_health_status_chk CHECK (((health_status)::text = ANY (ARRAY[('healthy'::character varying)::text, ('warning'::character varying)::text, ('error'::character varying)::text, ('unknown'::character varying)::text])))
);;

-- [约束] 主键
--
-- Name: clusters clusters_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clusters
    ADD CONSTRAINT clusters_pkey PRIMARY KEY (id);;

-- [约束] 其他约束
--
-- Name: clusters clusters_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clusters
    ADD CONSTRAINT clusters_name_key UNIQUE (name);;
--
-- Name: clusters clusters_uuid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clusters
    ADD CONSTRAINT clusters_uuid_key UNIQUE (uuid);;

-- [注释] 字段说明
--
-- Name: COLUMN clusters.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.id IS '主键ID';;
--
-- Name: COLUMN clusters.uuid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.uuid IS '集群唯一标识(UUID)';;
--
-- Name: COLUMN clusters.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.name IS '集群名称';;
--
-- Name: COLUMN clusters.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.type IS '集群类型';;
--
-- Name: COLUMN clusters.node_count; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.node_count IS '集群节点数量';;
--
-- Name: COLUMN clusters.health_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.health_status IS '集群健康状态(healthy/warning/error/unknown)';;
--
-- Name: COLUMN clusters.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.description IS '集群描述';;
--
-- Name: COLUMN clusters.config_info; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.config_info IS '集群配置信息(JSONB)';;
--
-- Name: COLUMN clusters.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.created_at IS '创建时间';;
--
-- Name: COLUMN clusters.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.clusters.updated_at IS '更新时间';;



-- ==================================================
-- 表名: hadoop_exec_logs
-- ==================================================
-- [结构] 创建表
--
-- Name: hadoop_exec_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hadoop_exec_logs (
    id integer NOT NULL,
    from_user_id integer NOT NULL,
    cluster_name character varying(255) NOT NULL,
    description text,
    start_time timestamp with time zone,
    end_time timestamp with time zone
);;

-- [约束] 主键
--
-- Name: hadoop_exec_logs hadoop_exec_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadoop_exec_logs
    ADD CONSTRAINT hadoop_exec_logs_pkey PRIMARY KEY (id);;



-- ==================================================
-- 表名: hadoop_logs
-- ==================================================
-- [结构] 创建表
--
-- Name: hadoop_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hadoop_logs (
    log_id integer NOT NULL,
    cluster_name character varying(255) NOT NULL,
    node_host character varying(100) NOT NULL,
    title character varying(255),
    info text,
    log_time timestamp with time zone NOT NULL
);;

-- [约束] 主键
--
-- Name: hadoop_logs hadoop_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadoop_logs
    ADD CONSTRAINT hadoop_logs_pkey PRIMARY KEY (log_id);;

-- [索引] 索引定义
--
-- Name: idx_hadoop_logs_cluster_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_hadoop_logs_cluster_name ON public.hadoop_logs USING btree (cluster_name);;



-- ==================================================
-- 表名: node_metrics
-- ==================================================
-- [结构] 创建表
--
-- Name: node_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.node_metrics (
    id integer NOT NULL,
    cluster_id integer,
    node_name character varying(100) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    cpu_usage double precision,
    mem_used double precision,
    mem_free double precision
);;

-- [约束] 主键
--
-- Name: node_metrics node_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.node_metrics
    ADD CONSTRAINT node_metrics_pkey PRIMARY KEY (id);;

-- [索引] 索引定义
--
-- Name: ix_node_metrics_node_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_node_metrics_node_name ON public.node_metrics USING btree (node_name);;
--
-- Name: ix_node_metrics_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_node_metrics_timestamp ON public.node_metrics USING btree ("timestamp");;



-- ==================================================
-- 表名: nodes
-- ==================================================
-- [结构] 创建表
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
    ssh_user character varying(50),
    ssh_password character varying(255),
    CONSTRAINT nodes_cpu_chk CHECK (((cpu_usage IS NULL) OR ((cpu_usage >= (0)::numeric) AND (cpu_usage <= (100)::numeric)))),
    CONSTRAINT nodes_disk_chk CHECK (((disk_usage IS NULL) OR ((disk_usage >= (0)::numeric) AND (disk_usage <= (100)::numeric)))),
    CONSTRAINT nodes_mem_chk CHECK (((memory_usage IS NULL) OR ((memory_usage >= (0)::numeric) AND (memory_usage <= (100)::numeric)))),
    CONSTRAINT nodes_status_chk CHECK (((status)::text = ANY (ARRAY[('healthy'::character varying)::text, ('unhealthy'::character varying)::text, ('warning'::character varying)::text, ('unknown'::character varying)::text])))
);;

-- [约束] 主键
--
-- Name: nodes nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_pkey PRIMARY KEY (id);;

-- [约束] 其他约束
--
-- Name: nodes nodes_uuid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_uuid_key UNIQUE (uuid);;

-- [索引] 索引定义
--
-- Name: idx_nodes_cluster_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nodes_cluster_id ON public.nodes USING btree (cluster_id);;
--
-- Name: idx_nodes_ip_address; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nodes_ip_address ON public.nodes USING btree (ip_address);;
--
-- Name: idx_nodes_last_heartbeat; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nodes_last_heartbeat ON public.nodes USING btree (last_heartbeat);;
--
-- Name: idx_nodes_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nodes_status ON public.nodes USING btree (status);;
--
-- Name: uk_cluster_hostname; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uk_cluster_hostname ON public.nodes USING btree (cluster_id, hostname);;

-- [约束] 外键关联
--
-- Name: nodes nodes_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.clusters(id) ON UPDATE CASCADE ON DELETE CASCADE;;

-- [注释] 字段说明
--
-- Name: COLUMN nodes.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.id IS '主键ID';;
--
-- Name: COLUMN nodes.uuid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.uuid IS '节点唯一标识(UUID)';;
--
-- Name: COLUMN nodes.cluster_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.cluster_id IS '所属集群ID';;
--
-- Name: COLUMN nodes.hostname; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.hostname IS '节点主机名';;
--
-- Name: COLUMN nodes.ip_address; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.ip_address IS '节点IP地址(INET, 兼容IPv4/IPv6)';;
--
-- Name: COLUMN nodes.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.status IS '节点健康状态(healthy/unhealthy/warning/unknown)';;
--
-- Name: COLUMN nodes.cpu_usage; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.cpu_usage IS 'CPU使用率(%)';;
--
-- Name: COLUMN nodes.memory_usage; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.memory_usage IS '内存使用率(%)';;
--
-- Name: COLUMN nodes.disk_usage; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.disk_usage IS '磁盘使用率(%)';;
--
-- Name: COLUMN nodes.last_heartbeat; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.last_heartbeat IS '最后心跳时间';;
--
-- Name: COLUMN nodes.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.created_at IS '创建时间';;
--
-- Name: COLUMN nodes.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.nodes.updated_at IS '更新时间';;



-- ==================================================
-- 表名: permissions
-- ==================================================
-- [结构] 创建表
--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id bigint NOT NULL,
    permission_name character varying(100) NOT NULL,
    permission_key character varying(100) NOT NULL,
    description character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);;

-- [约束] 主键
--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);;

-- [约束] 其他约束
--
-- Name: permissions permissions_permission_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_permission_key_key UNIQUE (permission_key);;

-- [注释] 字段说明
--
-- Name: COLUMN permissions.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.permissions.id IS '主键ID';;
--
-- Name: COLUMN permissions.permission_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.permissions.permission_name IS '权限名称';;
--
-- Name: COLUMN permissions.permission_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.permissions.permission_key IS '权限唯一标识';;
--
-- Name: COLUMN permissions.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.permissions.description IS '权限描述';;
--
-- Name: COLUMN permissions.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.permissions.created_at IS '创建时间';;



-- ==================================================
-- 表名: repair_templates
-- ==================================================
-- [结构] 创建表
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
    CONSTRAINT repair_templates_risk_chk CHECK (((risk_level)::text = ANY (ARRAY[('low'::character varying)::text, ('medium'::character varying)::text, ('high'::character varying)::text])))
);;

-- [约束] 主键
--
-- Name: repair_templates repair_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_templates
    ADD CONSTRAINT repair_templates_pkey PRIMARY KEY (id);;

-- [约束] 其他约束
--
-- Name: repair_templates repair_templates_template_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_templates
    ADD CONSTRAINT repair_templates_template_name_key UNIQUE (template_name);;

-- [索引] 索引定义
--
-- Name: idx_repair_templates_fault_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_repair_templates_fault_type ON public.repair_templates USING btree (fault_type);;

-- [注释] 字段说明
--
-- Name: COLUMN repair_templates.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.id IS '主键ID';;
--
-- Name: COLUMN repair_templates.template_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.template_name IS '模板名称';;
--
-- Name: COLUMN repair_templates.fault_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.fault_type IS '适用故障类型';;
--
-- Name: COLUMN repair_templates.script_content; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.script_content IS '脚本内容';;
--
-- Name: COLUMN repair_templates.risk_level; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.risk_level IS '风险级别(low/medium/high)';;
--
-- Name: COLUMN repair_templates.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.description IS '模板描述';;
--
-- Name: COLUMN repair_templates.parameters; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.parameters IS '模板参数定义(JSONB)';;
--
-- Name: COLUMN repair_templates.created_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.created_by IS '创建人';;
--
-- Name: COLUMN repair_templates.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.created_at IS '创建时间';;
--
-- Name: COLUMN repair_templates.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.repair_templates.updated_at IS '更新时间';;



-- ==================================================
-- 表名: role_permission_mapping
-- ==================================================
-- [结构] 创建表
--
-- Name: role_permission_mapping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permission_mapping (
    role_id bigint NOT NULL,
    permission_id bigint NOT NULL
);;

-- [约束] 主键
--
-- Name: role_permission_mapping role_permission_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permission_mapping
    ADD CONSTRAINT role_permission_mapping_pkey PRIMARY KEY (role_id, permission_id);;

-- [约束] 外键关联
--
-- Name: role_permission_mapping role_permission_mapping_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permission_mapping
    ADD CONSTRAINT role_permission_mapping_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON UPDATE CASCADE ON DELETE CASCADE;;
--
-- Name: role_permission_mapping role_permission_mapping_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permission_mapping
    ADD CONSTRAINT role_permission_mapping_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE;;

-- [注释] 字段说明
--
-- Name: COLUMN role_permission_mapping.role_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.role_permission_mapping.role_id IS '角色ID';;
--
-- Name: COLUMN role_permission_mapping.permission_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.role_permission_mapping.permission_id IS '权限ID';;



-- ==================================================
-- 表名: roles
-- ==================================================
-- [结构] 创建表
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
);;

-- [约束] 主键
--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);;

-- [约束] 其他约束
--
-- Name: roles roles_role_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_role_key_key UNIQUE (role_key);;

-- [注释] 字段说明
--
-- Name: COLUMN roles.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.id IS '主键ID';;
--
-- Name: COLUMN roles.role_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.role_name IS '角色名称';;
--
-- Name: COLUMN roles.role_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.role_key IS '角色唯一标识';;
--
-- Name: COLUMN roles.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.description IS '角色描述';;
--
-- Name: COLUMN roles.is_system_role; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.is_system_role IS '是否为系统内置角色';;
--
-- Name: COLUMN roles.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.created_at IS '创建时间';;
--
-- Name: COLUMN roles.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.updated_at IS '更新时间';;



-- ==================================================
-- 表名: sys_exec_logs
-- ==================================================
-- [结构] 创建表
--
-- Name: sys_exec_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_exec_logs (
    operation_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id integer NOT NULL,
    description text NOT NULL,
    operation_time timestamp with time zone DEFAULT now() NOT NULL
);;

-- [约束] 主键
--
-- Name: sys_exec_logs sys_exec_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_exec_logs
    ADD CONSTRAINT sys_exec_logs_pkey PRIMARY KEY (operation_id);;

-- [约束] 外键关联
--
-- Name: sys_exec_logs fk_sys_exec_logs_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_exec_logs
    ADD CONSTRAINT fk_sys_exec_logs_user_id FOREIGN KEY (user_id) REFERENCES public.users(id);;



-- ==================================================
-- 表名: user_cluster_mapping
-- ==================================================
-- [结构] 创建表
--
-- Name: user_cluster_mapping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_cluster_mapping (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    cluster_id bigint NOT NULL,
    role_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);;

-- [约束] 主键
--
-- Name: user_cluster_mapping user_cluster_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_cluster_mapping
    ADD CONSTRAINT user_cluster_mapping_pkey PRIMARY KEY (id);;

-- [约束] 其他约束
--
-- Name: user_cluster_mapping uk_user_cluster; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_cluster_mapping
    ADD CONSTRAINT uk_user_cluster UNIQUE (user_id, cluster_id);;

-- [约束] 外键关联
--
-- Name: user_cluster_mapping user_cluster_mapping_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_cluster_mapping
    ADD CONSTRAINT user_cluster_mapping_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.clusters(id) ON UPDATE CASCADE ON DELETE CASCADE;;
--
-- Name: user_cluster_mapping user_cluster_mapping_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_cluster_mapping
    ADD CONSTRAINT user_cluster_mapping_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE;;
--
-- Name: user_cluster_mapping user_cluster_mapping_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_cluster_mapping
    ADD CONSTRAINT user_cluster_mapping_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;;

-- [注释] 字段说明
--
-- Name: COLUMN user_cluster_mapping.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_cluster_mapping.id IS '主键ID';;
--
-- Name: COLUMN user_cluster_mapping.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_cluster_mapping.user_id IS '用户ID';;
--
-- Name: COLUMN user_cluster_mapping.cluster_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_cluster_mapping.cluster_id IS '集群ID';;
--
-- Name: COLUMN user_cluster_mapping.role_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_cluster_mapping.role_id IS '角色ID';;
--
-- Name: COLUMN user_cluster_mapping.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_cluster_mapping.created_at IS '创建时间';;



-- ==================================================
-- 表名: user_role_mapping
-- ==================================================
-- [结构] 创建表
--
-- Name: user_role_mapping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_role_mapping (
    user_id bigint NOT NULL,
    role_id bigint NOT NULL
);;

-- [约束] 主键
--
-- Name: user_role_mapping user_role_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT user_role_mapping_pkey PRIMARY KEY (user_id, role_id);;

-- [约束] 外键关联
--
-- Name: user_role_mapping user_role_mapping_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT user_role_mapping_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE;;
--
-- Name: user_role_mapping user_role_mapping_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT user_role_mapping_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;;

-- [注释] 字段说明
--
-- Name: COLUMN user_role_mapping.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_role_mapping.user_id IS '用户ID';;
--
-- Name: COLUMN user_role_mapping.role_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.user_role_mapping.role_id IS '角色ID';;



-- ==================================================
-- 表名: users
-- ==================================================
-- [结构] 创建表
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
);;

-- [约束] 主键
--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);;

-- [约束] 其他约束
--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);;
--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);;

-- [注释] 字段说明
--
-- Name: COLUMN users.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.id IS '主键ID';;
--
-- Name: COLUMN users.username; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.username IS '用户名';;
--
-- Name: COLUMN users.email; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.email IS '邮箱';;
--
-- Name: COLUMN users.password_hash; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.password_hash IS '密码哈希';;
--
-- Name: COLUMN users.full_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.full_name IS '姓名';;
--
-- Name: COLUMN users.is_active; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.is_active IS '是否激活';;
--
-- Name: COLUMN users.last_login; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.last_login IS '最后登录时间';;
--
-- Name: COLUMN users.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.created_at IS '创建时间';;
--
-- Name: COLUMN users.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.updated_at IS '更新时间';;


-- --------------------------------------------------
-- 4. 视图定义
-- --------------------------------------------------
--
-- Name: index_bloat; Type: VIEW; Schema: metric_helpers; Owner: postgres
--

CREATE VIEW metric_helpers.index_bloat AS
 SELECT get_btree_bloat_approx.i_database,
    get_btree_bloat_approx.i_schema_name,
    get_btree_bloat_approx.i_table_name,
    get_btree_bloat_approx.i_index_name,
    get_btree_bloat_approx.i_real_size,
    get_btree_bloat_approx.i_extra_size,
    get_btree_bloat_approx.i_extra_ratio,
    get_btree_bloat_approx.i_fill_factor,
    get_btree_bloat_approx.i_bloat_size,
    get_btree_bloat_approx.i_bloat_ratio,
    get_btree_bloat_approx.i_is_na
   FROM metric_helpers.get_btree_bloat_approx() get_btree_bloat_approx(i_database, i_schema_name, i_table_name, i_index_name, i_real_size, i_extra_size, i_extra_ratio, i_fill_factor, i_bloat_size, i_bloat_ratio, i_is_na);;
--
-- Name: nearly_exhausted_sequences; Type: VIEW; Schema: metric_helpers; Owner: postgres
--

CREATE VIEW metric_helpers.nearly_exhausted_sequences AS
 SELECT get_nearly_exhausted_sequences.schemaname,
    get_nearly_exhausted_sequences.sequencename,
    get_nearly_exhausted_sequences.seq_percent_used
   FROM metric_helpers.get_nearly_exhausted_sequences((0.8)::double precision) get_nearly_exhausted_sequences(schemaname, sequencename, seq_percent_used);;
--
-- Name: pg_stat_statements; Type: VIEW; Schema: metric_helpers; Owner: postgres
--

CREATE VIEW metric_helpers.pg_stat_statements AS
 SELECT pg_stat_statements.userid,
    pg_stat_statements.dbid,
    pg_stat_statements.toplevel,
    pg_stat_statements.queryid,
    pg_stat_statements.query,
    pg_stat_statements.plans,
    pg_stat_statements.total_plan_time,
    pg_stat_statements.min_plan_time,
    pg_stat_statements.max_plan_time,
    pg_stat_statements.mean_plan_time,
    pg_stat_statements.stddev_plan_time,
    pg_stat_statements.calls,
    pg_stat_statements.total_exec_time,
    pg_stat_statements.min_exec_time,
    pg_stat_statements.max_exec_time,
    pg_stat_statements.mean_exec_time,
    pg_stat_statements.stddev_exec_time,
    pg_stat_statements.rows,
    pg_stat_statements.shared_blks_hit,
    pg_stat_statements.shared_blks_read,
    pg_stat_statements.shared_blks_dirtied,
    pg_stat_statements.shared_blks_written,
    pg_stat_statements.local_blks_hit,
    pg_stat_statements.local_blks_read,
    pg_stat_statements.local_blks_dirtied,
    pg_stat_statements.local_blks_written,
    pg_stat_statements.temp_blks_read,
    pg_stat_statements.temp_blks_written,
    pg_stat_statements.blk_read_time,
    pg_stat_statements.blk_write_time,
    pg_stat_statements.wal_records,
    pg_stat_statements.wal_fpi,
    pg_stat_statements.wal_bytes
   FROM metric_helpers.pg_stat_statements(true) pg_stat_statements(userid, dbid, toplevel, queryid, query, plans, total_plan_time, min_plan_time, max_plan_time, mean_plan_time, stddev_plan_time, calls, total_exec_time, min_exec_time, max_exec_time, mean_exec_time, stddev_exec_time, rows, shared_blks_hit, shared_blks_read, shared_blks_dirtied, shared_blks_written, local_blks_hit, local_blks_read, local_blks_dirtied, local_blks_written, temp_blks_read, temp_blks_written, blk_read_time, blk_write_time, wal_records, wal_fpi, wal_bytes);;
--
-- Name: table_bloat; Type: VIEW; Schema: metric_helpers; Owner: postgres
--

CREATE VIEW metric_helpers.table_bloat AS
 SELECT get_table_bloat_approx.t_database,
    get_table_bloat_approx.t_schema_name,
    get_table_bloat_approx.t_table_name,
    get_table_bloat_approx.t_real_size,
    get_table_bloat_approx.t_extra_size,
    get_table_bloat_approx.t_extra_ratio,
    get_table_bloat_approx.t_fill_factor,
    get_table_bloat_approx.t_bloat_size,
    get_table_bloat_approx.t_bloat_ratio,
    get_table_bloat_approx.t_is_na
   FROM metric_helpers.get_table_bloat_approx() get_table_bloat_approx(t_database, t_schema_name, t_table_name, t_real_size, t_extra_size, t_extra_ratio, t_fill_factor, t_bloat_size, t_bloat_ratio, t_is_na);;


-- --------------------------------------------------
-- 5. 其他逻辑 (触发器等)
-- --------------------------------------------------
--
-- Name: nodes trigger_sync_node_count; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_sync_node_count AFTER INSERT OR DELETE OR UPDATE ON public.nodes FOR EACH ROW EXECUTE FUNCTION public.update_cluster_node_count();;
ALTER SCHEMA metric_helpers OWNER TO postgres;;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;;
ALTER SCHEMA user_management OWNER TO postgres;;
$$;;
ALTER FUNCTION metric_helpers.get_btree_bloat_approx(OUT i_database name, OUT i_schema_name name, OUT i_table_name name, OUT i_index_name name, OUT i_real_size numeric, OUT i_extra_size numeric, OUT i_extra_ratio double precision, OUT i_fill_factor integer, OUT i_bloat_size double precision, OUT i_bloat_ratio double precision, OUT i_is_na boolean) OWNER TO postgres;;
$$;;
ALTER FUNCTION metric_helpers.get_nearly_exhausted_sequences(threshold double precision, OUT schemaname name, OUT sequencename name, OUT seq_percent_used numeric) OWNER TO postgres;;
$$;;
ALTER FUNCTION metric_helpers.get_table_bloat_approx(OUT t_database name, OUT t_schema_name name, OUT t_table_name name, OUT t_real_size numeric, OUT t_extra_size double precision, OUT t_extra_ratio double precision, OUT t_fill_factor integer, OUT t_bloat_size double precision, OUT t_bloat_ratio double precision, OUT t_is_na boolean) OWNER TO postgres;;
$$;;
ALTER FUNCTION metric_helpers.pg_stat_statements(showtext boolean) OWNER TO postgres;;
END IF;;
END IF;;
RETURN NULL;  -- AFTER触发器返回值无意义，固定返回NULL
END;;
$$;;
ALTER FUNCTION public.update_cluster_node_count() OWNER TO postgres;;
BEGIN
    SELECT user_management.random_password(20) INTO pw;;
EXECUTE format($$ CREATE USER %I WITH PASSWORD %L $$, username, pw);;
RETURN pw;;
END
$_$;;
ALTER FUNCTION user_management.create_application_user(username text) OWNER TO postgres;;
IF FOUND
    THEN
        EXECUTE format($$ ALTER ROLE %I WITH PASSWORD %L $$, username, password);;
ELSE
        EXECUTE format($$ CREATE USER %I WITH PASSWORD %L $$, username, password);;
END IF;;
END
$_$;;
ALTER FUNCTION user_management.create_application_user_or_change_password(username text, password text) OWNER TO postgres;;
END;;
$_$;;
ALTER FUNCTION user_management.create_role(rolename text) OWNER TO postgres;;
END;;
$_$;;
ALTER FUNCTION user_management.create_user(username text) OWNER TO postgres;;
$$;;
ALTER FUNCTION user_management.drop_role(username text) OWNER TO postgres;;
END
$_$;;
ALTER FUNCTION user_management.drop_user(username text) OWNER TO postgres;;
$$;;
ALTER FUNCTION user_management.random_password(length integer) OWNER TO postgres;;
END
$_$;;
ALTER FUNCTION user_management.revoke_admin(username text) OWNER TO postgres;;
$$;;
ALTER FUNCTION user_management.terminate_backend(pid integer) OWNER TO postgres;;
ALTER TABLE metric_helpers.index_bloat OWNER TO postgres;;
ALTER TABLE metric_helpers.nearly_exhausted_sequences OWNER TO postgres;;
ALTER TABLE metric_helpers.pg_stat_statements OWNER TO postgres;;
ALTER TABLE metric_helpers.table_bloat OWNER TO postgres;;
ALTER TABLE public.app_configurations OWNER TO postgres;;
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
);;
ALTER TABLE public.chat_messages OWNER TO postgres;;
--
-- Name: chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;;
ALTER TABLE public.chat_messages_id_seq OWNER TO postgres;;
--
-- Name: chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_messages_id_seq OWNED BY public.chat_messages.id;;
ALTER TABLE public.chat_sessions OWNER TO postgres;;
ALTER TABLE public.cluster_metrics OWNER TO postgres;;
--
-- Name: cluster_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cluster_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;;
ALTER TABLE public.cluster_metrics_id_seq OWNER TO postgres;;
--
-- Name: cluster_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cluster_metrics_id_seq OWNED BY public.cluster_metrics.id;;
ALTER TABLE public.clusters OWNER TO postgres;;
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
);;
ALTER TABLE public.hadoop_exec_logs OWNER TO postgres;;
--
-- Name: hadoop_exec_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hadoop_exec_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;;
ALTER TABLE public.hadoop_exec_logs_id_seq OWNER TO postgres;;
--
-- Name: hadoop_exec_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hadoop_exec_logs_id_seq OWNED BY public.hadoop_exec_logs.id;;
ALTER TABLE public.hadoop_logs OWNER TO postgres;;
--
-- Name: hadoop_logs_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hadoop_logs_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;;
ALTER TABLE public.hadoop_logs_log_id_seq OWNER TO postgres;;
--
-- Name: hadoop_logs_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hadoop_logs_log_id_seq OWNED BY public.hadoop_logs.log_id;;
ALTER TABLE public.node_metrics OWNER TO postgres;;
--
-- Name: node_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.node_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;;
ALTER TABLE public.node_metrics_id_seq OWNER TO postgres;;
--
-- Name: node_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.node_metrics_id_seq OWNED BY public.node_metrics.id;;
ALTER TABLE public.nodes OWNER TO postgres;;
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
);;
ALTER TABLE public.permissions OWNER TO postgres;;
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
);;
ALTER TABLE public.repair_templates OWNER TO postgres;;
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
);;
ALTER TABLE public.role_permission_mapping OWNER TO postgres;;
ALTER TABLE public.roles OWNER TO postgres;;
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
);;
ALTER TABLE public.sys_exec_logs OWNER TO postgres;;
ALTER TABLE public.user_cluster_mapping OWNER TO postgres;;
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
);;
ALTER TABLE public.user_role_mapping OWNER TO postgres;;
ALTER TABLE public.users OWNER TO postgres;;
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
);;
--
-- Name: SCHEMA metric_helpers; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA metric_helpers TO admin;;
GRANT USAGE ON SCHEMA metric_helpers TO robot_zmon;;
--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;;
GRANT ALL ON SCHEMA public TO PUBLIC;;
GRANT USAGE ON SCHEMA public TO echo;;
--
-- Name: SCHEMA user_management; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA user_management TO admin;;
--
-- Name: FUNCTION get_btree_bloat_approx(OUT i_database name, OUT i_schema_name name, OUT i_table_name name, OUT i_index_name name, OUT i_real_size numeric, OUT i_extra_size numeric, OUT i_extra_ratio double precision, OUT i_fill_factor integer, OUT i_bloat_size double precision, OUT i_bloat_ratio double precision, OUT i_is_na boolean); Type: ACL; Schema: metric_helpers; Owner: postgres
--

REVOKE ALL ON FUNCTION metric_helpers.get_btree_bloat_approx(OUT i_database name, OUT i_schema_name name, OUT i_table_name name, OUT i_index_name name, OUT i_real_size numeric, OUT i_extra_size numeric, OUT i_extra_ratio double precision, OUT i_fill_factor integer, OUT i_bloat_size double precision, OUT i_bloat_ratio double precision, OUT i_is_na boolean) FROM PUBLIC;;
GRANT ALL ON FUNCTION metric_helpers.get_btree_bloat_approx(OUT i_database name, OUT i_schema_name name, OUT i_table_name name, OUT i_index_name name, OUT i_real_size numeric, OUT i_extra_size numeric, OUT i_extra_ratio double precision, OUT i_fill_factor integer, OUT i_bloat_size double precision, OUT i_bloat_ratio double precision, OUT i_is_na boolean) TO admin;;
GRANT ALL ON FUNCTION metric_helpers.get_btree_bloat_approx(OUT i_database name, OUT i_schema_name name, OUT i_table_name name, OUT i_index_name name, OUT i_real_size numeric, OUT i_extra_size numeric, OUT i_extra_ratio double precision, OUT i_fill_factor integer, OUT i_bloat_size double precision, OUT i_bloat_ratio double precision, OUT i_is_na boolean) TO robot_zmon;;
--
-- Name: FUNCTION get_nearly_exhausted_sequences(threshold double precision, OUT schemaname name, OUT sequencename name, OUT seq_percent_used numeric); Type: ACL; Schema: metric_helpers; Owner: postgres
--

REVOKE ALL ON FUNCTION metric_helpers.get_nearly_exhausted_sequences(threshold double precision, OUT schemaname name, OUT sequencename name, OUT seq_percent_used numeric) FROM PUBLIC;;
GRANT ALL ON FUNCTION metric_helpers.get_nearly_exhausted_sequences(threshold double precision, OUT schemaname name, OUT sequencename name, OUT seq_percent_used numeric) TO admin;;
GRANT ALL ON FUNCTION metric_helpers.get_nearly_exhausted_sequences(threshold double precision, OUT schemaname name, OUT sequencename name, OUT seq_percent_used numeric) TO robot_zmon;;
--
-- Name: FUNCTION get_table_bloat_approx(OUT t_database name, OUT t_schema_name name, OUT t_table_name name, OUT t_real_size numeric, OUT t_extra_size double precision, OUT t_extra_ratio double precision, OUT t_fill_factor integer, OUT t_bloat_size double precision, OUT t_bloat_ratio double precision, OUT t_is_na boolean); Type: ACL; Schema: metric_helpers; Owner: postgres
--

REVOKE ALL ON FUNCTION metric_helpers.get_table_bloat_approx(OUT t_database name, OUT t_schema_name name, OUT t_table_name name, OUT t_real_size numeric, OUT t_extra_size double precision, OUT t_extra_ratio double precision, OUT t_fill_factor integer, OUT t_bloat_size double precision, OUT t_bloat_ratio double precision, OUT t_is_na boolean) FROM PUBLIC;;
GRANT ALL ON FUNCTION metric_helpers.get_table_bloat_approx(OUT t_database name, OUT t_schema_name name, OUT t_table_name name, OUT t_real_size numeric, OUT t_extra_size double precision, OUT t_extra_ratio double precision, OUT t_fill_factor integer, OUT t_bloat_size double precision, OUT t_bloat_ratio double precision, OUT t_is_na boolean) TO admin;;
GRANT ALL ON FUNCTION metric_helpers.get_table_bloat_approx(OUT t_database name, OUT t_schema_name name, OUT t_table_name name, OUT t_real_size numeric, OUT t_extra_size double precision, OUT t_extra_ratio double precision, OUT t_fill_factor integer, OUT t_bloat_size double precision, OUT t_bloat_ratio double precision, OUT t_is_na boolean) TO robot_zmon;;
--
-- Name: TABLE pg_stat_statements; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.pg_stat_statements TO echo;;
--
-- Name: FUNCTION pg_stat_statements(showtext boolean); Type: ACL; Schema: metric_helpers; Owner: postgres
--

REVOKE ALL ON FUNCTION metric_helpers.pg_stat_statements(showtext boolean) FROM PUBLIC;;
GRANT ALL ON FUNCTION metric_helpers.pg_stat_statements(showtext boolean) TO admin;;
GRANT ALL ON FUNCTION metric_helpers.pg_stat_statements(showtext boolean) TO robot_zmon;;
--
-- Name: FUNCTION pg_switch_wal(); Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT ALL ON FUNCTION pg_catalog.pg_switch_wal() TO admin;;
--
-- Name: FUNCTION pg_stat_statements_reset(userid oid, dbid oid, queryid bigint); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pg_stat_statements_reset(userid oid, dbid oid, queryid bigint) TO admin;;
--
-- Name: FUNCTION set_user(text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.set_user(text) TO admin;;
--
-- Name: FUNCTION create_application_user(username text); Type: ACL; Schema: user_management; Owner: postgres
--

REVOKE ALL ON FUNCTION user_management.create_application_user(username text) FROM PUBLIC;;
GRANT ALL ON FUNCTION user_management.create_application_user(username text) TO admin;;
--
-- Name: FUNCTION create_application_user_or_change_password(username text, password text); Type: ACL; Schema: user_management; Owner: postgres
--

REVOKE ALL ON FUNCTION user_management.create_application_user_or_change_password(username text, password text) FROM PUBLIC;;
GRANT ALL ON FUNCTION user_management.create_application_user_or_change_password(username text, password text) TO admin;;
--
-- Name: FUNCTION create_role(rolename text); Type: ACL; Schema: user_management; Owner: postgres
--

REVOKE ALL ON FUNCTION user_management.create_role(rolename text) FROM PUBLIC;;
GRANT ALL ON FUNCTION user_management.create_role(rolename text) TO admin;;
--
-- Name: FUNCTION create_user(username text); Type: ACL; Schema: user_management; Owner: postgres
--

REVOKE ALL ON FUNCTION user_management.create_user(username text) FROM PUBLIC;;
GRANT ALL ON FUNCTION user_management.create_user(username text) TO admin;;
--
-- Name: FUNCTION drop_role(username text); Type: ACL; Schema: user_management; Owner: postgres
--

REVOKE ALL ON FUNCTION user_management.drop_role(username text) FROM PUBLIC;;
GRANT ALL ON FUNCTION user_management.drop_role(username text) TO admin;;
--
-- Name: FUNCTION drop_user(username text); Type: ACL; Schema: user_management; Owner: postgres
--

REVOKE ALL ON FUNCTION user_management.drop_user(username text) FROM PUBLIC;;
GRANT ALL ON FUNCTION user_management.drop_user(username text) TO admin;;
--
-- Name: FUNCTION revoke_admin(username text); Type: ACL; Schema: user_management; Owner: postgres
--

REVOKE ALL ON FUNCTION user_management.revoke_admin(username text) FROM PUBLIC;;
GRANT ALL ON FUNCTION user_management.revoke_admin(username text) TO admin;;
--
-- Name: FUNCTION terminate_backend(pid integer); Type: ACL; Schema: user_management; Owner: postgres
--

REVOKE ALL ON FUNCTION user_management.terminate_backend(pid integer) FROM PUBLIC;;
GRANT ALL ON FUNCTION user_management.terminate_backend(pid integer) TO admin;;
--
-- Name: TABLE index_bloat; Type: ACL; Schema: metric_helpers; Owner: postgres
--

GRANT SELECT ON TABLE metric_helpers.index_bloat TO admin;;
GRANT SELECT ON TABLE metric_helpers.index_bloat TO robot_zmon;;
--
-- Name: TABLE nearly_exhausted_sequences; Type: ACL; Schema: metric_helpers; Owner: postgres
--

GRANT SELECT ON TABLE metric_helpers.nearly_exhausted_sequences TO admin;;
GRANT SELECT ON TABLE metric_helpers.nearly_exhausted_sequences TO robot_zmon;;
--
-- Name: TABLE pg_stat_statements; Type: ACL; Schema: metric_helpers; Owner: postgres
--

GRANT SELECT ON TABLE metric_helpers.pg_stat_statements TO admin;;
GRANT SELECT ON TABLE metric_helpers.pg_stat_statements TO robot_zmon;;
--
-- Name: TABLE table_bloat; Type: ACL; Schema: metric_helpers; Owner: postgres
--

GRANT SELECT ON TABLE metric_helpers.table_bloat TO admin;;
GRANT SELECT ON TABLE metric_helpers.table_bloat TO robot_zmon;;
--
-- Name: TABLE pg_stat_activity; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_activity TO admin;;
--
-- Name: TABLE app_configurations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.app_configurations TO echo;;
--
-- Name: SEQUENCE app_configurations_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.app_configurations_id_seq TO echo;;
--
-- Name: TABLE chat_messages; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.chat_messages TO echo;;
--
-- Name: SEQUENCE chat_messages_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.chat_messages_id_seq TO echo;;
--
-- Name: TABLE chat_sessions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.chat_sessions TO echo;;
--
-- Name: TABLE cluster_metrics; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.cluster_metrics TO echo;;
--
-- Name: SEQUENCE cluster_metrics_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.cluster_metrics_id_seq TO echo;;
--
-- Name: TABLE clusters; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.clusters TO echo;;
--
-- Name: SEQUENCE clusters_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.clusters_id_seq TO echo;;
--
-- Name: TABLE hadoop_exec_logs; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.hadoop_exec_logs TO echo;;
--
-- Name: SEQUENCE hadoop_exec_logs_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.hadoop_exec_logs_id_seq TO echo;;
--
-- Name: TABLE hadoop_logs; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.hadoop_logs TO echo;;
--
-- Name: SEQUENCE hadoop_logs_log_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.hadoop_logs_log_id_seq TO echo;;
--
-- Name: TABLE node_metrics; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.node_metrics TO echo;;
--
-- Name: SEQUENCE node_metrics_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.node_metrics_id_seq TO echo;;
--
-- Name: TABLE nodes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.nodes TO echo;;
--
-- Name: SEQUENCE nodes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.nodes_id_seq TO echo;;
--
-- Name: TABLE permissions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.permissions TO echo;;
--
-- Name: SEQUENCE permissions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.permissions_id_seq TO echo;;
--
-- Name: TABLE pg_stat_kcache_detail; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.pg_stat_kcache_detail TO echo;;
--
-- Name: TABLE pg_stat_kcache; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.pg_stat_kcache TO echo;;
--
-- Name: TABLE pg_stat_statements_info; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.pg_stat_statements_info TO echo;;
--
-- Name: TABLE repair_templates; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.repair_templates TO echo;;
--
-- Name: SEQUENCE repair_templates_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.repair_templates_id_seq TO echo;;
--
-- Name: TABLE role_permission_mapping; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.role_permission_mapping TO echo;;
--
-- Name: TABLE roles; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.roles TO echo;;
--
-- Name: SEQUENCE roles_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.roles_id_seq TO echo;;
--
-- Name: TABLE sys_exec_logs; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sys_exec_logs TO echo;;
--
-- Name: TABLE user_cluster_mapping; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.user_cluster_mapping TO echo;;
--
-- Name: SEQUENCE user_cluster_mapping_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.user_cluster_mapping_id_seq TO echo;;
--
-- Name: TABLE user_role_mapping; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.user_role_mapping TO echo;;
--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.users TO echo;;
--
-- Name: SEQUENCE users_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.users_id_seq TO echo;;
--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES  TO echo;;
--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES  TO echo;;
--
-- PostgreSQL database dump complete
--

\unrestrict SXrgAm7tYeypjSdFNjkiY8IUbxx0EaiSgRlWAZQIjV3klsYOp84NcEuzavflAeq;;