from app.schemas.task import TaskCreate, TaskIn
from app.db.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from app.db.crud import create_task as create_tsk, get_project, get_task_info
from app.core.security import get_curr_user
from sqlalchemy.ext.asyncio import AsyncSession


tasks_router = APIRouter(prefix="/projects/{project_id}/tasks")


@tasks_router.post("/create", status_code=201)
async def create_task(task_create: TaskCreate, db: AsyncSession = Depends(get_db), user_id = Depends(get_curr_user)):
    proj_info = await get_project(db, task_create.project_id)
    if not proj_info:
        raise HTTPException(status_code=404, detail="Project not found")

    if not proj_info["is_public"] and proj_info["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You don't have access to this project")

    res = await create_tsk(db, task_create.name, task_create.project_id)
    

@tasks_router.get("/{task_id}", status_code=200)
async def get_task(project_id: int, task_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_curr_user)):
    proj_info = await get_project(db, project_id)
    if not proj_info:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not proj_info["is_public"] and proj_info["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You don't have access to this project")
    
    res = await get_task_info(db, project_id, task_id)
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])
    
    return res[1]