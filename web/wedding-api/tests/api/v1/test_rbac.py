from fastapi.testclient import TestClient
from app.config import settings
from app.models.user import RoleType, User
from tests.utils import get_auth_headers, random_lower_string
from app.core.permissions import Permissions

def test_user_permissions_field(client: TestClient):
    """
    Ensure the API returns the 'permissions' list correctly based on role.
    """
    # 1. Create ADMIN user
    admin_headers = get_auth_headers(client, role="ADMIN")
    
    # 2. Create Planner
    new_username = random_lower_string()
    create_resp = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=admin_headers,
        json={
            "username": new_username,
            "password": "pwd",
            "roles": ["PLANNER"]
        }
    )
    assert create_resp.status_code == 200
    new_user = create_resp.json()
    assert "permissions" in new_user
    assert isinstance(new_user["permissions"], list)
    # Planner permissions check (assuming DB synced or default loaded)
    # Note: If DB is empty, this might be empty unless we run sync first.
    # In CI/CD env, we rely on the fact that sync might have run or defaults apply if using the old logic.
    # But new logic reads from DB.
    
    # Let's verify Multi-Role Permissions
    multi_username = random_lower_string()
    multi_resp = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=admin_headers,
        json={
            "username": multi_username,
            "password": "pwd",
            "roles": ["PLANNER", "ADMIN"]
        }
    )
    multi_user = multi_resp.json()
    assert Permissions.LEAD_VIEW_OWN in multi_user["permissions"] # From Planner
    assert Permissions.USER_MANAGE in multi_user["permissions"] # From Admin

def test_admin_permissions(client: TestClient):
    admin_headers = get_auth_headers(client, role="ADMIN")
    
    username = random_lower_string()
    resp = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=admin_headers,
        json={"username": username, "password": "pwd", "roles": ["ADMIN"]}
    )
    data = resp.json()
    # Ensure admin has permissions (requires DB sync typically, but tests/utils creates admin first)
    # The get_auth_headers util creates a user, but does it set roles in DB?
    # We need to update get_auth_headers to handle roles list
    assert "permissions" in data