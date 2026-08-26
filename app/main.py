from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn

from app.database import init_db
from app.scraper import sync_favorited_tweets

app = FastAPI(title="X Archiver API")

# 在应用启动时初始化数据库表
@app.on_event("startup")
def startup_event():
    init_db()

class SyncRequest(BaseModel):
    username: str

@app.post("/api/sync")
async def trigger_sync(request: SyncRequest, background_tasks: BackgroundTasks):
    """
    触发抓取任务。使用 background_tasks 让接口立即返回，在后台静默抓取。
    """
    background_tasks.add_task(sync_favorited_tweets, request.username)
    return {"message": f"Background sync started for {request.username}"}

@app.get("/api/ping")
def ping():
    return {"status": "ok"}

# 本地调试用
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)