# 执行测试指令：pytest -v --asyncio-mode=auto
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

# 自动应用于所有测试，将数据库和媒体目录重定向到临时文件夹
@pytest.fixture(autouse=True)
def mock_env(tmp_path):
    test_db = str(tmp_path / "test_archiver.sqlite")
    test_media = str(tmp_path / "test_media")
    
    with patch("app.core.config.settings.DB_PATH", test_db), \
         patch("app.core.config.settings.MEDIA_DIR", test_media), \
         patch("app.main.scheduler.start"), \
         patch("app.main.scheduler.shutdown"):
        yield

# 提供带有生命周期管理的 TestClient，自动触发数据库初始化
@pytest.fixture
def client(mock_env):
    from app.main import app
    with TestClient(app) as c:
        yield c