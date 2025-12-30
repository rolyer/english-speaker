#!/bin/bash

echo "======================================"
echo "安装 Whisper 本地语音识别"
echo "======================================"
echo ""

# 检查是否在项目根目录
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查 Python
echo "1. 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi
echo "✅ Python 版本: $(python3 --version)"
echo ""

# 检查 FFmpeg
echo "2. 检查 FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg 未安装"
    echo "请运行以下命令安装："
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  brew install ffmpeg"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  sudo apt update && sudo apt install ffmpeg"
    fi
    echo ""
    read -p "是否继续安装 Python 依赖？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ FFmpeg 已安装: $(ffmpeg -version | head -n1)"
fi
echo ""

# 安装 Python 依赖
echo "3. 安装 Python 依赖..."
cd backend
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 安装成功！"
    echo ""
    echo "======================================"
    echo "下一步："
    echo "======================================"
    echo "1. 启动后端服务："
    echo "   cd backend"
    echo "   uvicorn app.main:app --reload"
    echo ""
    echo "2. 首次运行时会自动下载 Whisper 模型（约 74 MB）"
    echo ""
    echo "3. 查看完整文档："
    echo "   cat ../WHISPER_SETUP.md"
    echo "======================================"
else
    echo ""
    echo "❌ 安装失败，请检查错误信息"
    exit 1
fi

