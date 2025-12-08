# Cloudflare Tunnel 跨网络访问教程（方案 B）

## 适用场景
- 你与远程主机不在同一局域网，需要临时向公网暴露本地开发端口（前端 5173、后端 8000）
- 仅用于演示和联调；生产请使用命名隧道、反向代理与严格鉴权

## 准备
- 平台：Windows（PowerShell）
- 目录：在项目根目录执行（已下载 `cloudflared.exe`）

## 步骤一：下载 cloudflared（已完成）
- 命令（参考）：
```
$ProgressPreference = 'SilentlyContinue'; \
$url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe'; \
$out = Join-Path (Get-Location) 'cloudflared.exe'; \
Invoke-WebRequest -Uri $url -OutFile $out; \
Write-Host "Downloaded: $out"
```

## 步骤二：启动前端隧道（Vite 5173）
- 启动命令：
```
.\cloudflared.exe tunnel --protocol http2 --url http://localhost:5173
```
- 终端会打印一个临时域名（示例）：
```
https://<随机>.trycloudflare.com
```
- 远程访问：在浏览器打开该域名即可访问你的前端页面
- 提示：保持命令行进程运行；若 HMR 异常，可在 `frontend-vue/.env` 设置：
```
VITE_HMR_HOST=<上述临时域名>
VITE_HMR_PORT=443
```

## 步骤三：启动后端隧道（API 8000）
- 启动命令：
```
根目录执行
.\cloudflared.exe tunnel --protocol http2 --url http://localhost:8000 --no-autoupdate
```
- 终端会打印另一个临时域名；将前端代理目标指向该域名：
```
VITE_API_TARGET=https://<后端临时域名>
```

## 验证
- 前端：打开前端临时域名首页；访问 `/<任意页面>` 与 `/@vite/client`（HMR 检测）
- 后端：访问 `https://<后端临时域名>/api/v1/health` 返回 200 即可

## 常见问题
- QUIC 连接超时：增加 `--protocol http2`（已使用）
- 日志提示未找到证书：Quick Tunnel 可忽略；若使用命名隧道请按官方文档配置证书
- 端口未监听：确保本地 `npm run dev` 与 `uvicorn` 已启动（5173、8000）

## 安全与说明
- 临时域名仅用于演示；Cloudflare 可能回收，随时重启生成新域名
- 不要在开发环境暴露敏感信息；生产务必启用 TLS 与鉴权，并限制来源

## 关闭隧道
- 在运行隧道的终端按 `Ctrl + C` 即可

## 参考
- 官方文档：https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/run-tunnel/trycloudflare/
