# Tailscale 启动指南

本文档用于在本项目部署/联调环境中启动与验证 Tailscale 连接。覆盖两类常见环境：

- 机器/VM 有 systemd，可用 `systemctl` 管理 `tailscaled`
- 容器/受限环境无 systemd（例如 PID 1 不是 systemd），使用 userspace networking 启动 `tailscaled`

## 1. 前置检查

确认已安装：

```bash
which tailscale
tailscale version
```

查看当前状态：

```bash
tailscale status
```

如果提示 `failed to connect to local tailscaled`，说明 `tailscaled` 没有运行或 socket 不对。

## 2. 方式 A：systemd 环境启动（推荐）

启动并设置开机自启：

```bash
sudo systemctl start tailscaled
sudo systemctl enable tailscaled
```

登录并启用（首次需要网页登录授权）：

```bash
sudo tailscale up --accept-dns=false --accept-routes=false
```

验证：

```bash
tailscale status
tailscale ip -4
```

## 3. 方式 B：无 systemd / 容器环境启动（userspace networking）

当 `systemctl` 不可用（例如 PID 1 不是 systemd），用 userspace networking 启动 `tailscaled`：

```bash
sudo tailscaled \
  --tun=userspace-networking \
  --socket=/var/run/tailscale/tailscaled.sock \
  --state=/var/lib/tailscale/tailscaled.state
```

为了让其在后台运行且不占用终端，可使用：

```bash
sudo nohup tailscaled \
  --tun=userspace-networking \
  --socket=/var/run/tailscale/tailscaled.sock \
  --state=/var/lib/tailscale/tailscaled.state \
  >/tmp/tailscaled.log 2>&1 &
```

首次登录（会输出一个 URL，打开后完成授权）：

```bash
sudo tailscale up --accept-dns=false --accept-routes=false
```

验证：

```bash
tailscale status
tailscale ip -4
```

## 4. 常用参数说明

- `--accept-dns=false`：避免 Tailscale 接管系统 DNS（更稳妥，减少联调环境干扰）
- `--accept-routes=false`：不接收其它节点宣告的子网路由（除非明确需要）

如果你看到 `Some peers are advertising routes but --accept-routes is false` 属正常提示。

## 5. 常见问题

### 5.1 `Logged out.` / `NeedsLogin`

执行：

```bash
sudo tailscale up --accept-dns=false --accept-routes=false
```

根据输出提示访问登录链接完成授权。

### 5.2 `failed to connect to local tailscaled`

说明 `tailscaled` 未运行或 socket 路径不一致：

- systemd 环境：确认 `sudo systemctl status tailscaled`
- 无 systemd 环境：确认 `tailscaled` 进程存在，以及 `--socket` 路径与 `tailscale` 命令一致

### 5.3 退出/停止

退出网络：

```bash
sudo tailscale down
```

停止守护进程：

- systemd：`sudo systemctl stop tailscaled`
- 无 systemd：`sudo pkill tailscaled`

