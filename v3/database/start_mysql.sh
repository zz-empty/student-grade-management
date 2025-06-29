#!/bin/bash

# 解决locale警告
unset LC_ALL
export LANG=C.UTF-8

# 容器配置
CONTAINER_NAME="v3mysql"
NETWORK_NAME="net-v3"
INIT_SCRIPT="${HOME}/workSpace/student-grade-management/v3/database/init.sql"
VOLUME_NAME="v3_mysql_data"

# 用户配置
MYSQL_ROOT_PASSWORD="v3mysql"
MYSQL_USER="v3mysql_usr"
MYSQL_USER_PASSWORD="v3mysql_usr_pwd"
MYSQL_DATABASE="student_grade_db"

# 检查并删除同名容器
if docker container inspect ${CONTAINER_NAME} >/dev/null 2>&1; then
  echo "删除已存在的容器: ${CONTAINER_NAME}"
  docker stop ${CONTAINER_NAME} >/dev/null
  docker rm ${CONTAINER_NAME} >/dev/null
fi

# 创建网络（如果不存在）
if ! docker network inspect ${NETWORK_NAME} >/dev/null 2>&1; then
  echo "创建网络: ${NETWORK_NAME}"
  docker network create ${NETWORK_NAME}
fi

# 运行MySQL容器
echo "启动MySQL容器..."
docker run -d \
  --name ${CONTAINER_NAME} \
  -p 3306:3306 \
  -v ${VOLUME_NAME}:/var/lib/mysql \
  -v "${INIT_SCRIPT}:/docker-entrypoint-initdb.d/init.sql" \
  -e MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
  -e MYSQL_USER=${MYSQL_USER} \
  -e MYSQL_PASSWORD=${MYSQL_USER_PASSWORD} \
  -e MYSQL_DATABASE=${MYSQL_DATABASE} \
  --network ${NETWORK_NAME} \
  --network-alias mysql \
  mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 等待初始化完成
echo -n "等待数据库初始化"
for i in {1..30}; do
  if docker logs ${CONTAINER_NAME} 2>&1 | grep -q "MySQL init process done. Ready for start up"; then
    break
  fi
  sleep 1
  echo -n "."
done
echo

# 等待额外几秒确保MySQL完全启动
sleep 3

# 创建用户并授予权限
echo "创建普通用户并设置权限..."
docker exec -i ${CONTAINER_NAME} sh -c "exec mysql -uroot -p${MYSQL_ROOT_PASSWORD} -e \"
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_USER_PASSWORD}';
GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
\""

# 验证普通用户访问
echo ""
echo "验证普通用户访问权限..."
docker exec -i ${CONTAINER_NAME} sh -c "exec mysql -u${MYSQL_USER} -p${MYSQL_USER_PASSWORD} -e \"
USE ${MYSQL_DATABASE};
SHOW TABLES;
SELECT COUNT(*) FROM accounts;
\""

echo ""
echo "MySQL容器已启动："
echo "容器名称: ${CONTAINER_NAME}"
echo "数据库名: ${MYSQL_DATABASE}"
echo "普通用户: ${MYSQL_USER}"
echo "普通用户密码: ${MYSQL_USER_PASSWORD}"
echo "端口: 3306"
echo "网络: ${NETWORK_NAME} (别名: mysql)"
echo "数据卷: ${VOLUME_NAME}"
echo ""
echo "重要提示: 不再使用 root 用户进行应用连接"
echo "应用连接应使用用户: ${MYSQL_USER} 密码: ${MYSQL_USER_PASSWORD}"
