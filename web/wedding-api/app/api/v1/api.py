from fastapi import APIRouter
from app.api.v1.endpoints import auth, leads, projects, budgets, approvals, proposals, assets, users, permissions

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["proposals"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
