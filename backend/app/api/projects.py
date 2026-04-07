from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud import create_project as create_proj, get_project as get_proj
from app.db.session import get_db
from app.schemas.project import ProjectIn, ProjectOut
from fastapi import HTTPException


project_router = APIRouter()


@project_router.post("/create", status_code=201)
async def project_creation(project_in: ProjectIn, db: AsyncSession = Depends(get_db)):
    created = await create_proj(db, project_in.name, project_in.user_id, project_in.description, project_in.is_public)
    if created[0]:
        return created[1]
    else:
        raise HTTPException(status_code=400, detail="User not found")
    

@project_router.get("/get", status_code=200)
async def get_project(project_in: ProjectIn, db: AsyncSession = Depends(get_db)):
    project = await get_proj(db, project_in.name, project_in.user_id)
    if not project:
        raise HTTPException(status_code=400, detail="User not found")
    else:
        return project