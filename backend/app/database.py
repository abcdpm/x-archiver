import sqlite3
import os
import logging

# 数据库路径：优先从环境变量读取，否则使用默认的本地测试路径
DB_PATH = os.getenv("DB_PATH", "./data/archiver.sqlite")

def get_db_connection():
    # 确保目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使得查询结果可以像字典一样访问
    return conn

def init_db():
    logging.info(f"Initialize database at {DB_PATH}")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 执行我们之前设计的表结构
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS tweets (
            tweet_id TEXT PRIMARY KEY,
            author_name TEXT NOT NULL,
            author_handle TEXT NOT NULL,
            author_avatar TEXT,
            content TEXT,
            post_type TEXT NOT NULL,
            original_url TEXT NOT NULL,
            posted_at DATETIME NOT NULL,
            archived_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id TEXT NOT NULL,
            media_type TEXT NOT NULL,
            original_url TEXT NOT NULL,
            local_path TEXT,
            download_status INTEGER DEFAULT 0,
            FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id) ON DELETE CASCADE
        );
    ''')
    conn.commit()
    conn.close()