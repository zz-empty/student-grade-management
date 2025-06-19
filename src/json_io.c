#include "json_io.h"
#include <stdio.h>  
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <cjson/cJSON.h>



int compare_students(const void *a, const void *b) {
    const Student *student_a = *(const Student **)a;
    const Student *student_b = *(const Student **)b;
    return student_a->totalScore - student_b->totalScore;
}

int load_from_json(const char *filename, StudentList *list, HashTable *table) {
    // 打开文件流
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Failed to open file");
        return -1;
    }

    // 获取所有字节
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);
    char *data = (char *)malloc(file_size + 1);
    fread(data, 1, file_size, file);
    fclose(file);
    data[file_size] = '\0'; // 确保字符串以 null 结

    // 解析 JSON 数据
    cJSON *root = cJSON_Parse(data);
    free(data);
    if (!root) {
        fprintf(stderr, "Failed to parse JSON: %s\n", cJSON_GetErrorPtr());
        return -1;
    }

    // 获取学生数组
    cJSON *students = cJSON_GetObjectItem(root, "students");
    if (!students || !cJSON_IsArray(students)) {
        fprintf(stderr, "Invalid JSON format: students is not an array\n");
        cJSON_Delete(root);
        return -1;
    }

    // 遍历学生数组
    cJSON *stu;
    cJSON_ArrayForEach(stu, students) {
        // 检查学生对象是否有效
        if (!cJSON_IsObject(stu)) {
            fprintf(stderr, "Invalid JSON format: student is not an object\n");
            continue;
        }

        // 创建学生对象
        Student *student = (Student *)malloc(sizeof(Student));

        // 解析字段
        cJSON *item = cJSON_GetObjectItem(stu, "id");
        if (item) strncpy(student->id, item->valuestring, ID_LENGTH - 1);

        item = cJSON_GetObjectItem(stu, "name");
        if (item) strncpy(student->name, item->valuestring, NAME_LENGTH - 1);

        item = cJSON_GetObjectItem(stu, "gender");
        if (item) student->gender = strcmp(item->valuestring, "FEMALE") == 0 ? FEMALE : MALE;

        item = cJSON_GetObjectItem(stu, "scores");
        if (item && cJSON_IsArray(item)) {
            for (int i = 0; i < 3; i++) {
                cJSON *score_item = cJSON_GetArrayItem(item, i);
                if (score_item && cJSON_IsNumber(score_item)) {
                    student->score[i] = (float)score_item->valuedouble;
                } else {
                    student->score[i] = 0.0f; // 默认值
                }
            }
        }

        // 计算总分
        student->totalScore = 0.0f;
        for (int i = 0; i < 3; i++) {
            student->totalScore += student->score[i];   
        }

        // 将学生添加到链表和哈希表中
        insert_hash_table(table, student);
        addStudent(list, student);
    }

    // 删除 JSON 对象
    cJSON_Delete(root);
    return 1;
}

int save_to_json(const char *filename, StudentList *list) {
    // 创建 JSON 对象
    cJSON *root = cJSON_CreateObject();
    cJSON *students = cJSON_CreateArray();

    // 按学号排序
    Student **arr = (Student **)malloc(list->size * sizeof(Student *));
    Student *cur = list->head;
    for (int i = 0; i < list->size; i++) {
        arr[i] = cur;
        cur = cur->next;
    }
    qsort(arr, list->size, sizeof(Student *), compare_students);

    // 构建 JSON 数据
    for (int i = 0; i < list->size; i++) {
        cJSON *stu = cJSON_CreateObject();
        cJSON_AddStringToObject(stu, "id", arr[i]->id);
        cJSON_AddStringToObject(stu, "name", arr[i]->name);
        cJSON_AddStringToObject(stu, "gender", arr[i]->gender == FEMALE ? "FAMALE" : "MALE");
        
        cJSON *scores = cJSON_CreateArray();
        for (int j = 0; j < 3; j++) {
            cJSON_AddItemToArray(scores, cJSON_CreateNumber(arr[i]->score[j]));
        }
        cJSON_AddItemToObject(stu, "scores", scores);
        cJSON_AddItemToArray(students, stu);
    }
    free(arr);

    // 添加到根对象
    cJSON_AddItemToObject(root, "students", students);
    char *json_string = cJSON_Print(root);
    cJSON_Delete(root);

    // 写入文件
    FILE *fp = fopen(filename, "w");
    if (!fp) {
        perror("Failed to open file");
        return -1;
    }
    fputs(json_string, fp);
    fclose(fp);
    free(json_string);
    return 1;
}

int compare_students_by_total_score(const void *a, const void *b) {
    const Student *student_a = *(const Student **)a;
    const Student *student_b = *(const Student **)b;
    return student_b->totalScore - student_a->totalScore;
}

char *generate_score_table(StudentList *list) {
    if (list->size == 0) {
        return NULL; // 如果链表为空，返回 NULL
    }

    // 创建指针数组，用于排序
    Student **arr = (Student **)malloc(list->size * sizeof(Student *));
    Student *cur = list->head;
    for (int i = 0; i < list->size; i++) {
        arr[i] = cur;
        cur = cur->next;
    }

    // 按总分排序
    qsort(arr, list->size, sizeof(Student *), compare_students_by_total_score);

    // 计算所需内存
    size_t buffer_size = 0;
    for (int i = 0; i < list->size; i++) {
        buffer_size += snprintf(NULL, 0, "%s\t%s\t%s\t%f\t%f\t%f\t%.2f\n",
                                arr[i]->id, arr[i]->name, 
                                arr[i]->gender == FEMALE ? "女" : "男",
                                arr[i]->score[0], arr[i]->score[1], arr[i]->score[2],  
                                arr[i]->totalScore);
    }

    // 分配内存并生成表格
    char *result = (char *)malloc(buffer_size + 1);
    char *pos = result;
    pos += snprintf(pos, buffer_size + 1, "学号\t姓名\t性别\t成绩1\t成绩2\t成绩3\t总分\n");
    for (int i = 0; i < list->size; i++) {
        pos += snprintf(pos, buffer_size + 1 - (pos - result), "%s\t%s\t%s\t%f\t%f\t%f\t%.2f\n",
                        arr[i]->id, arr[i]->name,
                        arr[i]->gender == FEMALE ? "女" : "男",
                        arr[i]->score[0], arr[i]->score[1], arr[i]->score[2],
                        arr[i]->totalScore);
    }

    free(arr);
    return result; // 返回生成的表格字符串
}