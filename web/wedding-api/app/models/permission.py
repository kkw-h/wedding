import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class Permission(Base):
    """
    权限定义表
    存储系统中所有可用的权限点
    """
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, index=True, nullable=False, comment="权限标识符 (e.g. 'user:manage')")
    name = Column(String, nullable=False, comment="权限名称 (e.g. '用户管理')")
    module = Column(String, nullable=False, comment="所属模块 (e.g. '系统设置')")
    description = Column(String, nullable=True, comment="详细描述")

class RolePermission(Base):
    """
    角色-权限关联表
    存储每个角色拥有的权限
    """
    __tablename__ = "role_permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String, nullable=False, index=True, comment="角色 Enum Value (e.g. 'ADMIN')")
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), nullable=False)
    
    # Relationships
    permission = relationship("Permission")
