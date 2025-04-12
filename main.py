from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from api import router as v1_router
from api.utils.system import create_system_user_and_categories
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware

from core.models import db_helper, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ЗАКОММЕНТИРОВАТЬ, ЕСЛИ ТАБЛИЦЫ УЖЕ СУЩЕСТВУЮТ
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with db_helper.session_factory() as session:
        await create_system_user_and_categories(session)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(v1_router, prefix=settings.api_v1_prefix)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
