from fastapi.testclient import TestClient
from app.config import settings
from tests.utils import get_auth_headers, random_phone, random_lower_string

def create_project_helper(client, headers):
    lead_resp = client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers,
        json={"customer_name": "Approval Lead " + random_lower_string(), "phone": random_phone()},
    )
    lead_id = lead_resp.json()["id"]
    
    proj_resp = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=headers,
        json={
            "lead_id": lead_id,
            "name": "Approval Project",
            "wedding_date": "2025-12-01"
        },
    )
    return proj_resp.json()["id"]

def test_approval_flow(client: TestClient):
    # 1. Setup Users
    planner_headers = get_auth_headers(client, role="PLANNER")
    manager_headers = get_auth_headers(client, role="MANAGER")
    
    # 2. Planner Creates Project & Approval
    project_id = create_project_helper(client, planner_headers)
    
    approval_data = {
        "project_id": project_id,
        "type": "DISCOUNT",
        "current_data": {"discount_amount": 500, "reason": "VIP Customer"}
    }
    create_resp = client.post(
        f"{settings.API_V1_STR}/approvals/",
        headers=planner_headers,
        json=approval_data
    )
    assert create_resp.status_code == 200
    approval_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "PENDING"
    
    # 3. Manager Reads Approval
    list_resp = client.get(
        f"{settings.API_V1_STR}/approvals/",
        headers=manager_headers
    )
    ids = [a["id"] for a in list_resp.json()]
    assert approval_id in ids
    
    # 4. Manager Approves
    process_resp = client.put(
        f"{settings.API_V1_STR}/approvals/{approval_id}/process",
        headers=manager_headers,
        json={"status": "APPROVED", "audit_log": "Approved by Manager"}
    )
    assert process_resp.status_code == 200
    assert process_resp.json()["status"] == "APPROVED"
    assert process_resp.json()["approver_id"] is not None
    
    # 5. Planner Check Status
    check_resp = client.get(
        f"{settings.API_V1_STR}/approvals/",
        headers=planner_headers
    )
    my_approvals = check_resp.json()
    my_approval = next((a for a in my_approvals if a["id"] == approval_id), None)
    assert my_approval["status"] == "APPROVED"

def test_planner_cannot_process_approval(client: TestClient):
    planner_headers = get_auth_headers(client, role="PLANNER")
    project_id = create_project_helper(client, planner_headers)
    
    # Create Approval
    create_resp = client.post(
        f"{settings.API_V1_STR}/approvals/",
        headers=planner_headers,
        json={"project_id": project_id, "type": "PAYMENT"}
    )
    approval_id = create_resp.json()["id"]
    
    # Planner tries to self-approve
    resp = client.put(
        f"{settings.API_V1_STR}/approvals/{approval_id}/process",
        headers=planner_headers,
        json={"status": "APPROVED"}
    )
    assert resp.status_code == 403
