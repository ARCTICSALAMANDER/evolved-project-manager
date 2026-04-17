from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud import create_project as create_proj, get_project as get_proj, delete_project as delete_proj, update_project_data as update_proj
from app.db.session import get_db
from app.schemas.project import ProjectIn, ProjectUpdate
from fastapi import HTTPException
from app.core.security import get_curr_user


project_router = APIRouter()


@project_router.post("/create", status_code=201)
async def project_creation(project_in: ProjectIn, db: AsyncSession = Depends(get_db), user_id : int = Depends(get_curr_user)):
    created = await create_proj(db, project_in.name, user_id, project_in.description, project_in.is_public)
    if created[0]:
        return created[1]
    else:
        raise HTTPException(status_code=404, detail="User not found")
    

@project_router.get("/get", status_code=200)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db), user_id : int = Depends(get_curr_user)):
    status_code, res = await get_proj(db, project_id, user_id)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=res if isinstance(res, str) else ("Project not found" if status_code == 404 else "Forbidden"))
    
    return res


@project_router.delete("/delete", status_code=204)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db), user_id : int = Depends(get_curr_user)):
    status_code, detail = await delete_proj(db, project_id, user_id)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=detail)


@project_router.patch("/update", status_code=200)
async def update_project_data(project_update: ProjectUpdate, db: AsyncSession = Depends(get_db), user_id : int = Depends(get_curr_user)):
    status_code, detail = await update_proj(db, project_update, user_id)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=detail)
    
    return detail