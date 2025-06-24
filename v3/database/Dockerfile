# 使用官方MySQL 8.0镜像
FROM mysql:8.0

# 复制配置文件
COPY my.cnf /etc/mysql/conf.d/my-custom.cnf

# 复制初始化脚本
COPY init.sql /docker-entrypoint-initdb.d/

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD mysqladmin ping -u root -p${MYSQL_ROOT_PASSWORD} || exit 1
