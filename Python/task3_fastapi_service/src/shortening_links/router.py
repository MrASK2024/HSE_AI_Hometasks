import random
import string
import asyncio
# from redis_client import redis

from auth.db import User
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from redis_client import get_redis
from fastapi import BackgroundTasks
from redis import asyncio as aioredis
from database import get_async_session
from fastapi_cache.decorator import cache
from auth.users import current_active_user
from .shortening_models import shorten_links
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update
from auth.users import current_active_user, fastapi_users
from fastapi import APIRouter, Depends, HTTPException, Query

import logging
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/shorten_links",
    tags=["ShortenLinks"]
)

async def check_auth_user(short_code: str, user: User = Depends(current_active_user), session: AsyncSession = Depends(get_async_session)):
    query = select(shorten_links.c.user_id).where(shorten_links.c.short_link == short_code)
    result = await session.execute(query)
    
    result = result.fetchall()
    if result is None:
        raise HTTPException(status_code=404, detail=f"Cсылки {short_code} не существует")

    user_id = result[0][0]
    if user_id != str(user.id):
        raise HTTPException(
            status_code=403,
            detail="Вы не являетесь владельцем ссылки",
        )
    return True

@router.post("/links/shorten")
async def create_short_link(url: str = Query(),
                            user: Optional[User] = Depends(fastapi_users.current_user(active=True, optional=True)),
                            custom_alias: str = Query(None, description="создание кастомной ссылки(опционально)"),
                            expires_at: Optional[datetime] = Query(None, description="создание c временем жизни ссылки(опционально). Формат: %Y-%m-%d %H:%M "),
                            session: AsyncSession = Depends(get_async_session),
                            redis: aioredis.Redis = Depends(get_redis),
                            background_tasks: BackgroundTasks = BackgroundTasks(),
                            ):
    try:   
        short_link = None
        
        if custom_alias:
            result = await session.execute(
                select(shorten_links).where(shorten_links.c.short_link == custom_alias)
            )
    
            if result.scalar() is not None:
                raise HTTPException(status_code=400, detail={
                    "status": "error",
                    "alias": "уже существует",
                })
    
            short_link = custom_alias
        else:
            short_link = generate_random_short_link()

        if expires_at:
             background_tasks.add_task(delete_links_after_delay, session, short_link, expires_at, redis)
        
        statement = insert(shorten_links).values(url = url, short_link = short_link, creation_date = datetime.now(), expires_at = expires_at, user_id=str(user.id) if user else None)
        await session.execute(statement)
        await session.commit()
        
        return {
            "status": "success",
            "short_link": short_link,
            "expires_at": expires_at,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": str(e)
        })


@router.get("/links/{short_code}")
@cache(expire=60)
async def get_short_links(short_code: str, session: AsyncSession = Depends(get_async_session), redis: aioredis.Redis = Depends(get_redis)):
    try:
        
        query = select(shorten_links.c.url, shorten_links.c.creation_date).where(shorten_links.c.short_link == short_code)
        result = await session.execute(query)
        result = result.fetchall()

        url = result[0][0]
        
        update_query = (
            update(shorten_links)
            .where(shorten_links.c.short_link == short_code)
            .values(last_use_date = datetime.now())
            )
        
        await session.execute(update_query)
        await session.commit()
        
        key = f"short_url:{short_code}:clics_num"
        
        if not await redis.exists(key):
            await redis.set(key, 0)

        await redis.incr(key)
        
        return RedirectResponse(url=url, status_code=307)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": e,
        })

@router.delete("/links/{short_code}")
async def delete_short_links(short_code: str, link: bool = Depends(check_auth_user), session: AsyncSession = Depends(get_async_session), redis: aioredis.Redis = Depends(get_redis)):
    
    delete_query = delete(shorten_links).where(shorten_links.c.short_link == short_code)
    await session.execute(delete_query)
    await session.commit()
    await redis.delete(f"short_url:{short_code}:clics_num")
    return {"status": "success deleted", "short_link": short_code}

@router.put("/links/{short_code:path}")
async def update_short_links(short_code: str, link: bool = Depends(check_auth_user), new_short_code: str = Query(), session: AsyncSession = Depends(get_async_session), redis: aioredis.Redis = Depends(get_redis)):
    try:
        result = await session.execute(
            select(shorten_links).where(shorten_links.c.short_link == new_short_code)
        )
        if result.scalar() is not None:
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "message": "Новая короткая ссылка уже существует"
            })
        
        result = await session.execute(
            select(shorten_links).where(shorten_links.c.short_link == short_code)
        )
        if result.scalar() is None:
            raise HTTPException(status_code=404, detail={
                "status": "error",
                "message": "Исходная короткая ссылка не найдена",
            })
        
        update_query = (
            update(shorten_links)
            .where(shorten_links.c.short_link == short_code)
            .values(short_link=new_short_code)
            )
        
        await redis.delete(f"short_url:{short_code}:clics_num")

        await session.execute(update_query)

        await session.commit()

        return {
            "status": "success update",
            "new_short_link": new_short_code
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
        })


@router.get("/links/{short_code}/stats")
@cache(expire=60)
async def get_short_links(short_code: str, session: AsyncSession = Depends(get_async_session), redis: aioredis.Redis = Depends(get_redis)):
    try:
        query = select(shorten_links.c.url, shorten_links.c.creation_date, shorten_links.c.last_use_date).where(shorten_links.c.short_link == short_code)
        result = await session.execute(query)
        result = result.fetchall()

        url = result[0][0]
        date_create = result[0][1]
        last_use_date = result[0][2]
        clics_num = await redis.get(f"short_url:{short_code}:clics_num")
        
        if not clics_num:
            clics_num = 0
        
        return {
            "status": "success stats",
            "url": url,
            "date_create": date_create,
            "clics_num": clics_num,
            "last_use_date": last_use_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
        })

@router.get("/links/search/")
async def search_links(url: str, session: AsyncSession = Depends(get_async_session)):
        try:
            query = select(shorten_links.c.short_link).where(shorten_links.c.url == url)
            result = await session.execute(query)
            result = result.fetchall()

            short_link = result[0][0]
            
            return {
                "status": "success",
                "short_link": short_link
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail={
                "status": "error",
                "data": None,
            })

async def delete_links_after_delay(session, short_link, expires_at, redis):  
    try:
        date_now = datetime.now()
        time_difference = expires_at - date_now
        sleep_duration = time_difference.total_seconds()

        if sleep_duration > 0:
            await asyncio.sleep(sleep_duration)
    
            delete_query = delete(shorten_links).where(shorten_links.c.short_link == short_link)
            await session.execute(delete_query)
            await session.commit()
            
            await redis.delete(f"short_url:{short_link}:clics_num")
            
            print(f"Строка с short_link={short_link} удалена.")

    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": str(e)
        })

def generate_random_short_link(length=6):
    characters = string.ascii_letters + string.digits
    short_link = ''.join(random.choice(characters) for _ in range(length))
    return f"https://short.link/{short_link}"