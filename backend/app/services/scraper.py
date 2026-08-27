import asyncio
import logging
from twscrape import API, gather
from app.database import get_db_connection
from app.downloader import process_media_downloads

async def sync_favorited_tweets(username: str):
    """抓取指定用户的点赞推文并入库"""
    # 注意：twscrape 会在本地生成一个 accounts.db 来保存登录状态
    api = API()
    
    # 初始化账号池（第一次运行前需要通过 CLI 或代码 add_account）
    # await api.pool.login_all()
    
    # 获取目标用户的 user_id
    user = await api.user_by_login(username)
    if not user:
        logging.error("User not found!")
        return {"status": "error", "message": "User not found"}

    logging.info(f"Start fetching favorites for {username}...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    added_count = 0
    # gather 将异步生成器转为列表。建议通过 limit 限制单次抓取数量，避免风控
    tweets = await gather(api.favorited_by(user.id, limit=50)) 
    
    for tweet in tweets:
        try:
            # 1. 插入推文主表 (利用 INSERT OR IGNORE 去重)
            cursor.execute('''
                INSERT OR IGNORE INTO tweets 
                (tweet_id, author_name, author_handle, author_avatar, content, post_type, original_url, posted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(tweet.id), tweet.user.name, tweet.user.username, 
                tweet.user.profileImageUrl, tweet.rawContent, 'like', tweet.url, tweet.date
            ))
            
            # 检查是否是真的插入了新数据（根据 rowcount 判断）
            if cursor.rowcount > 0:
                added_count += 1
                
                # 2. 提取并插入媒体附件信息 (状态默认为0，等待另一个异步任务去下载)
                if tweet.media:
                    for m in tweet.media.photos:
                        cursor.execute('INSERT INTO media (tweet_id, media_type, original_url) VALUES (?, ?, ?)',
                                       (str(tweet.id), 'image', m.url))
                    for m in tweet.media.videos:
                        cursor.execute('INSERT INTO media (tweet_id, media_type, original_url) VALUES (?, ?, ?)',
                                       (str(tweet.id), 'video', m.variants[0].url if m.variants else m.url))
            
        except Exception as e:
            logging.error(f"Error saving tweet {tweet.id}: {e}")

    conn.commit()
    conn.close()
    
    logging.info(f"Sync complete! Added {added_count} new tweets.")
    
    # 抓取结束后，紧接着启动媒体下载任务
    await process_media_downloads()
    
    return {"status": "success", "new_tweets": added_count}