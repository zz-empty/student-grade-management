#ifndef REQUEST_HANDLER_H
#define REQUEST_HANDLER_H

#include "auth.h"
#include "db.h"
#include "student.h"
#include <jansson.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 请求类型枚举
typedef enum {
  REQ_LOGIN,
  REQ_ADD_STUDENT,
  REQ_DELETE_STUDENT,
  REQ_UPDATE_STUDENT,
  REQ_GET_STUDENT,
  REQ_LIST_STUDENTS,
  REQ_GET_STATISTICS,
  REQ_CHANGE_PASSWORD,
  REQ_UNKNOWN
} RequestType;

// 解析请求类型
RequestType parse_request_type(const char *request);

// 处理登录请求
char *handle_login(MYSQL *conn, const char *request);

// 处理添加学生请求
char *handle_add_student(MYSQL *conn, const char *request);

// 处理删除学生请求
char *handle_delete_student(MYSQL *conn, const char *request);

// 处理更新学生请求
char *handle_update_student(MYSQL *conn, const char *request);

// 处理查询学生请求
char *handle_get_student(MYSQL *conn, const char *request);

// 处理学生列表请求
char *handle_list_students(MYSQL *conn, const char *request);

// 处理统计请求
char *handle_get_statistics(MYSQL *conn, const char *request);

// 处理修改密码请求
char *handle_change_password(MYSQL *conn, const char *request);

#endif
