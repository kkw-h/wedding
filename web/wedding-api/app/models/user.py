import uuid
import enum
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class RoleType(str, enum.Enum):
    """
    用户角色枚举
    用于控制系统权限 (RBAC)
    """
    ADMIN = "ADMIN"       # 超级管理员：拥有所有权限，可查看成本、毛利、所有数据
    MANAGER = "MANAGER"   # 团队经理/店长：管理团队线索，审批折扣，查看团队业绩
    PLANNER = "PLANNER"   # 策划师：核心作业人员，仅查看自己负责的线索/项目，成本数据脱敏
    VENDOR = "VENDOR"     # 供应商/外部人员：仅查看分配的任务排期，权限最低
    FINANCE = "FINANCE"   # 财务：负责收付款确认，工资结算

class UserRole(Base):
    """
    用户-角色关联表 (Many-to-Many 实现)
    """
    __tablename__ = "user_roles"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(String, primary_key=True, nullable=False)

class User(Base):
    """
    用户表 (users)
    存储系统所有登录用户的信息
    """
    __tablename__ = "users"

    # 核心字段
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="用户唯一ID")
    username = Column(String, unique=True, index=True, comment="登录用户名")
    password_hash = Column(String, comment="加密后的密码哈希值")
    
    # 权限控制 (Deprecated single role column, moving to user_roles relationship)
    # role = Column(Enum(RoleType), nullable=False, comment="用户角色，决定权限范围") # Removing this
    
    # 组织架构
    team_id = Column(UUID(as_uuid=True), nullable=True, comment="所属团队/门店ID (外键)")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="账户是否激活，False表示已禁用")

    # 关系定义 (ORM)
    roles = relationship("UserRole", backref="user", cascade="all, delete-orphan")
    
    leads = relationship("Lead", back_populates="owner", doc="该用户负责的所有线索")
    
    # 审批流相关关系
    approvals_requested = relationship(
        "Approval", 
        foreign_keys="[Approval.requester_id]", 
        back_populates="requester",
        doc="该用户发起的所有审批"
    )
    approvals_reviewed = relationship(
        "Approval", 
        foreign_keys="[Approval.approver_id]", 
        back_populates="approver",
        doc="该用户审核过的所有审批"
    )

    # 方案策划相关
    proposals_created = relationship(
        "Proposal",
        back_populates="creator",
        doc="该用户创建的方案"
    )
    proposal_versions_edited = relationship(
        "ProposalVersion",
        back_populates="editor",
        doc="该用户提交的方案版本"
    )

    @property
    def role_list(self):
        """
        获取用户角色列表 (List[str])
        """
        return [r.role for r in self.roles]

    @property
    def permissions(self):
        """
        动态获取该用户的具体权限列表 (合并所有角色)
        """
        from app.core.permissions import get_role_permissions
        from app.database import SessionLocal 
        db = SessionLocal()
        try:
            all_perms = set()
            for user_role in self.roles:
                # user_role.role is a string
                try:
                    role_enum = RoleType(user_role.role)
                    perms = get_role_permissions(db, role_enum)
                    all_perms.update(perms)
                except ValueError:
                    continue # Ignore invalid roles
            return list(all_perms)
        finally:
            db.close()
            
    @property
    def role_list(self):
        """Helper to get list of role strings"""
        return [r.role for r in self.roles]