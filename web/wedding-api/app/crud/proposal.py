from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.proposal import Proposal, ProposalVersion, ProposalStatus, VersionChangeType
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
    # Calculate Version Number
    last_version = db.query(ProposalVersion).filter(
        ProposalVersion.proposal_id == version_in.proposal_id
    ).order_by(ProposalVersion.created_at.desc()).first()
    
    new_version_number = "1.0"
    if last_version:
        try:
            # Handle existing versions that might not have version_number yet (migration)
            v_str = last_version.version_number if last_version.version_number else "1.0"
            major, minor = map(int, v_str.split('.'))
            
            if version_in.change_type == VersionChangeType.MAJOR:
                major += 1
                minor = 0
            else:
                minor += 1
            new_version_number = f"{major}.{minor}"
        except Exception:
            # Fallback if parsing fails
            new_version_number = "1.0"

    db_version = ProposalVersion(
        **version_in.model_dump(),
        version_number=new_version_number,
        editor_id=editor_id
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version
