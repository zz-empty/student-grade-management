#ifndef DB_H
#define DB_H

#include <jansson.h>
#include <mysql/mysql.h>

// 数据库连接信息结构体
typedef struct {
  char *host;
  char *user;
  char *password;
  char *database;
} DBConfig;

// 初始化数据库连接
MYSQL *db_init(DBConfig config);

// 执行SQL查询
MYSQL_RES *db_query(MYSQL *conn, const char *sql);

// 执行SQL命令
int db_execute(MYSQL *conn, const char *sql);

// 从JSON文件加载数据库配置
DBConfig load_db_config(const char *config_file);

// 关闭数据库连接
void db_close(MYSQL *conn);

#endif
