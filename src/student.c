#include "student.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


// 创建一个学生信息结构体
Student *createStudent(const char *id, const char *name, Gender gender, float *scores) {
    Student *stu = (Student *)malloc(sizeof(Student));
    if (stu == NULL) {
        printf("内存分配失败\n");
        return NULL;
    }
    strncpy(stu->id, id, ID_LENGTH);
    strncpy(stu->name, name, NAME_LENGTH);
    stu->gender = gender;
    memcpy(stu->score, scores, 3 * sizeof(float));
    stu->totalScore = scores[0] + scores[1] + scores[2];
    stu->prev = NULL; // 初始化前驱指针
    stu->next = NULL; // 初始化后继指针
    return stu;
}

// 初始化链表
void initList(StudentList *list) {
    list->head = NULL;
    list->tail = NULL;
    list->size = 0;
}

// 添加学生到链表
void addStudent(StudentList *list, Student *stu) {
    if (list->head == NULL) {
        list->head = stu;
        list->tail = stu;
    } else {
        list->tail->next = stu;
        stu->prev = list->tail;
        list->tail = stu;
    }
    list->size++;
}

// 删除学生信息
// 删除学生函数
void deleteStudent(StudentList *list, const char *id) {
    Student *current = list->head;
    while (current != NULL) {
        if (strcmp(current->id, id) == 0) {
            if (current->prev != NULL) {
                current->prev->next = current->next;
            } else {
                list->head = current->next;
            }
            if (current->next != NULL) {
                current->next->prev = current->prev;
            } else {
                list->tail = current->prev;
            }
            free(current);
            list->size--;
            return;
        }
        current = current->next;
    }
}
// 释放链表
void freeList(StudentList *list) {
    Student *current = list->head;
    while (current != NULL) {
        Student *next = current->next;
        free(current);
        current = next;
    }
    list->head = NULL;
    list->tail = NULL;
    list->size = 0;
}