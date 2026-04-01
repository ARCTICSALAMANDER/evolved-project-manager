from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .schema import settings


engine = create_async_engine(f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.HOST}/project_manager")
async_sess_local = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with async_sess_local() as session:
        yield session