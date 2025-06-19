#ifndef __JSON_IO_H
#define __JSON_IO_H

#include "student.h"
#include "hash_table.h"

int load_from_json(const char *filename, StudentList *list, HashTable *table);
int save_to_json(const char *filename, StudentList *list);
char *generate_score_table(StudentList *list);

#endif // __JSON_IO_H