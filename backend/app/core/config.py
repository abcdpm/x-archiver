import os

class Settings:
    # 数据库与媒体文件路径，优先从环境变量获取
    DB_PATH: str = os.getenv("DB_PATH", "/app/database/archiver.sqlite")
    MEDIA_DIR: str = os.getenv("MEDIA_DIR", "/app/media")
    # 默认定时抓取的 X 账号
    TARGET_USERNAME: str = os.getenv("TARGET_USERNAME", "elonmusk")

settings = Settings()