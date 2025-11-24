import uuid
import enum
from sqlalchemy import Column, ForeignKey, Enum, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class ApprovalType(str, enum.Enum):
    """
    审批类型枚举
    """
    DISCOUNT = "DISCOUNT" # 折扣申请：申请低于底价的折扣
    PAYMENT = "PAYMENT"   # 付款申请：申请支付供应商款项
    REFUND = "REFUND"     # 退款申请：客户退单退款

class ApprovalStatus(str, enum.Enum):
    """
    审批状态枚举
    """
    PENDING = "PENDING"   # 待审批
    APPROVED = "APPROVED" # 已通过
    REJECTED = "REJECTED" # 已驳回

class Approval(Base):
    """
    审批流水表 (approvals)
    记录所有需要上级确认的操作
    """
    __tablename__ = "approvals"

    # 基础信息
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="审批单ID")
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, comment="关联项目ID")
    
    # 人员
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, comment="申请人ID")
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, comment="审批人ID (处理后填充)")
    
    # 内容
    type = Column(Enum(ApprovalType), nullable=False, comment="审批类型")
    current_data = Column(JSON, nullable=True, comment="申请时的快照数据 (如: 申请时的折扣金额、原价等)")
    
    # 结果
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False, comment="当前状态")
    audit_log = Column(Text, nullable=True, comment="审批日志/备注 (如: 驳回原因)")

    # 关系定义 (ORM)
    project = relationship("Project", back_populates="approvals", doc="关联项目")
    requester = relationship("User", foreign_keys=[requester_id], back_populates="approvals_requested", doc="申请人")
    approver = relationship("User", foreign_keys=[approver_id], back_populates="approvals_reviewed", doc="审批人")