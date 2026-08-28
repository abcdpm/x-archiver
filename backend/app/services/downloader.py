import os
import logging
import asyncio
import aiohttp
import aiofiles
from urllib.parse import urlparse, parse_qs
from app.database import get_db_connection
from app.core.config import settings

def get_filename_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    base_name = os.path.basename(parsed_url.path)
    qs = parse_qs(parsed_url.query)
    if 'format' in qs:
        ext = qs['format'][0]
        if not base_name.endswith(f".{ext}"):
            base_name = f"{base_name}.{ext}"
    return base_name

async def download_file(session: aiohttp.ClientSession, url: str, dest_path: str) -> bool:
    try:
        async with session.get(url, timeout=60) as response:
            if response.status == 200:
                async with aiofiles.open(dest_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024 * 1024):
                        await f.write(chunk)
                return True
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")
    return False

async def process_media_downloads():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, original_url, tweet_id FROM media WHERE download_status = 0")
    pending_media = cursor.fetchall()
    conn.close()

    if not pending_media:
        return

    os.makedirs(settings.MEDIA_DIR, exist_ok=True)
    semaphore = asyncio.Semaphore(5)

    async def bounded_download(session: aiohttp.ClientSession, record):
        media_id = record['id']
        url = record['original_url']
        tweet_id = record['tweet_id']

        async with semaphore:
            filename = f"{media_id}_{get_filename_from_url(url)}"
            relative_dir = str(tweet_id)
            absolute_dir = os.path.join(settings.MEDIA_DIR, relative_dir)
            os.makedirs(absolute_dir, exist_ok=True)
            
            relative_path = os.path.join(relative_dir, filename)
            absolute_path = os.path.join(absolute_dir, filename)

            is_success = await download_file(session, url, absolute_path)
            
            db_conn = get_db_connection()
            db_cursor = db_conn.cursor()
            if is_success:
                db_cursor.execute("UPDATE media SET download_status = 1, local_path = ? WHERE id = ?", (relative_path, media_id))
            else:
                db_cursor.execute("UPDATE media SET download_status = 2 WHERE id = ?", (media_id,))
            db_conn.commit()
            db_conn.close()

    async with aiohttp.ClientSession() as session:
        tasks = [bounded_download(session, record) for record in pending_media]
        await asyncio.gather(*tasks)