#!/bin/bash

# 启动学生成绩管理系统服务器

# 检查Python版本
PYTHON_CMD="python3"
if ! command -v $PYTHON_CMD &>/dev/null; then
  PYTHON_CMD="python"
fi

# 检查依赖
echo "检查Python依赖..."
$PYTHON_CMD -c "import mysql.connector" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "安装缺失的Python依赖..."
  $PYTHON_CMD -m pip install mysql-connector-python cryptography
fi

# 设置日志目录
LOG_DIR="logs"
mkdir -p $LOG_DIR

# 启动服务器
echo "启动服务器..."
$PYTHON_CMD main.py

# 等待服务器关闭
wait
echo "服务器已停止"
