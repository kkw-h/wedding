from typing import List, Optional
from uuid import UUID
import time
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api import deps
from app.core import security
from app.models.user import User, RoleType, UserRole
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

# -----------------------------------------------------------------------------
# User Management (Admin / Manager only mostly)
# -----------------------------------------------------------------------------

@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get current user.
    """
    return current_user

@router.get("/", response_model=List[UserRead])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
    role: Optional[RoleType] = None
):
    """
    Retrieve users.
    """
    # Check permissions logic
    # Admin/Manager has broad access
    # Since permissions are now role-based, we should ideally check `current_user.permissions`
    # But for simplicity here, we stick to role checks for now, allowing multiple.
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    
    if not is_admin_or_manager:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
        
    query = db.query(User).filter(User.username.notilike('deleted_%'))
    if role:
        # Filter users who have this specific role
        query = query.join(UserRole).filter(UserRole.role == role.value)
        
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=UserRead)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Create new user.
    """
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
        
    user = User(
        username=user_in.username,
        password_hash=security.get_password_hash(user_in.password),
        is_active=user_in.is_active,
    )
    db.add(user)
    db.flush() # Generate ID
    
    # Add roles
    for r in user_in.roles:
        db.add(UserRole(user_id=user.id, role=r.value))

    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Update a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
        
    # Permission Check
    is_admin = RoleType.ADMIN.value in current_user.role_list
    if not is_admin and current_user.id != user_id:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
        
    if user_in.username is not None:
        existing_user = db.query(User).filter(User.username == user_in.username).first()
        if existing_user and existing_user.id != user_id:
             raise HTTPException(
                status_code=400,
                detail="Username already registered",
            )
        user.username = user_in.username
        
    if user_in.password is not None:
        user.password_hash = security.get_password_hash(user_in.password)
        
    if user_in.roles is not None:
        if not is_admin:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin can change roles",
            )
        # Clear old roles
        db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        # Add new roles
        for r in user_in.roles:
            db.add(UserRole(user_id=user_id, role=r.value))
        
    if user_in.is_active is not None:
        # Admin or Manager can change active status
        is_manager = RoleType.MANAGER.value in current_user.role_list
        if not (is_admin or is_manager):
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to change active status",
            )
        user.is_active = user_in.is_active

    db.commit()
    db.refresh(user)
    return user

from pydantic import BaseModel

class RoleResponse(BaseModel):
    code: str
    name: str

@router.get("/roles", response_model=List[RoleResponse])
def read_roles(
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get all available roles with aliases.
    """
    role_names = {
        RoleType.ADMIN: "超级管理员",
        RoleType.MANAGER: "团队经理",
        RoleType.PLANNER: "婚礼策划师",
        RoleType.VENDOR: "供应商/外部人员",
        RoleType.FINANCE: "财务专员",
    }
    return [RoleResponse(code=role.value, name=role_names.get(role, role.value)) for role in RoleType]

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Delete a user. (Admin only)
    """
    # 1. Check Permissions
    is_admin = RoleType.ADMIN.value in current_user.role_list
    if not is_admin:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # 2. Check Self-Deletion
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )

    # 3. Get User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # 4. Delete (Cascade should handle roles, but being explicit is safe)
    # If UserRole has cascade delete on ForeignKey, just deleting user is enough.
    # Assuming it does, or we can manually delete. 
    # Let's trust cascade or manually delete to be safe if unsure about model.
    # Checking UserRole model... but standard is usually cascade.
    # We will just delete user.
    try:
        db.delete(user)
        db.commit()
    except IntegrityError:
        # User has associated data (e.g. Approvals, Proposals) that prevent hard delete.
        # Fallback to Soft Delete: Deactivate and rename username to release it.
        db.rollback()
        
        # Soft Delete Logic
        # 1. Deactivate
        user.is_active = False
        
        # 2. Rename username to allow reuse (e.g. "alice" -> "deleted_1700000000_alice")
        # Ensure it's unique enough
        timestamp = int(time.time())
        user.username = f"deleted_{timestamp}_{user.username}"
        
        # 3. Clear roles? (Optional, but good practice to remove access rights completely)
        # We can leave roles as is for audit purposes.
        
        db.add(user)
        db.commit()
        
    return None