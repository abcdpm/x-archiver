from fastapi import APIRouter, BackgroundTasks, Query
from app.models.archive import PaginatedTweets, SyncRequest
from app.database import get_db_connection
from app.services.scraper import sync_favorited_tweets
from app.services.downloader import process_media_downloads

router = APIRouter()

@router.get("/tweets", response_model=PaginatedTweets)
def get_tweets(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM tweets")
    total = cursor.fetchone()['total']
    
    offset = (page - 1) * size
    cursor.execute("SELECT * FROM tweets ORDER BY posted_at DESC LIMIT ? OFFSET ?", (size, offset))
    tweets_rows = cursor.fetchall()
    
    if not tweets_rows:
        conn.close()
        return {"total": total, "page": page, "size": size, "data": []}
        
    tweet_ids = [row['tweet_id'] for row in tweets_rows]
    placeholders = ','.join(['?'] * len(tweet_ids))
    
    cursor.execute(f"SELECT * FROM media WHERE tweet_id IN ({placeholders})", tweet_ids)
    media_rows = cursor.fetchall()
    conn.close()
    
    media_map = {}
    for row in media_rows:
        tid = row['tweet_id']
        if tid not in media_map:
            media_map[tid] = []
        media_map[tid].append(dict(row))
        
    result_data = []
    for tweet in tweets_rows:
        tweet_dict = dict(tweet)
        tweet_dict['media'] = media_map.get(tweet['tweet_id'], [])
        result_data.append(tweet_dict)
        
    return {"total": total, "page": page, "size": size, "data": result_data}

@router.post("/sync")
async def trigger_sync(request: SyncRequest, background_tasks: BackgroundTasks):
    async def run_sync_and_download():
        await sync_favorited_tweets(request.username)
        await process_media_downloads()
        
    background_tasks.add_task(run_sync_and_download)
    return {"message": f"Background tasks started for {request.username}"}