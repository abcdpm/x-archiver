def test_get_tweets_empty(client):
    """测试初始状态下数据库为空时的瀑布流接口"""
    response = client.get("/api/tweets?page=1&size=20")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["data"] == []

def test_trigger_sync(client):
    """测试抓取触发接口是否正常返回 200 并启动后台任务"""
    response = client.post("/api/sync", json={"username": "testuser"})
    assert response.status_code == 200
    
    data = response.json()
    assert "Background tasks started" in data["message"]
    assert "testuser" in data["message"]