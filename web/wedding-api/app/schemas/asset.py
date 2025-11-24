from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Shared properties
class AssetBase(BaseModel):
    filename: str
    content_type: str
    size: int
    url: str # Computed/Returned, not stored

# Properties to receive via API on creation (internal use mostly)
class AssetCreate(AssetBase):
    file_key: str
    uploaded_by: UUID

# Properties to return to client
class AssetRead(AssetBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)