# src/tests/conftest.py
import pytest
from fastapi import FastAPI
from auth.users import UserManager
from fastapi_cache import FastAPICache
from database import get_async_session
from datetime import datetime, timedelta
from sqlalchemy.orm import declarative_base
from fastapi_cache.backends.redis import RedisBackend
from unittest.mock import MagicMock, AsyncMock, patch
from shortening_links.router import router as shorten_links_router
from sqlalchemy import create_engine, Column, Integer, String, DateTime
 

@pytest.fixture
def sample_data_shorten_links():
    create_date = datetime.now()
    last_use_date = datetime.now() + timedelta(hours=4)
    return {"url":"https://example.com",
            "short_link":"ex.com",
            "create_date":create_date,
            "last_use_date":last_use_date,
            "expires_at":datetime.now() + timedelta(seconds=1)
            }

@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = None
    mock_result.fetchall.return_value = None
    session.execute = AsyncMock(return_value=mock_result)
    session.commit = AsyncMock()
    return session
    
@pytest.fixture
def mock_user():
    user = MagicMock()
    # user.id = "user-id"
    return user

@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.get.return_value = b'5'
    return mock

@pytest.fixture
def mock_fastapi_cache_backend():
    backend = AsyncMock()
    backend.get_with_ttl = AsyncMock(return_value=(None, None))  # Для test_get_stats_error
    return backend

@pytest.fixture
def mock_fastapi_cache(mock_fastapi_cache_backend):
    with patch("fastapi_cache.FastAPICache.get_backend", return_value=mock_fastapi_cache_backend):
        yield

@pytest.fixture
async def test_fastapi(mock_redis, mock_db_session, mock_fastapi_cache):
    async def override_get_async_session():
        return mock_db_session

    with patch('redis_client.redis', mock_redis), \
         patch('redis_client.get_redis', AsyncMock(return_value=mock_redis)):
        
        app = FastAPI()
        app.include_router(shorten_links_router)
        app.dependency_overrides[get_async_session] = override_get_async_session
        FastAPICache.init(RedisBackend(mock_redis), prefix="test-cache")
        yield app


@pytest.fixture
def mock_user_db():
    return AsyncMock()

@pytest.fixture
def user_manager(mock_user):
    return UserManager(mock_user)