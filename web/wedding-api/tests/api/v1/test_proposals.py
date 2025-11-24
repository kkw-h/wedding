from fastapi.testclient import TestClient
from app.config import settings
from tests.utils import get_auth_headers, random_phone, random_lower_string

def create_project_helper(client, headers):
    lead_resp = client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers,
        json={"customer_name": "Proposal Lead " + random_lower_string(), "phone": random_phone()},
    )
    lead_id = lead_resp.json()["id"]
    
    proj_resp = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=headers,
        json={
            "lead_id": lead_id,
            "name": "Proposal Project",
            "wedding_date": "2025-12-01"
        },
    )
    return proj_resp.json()["id"]

def test_proposal_crud_and_versioning(client: TestClient):
    # 1. Setup
    planner_headers = get_auth_headers(client, role="PLANNER")
    project_id = create_project_helper(client, planner_headers)
    
    # 2. Create Proposal (Plan A)
    prop_data = {
        "project_id": project_id,
        "name": "Plan A - Mori Style",
        "description": "Green and white theme"
    }
    create_resp = client.post(
        f"{settings.API_V1_STR}/proposals/project/{project_id}",
        headers=planner_headers,
        json=prop_data
    )
    assert create_resp.status_code == 200
    proposal_id = create_resp.json()["id"]
    
    # 3. Auto-Save (Update current_data)
    # Simulate user adding some budget items in editor
    draft_data_v1 = {
        "sections": ["stage", "welcome_area"],
        "budget": 20000,
        "colors": ["green", "white"]
    }
    update_resp = client.put(
        f"{settings.API_V1_STR}/proposals/{proposal_id}",
        headers=planner_headers,
        json={"current_data": draft_data_v1}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["current_data"]["budget"] == 20000
    
    # 4. Create Version v1.0 (Manual Save)
    version_data = {
        "proposal_id": proposal_id,
        "snapshot_data": draft_data_v1,
        "tag_name": "v1.0 Initial",
        "change_log": {"diff": "Created"}
    }
    v1_resp = client.post(
        f"{settings.API_V1_STR}/proposals/{proposal_id}/versions",
        headers=planner_headers,
        json=version_data
    )
    assert v1_resp.status_code == 200
    v1_id = v1_resp.json()["id"]
    
    # 5. Continue Editing (Auto-Save v2 state)
    draft_data_v2 = {
        "sections": ["stage", "welcome_area", "dessert_table"],
        "budget": 25000, # Increased
        "colors": ["green", "white", "gold"]
    }
    client.put(
        f"{settings.API_V1_STR}/proposals/{proposal_id}",
        headers=planner_headers,
        json={"current_data": draft_data_v2}
    )
    
    # Verify current is v2
    get_resp = client.get(
        f"{settings.API_V1_STR}/proposals/{proposal_id}",
        headers=planner_headers
    )
    assert get_resp.json()["current_data"]["budget"] == 25000
    
    # 6. Restore to v1.0
    restore_resp = client.post(
        f"{settings.API_V1_STR}/proposals/{proposal_id}/restore/{v1_id}",
        headers=planner_headers
    )
    assert restore_resp.status_code == 200
    
    # Verify current is back to v1
    restored_prop = restore_resp.json()
    assert restored_prop["current_data"]["budget"] == 20000
    assert "dessert_table" not in restored_prop["current_data"]["sections"]

def test_multiple_proposals(client: TestClient):
    planner_headers = get_auth_headers(client, role="PLANNER")
    project_id = create_project_helper(client, planner_headers)
    
    # Plan A
    client.post(
        f"{settings.API_V1_STR}/proposals/project/{project_id}",
        headers=planner_headers,
        json={"project_id": project_id, "name": "Plan A"}
    )
    # Plan B
    client.post(
        f"{settings.API_V1_STR}/proposals/project/{project_id}",
        headers=planner_headers,
        json={"project_id": project_id, "name": "Plan B"}
    )
    
    # List
    list_resp = client.get(
        f"{settings.API_V1_STR}/proposals/project/{project_id}",
        headers=planner_headers
    )
    assert len(list_resp.json()) == 2
