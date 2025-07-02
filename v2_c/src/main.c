#include "../include/auth.h"
#include "../include/db.h"
#include "../include/menu.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
  if (argc != 2) {
    fprintf(stderr, "用法: %s <配置文件路径>\n", argv[0]);
    return 1;
  }

  // 加载数据库配置
  DBConfig config = load_db_config(argv[1]);

  // 初始化数据库连接
  MYSQL *conn = db_init(config);
  if (conn == NULL) {
    fprintf(stderr, "数据库连接失败\n");
    return 1;
  }

  // 登录
  User *user = login_ui(conn);
  if (user == NULL) {
    db_close(conn);
    return 0;
  }

  // 进入主菜单
  main_menu(conn, user);

  // 清理资源
  free_user(user);
  db_close(conn);

  return 0;
}
