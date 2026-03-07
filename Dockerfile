# Symphony v{version} Docker安装
# 使用: docker-compose up -d

version: '3.8'

services:
  symphony:
    image: python:3.9-slim
    working_dir: /app
    volumes:
      - ./config.py:/app/config.py
      - ./data:/app/data
    command: python symphony_core.py
    environment:
      - PYTHONUNBUFFERED=1
