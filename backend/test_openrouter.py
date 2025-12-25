#!/usr/bin/env python3
"""测试OpenRouter API"""
import sys
import os
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai_service import ai_service

async def test_openrouter():
    """测试OpenRouter API"""
    print("=" * 60)
    print("测试 OpenRouter API")
    print("=" * 60)
    
    try:
        print("\n发送测试消息...")
        response = ""
        async for chunk in ai_service.stream_chat(
            user_message="Hello, how are you?",
            model_type="openrouter"
        ):
            response += chunk
            print(chunk, end="", flush=True)
        
        print(f"\n\n完整响应: {response}")
        print("\n✅ 测试成功!")
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openrouter())
    sys.exit(0 if success else 1)

