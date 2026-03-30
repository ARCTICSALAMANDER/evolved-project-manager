from backend.app.core.config import Settings
from flask import config
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT as ILA
from sqlalchemy import Boolean, Column, ForeignKey, Integer, MetaData, String, Table
import sqlalchemy


def create_db():
    conn = psycopg2.connect(user="postgres", password=Settings.DB_PASSWORD)
    conn.set_isolation_level(ILA)

    cursor = conn.cursor()
    cursor.execute('create database if not exists project_manager')


DATABASE_URL = sqlalchemy.create_engine(
    f"postgresql+psycopg2://postgres:{Settings.DB_PASSWORD}@{Settings.HOST}/project_manager")

metadata = MetaData()

users_table = Table('users', metadata,
                    Column('id', Integer(), primary_key=True, nullable=False),
                    Column('username', String(), nullable=False, unique=True)
                    )

projects_table = Table('projects', metadata,
                       Column('project_id', Integer(),
                              primary_key=True, nullable=False),
                       Column('user_id', ForeignKey("users.id")),
                       Column('name', String(), nullable=False, unique=True),
                       Column('is_public', Boolean(), default=False)
                       )


def init_db():
    metadata.create_all(DATABASE_URL)


def clear_db():
    metadata.drop_all(DATABASE_URL)


if __name__ == "__main__":
    create_db()
    init_db()
