from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.user import RoleType

# Shared properties
class UserBase(BaseModel):
    username: Optional[str] = None
    is_active: Optional[bool] = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    password: str
    roles: List[RoleType] = [RoleType.PLANNER]

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    roles: Optional[List[RoleType]] = None
    is_active: Optional[bool] = None

# Properties to return to client
class UserRead(UserBase):
    id: UUID
    username: str
    roles: List[RoleType] = Field(default=[], validation_alias="role_list")
    is_active: bool
    permissions: List[str] = []
    
    model_config = ConfigDict(from_attributes=True)