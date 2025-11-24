from fastapi.testclient import TestClient
from app.config import settings

def test_register_new_user(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "username": "test_planner_1",
            "password": "password123",
            "role": "PLANNER"
        },
    )
    if response.status_code == 400:
        # User might already exist from previous runs
        assert response.json()["detail"] == "Username already registered"
    else:
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "test_planner_1"
        assert "id" in data
        assert "password" not in data

def test_login_access_token(client: TestClient):
    # Ensure user exists
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "username": "test_login_user",
            "password": "password123",
            "role": "MANAGER"
        },
    )
    
    login_data = {
        "username": "test_login_user",
        "password": "password123"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data=login_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient):
    login_data = {
        "username": "test_login_user",
        "password": "wrongpassword"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data=login_data,
    )
    assert response.status_code == 401
