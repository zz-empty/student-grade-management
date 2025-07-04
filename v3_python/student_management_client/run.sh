#!/bin/bash

# 创建日志记录
mkdir -p logs

# 启动客户端
python cli.py

# 程序结束后暂停
echo "按任意键关闭窗口..."
read -n 1
