from app.db.tools import does_project_exist, is_user_project_admin
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud import create_project as create_proj, get_project as get_proj, delete_project as delete_proj, update_project_data as update_proj, get_tasks_in_project as get_proj_tasks, add_member_to_project as add_member, remove_project_member
from app.db.session import get_db
from app.schemas.project import ProjectIn, ProjectUpdate, ProjectMember
from fastapi import HTTPException
from app.core.security import get_curr_user


project_router = APIRouter()


@project_router.post("/create", status_code=201)
async def project_creation(project_in: ProjectIn, db: AsyncSession = Depends(get_db), user_id : int = Depends(get_curr_user)):
    created = await create_proj(
        db, project_in.name, user_id, project_in.description, project_in.is_public,
        repository_url=project_in.repository_url
    )
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


@project_router.get("/get_tasks", status_code=200)
async def get_project_tasks(project_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_curr_user)):
    res = await get_proj_tasks(db, project_id, user_id)    
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])

    return res[2]


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


@project_router.patch("/add_member", status_code=200)
async def add_project_member(member: ProjectMember, user_id: int = Depends(get_curr_user), db: AsyncSession = Depends(get_db)):
    res = await add_member(db, member.project_id, user_id, member.user_id)
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])
    
    return res[1]
            

@project_router.delete("/delete_member", status_code=204)
async def delete_member(member: ProjectMember, user_id: int = Depends(get_curr_user), db: AsyncSession = Depends(get_db)):
    res = await remove_project_member(db, member.user_id, member.project_id, user_id)
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])