import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class Asset(Base):
    """
    资源文件表 (assets)
    存储上传到 MinIO/S3 的文件元数据
    """
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="资源ID")
    
    # 文件元信息
    filename = Column(String, nullable=False, comment="原始文件名")
    file_key = Column(String, unique=True, nullable=False, comment="MinIO存储键 (如: uploader/uuid.jpg)")
    content_type = Column(String, nullable=False, comment="MIME类型")
    size = Column(Integer, comment="文件大小 (bytes)")
    
    # 审计
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, comment="上传人")
    created_at = Column(DateTime, default=datetime.utcnow, comment="上传时间")

    # Relationships
    uploader = relationship("User", backref="uploaded_assets")