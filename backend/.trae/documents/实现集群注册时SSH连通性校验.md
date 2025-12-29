## 需求摘要
- 在注册集群时，逐一验证每个节点的SSH连通性；全部可连通则生成集群UUID并写入数据库；若任一不可连通则返回注册失败。

## 改动点
1. 修改集群注册接口实现
- 文件：app/routers/clusters.py 的 create_cluster（[clusters.py](file:///c:/Users/30326/Desktop/git/backend/app/routers/clusters.py#L75-L161)）
- 引入检查方法：from app.services.ssh_probe import check_ssh_connectivity
- 在参数校验通过后、数据库写入前，新增“SSH连通性预检查”循环：
  - 遍历 req.nodes，取 ip_address、ssh_user、ssh_password
  - 调用 check_ssh_connectivity(ip, user, pwd)
  - 若返回 (False, err)，收集错误项：field=nodes[i].ssh、message="注册失败：SSH不可连接"、step="connect"、detail=err、hostname/ip
  - 若存在错误项：返回 400；不进行任何数据库写入
  - 全部通过后再生成 new_uuid 并写入 Cluster 与 Node 记录，最后提交
- 事务性：预检查完成后才执行 db.add/commit；失败时不修改数据库

2. 保持现有参数校验与权限逻辑
- 仍校验 type/health_status/node_count 等字段
- 继续仅允许 admin/ops 进行注册

## 接口行为
- 成功：
  - 状态码 200
  - 响应：{"status":"success","message":"集群注册成功","uuid":"<uuid>"}
- 失败（SSH不可连通）：
  - 状态码 400
  - 响应：{"detail":{"errors":[{field, message, step, detail, hostname, ip}, ...]}}
  - errors 数量等于不可连通的节点数

## 错误格式
- 单个错误示例：
  - field: "nodes[3].ssh"
  - message: "注册失败：SSH不可连接"
  - step: "connect"
  - detail: "Connection timed out"（或具体异常信息）
  - hostname: "hadoop105"
  - ip: "192.168.10.105"

## 测试用例
- 文件新增：tests/test_cluster_registration_ssh.py
- 用例：
  1) 所有节点连通 → 期望 200、返回 success 与 uuid
  2) 所有节点不连通 → 期望 400、errors=5、每项包含 "SSH不可连接"
  3) 部分节点不连通 → 期望 400、errors=失败节点数量、校验字段与信息
- 通过 monkeypatch 将 app.services.ssh_probe.check_ssh_connectivity 模拟为成功/失败，避免真实SSH连接
- 使用请求体字段 ip_address、ssh_user、ssh_password 与现有 Pydantic 模型对齐

## 验证方式
- 运行测试文件确保所有场景覆盖通过
- 手动调用接口（POST /api/v1/clusters）验证成功与失败返回格式

## 兼容与注意
- node_count 与 nodes 列表长度不一致时：保持现有校验；可选校正为 len(nodes)
- 不更改既有错误返回结构（置于 detail.errors），与当前代码风格一致
- 如需并发提升，可在后续采用 asyncio.gather 并发检查；本次先按顺序实现，保证清晰与稳定

## 相关代码参考
- 集群路由入口与前缀：app/main.py（[main.py](file:///c:/Users/30326/Desktop/git/backend/app/main.py#L1-L28)）
- SSH探测服务：app/services/ssh_probe.py（[ssh_probe.py](file:///c:/Users/30326/Desktop/git/backend/app/services/ssh_probe.py)）
- 集群与节点模型：app/models/clusters.py、app/models/nodes.py（[clusters.py](file:///c:/Users/30326/Desktop/git/backend/app/models/clusters.py)；[nodes.py](file:///c:/Users/30326/Desktop/git/backend/app/models/nodes.py)）
