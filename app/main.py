import os
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from app.database import init_db, get_db_connection
from app.scraper import sync_favorited_tweets

app = FastAPI(title="X Archiver API")

# 1. 挂载本地媒体目录为静态资源服务
# 这样前端就能通过 /media/xxx/xxx.jpg 访问图片
MEDIA_DIR = os.getenv("MEDIA_DIR", "./media")
os.makedirs(MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

@app.on_event("startup")
def startup_event():
    init_db()

# ==================== Pydantic 响应模型 ====================
class MediaItem(BaseModel):
    id: int
    media_type: str
    original_url: str
    local_path: Optional[str] = None
    download_status: int

class TweetItem(BaseModel):
    tweet_id: str
    author_name: str
    author_handle: str
    author_avatar: Optional[str] = None
    content: Optional[str] = None
    post_type: str
    original_url: str
    posted_at: str
    archived_at: str
    media: List[MediaItem] = []

class PaginatedTweets(BaseModel):
    total: int
    page: int
    size: int
    data: List[TweetItem]

# ==================== 前端查询 API ====================

@app.get("/api/tweets", response_model=PaginatedTweets)
def get_tweets(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取分页的推文列表，用于前端瀑布流展示
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. 获取推文总数 (用于前端分页组件或判断是否加载到底)
    cursor.execute("SELECT COUNT(*) as total FROM tweets")
    total = cursor.fetchone()['total']
    
    # 2. 分页获取推文主体
    offset = (page - 1) * size
    cursor.execute('''
        SELECT * FROM tweets 
        ORDER BY posted_at DESC 
        LIMIT ? OFFSET ?
    ''', (size, offset))
    tweets_rows = cursor.fetchall()
    
    if not tweets_rows:
        conn.close()
        return {"total": total, "page": page, "size": size, "data": []}
        
    # 3. 提取这一页的推文 ID，去查询对应的媒体文件 (避免 N+1 查询问题)
    tweet_ids = [row['tweet_id'] for row in tweets_rows]
    placeholders = ','.join(['?'] * len(tweet_ids))
    
    cursor.execute(f'''
        SELECT * FROM media WHERE tweet_id IN ({placeholders})
    ''', tweet_ids)
    media_rows = cursor.fetchall()
    conn.close()
    
    # 4. 将媒体文件按 tweet_id 分组
    media_map = {}
    for row in media_rows:
        tid = row['tweet_id']
        if tid not in media_map:
            media_map[tid] = []
        media_map[tid].append(dict(row))
        
    # 5. 拼装最终的嵌套 JSON 数据
    result_data = []
    for tweet in tweets_rows:
        tweet_dict = dict(tweet)
        # 将关联的媒体列表附加到推文对象中
        tweet_dict['media'] = media_map.get(tweet['tweet_id'], [])
        result_data.append(tweet_dict)
        
    return {
        "total": total,
        "page": page,
        "size": size,
        "data": result_data
    }

# 挂载前端打包后的静态文件目录 (dist)
frontend_dist = os.path.join(os.path.dirname(__dirname), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # 捕获所有非 /api 的前端路由，返回 index.html 交给 Vue Router 处理（如果有的话）
    @app.get("/{catchall:path}")
    def serve_frontend(catchall: str):
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend build not found"}

# ==================== (保留之前的接口) ====================
class SyncRequest(BaseModel):
    username: str

@app.post("/api/sync")
async def trigger_sync(request: SyncRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_favorited_tweets, request.username)
    return {"message": f"Background sync started for {request.username}"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)