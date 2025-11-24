from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.schemas.approval import ApprovalCreate, ApprovalResponse, ApprovalUpdate
from app.crud import approval as crud_approval
from app.crud import project as crud_project
from app.models.user import User, RoleType
from app.models.approval import ApprovalStatus

router = APIRouter()

@router.get("/", response_model=List[ApprovalResponse])
def read_approvals(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status_filter: ApprovalStatus = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取审批列表。
    - PLANNER: 仅看自己发起的
    - MANAGER/ADMIN: 看所有
    """
    requester_id = None
    if current_user.role == RoleType.PLANNER:
        requester_id = current_user.id
        
    approvals = crud_approval.get_approvals(
        db, skip=skip, limit=limit, requester_id=requester_id, status=status_filter
    )
    return approvals

@router.post("/", response_model=ApprovalResponse)
def create_approval(
    approval_in: ApprovalCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    发起审批。
    """
    # Check Project Existence
    project = crud_project.get_project(db, project_id=approval_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Permission: Planner must own project
    if current_user.role == RoleType.PLANNER and project.lead.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return crud_approval.create_approval(db, approval_in=approval_in, requester_id=current_user.id)

@router.put("/{approval_id}/process", response_model=ApprovalResponse)
def process_approval(
    approval_id: UUID,
    approval_in: ApprovalUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    审批处理 (通过/驳回)。
    - 仅 MANAGER/ADMIN 可操作
    """
    if current_user.role not in [RoleType.MANAGER, RoleType.ADMIN]:
        raise HTTPException(status_code=403, detail="Only managers can process approvals")
        
    approval = crud_approval.get_approval(db, approval_id=approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Approval already processed")
        
    return crud_approval.update_approval(
        db, db_approval=approval, approval_update=approval_in, approver_id=current_user.id
    )
