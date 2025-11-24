from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.project import Project
from app.models.lead import Lead, LeadStatus
from app.schemas.project import ProjectCreate, ProjectUpdate

def get_project(db: Session, project_id: UUID) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()

def get_project_by_lead(db: Session, lead_id: UUID) -> Optional[Project]:
    return db.query(Project).filter(Project.lead_id == lead_id).first()

def get_projects(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    owner_id: Optional[UUID] = None
) -> List[Project]:
    query = db.query(Project)
    if owner_id:
        # Join with Lead to filter by owner
        query = query.join(Lead).filter(Lead.owner_id == owner_id)
    return query.offset(skip).limit(limit).all()

def create_project(db: Session, project_in: ProjectCreate) -> Project:
    # 1. Create Project
    db_project = Project(
        **project_in.model_dump(),
        # Default stage is PREPARING defined in Model
    )
    db.add(db_project)
    
    # 2. Update Lead Status to WON
    # We assume validation happens before calling crud (e.g. checking lead existence)
    # But safely, we should fetch the lead and update it within the transaction.
    lead = db.query(Lead).filter(Lead.id == project_in.lead_id).first()
    if lead:
        lead.status = LeadStatus.WON
        db.add(lead)
        
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, db_project: Project, project_update: ProjectUpdate) -> Project:
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project
