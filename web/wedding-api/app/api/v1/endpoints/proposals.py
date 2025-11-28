from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.schemas.proposal import (
    ProposalCreate, ProposalUpdate, ProposalResponse,
    ProposalVersionCreate, ProposalVersionResponse
)
from app.crud import proposal as crud_proposal
from app.crud import project as crud_project
from app.models.user import User, RoleType
from app.models.proposal import VersionActionType

router = APIRouter()

# --- Proposal Endpoints ---

@router.post("/project/{project_id}", response_model=ProposalResponse)
def create_proposal(
    project_id: UUID,
    proposal_in: ProposalCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    为项目创建新方案 (Plan A / Plan B)。
    """
    # 1. Check Project & Permission
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager and project.lead.owner_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Ensure payload project_id matches path
    proposal_in.project_id = project_id
    
    return crud_proposal.create_proposal(db, proposal_in=proposal_in, creator_id=current_user.id)

@router.get("/project/{project_id}", response_model=List[ProposalResponse])
def read_proposals(
    project_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取项目的所有方案。
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager and project.lead.owner_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not enough permissions")
         
    return crud_proposal.get_proposals_by_project(db, project_id=project_id)

@router.get("/{proposal_id}", response_model=ProposalResponse)
def read_proposal(
    proposal_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取方案详情 (含当前草稿数据)。
    """
    proposal = crud_proposal.get_proposal(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Check Permission via Project
    project = crud_project.get_project(db, project_id=proposal.project_id)
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager and project.lead.owner_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not enough permissions")
         
    return proposal

@router.put("/{proposal_id}", response_model=ProposalResponse)
def update_proposal(
    proposal_id: UUID,
    proposal_in: ProposalUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新方案 (Auto-Save 接口)。
    前端应定时调用此接口保存 current_data。
    """
    proposal = crud_proposal.get_proposal(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
        
    project = crud_project.get_project(db, project_id=proposal.project_id)
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager and project.lead.owner_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not enough permissions")
         
    return crud_proposal.update_proposal(db, db_proposal=proposal, proposal_update=proposal_in)

# --- Version Control Endpoints ---

@router.post("/{proposal_id}/versions", response_model=ProposalVersionResponse)
def create_version(
    proposal_id: UUID,
    version_in: ProposalVersionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新版本 (Snapshot)。
    用于手动保存节点、发布等。
    """
    proposal = crud_proposal.get_proposal(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    project = crud_project.get_project(db, project_id=proposal.project_id)
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager and project.lead.owner_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not enough permissions")
    
    version_in.proposal_id = proposal_id
    return crud_proposal.create_version(db, version_in=version_in, editor_id=current_user.id)

@router.get("/{proposal_id}/versions", response_model=List[ProposalVersionResponse])
def read_versions(
    proposal_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取方案的历史版本列表。
    """
    proposal = crud_proposal.get_proposal(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    project = crud_project.get_project(db, project_id=proposal.project_id)
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager and project.lead.owner_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not enough permissions")
         
    return crud_proposal.get_versions(db, proposal_id=proposal_id, skip=skip, limit=limit)

@router.post("/{proposal_id}/restore/{version_id}", response_model=ProposalResponse)
def restore_version(
    proposal_id: UUID,
    version_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    恢复到指定版本。
    Current Draft (current_data) 将被覆盖。
    """
    proposal = crud_proposal.get_proposal(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
        
    version = crud_proposal.get_version(db, version_id=version_id)
    if not version or version.proposal_id != proposal_id:
        raise HTTPException(status_code=404, detail="Version not found")
        
    project = crud_project.get_project(db, project_id=proposal.project_id)
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager and project.lead.owner_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not enough permissions")

    # Restore logic: Update Proposal.current_data = Version.snapshot_data
    update_data = ProposalUpdate(current_data=version.snapshot_data)
    
    # Optional: Log this restore as a new version or just update current?
    # Requirement: "Overwrite current draft".
    # We just update current_data.
    
    return crud_proposal.update_proposal(db, db_proposal=proposal, proposal_update=update_data)
