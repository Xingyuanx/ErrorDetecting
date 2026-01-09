#!/bin/bash

# 配置变量
BASE_URL="http://localhost:8000/api/v1"
USERNAME="admin"
PASSWORD="admin123"
CLUSTER_UUID="5c43a9c7-e2a9-4756-b75d-6813ac55d3ba"

echo "正在登录获取 Token..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/user/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -oP '(?<="token":")[^"]*')

if [ -z "$TOKEN" ]; then
    echo "登录失败，无法获取 Token"
    echo "响应内容: $LOGIN_RESPONSE"
    exit 1
fi

echo "登录成功，正在调用集群停止接口..."
curl -X POST "$BASE_URL/ops/clusters/$CLUSTER_UUID/stop" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n操作完成"
