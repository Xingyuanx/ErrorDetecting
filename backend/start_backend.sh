#!/bin/bash

# 确保脚本在 backend 目录下运行
cd "$(dirname "$0")"

echo "=== 正在检查 Tailscale 状态 ==="

# 1. 检查并启动 tailscaled (SOCKS5 代理模式)
if ! pgrep -f "tailscaled.*--socks5-server=127.0.0.1:1080" > /dev/null; then
    echo "Tailscale SOCKS5 代理未运行，正在启动..."
    sudo pkill tailscaled 2>/dev/null || true
    sudo nohup /usr/sbin/tailscaled \
      --tun=userspace-networking \
      --socket=/var/run/tailscale/tailscaled.sock \
      --state=/var/lib/tailscale/tailscaled.state \
      --socks5-server=127.0.0.1:1080 \
      >/tmp/tailscaled.log 2>&1 &
    
    # 等待启动完成
    sleep 2
    
    # 确保加入网络
    sudo tailscale up --accept-dns=false --accept-routes=true
else
    echo "Tailscale SOCKS5 代理已在 127.0.0.1:1080 运行。"
fi

# 2. 验证代理端口是否可用
if python3 -c "import socket; s=socket.create_connection(('127.0.0.1',1080),2); s.close()" 2>/dev/null; then
    echo "SOCKS5 代理验证成功。"
else
    echo "错误: SOCKS5 代理端口 1080 无法访问，请检查 /tmp/tailscaled.log"
    exit 1
fi

echo "=== 正在启动后端服务 ==="

# 3. 启动后端服务 (注入代理环境变量)
export TS_SOCKS5_SERVER='127.0.0.1:1080'
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
