#ifndef __STUDENT_H__
#define __STUDENT_H__

#define ID_LENGTH 20
#define NAME_LENGTH 50

typedef enum {
    MALE,
    FEMALE
} Gender;

// 学生信息结构体
typedef struct Student {
    char id[ID_LENGTH];
    char name[NAME_LENGTH];
    Gender gender;
    float score[3]; // Assuming 3 subjects
    float totalScore;
    struct Student *prev; // 指向上一个学生节点
    struct Student *next; // 指向下一个学生节点
} Student;


// 双向链表管理
typedef struct StudentList {
    Student *head;
    Student *tail;
    int size; // 当前链表中的学生数量
} StudentList;


// 创建一个学生信息结构体
Student *createStudent(const char *id, const char *name, Gender gender, float *scores);
// 初始化链表
void initList(StudentList *list);
// 添加学生到链表
void addStudent(StudentList *list, Student *stu);
// 删除学生信息
void deleteStudent(StudentList *list, const char *id);
// 释放链表
void freeList(StudentList *list);

#endif // __STUDENT_H__