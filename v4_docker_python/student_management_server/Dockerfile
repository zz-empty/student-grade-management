# 使用官方 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
  gcc \
  default-libmysqlclient-dev \
  && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 8888

# 设置启动命令
CMD ["python", "main.py"]
