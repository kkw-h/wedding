import uuid
import enum
from sqlalchemy import Column, String, ForeignKey, Numeric, Date, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class ProjectStage(str, enum.Enum):
    """
    项目阶段枚举
    """
    PREPARING = "PREPARING"   # 筹备期：合同已签，正在组建团队，细化方案
    DESIGNING = "DESIGNING"   # 设计期：出设计图，改方案，确定最终效果
    EXECUTING = "EXECUTING"   # 执行期：婚礼临近，物料采购，现场搭建
    COMPLETED = "COMPLETED"   # 已完成：婚礼结束，尾款结清
    ARCHIVED = "ARCHIVED"     # 已归档：资料存档，不再变动

class Project(Base):
    """
    项目表 (projects)
    线索成交后转化而来，管理婚礼执行全过程
    """
    __tablename__ = "projects"

    # 基础信息
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="项目唯一ID")
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), unique=True, nullable=False, comment="关联的线索ID (一对一)")
    
    # 项目详情
    name = Column(String, nullable=False, comment="项目名称 (如: 张伟&王芳婚礼)")
    wedding_date = Column(Date, nullable=False, comment="最终确定的婚期")
    hotel_name = Column(String, nullable=True, comment="举办酒店名称")
    
    # 财务概览
    total_budget = Column(Numeric(10, 2), default=0, comment="合同总金额 (元)")
    
    # 状态
    stage = Column(Enum(ProjectStage), default=ProjectStage.PREPARING, nullable=False, comment="当前项目阶段")
    
    # 注意: is_presentation_mode (演示模式) 是前端状态，不需要存储在数据库中

    # 关系定义 (ORM)
    lead = relationship("Lead", back_populates="project", doc="来源线索")
    budget_items = relationship("BudgetItem", back_populates="project", doc="包含的报价单明细")
    approvals = relationship("Approval", back_populates="project", doc="关联的审批记录")
    proposals = relationship("Proposal", back_populates="project", doc="关联的策划方案")