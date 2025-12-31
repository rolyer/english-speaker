#!/bin/bash

# 测试消息分页 API
echo "Testing message pagination API..."

# 首先获取一个会话ID（从最近的对话中）
echo -e "\n1. Getting recent conversations..."
CONVERSATIONS=$(curl -s -X GET "http://localhost:8000/api/progress/stats" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" | jq '.recent_conversations[0].id')

echo "Conversation ID: $CONVERSATIONS"

# 测试获取消息（第一页）
echo -e "\n2. Testing first page (offset=0, limit=10)..."
curl -s -X GET "http://localhost:8000/api/chat/conversations/$CONVERSATIONS/messages?offset=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" | jq '.'

# 测试获取消息（第二页）
echo -e "\n3. Testing second page (offset=10, limit=10)..."
curl -s -X GET "http://localhost:8000/api/chat/conversations/$CONVERSATIONS/messages?offset=10&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" | jq '.'

echo -e "\nDone!"
