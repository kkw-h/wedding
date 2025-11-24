from fastapi.testclient import TestClient
from app.config import settings
from tests.utils import get_auth_headers, random_phone, random_lower_string

def test_create_project(client: TestClient):
    headers = get_auth_headers(client, role="PLANNER")
    
    # 1. Create Lead
    lead_resp = client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers,
        json={"customer_name": "Project Lead", "phone": random_phone()},
    )
    lead_id = lead_resp.json()["id"]
    
    # 2. Create Project
    data = {
        "lead_id": lead_id,
        "name": "Wedding Project 1",
        "wedding_date": "2025-12-01",
        "total_budget": 50000
    }
    response = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["lead_id"] == lead_id
    assert content["stage"] == "PREPARING"
    
    # 3. Verify Lead Status is WON
    # We need to fetch the lead again
    lead_resp_2 = client.get(f"{settings.API_V1_STR}/leads/{lead_id}", headers=headers)
    assert lead_resp_2.json()["status"] == "WON"

def test_create_project_permission(client: TestClient):
    # Planner A
    username_a = random_lower_string()
    headers_a = get_auth_headers(client, username=username_a, role="PLANNER")
    
    # Planner B
    username_b = random_lower_string()
    headers_b = get_auth_headers(client, username=username_b, role="PLANNER")
    
    # A creates lead
    lead_resp = client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers_a,
        json={"customer_name": "Lead A", "phone": random_phone()},
    )
    lead_id = lead_resp.json()["id"]
    
    # B tries to convert A's lead
    data = {
        "lead_id": lead_id,
        "name": "Stolen Project",
        "wedding_date": "2025-12-01"
    }
    response = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=headers_b, # B's token
        json=data,
    )
    assert response.status_code == 403

def test_read_projects_isolation(client: TestClient):
    # Planner A
    headers_a = get_auth_headers(client, role="PLANNER")
    # Planner B
    headers_b = get_auth_headers(client, role="PLANNER")
    
    # A creates lead & project
    lead_resp = client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers_a,
        json={"customer_name": "Lead A", "phone": random_phone()},
    )
    client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=headers_a,
        json={
            "lead_id": lead_resp.json()["id"],
            "name": "Project A",
            "wedding_date": "2025-12-01"
        },
    )
    
    # B should not see Project A
    resp_b = client.get(f"{settings.API_V1_STR}/projects/", headers=headers_b)
    projects_b = resp_b.json()
    # Ensure no project with name "Project A" is in the list (assuming unique names for test simplicity, though not enforced)
    names_b = [p["name"] for p in projects_b]
    assert "Project A" not in names_b
