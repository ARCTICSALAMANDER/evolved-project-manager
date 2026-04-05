from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.crud import create_project
from app.db.session import get_db
from app.schemas.project import ProjectIn, ProjectOut
from app.db.schema import projects_table
from datetime import datetime
from fastapi import HTTPException


project_router = APIRouter()


@project_router.post("/", status_code=201)
async def project_creation(project_in: ProjectIn, db: AsyncSession = Depends(get_db)):
    created = await create_project(db, project_in.name, project_in.user_id, project_in.description, project_in.is_public)
    if created[0]:
        return created[1]
    else:
        raise HTTPException(status_code=400, detail="User not found")
