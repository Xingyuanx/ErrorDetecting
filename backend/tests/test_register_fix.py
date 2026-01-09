import httpx
import asyncio
import json
import os
import pytest

async def _run_register_checks(base_url: str):
    url = f"{base_url.rstrip('/')}/api/v1/user/register"
    
    # 1. 测试字段缺失 (422)
    print("\n1. Testing missing field...")
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
        # fullName missing
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")

    # 2. 测试校验错误 (400 with errors)
    print("\n2. Testing validation error (short username)...")
    payload = {
        "username": "t",
        "email": "invalid-email",
        "password": "123",
        "fullName": "Z"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")

    # 3. 测试用户名已存在 (400 with message)
    # 假设 admin 已存在
    print("\n3. Testing duplicate username...")
    payload = {
        "username": "admin",
        "email": "admin_new@example.com",
        "password": "Password123",
        "fullName": "Administrator"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")

def test_register_fix_e2e():
    base_url = os.getenv("E2E_BASE_URL", "").strip()
    if not base_url:
        pytest.skip("需要设置 E2E_BASE_URL 并启动后端服务")
    asyncio.run(_run_register_checks(base_url))

if __name__ == "__main__":
    url = os.getenv("E2E_BASE_URL", "http://localhost:8000").strip()
    asyncio.run(_run_register_checks(url))
