from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from app.crud import lead as crud_lead
from app.models.user import User, RoleType

router = APIRouter()

@router.get("/", response_model=List[LeadResponse])
def read_leads(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取线索列表。
    - ADMIN/MANAGER: 获取所有线索
    - PLANNER: 仅获取自己负责的线索
    """
    owner_id = None
    if current_user.role == RoleType.PLANNER:
        owner_id = current_user.id
        
    leads = crud_lead.get_leads(db, skip=skip, limit=limit, owner_id=owner_id)
    return leads

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
    if current_user.role == RoleType.PLANNER and lead.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return lead
