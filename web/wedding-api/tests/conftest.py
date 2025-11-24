import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
# Import all models to ensure they are registered with Base
from app.models import * 

# Use SQLite for testing to avoid needing a separate Postgres DB setup
# Note: This requires handling Postgres-specific types if used. 
# Since we use sqlalchemy.dialects.postgresql.UUID, this might fail with SQLite.
# We will use a Mock or a separate Postgres connection if available.
# For simplicity in this environment, let's assume we might need to Mock the DB 
# or use the DEV DB with transaction rollback (careful!).

# Better approach for this environment: 
# Override the dependency to use a test session.

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c

# For a real project, we would setup a separate test database.
# Here, to ensure it works without complex setup, we will just rely on the TestClient 
# hitting the app. 
# WARNING: This might write to the actual DB if we don't override get_db.

# Let's try to override get_db to use a transaction that rolls back.
# However, `TestClient` runs in the same thread/process usually, so it's possible.
