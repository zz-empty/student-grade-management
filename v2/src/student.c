#include "../include/student.h"
#include "../include/db.h"
#include <mysql/mysql.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int add_student(MYSQL *conn, Student *student) {
  char query[512];
  snprintf(
      query, sizeof(query),
      "INSERT INTO scores (student_id, name, gender, score1, score2, score3) "
      "VALUES ('%s', '%s', '%s', %.2f, %.2f, %.2f)",
      student->student_id, student->name, student->gender, student->score1,
      student->score2, student->score3);

  return db_execute(conn, query);
}

int delete_student(MYSQL *conn, const char *student_id) {
  char query[128];
  snprintf(query, sizeof(query), "DELETE FROM scores WHERE student_id = '%s'",
           student_id);
  return db_execute(conn, query);
}

int update_student(MYSQL *conn, Student *student) {
  char query[512];
  snprintf(query, sizeof(query),
           "UPDATE scores SET name = '%s', gender = '%s', score1 = %.2f, "
           "score2 = %.2f, score3 = %.2f WHERE student_id = '%s'",
           student->name, student->gender, student->score1, student->score2,
           student->score3, student->student_id);

  return db_execute(conn, query);
}

Student *get_student(MYSQL *conn, const char *student_id) {
  char query[128];
  snprintf(query, sizeof(query), "SELECT * FROM scores WHERE student_id = '%s'",
           student_id);

  MYSQL_RES *result = db_query(conn, query);
  if (result == NULL) {
    return NULL;
  }

  MYSQL_ROW row = mysql_fetch_row(result);
  if (row == NULL) {
    mysql_free_result(result);
    return NULL;
  }

  Student *student = malloc(sizeof(Student));
  student->student_id = strdup(row[0]);
  student->name = strdup(row[1]);
  student->gender = strdup(row[2]);
  student->score1 = atof(row[3]);
  student->score2 = atof(row[4]);
  student->score3 = atof(row[5]);

  mysql_free_result(result);
  return student;
}

MYSQL_RES *get_all_students_sorted(MYSQL *conn) {
  const char *query = "SELECT *, (score1 + score2 + score3) AS total "
                      "FROM scores ORDER BY total DESC";
  return db_query(conn, query);
}

void get_statistics(MYSQL *conn, float *avg1, float *max1, float *avg2,
                    float *max2, float *avg3, float *max3) {
  const char *query = "SELECT "
                      "AVG(score1), MAX(score1), "
                      "AVG(score2), MAX(score2), "
                      "AVG(score3), MAX(score3) "
                      "FROM scores";

  MYSQL_RES *result = db_query(conn, query);
  if (result == NULL) {
    return;
  }

  MYSQL_ROW row = mysql_fetch_row(result);
  if (row) {
    *avg1 = atof(row[0]);
    *max1 = atof(row[1]);
    *avg2 = atof(row[2]);
    *max2 = atof(row[3]);
    *avg3 = atof(row[4]);
    *max3 = atof(row[5]);
  }

  mysql_free_result(result);
}

void free_student(Student *student) {
  free(student->student_id);
  free(student->name);
  free(student->gender);
  free(student);
}
