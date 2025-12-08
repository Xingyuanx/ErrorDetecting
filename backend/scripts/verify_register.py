from fastapi.testclient import TestClient
from app.main import app

def run():
    client = TestClient(app)
    username = "user_test_001"
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "Passw0rd!",
        "fullName": "测试用户"
    }
    r = client.post("/api/v1/user/register", json=payload)
    print("register.status", r.status_code)
    print("register.body", r.json())
    lr = client.post("/api/v1/user/login", json={"username": username, "password": "Passw0rd!"})
    print("login.status", lr.status_code)
    print("login.body", lr.json())

if __name__ == "__main__":
    run()
