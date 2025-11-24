import io
from minio import Minio
from minio.error import S3Error
from app.config import settings

class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET_NAME
        # self._ensure_bucket()  # Don't check on import to avoid breaking tests if MinIO is down

    def _ensure_bucket(self):
        """Ensure the bucket exists, create if not."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except Exception as e:
            print(f"MinIO Bucket Check Error: {e}")

    def upload_file(self, file_data: bytes, filename: str, content_type: str) -> str:
        """
        Uploads a file to MinIO and returns the object key.
        """
        # Create a unique key (e.g., date/uuid-filename)
        import uuid
        from datetime import datetime
        
        # Ensure bucket exists before first upload
        # (Optimistic approach: try upload, if fail, check bucket? Or just check once?)
        # For now, let's just try to ensure it exists here, but catch errors safely.
        # Ideally this should be done in a startup event, not per request.
        # But for simplicity in this MVP:
        # self._ensure_bucket() 
        
        # 简单的目录结构: YYYY/MM/uuid.ext
        now = datetime.utcnow()
        ext = filename.split('.')[-1] if '.' in filename else ""
        key = f"{now.year}/{now.month:02d}/{uuid.uuid4()}.{ext}"

        try:
            self.client.put_object(
                self.bucket,
                key,
                io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type
            )
            return key
        except S3Error as e:
            print(f"Failed to upload: {e}")
            raise e

    def get_url(self, key: str) -> str:
        """
        Generates the URL for the file.
        If ASSET_URL_PREFIX is set, uses that.
        Otherwise constructs from MinIO endpoint.
        """
        if settings.ASSET_URL_PREFIX:
            # 去除末尾斜杠
            base = settings.ASSET_URL_PREFIX.rstrip("/")
            return f"{base}/{self.bucket}/{key}"
        
        # 默认 MinIO URL
        protocol = "https" if settings.MINIO_SECURE else "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{self.bucket}/{key}"

storage = StorageService()
