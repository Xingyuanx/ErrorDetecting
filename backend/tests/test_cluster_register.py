import os
import time
import json
import httpx


def _env(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    if v is None:
        return default
    v2 = v.strip()
    return v2 if v2 else default


def _login(client: httpx.Client, base_url: str, username: str, password: str) -> str:
    r = client.post(
        f"{base_url}/api/v1/user/login",
        json={"username": username, "password": password},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    token = data.get("token")
    if not token:
        raise RuntimeError("login_no_token")
    return token


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _list_clusters(client: httpx.Client, base_url: str, token: str) -> list[dict]:
    r = client.get(f"{base_url}/api/v1/clusters", headers=_auth_headers(token), timeout=20)
    r.raise_for_status()
    data = r.json() or {}
    return data.get("clusters") or []


def _delete_cluster(client: httpx.Client, base_url: str, token: str, uuid: str) -> None:
    r = client.delete(f"{base_url}/api/v1/clusters/{uuid}", headers=_auth_headers(token), timeout=30)
    r.raise_for_status()


def _create_cluster(client: httpx.Client, base_url: str, token: str, payload: dict) -> httpx.Response:
    return client.post(
        f"{base_url}/api/v1/clusters",
        headers={**_auth_headers(token), "Content-Type": "application/json"},
        content=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        timeout=120,
    )


def _success_payload(cluster_name: str, ssh_user: str, ssh_password: str) -> dict:
    nodes = [
        {"hostname": "hadoop102", "ip_address": "100.71.90.16", "ssh_user": ssh_user, "ssh_password": ssh_password},
        {"hostname": "hadoop103", "ip_address": "100.74.47.4", "ssh_user": ssh_user, "ssh_password": ssh_password},
        {"hostname": "hadoop104", "ip_address": "100.99.172.96", "ssh_user": ssh_user, "ssh_password": ssh_password},
        {"hostname": "hadoop105", "ip_address": "100.91.174.104", "ssh_user": ssh_user, "ssh_password": ssh_password},
        {"hostname": "hadoop100", "ip_address": "100.73.220.46", "ssh_user": ssh_user, "ssh_password": ssh_password},
    ]
    return {
        "name": cluster_name,
        "type": "hadoop",
        "node_count": 5,
        "health_status": "unknown",
        "description": "test cluster register",
        "namenode_ip": "100.71.90.16",
        "namenode_psw": ssh_password,
        "rm_ip": "100.74.47.4",
        "rm_psw": ssh_password,
        "nodes": nodes,
    }


def _failure_payload(base: dict) -> dict:
    bad = dict(base)
    bad["name"] = f"{base['name']}-bad-{int(time.time())}"
    bad["type"] = "bad_type"
    return bad


def main() -> int:
    base_url = _env("BASE_URL", "http://127.0.0.1:8000")
    login_user = _env("LOGIN_USER", "admin")
    login_password = _env("LOGIN_PASSWORD")
    ssh_user = _env("HADOOP_USER", "hadoop")
    ssh_password = _env("HADOOP_PASSWORD")

    missing = [k for k, v in [("LOGIN_PASSWORD", login_password), ("HADOOP_PASSWORD", ssh_password)] if not v]
    if missing:
        print(f"缺少环境变量: {', '.join(missing)}")
        print("示例：LOGIN_PASSWORD=admin123 HADOOP_PASSWORD='limouren...' BASE_URL=http://127.0.0.1:8000 python3 backend/tests/test_cluster_register.py")
        return 2

    with httpx.Client() as client:
        token = _login(client, base_url, login_user, login_password)

        clusters = _list_clusters(client, base_url, token)
        for c in clusters:
            if c.get("name") == "test" and c.get("uuid"):
                _delete_cluster(client, base_url, token, c["uuid"])

        ok_payload = _success_payload("test", ssh_user, ssh_password)
        r_ok = _create_cluster(client, base_url, token, ok_payload)
        if r_ok.status_code != 200:
            try:
                print("成功用例失败:", r_ok.status_code, r_ok.json())
            except Exception:
                print("成功用例失败:", r_ok.status_code, r_ok.text[:500])
            return 1
        data_ok = r_ok.json() or {}
        if data_ok.get("status") != "success":
            print("成功用例返回异常:", data_ok)
            return 1
        uuid = data_ok.get("uuid")
        print("成功用例通过: uuid=", uuid)

        bad_payload = _failure_payload(ok_payload)
        r_bad = _create_cluster(client, base_url, token, bad_payload)
        if r_bad.status_code != 400:
            try:
                print("失败用例未按预期返回 400:", r_bad.status_code, r_bad.json())
            except Exception:
                print("失败用例未按预期返回 400:", r_bad.status_code, r_bad.text[:500])
            return 1
        try:
            detail = r_bad.json()
        except Exception:
            detail = {"raw": r_bad.text[:500]}
        print("失败用例通过: status=400 detail=", detail)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

