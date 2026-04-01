import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer
from collections.abc import AsyncGenerator

from db import get_session
from main import app
from models.user_model import Base


@pytest.fixture(scope="session")
def db_url():
    with PostgresContainer("postgres:17-alpine") as pg:
        yield pg.get_connection_url().replace(
            "postgresql+psycopg2://", "postgresql+asyncpg://"
        )


@pytest.fixture()
async def db_session(db_url) -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(db_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.connect() as conn:
        transaction = await conn.begin()
        session = session_factory(bind=conn)

        nested = await conn.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def reopen_nested(sync_session, sync_transaction):
            nonlocal nested
            if not nested.is_active:
                nested = conn.sync_connection.begin_nested()

        yield session

        await transaction.rollback()
        await session.close()

    await engine.dispose()


@pytest.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    def _override():
        yield db_session

    app.dependency_overrides[get_session] = _override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture()
def test_user() -> dict:
    return {
        "login": "bot@mail.ru",
        "password": "tessssat1123",
        "project_id": "11111111-1111-1111-1111-111111111111",
        "env": "prod",
        "domain": "regular",
    }