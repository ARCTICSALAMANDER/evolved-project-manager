from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, insert, select, update
from .schema import users_table, projects_table
from datetime import datetime


async def create_user(session: AsyncSession, username: str):
    stmt = insert(users_table).values(username=username)
    await session.execute(stmt)
    await session.commit()


async def create_users(session: AsyncSession, usernames: list):
    usernames = list(set(usernames))
    for username in usernames:
        await create_user(session, username)


async def create_project(session: AsyncSession, project_name: str, user_id: int, description: str | None, is_public: bool, created_at: datetime | None = None) -> tuple:
    if created_at is None:
        created_at = datetime.now()
    
    stmt = select(users_table).where(users_table.c.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        return False, None

    stmt = insert(projects_table).values(
        name=project_name, user_id=user_id, is_public=is_public, description=description, created_at=created_at).returning(projects_table)
    res = await session.execute(stmt)
    await session.commit()
    return True, res.mappings().first()


async def create_projects(session: AsyncSession, projects_data: list) -> list:
    failed = []
    for name, user_id, description, is_public, created_at in projects_data:
        success = await create_project(session, name, user_id, description, is_public, created_at)
        if not success[0]:
            failed.append((name, user_id, description, is_public, created_at))    
    
    return failed


async def delete_project(session: AsyncSession, project_id: int) -> bool:
    stmt = select(projects_table).where(
        projects_table.c.project_id == project_id)
    result = await session.execute(stmt)
    if result.first() is None:
        return False

    stmt = delete(projects_table).where(
        projects_table.c.project_id == project_id)
    await session.execute(stmt)
    await session.commit()
    return True


async def delete_projects(session: AsyncSession, projects_ids: list) -> list:
    projects_ids = list(set(projects_ids))
    failed = []
    for project_id in projects_ids:
        status = await delete_project(session, project_id)
        if not status:
            failed.append(project_id)

    return failed
    
    
async def toggle_project_is_public(session: AsyncSession, project_id: int) -> bool:
    stmt = select(projects_table.c.is_public).where(
        projects_table.c.project_id == project_id)
    result = await session.execute(stmt)
    row = result.first()
    if row is None:
        return False
    curr_is_public = row[0]

    stmt = update(projects_table).where(projects_table.c.project_id ==
                                        project_id).values(is_public=not curr_is_public)
    await session.execute(stmt)
    await session.commit()

    return True