from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.approval import ApprovalType, ApprovalStatus

class ApprovalBase(BaseModel):
    project_id: UUID
    type: ApprovalType
    current_data: Optional[Dict[str, Any]] = None

class ApprovalCreate(ApprovalBase):
    pass

class ApprovalUpdate(BaseModel):
    status: ApprovalStatus
    audit_log: Optional[str] = None

class ApprovalResponse(ApprovalBase):
    id: UUID
    requester_id: UUID
    approver_id: Optional[UUID] = None
    status: ApprovalStatus
    audit_log: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
