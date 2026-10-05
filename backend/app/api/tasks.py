from app.schemas.task import TaskCreate, TaskUpdate
from app.db.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from app.db.crud import create_task as create_tsk, get_task_info, change_task_coords, delete_task as delete_tsk, update_task as update_tsk
from app.core.security import get_curr_user
from sqlalchemy.ext.asyncio import AsyncSession


tasks_router = APIRouter(prefix="/projects/{project_id}/tasks")


@tasks_router.post("/create", status_code=201)
async def create_task(task_create: TaskCreate, project_id: int, db: AsyncSession = Depends(get_db), user_id=Depends(get_curr_user)):
    status_code, result = await create_tsk(
        db, task_create.name, project_id, user_id, task_create.description)
    if status_code != 201:
        raise HTTPException(status_code=status_code, detail=result)

    return result


@tasks_router.get("/{task_id}", status_code=200)
async def get_task(project_id: int, task_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_curr_user)):
    status_code, result = await get_task_info(db, project_id, task_id, user_id)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=result)

    return result


@tasks_router.patch(path="/{task_id}/update_coords", status_code=200)
async def update_task_coords(task_id: int, new_x: int, new_y: int, project_id: int, user_id: int = Depends(get_curr_user), db: AsyncSession = Depends(get_db)):
    res = await change_task_coords(task_id, project_id, new_x, new_y, user_id, db)
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])

    return res[1]


@tasks_router.put(path="/{task_id}", status_code=200)
async def update_task(task_id: int, task_update: TaskUpdate, project_id: int, user_id: int = Depends(get_curr_user), db: AsyncSession = Depends(get_db)):
    res = await update_tsk(task_id, project_id, user_id, db, task_update.name, task_update.description, task_update.task_executor, task_update.deadline)
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])

    return res[1]


@tasks_router.delete(path="/{task_id}", status_code=200)
async def delete_task(task_id: int, project_id: int, user_id: int = Depends(get_curr_user), db: AsyncSession = Depends(get_db)):
    res = await delete_tsk(task_id, project_id, user_id, db)
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])

    return res[1]
