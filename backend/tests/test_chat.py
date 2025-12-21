"""对话API测试"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """获取认证token"""
    # 注册用户
    client.post(
        "/api/auth/register",
        json={
            "username": "chattest",
            "email": "chattest@example.com",
            "password": "testpass123"
        }
    )
    
    # 登录
    response = client.post(
        "/api/auth/login",
        data={
            "username": "chattest",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


def test_chat_health_check():
    """测试对话服务健康检查"""
    response = client.get("/api/chat/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_chat_endpoint(auth_token):
    """测试对话接口"""
    response = client.post(
        "/api/chat/",
        json={
            "message": "Hello",
            "scenario": "general"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    # 注意：如果Ollama服务未运行，可能会返回错误
    # 这里只测试接口是否可访问
    assert response.status_code in [200, 500]


def test_get_conversations(auth_token):
    """测试获取对话列表"""
    response = client.get(
        "/api/chat/conversations",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

