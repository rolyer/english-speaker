#!/usr/bin/env python3
"""测试 Emoji 过滤功能"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.tts_service import remove_emojis

def test_emoji_removal():
    """测试 emoji 移除功能"""
    test_cases = [
        ("Hello! 😊 How are you?", "Hello!  How are you?"),
        ("I'm so happy to see you today! 🌟", "I'm so happy to see you today! "),
        ("Goodbye! 👋", "Goodbye! "),
        ("Hello 😊 I'm very happy 🎉 to talk with you! 🌟", "Hello  I'm very happy  to talk with you! "),
        ("No emojis here", "No emojis here"),
        ("😊😊😊", ""),
        ("你好 👋 世界 🌍", "你好  世界 "),
    ]
    
    print("=" * 60)
    print("测试 Emoji 过滤功能")
    print("=" * 60)
    
    all_passed = True
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = remove_emojis(input_text)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n测试 {i}: {status}")
        print(f"  输入: {input_text}")
        print(f"  期望: {expected}")
        print(f"  结果: {result}")
        
        if not passed:
            print(f"  差异: 期望长度={len(expected)}, 实际长度={len(result)}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_emoji_removal()
    sys.exit(0 if success else 1)

