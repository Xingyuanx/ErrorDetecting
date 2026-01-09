# 邹佳轩第12周周计划

## 目标
- 在不同主机之间实现 PostgreSQL 的数据共享与访问，使测试与开发环境可在跨局域网条件下正常协作。

## 范围
- 单库远程访问与权限控制（基础共享）
- 逻辑共享：使用 `postgres_fdw` 建立跨主机只读/读写访问
- 数据同步：逻辑复制（Publisher/Subscriber）在选定表进行增量同步

## 交付物
- 主机 A/B 的 PostgreSQL 安装与基础网络访问配置说明
- `pg_hba.conf` 与 `postgresql.conf` 配置文件变更清单
- FDW 访问示例（创建扩展、Server、User Mapping、Foreign Table）
- 逻辑复制示例（发布端/订阅端SQL与验证步骤）
- 风险与回滚预案（含权限、网络与数据一致性）

## 任务拆解
- 环境与网络
  - 在主机 A/B 安装并启动 PostgreSQL（版本统一，例如 15）
  - 配置 `postgresql.conf`：`listen_addresses='*'`，设置合理 `max_connections`
  - 配置 `pg_hba.conf`：允许来自对端主机的 `host` 连接（限制 IP/网段、使用 `md5`）
  - 防火墙与路由：开放 `5432` 端口，仅允许指定来源 IP 访问

- 远程访问与权限
  - 在主机 A 创建用于远程访问的角色与数据库：`CREATE ROLE remote_user LOGIN ENCRYPTED PASSWORD '***';`
  - 赋予最小权限策略（只读或指定模式/表的读写）
  - 使用 `psql` 或客户端从主机 B 验证连接与基本查询

- FDW 共享（主机 B 访问主机 A 数据）
  - 安装/启用扩展：`CREATE EXTENSION postgres_fdw;`
  - 创建 Server：`CREATE SERVER host_a_srv FOREIGN DATA WRAPPER postgres_fdw OPTIONS (host 'A_IP', dbname 'db', port '5432');`
  - 创建 User Mapping：`CREATE USER MAPPING FOR current_user SERVER host_a_srv OPTIONS (user 'remote_user', password '***');`
  - 导入或手动创建外部表：`IMPORT FOREIGN SCHEMA public FROM SERVER host_a_srv INTO foreign_public;`
  - 验证：在主机 B 查询外部表，评估读写能力与性能

- 逻辑复制（选定表增量同步）
  - 发布端（主机 A）：`CREATE PUBLICATION pub_demo FOR TABLE public.t_demo;`
  - 订阅端（主机 B）：`CREATE SUBSCRIPTION sub_demo CONNECTION 'host=A_IP dbname=db user=remote_user password=***' PUBLICATION pub_demo;`
  - 验证：在主机 A 向 `t_demo` 插入数据，确认主机 B 自动同步

- 文档与验收
  - 输出配置变更清单与安全策略说明（包含 IP 白名单与角色权限）
  - 提供操作脚本与回滚步骤（撤销订阅/发布、删除 FDW 对象）
  - 验收：
    - 跨主机远程连接稳定，权限符合最小化原则
    - FDW 访问正常（至少 1 个模式被共享），逻辑复制在目标表生效

## 时间安排（预估）
- D1：环境准备与网络打通（安装、配置、端口放通）
- D2：远程访问与权限配置验证；完成 FDW 读写演示
- D3：搭建逻辑复制与同步验证；补充安全与回滚方案
- D4：完善文档与脚本；交付验收

## 风险与应对
- 网络不通或端口受限：与网络管理员同步白名单与路由
- 权限过宽：采用最小权限、限制模式/表、分离读写账户
- 复制冲突或不一致：仅对单向写入表启用逻辑复制，必要时加行级约束
- 密码与凭据泄露：使用环境变量或受控配置文件，定期轮换密码

## 成功标准
- 主机 B 能稳定访问主机 A 的 PostgreSQL 数据（FDW 与直接连接均验证）
- 至少 1 张目标表实现逻辑复制的增量同步
- 文档完整可复现，包含安全与回滚说明

