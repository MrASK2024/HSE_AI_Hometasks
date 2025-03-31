import pytest
from auth.db import User
from fastapi import HTTPException
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from shortening_links.router import generate_random_short_link
from shortening_links.router import check_auth_user, delete_links_after_delay

@pytest.mark.parametrize("length, expected", [
    (6, 25),
    (8, 27),
    (20, 39)
])

def test_generate_random_short_link(length, expected):
    assert len(generate_random_short_link(length)) == expected


@pytest.mark.asyncio
async def test_check_auth_user_success(mock_db_session, mock_user):
    """Тест успешной проверки владельца ссылки"""
    
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [(str(mock_user.id),)]
    mock_db_session.execute.return_value = mock_result

    result = await check_auth_user(
        short_code="valid-code",
        user=mock_user,
        session=mock_db_session
    )

    assert result is True


@pytest.mark.asyncio
async def test_check_auth_user_unauthorized():
    """Тест неавторизованного пользователя"""
    
    with pytest.raises(HTTPException) as exc_info:
        await check_auth_user(
            short_code="any-code",
            user=None, 
            session=AsyncMock() 
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Вы не авторизованы"


@pytest.mark.asyncio
async def test_check_auth_user_not_owner(mock_db_session, mock_user):
    """Тест случая, когда пользователь не владелец ссылки"""
    
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [("other-user-id",)]
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await check_auth_user(
            short_code="valid-code",
            user=mock_user,
            session=mock_db_session
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Вы не являетесь владельцем ссылки"


@pytest.mark.asyncio
async def test_check_auth_user_link_not_found(mock_db_session, mock_user):
    """Тест случая, когда ссылка не существует"""
    
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await check_auth_user(
            short_code="non-existent-code",
            user=mock_user,
            session=mock_db_session
        )

    assert exc_info.value.status_code == 404
    assert "не существует" in exc_info.value.detail
    

@pytest.mark.asyncio
async def test_delete_links_after_delay(sample_data_shorten_links):
    test_short_link = sample_data_shorten_links['short_link']
    test_expires_at = sample_data_shorten_links['expires_at']
    
    mock_session = AsyncMock()
    mock_redis = AsyncMock()
    
    with patch('fastapi_cache.FastAPICache.clear', new_callable=AsyncMock) as mock_clear:
        result = await delete_links_after_delay(
            session=mock_session,
            short_link=test_short_link,
            expires_at=test_expires_at,
            redis=mock_redis
        )
        
        assert result is True
        
        mock_session.execute.assert_awaited_once()
        mock_session.commit.assert_awaited_once()
        
        mock_redis.delete.assert_awaited_once_with(f"short_url:{test_short_link}:clics_num")
        mock_clear.assert_awaited_once_with(namespace=f"short_link_stats:{test_short_link}")

@pytest.mark.asyncio
async def test_delete_links_after_delay_immediate(sample_data_shorten_links):
    test_short_link = sample_data_shorten_links['short_link']
    test_expires_at = datetime.now() - timedelta(seconds=5)
    
    mock_session = AsyncMock()
    mock_redis = AsyncMock()
    
    with patch('fastapi_cache.FastAPICache.clear', new_callable=AsyncMock):
        result = await delete_links_after_delay(
            session=mock_session,
            short_link=test_short_link,
            expires_at=test_expires_at,
            redis=mock_redis
        )
        
        assert result is False

        mock_session.execute.assert_not_awaited()
        mock_redis.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_on_after_register(user_manager, mock_user_db):
    """Проверяет, что on_after_register выводит сообщение."""
    
    user = User(id="123", email="test@email.com")
    with patch("builtins.print") as mock_print:
        await user_manager.on_after_register(user)
        mock_print.assert_called_once_with(f"User {user.id} has registered.")

@pytest.mark.asyncio
async def test_on_after_forgot_password(user_manager, mock_user_db):
    """Проверяет обработку забытого пароля."""
    
    user = User(id="123", email="test@mail.com")
    token = "test_token"
    with patch("builtins.print") as mock_print:
        await user_manager.on_after_forgot_password(user, token)
        mock_print.assert_called_once_with(
            f"User {user.id} has forgot their password. Reset token: {token}"
        )

@pytest.mark.asyncio
async def test_on_after_request_verify(user_manager, mock_user_db):
    """Проверяет обработку верификации."""
    
    user = User(id="123", email="test@mail.com")
    token = "test_token"
    with patch("builtins.print") as mock_print:
        await user_manager.on_after_request_verify(user, token)
        mock_print.assert_called_once_with(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )