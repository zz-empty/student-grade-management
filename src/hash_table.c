#include "hash_table.h"
#include <stdio.h>
#include <stdlib.h> 
#include <string.h>

unsigned int hash_function(const char* id) {
    unsigned int hash = 0;
    while (*id) {
        hash = (hash << 5) + *id++; // 简单的哈希函数
    }
    return hash % TABLE_SIZE; // 确保哈希值在表大小范围内
}

void init_hash_table(HashTable* table) {
    for (int i = 0; i < TABLE_SIZE; i++) {
        table->buckets[i] = NULL;
    }
}

// 向哈希表中插入一个学生节点
void insert_hash_table(HashTable* table, Student* stu) {
    // 计算学生节点的哈希值
    unsigned int index = hash_function(stu->id);
    // 为新节点分配内存
    HashNode* new_node = (HashNode*)malloc(sizeof(HashNode));
    // 如果内存分配失败，则输出错误信息并返回
    if (new_node == NULL) {
        printf("内存分配失败\n");
        return;
    }
    // 将学生节点赋值给新节点
    new_node->student = stu;
    // 将新节点插入到哈希表中的对应位置
    new_node->next = table->buckets[index];
    table->buckets[index] = new_node;

}


Student* search_hash_table(HashTable* table, const char* id) {
    unsigned int index = hash_function(id);
    HashNode* current = table->buckets[index];
    while (current != NULL) {
        if (strcmp(current->student->id, id) == 0) {
            return current->student;
        }
        current = current->next;
    }
    return NULL;
}

void delete_hash_table(HashTable* table, const char* id) {
    unsigned int index = hash_function(id);
    HashNode* current = table->buckets[index];
    HashNode* prev = NULL;
    while (current != NULL) {
        if (strcmp(current->student->id, id) == 0) {
            if (prev == NULL) {
                table->buckets[index] = current->next;
            } else {
                prev->next = current->next;
            }
            free(current->student);
            free(current);
            return;
        }
        prev = current;
        current = current->next;
    }
}

void free_hash_table(HashTable* table) {
    for (int i = 0; i < TABLE_SIZE; i++) {
        HashNode* current = table->buckets[i];
        while (current != NULL) {
            HashNode* temp = current;
            current = current->next;
            free(temp->student);
            free(temp);
        }
    }
}
