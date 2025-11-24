from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.approval import Approval, ApprovalStatus
from app.schemas.approval import ApprovalCreate, ApprovalUpdate

def get_approval(db: Session, approval_id: UUID) -> Optional[Approval]:
    return db.query(Approval).filter(Approval.id == approval_id).first()

def get_approvals(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    requester_id: Optional[UUID] = None,
    status: Optional[ApprovalStatus] = None
) -> List[Approval]:
    query = db.query(Approval)
    if requester_id:
        query = query.filter(Approval.requester_id == requester_id)
    if status:
        query = query.filter(Approval.status == status)
    return query.offset(skip).limit(limit).all()

def create_approval(db: Session, approval_in: ApprovalCreate, requester_id: UUID) -> Approval:
    db_approval = Approval(
        **approval_in.model_dump(),
        requester_id=requester_id,
        status=ApprovalStatus.PENDING
    )
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    return db_approval

def update_approval(
    db: Session, 
    db_approval: Approval, 
    approval_update: ApprovalUpdate, 
    approver_id: UUID
) -> Approval:
    db_approval.status = approval_update.status
    db_approval.audit_log = approval_update.audit_log
    db_approval.approver_id = approver_id
    
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    return db_approval
