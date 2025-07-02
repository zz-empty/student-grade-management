#include "student.h"
#include "func.h"
#include <sys/syslimits.h>

// 初始化动态数组
void initVec(Vec *vec) {
  vec->size = 0;
  vec->capacity = VEC_CAPACITY;
  vec->arr = (Student *)malloc(sizeof(Student) * vec->capacity);
}

// 从文件中读取数据，放入数组
void getInfo(const char *filename, Vec *vec) {
  FILE *fp = (FILE *)fopen(filename, "r");

  char line[LINE_MAX];       // 读取文件的每一行, 就是一个学生信息
  fgets(line, LINE_MAX, fp); // 忽略标题行
  while (fgets(line, LINE_MAX, fp)) {
    // 格式化一个node
    Student node;
    char gender[LINE_MAX];
    sscanf(line, "%s %s %s %f %f %f", node.id, node.name, gender,
           &node.scores[0], &node.scores[1], &node.scores[2]);
    if (strcmp(gender, "女") == 0) {
      node.gender = FEMALE;
    } else {
      node.gender = MALE;
    }
    node.totalScore = node.scores[0] + node.scores[1] + node.scores[2];
    // 将node加入数组
    addVec(vec, &node);
  }

  fclose(fp);
}

// 添加学生到链表
int addVec(Vec *vec, Student *stu) {
  // 判断学号是否重复
  for (int i = 0; i < vec->size; ++i) {
    if (strcmp(stu->id, vec->arr[i].id) == 0) {
      return 0;
    }
  }

  // 数组已满，重新申请一片空间
  if (vec->size == vec->capacity) {
    Student *tmp = vec->arr;
    vec->capacity = vec->capacity * 2;
    vec->arr = (Student *)malloc(sizeof(Student) * vec->capacity);
    memcpy(vec->arr, tmp, vec->size * sizeof(Student));
    free(tmp);
    tmp = NULL;
  }

  // 插入到数组的末尾
  vec->arr[vec->size] = *stu;
  vec->size++;
  return 1;
}

// 查询学生信息
Student *searchVec(Vec *vec, const char *id) {
  if (vec->size) {
    for (int i = 0; i < vec->size; ++i) {
      if (0 == strcmp(vec->arr[i].id, id)) {
        return &vec->arr[i];
      }
    }
  }
  return NULL;
}

// 更新学生信息
void updateVec(Vec *vec, Student *stu) {
  Student *result = searchVec(vec, stu->id);
  if (result) {
    *result = *stu;
    return;
  }
  printf("没有找到id，无法更新\n");
  return;
}

// 删除学生信息
int delVec(Vec *vec, const char *id) {
  if (vec->size) {
    for (int i = 0; i < vec->size; ++i) {
      if (strcmp(vec->arr[i].id, id) == 0) {
        // 找到了，后续所有节点前移，size--
        for (int j = i + 1; j < vec->size; ++j) {
          vec->arr[j - 1] = vec->arr[j];
        }
        vec->size--;
        return 1;
      }
    }
  }

  return 0;
}

// 释放动态数组
void freeVec(Vec *vec) {
  if (vec->arr) {
    free(vec->arr);
    vec->arr = NULL;
  }
  vec->size = 0;
}

// 打印所有学生信息
void printVec(Vec *vec) {
  printf("All_stu_info------------------------------\n");
  for (int i = 0; i < vec->size; ++i) {
    printf("%s\t%s\t%s\t%5.2f\t%5.2f\t%5.2f\t%5.2f\n", vec->arr[i].id,
           vec->arr[i].name, vec->arr[i].gender == FEMALE ? "女" : "男",
           vec->arr[i].scores[0], vec->arr[i].scores[1], vec->arr[i].scores[2],
           vec->arr[i].totalScore);
  }
}

// 设置一个node结点
void setNode(Student *stu, const char *id, const char *name, Gender gender,
             float f1, float f2, float f3) {
  strcpy(stu->id, id);
  strcpy(stu->name, name);
  stu->gender = gender;
  stu->scores[0] = f1;
  stu->scores[1] = f2;
  stu->scores[2] = f3;
  stu->totalScore = stu->scores[0] + stu->scores[1] + stu->scores[2];
}

// 打印一个学生信息
void printStu(Student *stu) {
  if (stu) {
    printf("%s\t%s\t%s\t%5.2f\t%5.2f\t%5.2f\t%5.2f\n", stu->id, stu->name,
           stu->gender == FEMALE ? "女" : "男", stu->scores[0], stu->scores[1],
           stu->scores[2], stu->totalScore);
  }
}

int compare_total(const void *p1, const void *p2) {
  Student *s1 = *(Student **)p1;
  Student *s2 = *(Student **)p2;
  return s2->totalScore - s1->totalScore;
}

// 打印总分降序
void descTable(Vec *vec) {
  Student **result = (Student **)malloc(sizeof(Student *) * vec->size);
  for (int i = 0; i < vec->size; ++i) {
    result[i] = vec->arr + i;
  }
  qsort(result, vec->size, sizeof(Student *), compare_total);

  for (int i = 0; i < vec->size; ++i) {
    printStu(result[i]);
  }

  free(result);
}
// 打印各科平均分
void getAverage(Vec *vec) {
  if (vec->size) {
    float as1 = 0;
    float as2 = 0;
    float as3 = 0;
    for (int i = 0; i < vec->size; ++i) {
      as1 += vec->arr[i].scores[0];
      as2 += vec->arr[i].scores[1];
      as3 += vec->arr[i].scores[2];
    }

    printf("各科平均分：score1-%5.2f, score2-%5.2f, score3-%5.2f\n",
           as1 / vec->size, as2 / vec->size, as3 / vec->size);
  }
}
// 各科最高分
void getTopScore(Vec *vec) {
  if (vec->size) {
    float max1 = 0, max2 = 0, max3 = 0;
    for (int i = 0; i < vec->size; ++i) {
      if (max1 < vec->arr[i].scores[0]) {
        max1 = vec->arr[i].scores[0];
      }
      if (max2 < vec->arr[i].scores[1]) {
        max2 = vec->arr[i].scores[1];
      }
      if (max3 < vec->arr[i].scores[2]) {
        max3 = vec->arr[i].scores[2];
      }
    }

    printf("各科最高分：max1（%5.2f），max2（%5.2f），max3（%5.2f）\n", max1,
           max2, max3);
  }
}
