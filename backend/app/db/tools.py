# will move here some frequently used functions for checking that user/project/task does exist, user has access to the projects, etc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schema import users_table, projects_table, tasks_table, project_members_table
from sqlalchemy import select


async def does_user_exist(session: AsyncSession, user_id: int) -> bool:
    stmt = select(users_table).where(users_table.c.id == user_id)
    res = await session.execute(stmt)

    return res.first() is not None


async def does_project_exist(session: AsyncSession, project_id: int) -> bool:
    stmt = select(projects_table.c.name).where(projects_table.c.project_id == project_id)
    res = await session.execute(stmt)

    return res.first() is not None


async def check_user_access_to_project(session: AsyncSession, project_id: int, user_id: int) -> bool:
    stmt = select(projects_table.c.is_public, projects_table.c.user_id).where(projects_table.c.project_id == project_id)
    proj_info = await session.execute(stmt)
    proj_info = proj_info.first()

    stmt = select(project_members_table.c.id).where(project_members_table.c.project_id == project_id, project_members_table.c.user_id == user_id)
    is_user_member = await session.execute(stmt)
    is_user_member = is_user_member.first()

    if proj_info is not None:
        is_public, author_id = proj_info
        if not is_public:
            return (author_id == user_id) or (is_user_member is not None)

        return True    
    
    return False


async def is_user_project_admin(session: AsyncSession, project_id: int, user_id: int) -> bool:
    stmt = select(projects_table.c.user_id).where(projects_table.c.project_id == project_id)
    res = await session.scalars(stmt)
    res = res.first()

    return res == user_id
        

async def does_username_exist(session: AsyncSession, username: str) -> bool:
    stmt = select(users_table.c.id).where(users_table.c.username == username)
    res = await session.scalar(stmt)

    return res is not None


async def does_project_name_exist(session: AsyncSession, project_name: str) -> bool:
    stmt = select(projects_table.c.project_id).where(projects_table.c.name == project_name)
    res = await session.scalar(stmt)

    return res is not None


async def does_task_exist(session: AsyncSession, task_id: int) -> bool:
    stmt = select(tasks_table.c.task_name).where(tasks_table.c.task_id == task_id)
    res = await session.scalar(stmt)

    return res is not None


async def is_task_in_the_project(session: AsyncSession, task_id: int, project_id: int) -> bool:
    stmt = select(tasks_table.c.task_name).where(tasks_table.c.task_id == task_id, tasks_table.c.project_id == project_id)
    res = await session.scalar(stmt)

    return res is not None