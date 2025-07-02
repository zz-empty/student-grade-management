#ifndef STUDENT_H
#define STUDENT_H

#include <mysql/mysql.h>

// 学生成绩结构体
typedef struct {
  char *student_id;
  char *name;
  char *gender;
  float score1;
  float score2;
  float score3;
} Student;

// 添加学生
int add_student(MYSQL *conn, Student *student);

// 删除学生
int delete_student(MYSQL *conn, const char *student_id);

// 更新学生信息
int update_student(MYSQL *conn, Student *student);

// 查询学生
Student *get_student(MYSQL *conn, const char *student_id);

// 获取所有学生（按总分降序）
MYSQL_RES *get_all_students_sorted(MYSQL *conn);

// 获取统计信息
void get_statistics(MYSQL *conn, float *avg1, float *max1, float *avg2,
                    float *max2, float *avg3, float *max3);

// 释放学生结构体
void free_student(Student *student);

#endif
