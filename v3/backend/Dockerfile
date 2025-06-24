# 使用官方Ubuntu基础镜像
FROM ubuntu:20.04

# 安装必要依赖
RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential \
  libmysqlclient-dev \
  libjansson-dev \
  python3 \
  python3-pip \
  netcat

# 安装Python的MySQL连接器
RUN pip3 install mysql-connector-python

# 设置工作目录
WORKDIR /app

# 复制后端源代码
COPY src/ /app/src/
COPY include/ /app/include/
COPY Makefile config.json /app/

# 清理可能的残留文件并重新编译
RUN make clean && make env


# 暴露后端服务端口
EXPOSE 8888

# 启动脚本：等待数据库就绪后启动后端
CMD ["sh", "-c", "while ! nc -z $DB_HOST 3306; do sleep 1; done && /app/backend_server"]
