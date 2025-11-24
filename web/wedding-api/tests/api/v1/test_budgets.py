from fastapi.testclient import TestClient
from app.config import settings
from tests.utils import get_auth_headers, random_phone, random_lower_string

def create_project_helper(client, headers):
    # 1. Create Lead
    lead_resp = client.post(
        f"{settings.API_V1_STR}/leads/",
        headers=headers,
        json={"customer_name": "Budget Lead " + random_lower_string(), "phone": random_phone()},
    )
    lead_id = lead_resp.json()["id"]
    
    # 2. Create Project
    proj_resp = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=headers,
        json={
            "lead_id": lead_id,
            "name": "Budget Project",
            "wedding_date": "2025-12-01"
        },
    )
    return proj_resp.json()["id"]

def test_budget_crud_and_security(client: TestClient):
    # 1. Setup Users
    # Planner
    planner_headers = get_auth_headers(client, role="PLANNER")
    # Manager
    manager_headers = get_auth_headers(client, role="MANAGER")
    
    # 2. Planner creates Project
    project_id = create_project_helper(client, planner_headers)
    
    # 3. Planner creates Budget Item
    item_data = {
        "project_id": project_id,
        "category": "Decor",
        "name": "Flowers",
        "quantity": 10,
        "unit_price": 100.0, # Sale Price: 100 * 10 = 1000
        "cost_price": 50.0   # Cost Price: 50 * 10 = 500. Planner inputs this but shouldn't see it back?
    }
    # Note: In our implementation, Planner CAN input cost_price (optional), 
    # but the response model `BudgetItemResponse` strips it.
    
    create_resp = client.post(
        f"{settings.API_V1_STR}/budgets/",
        headers=planner_headers,
        json=item_data,
    )
    assert create_resp.status_code == 200
    created_item = create_resp.json()
    assert created_item["name"] == "Flowers"
    assert created_item["total_sale_price"] == 1000.0
    # Security Check: Planner should NOT see cost_price
    assert "cost_price" not in created_item
    assert "gross_profit" not in created_item
    
    # 4. Planner Reads Budget
    list_resp = client.get(
        f"{settings.API_V1_STR}/budgets/project/{project_id}",
        headers=planner_headers
    )
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert "cost_price" not in items[0]
    
    # 5. Manager Reads Budget (Should see cost & profit)
    # Manager needs permission to read project?
    # Our project logic: Manager sees all projects.
    
    manager_list_resp = client.get(
        f"{settings.API_V1_STR}/budgets/project/{project_id}",
        headers=manager_headers
    )
    assert manager_list_resp.status_code == 200
    m_items = manager_list_resp.json()
    assert len(m_items) == 1
    item = m_items[0]
    
    assert "cost_price" in item
    assert item["cost_price"] == 50.0
    assert "gross_profit" in item
    assert item["gross_profit"] == 500.0 # (100-50)*10

def test_planner_cannot_update_cost_price(client: TestClient):
    planner_headers = get_auth_headers(client, role="PLANNER")
    project_id = create_project_helper(client, planner_headers)
    
    # Create Item
    item_resp = client.post(
        f"{settings.API_V1_STR}/budgets/",
        headers=planner_headers,
        json={
            "project_id": project_id,
            "category": "Labor",
            "name": "Host",
            "unit_price": 2000,
            "cost_price": 1000
        },
    )
    item_id = item_resp.json()["id"]
    
    # Planner tries to update cost_price to 1500
    # Our logic: Silent ignore
    update_data = {
        "cost_price": 1500,
        "unit_price": 2500
    }
    update_resp = client.put(
        f"{settings.API_V1_STR}/budgets/{item_id}",
        headers=planner_headers,
        json=update_data
    )
    assert update_resp.status_code == 200
    
    # Verify with Manager account that cost_price did NOT change
    manager_headers = get_auth_headers(client, role="MANAGER")
    check_resp = client.get(
        f"{settings.API_V1_STR}/budgets/project/{project_id}",
        headers=manager_headers
    )
    item = check_resp.json()[0]
    assert item["unit_price"] == 2500.0 # Changed
    assert item["cost_price"] == 1000.0 # Unchanged (Silent Ignore worked)
