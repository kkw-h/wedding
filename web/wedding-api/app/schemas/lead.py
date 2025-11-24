from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.lead import LeadStatus

class LeadBase(BaseModel):
    customer_name: str
    phone: str
    wedding_date: Optional[date] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    source: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    wedding_date: Optional[date] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    source: Optional[str] = None
    status: Optional[LeadStatus] = None
    owner_id: Optional[UUID] = None

class LeadResponse(LeadBase):
    id: UUID
    owner_id: Optional[UUID] = None
    last_contact_at: Optional[datetime] = None
    status: LeadStatus
    
    model_config = ConfigDict(from_attributes=True)
