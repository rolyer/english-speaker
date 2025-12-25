#!/bin/bash

# 设置UTF-8编码环境
export PYTHONIOENCODING=utf-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# 启动应用
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

