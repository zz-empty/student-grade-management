#!/bin/bash

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
  $PYTHON_CMD -m pip install rich
fi

# 创建日志记录
mkdir -p logs

# 启动客户端
python cli.py

# 程序结束后暂停
echo "按任意键关闭窗口..."
read -n 1
