#include "hash_table.h"
#include "json_io.h"
#include "student.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
  // 引入json文件
  if (argc != 2) {
    printf("Usage: %s <input_file>\n", argv[0]);
    return 1;
  }

  StudentList list;
  HashTable table;
  initList(&list);
  init_hash_table(&table);

  // 从JSON文件加载学生信息
  if (load_from_json(argv[1], &list, &table) != 1) {
    fprintf(stderr, "Failed to load student data from JSON file\n");
    return 1;
  }

  // 测试查找
  Student *student = search_hash_table(&table, "2023001");
  if (student) {
    printf("Found student: %s\n", student->name);
    // 测试更新
    strcpy(student->name, "李建成");
    student->score[0] = 95.0;
  } else {
    printf("Student not found\n");
  }

  // 测试添加
  Student *new_stu = (Student *)malloc(sizeof(Student));
  strcpy(new_stu->id, "2023002");
  strcpy(new_stu->name, "赵云");
  new_stu->score[0] = 90.0;
  new_stu->score[1] = 85.0;
  new_stu->score[2] = 80.0;
  new_stu->totalScore =
      new_stu->score[0] + new_stu->score[1] + new_stu->score[2];

  // 添加到链表和哈希表
  addStudent(&list, new_stu);
  insert_hash_table(&table, new_stu);

  // 测试删除
  deleteStudent(&list, "2023002");
  delete_hash_table(&table, "2023002");
}
