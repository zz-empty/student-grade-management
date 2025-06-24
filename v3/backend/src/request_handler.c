#include "../include/request_handler.h"
#include <jansson.h>

RequestType parse_request_type(const char *request) {
  json_error_t error;
  json_t *root = json_loads(request, 0, &error);
  if (!root) {
    fprintf(stderr, "JSON parse error: %s\n", error.text);
    return REQ_UNKNOWN;
  }

  json_t *action = json_object_get(root, "action");
  if (!json_is_string(action)) {
    json_decref(root);
    return REQ_UNKNOWN;
  }

  const char *action_str = json_string_value(action);
  RequestType type = REQ_UNKNOWN;

  if (strcmp(action_str, "login") == 0) {
    type = REQ_LOGIN;
  } else if (strcmp(action_str, "add_student") == 0) {
    type = REQ_ADD_STUDENT;
  } else if (strcmp(action_str, "delete_student") == 0) {
    type = REQ_DELETE_STUDENT;
  } else if (strcmp(action_str, "update_student") == 0) {
    type = REQ_UPDATE_STUDENT;
  } else if (strcmp(action_str, "get_student") == 0) {
    type = REQ_GET_STUDENT;
  } else if (strcmp(action_str, "list_students") == 0) {
    type = REQ_LIST_STUDENTS;
  } else if (strcmp(action_str, "get_statistics") == 0) {
    type = REQ_GET_STATISTICS;
  } else if (strcmp(action_str, "change_password") == 0) {
    type = REQ_CHANGE_PASSWORD;
  }

  json_decref(root);
  return type;
}

char *handle_login(MYSQL *conn, const char *request) {
  json_error_t error;
  json_t *root = json_loads(request, 0, &error);
  if (!root) {
    return strdup("{\"status\":\"error\",\"message\":\"Invalid JSON format\"}");
  }

  json_t *j_username = json_object_get(root, "username");
  json_t *j_password = json_object_get(root, "password");

  if (!json_is_string(j_username) || !json_is_string(j_password)) {
    json_decref(root);
    return strdup(
        "{\"status\":\"error\",\"message\":\"Missing username or password\"}");
  }

  const char *username = json_string_value(j_username);
  const char *password = json_string_value(j_password);

  User *user = authenticate(conn, username, password);
  if (user) {
    char *response = malloc(256);
    snprintf(response, 256, "{\"status\":\"success\",\"permission\":\"%s\"}",
             (user->permission == PERM_ADMIN) ? "admin" : "user");
    free_user(user);
    json_decref(root);
    return response;
  }

  json_decref(root);
  return strdup("{\"status\":\"error\",\"message\":\"Invalid credentials\"}");
}

char *handle_add_student(MYSQL *conn, const char *request) {
  json_error_t error;
  json_t *root = json_loads(request, 0, &error);
  if (!root) {
    return strdup("{\"status\":\"error\",\"message\":\"Invalid JSON format\"}");
  }

  // 验证必需字段
  const char *required_fields[] = {"student_id", "name",   "gender",
                                   "score1",     "score2", "score3"};
  for (int i = 0; i < 6; i++) {
    if (!json_object_get(root, required_fields[i])) {
      json_decref(root);
      char msg[256];
      snprintf(msg, sizeof(msg),
               "{\"status\":\"error\",\"message\":\"Missing field: %s\"}",
               required_fields[i]);
      return strdup(msg);
    }
  }

  Student student;
  student.student_id =
      strdup(json_string_value(json_object_get(root, "student_id")));
  student.name = strdup(json_string_value(json_object_get(root, "name")));
  student.gender = strdup(json_string_value(json_object_get(root, "gender")));
  student.score1 = json_real_value(json_object_get(root, "score1"));
  student.score2 = json_real_value(json_object_get(root, "score2"));
  student.score3 = json_real_value(json_object_get(root, "score3"));

  int result = add_student(conn, &student);
  free_student(&student);
  json_decref(root);

  if (result > 0) {
    return strdup(
        "{\"status\":\"success\",\"message\":\"Student added successfully\"}");
  } else {
    return strdup(
        "{\"status\":\"error\",\"message\":\"Failed to add student\"}");
  }
}

char *handle_delete_student(MYSQL *conn, const char *request) {
  json_error_t error;
  json_t *root = json_loads(request, 0, &error);
  if (!root) {
    return strdup("{\"status\":\"error\",\"message\":\"Invalid JSON format\"}");
  }

  json_t *j_student_id = json_object_get(root, "student_id");
  if (!json_is_string(j_student_id)) {
    json_decref(root);
    return strdup("{\"status\":\"error\",\"message\":\"Missing student_id\"}");
  }

  const char *student_id = json_string_value(j_student_id);
  int result = delete_student(conn, student_id);
  json_decref(root);

  if (result > 0) {
    return strdup("{\"status\":\"success\",\"message\":\"Student deleted "
                  "successfully\"}");
  } else {
    return strdup(
        "{\"status\":\"error\",\"message\":\"Failed to delete student\"}");
  }
}

char *handle_update_student(MYSQL *conn, const char *request) {
  json_error_t error;
  json_t *root = json_loads(request, 0, &error);
  if (!root) {
    return strdup("{\"status\":\"error\",\"message\":\"Invalid JSON format\"}");
  }

  // 验证必需字段
  json_t *j_student_id = json_object_get(root, "student_id");
  if (!json_is_string(j_student_id)) {
    json_decref(root);
    return strdup("{\"status\":\"error\",\"message\":\"Missing student_id\"}");
  }

  Student student;
  student.student_id = strdup(json_string_value(j_student_id));

  // 获取可选的更新字段
  json_t *j_name = json_object_get(root, "name");
  student.name = j_name ? strdup(json_string_value(j_name)) : NULL;

  json_t *j_gender = json_object_get(root, "gender");
  student.gender = j_gender ? strdup(json_string_value(j_gender)) : NULL;

  json_t *j_score1 = json_object_get(root, "score1");
  student.score1 = j_score1 ? json_real_value(j_score1) : -1;

  json_t *j_score2 = json_object_get(root, "score2");
  student.score2 = j_score2 ? json_real_value(j_score2) : -1;

  json_t *j_score3 = json_object_get(root, "score3");
  student.score3 = j_score3 ? json_real_value(j_score3) : -1;

  int result = update_student(conn, &student);
  free_student(&student);
  json_decref(root);

  if (result > 0) {
    return strdup("{\"status\":\"success\",\"message\":\"Student updated "
                  "successfully\"}");
  } else {
    return strdup(
        "{\"status\":\"error\",\"message\":\"Failed to update student\"}");
  }
}

char *handle_get_student(MYSQL *conn, const char *request) {
  json_error_t error;
  json_t *root = json_loads(request, 0, &error);
  if (!root) {
    return strdup("{\"status\":\"error\",\"message\":\"Invalid JSON format\"}");
  }

  json_t *j_student_id = json_object_get(root, "student_id");
  if (!json_is_string(j_student_id)) {
    json_decref(root);
    return strdup("{\"status\":\"error\",\"message\":\"Missing student_id\"}");
  }

  const char *student_id = json_string_value(j_student_id);
  Student *student = get_student(conn, student_id);
  json_decref(root);

  if (!student) {
    return strdup("{\"status\":\"error\",\"message\":\"Student not found\"}");
  }

  json_t *response = json_object();
  json_object_set_new(response, "status", json_string("success"));

  json_t *data = json_object();
  json_object_set_new(data, "student_id", json_string(student->student_id));
  json_object_set_new(data, "name", json_string(student->name));
  json_object_set_new(data, "gender", json_string(student->gender));
  json_object_set_new(data, "score1", json_real(student->score1));
  json_object_set_new(data, "score2", json_real(student->score2));
  json_object_set_new(data, "score3", json_real(student->score3));

  json_object_set_new(response, "data", data);

  char *result = json_dumps(response, JSON_COMPACT);
  json_decref(response);
  free_student(student);

  return result;
}

char *handle_list_students(MYSQL *conn, const char *request) {
  MYSQL_RES *result_set = get_all_students_sorted(conn);
  if (!result_set) {
    return strdup(
        "{\"status\":\"error\",\"message\":\"Failed to retrieve students\"}");
  }

  json_t *response = json_object();
  json_object_set_new(response, "status", json_string("success"));

  json_t *students = json_array();

  MYSQL_ROW row;
  while ((row = mysql_fetch_row(result_set))) {
    json_t *student = json_object();
    json_object_set_new(student, "student_id", json_string(row[0]));
    json_object_set_new(student, "name", json_string(row[1]));
    json_object_set_new(student, "gender", json_string(row[2]));
    json_object_set_new(student, "score1", json_real(atof(row[3])));
    json_object_set_new(student, "score2", json_real(atof(row[4])));
    json_object_set_new(student, "score3", json_real(atof(row[5])));
    json_object_set_new(student, "total",
                        json_real(atof(row[3]) + atof(row[4]) + atof(row[5])));

    json_array_append_new(students, student);
  }

  json_object_set_new(response, "data", students);
  mysql_free_result(result_set);

  char *result = json_dumps(response, JSON_COMPACT);
  json_decref(response);

  return result;
}

char *handle_get_statistics(MYSQL *conn, const char *request) {
  float avg1, max1, avg2, max2, avg3, max3;
  get_statistics(conn, &avg1, &max1, &avg2, &max2, &avg3, &max3);

  json_t *response = json_object();
  json_object_set_new(response, "status", json_string("success"));

  json_t *stats = json_object();
  json_t *subject1 = json_object();
  json_object_set_new(subject1, "average", json_real(avg1));
  json_object_set_new(subject1, "max", json_real(max1));

  json_t *subject2 = json_object();
  json_object_set_new(subject2, "average", json_real(avg2));
  json_object_set_new(subject2, "max", json_real(max2));

  json_t *subject3 = json_object();
  json_object_set_new(subject3, "average", json_real(avg3));
  json_object_set_new(subject3, "max", json_real(max3));

  json_object_set_new(stats, "subject1", subject1);
  json_object_set_new(stats, "subject2", subject2);
  json_object_set_new(stats, "subject3", subject3);

  json_object_set_new(response, "data", stats);

  char *result = json_dumps(response, JSON_COMPACT);
  json_decref(response);

  return result;
}

char *handle_change_password(MYSQL *conn, const char *request) {
  json_error_t error;
  json_t *root = json_loads(request, 0, &error);
  if (!root) {
    return strdup("{\"status\":\"error\",\"message\":\"Invalid JSON format\"}");
  }

  json_t *j_username = json_object_get(root, "username");
  json_t *j_old_password = json_object_get(root, "old_password");
  json_t *j_new_password = json_object_get(root, "new_password");

  if (!json_is_string(j_username) || !json_is_string(j_old_password) ||
      !json_is_string(j_new_password)) {
    json_decref(root);
    return strdup(
        "{\"status\":\"error\",\"message\":\"Missing required fields\"}");
  }

  const char *username = json_string_value(j_username);
  const char *old_password = json_string_value(j_old_password);
  const char *new_password = json_string_value(j_new_password);

  // 验证旧密码
  User *user = authenticate(conn, username, old_password);
  if (!user) {
    json_decref(root);
    return strdup(
        "{\"status\":\"error\",\"message\":\"Invalid old password\"}");
  }
  free_user(user);

  // 更新密码
  if (change_password(conn, username, new_password)) {
    json_decref(root);
    return strdup(
        "{\"status\":\"error\",\"message\":\"Failed to change password\"}");
  }

  json_decref(root);
  return strdup(
      "{\"status\":\"success\",\"message\":\"Password changed successfully\"}");
}
