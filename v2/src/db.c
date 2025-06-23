#include "../include/db.h"
#include <jansson.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

MYSQL *db_init(DBConfig config) {
  MYSQL *conn = mysql_init(NULL);
  if (conn == NULL) {
    fprintf(stderr, "mysql_init() failed\n");
    return NULL;
  }

  if (mysql_real_connect(conn, config.host, config.user, config.password,
                         config.database, 0, NULL, 0) == NULL) {
    fprintf(stderr, "mysql_real_connect() failed: %s\n", mysql_error(conn));
    mysql_close(conn);
    return NULL;
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

  DBConfig config;
  config.host = strdup(json_string_value(json_object_get(root, "host")));
  config.user = strdup(json_string_value(json_object_get(root, "user")));
  config.password =
      strdup(json_string_value(json_object_get(root, "password")));
  config.database =
      strdup(json_string_value(json_object_get(root, "database")));

  json_decref(root);
  return config;
}

void db_close(MYSQL *conn) { mysql_close(conn); }
