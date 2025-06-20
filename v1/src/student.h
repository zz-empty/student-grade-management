#ifndef __STUDENT_H__
#define __STUDENT_H__

#define ID_LENGTH 20
#define NAME_LENGTH 50
#define VEC_CAPACITY 10

typedef enum { MALE, FEMALE } Gender;

// 学生信息结构体
typedef struct Student {
  char id[ID_LENGTH];
  char name[NAME_LENGTH];
  Gender gender;
  float scores[3]; // Assuming 3 subjects
  float totalScore;
} Student;

// 动态数组
typedef struct Vec {
  Student *arr;
  int size;
  int capacity;
} Vec;

// 初始化动态数组
void initVec(Vec *vec);
// 从文件中读取数据，放入数组
void getInfo(const char *filename, Vec *vec);
// 添加学生到链表
int addVec(Vec *vec, Student *stu);
// 删除学生信息
int delVec(Vec *vec, const char *id);
// 查询学生信息, 用原数组
Student *searchVec(Vec *vec, const char *id);
// 更新学生信息, 用原数组
void updateVec(Vec *vec, Student *stu);
// 释放动态数组
void freeVec(Vec *vec);
// 打印所有学生信息
void printVec(Vec *vec);
// 打印一个学生信息
void printStu(Student *stu);
// 设置一个node结点
void setNode(Student *stu, const char *id, const char *name, Gender gender,
             float f1, float f2, float f3);

// 打印总分降序
void descTable(Vec *vec);
// 打印各科平均分
void getAverage(Vec *vec);
// 各科最高分
void getTopScore(Vec *vec);

#endif // __STUDENT_H__
