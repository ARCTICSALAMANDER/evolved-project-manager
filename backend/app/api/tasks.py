from app.schemas.task import TaskCreate
from app.db.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from app.db.crud import create_task as create_tsk, get_project, get_task_info, change_task_coords
from app.core.security import get_curr_user
from app.db.tools import check_user_access_to_project, does_task_exist, is_task_in_the_project, does_project_exist
from sqlalchemy.ext.asyncio import AsyncSession


tasks_router = APIRouter(prefix="/projects/{project_id}/tasks")


@tasks_router.post("/create", status_code=201)
async def create_task(task_create: TaskCreate, project_id: int, db: AsyncSession = Depends(get_db), user_id = Depends(get_curr_user)):
    proj_info = await get_project(db, project_id)
    if not proj_info:
        raise HTTPException(status_code=404, detail="Project not found")

    has_access = await check_user_access_to_project(db, project_id, user_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="You don't have access to this project")

    res = await create_tsk(db, task_create.name, project_id)
    if res[0] != 201:
        raise HTTPException(status_code=res[0], detail=res[1])
    
    return res[1]


@tasks_router.get("/{task_id}", status_code=200)
async def get_task(project_id: int, task_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_curr_user)):
    if not await get_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    has_access = await check_user_access_to_project(db, project_id, user_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="You don't have access to this project")
    
    if not await does_task_exist(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not await is_task_in_the_project(db, task_id, project_id):
        raise HTTPException(status_code=404, detail="Task not found in this project")
    
    res = await get_task_info(db, project_id, task_id)
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])
    
    return res[1]


@tasks_router.patch(path="/{task_id}/update_coords", status_code=200)
async def update_task_coords(task_id: int, new_x: int, new_y: int, project_id: int, user_id: int = Depends(get_curr_user), db: AsyncSession = Depends(get_db)):
    project_exists = await does_project_exist(db, project_id)
    if not project_exists:
        raise HTTPException(status_code=404, detail="Project not found")
    
    access_to_project = await check_user_access_to_project(db, project_id, user_id)
    if not access_to_project:
        raise HTTPException(status_code=403, detail="You don't have access to this project")
    
    task_exists = await does_task_exist(db, task_id)
    if task_exists:
        await change_task_coords(task_id, new_x, new_y, db)
    else:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return "OK"