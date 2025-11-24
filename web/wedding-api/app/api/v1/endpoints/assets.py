from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.core.storage import storage
from app.models.asset import Asset
from app.schemas.asset import AssetRead

router = APIRouter()

@router.post("/upload", response_model=AssetRead)
async def upload_file(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
    file: UploadFile = File(...)
):
    """
    上传文件到对象存储 (MinIO).
    """
    # 1. Read file content
    try:
        contents = await file.read()
        file_size = len(contents)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read file")

    # 2. Upload to MinIO
    try:
        # key 是存储在 bucket 中的路径
        key = storage.upload_file(contents, file.filename, file.content_type)
        # url 是前端访问的完整路径
        url = storage.get_url(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # 3. Save metadata to Database
    asset = Asset(
        filename=file.filename,
        file_key=key,
        content_type=file.content_type,
        size=file_size,
        uploaded_by=current_user.id
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    # 4. Construct Response manually to include the URL (which is not in DB)
    return AssetRead(
        id=asset.id,
        filename=asset.filename,
        content_type=asset.content_type,
        size=asset.size,
        url=url,
        created_at=asset.created_at
    )