#include "../include/menu.h"
#include "../include/student.h"
#include "../include/utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ATTEMPTS 3

User *login_ui(MYSQL *conn) {
  int attempts = 0;
  User *user = NULL;

  clear_screen();
  printf("========== 学生成绩管理系统 ==========\n");
  printf("              登录界面\n");
  printf("======================================\n");

  while (attempts < MAX_ATTEMPTS) {
    char *username = read_string("用户名: ", 50);
    char *password = get_password("密码: ");

    user = authenticate(conn, username, password);

    free(username);
    free(password);

    if (user != NULL) {
      printf("\n登录成功!\n");
      pause_program();
      return user;
    }

    attempts++;
    printf("\n用户名或密码错误! 剩余尝试次数: %d\n\n", MAX_ATTEMPTS - attempts);
  }

  printf("\n登录失败次数过多，系统退出!\n");
  return NULL;
}

void main_menu(MYSQL *conn, User *user) {
  if (user == NULL)
    return;

  if (user->permission == PERM_ADMIN) {
    admin_menu(conn);
  } else {
    user_menu(conn, user->username);
  }
}

// 添加学生界面
void add_student_ui(MYSQL *conn) {
  clear_screen();
  printf("========== 添加学生 ==========\n");

  Student *student = malloc(sizeof(Student));
  student->student_id = read_string("学号: ", 20);
  student->name = read_string("姓名: ", 50);
  student->gender = read_string("性别(男/女): ", 10);
  student->score1 = read_float("分数1: ");
  student->score2 = read_float("分数2: ");
  student->score3 = read_float("分数3: ");

  if (add_student(conn, student)) {
    printf("\n学生添加成功!\n");
  } else {
    printf("\n添加失败!\n");
  }

  free_student(student);
  pause_program();
}

// 删除学生界面
void delete_student_ui(MYSQL *conn) {
  clear_screen();
  printf("========== 删除学生 ==========\n");

  char *student_id = read_string("请输入要删除的学生学号: ", 20);

  if (delete_student(conn, student_id)) {
    printf("\n学生删除成功!\n");
  } else {
    printf("\n删除失败! 学号不存在?\n");
  }

  free(student_id);
  pause_program();
}

// 更新学生界面
void update_student_ui(MYSQL *conn) {
  clear_screen();
  printf("========== 修改学生信息 ==========\n");

  char *student_id = read_string("请输入要修改的学生学号: ", 20);
  Student *student = get_student(conn, student_id);

  if (student == NULL) {
    printf("找不到该学生!\n");
    free(student_id);
    pause_program();
    return;
  }

  printf("\n当前学生信息:\n");
  printf("学号: %s\n", student->student_id);
  printf("姓名: %s\n", student->name);
  printf("性别: %s\n", student->gender);
  printf("分数1: %.2f\n", student->score1);
  printf("分数2: %.2f\n", student->score2);
  printf("分数3: %.2f\n", student->score3);
  printf("\n");

  // 更新信息
  free(student->name);
  free(student->gender);

  student->name = read_string("新姓名: ", 50);
  student->gender = read_string("新性别(男/女): ", 10);
  student->score1 = read_float("新分数1: ");
  student->score2 = read_float("新分数2: ");
  student->score3 = read_float("新分数3: ");

  if (update_student(conn, student)) {
    printf("\n学生信息更新成功!\n");
  } else {
    printf("\n更新失败!\n");
  }

  free(student_id);
  free_student(student);
  pause_program();
}

// 查询学生界面
void query_student_ui(MYSQL *conn) {
  clear_screen();
  printf("========== 查询学生信息 ==========\n");

  char *student_id = read_string("请输入学生学号: ", 20);
  Student *student = get_student(conn, student_id);

  if (student) {
    printf("\n学生信息:\n");
    printf("学号: %s\n", student->student_id);
    printf("姓名: %s\n", student->name);
    printf("性别: %s\n", student->gender);
    printf("分数1: %.2f\n", student->score1);
    printf("分数2: %.2f\n", student->score2);
    printf("分数3: %.2f\n", student->score3);
    printf("总分: %.2f\n", student->score1 + student->score2 + student->score3);
  } else {
    printf("\n找不到该学生!\n");
  }

  free(student_id);
  if (student)
    free_student(student);
  pause_program();
}

// 学生列表界面
void list_students_ui(MYSQL *conn) {
  clear_screen();
  printf("========== 学生成绩列表（按总分排序） ==========\n");

  MYSQL_RES *result = get_all_students_sorted(conn);
  if (result == NULL) {
    printf("获取数据失败!\n");
    pause_program();
    return;
  }

  int num_fields = mysql_num_fields(result);
  MYSQL_ROW row;

  printf("\n%-10s %-10s %-6s %-8s %-8s %-8s %-8s\n", "学号", "姓名", "性别",
         "分数1", "分数2", "分数3", "总分");
  printf("------------------------------------------------------------\n");

  while ((row = mysql_fetch_row(result))) {
    float total = atof(row[3]) + atof(row[4]) + atof(row[5]);
    printf("%-10s %-10s %-6s %-8.2f %-8.2f %-8.2f %-8.2f\n", row[0], row[1],
           row[2], atof(row[3]), atof(row[4]), atof(row[5]), total);
  }

  mysql_free_result(result);
  pause_program();
}

// 成绩统计界面
void show_statistics_ui(MYSQL *conn) {
  clear_screen();
  printf("========== 成绩统计 ==========\n");

  float avg1, max1, avg2, max2, avg3, max3;
  get_statistics(conn, &avg1, &max1, &avg2, &max2, &avg3, &max3);

  printf("\n科目\t平均分\t最高分\n");
  printf("----------------------------\n");
  printf("科目1\t%.2f\t%.2f\n", avg1, max1);
  printf("科目2\t%.2f\t%.2f\n", avg2, max2);
  printf("科目3\t%.2f\t%.2f\n", avg3, max3);

  pause_program();
}

// 修改密码界面
void change_password_ui(MYSQL *conn, const char *username) {
  clear_screen();
  printf("========== 修改密码 ==========\n");

  char *old_password = get_password("当前密码: ");
  char *new_password = get_password("新密码: ");
  char *confirm_password = get_password("确认新密码: ");

  if (strcmp(new_password, confirm_password) != 0) {
    printf("\n两次输入的密码不一致!\n");
    free(old_password);
    free(new_password);
    free(confirm_password);
    pause_program();
    return;
  }

  // 验证旧密码
  User *user = authenticate(conn, username, old_password);
  if (user == NULL) {
    printf("\n当前密码错误!\n");
    free(old_password);
    free(new_password);
    free(confirm_password);
    pause_program();
    return;
  }

  free_user(user);

  if (change_password(conn, username, new_password)) {
    printf("\n密码修改失败!\n");
  } else {
    printf("\n密码修改成功!\n");
  }

  free(old_password);
  free(new_password);
  free(confirm_password);
  pause_program();
}

void admin_menu(MYSQL *conn) {
  int choice;

  while (1) {
    clear_screen();
    printf("========== 管理员菜单 ==========\n");
    printf("1. 添加学生\n");
    printf("2. 删除学生\n");
    printf("3. 修改学生信息\n");
    printf("4. 查询学生信息\n");
    printf("5. 查看所有学生成绩（总分排序）\n");
    printf("6. 查看成绩统计\n");
    printf("7. 修改密码\n");
    printf("0. 退出系统\n");
    printf("===============================\n");

    choice = read_int("请选择操作: ");

    switch (choice) {
    case 1:
      add_student_ui(conn);
      break;
    case 2:
      delete_student_ui(conn);
      break;
    case 3:
      update_student_ui(conn);
      break;
    case 4:
      query_student_ui(conn);
      break;
    case 5:
      list_students_ui(conn);
      break;
    case 6:
      show_statistics_ui(conn);
      break;
    case 7:
      change_password_ui(conn, "admin");
      break;
    case 0:
      return;
    default:
      printf("无效选择!\n");
      pause_program();
    }
  }
}

void user_menu(MYSQL *conn, const char *username) {
  int choice;

  while (1) {
    clear_screen();
    printf("========== 普通用户菜单 ==========\n");
    printf("1. 查询学生信息\n");
    printf("2. 查看所有学生成绩（总分排序）\n");
    printf("3. 查看成绩统计\n");
    printf("4. 修改密码\n");
    printf("0. 退出系统\n");
    printf("===============================\n");

    choice = read_int("请选择操作: ");

    switch (choice) {
    case 1:
      query_student_ui(conn);
      break;
    case 2:
      list_students_ui(conn);
      break;
    case 3:
      show_statistics_ui(conn);
      break;
    case 4:
      change_password_ui(conn, username);
      break;
    case 0:
      return;
    default:
      printf("无效选择!\n");
      pause_program();
    }
  }
}
