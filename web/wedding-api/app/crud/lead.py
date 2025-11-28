from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import LeadCreate, LeadUpdate

def get_lead(db: Session, lead_id: UUID) -> Optional[Lead]:
    return db.query(Lead).filter(Lead.id == lead_id).first()

def get_lead_by_phone(db: Session, phone: str) -> Optional[Lead]:
    return db.query(Lead).filter(Lead.phone == phone).first()

def get_leads(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    owner_id: Optional[UUID] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None
) -> List[Lead]:
    query = db.query(Lead)
    if owner_id:
        query = query.filter(Lead.owner_id == owner_id)
    if status:
        query = query.filter(Lead.status == status)
    if keyword:
        # Search in customer_name or phone
        query = query.filter((Lead.customer_name.ilike(f"%{keyword}%")) | (Lead.phone.ilike(f"%{keyword}%")))
        
    return query.offset(skip).limit(limit).all()

def count_leads(
    db: Session,
    owner_id: Optional[UUID] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None
) -> int:
    query = db.query(Lead)
    if owner_id:
        query = query.filter(Lead.owner_id == owner_id)
    if status:
        query = query.filter(Lead.status == status)
    if keyword:
        query = query.filter((Lead.customer_name.ilike(f"%{keyword}%")) | (Lead.phone.ilike(f"%{keyword}%")))
    return query.count()

def create_lead(db: Session, lead: LeadCreate, owner_id: Optional[UUID] = None) -> Lead:
    db_lead = Lead(
        **lead.model_dump(),
        owner_id=owner_id,
        status=LeadStatus.NEW if owner_id else LeadStatus.PUBLIC_POOL
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def update_lead(db: Session, db_lead: Lead, lead_update: LeadUpdate) -> Lead:
    update_data = lead_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lead, key, value)
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def delete_lead(db: Session, lead_id: UUID) -> None:
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead:
        db.delete(db_lead)
        db.commit()
