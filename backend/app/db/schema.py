from app.core.config import Settings
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT as ILA
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, MetaData, String, Table
import sqlalchemy
from datetime import datetime


settings = Settings()


def create_db():
    conn = psycopg2.connect(user=settings.DB_USER,
                            password=settings.DB_PASSWORD, host=settings.HOST)
    conn.set_isolation_level(ILA)

    cursor = conn.cursor()
    try:
        cursor.execute('CREATE DATABASE project_manager')
    except psycopg2.errors.DuplicateDatabase:
        pass

    cursor.close()
    conn.close()


DATABASE_URL = sqlalchemy.create_engine(
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.HOST}/project_manager")

metadata = MetaData()

users_table = Table('users', metadata,
                    Column('id', Integer(), primary_key=True, nullable=False),
                    Column('username', String(), nullable=False, unique=True),
                    Column('hashed_password', String(length=255), nullable=False)
                    )

projects_table = Table('projects', metadata,
                       Column('project_id', Integer(),
                              primary_key=True, nullable=False),
                       Column('user_id', ForeignKey(
                           "users.id"), nullable=False),
                       Column('name', String(), nullable=False, unique=True),
                       Column('description', String(), nullable=True),
                       Column('is_public', Boolean(), default=False),
                       Column('created_at', DateTime(), default=datetime.now)
                       )

tasks_table = Table('tasks', metadata,
                    Column('task_id', Integer(), primary_key=True),
                    Column('task_name', String(), nullable=False),
                    Column('task_description', String(), nullable=True),
                    Column('task_executor', ForeignKey(
                        users_table.c.id), nullable=True),
                    Column('status', String(), nullable=False, default="open"),
                    Column('deadline', DateTime(), nullable=True),
                    Column('project_id', ForeignKey(
                        projects_table.c.project_id), nullable=False),
                    Column('x_coord', Integer(), nullable=False, default=0),
                    Column('y_coord', Integer(), nullable=False, default=0)
                    )

refresh_tokens_table = Table('refresh_tokens', metadata,
                            Column('id', Integer(), primary_key=True, nullable=False),
                            Column('user_id', ForeignKey(users_table.c.id), nullable=False),
                            Column('token', String(512), nullable=False, index=True),
                            Column('expires_at', DateTime(timezone=True), nullable=False)
                            )

project_members_table = Table('project_members', metadata,
                            Column('id', Integer(), primary_key=True, nullable=False),
                            Column('user_id', ForeignKey(users_table.c.id), nullable=False),
                            Column('project_id', ForeignKey(projects_table.c.project_id), nullable=False)
                            )


def init_db():
    metadata.create_all(DATABASE_URL)


def clear_db():
    metadata.drop_all(DATABASE_URL)


if __name__ == "__main__":
    create_db()
    init_db()
