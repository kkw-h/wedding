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