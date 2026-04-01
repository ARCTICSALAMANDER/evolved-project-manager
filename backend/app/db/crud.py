from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from .schema import DATABASE_URL as engine, users_table, projects_table
from .models import User, Project


async def create_user(session: AsyncSession, username: str):
    stmt = insert(users_table).values(username=username)
    await session.execute(stmt)
    await session.commit()


async def create_users(session: AsyncSession, usernames: list):
    for username in usernames:
        await create_user(session, username)


async def create_project(session: AsyncSession, project_name: str, user_id: int, is_public: bool) -> bool:
    stmt = select(users_table).where(users_table.c.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        return False

    stmt = insert(projects_table).values(name=project_name, user_id=user_id, is_public=is_public)
    await session.execute(stmt)
    await session.commit()
    return True


async def create_projects(session: AsyncSession, projects_data: list):
    for name, user_id, is_public in projects_data:
        await create_project(session, name, user_id, is_public)


def delete_project(session: AsyncSession, project_id: int) -> bool:
    project = session.get(Project, project_id)
    if not project:
        return False

    session.delete(project)
    session.commit()

    return True


def delete_projects(session: AsyncSession, projects_ids: list) -> bool:
    for project_id in projects_ids:
        res = delete_project(session, project_id)
        if not res:
            return False

    return True


def toggle_projects_is_public(session: AsyncSession, project_ids: list) -> bool:
    for i in range(len(project_ids)):
        project_id = project_ids[i]
        project = session.get(Project, project_id)

        if project:
            project.is_public = not project.is_public
            session.commit()
        else:
            return False

    return True
