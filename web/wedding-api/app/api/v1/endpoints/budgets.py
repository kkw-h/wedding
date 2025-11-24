from typing import Any, List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.schemas.budget import (
    BudgetItemCreate, 
    BudgetItemUpdate, 
    BudgetItemResponse, 
    BudgetItemAdminResponse
)
from app.crud import budget as crud_budget
from app.crud import project as crud_project
from app.models.user import User, RoleType

router = APIRouter()

@router.get("/project/{project_id}", response_model=Union[List[BudgetItemAdminResponse], List[BudgetItemResponse]])
def read_project_budget(
    project_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取项目报价单。
    - PLANNER: 仅返回销售价相关字段
    - ADMIN/MANAGER: 返回包含成本价和毛利的完整数据
    """
    # 1. Check Project Existence & Permissions
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if current_user.role == RoleType.PLANNER:
        # 策划师只能看自己负责项目的报价单
        # Check through lead relation
        if project.lead.owner_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not enough permissions")

    # 2. Get Items
    items = crud_budget.get_budget_items(db, project_id=project_id)
    
    # 3. Dynamic Response based on Role
    if current_user.role in [RoleType.ADMIN, RoleType.MANAGER]:
        return [BudgetItemAdminResponse.model_validate(item) for item in items]
    else:
        return [BudgetItemResponse.model_validate(item) for item in items]

@router.post("/", response_model=BudgetItemResponse)
def create_budget_item(
    item_in: BudgetItemCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建报价单明细项。
    """
    # Check Project Permission
    project = crud_project.get_project(db, project_id=item_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if current_user.role == RoleType.PLANNER and project.lead.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    # If Planner, ensure cost_price is handled safely (e.g. they can set it if they know, or it defaults)
    # The schema allows it. Logic is fine.
    
    return crud_budget.create_budget_item(db, item_in=item_in)

@router.put("/{item_id}", response_model=BudgetItemResponse)
def update_budget_item(
    item_id: UUID,
    item_in: BudgetItemUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新报价单明细。
    """
    item = crud_budget.get_budget_item(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Check Project Permission via item -> project
    project = crud_project.get_project(db, project_id=item.project_id)
    if current_user.role == RoleType.PLANNER and project.lead.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    # Security: If Planner tries to update cost_price?
    # Ideally, we should ignore cost_price updates from Planner if strict.
    if current_user.role == RoleType.PLANNER:
        # Remove 'cost_price' from the set of fields to update, effectively ignoring it
        if "cost_price" in item_in.model_fields_set:
            item_in.model_fields_set.remove("cost_price")
             
    return crud_budget.update_budget_item(db, db_item=item, item_update=item_in)

@router.delete("/{item_id}", response_model=BudgetItemResponse)
def delete_budget_item(
    item_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    删除报价单明细。
    """
    item = crud_budget.get_budget_item(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    project = crud_project.get_project(db, project_id=item.project_id)
    if current_user.role == RoleType.PLANNER and project.lead.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    crud_budget.delete_budget_item(db, db_item=item)
    return item
