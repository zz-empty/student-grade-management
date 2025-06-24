#include "../include/db.h"

MYSQL *db_init(DBConfig config) {
  MYSQL *conn = mysql_init(NULL);
  if (conn == NULL) {
    fprintf(stderr, "mysql_init() failed\n");
    return NULL;
  }

  // 设置连接超时时间为5秒
  unsigned int timeout = 5;
  mysql_options(conn, MYSQL_OPT_CONNECT_TIMEOUT, &timeout);

  if (mysql_real_connect(conn, config.host, config.user, config.password,
                         config.database, 0, NULL,
                         CLIENT_MULTI_STATEMENTS) == NULL) {
    fprintf(stderr, "mysql_real_connect() failed: %s\n", mysql_error(conn));
    mysql_close(conn);
    return NULL;
  }

  // 设置字符集为UTF-8
  if (mysql_set_character_set(conn, "utf8mb4")) {
    fprintf(stderr, "Error setting charset: %s\n", mysql_error(conn));
  }

  return conn;
}

MYSQL_RES *db_query(MYSQL *conn, const char *sql) {
  if (mysql_query(conn, sql)) {
    fprintf(stderr, "Query error: %s\n", mysql_error(conn));
    return NULL;
  }
  return mysql_store_result(conn);
}

int db_execute(MYSQL *conn, const char *sql) {
  if (mysql_query(conn, sql)) {
    fprintf(stderr, "Execute error: %s\n", mysql_error(conn));
    return -1;
  }
  return mysql_affected_rows(conn);
}

DBConfig load_db_config(const char *config_file) {
  FILE *fp = fopen(config_file, "r");
  if (!fp) {
    perror("Failed to open config file");
    exit(1);
  }

  fseek(fp, 0, SEEK_END);
  long size = ftell(fp);
  fseek(fp, 0, SEEK_SET);
  char *json_str = malloc(size + 1);
  fread(json_str, 1, size, fp);
  fclose(fp);
  json_str[size] = '\0';

  json_error_t error;
  json_t *root = json_loads(json_str, 0, &error);
  free(json_str);

  if (!root) {
    fprintf(stderr, "JSON error on line %d: %s\n", error.line, error.text);
    exit(1);
  }

  json_t *db_config = json_object_get(root, "database");
  if (!db_config) {
    fprintf(stderr, "Missing 'database' section in config\n");
    exit(1);
  }

  DBConfig config;
  config.host = strdup(json_string_value(json_object_get(db_config, "host")));
  config.user = strdup(json_string_value(json_object_get(db_config, "user")));
  config.password =
      strdup(json_string_value(json_object_get(db_config, "password")));
  config.database =
      strdup(json_string_value(json_object_get(db_config, "database")));

  json_decref(root);
  return config;
}

DBConfig load_db_config_from_env() {
  DBConfig config;

  // 从环境变量获取配置，如果不存在则使用默认值
  config.host =
      getenv("DB_HOST") ? strdup(getenv("DB_HOST")) : strdup("database");
  config.user = getenv("DB_USER") ? strdup(getenv("DB_USER")) : strdup("root");
  config.password = getenv("DB_PASSWORD") ? strdup(getenv("DB_PASSWORD"))
                                          : strdup("mysqlpassword");
  config.database = getenv("DB_NAME") ? strdup(getenv("DB_NAME"))
                                      : strdup("student_management");

  return config;
}

void db_close(MYSQL *conn) { mysql_close(conn); }
