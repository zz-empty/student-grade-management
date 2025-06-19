#ifndef __HASH_TABLE_H__
#define __HASH_TABLE_H__

#include "student.h"

#define TABLE_SIZE 100

typedef struct HashNode {
    Student* student;
    struct HashNode* next;
} HashNode;

typedef struct HashTable {
    HashNode* buckets[TABLE_SIZE];
} HashTable;

unsigned int hash_function(const char* id);
void init_hash_table(HashTable* table);
void insert_hash_table(HashTable* table, Student* stu);
Student* search_hash_table(HashTable* table, const char* id);
void delete_hash_table(HashTable* table, const char* id);
void free_hash_table(HashTable* table);

#endif // __HASH_TABLE_H__