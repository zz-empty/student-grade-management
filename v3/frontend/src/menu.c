#include "../include/menu.h"
#include "../include/utils.h"
#include <jansson.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ATTEMPTS 3

User *login_menu(int sock) {
  clear_screen();
  printf("========== Student Grade Management System ==========\n");
  printf("                      Login\n");
  printf("====================================================\n");

  int attempts = 0;
  User *user = NULL;

  while (attempts < MAX_ATTEMPTS) {
    char *username = read_string("Username: ");
    if (!username)
      continue;

    char *password = read_password("Password: ");
    if (!password) {
      free(username);
      continue;
    }

    // 构造登录请求
    char request[256];
    snprintf(request, sizeof(request),
             "{\"action\":\"login\",\"username\":\"%s\",\"password\":\"%s\"}",
             username, password);

    // 发送请求并获取响应
    char *response = send_request(sock, request);
    free(username);
    free(password);

    if (!response) {
      attempts++;
      printf("\nLogin failed. Attempts left: %d\n", MAX_ATTEMPTS - attempts);
      pause_program();
      continue;
    }

    // 解析JSON响应
    json_error_t error;
    json_t *root = json_loads(response, 0, &error);

    if (!root) {
      printf("\nInvalid response from server: %s\n", response);
      attempts++;
      pause_program();
      continue;
    }

    json_t *status = json_object_get(root, "status");
    if (status && json_is_string(status) &&
        strcmp(json_string_value(status), "success") == 0) {
      json_t *perm = json_object_get(root, "permission");
      if (perm && json_is_string(perm)) {
        user = malloc(sizeof(User));
        user->username = strdup(username);
        user->permission = strdup(json_string_value(perm));

        printf("\nLogin successful! Welcome %s (%s)\n", user->username,
               user->permission);
        pause_program();
        json_decref(root);
        return user;
      }
    }

    json_t *message = json_object_get(root, "message");
    if (message && json_is_string(message)) {
      printf("\nLogin failed: %s\n", json_string_value(message));
    } else {
      printf("\nLogin failed. Please try again.\n");
    }

    json_decref(root);
    attempts++;
    printf("Attempts left: %d\n", MAX_ATTEMPTS - attempts);
    pause_program();
  }

  printf("\nToo many failed attempts. Exiting.\n");
  return NULL;
}

void main_menu(int sock, User *user) {
  if (!user)
    return;

  if (strcmp(user->permission, "admin") == 0) {
    admin_menu(sock);
  } else {
    user_menu(sock, user->username);
  }
}

void add_student_menu(int sock) {
  clear_screen();
  printf("========== Add Student ==========\n");

  char *student_id = read_string("Student ID: ");
  char *name = read_string("Name: ");
  char *gender = read_string("Gender (男/女): ");
  char *score1_str = read_string("Score 1: ");
  char *score2_str = read_string("Score 2: ");
  char *score3_str = read_string("Score 3: ");

  float score1 = atof(score1_str);
  float score2 = atof(score2_str);
  float score3 = atof(score3_str);

  // 构造请求
  char request[512];
  snprintf(request, sizeof(request),
           "{\"action\":\"add_student\",\"student_id\":\"%s\",\"name\":\"%s\","
           "\"gender\":\"%s\",\"score1\":%.2f,\"score2\":%.2f,\"score3\":%.2f}",
           student_id, name, gender, score1, score2, score3);

  free(student_id);
  free(name);
  free(gender);
  free(score1_str);
  free(score2_str);
  free(score3_str);

  // 发送请求
  char *response = send_request(sock, request);
  if (response) {
    // 解析JSON响应
    json_error_t error;
    json_t *root = json_loads(response, 0, &error);

    if (root) {
      json_t *status = json_object_get(root, "status");
      json_t *message = json_object_get(root, "message");

      if (status && json_is_string(status) &&
          strcmp(json_string_value(status), "success") == 0) {
        printf("\nStudent added successfully!\n");
      } else {
        printf("\nFailed to add student: %s\n",
               message ? json_string_value(message) : "Unknown error");
      }
      json_decref(root);
    } else {
      printf("\nInvalid response: %s\n", response);
    }
  } else {
    printf("\nFailed to add student (connection error)\n");
  }

  pause_program();
}

void delete_student_menu(int sock) {
  clear_screen();
  printf("========== Delete Student ==========\n");

  char *student_id = read_string("Enter Student ID to delete: ");

  // 构造请求
  char request[128];
  snprintf(request, sizeof(request),
           "{\"action\":\"delete_student\",\"student_id\":\"%s\"}", student_id);

  free(student_id);

  // 发送请求
  char *response = send_request(sock, request);
  if (response) {
    // 解析JSON响应
    json_error_t error;
    json_t *root = json_loads(response, 0, &error);

    if (root) {
      json_t *status = json_object_get(root, "status");
      json_t *message = json_object_get(root, "message");

      if (status && json_is_string(status) &&
          strcmp(json_string_value(status), "success") == 0) {
        printf("\nStudent deleted successfully!\n");
      } else {
        printf("\nFailed to delete student: %s\n",
               message ? json_string_value(message) : "Unknown error");
      }
      json_decref(root);
    } else {
      printf("\nInvalid response: %s\n", response);
    }
  } else {
    printf("\nFailed to delete student (connection error)\n");
  }

  pause_program();
}

void update_student_menu(int sock) {
  clear_screen();
  printf("========== Update Student ==========\n");

  char *student_id = read_string("Enter Student ID to update: ");

  // 先获取学生当前信息
  char request[128];
  snprintf(request, sizeof(request),
           "{\"action\":\"get_student\",\"student_id\":\"%s\"}", student_id);

  char *response = send_request(sock, request);
  if (!response) {
    printf("\nFailed to retrieve student information\n");
    free(student_id);
    pause_program();
    return;
  }

  // 解析JSON响应
  json_error_t error;
  json_t *root = json_loads(response, 0, &error);

  if (!root) {
    printf("\nInvalid response: %s\n", response);
    free(student_id);
    pause_program();
    return;
  }

  json_t *data = json_object_get(root, "data");
  if (!data) {
    printf("\nStudent not found\n");
    json_decref(root);
    free(student_id);
    pause_program();
    return;
  }

  // 显示当前信息
  printf("\nCurrent student information:\n");
  printf("Student ID: %s\n", student_id);
  printf("Name: %s\n", json_string_value(json_object_get(data, "name")));
  printf("Gender: %s\n", json_string_value(json_object_get(data, "gender")));
  printf("Score 1: %.2f\n", json_real_value(json_object_get(data, "score1")));
  printf("Score 2: %.2f\n", json_real_value(json_object_get(data, "score2")));
  printf("Score 3: %.2f\n", json_real_value(json_object_get(data, "score3")));

  // 获取新信息
  printf("\nEnter new information (leave blank to keep current value):\n");
  char *new_name = read_string("New name: ");
  char *new_gender = read_string("New gender (男/女): ");
  char *new_score1_str = read_string("New score 1: ");
  char *new_score2_str = read_string("New score 2: ");
  char *new_score3_str = read_string("New score 3: ");

  // 构造更新请求
  snprintf(request, sizeof(request),
           "{\"action\":\"update_student\",\"student_id\":\"%s\","
           "\"name\":\"%s\",\"gender\":\"%s\","
           "\"score1\":%s,\"score2\":%s,\"score3\":%s}",
           student_id,
           new_name ? new_name
                    : json_string_value(json_object_get(data, "name")),
           new_gender ? new_gender
                      : json_string_value(json_object_get(data, "gender")),
           new_score1_str ? new_score1_str : "null",
           new_score2_str ? new_score2_str : "null",
           new_score3_str ? new_score3_str : "null");

  free(student_id);
  free(new_name);
  free(new_gender);
  free(new_score1_str);
  free(new_score2_str);
  free(new_score3_str);
  json_decref(root);

  // 发送更新请求
  char *update_response = send_request(sock, request);
  if (update_response) {
    // 解析JSON响应
    json_error_t error;
    json_t *root = json_loads(update_response, 0, &error);

    if (root) {
      json_t *status = json_object_get(root, "status");
      json_t *message = json_object_get(root, "message");

      if (status && json_is_string(status) &&
          strcmp(json_string_value(status), "success") == 0) {
        printf("\nStudent updated successfully!\n");
      } else {
        printf("\nFailed to update student: %s\n",
               message ? json_string_value(message) : "Unknown error");
      }
      json_decref(root);
    } else {
      printf("\nInvalid response: %s\n", update_response);
    }
  } else {
    printf("\nFailed to update student (connection error)\n");
  }

  pause_program();
}

void view_student_menu(int sock, const char *username) {
  clear_screen();
  printf("========== View Student ==========\n");

  char *student_id = NULL;
  if (username) {
    // 如果是用户查看自己信息
    student_id = strdup(username);
  } else {
    // 如果是管理员查看其他学生
    student_id = read_string("Enter Student ID: ");
  }

  if (!student_id) {
    printf("Invalid student ID\n");
    pause_program();
    return;
  }

  // 构造请求
  char request[128];
  snprintf(request, sizeof(request),
           "{\"action\":\"get_student\",\"student_id\":\"%s\"}", student_id);

  free(student_id);

  // 发送请求
  char *response = send_request(sock, request);
  if (response) {
    // 解析JSON响应
    json_error_t error;
    json_t *root = json_loads(response, 0, &error);

    if (root) {
      json_t *status = json_object_get(root, "status");
      json_t *data = json_object_get(root, "data");

      if (status && json_is_string(status) &&
          strcmp(json_string_value(status), "success") == 0 && data) {
        printf("\nStudent Information:\n");
        printf("Student ID: %s\n",
               json_string_value(json_object_get(data, "student_id")));
        printf("Name: %s\n", json_string_value(json_object_get(data, "name")));
        printf("Gender: %s\n",
               json_string_value(json_object_get(data, "gender")));
        printf("Score 1: %.2f\n",
               json_real_value(json_object_get(data, "score1")));
        printf("Score 2: %.2f\n",
               json_real_value(json_object_get(data, "score2")));
        printf("Score 3: %.2f\n",
               json_real_value(json_object_get(data, "score3")));
        printf("Total Score: %.2f\n",
               json_real_value(json_object_get(data, "score1")) +
                   json_real_value(json_object_get(data, "score2")) +
                   json_real_value(json_object_get(data, "score3")));
      } else {
        json_t *message = json_object_get(root, "message");
        printf("\nFailed to retrieve student: %s\n",
               message ? json_string_value(message) : "Unknown error");
      }
      json_decref(root);
    } else {
      printf("\nInvalid response: %s\n", response);
    }
  } else {
    printf("\nFailed to retrieve student (connection error)\n");
  }

  pause_program();
}

void list_students_menu(int sock) {
  clear_screen();
  printf("========== List All Students ==========\n");

  // 构造请求
  const char *request = "{\"action\":\"list_students\"}";

  // 发送请求
  char *response = send_request(sock, request);
  if (response) {
    // 解析JSON响应
    json_error_t error;
    json_t *root = json_loads(response, 0, &error);

    if (root) {
      json_t *status = json_object_get(root, "status");
      json_t *data = json_object_get(root, "data");

      if (status && json_is_string(status) &&
          strcmp(json_string_value(status), "success") == 0 && data) {
        printf("\n%-12s %-10s %-6s %-8s %-8s %-8s %-8s\n", "Student ID", "Name",
               "Gender", "Score1", "Score2", "Score3", "Total");
        printf(
            "------------------------------------------------------------\n");

        size_t index;
        json_t *value;
        json_array_foreach(data, index, value) {
          printf("%-12s %-10s %-6s %-8.2f %-8.2f %-8.2f %-8.2f\n",
                 json_string_value(json_object_get(value, "student_id")),
                 json_string_value(json_object_get(value, "name")),
                 json_string_value(json_object_get(value, "gender")),
                 json_real_value(json_object_get(value, "score1")),
                 json_real_value(json_object_get(value, "score2")),
                 json_real_value(json_object_get(value, "score3")),
                 json_real_value(json_object_get(value, "score1")) +
                     json_real_value(json_object_get(value, "score2")) +
                     json_real_value(json_object_get(value, "score3")));
        }
      } else {
        json_t *message = json_object_get(root, "message");
        printf("\nFailed to list students: %s\n",
               message ? json_string_value(message) : "Unknown error");
      }
      json_decref(root);
    } else {
      printf("\nInvalid response: %s\n", response);
    }
  } else {
    printf("\nFailed to list students (connection error)\n");
  }

  pause_program();
}

void view_statistics_menu(int sock) {
  clear_screen();
  printf("========== View Statistics ==========\n");

  // 构造请求
  const char *request = "{\"action\":\"get_statistics\"}";

  // 发送请求
  char *response = send_request(sock, request);
  if (response) {
    // 解析JSON响应
    json_error_t error;
    json_t *root = json_loads(response, 0, &error);

    if (root) {
      json_t *status = json_object_get(root, "status");
      json_t *data = json_object_get(root, "data");

      if (status && json_is_string(status) &&
          strcmp(json_string_value(status), "success") == 0 && data) {
        printf("\nSubject Statistics:\n");
        printf("%-10s %-10s %-10s\n", "Subject", "Average", "Max");
        printf("---------------------------------\n");

        for (int i = 1; i <= 3; i++) {
          char subject_key[16];
          snprintf(subject_key, sizeof(subject_key), "subject%d", i);

          json_t *subject = json_object_get(data, subject_key);
          if (subject) {
            printf("%-10d %-10.2f %-10.2f\n", i,
                   json_real_value(json_object_get(subject, "average")),
                   json_real_value(json_object_get(subject, "max")));
          }
        }
      } else {
        json_t *message = json_object_get(root, "message");
        printf("\nFailed to retrieve statistics: %s\n",
               message ? json_string_value(message) : "Unknown error");
      }
      json_decref(root);
    } else {
      printf("\nInvalid response: %s\n", response);
    }
  } else {
    printf("\nFailed to retrieve statistics (connection error)\n");
  }

  pause_program();
}

void change_password_menu(int sock, const char *username) {
  clear_screen();
  printf("========== Change Password ==========\n");

  char *old_password = read_password("Current password: ");
  char *new_password = read_password("New password: ");
  char *confirm_password = read_password("Confirm new password: ");

  if (strcmp(new_password, confirm_password) != 0) {
    printf("\nPasswords do not match!\n");
    free(old_password);
    free(new_password);
    free(confirm_password);
    pause_program();
    return;
  }

  // 构造请求
  char request[256];
  snprintf(request, sizeof(request),
           "{\"action\":\"change_password\",\"username\":\"%s\","
           "\"old_password\":\"%s\",\"new_password\":\"%s\"}",
           username, old_password, new_password);

  free(old_password);
  free(new_password);
  free(confirm_password);

  // 发送请求
  char *response = send_request(sock, request);
  if (response) {
    // 解析JSON响应
    json_error_t error;
    json_t *root = json_loads(response, 0, &error);

    if (root) {
      json_t *status = json_object_get(root, "status");
      json_t *message = json_object_get(root, "message");

      if (status && json_is_string(status) &&
          strcmp(json_string_value(status), "success") == 0) {
        printf("\nPassword changed successfully!\n");
      } else {
        printf("\nFailed to change password: %s\n",
               message ? json_string_value(message) : "Unknown error");
      }
      json_decref(root);
    } else {
      printf("\nInvalid response: %s\n", response);
    }
  } else {
    printf("\nFailed to change password (connection error)\n");
  }

  pause_program();
}

void free_user(User *user) {
  if (user) {
    free(user->username);
    free(user->permission);
    free(user);
  }
}

void admin_menu(int sock) {
  int choice;

  while (1) {
    clear_screen();
    printf("========== Admin Menu ==========\n");
    printf("1. Add Student\n");
    printf("2. Delete Student\n");
    printf("3. Update Student\n");
    printf("4. View Student\n");
    printf("5. List All Students\n");
    printf("6. View Statistics\n");
    printf("7. Change Password\n");
    printf("0. Logout\n");
    printf("===============================\n");

    char *input = read_string("Select option: ");
    if (!input)
      continue;

    choice = atoi(input);
    free(input);

    switch (choice) {
    case 0:
      printf("Logging out...\n");
      return;
    case 1:
      add_student_menu(sock);
      break;
    case 2:
      delete_student_menu(sock);
      break;
    case 3:
      update_student_menu(sock);
      break;
    case 4:
      view_student_menu(sock, NULL);
      break;
    case 5:
      list_students_menu(sock);
      break;
    case 6:
      view_statistics_menu(sock);
      break;
    case 7:
      change_password_menu(sock, "admin");
      break;
    default:
      printf("Invalid option\n");
      pause_program();
    }
  }
}

void user_menu(int sock, const char *username) {
  int choice;

  while (1) {
    clear_screen();
    printf("========== User Menu ==========\n");
    printf("1. View My Information\n");
    printf("2. View All Students\n");
    printf("3. View Statistics\n");
    printf("4. Change Password\n");
    printf("0. Logout\n");
    printf("==============================\n");

    char *input = read_string("Select option: ");
    if (!input)
      continue;

    choice = atoi(input);
    free(input);

    switch (choice) {
    case 0:
      printf("Logging out...\n");
      return;
    case 1:
      view_student_menu(sock, username);
      break;
    case 2:
      list_students_menu(sock);
      break;
    case 3:
      view_statistics_menu(sock);
      break;
    case 4:
      change_password_menu(sock, username);
      break;
    default:
      printf("Invalid option\n");
      pause_program();
    }
  }
}
