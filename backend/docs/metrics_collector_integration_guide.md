# Metrics 采集器前端联调指南

## 1. 概述
本文档旨在指导前端开发人员如何调用新增的 Metrics 采集器接口，实现对集群节点 CPU、内存等指标的实时持续采集。该功能通过后台线程运行，每隔固定周期（默认 5 秒）自动更新数据库中的节点状态。

## 2. 接口说明

所有接口均需在 Header 中携带有效的 JWT Token 进行认证。

### 2.1 启动集群采集
**接口地址**: `POST /api/v1/metrics/collectors/start-by-cluster/{cluster_uuid}`

**功能描述**: 启动指定集群下所有节点的后台采集线程。如果采集已在运行，此操作将重启采集并应用新的 `interval`。

**Query 参数**:
- `interval` (int, 可选): 采集周期，单位为秒。默认为 `5`。

**请求示例**:
`POST /api/v1/metrics/collectors/start-by-cluster/550e8400-e29b-41d4-a716-446655440000?interval=10`

**响应示例**:
```json
{
  "ok": true,
  "message": "Metrics collection started for cluster 550e8400-e29b-41d4-a716-446655440000 with interval 10s"
}
```

---

### 2.2 获取采集器状态
**接口地址**: `GET /api/v1/metrics/collectors/status`

**功能描述**: 查询当前后台采集器的运行状态，包括活跃的采集线程数、周期以及最近的错误信息。

**Query 参数**:
- `cluster` (string, 可选): 指定集群 UUID 过滤状态。

**请求示例**:
`GET /api/v1/metrics/collectors/status?cluster=550e8400-e29b-41d4-a716-446655440000`

**响应示例**:
```json
{
  "is_running": true,
  "active_collectors_count": 3,
  "interval": 5,
  "collectors": {
    "node-01": "running",
    "node-02": "running"
  },
  "errors": {
    "node-03": "SSH Timeout"
  }
}
```

---

### 2.3 停止集群采集
**接口地址**: `POST /api/v1/metrics/collectors/stop-by-cluster/{cluster_uuid}`

**功能描述**: 停止指定集群下所有节点的后台采集线程。

**请求示例**:
`POST /api/v1/metrics/collectors/stop-by-cluster/550e8400-e29b-41d4-a716-446655440000`

**响应示例**:
```json
{
  "ok": true,
  "message": "Metrics collection stopping for cluster 550e8400-e29b-41d4-a716-446655440000"
}
```

## 3. 前端集成逻辑建议

### 3.1 页面加载时同步状态
当用户进入“集群监控”或“节点列表”页面时，应先调用 `GET /api/v1/metrics/collectors/status` 接口。
- 如果 `is_running` 为 `false`，界面可以显示“启动监控”按钮。
- 如果为 `true`，界面显示“监控中”状态，并可以根据 `interval` 开启前端定时刷新（调用原有的节点数据接口获取最新值）。

### 3.2 启动监控
点击“启动监控”按钮后，调用 `start-by-cluster` 接口。成功后，前端应每隔一段时间（建议大于等于 `interval`）重新获取节点列表数据，以展示最新的 CPU 和内存使用率。

### 3.3 错误处理
如果在状态接口中发现 `errors` 字段有内容，前端应在对应的节点行或监控卡片上显示错误图标及详情（如 SSH 连接失败等）。

## 4. 注意事项
1. **权限控制**: 只有拥有该集群访问权限的用户才能操作其采集器。
2. **性能影响**: 采集器运行在后台线程，过多频繁的 SSH 轮询可能对目标节点产生轻微负载，建议 `interval` 不要小于 `2` 秒。
3. **数据一致性**: 采集器更新的是 `nodes` 表。前端展示数据时，请调用 `GET /api/v1/nodes` 相关接口获取最新字段。

---
**版本**: v1.0  
**最后更新**: 2026-01-07
