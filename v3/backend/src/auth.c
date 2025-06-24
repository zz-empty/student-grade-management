#include "../include/auth.h"
#include <openssl/sha.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

User *authenticate(MYSQL *conn, const char *username, const char *password) {
  char query[512];
  snprintf(query, sizeof(query),
           "SELECT permission FROM accounts WHERE username = '%s' AND password "
           "= SHA2('%s', 256)",
           username, password);

  if (mysql_query(conn, query)) {
    fprintf(stderr, "Query error: %s\n", mysql_error(conn));
    return NULL;
  }

  MYSQL_RES *result = mysql_store_result(conn);
  if (result == NULL) {
    return NULL;
  }

  MYSQL_ROW row = mysql_fetch_row(result);
  if (row == NULL) {
    mysql_free_result(result);
    return NULL;
  }

  User *user = malloc(sizeof(User));
  user->username = strdup(username);

  if (strcmp(row[0], "admin") == 0) {
    user->permission = PERM_ADMIN;
  } else if (strcmp(row[0], "user") == 0) {
    user->permission = PERM_USER;
  } else {
    user->permission = PERM_UNKNOWN;
  }

  mysql_free_result(result);
  return user;
}

int change_password(MYSQL *conn, const char *username,
                    const char *new_password) {
  char query[256];
  snprintf(
      query, sizeof(query),
      "UPDATE accounts SET password = SHA2('%s', 256) WHERE username = '%s'",
      new_password, username);

  if (mysql_query(conn, query)) {
    fprintf(stderr, "Password change failed: %s\n", mysql_error(conn));
    return -1;
  }

  if (mysql_affected_rows(conn) == 0) {
    fprintf(stderr, "No such user: %s\n", username);
    return -1;
  }

  return 0;
}

void free_user(User *user) {
  if (user) {
    free(user->username);
    free(user);
  }
}
