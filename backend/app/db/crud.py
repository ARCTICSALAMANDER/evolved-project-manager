from sqlalchemy.orm import Session
from schema import DATABASE_URL as engine
from models import User, Project


def create_user(session: Session, username: str) -> bool:
    try:
        session.add(User(username=username))
        session.commit()

        return True
    except Exception as e:
        print('error occured:', e)
        session.rollback()
        return False


def create_users(session: Session, usernames: list) -> bool:
    for username in usernames:
        res = create_user(session, username)
        if not res:
            return False
        
    return True


def delete_user(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if not user:
        return False

    session.delete(user)
    session.commit()
    return True


def delete_users(session: Session, users_ids: list) -> bool:
    for user_id in users_ids:
        res = delete_user(session, user_id)
        if not res:
            return False
        
    return True


def create_project(session: Session, project_name: str, user_id: int, is_public: bool) -> bool:
    user = session.get(User, user_id)
    if not user:
        return False

    try:
        user.projects.append(Project(name=project_name, is_public=is_public))
        session.commit()
    except Exception as e:
        print("error occured:", e)
        session.rollback()
        return False

    return True


def create_projects(session: Session, projects: list) -> bool:
    for project in projects:
        res = create_project(session, project[0], project[1], project[2])
        if not res:
            return False
        
    return True


def delete_project(session: Session, project_id: int) -> bool:
    project = session.get(Project, project_id)
    if not project:
        return False
    
    session.delete(project)
    session.commit()

    return True


def delete_projects(session: Session, projects_ids: list) -> bool:
    for project_id in projects_ids:
        res = delete_project(session, project_id)
        if not res:
            return False
        
    return True


def toggle_projects_is_public(session: Session, project_ids: list) -> bool:
    for i in range(len(project_ids)):
        project_id = project_ids[i]
        project = session.get(Project, project_id)

        if project:
            project.is_public = not project.is_public
            session.commit()
        else:
            return False
        
    return True