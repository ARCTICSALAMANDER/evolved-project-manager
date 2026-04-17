from app.schemas.project import ProjectUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, insert, select, update, join
from .schema import users_table, projects_table, tasks_table
from .tools import does_user_exist, does_project_exist, does_username_exist, does_project_name_exist, does_task_exist, is_task_in_the_project
from datetime import datetime
import bcrypt


async def create_user(session: AsyncSession, username: str, hashed_password: str):
    if await does_username_exist(session, username):
        return (False, 0)

    stmt = insert(users_table).values(username=username, hashed_password=hashed_password).returning(users_table.c.id)
    res = await session.scalar(stmt)
    await session.commit()
    
    return (True, res)


async def check_user_data(session: AsyncSession, username: str, password: str):
    stmt = select(users_table.c.id, users_table.c.hashed_password).where(users_table.c.username == username)
    res = await session.execute(stmt)
    user_data = res.first()
  
    if user_data is None:
        return (False, 0)   
    
    user_id, stored_hash = user_data
    
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return (True, user_id)
    else:
        return (False, 0)


async def change_username(session: AsyncSession, user_id: int, new_username: str) -> tuple[int, str]:
    if not await does_user_exist(session, user_id):
        return (404, "User not found")
    
    if await does_username_exist(session, new_username):
        return (409, "Username already exists")

    stmt = update(users_table).where(users_table.c.id == user_id).values(username=new_username)
    await session.execute(stmt)
    await session.commit()
    return (200, "OK")


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    if not await does_user_exist(session, user_id):
        return False
    
    stmt = delete(users_table).where(users_table.c.id == user_id)
    await session.execute(stmt)
    await session.commit()
    return True


async def get_user(session: AsyncSession, user_id: int):
    stmt = select(users_table.c.username, users_table.c.hashed_password).where(users_table.c.id == user_id)
    res = await session.execute(stmt)
    res = res.first()
    if res is None:
        return False, {}

    return True, {"username": res[0], "hashed_password": res[1]}


async def check_username(session: AsyncSession, username: str) -> bool:
    stmt = select(users_table.c.id).where(users_table.c.username == username)
    res = await session.execute(stmt)
    res = res.first()

    return res is None


async def create_project(session: AsyncSession, project_name: str, user_id: int, description: str | None, is_public: bool, created_at: datetime | None = None) -> tuple:
    if created_at is None:
        created_at = datetime.now()

    if not await does_user_exist(session, user_id):
        return False, 0

    stmt = insert(projects_table).values(
        name=project_name,
        user_id=user_id,
        is_public=is_public,
        description=description,
        created_at=created_at
    ).returning(projects_table.c.project_id)

    res = await session.scalar(stmt)
    await session.commit()
    return True, res


# async def create_projects(session: AsyncSession, projects_data: list) -> list:
#     failed = []
#     for name, user_id, description, is_public, created_at in projects_data:
#         success = await create_project(session, name, user_id, description, is_public, created_at)
#         if not success[0]:
#             failed.append((name, user_id, description, is_public, created_at))

#     return failed


async def get_project(session: AsyncSession, project_id: int) -> dict:
    stmt = select(projects_table.c.name,
                  projects_table.c.description,
                  projects_table.c.is_public,
                  projects_table.c.created_at,
                  projects_table.c.user_id).where(projects_table.c.project_id == project_id)
    res = await session.execute(stmt)
    res = res.first()
    if res is None:
        return {}

    return {"name": res[0], "description": res[1], "is_public": res[2], "created_at": res[3], "user_id": res[4]}


async def delete_project(session: AsyncSession, project_id: int) -> bool:
    if not await does_project_exist(session, project_id):
        return False

    stmt = delete(projects_table).where(
        projects_table.c.project_id == project_id)
    await session.execute(stmt)
    await session.commit()
    return True


# async def delete_projects(session: AsyncSession, projects_ids: list) -> list:
#     projects_ids = list(set(projects_ids))
#     failed = []
#     for project_id in projects_ids:
#         status = await delete_project(session, project_id)
#         if not status:
#             failed.append(project_id)

#     return failed


async def update_project_data(session: AsyncSession, project_update: ProjectUpdate) -> tuple[int, str]:
    project_id = project_update.project_id

    if not await does_project_exist(session, project_id):
        return (404, "Project not found")

    if project_update.name is not None:
        # Check if new project name already exists (for other projects)
        stmt = select(projects_table.c.project_id).where(
            (projects_table.c.project_id != project_id) &
            (projects_table.c.name == project_update.name))
        res = await session.scalar(stmt)
        if res is not None:
            return (409, "Project name already exists")

    values_dict = {}
    if project_update.name is not None:
        values_dict["name"] = project_update.name
    if project_update.description is not None:
        values_dict["description"] = project_update.description
    if project_update.is_public is not None:
        values_dict["is_public"] = project_update.is_public

    if values_dict:
        stmt = update(projects_table).where(
            projects_table.c.project_id == project_id).values(**values_dict)
        await session.execute(stmt)

    await session.commit()
    return (200, "OK")


async def create_task(session: AsyncSession, task_name: str, project_id: int):
    stmt = insert(tasks_table).values(task_name=task_name, project_id=project_id).returning(tasks_table.c.task_id)
    task_id = await session.scalar(stmt)
    await session.commit()

    return (True, task_id)


async def get_task_info(session: AsyncSession, project_id: int, task_id: int) -> tuple[int, list]:
    stmt = select(projects_table.c.user_id).where(projects_table.c.project_id == project_id)
    user_id = await session.scalar(stmt)
    
    stmt = select(tasks_table.c.task_name, 
                  tasks_table.c.task_description, 
                  tasks_table.c.task_executor,
                  tasks_table.c.deadline).where(tasks_table.c.task_id == task_id)
    task_info = await session.execute(stmt)
    task_info = task_info.first()
    if task_info is None:
        return (404, [])

    res = [task_info, user_id]

    return (200, res)


async def change_task_coords(task_id: int, new_x: int, new_y: int, session: AsyncSession):
    stmt = update(tasks_table).where(tasks_table.c.task_id == task_id).values(x_coord=new_x, y_coord=new_y)
    await session.execute(stmt)
    await session.commit()