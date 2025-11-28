import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Enum, JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class ProposalStatus(str, enum.Enum):
    DRAFT = "DRAFT"         # 草稿
    ACTIVE = "ACTIVE"       # 进行中/活跃
    SELECTED = "SELECTED"   # 已定稿 (被选中的方案)
    ARCHIVED = "ARCHIVED"   # 已归档 (备选或废弃)

class VersionActionType(str, enum.Enum):
    AUTO_SAVE = "AUTO_SAVE"     # 自动保存
    MANUAL_SAVE = "MANUAL_SAVE" # 手动保存
    PUBLISH = "PUBLISH"         # 发布/发给客户

class VersionChangeType(str, enum.Enum):
    MAJOR = "MAJOR"  # 重大修改
    MINOR = "MINOR"  # 微调

class Proposal(Base):
    """
    策划方案表 (proposals)
    一个项目可以有多个方案 (Plan A, Plan B)
    """
    __tablename__ = "proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="方案ID")
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, comment="所属项目ID")
    
    name = Column(String, nullable=False, comment="方案名称 (如: 森系方案A)")
    description = Column(Text, nullable=True, comment="方案描述/备注")
    status = Column(Enum(ProposalStatus), default=ProposalStatus.DRAFT, nullable=False, comment="方案状态")
    
    # 当前的工作副本数据 (Latest Working Copy)
    # 前端实时编辑保存到这里，避免每次都生成 Version
    current_data = Column(JSON, nullable=True, comment="当前编辑内容快照")
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, comment="创建人")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="最后更新时间")

    # Relationships
    project = relationship("Project", back_populates="proposals")
    versions = relationship("ProposalVersion", back_populates="proposal", cascade="all, delete-orphan", order_by="desc(ProposalVersion.created_at)")
    creator = relationship("User", back_populates="proposals_created")


class ProposalVersion(Base):
    """
    方案版本历史表 (proposal_versions)
    """
    __tablename__ = "proposal_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="版本ID")
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("proposals.id"), nullable=False, comment="所属方案ID")
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey("proposal_versions.id"), nullable=True, comment="父版本ID")
    
    # 核心数据
    snapshot_data = Column(JSON, nullable=False, comment="版本全量快照数据")
    change_log = Column(JSON, nullable=True, comment="修改摘要 (如: {'diff': 'Deleted flower wall'})")
    
    # 版本元信息
    action_type = Column(Enum(VersionActionType), default=VersionActionType.MANUAL_SAVE, nullable=False, comment="保存类型")
    change_type = Column(Enum(VersionChangeType), default=VersionChangeType.MINOR, nullable=False, comment="修改类型")
    version_number = Column(String, nullable=False, default="1.0", comment="版本号")
    
    editor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, comment="修改人/版本提交人")
    created_at = Column(DateTime, default=datetime.utcnow, comment="版本生成时间")

    # Relationships
    proposal = relationship("Proposal", back_populates="versions")
    editor = relationship("User", back_populates="proposal_versions_edited")
