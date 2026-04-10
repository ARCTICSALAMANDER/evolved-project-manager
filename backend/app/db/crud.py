from app.schemas.project import ProjectUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, insert, select, update
from .schema import users_table, projects_table
from datetime import datetime


async def create_user(session: AsyncSession, username: str, hashed_password: str):
    stmt = select(users_table).where(users_table.c.username == username)
    res = await session.execute(stmt)
    if res.first() is not None:
        return (False, 0)

    stmt = insert(users_table).values(username=username, hashed_password=hashed_password).returning(users_table.c.id)
    res = await session.scalar(stmt)
    await session.commit()
    
    return (True, res)


async def change_username(session: AsyncSession, user_id: int, new_username: str) -> tuple[int, str]:
    stmt = select(users_table).where(users_table.c.id == user_id)
    res = await session.execute(stmt)
    if res.first() is None:
        return (404, "User not found")
    
    stmt = select(users_table.c.id).where(users_table.c.username == new_username)
    res = await session.execute(stmt)
    if res.first() is not None:
        return (409, "Username already exists")

    stmt = update(users_table).where(users_table.c.id == user_id).values(username=new_username)
    await session.execute(stmt)
    await session.commit()
    return (200, "OK")


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    stmt = select(users_table).where(users_table.c.id == user_id)
    res = await session.execute(stmt)
    if res.first() is None:
        return False
    
    stmt = delete(users_table).where(users_table.c.id == user_id)
    await session.execute(stmt)
    await session.commit()
    return True


async def get_user(session: AsyncSession, user_id: int):
    stmt = select(users_table.c.username).where(users_table.c.id == user_id)
    res = await session.execute(stmt)
    res = res.first()
    if res is None:
        return False, {}

    return True, {"username": res}


async def check_username(session: AsyncSession, username: str) -> bool:
    stmt = select(users_table.c.id).where(users_table.c.username == username)
    res = await session.execute(stmt)
    res = res.first()

    return res is None


async def create_project(session: AsyncSession, project_name: str, user_id: int, description: str | None, is_public: bool, created_at: datetime | None = None) -> tuple:
    if created_at is None:
        created_at = datetime.now()

    stmt = select(users_table).where(users_table.c.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        return False, None

    stmt = insert(projects_table).values(
        name=project_name,
        user_id=user_id,
        is_public=is_public,
        description=description,
        created_at=created_at
    ).returning(projects_table.c.project_id)

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


async def update_project_data(session: AsyncSession, project_update: ProjectUpdate) -> tuple[int, str]:
    project_id = project_update.project_id

    stmt = select(projects_table.c.name).where(
        projects_table.c.project_id == project_id)
    res = await session.execute(stmt)
    if res.first() is None:
        return (404, "Project not found")

    if project_update.name is not None:
        stmt = select(projects_table.c.name).where(
            (projects_table.c.project_id != project_id) &
            (projects_table.c.name == project_update.name))
        res = await session.execute(stmt)
        if res.first() is not None:
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
