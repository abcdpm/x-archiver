import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.database import init_db
from app.api.routers import router
from app.services.scraper import sync_favorited_tweets
from app.services.downloader import process_media_downloads

scheduler = AsyncIOScheduler()

async def scheduled_job():
    await sync_favorited_tweets(settings.TARGET_USERNAME)
    await process_media_downloads()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 数据库初始化
    init_db()
    # 2. 定时调度器初始化 (每天凌晨3点执行)
    scheduler.add_job(scheduled_job, 'cron', hour=3, minute=0)
    scheduler.start()
    yield
    # 3. 优雅关闭
    scheduler.shutdown()

app = FastAPI(title="X Archiver API", lifespan=lifespan)

# 注册 API 路由分发
app.include_router(router, prefix="/api")

# 挂载本地媒体目录，供前端直接读取
os.makedirs(settings.MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")