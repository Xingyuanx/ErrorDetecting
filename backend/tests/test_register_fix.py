import httpx
import asyncio
import json

async def test_register():
    url = "http://localhost:8000/api/v1/user/register"
    
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

if __name__ == "__main__":
    asyncio.run(test_register())
