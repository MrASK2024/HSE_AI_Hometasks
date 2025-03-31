import pytest
from database import get_async_session
from httpx import AsyncClient, ASGITransport
from shortening_links.router import check_auth_user
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_create_short_link_success(test_fastapi, mock_db_session, sample_data_shorten_links):
    """Тест успешного создания ссылки"""
    
    async with AsyncClient(
        transport=ASGITransport(app=test_fastapi),
        base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/shorten_links/links/shorten",
            params={
                "url": sample_data_shorten_links['url'],
                "custom_alias": sample_data_shorten_links['short_link']
            }
        )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_short_link_error(test_fastapi, mock_db_session, sample_data_shorten_links):
    """Тест ошибки при создании ссылки (существование кастомной ссылки)"""
    
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = "ex.ru"
    mock_db_session.execute.return_value = mock_result
    
    test_fastapi.dependency_overrides[get_async_session] = lambda: mock_db_session
    
    async with AsyncClient(
        transport=ASGITransport(app=test_fastapi),
        base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/shorten_links/links/shorten",
            params={
                "url": sample_data_shorten_links['url'],
                "custom_alias": sample_data_shorten_links['short_link']
            }
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_short_links_success(test_fastapi, mock_db_session, sample_data_shorten_links):
    """Тест успешного получения и перенаправления по короткой ссылке"""

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [(sample_data_shorten_links['url'], sample_data_shorten_links['create_date'])]
    mock_db_session.execute.return_value = mock_result

    short_code = sample_data_shorten_links['short_link']
    
    async with AsyncClient(
        transport=ASGITransport(app=test_fastapi),
        base_url="http://test"
    ) as ac:
        response = await ac.get(f"/shorten_links/links/{short_code}", follow_redirects=False)
    
    assert response.status_code == 307
    assert response.headers["location"] == sample_data_shorten_links['url']

@pytest.mark.asyncio
async def test_get_short_links_error(test_fastapi, sample_data_shorten_links):
    """Тест ошибки сервера при получении и перенаправлении по короткой ссылке"""

    short_code = sample_data_shorten_links['short_link']
    
    async with AsyncClient(
        transport=ASGITransport(app=test_fastapi),
        base_url="http://test"
    ) as ac:
        response = await ac.get(f"/shorten_links/links/{short_code}", follow_redirects=False)
    
    assert response.status_code == 500
    

@pytest.mark.asyncio
async def test_delete_short_links_success(test_fastapi, sample_data_shorten_links):
    """Тест успешного удаления ссылки при авторизованном пользователе"""
    
    async def mock_check_auth_user():
        return True
    
    test_fastapi.dependency_overrides[check_auth_user] = mock_check_auth_user
    short_code = sample_data_shorten_links['short_link']
    
    try:
        async with AsyncClient(
            transport=ASGITransport(app=test_fastapi),
            base_url="http://test"
        ) as ac:
            response = await ac.delete(f"/shorten_links/links/{short_code}")
        
        assert response.status_code == 200
        assert response.json() == {
            "status": "success deleted",
            "short_link": short_code
        }
        
    finally:
        test_fastapi.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_short_link_success(test_fastapi):
    """Тест успешного обновления ссылки при авторизованном пользователе"""
    
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    
    mock_result.scalar.side_effect = [None, MagicMock()]
    mock_db_session.execute.return_value = mock_result
    mock_db_session.commit = AsyncMock()
    
    test_fastapi.dependency_overrides[get_async_session] = lambda: mock_db_session
    
    async def mock_check_auth_user():
        return True
    
    test_fastapi.dependency_overrides[check_auth_user] = mock_check_auth_user
    
    try:
        async with AsyncClient(
            transport=ASGITransport(app=test_fastapi),
            base_url="http://test"
        ) as ac:
            response = await ac.put(
                "/shorten_links/links/old-code",
                params={"new_short_code": "new-code"}
            )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success update"
        assert response.json()["new_short_link"] == "new-code"
        
    finally:
        test_fastapi.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_short_link_not_found(test_fastapi):
    """Тест ошибки обновления ссылки при отсуствии исходной короткой ссылки"""
    
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.side_effect = [None, None]
    mock_db_session.execute.return_value = mock_result
    
    test_fastapi.dependency_overrides[get_async_session] = lambda: mock_db_session

    async def mock_check_auth_user():
        return True
    
    test_fastapi.dependency_overrides[check_auth_user] = mock_check_auth_user
    
    try:
        async with AsyncClient(
            transport=ASGITransport(app=test_fastapi),
            base_url="http://test"
        ) as ac:
            response = await ac.put(
                "/shorten_links/links/non-existent-code",
                params={"new_short_code": "new-code"}
            )

        assert response.status_code == 404
        response_data = response.json()['detail']
        assert response_data["status"] == "error"
        assert response_data["message"] == "Исходная короткая ссылка не найдена"
        
    finally:
        test_fastapi.dependency_overrides.clear()
        


@pytest.mark.asyncio
async def test_update_short_link_exsisting(test_fastapi):
    """Тест ошибки обновления ссылки при наличии новой ссылки в бд"""
    
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.side_effect = ['example.com', None]
    mock_db_session.execute.return_value = mock_result
    
    test_fastapi.dependency_overrides[get_async_session] = lambda: mock_db_session

    async def mock_check_auth_user():
        return True
    
    test_fastapi.dependency_overrides[check_auth_user] = mock_check_auth_user
    
    try:
        async with AsyncClient(
            transport=ASGITransport(app=test_fastapi),
            base_url="http://test"
        ) as ac:
            response = await ac.put(
                "/shorten_links/links/non-existent-code",
                params={"new_short_code": "new-code"}
            )

        assert response.status_code == 400
        response_data = response.json()['detail']
        assert response_data["status"] == "error"
        assert response_data["message"] == "Новая короткая ссылка уже существует"
        
    finally:
        test_fastapi.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_stats_success(test_fastapi, mock_redis, sample_data_shorten_links):
    """Тест успешного получения статистики по короткой ссылки"""
    
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        (sample_data_shorten_links['url'],
         sample_data_shorten_links['create_date'],
         sample_data_shorten_links['last_use_date'])
    ]
    mock_db_session.execute.return_value = mock_result
    
    test_fastapi.dependency_overrides[get_async_session] = lambda: mock_db_session
    
    try:
        async with AsyncClient(
            transport=ASGITransport(app=test_fastapi),
            base_url="http://test"
        ) as ac:
            response = await ac.get("/shorten_links/links/ex.com/stats")

        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["status"] == "success stats"
        assert response_data["url"] == sample_data_shorten_links['url']
        assert response_data["date_create"] == sample_data_shorten_links['create_date'].isoformat()
        assert response_data["last_use_date"] == sample_data_shorten_links['last_use_date'].isoformat()
        assert response_data["clics_num"] == '5'
            
    finally:
        test_fastapi.dependency_overrides.clear()
    
@pytest.mark.asyncio
async def test_get_stats_error(test_fastapi, sample_data_shorten_links):
    """Тест ошибки сервера при получении статистики и отсуствии данных по короткой ссылки"""
    
    async with AsyncClient(
        transport=ASGITransport(app=test_fastapi),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/shorten_links/links/ex.com/stats")

    assert response.status_code == 500
        

@pytest.mark.asyncio
async def test_get_search_success(test_fastapi, sample_data_shorten_links):
    """Тест успешного получения короткой ссылки по url"""
    
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [[sample_data_shorten_links['short_link']]]
    mock_db_session.execute.return_value = mock_result
    
    test_fastapi.dependency_overrides[get_async_session] = lambda: mock_db_session
    
    try:
        async with AsyncClient(
            transport=ASGITransport(app=test_fastapi),
            base_url="http://test"
        ) as ac:
            response = await ac.get("/shorten_links/links/search/",
                params={"url": sample_data_shorten_links['url']}
            )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "success"
        assert response_data["short_link"] == sample_data_shorten_links['short_link']
            
    finally:
        test_fastapi.dependency_overrides.clear()
    

@pytest.mark.asyncio
async def test_get_search_error(test_fastapi, sample_data_shorten_links):
    """Тест ошибки получения короткой ссылки по url"""
    
    async with AsyncClient(
        transport=ASGITransport(app=test_fastapi),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/shorten_links/links/search/",
            params={"url": sample_data_shorten_links['url']}
        )

    assert response.status_code == 500
        

    
        

