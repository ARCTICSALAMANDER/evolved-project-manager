from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.crud import create_project 
from app.db.session import get_db

class Project(BaseModel):
    name: str
    user_id: int # TODO: убрать отсюда, брать из токена
    is_public: bool


router = APIRouter()


@router.post("/", status_code=201)
async def project_creation(project: Project, db: AsyncSession = Depends(get_db)):
    created = await create_project(db, project.name, project.user_id, project.is_public)
    return created