from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.project import ProjectStage

class ProjectBase(BaseModel):
    name: str
    wedding_date: date
    hotel_name: Optional[str] = None
    total_budget: Optional[float] = 0

class ProjectCreate(ProjectBase):
    lead_id: UUID

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    wedding_date: Optional[date] = None
    hotel_name: Optional[str] = None
    total_budget: Optional[float] = None
    stage: Optional[ProjectStage] = None

class ProjectResponse(ProjectBase):
    id: UUID
    lead_id: UUID
    stage: ProjectStage
    
    model_config = ConfigDict(from_attributes=True)
