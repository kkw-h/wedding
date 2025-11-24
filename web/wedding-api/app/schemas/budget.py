from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, computed_field

class BudgetItemBase(BaseModel):
    category: str
    name: str
    quantity: int = 1
    unit_price: float = 0.0

class BudgetItemCreate(BudgetItemBase):
    project_id: UUID
    cost_price: Optional[float] = 0.0

class BudgetItemUpdate(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    cost_price: Optional[float] = None

class BudgetItemResponse(BudgetItemBase):
    id: UUID
    project_id: UUID
    
    @computed_field
    def total_sale_price(self) -> float:
        return self.unit_price * self.quantity

    model_config = ConfigDict(from_attributes=True)

class BudgetItemAdminResponse(BudgetItemResponse):
    cost_price: float = 0.0
    
    @computed_field
    def total_cost_price(self) -> float:
        return self.cost_price * self.quantity
        
    @computed_field
    def gross_profit(self) -> float:
        return self.total_sale_price - self.total_cost_price
