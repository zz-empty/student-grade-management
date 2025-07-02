#!/bin/bash

# 停止学生成绩管理系统服务器

# 查找服务器进程ID
SERVER_PID=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}')

if [ -z "$SERVER_PID" ]; then
  echo "服务器未运行"
  exit 0
fi

# 发送SIGTERM信号
echo "正在停止服务器 (PID: $SERVER_PID)..."
kill -SIGTERM $SERVER_PID

# 等待最多10秒
TIMEOUT=10
while [ $TIMEOUT -gt 0 ]; do
  if ! ps -p $SERVER_PID >/dev/null; then
    echo "服务器已停止"
    exit 0
  fi
  sleep 1
  TIMEOUT=$((TIMEOUT - 1))
done

# 强制终止
echo "服务器未响应，强制终止..."
kill -9 $SERVER_PID
echo "服务器已强制终止"
