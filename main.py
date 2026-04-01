from contextlib import asynccontextmanager

from fastapi import FastAPI

from controllers import user_controller
from db import engine
from models.user_model import Base
from controllers.user_controller import router as user_controller


@asynccontextmanager
async def lifespan(application: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(user_controller, prefix="/api/v1")
