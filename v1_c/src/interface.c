#include "interface.h"
#include "func.h"
#include "student.h"
#include <_inttypes.h>
#include <stdlib.h>

#define LINE_MAX 1024

void print_menu() {
  puts("======================================================================="
       "========");
  puts("=             Student    Information    Management    System           "
       "       =");
  puts("======================================================================="
       "========");
  puts("");

  // puts("              0. quit");
  puts("");
  puts("              1. search by id");
  puts("              2. add ");
  puts("              3. update");
  puts("              4. delete ");
  puts("              5. show all info ");
  puts("              6. display totalScores_desc_table");
  puts("              7. average");
  puts("              8. top");
  puts("======================================================================="
       "========");
  puts("退出主界面按0，退出功能菜单按q  ");
  puts("======================================================================="
       "========");
  puts("");
}

// 主界面
void main_interface(Vec *vec) {
  while (1) {
    // 打印功能选择界面
    system("clear");
    print_menu();
    int opt;
    printf("请选择：");
    scanf("%d", &opt);

    if (0 == opt) {
      system("clear");
      break;
    }

    switch (opt) {
    case 1:
      function_1(vec);
      break;
    case 2:
      function_2(vec);
      break;
    case 3:
      function_3(vec);
      break;
    case 4:
      function_4(vec);
      break;
    case 5:
      function_5(vec);
      break;
    case 6:
      function_6(vec);
      break;
    case 7:
      function_7(vec);
      break;
    case 8:
      function_8(vec);
      break;
    }
  }
}

void function_1(Vec *vec) {
  system("clear");
  printf("请输入查找的id：");
  char id[LINE_MAX] = "";
  scanf("%s", id);
  Student *result = searchVec(vec, id);
  if (result) {
    printf("Find!----------");
    printStu(result);
  } else {
    printf("Not Find\n");
  }
  printf("退出按q：");
  char c = 0;
  while (c != 'q') {
    scanf("%c", &c);
  }
  return;
}

void function_2(Vec *vec) {
  system("clear");
  printf("输入新增的学生信息：\n");
  Student node;
  int gender;
  printf("学号：");
  scanf("%s", node.id);
  printf("姓名：");
  scanf("%s", node.name);
  printf("性别（女0，男1）：");
  scanf("%d", &gender);
  if (gender) {
    node.gender = MALE;
  } else {
    node.gender = FEMALE;
  }
  printf("三科成绩：");
  scanf("%f%f%f", &node.scores[0], &node.scores[1], &node.scores[2]);
  node.totalScore = node.scores[0] + node.scores[1] + node.scores[2];
  if (addVec(vec, &node)) {
    printf("添加成功\n");
  } else {
    printf("添加失败，学号重复\n");
  }
  // 退出
  char c = 0;
  while ('q' != c) {
    scanf("%c", &c);
  }
}

void function_3(Vec *vec) {
  printf("更新的学生id：");
  char id[ID_LENGTH];
  scanf("%s", id);
  Student *result = searchVec(vec, id);
  if (result) {
    printf("Find! 输入更新的内容（三科成绩）----------");
    scanf("%f%f%f", &result->scores[0], &result->scores[1], &result->scores[2]);
  } else {
    printf("Not Find\n");
  }
  // 退出
  char c = 0;
  while ('q' != c) {
    scanf("%c", &c);
  }
}
void function_4(Vec *vec) {
  system("clear");
  printf("输入要删除的学号：");
  char id[ID_LENGTH];
  scanf("%s", id);
  if (delVec(vec, id)) {
    printf("删除成功\n");
  } else {
    printf("删除失败, 未找到该学号\n");
  }
  // 退出
  char c = 0;
  while ('q' != c) {
    scanf("%c", &c);
  }
}
void function_5(Vec *vec) {
  system("clear");
  printVec(vec);
  // 退出
  char c = 0;
  while ('q' != c) {
    scanf("%c", &c);
  }
}
void function_6(Vec *vec) {
  system("clear");
  descTable(vec);
  // 退出
  char c = 0;
  while ('q' != c) {
    scanf("%c", &c);
  }
}
void function_7(Vec *vec) {
  system("clear");
  getAverage(vec);
  // 退出
  char c = 0;
  while ('q' != c) {
    scanf("%c", &c);
  }
}
void function_8(Vec *vec) {
  system("clear");
  getTopScore(vec);
  // 退出
  char c = 0;
  while ('q' != c) {
    scanf("%c", &c);
  }
}
