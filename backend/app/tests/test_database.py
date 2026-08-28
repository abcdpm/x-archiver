import sqlite3
from app.database import get_db_connection, init_db

def test_database_initialization():
    """验证表结构是否被正确创建"""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert "tweets" in tables
    assert "media" in tables
    
    conn.close()