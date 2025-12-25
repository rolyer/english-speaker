#!/usr/bin/env python3
"""测试配置脚本"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings
from app.core.model_config import model_config

def test_config():
    """测试配置"""
    print("=" * 60)
    print("配置检查")
    print("=" * 60)
    
    print(f"\n默认模型: {settings.DEFAULT_MODEL}")
    print(f"OpenRouter API Key: {'已配置' if settings.OPENROUTER_API_KEY else '未配置'}")
    if settings.OPENROUTER_API_KEY:
        print(f"  - Key前缀: {settings.OPENROUTER_API_KEY[:10]}...")
    print(f"OpenRouter Base URL: {settings.OPENROUTER_BASE_URL}")
    print(f"OpenRouter 默认模型: {settings.OPENROUTER_DEFAULT_MODEL}")
    
    print(f"\nOpenAI API Key: {'已配置' if settings.OPENAI_API_KEY else '未配置'}")
    print(f"Ollama Base URL: {settings.OLLAMA_BASE_URL}")
    
    print("\n" + "=" * 60)
    print("模型配置测试")
    print("=" * 60)
    
    try:
        model_type = model_config.get_model_type()
        print(f"\n当前模型类型: {model_type}")
        
        if model_type.value == "openrouter":
            config = model_config.get_openrouter_config()
            print(f"OpenRouter 配置:")
            print(f"  - API Key: {config['api_key'][:10]}...")
            print(f"  - Base URL: {config['base_url']}")
            print(f"  - Model: {config['model']}")
            print(f"  - Temperature: {config['temperature']}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False
    
    print("\n✅ 配置检查通过!")
    return True

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)

