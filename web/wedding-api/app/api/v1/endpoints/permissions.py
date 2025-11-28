from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from app.api import deps
from app.core import permissions
from app.models.user import User, RoleType, UserRole
from app.models.permission import Permission, RolePermission

router = APIRouter()

class PermissionRead(BaseModel):
    id: UUID
    code: str
    name: str
    module: str
    description: str | None = None
    
    class Config:
        from_attributes = True

@router.post("/sync", status_code=200)
def sync_permissions_db(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Force sync permissions from code to DB. (Admin only)
    """
    if RoleType.ADMIN.value not in current_user.role_list:
         raise HTTPException(status_code=403, detail="Not authorized")
    
    permissions.sync_permissions(db)
    return {"message": "Permissions synced successfully"}

@router.get("/", response_model=List[PermissionRead])
def list_permissions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    if RoleType.ADMIN.value not in current_user.role_list:
         raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(Permission).all()

@router.get("/matrix", response_model=dict[str, List[str]])
def get_permission_matrix(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get all role permissions: { "ADMIN": ["p1", "p2"], ... }
    """
    if RoleType.ADMIN.value not in current_user.role_list:
         raise HTTPException(status_code=403, detail="Not authorized")
         
    results = db.query(RolePermission.role, Permission.code)\
                .join(Permission, RolePermission.permission_id == Permission.id)\
                .all()
    
    matrix = {}
    for role, code in results:
        if role not in matrix:
            matrix[role] = []
        matrix[role].append(code)
    return matrix

@router.put("/roles/{role_code}", status_code=200)
def update_role_permissions(
    role_code: str,
    permission_codes: List[str],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Update permissions for a specific role.
    """
    if RoleType.ADMIN.value not in current_user.role_list:
         raise HTTPException(status_code=403, detail="Not authorized")
         
    # Validate role
    try:
        RoleType(role_code)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role code")
        
    # Get Permission IDs
    perms = db.query(Permission).filter(Permission.code.in_(permission_codes)).all()
    if len(perms) != len(permission_codes):
         # Some codes might be invalid, but we can just use the valid ones or strict check
         pass 

    # Transaction
    # 1. Delete existing
    db.query(RolePermission).filter(RolePermission.role == role_code).delete()
    
    # 2. Insert new
    for p in perms:
        db.add(RolePermission(role=role_code, permission_id=p.id))
        
    db.commit()
    return {"message": "Permissions updated"}