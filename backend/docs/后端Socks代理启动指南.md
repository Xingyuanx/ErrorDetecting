# 后端 Socks 代理启动指南

本文档说明如何在“无 TUN / 无 systemd”的环境中，通过 Tailscale userspace networking + 本地 SOCKS5，让后端在注册集群时能正常用 SSH 连接到各节点。

适用场景：

- `ls -l /dev/net/tun` 提示不存在
- `ssh hadoop@100.x.x.x` 出现 `Connection closed by UNKNOWN port 65535` 或 TCP 22 超时
- 后端集群注册返回 `注册失败：SSH不可连接 (timed out)`

## 1. 启动 tailscaled（userspace + SOCKS5）

以 root 权限后台启动，并在本机开一个 SOCKS5 代理端口 `127.0.0.1:1080`：

```bash
sudo nohup /usr/sbin/tailscaled \
  --tun=userspace-networking \
  --socket=/var/run/tailscale/tailscaled.sock \
  --state=/var/lib/tailscale/tailscaled.state \
  --socks5-server=127.0.0.1:1080 \
  >/tmp/tailscaled.log 2>&1 &
```

检查是否启动成功：

```bash
pgrep -a tailscaled
python3 -c "import socket; s=socket.create_connection(('127.0.0.1',1080),2); print('socks_up'); s.close()"
```

## 2. 登录并加入 tailnet

首次使用需要登录授权：

```bash
sudo tailscale up --accept-dns=false --accept-routes=true
```

按输出提示打开登录链接完成授权，然后验证：

```bash
tailscale status
```

## 3. 启动后端（让 SSH 走 SOCKS5）

启动后端时设置环境变量 `TS_SOCKS5_SERVER`，让后端的 SSH 探测通过 SOCKS5 走 tailscale netstack：

```bash
TS_SOCKS5_SERVER='127.0.0.1:1080' \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

说明：

- `TS_SOCKS5_SERVER`：后端通过此 SOCKS5 建立到节点的 SSH 连接
- `--reload`：开发态自动重载（生产环境建议去掉）

## 4. 快速验证（后端视角）

在后端启动后运行集群注册测试（见 [集群注册测试运行指南.md](file:///home/devbox/project/backend/docs/%E9%9B%86%E7%BE%A4%E6%B3%A8%E5%86%8C%E6%B5%8B%E8%AF%95%E8%BF%90%E8%A1%8C%E6%8C%87%E5%8D%97.md)）：

```bash
LOGIN_PASSWORD='admin123' \
HADOOP_PASSWORD='limouren...' \
BASE_URL='http://127.0.0.1:8000' \
python3 /home/devbox/project/backend/tests/test_cluster_register.py
```

如果成功用例通过，说明 SSH 路由链路已打通。

## 5. 常见问题与排查

### 5.1 `注册失败：SSH不可连接` (Connection refused)

**现象**：后端返回 `[Errno 111] Connection refused`。
**原因**：后端配置了 `TS_SOCKS5_SERVER`，但本地 `1080` 端口没有 SOCKS5 服务在运行。
**解决**：
1. 检查 `tailscaled` 是否带 `--socks5-server=127.0.0.1:1080` 参数启动。
2. 使用 `ss -tunlp | grep 1080` 确认端口是否被监听。

### 5.2 `注册失败：SSH不可连接` (timed out)

**现象**：后端返回 `timed out`。
**原因**：SOCKS5 代理虽然开了，但 Tailscale 未连接或目标节点不在线。
**解决**：
1. 执行 `tailscale status` 检查节点状态。
2. 检查 `/tmp/tailscaled.log` 是否有连接报错。

### 5.3 `tailscale status` 显示 `NeedsLogin`

重新执行：

```bash
sudo tailscale up --accept-dns=false --accept-routes=true
```

### 5.4 快速重启代理

如果发现代理失效，可以使用以下组合命令：

```bash
sudo pkill tailscaled
sudo nohup /usr/sbin/tailscaled \
  --tun=userspace-networking \
  --socket=/var/run/tailscale/tailscaled.sock \
  --state=/var/lib/tailscale/tailscaled.state \
  --socks5-server=127.0.0.1:1080 \
  >/tmp/tailscaled.log 2>&1 &
```

