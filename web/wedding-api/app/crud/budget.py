from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.budget import BudgetItem
from app.schemas.budget import BudgetItemCreate, BudgetItemUpdate

def get_budget_items(db: Session, project_id: UUID) -> List[BudgetItem]:
    return db.query(BudgetItem).filter(BudgetItem.project_id == project_id).all()

def get_budget_item(db: Session, item_id: UUID) -> Optional[BudgetItem]:
    return db.query(BudgetItem).filter(BudgetItem.id == item_id).first()

def create_budget_item(db: Session, item_in: BudgetItemCreate) -> BudgetItem:
    db_item = BudgetItem(**item_in.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_budget_item(db: Session, db_item: BudgetItem, item_update: BudgetItemUpdate) -> BudgetItem:
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_budget_item(db: Session, db_item: BudgetItem) -> None:
    db.delete(db_item)
    db.commit()
