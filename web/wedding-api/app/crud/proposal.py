from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.proposal import Proposal, ProposalVersion, ProposalStatus
from app.schemas.proposal import ProposalCreate, ProposalUpdate, ProposalVersionCreate

# --- Proposal CRUD ---

def get_proposal(db: Session, proposal_id: UUID) -> Optional[Proposal]:
    return db.query(Proposal).filter(Proposal.id == proposal_id).first()

def get_proposals_by_project(db: Session, project_id: UUID) -> List[Proposal]:
    return db.query(Proposal).filter(Proposal.project_id == project_id).all()

def create_proposal(db: Session, proposal_in: ProposalCreate, creator_id: UUID) -> Proposal:
    db_proposal = Proposal(
        **proposal_in.model_dump(),
        created_by=creator_id,
        status=ProposalStatus.DRAFT,
        current_data={}
    )
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal

def update_proposal(db: Session, db_proposal: Proposal, proposal_update: ProposalUpdate) -> Proposal:
    update_data = proposal_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_proposal, key, value)
    
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal

# --- Version CRUD ---

def get_version(db: Session, version_id: UUID) -> Optional[ProposalVersion]:
    return db.query(ProposalVersion).filter(ProposalVersion.id == version_id).first()

def get_versions(db: Session, proposal_id: UUID, skip: int = 0, limit: int = 100) -> List[ProposalVersion]:
    return db.query(ProposalVersion).filter(
        ProposalVersion.proposal_id == proposal_id
    ).order_by(
        ProposalVersion.created_at.desc()
    ).offset(skip).limit(limit).all()

def create_version(db: Session, version_in: ProposalVersionCreate, editor_id: UUID) -> ProposalVersion:
    db_version = ProposalVersion(
        **version_in.model_dump(),
        editor_id=editor_id
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version
