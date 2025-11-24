from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.models.user import User, RoleType, UserRole
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

# -----------------------------------------------------------------------------
# User Management (Admin / Manager only mostly)
# -----------------------------------------------------------------------------

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
        
    query = db.query(User)
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

@router.get("/roles", response_model=List[str])
def read_roles(
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get all available roles.
    """
    return [role.value for role in RoleType]