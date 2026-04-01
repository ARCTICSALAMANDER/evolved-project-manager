from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from .schema import DATABASE_URL as engine, users_table
from .models import User, Project


async def create_user(session: AsyncSession, username: str):
    # try:
    #     session.add(User(username=username))
    #     session.commit()

    #     return True
    # except Exception as e:
    #     session.rollback()
    #     return False
    stmt = insert(users_table).values(username=username)
    await session.execute(stmt)
    await session.commit()


async def create_users(session: AsyncSession, usernames: list):
    for username in usernames:
        await create_user(session, username)


def delete_user(session: AsyncSession, user_id: int) -> bool:
    user = session.get(User, user_id)
    if not user:
        return False

    session.delete(user)
    session.commit()
    return True


def delete_users(session: AsyncSession, users_ids: list) -> bool:
    for user_id in users_ids:
        res = delete_user(session, user_id)
        if not res:
            return False
        
    return True


async def create_project(session: AsyncSession, project_name: str, user_id: int, is_public: bool): # TODO: перевести на async
    user = await session.get(User, user_id)
    if not user:
        yield

    try:
        user.projects.append(Project(name=project_name, is_public=is_public))
        await session.commit()
    except Exception as e:
        print(e)
        await session.rollback()


async def create_projects(session: AsyncSession, projects: list):
    for project in projects:
        res = create_project(session, project[0], project[1], project[2])


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