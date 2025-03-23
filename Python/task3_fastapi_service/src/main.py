import uvicorn
from fastapi import FastAPI
from redis_client import init_redis
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from auth.schemas import UserCreate, UserRead
from fastapi.middleware.cors import CORSMiddleware
from auth.users import auth_backend, fastapi_users
from shortening_links.router import router as shorten_links


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_redis()
    yield

app = FastAPI(lifespan=lifespan)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(shorten_links)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="info")
