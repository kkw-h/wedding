from unittest.mock import patch
from fastapi.testclient import TestClient
from app.config import settings
from tests.utils import get_auth_headers

def test_upload_file(client: TestClient) -> None:
    # Get auth headers
    headers = get_auth_headers(client, role="PLANNER")

    # Mock StorageService to avoid real MinIO calls during test
    with patch("app.api.v1.endpoints.assets.storage.upload_file") as mock_upload, \
         patch("app.api.v1.endpoints.assets.storage.get_url") as mock_get_url:
        
        import uuid
        random_key = f"2025/01/{uuid.uuid4()}.jpg"
        mock_upload.return_value = random_key
        mock_get_url.return_value = f"http://minio/wedding/{random_key}"
        
        # Create a fake file
        files = {
            "file": ("test_image.jpg", b"fake-image-content", "image/jpeg")
        }
        
        # No project_id provided (optional)
        data = {} 
        
        response = client.post(
            f"{settings.API_V1_STR}/assets/upload",
            headers=headers,
            files=files,
            data=data,
        )
        
        assert response.status_code == 200, response.text
        content = response.json()
        assert content["filename"] == "test_image.jpg"
        assert content["url"] == f"http://minio/wedding/{random_key}"
        assert "id" in content

def test_upload_file_no_auth(client: TestClient) -> None:
    files = {
        "file": ("test.jpg", b"content", "image/jpeg")
    }
    response = client.post(
        f"{settings.API_V1_STR}/assets/upload",
        files=files,
    )
    assert response.status_code == 401
