from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.user import RoleType
from app.models.permission import Permission, RolePermission

# Permission Constants
class Permissions:
    # Dashboard
    DASHBOARD_VIEW_KPI = "dashboard:view_kpi"          # See company revenue, profit
    DASHBOARD_VIEW_TEAM = "dashboard:view_team"        # See team performance
    DASHBOARD_VIEW_PERSONAL = "dashboard:view_personal"# See own tasks
    
    # Leads (CRM)
    LEAD_VIEW_ALL = "lead:view_all"
    LEAD_VIEW_TEAM = "lead:view_team"
    LEAD_VIEW_OWN = "lead:view_own"
    LEAD_CREATE = "lead:create"
    LEAD_EDIT = "lead:edit"
    LEAD_DELETE = "lead:delete"
    LEAD_ASSIGN = "lead:assign"
    
    # Projects
    PROJECT_VIEW_ALL = "project:view_all"
    PROJECT_VIEW_TEAM = "project:view_team"
    PROJECT_VIEW_OWN = "project:view_own"
    PROJECT_EDIT_ALL = "project:edit_all"
    PROJECT_EDIT_OWN = "project:edit_own"
    
    # Budget & Finance
    BUDGET_VIEW_COST = "budget:view_cost"      # See cost price
    BUDGET_VIEW_PROFIT = "budget:view_profit"  # See profit margin
    BUDGET_APPROVE = "budget:approve"          # Approve discounts/refunds
    FINANCE_MANAGE = "finance:manage"          # AP/AR management
    
    # Users & Settings
    USER_MANAGE = "user:manage"                # Create/Edit users
    SYSTEM_SETTINGS = "system:settings"        # Global configs

# Detailed Information for Permissions
PERMISSION_DETAILS = {
    Permissions.DASHBOARD_VIEW_KPI: {"name": "查看KPI报表", "description": "允许查看公司营收、利润等核心经营指标数据"},
    Permissions.DASHBOARD_VIEW_TEAM: {"name": "查看团队报表", "description": "允许查看团队成员的工作绩效和统计数据"},
    Permissions.DASHBOARD_VIEW_PERSONAL: {"name": "查看个人报表", "description": "允许查看个人的工作任务和绩效统计"},
    
    Permissions.LEAD_VIEW_ALL: {"name": "查看所有线索", "description": "允许查看系统中的所有销售线索"},
    Permissions.LEAD_VIEW_TEAM: {"name": "查看团队线索", "description": "允许查看所属团队成员的销售线索"},
    Permissions.LEAD_VIEW_OWN: {"name": "查看个人线索", "description": "仅允许查看分配给自己的销售线索"},
    Permissions.LEAD_CREATE: {"name": "创建线索", "description": "允许录入新的销售线索"},
    Permissions.LEAD_EDIT: {"name": "编辑线索", "description": "允许修改线索的详细信息"},
    Permissions.LEAD_DELETE: {"name": "删除线索", "description": "允许删除线索"},
    Permissions.LEAD_ASSIGN: {"name": "分配线索", "description": "允许将线索分配给其他人员"},
    
    Permissions.PROJECT_VIEW_ALL: {"name": "查看所有项目", "description": "允许查看系统中的所有婚礼项目"},
    Permissions.PROJECT_VIEW_TEAM: {"name": "查看团队项目", "description": "允许查看所属团队成员负责的婚礼项目"},
    Permissions.PROJECT_VIEW_OWN: {"name": "查看个人项目", "description": "仅允许查看自己负责的婚礼项目"},
    Permissions.PROJECT_EDIT_ALL: {"name": "编辑所有项目", "description": "允许修改任意项目的信息"},
    Permissions.PROJECT_EDIT_OWN: {"name": "编辑个人项目", "description": "仅允许修改自己负责的项目信息"},
    
    Permissions.BUDGET_VIEW_COST: {"name": "查看成本价", "description": "允许查看项目和服务项目的成本价格"},
    Permissions.BUDGET_VIEW_PROFIT: {"name": "查看利润率", "description": "允许查看项目和服务项目的利润分析"},
    Permissions.BUDGET_APPROVE: {"name": "审批预算", "description": "允许审批项目预算、折扣和退款申请"},
    Permissions.FINANCE_MANAGE: {"name": "财务管理", "description": "允许进行应收应付管理、发票开具等财务操作"},
    
    Permissions.USER_MANAGE: {"name": "用户管理", "description": "允许创建、编辑和禁用系统用户账号"},
    Permissions.SYSTEM_SETTINGS: {"name": "系统设置", "description": "允许修改全局系统配置参数"},
}

# Default Role -> Permissions Mapping (for initialization)
DEFAULT_ROLE_PERMISSIONS: Dict[RoleType, List[str]] = {
    RoleType.ADMIN: list(PERMISSION_DETAILS.keys()),
    RoleType.MANAGER: [
        Permissions.DASHBOARD_VIEW_TEAM,
        Permissions.LEAD_VIEW_TEAM, Permissions.LEAD_CREATE, Permissions.LEAD_EDIT, Permissions.LEAD_ASSIGN,
        Permissions.PROJECT_VIEW_TEAM, Permissions.PROJECT_EDIT_ALL, 
        Permissions.BUDGET_VIEW_COST, Permissions.BUDGET_VIEW_PROFIT, Permissions.BUDGET_APPROVE,
    ],
    RoleType.PLANNER: [
        Permissions.DASHBOARD_VIEW_PERSONAL,
        Permissions.LEAD_VIEW_OWN, Permissions.LEAD_CREATE, Permissions.LEAD_EDIT,
        Permissions.PROJECT_VIEW_OWN, Permissions.PROJECT_EDIT_OWN,
    ],
    RoleType.FINANCE: [
        Permissions.DASHBOARD_VIEW_KPI, # Maybe limited view
        Permissions.BUDGET_VIEW_COST,
        Permissions.FINANCE_MANAGE,
    ],
    RoleType.VENDOR: [
        Permissions.PROJECT_VIEW_OWN, # Only assigned tasks
    ]
}

def sync_permissions(db: Session):
    """
    Sync constants to Database (Idempotent)
    """
    # 1. Sync Definitions
    for code, details in PERMISSION_DETAILS.items():
        module = code.split(":")[0] if ":" in code else "common"
        name = details["name"]
        description = details["description"]
        
        perm = db.query(Permission).filter(Permission.code == code).first()
        if not perm:
            perm = Permission(code=code, module=module, name=name, description=description)
            db.add(perm)
        else:
            # Update existing details
            perm.name = name
            perm.description = description
            perm.module = module
            db.add(perm)
            
    db.flush()
    
    # Map codes to IDs for role assignment
    perm_map = {p.code: p.id for p in db.query(Permission).all()}
    
    # 2. Sync Default Role Mappings (Only if role has NO permissions yet, to avoid overwriting custom configs)
    for role, codes in DEFAULT_ROLE_PERMISSIONS.items():
        existing = db.query(RolePermission).filter(RolePermission.role == role.value).first()
        if not existing:
            for code in codes:
                if code in perm_map:
                    rp = RolePermission(role=role.value, permission_id=perm_map[code])
                    db.add(rp)
    
    db.commit()

def get_role_permissions(db: Session, role: RoleType) -> List[str]:
    """
    Fetch permissions for a role from DB
    """
    results = db.query(Permission.code)\
                .join(RolePermission, RolePermission.permission_id == Permission.id)\
                .filter(RolePermission.role == role.value)\
                .all()
    return [r[0] for r in results]