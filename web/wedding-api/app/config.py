from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Wedding SaaS API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{quote_plus(self.POSTGRES_USER)}:{quote_plus(self.POSTGRES_PASSWORD)}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # JWT
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE" # Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days

    # MinIO / S3
    MINIO_ENDPOINT: str = "172.31.6.137" # IP:Port without http://
    MINIO_ACCESS_KEY: str = "demo"
    MINIO_SECRET_KEY: str = "demo12345"
    MINIO_BUCKET_NAME: str = "wedding"
    MINIO_SECURE: bool = False # False for http, True for https
    
    # Public URL Prefix (Useful if behind Nginx/Proxy)
    # If empty, will use http://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}
    ASSET_URL_PREFIX: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()