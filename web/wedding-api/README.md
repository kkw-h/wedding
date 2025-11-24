# Wedding SaaS API

Backend service for the Wedding SaaS platform.

## Tech Stack

- Python 3.9+
- FastAPI
- PostgreSQL
- SQLAlchemy (ORM)
- Alembic (Migrations)

## Setup

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the server:**
    ```bash
    uvicorn main:app --reload
    ```

4.  **Access Documentation:**
    - Swagger UI: `http://127.0.0.1:8000/docs`
    - ReDoc: `http://127.0.0.1:8000/redoc`
