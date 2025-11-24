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

# Default Role -> Permissions Mapping (for initialization)
DEFAULT_ROLE_PERMISSIONS: Dict[RoleType, List[str]] = {
    RoleType.ADMIN: [
        Permissions.DASHBOARD_VIEW_KPI,
        Permissions.LEAD_VIEW_ALL, Permissions.LEAD_CREATE, Permissions.LEAD_EDIT, Permissions.LEAD_ASSIGN,
        Permissions.PROJECT_VIEW_ALL, Permissions.PROJECT_EDIT_ALL,
        Permissions.BUDGET_VIEW_COST, Permissions.BUDGET_VIEW_PROFIT, Permissions.BUDGET_APPROVE,
        Permissions.FINANCE_MANAGE,
        Permissions.USER_MANAGE, Permissions.SYSTEM_SETTINGS
    ],
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
    defined_permissions = []
    for name, code in vars(Permissions).items():
        if name.isupper():
            module = code.split(":")[0] if ":" in code else "common"
            defined_permissions.append({"code": code, "module": module, "name": code}) # Name can be improved

    perm_map = {}
    for p_data in defined_permissions:
        perm = db.query(Permission).filter(Permission.code == p_data["code"]).first()
        if not perm:
            perm = Permission(code=p_data["code"], module=p_data["module"], name=p_data["name"])
            db.add(perm)
            db.flush()
        perm_map[p_data["code"]] = perm.id
    
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