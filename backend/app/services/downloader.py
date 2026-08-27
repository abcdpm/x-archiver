import os
import logging
import asyncio
import aiohttp
import aiofiles
from urllib.parse import urlparse, parse_qs
from app.database import get_db_connection

# 媒体存放的根目录，可以通过环境变量指定
MEDIA_DIR = os.getenv("MEDIA_DIR", "./media")

def get_filename_from_url(url: str) -> str:
    """
    解析 Twitter 媒体 URL 获取正确的文件名和后缀。
    例如: https://pbs.twimg.com/media/F_xxx?format=jpg&name=large -> F_xxx.jpg
    """
    parsed_url = urlparse(url)
    base_name = os.path.basename(parsed_url.path)
    
    # 提取格式参数作为文件扩展名
    qs = parse_qs(parsed_url.query)
    if 'format' in qs:
        ext = qs['format'][0]
        if not base_name.endswith(f".{ext}"):
            base_name = f"{base_name}.{ext}"
            
    return base_name

async def download_file(session: aiohttp.ClientSession, url: str, dest_path: str) -> bool:
    """流式下载单个文件"""
    try:
        async with session.get(url, timeout=60) as response:
            if response.status == 200:
                # 使用 aiofiles 分块异步写入，1MB 一个 chunk，安全处理大型视频
                async with aiofiles.open(dest_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024 * 1024):
                        await f.write(chunk)
                return True
            else:
                logging.error(f"Download failed for {url} with status: {response.status}")
                return False
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")
        return False

async def process_media_downloads():
    """
    检索数据库中未下载的媒体并执行并发下载。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查找所有状态为 0 (等待下载) 的媒体
    cursor.execute("SELECT id, original_url, tweet_id FROM media WHERE download_status = 0")
    pending_media = cursor.fetchall()
    conn.close()

    if not pending_media:
        logging.info("No pending media to download.")
        return {"status": "success", "message": "No pending media"}

    logging.info(f"Found {len(pending_media)} media files to download. Starting...")
    
    os.makedirs(MEDIA_DIR, exist_ok=True)
    
    # 限制最大并发数为 5，避免被平台限流或占用过多本地网络/磁盘 IO
    semaphore = asyncio.Semaphore(5)
    success_count = 0
    failed_count = 0

    async def bounded_download(session: aiohttp.ClientSession, record):
        nonlocal success_count, failed_count
        media_id = record['id']
        url = record['original_url']
        tweet_id = record['tweet_id']

        async with semaphore:
            # 按照 tweet_id 创建子文件夹组织文件： /media/tweet_id/filename.jpg
            filename = get_filename_from_url(url)
            # 加上 media_id 前缀确保文件名绝对唯一
            local_filename = f"{media_id}_{filename}"
            
            relative_dir = str(tweet_id)
            absolute_dir = os.path.join(MEDIA_DIR, relative_dir)
            os.makedirs(absolute_dir, exist_ok=True)
            
            relative_path = os.path.join(relative_dir, local_filename)
            absolute_path = os.path.join(absolute_dir, local_filename)

            logging.info(f"Downloading: {filename}...")
            is_success = await download_file(session, url, absolute_path)
            
            # 单个文件下载完成后，立即短暂连接数据库更新状态
            # 这比全部下载完再一次性更新更安全，如果程序中断不会丢失进度
            db_conn = get_db_connection()
            db_cursor = db_conn.cursor()
            if is_success:
                db_cursor.execute(
                    "UPDATE media SET download_status = 1, local_path = ? WHERE id = ?", 
                    (relative_path, media_id)
                )
                success_count += 1
            else:
                db_cursor.execute(
                    "UPDATE media SET download_status = 2 WHERE id = ?", 
                    (media_id,)
                )
                failed_count += 1
            db_conn.commit()
            db_conn.close()

    # 使用同一个 session 复用 TCP 连接，提高下载效率
    async with aiohttp.ClientSession() as session:
        tasks = [bounded_download(session, record) for record in pending_media]
        # 等待所有下载任务完成
        await asyncio.gather(*tasks)

    logging.info(f"Download task complete! Success: {success_count}, Failed: {failed_count}")
    return {"status": "success", "downloaded": success_count, "failed": failed_count}