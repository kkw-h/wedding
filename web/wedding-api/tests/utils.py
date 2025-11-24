import random
import string
from typing import Dict, List, Union
from fastapi.testclient import TestClient
from app.config import settings

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))

def random_phone() -> str:
    return f"13{random.randint(100000000, 999999999)}"

def get_auth_headers(client: TestClient, username: str = None, role: Union[str, List[str]] = "PLANNER") -> Dict[str, str]:
    if not username:
        username = random_lower_string()
    password = "password123"
    
    roles = [role] if isinstance(role, str) else role

    # Try to register (ignore if exists)
    # Note: /register now expects "roles" (list) not "role"
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "username": username,
            "password": password,
            "roles": roles
        },
    )
    
    # Login
    response = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data={
            "username": username,
            "password": password
        },
    )
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.text}")
        
    data = response.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}