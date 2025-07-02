#include "func.h"
#include "interface.h"
#include "student.h"

int main(int argc, char *argv[]) {
  // 加载配置文件
  if (2 != argc) {
    printf("Usage: %s <input_file>\n", argv[0]);
    return 1;
  }

  // 从配置文件中，读取所有数据，用动态数组存储
  Vec datas;
  initVec(&datas);
  getInfo(argv[1], &datas);

  // 测试接口
#if DEBUG
  printVec(&datas);
  printf("---------------add\n");
  Student node;
  setNode(&node, "1001", "朴正熙", MALE, 77.9, 88.9, 69.3);
  addVec(&datas, &node);
  printVec(&datas);

  printf("----------------del\n");
  delVec(&datas, "19");
  printVec(&datas);

  printf("-----------------search\n");
  Student *result = searchVec(&datas, "35");
  if (result) {
    printf("Find!----------");
    printStu(result);
  } else {
    printf("Not Find\n");
  }

  printf("--------------------update\n");
  setNode(&node, "20", "黑豹", MALE, 66.6, 77.7, 88.8);
  updateVec(&datas, &node);
  printVec(&datas);

  printf("---------------------总分降序\n");
  descTable(&datas);

  printf("---------------------平均分\n");
  getAverage(&datas);

  printf("---------------------最高分\n");
  getTopScore(&datas);

#endif

  // 进入初始界面，不选择退出，就一直在这个界面
  main_interface(&datas);

  // 销毁动态数组
  freeVec(&datas);
}
