from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.crud import project as crud_project
from app.crud import lead as crud_lead
from app.models.user import User, RoleType

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取项目列表。
    - ADMIN/MANAGER: 获取所有项目
    - PLANNER: 仅获取自己负责的线索转化成的项目
    """
    owner_id = None
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    
    if not is_admin_or_manager:
        owner_id = current_user.id
        
    projects = crud_project.get_projects(db, skip=skip, limit=limit, owner_id=owner_id)
    return projects

@router.post("/", response_model=ProjectResponse)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建项目 (将线索转化为项目)。
    """
    # 1. Check Lead Existence
    lead = crud_lead.get_lead(db, lead_id=project_in.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # 2. Check Permission (Only owner or Admin/Manager can convert)
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager and lead.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to convert this lead")

    # 3. Check if Project already exists for this lead
    existing_project = crud_project.get_project_by_lead(db, lead_id=project_in.lead_id)
    if existing_project:
        raise HTTPException(status_code=400, detail="Project already created for this lead")

    # 4. Create
    return crud_project.create_project(db, project_in=project_in)

@router.get("/{project_id}", response_model=ProjectResponse)
def read_project(
    project_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取项目详情。
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Permission Check
    # Need to check the owner of the associated lead
    if current_user.role == RoleType.PLANNER:
        # We need to load the lead to check owner. 
        # Since 'lead' is a relationship, it might be lazy loaded.
        # But accessing project.lead should work if session is open.
        if project.lead.owner_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新项目信息。
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    is_admin_or_manager = any(r in [RoleType.ADMIN.value, RoleType.MANAGER.value] for r in current_user.role_list)
    if not is_admin_or_manager and project.lead.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return project.update_project(db, db_project=project, project_update=project_in)
