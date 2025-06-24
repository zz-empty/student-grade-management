# 使用官方MySQL 8.0镜像
FROM mysql:8.0

# 设置环境变量
ENV MYSQL_ROOT_PASSWORD=StrongPassword123!
ENV MYSQL_DATABASE=student_management
ENV MYSQL_USER=app_user
ENV MYSQL_PASSWORD=AppUserPassword456!

# 复制配置文件
COPY my.cnf /etc/mysql/conf.d/my-custom.cnf

# 复制初始化脚本
COPY init.sql /docker-entrypoint-initdb.d/

# 设置数据卷
VOLUME /var/lib/mysql

# 暴露MySQL端口
EXPOSE 3306

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD mysqladmin ping -u root -p${MYSQL_ROOT_PASSWORD} || exit 1

# 设置启动命令（使用官方入口点）
CMD ["mysqld"]
