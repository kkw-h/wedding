import uuid
import enum
from sqlalchemy import Column, String, ForeignKey, Numeric, TIMESTAMP, Date, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class LeadStatus(str, enum.Enum):
    """
    线索状态枚举
    描述客户从录入到成交/流失的全生命周期
    """
    NEW = "NEW"                 # 新录入：刚创建，尚未联系
    CONTACTING = "CONTACTING"   # 跟进中：已建立联系，正在沟通需求
    VISITED = "VISITED"         # 已进店：客户已到店面谈
    INTENTIONAL = "INTENTIONAL" # 有意向：客户表达了明确合作意向，正在出方案
    WON = "WON"                 # 已成交：签订合同，转化为项目 (Project)
    LOST = "LOST"               # 已流失：客户明确拒绝或无效
    PUBLIC_POOL = "PUBLIC_POOL" # 公海池：长期未跟进自动掉入，或手动放弃，可被其他人捞取

class Lead(Base):
    """
    线索表 (leads)
    CRM 核心表，存储潜在客户信息
    """
    __tablename__ = "leads"

    # 基础信息
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="线索唯一ID")
    customer_name = Column(String, nullable=False, comment="客户姓名")
    phone = Column(String, unique=True, index=True, nullable=False, comment="手机号 (唯一标识，用于查重)")
    wedding_date = Column(Date, nullable=True, comment="预计婚期")
    
    # 预算范围
    budget_min = Column(Numeric(10, 2), nullable=True, comment="最低预算 (元)")
    budget_max = Column(Numeric(10, 2), nullable=True, comment="最高预算 (元)")
    
    # 归属与状态
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, comment="当前负责人ID (为空表示在公海)")
    last_contact_at = Column(TIMESTAMP, nullable=True, comment="最后跟进时间 (用于判定是否掉入公海)")
    source = Column(String, nullable=True, comment="线索来源 (如: 小红书, 转介绍, 门店自然到访)")
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False, comment="当前线索状态")

    # 关系定义 (ORM)
    owner = relationship("User", back_populates="leads", doc="该线索的负责人")
    project = relationship("Project", back_populates="lead", uselist=False, doc="关联的项目 (成交后生成)")