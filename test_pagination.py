#!/usr/bin/env python3
"""
Dashboard 分页功能测试脚本

用法:
1. 确保后端服务正在运行
2. 修改 TOKEN 为你的认证令牌
3. 运行: python test_pagination.py
"""

import requests
import time

# 配置
BASE_URL = "http://localhost:8000"
TOKEN = "your_auth_token_here"  # 替换为实际的 token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def test_pagination():
    """测试分页功能"""
    print("=" * 60)
    print("Dashboard 分页功能测试")
    print("=" * 60)
    
    # 测试 1: 获取第一页
    print("\n[测试 1] 获取第一页（offset=0, limit=5）")
    response = requests.get(
        f"{BASE_URL}/api/progress/stats",
        params={"days": 7, "offset": 0, "limit": 5},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 状态码: {response.status_code}")
        print(f"   对话数量: {len(data.get('recent_conversations', []))}")
        print(f"   总对话数: {data.get('total_conversations', 0)}")
        print(f"   还有更多: {data.get('has_more', False)}")
        
        if data.get('recent_conversations'):
            first_conv = data['recent_conversations'][0]
            print(f"   第一条: ID={first_conv['id']}, 场景={first_conv['scenario']}")
    else:
        print(f"❌ 失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return
    
    # 测试 2: 获取第二页
    print("\n[测试 2] 获取第二页（offset=5, limit=5）")
    response = requests.get(
        f"{BASE_URL}/api/progress/stats",
        params={"days": 7, "offset": 5, "limit": 5},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 状态码: {response.status_code}")
        print(f"   对话数量: {len(data.get('recent_conversations', []))}")
        print(f"   还有更多: {data.get('has_more', False)}")
        
        if data.get('recent_conversations'):
            first_conv = data['recent_conversations'][0]
            print(f"   第一条: ID={first_conv['id']}, 场景={first_conv['scenario']}")
    else:
        print(f"❌ 失败: {response.status_code}")
    
    # 测试 3: 获取超出范围的页
    print("\n[测试 3] 获取超出范围的页（offset=1000, limit=5）")
    response = requests.get(
        f"{BASE_URL}/api/progress/stats",
        params={"days": 7, "offset": 1000, "limit": 5},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 状态码: {response.status_code}")
        print(f"   对话数量: {len(data.get('recent_conversations', []))}")
        print(f"   还有更多: {data.get('has_more', False)}")
        
        if len(data.get('recent_conversations', [])) == 0:
            print("   ✅ 正确返回空列表")
        if not data.get('has_more', True):
            print("   ✅ 正确标记 has_more=False")
    else:
        print(f"❌ 失败: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


def create_test_conversations(count=15):
    """创建测试对话数据"""
    print(f"\n创建 {count} 个测试对话...")
    
    scenarios = ['general', 'school', 'home', 'shopping', 'travel']
    
    for i in range(count):
        scenario = scenarios[i % len(scenarios)]
        response = requests.post(
            f"{BASE_URL}/api/chat/",
            json={
                "message": f"Test message {i+1}",
                "scenario": scenario
            },
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ 创建对话 {i+1}/{count}")
        else:
            print(f"❌ 创建失败 {i+1}/{count}: {response.status_code}")
        
        time.sleep(0.5)  # 避免请求过快
    
    print(f"\n✅ 完成！创建了 {count} 个测试对话")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        # 创建测试数据
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        create_test_conversations(count)
    else:
        # 运行测试
        test_pagination()
    
    print("\n提示:")
    print("- 如需创建测试数据: python test_pagination.py create [数量]")
    print("- 如需测试分页: python test_pagination.py")
    print("- 记得替换脚本中的 TOKEN 为实际的认证令牌")

