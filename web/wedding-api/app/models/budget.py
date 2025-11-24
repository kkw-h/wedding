import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class BudgetItem(Base):
    """
    报价单明细表 (budget_items)
    存储具体的服务或物料项。
    **敏感数据说明**: 
    普通策划师 (PLANNER) 只能看到 unit_price (销售价)，
    严禁向其返回 cost_price (成本价)。
    """
    __tablename__ = "budget_items"

    # 基础信息
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="明细项ID")
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, comment="所属项目ID")
    
    # 物料详情
    category = Column(String, nullable=False, comment="分类 (如: 鲜花, 灯光, 人员, 搭建)")
    name = Column(String, nullable=False, comment="项目名称 (如: 进口红玫瑰, 主持人)")
    
    # 价格体系
    unit_price = Column(Numeric(10, 2), default=0, comment="销售单价 (对客价) - 策划师可见")
    cost_price = Column(Numeric(10, 2), default=0, comment="成本单价 (内部价) - 仅Admin/Manager可见")
    
    # 数量与供应商
    quantity = Column(Integer, default=1, comment="数量")
    supplier_id = Column(UUID(as_uuid=True), nullable=True, comment="关联供应商ID (用于自动结算)")
    
    # 状态
    is_locked = Column(Boolean, default=False, comment="是否已锁定 (审批通过后不可修改)")

    # 关系定义 (ORM)
    project = relationship("Project", back_populates="budget_items", doc="所属项目")