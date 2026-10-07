from app.schemas.project import ProjectUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, insert, select, update
from .schema import users_table, projects_table, tasks_table, refresh_tokens_table, project_members_table
from .tools import check_user_access_to_project, does_user_exist, does_project_exist, does_username_exist, does_project_name_exist, does_task_exist, is_task_in_the_project, is_user_project_admin
import datetime
import bcrypt
import secrets


async def create_user(session: AsyncSession, username: str, hashed_password: str,
                      email: str | None = None,
                      tech_stack: list[str] | None = None) -> tuple[bool, int]:
    if await does_username_exist(session, username):
        return (False, 0)

    if email is not None:
        existing_email = await session.scalar(
            select(users_table.c.id).where(users_table.c.email == email)
        )
        if existing_email is not None:
            return (False, 0)

    stmt = insert(users_table).values(username=username,
                                      email=email,
                                      tech_stack=tech_stack or [],
                                      hashed_password=hashed_password).returning(users_table.c.id)
    res = await session.scalar(stmt)
    if res is None:
        raise RuntimeError("User insert did not return an id")
    await session.commit()

    return (True, res)


async def check_user_data(session: AsyncSession, username: str, password: str) -> tuple[bool, int]:
    stmt = select(users_table.c.id, users_table.c.hashed_password).where(
        users_table.c.username == username)
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

    stmt = update(users_table).where(users_table.c.id ==
                                     user_id).values(username=new_username)
    await session.execute(stmt)
    await session.commit()
    return (200, "OK")


async def update_user_profile(session: AsyncSession, user_id: int, updates: dict) -> tuple[int, str]:
    if not await does_user_exist(session, user_id):
        return (404, "User not found")

    values = {}
    new_username = updates.get("new_username")
    if new_username is not None:
        existing_user_id = await session.scalar(
            select(users_table.c.id).where(
                users_table.c.username == new_username,
                users_table.c.id != user_id
            )
        )
        if existing_user_id is not None:
            return (409, "Username already exists")
        values["username"] = new_username

    if "email" in updates:
        email = updates["email"]
        if email is not None:
            existing_user_id = await session.scalar(
                select(users_table.c.id).where(
                    users_table.c.email == email,
                    users_table.c.id != user_id
                )
            )
            if existing_user_id is not None:
                return (409, "Email already exists")
        values["email"] = email

    if "tech_stack" in updates:
        values["tech_stack"] = updates["tech_stack"] or []

    if values:
        stmt = update(users_table).where(users_table.c.id == user_id).values(**values)
        await session.execute(stmt)
        await session.commit()

    return (200, "OK")


async def delete_user(session: AsyncSession, user_id: int, requesting_user_id: int) -> tuple[int, str]:
    if requesting_user_id != user_id:
        return (403, "You can only delete your own account")

    if not await does_user_exist(session, user_id):
        return (404, "User not found")

    stmt = delete(users_table).where(users_table.c.id == user_id)
    await session.execute(stmt)
    await session.commit()
    return (200, "OK")


async def get_user(session: AsyncSession, user_id: int):
    stmt = select(users_table.c.username, users_table.c.email, users_table.c.tech_stack).where(
        users_table.c.id == user_id)
    res = await session.execute(stmt)
    res = res.first()
    if res is None:
        return False, {}

    return True, {"username": res[0], "email": res[1], "tech_stack": res[2]}


async def get_user_projects(session: AsyncSession, user_id: int):
    if await does_user_exist(session, user_id):
        stmt = select(projects_table.c.project_id, projects_table.c.name).where(
            projects_table.c.user_id == user_id)
        res = await session.execute(stmt)
        return (200, "OK", res.all())
    else:
        return (404, "User not found", tuple())


async def check_username(session: AsyncSession, username: str) -> bool:
    stmt = select(users_table.c.id).where(users_table.c.username == username)
    res = await session.execute(stmt)
    res = res.first()

    return res is None


async def create_project(session: AsyncSession, project_name: str, user_id: int,
                         description: str | None, is_public: bool,
                         created_at: datetime.datetime | None = None,
                         repository_url: str | None = None) -> tuple:
    if created_at is None:
        created_at = datetime.datetime.now()

    if not await does_user_exist(session, user_id):
        return False, 0

    stmt = insert(projects_table).values(
        name=project_name,
        user_id=user_id,
        is_public=is_public,
        description=description,
        repository_url=repository_url,
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


async def get_project(session: AsyncSession, project_id: int, user_id: int | None = None) -> tuple[int, dict]:
    stmt = select(projects_table.c.name,
                  projects_table.c.description,
                  projects_table.c.is_public,
                  projects_table.c.created_at,
                  projects_table.c.user_id,
                  projects_table.c.repository_url).where(projects_table.c.project_id == project_id)
    res = await session.execute(stmt)
    res = res.first()
    if res is None:
        return (404, {})

    if user_id is not None:
        has_access = await check_user_access_to_project(session, project_id, user_id)
        if not has_access:
            return (404, {})

    can_view_repository = (
        user_id is not None
        and (user_id == res[4] or await is_user_project_member(session, project_id, user_id))
    )
    return (200, {
        "name": res[0],
        "description": res[1],
        "is_public": res[2],
        "created_at": res[3],
        "user_id": res[4],
        "repository_url": res[5] if can_view_repository else None
    })


async def delete_project(session: AsyncSession, project_id: int, user_id: int) -> tuple[int, str]:
    if not await does_project_exist(session, project_id):
        return (404, "Project not found")

    stmt = select(projects_table.c.user_id).where(
        projects_table.c.project_id == project_id)
    creator_id = await session.scalar(stmt)
    if creator_id != user_id:
        return (403, "Only the creator can delete this project")

    stmt = delete(projects_table).where(
        projects_table.c.project_id == project_id)
    await session.execute(stmt)
    await session.commit()
    return (200, "OK")


# async def delete_projects(session: AsyncSession, projects_ids: list) -> list:
#     projects_ids = list(set(projects_ids))
#     failed = []
#     for project_id in projects_ids:
#         status = await delete_project(session, project_id)
#         if not status:
#             failed.append(project_id)

#     return failed


async def update_project_data(session: AsyncSession, project_update: ProjectUpdate, user_id: int) -> tuple[int, str]:
    project_id = project_update.project_id

    if not await does_project_exist(session, project_id):
        return (404, "Project not found")

    stmt = select(projects_table.c.user_id).where(
        projects_table.c.project_id == project_id)
    creator_id = await session.scalar(stmt)
    if creator_id != user_id:
        return (403, "Only the creator can update this project")

    if "name" in project_update.model_fields_set and project_update.name is None:
        return (400, "Project name cannot be null")

    if project_update.name is not None:
        stmt = select(projects_table.c.project_id).where(
            (projects_table.c.project_id != project_id) &
            (projects_table.c.name == project_update.name))
        res = await session.scalar(stmt)
        if res is not None:
            return (409, "Project name already exists")

    values_dict = {
        field: getattr(project_update, field)
        for field in ("name", "description", "repository_url", "is_public")
        if field in project_update.model_fields_set
    }

    if values_dict:
        stmt = update(projects_table).where(
            projects_table.c.project_id == project_id).values(**values_dict)
        await session.execute(stmt)

    await session.commit()
    return (200, "OK")


async def is_user_project_member(session: AsyncSession, project_id: int, member_id: int) -> bool:
    stmt = select(project_members_table.c.id).where((project_members_table.c.user_id ==
                                                     member_id) & (project_members_table.c.project_id == project_id))
    res = await session.scalars(stmt)
    res = res.first()

    return res is not None


async def add_member_to_project(session: AsyncSession, project_id: int, user_id: int, member_id: int) -> tuple[int, str]:
    if not await does_project_exist(session, project_id):
        return (404, "Project not found")

    stmt = select(projects_table.c.user_id).where(
        projects_table.c.project_id == project_id)
    creator_id = await session.scalar(stmt)
    if creator_id != user_id:
        return (403, "Only the creator can add members to this project")

    if not await does_user_exist(session, member_id):
        return (404, "User not found")

    stmt = select(project_members_table.c.id).where(
        project_members_table.c.project_id == project_id, project_members_table.c.user_id == member_id)
    res = await session.execute(stmt)
    res = res.first()
    if res is not None:
        return (409, "User is already a member of this project")

    stmt = insert(project_members_table).values(
        user_id=member_id, project_id=project_id)
    await session.execute(stmt)
    await session.commit()

    return (200, "OK")


async def remove_project_member(session: AsyncSession, member_id: int, project_id: int, user_id: int) -> tuple[int, str]:
    if not await does_project_exist(session, project_id):
        return (404, "Project not found")

    stmt = select(projects_table.c.user_id).where(
        projects_table.c.project_id == project_id)
    creator_id = await session.scalar(stmt)
    if creator_id != user_id:
        return (403, "Only the creator can remove members from this project")

    if not await is_user_project_member(session, project_id, member_id):
        return (400, "This user is not a member of this project")

    stmt = delete(project_members_table).where((project_members_table.c.user_id == member_id) & (
        project_members_table.c.project_id == project_id))
    await session.execute(stmt)
    await session.commit()

    return (200, "OK")


async def get_tasks_in_project(session: AsyncSession, project_id: int, user_id: int):
    if await does_project_exist(session, project_id):
        if await check_user_access_to_project(session, project_id, user_id):
            stmt = select(
                tasks_table.c.task_id,
                tasks_table.c.task_name,
                tasks_table.c.task_description,
                tasks_table.c.task_executor,
                tasks_table.c.status,
                tasks_table.c.commit_url,
                tasks_table.c.deadline,
                tasks_table.c.x_coord,
                tasks_table.c.y_coord
            ).where(
                tasks_table.c.project_id == project_id)
            res = (await session.execute(stmt)).mappings().all()
            tasks_list = [
                {
                    "task_id": row["task_id"],
                    "name": row["task_name"],
                    "description": row["task_description"],
                    "task_executor": row["task_executor"],
                    "status": row["status"],
                    "commit_url": row["commit_url"],
                    "deadline": row["deadline"],
                    "x_coord": row["x_coord"],
                    "y_coord": row["y_coord"]
                }
                for row in res
            ]
            return (200, "OK", tasks_list)
        else:
            return (403, "You don't have access to this project")    
    else:
        return (404, "Project not found", [])


async def create_task(session: AsyncSession, task_name: str, project_id: int, user_id: int,
                      task_description: str | None = None,
                      task_status: str = "not_started",
                      commit_url: str | None = None,
                      task_executor: int | None = None,
                      deadline: datetime.datetime | None = None):
    if not await does_project_exist(session, project_id):
        return (404, "Project not found")

    has_access = await check_user_access_to_project(session, project_id, user_id)
    if not has_access:
        return (403, "You don't have access to this project")

    if task_executor is not None:
        project_owner_id = await session.scalar(
            select(projects_table.c.user_id).where(
                projects_table.c.project_id == project_id
            )
        )
        is_project_member = await is_user_project_member(
            session, project_id, task_executor
        )
        if task_executor != project_owner_id and not is_project_member:
            return (400, "Task executor must be a project member")

    stmt = insert(tasks_table).values(task_name=task_name,
                                      task_description=task_description,
                                      task_executor=task_executor,
                                      status=task_status,
                                      commit_url=commit_url,
                                      deadline=deadline,
                                      project_id=project_id).returning(tasks_table.c.task_id)
    task_id = await session.scalar(stmt)
    await session.commit()

    return (201, task_id)


async def get_task_info(session: AsyncSession, project_id: int, task_id: int, user_id: int) -> tuple[int, dict]:
    if not await does_project_exist(session, project_id):
        return (404, {})

    has_access = await check_user_access_to_project(session, project_id, user_id)
    if not has_access:
        return (403, {})

    if not await does_task_exist(session, task_id):
        return (404, {})

    if not await is_task_in_the_project(session, task_id, project_id):
        return (404, {})

    stmt = select(tasks_table.c.task_id,
                  tasks_table.c.task_name,
                  tasks_table.c.task_description,
                  tasks_table.c.task_executor,
                  tasks_table.c.status,
                  tasks_table.c.commit_url,
                  tasks_table.c.deadline,
                  tasks_table.c.x_coord,
                  tasks_table.c.y_coord).where(tasks_table.c.task_id == task_id)
    task_info = (await session.execute(stmt)).mappings().first()
    if task_info is None:
        return (404, {})

    return (200, {
        "task_id": task_info["task_id"],
        "name": task_info["task_name"],
        "description": task_info["task_description"],
        "task_executor": task_info["task_executor"],
        "status": task_info["status"],
        "commit_url": task_info["commit_url"],
        "deadline": task_info["deadline"],
        "x_coord": task_info["x_coord"],
        "y_coord": task_info["y_coord"]
    })


async def change_task_coords(task_id: int, project_id: int, new_x: int, new_y: int, user_id: int, session: AsyncSession):
    project_exists = await does_project_exist(session, project_id)
    if not project_exists:
        return (404, "Project not found")

    access_to_project = await check_user_access_to_project(session, project_id, user_id)
    if not access_to_project:
        return (404, "Project not found")

    task_exists = await does_task_exist(session, task_id)
    if not task_exists:
        return (404, "Task not found")

    if not await is_task_in_the_project(session, task_id, project_id):
        return (404, "Task not found")

    stmt = update(tasks_table).where(tasks_table.c.task_id ==
                                     task_id).values(x_coord=new_x, y_coord=new_y)
    await session.execute(stmt)
    await session.commit()
    return (200, "OK")


async def delete_task(task_id: int, project_id: int, user_id: int, session: AsyncSession):
    project_exists = await does_project_exist(session, project_id)
    if not project_exists:
        return (404, "Project not found")

    access_to_project = await check_user_access_to_project(session, project_id, user_id)
    if not access_to_project:
        return (403, "You don't have access to this project")

    task_exists = await does_task_exist(session, task_id)
    if not task_exists:
        return (404, "Task not found")

    if not await is_task_in_the_project(session, task_id, project_id):
        return (404, "Task not found")

    stmt = delete(tasks_table).where(tasks_table.c.task_id == task_id)
    await session.execute(stmt)
    await session.commit()
    return (200, "OK")


async def update_task(task_id: int, project_id: int, user_id: int, session: AsyncSession,
                      updates: dict):
    project_exists = await does_project_exist(session, project_id)
    if not project_exists:
        return (404, "Project not found")

    access_to_project = await check_user_access_to_project(session, project_id, user_id)
    if not access_to_project:
        return (403, "You don't have access to this project")

    task_exists = await does_task_exist(session, task_id)
    if not task_exists:
        return (404, "Task not found")

    if not await is_task_in_the_project(session, task_id, project_id):
        return (404, "Task not found")

    values_dict = {}
    field_map = {
        "name": "task_name",
        "description": "task_description",
        "task_executor": "task_executor",
        "deadline": "deadline",
        "status": "status",
        "commit_url": "commit_url"
    }
    for field, column in field_map.items():
        if field in updates:
            value = updates[field]
            if field in ("name", "status") and value is None:
                return (400, f"{field} cannot be null")
            if field == "task_executor" and value is not None:
                if not await does_user_exist(session, value):
                    return (404, "Executor user not found")
                project_owner_id = await session.scalar(
                    select(projects_table.c.user_id).where(
                        projects_table.c.project_id == project_id
                    )
                )
                if value != project_owner_id and not await is_user_project_member(
                    session, project_id, value
                ):
                    return (400, "Task executor must be a project member")
            values_dict[column] = value

    if values_dict:
        stmt = update(tasks_table).where(
            tasks_table.c.task_id == task_id).values(**values_dict)
        await session.execute(stmt)

    await session.commit()
    return (200, "OK")


async def check_refresh_token(token: str, session: AsyncSession):
    stmt = select(refresh_tokens_table.c.user_id, refresh_tokens_table.c.expires_at).where(
        refresh_tokens_table.c.token == token)
    res = await session.execute(stmt)
    res = res.first()
    if res is None:
        return (403, "Unauthorized")

    user_id, exp_at = res

    if exp_at <= datetime.datetime.now(datetime.timezone.utc):
        return (401, "Refresh token expired")

    return (200, user_id)


async def create_refresh_token(session: AsyncSession, user_id: int) -> str:
    stmt = select(refresh_tokens_table.c.id).where(
        refresh_tokens_table.c.user_id == user_id)
    res = await session.scalars(stmt)
    res = res.all()
    if res:
        stmt = delete(refresh_tokens_table).where(
            refresh_tokens_table.c.id.in_(res))
        await session.execute(stmt)

    refresh_token = secrets.token_urlsafe(64)
    exp_at = datetime.datetime.now(
        datetime.timezone.utc) + datetime.timedelta(days=7)

    stmt = insert(refresh_tokens_table).values(
        user_id=user_id, token=refresh_token, expires_at=exp_at)
    await session.execute(stmt)
    await session.commit()

    return refresh_token
