from fastapi.testclient import TestClient
from app.config import settings
from app.models.user import RoleType, User
from tests.utils import get_auth_headers, random_lower_string

# Removing 'db' fixture dependency for now as it's not set up in conftest.py yet.
# We will verify via API calls instead of direct DB access for this environment.

def test_create_user_by_admin(client: TestClient):
    admin_headers = get_auth_headers(client, role="ADMIN")
    username = random_lower_string()
    password = "newpassword123"
    
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=admin_headers,
        json={
            "username": username,
            "password": password,
            "roles": ["PLANNER"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username
    assert "PLANNER" in data["roles"] or "PLANNER" in data["role_list"] # depending on alias
    
    # Login check
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data={"username": username, "password": password}
    )
    assert login_resp.status_code == 200

def test_create_user_by_planner_forbidden(client: TestClient):
    planner_headers = get_auth_headers(client, role="PLANNER")
    username = random_lower_string()
    
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=planner_headers,
        json={
            "username": username,
            "password": "password",
            "roles": ["PLANNER"]
        }
    )
    assert response.status_code == 403

def test_read_users_by_admin(client: TestClient):
    admin_headers = get_auth_headers(client, role="ADMIN")
    response = client.get(
        f"{settings.API_V1_STR}/users/",
        headers=admin_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_user_role_by_admin(client: TestClient):
    admin_headers = get_auth_headers(client, role="ADMIN")
    
    # Create a target user first
    username = random_lower_string()
    create_resp = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=admin_headers,
        json={"username": username, "password": "pwd", "roles": ["PLANNER"]}
    )
    user_id = create_resp.json()["id"]
    
    # Update role to MANAGER and PLANNER
    response = client.put(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=admin_headers,
        json={"roles": ["MANAGER", "PLANNER"]}
    )
    assert response.status_code == 200
    roles = response.json().get("role_list") or response.json().get("roles")
    assert "MANAGER" in roles
    assert "PLANNER" in roles

def test_get_roles(client: TestClient):
    headers = get_auth_headers(client, role="PLANNER")
    response = client.get(f"{settings.API_V1_STR}/users/roles", headers=headers)
    assert response.status_code == 200
    assert "ADMIN" in response.json()
    assert "PLANNER" in response.json()
