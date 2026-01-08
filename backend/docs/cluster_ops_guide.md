# Hadoop 集群启动与停止接口前端联调指南

本文档提供了 Hadoop 集群启动与停止相关 API 的详细说明，用于指导前端开发人员进行接口对接。

## 1. 接口基本信息

| 功能 | 请求方法 | 接口路径 | 权限要求 |
| :--- | :--- | :--- | :--- |
| **启动集群** | `POST` | `/api/v1/ops/clusters/{cluster_uuid}/start` | `cluster:start` |
| **停止集群** | `POST` | `/api/v1/ops/clusters/{cluster_uuid}/stop` | `cluster:stop` |

- **Base URL**: `http://<server-ip>:<port>`
- **Content-Type**: `application/json`
- **认证方式**: 需要在 Header 中携带有效 JWT Token：`Authorization: Bearer <your_token>`

## 2. 请求参数 (Path Parameters)

| 参数名 | 类型 | 必选 | 说明 |
| :--- | :--- | :--- | :--- |
| `cluster_uuid` | `string` | 是 | 集群的唯一标识符（UUID），可从 `/api/v1/clusters` 接口获取。 |

## 3. 响应结构

### 3.1 成功响应 (200 OK)

接口执行时间较长（涉及远程 SSH 指令），建议前端超时时间设置为 **60s**。

```json
{
  "status": "success",
  "logs": [
    "NameNode (192.168.1.10) start: Starting namenodes on [localhost]\nlocalhost: starting namenode...",
    "ResourceManager (192.168.1.11) start: Starting resourcemanager..."
  ]
}
```

**字段说明：**
- `status`: 固定为 `"success"`。
- `logs`: 字符串数组，包含各关键组件（NameNode, ResourceManager）执行脚本后的标准输出与错误信息。

### 3.2 错误响应

- **401 Unauthorized**: 未提供 Token 或 Token 已失效。
- **403 Forbidden**: 权限不足（仅 `admin` 或 `ops` 角色可操作）。
- **404 Not Found**: 集群 UUID 不存在。
- **400 Bad Request**: 请求参数错误。
  - `{"detail": "invalid_uuid_format"}`: 传入的 UUID 格式不正确（例如前端误传了 `[object Object]`）。
- **500 Internal Server Error**: 后端连接 SSH 超时或内部逻辑错误。

## 4. 前端联调建议

1. **Loading 状态**: 由于是长耗时操作，UI 必须提供明确的加载提示，并禁用操作按钮以防重发。
2. **日志展示**: 建议将返回的 `logs` 数组内容渲染在侧边栏或弹窗的日志终端组件中。
3. **超时处理**: 请务必在 Axios 或 Fetch 配置中显式设置 `timeout: 60000`。
4. **状态刷新**: 操作成功后，建议前端重新触发一次集群状态列表查询，以获取最新的 `health_status`。

## 5. 代码参考 (JavaScript/Axios)

```javascript
import axios from 'axios';

const clusterApi = {
  async controlCluster(uuid, action) {
    // action: 'start' 或 'stop'
    const response = await axios.post(`/api/v1/ops/clusters/${uuid}/${action}`, {}, {
      timeout: 60000
    });
    return response.data;
  }
};
```
