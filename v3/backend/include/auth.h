#ifndef AUTH_H
#define AUTH_H

#include <mysql/mysql.h>

// 用户权限枚举
typedef enum { PERM_ADMIN, PERM_USER, PERM_UNKNOWN } Permission;

// 用户结构体
typedef struct {
  char *username;
  Permission permission;
} User;

// 登录验证
User *authenticate(MYSQL *conn, const char *username, const char *password);

// 更改密码
int change_password(MYSQL *conn, const char *username,
                    const char *new_password);

// 释放用户结构体
void free_user(User *user);

#endif
