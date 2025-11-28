from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate, LeadPagination
from app.crud import lead as crud_lead
from app.models.user import User, RoleType

router = APIRouter()

@router.get("/", response_model=LeadPagination)
def read_leads(
    db: Session = Depends(deps.get_db),
    page: int = 1,
    size: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取线索列表。
    - ADMIN/MANAGER: 获取所有线索
    - PLANNER: 仅获取自己负责的线索
    """
    owner_id = None
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager:
        owner_id = current_user.id
        
    skip = (page - 1) * size
    
    leads = crud_lead.get_leads(db, skip=skip, limit=size, owner_id=owner_id, status=status, keyword=keyword)
    total = crud_lead.count_leads(db, owner_id=owner_id, status=status, keyword=keyword)
    
    return {"total": total, "list": leads}

@router.post("/", response_model=LeadResponse)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新线索。
    自动检测手机号冲突。
    """
    # 1. Check Conflict
    existing_lead = crud_lead.get_lead_by_phone(db, phone=lead_in.phone)
    if existing_lead:
        # 简单冲突检测，实际业务可能需要返回 conflict: true
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lead with this phone already exists."
        )

    # 2. Create
    # 如果是 Planner 创建，默认归属自己；Admin/Manager 创建如果不指定则可能归公海(这里简化为归属创建者)
    owner_id = current_user.id 
    return crud_lead.create_lead(db, lead=lead_in, owner_id=owner_id)

@router.get("/{lead_id}", response_model=LeadResponse)
def read_lead(
    lead_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取特定线索详情。
    """
    lead = crud_lead.get_lead(db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Permission Check
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager and lead.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return lead

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    删除线索。
    """
    lead = crud_lead.get_lead(db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # Permission Check
    # Only Admin or Manager can delete
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
        
    crud_lead.delete_lead(db, lead_id=lead_id)
    return None
