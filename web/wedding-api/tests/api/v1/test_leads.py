from fastapi.testclient import TestClient
from app.config import settings
from tests.utils import get_auth_headers, random_phone, random_lower_string

def test_create_lead(client: TestClient):
    headers = get_auth_headers(client, role="PLANNER")
    phone = random_phone()
    data = {
        "customer_name": "Test Customer",
        "phone": phone,
        "wedding_date": "2025-10-01",
        "budget_min": 10000,
        "budget_max": 20000
    }
    response = client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["customer_name"] == data["customer_name"]
    assert content["phone"] == data["phone"]
    assert "id" in content

def test_create_lead_duplicate_phone(client: TestClient):
    headers = get_auth_headers(client, role="PLANNER")
    phone = random_phone()
    data = {
        "customer_name": "Test Customer 1",
        "phone": phone
    }
    
    # First create
    client.post(f"{settings.API_V1_STR}/leads/", headers=headers, json=data)
    
    # Second create with same phone
    response = client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_read_leads(client: TestClient):
    headers = get_auth_headers(client, role="PLANNER")
    # Create a lead first to ensure there is at least one
    client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers,
        json={"customer_name": "My Lead", "phone": random_phone()},
    )
    
    response = client.get(f"{settings.API_V1_STR}/leads/", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) >= 1

def test_read_lead_permissions(client: TestClient):
    # Planner A
    username_a = random_lower_string()
    headers_a = get_auth_headers(client, username=username_a, role="PLANNER")
    
    # Planner B
    username_b = random_lower_string()
    headers_b = get_auth_headers(client, username=username_b, role="PLANNER")
    
    # A creates a lead
    resp = client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers_a,
        json={"customer_name": "Lead A", "phone": random_phone()},
    )
    lead_id = resp.json()["id"]
    
    # A reads it -> OK
    resp_a = client.get(f"{settings.API_V1_STR}/leads/{lead_id}", headers=headers_a)
    assert resp_a.status_code == 200
    
    # B reads it -> 403 Forbidden
    resp_b = client.get(f"{settings.API_V1_STR}/leads/{lead_id}", headers=headers_b)
    assert resp_b.status_code == 403

def test_read_leads_isolation(client: TestClient):
    # Planner A
    headers_a = get_auth_headers(client, role="PLANNER")
    # Planner B
    headers_b = get_auth_headers(client, role="PLANNER")
    
    # A creates lead
    client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers_a,
        json={"customer_name": "Lead A", "phone": random_phone()},
    )
    
    # B should not see A's lead in list
    resp_b = client.get(f"{settings.API_V1_STR}/leads/", headers=headers_b)
    leads_b = resp_b.json()
    
    # We can't strictly assert leads_b is empty because B might have created leads in previous tests 
    # if we reused the user, but here we generate random users every time (mostly).
    # Ideally, we check that none of the IDs in leads_b belong to A. 
    # But for now, let's just create a unique marker.
    
    marker_phone = random_phone()
    client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers_a,
        json={"customer_name": "Unique Lead A", "phone": marker_phone},
    )
    
    resp_list_b = client.get(f"{settings.API_V1_STR}/leads/", headers=headers_b)
    phones_b = [l["phone"] for l in resp_list_b.json()]
    assert marker_phone not in phones_b
