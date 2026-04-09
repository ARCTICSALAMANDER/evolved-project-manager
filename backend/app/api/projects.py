from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud import create_project as create_proj, get_project as get_proj, delete_project as delete_proj, update_project_data as update_proj
from app.db.session import get_db
from app.schemas.project import ProjectIn, ProjectUpdate
from fastapi import HTTPException


project_router = APIRouter()


@project_router.post("/create", status_code=201)
async def project_creation(project_in: ProjectIn, db: AsyncSession = Depends(get_db)):
    created = await create_proj(db, project_in.name, project_in.user_id, project_in.description, project_in.is_public)
    if created[0]:
        return created[1]
    else:
        raise HTTPException(status_code=404, detail="User not found")
    

@project_router.get("/get", status_code=200)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    res = await get_proj(db, project_id)
    if not res:
        raise HTTPException(status_code=404, detail="Project not found")    
    return res
    

@project_router.delete("/delete", status_code=204)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    res = await delete_proj(db, project_id)
    if not res:
        raise HTTPException(status_code=404, detail="Project not found")
    return None


@project_router.patch("/update", status_code=200)
async def update_project_data(project_update: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    res = await update_proj(db, project_update)
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])
    return res[1]