import logging
from twscrape import API, gather
from app.database import get_db_connection

async def sync_favorited_tweets(username: str):
    api = API()
    user = await api.user_by_login(username)
    if not user:
        logging.error("User not found!")
        return {"status": "error", "message": "User not found"}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    added_count = 0
    
    # 限制单次抓取数量以防风控
    tweets = await gather(api.favorited_by(user.id, limit=50)) 
    
    for tweet in tweets:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO tweets 
                (tweet_id, author_name, author_handle, author_avatar, content, post_type, original_url, posted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(tweet.id), tweet.user.name, tweet.user.username, 
                tweet.user.profileImageUrl, tweet.rawContent, 'like', tweet.url, tweet.date
            ))
            
            if cursor.rowcount > 0:
                added_count += 1
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
    return {"status": "success", "new_tweets": added_count}