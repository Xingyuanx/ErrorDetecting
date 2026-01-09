import os
import json
import requests

def main():
    base = os.getenv("API_BASE", "http://localhost:8000")
    token = os.getenv("API_TOKEN", "")
    name = os.getenv("CLUSTER_NAME", "test-cluster")
    ctype = os.getenv("CLUSTER_TYPE", "hadoop")
    nodes_env = os.getenv("CLUSTER_NODES")
    if not nodes_env:
        print("请通过环境变量 CLUSTER_NODES 提供节点信息，示例：")
        print('[{"hostname":"nn","ip_address":"10.0.0.1","ssh_user":"u","ssh_password":"p"}]')
        return
    nodes = json.loads(nodes_env)
    payload = {
        "name": name,
        "type": ctype,
        "node_count": len(nodes),
        "health_status": "unknown",
        "nodes": nodes
    }
    if not token:
        try:
            r = requests.post(f"{base}/user/login", json={"username": "admin", "password": "admin123"}, timeout=15)
            if r.status_code == 200:
                token = r.json().get("token") or ""
                print("已自动登录获取 token")
            else:
                print("自动登录失败，请设置 API_TOKEN 环境变量")
        except Exception as e:
            print(f"自动登录异常：{e}")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.post(f"{base}/clusters", json=payload, headers=headers, timeout=30)
    print(r.status_code, r.text)

if __name__ == "__main__":
    main()
