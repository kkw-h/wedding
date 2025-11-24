from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.proposal import ProposalStatus, VersionActionType

# --- Version Schemas ---

class ProposalVersionBase(BaseModel):
    snapshot_data: Dict[str, Any]
    change_log: Optional[Dict[str, Any]] = None
    tag_name: Optional[str] = None
    action_type: VersionActionType = VersionActionType.MANUAL_SAVE

class ProposalVersionCreate(ProposalVersionBase):
    proposal_id: UUID
    parent_version_id: Optional[UUID] = None

class ProposalVersionResponse(ProposalVersionBase):
    id: UUID
    proposal_id: UUID
    parent_version_id: Optional[UUID] = None
    editor_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Proposal Schemas ---

class ProposalBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProposalCreate(ProposalBase):
    project_id: UUID

class ProposalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProposalStatus] = None
    current_data: Optional[Dict[str, Any]] = None

class ProposalResponse(ProposalBase):
    id: UUID
    project_id: UUID
    status: ProposalStatus
    current_data: Optional[Dict[str, Any]] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
