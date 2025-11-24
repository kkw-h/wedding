from fastapi.testclient import TestClient
from app.config import settings
from app.models.user import RoleType, User
from tests.utils import get_auth_headers, random_lower_string
from app.core.permissions import Permissions

def test_sync_and_rbac(client: TestClient):
    """
    Test synchronization and DB-based RBAC
    """
    admin_headers = get_auth_headers(client, role="ADMIN")
    
    # 1. Sync Permissions
    sync_resp = client.post(
        f"{settings.API_V1_STR}/permissions/sync",
        headers=admin_headers
    )
    assert sync_resp.status_code == 200
    
    # 2. Verify Permissions exist in DB
    list_resp = client.get(
        f"{settings.API_V1_STR}/permissions/",
        headers=admin_headers
    )
    assert list_resp.status_code == 200
    perms = list_resp.json()
    assert len(perms) > 0
    assert any(p["code"] == Permissions.USER_MANAGE for p in perms)
    
    # 3. Create a Planner and verify they have DB-sourced permissions
    username = random_lower_string()
    client.post(
        f"{settings.API_V1_STR}/users/",
        headers=admin_headers,
        json={"username": username, "password": "pwd", "roles": ["PLANNER"]}
    )
    
    # Login as new planner
    planner_login = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data={"username": username, "password": "pwd"}
    )
    token = planner_login.json()["access_token"]
    
    # Get ME (assuming there was an endpoint, or we infer from what they can do)
    # Since we updated User schema to return permissions, we can check a user list or create response
    # Let's check the user list as Admin to see the planner's perms
    user_list = client.get(
        f"{settings.API_V1_STR}/users/",
        headers=admin_headers
    ).json()
    
    target_user = next(u for u in user_list if u["username"] == username)
    assert isinstance(target_user["permissions"], list)
    assert Permissions.LEAD_VIEW_OWN in target_user["permissions"]
    assert Permissions.USER_MANAGE not in target_user["permissions"]