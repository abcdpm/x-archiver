import pytest
from unittest.mock import AsyncMock, patch
from app.services.scraper import sync_favorited_tweets
from app.services.downloader import get_filename_from_url

@pytest.mark.asyncio
async def test_sync_user_not_found():
    """测试 twscrape 未找到用户时的错误处理逻辑"""
    with patch("app.services.scraper.API") as MockAPI:
        # 拦截 API.user_by_login 并强制返回 None
        mock_instance = MockAPI.return_value
        mock_instance.user_by_login = AsyncMock(return_value=None)
        
        result = await sync_favorited_tweets("nonexistent_user")
        assert result["status"] == "error"
        assert result["message"] == "User not found"

def test_get_filename_from_url():
    """测试从 X 平台特殊的 URL 结构中正确提取文件名与后缀"""
    # 场景 1: 带 format 参数的 URL
    url1 = "https://pbs.twimg.com/media/F_xxx?format=jpg&name=large"
    assert get_filename_from_url(url1) == "F_xxx.jpg"
    
    # 场景 2: 已自带后缀的 URL
    url2 = "https://pbs.twimg.com/media/F_yyy.png"
    assert get_filename_from_url(url2) == "F_yyy.png"