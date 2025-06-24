#include "../include/menu.h"
#include "../include/utils.h"
#include <libgen.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
  char *backend_ip = NULL;
  int backend_port;

  // 获取当前可执行文件路径
  char path[1024];
  ssize_t len = readlink("/proc/self/exe", path, sizeof(path) - 1);
  if (len != -1) {
    path[len] = '\0';
    char *dir = dirname(path);

    // 构建.env文件路径
    char env_path[2048];
    snprintf(env_path, sizeof(env_path), "%s/.env", dir);

    // 加载环境配置
    load_env_config(env_path, &backend_ip, &backend_port);
  } else {
    // 如果无法获取路径，使用当前目录
    fprintf(stderr, "Warning: Could not determine executable path, using "
                    "current directory\n");
    load_env_config(".env", &backend_ip, &backend_port);
  }

  printf("Connecting to backend at %s:%d\n", backend_ip, backend_port);

  // 连接后端服务器
  int sock = connect_to_server(backend_ip, backend_port);
  if (sock < 0) {
    free(backend_ip);
    return 1;
  }

  // 显示登录菜单
  User *user = login_menu(sock);

  if (user) {
    // 进入主菜单
    main_menu(sock, user);

    // 清理用户数据
    free_user(user);
  }

  // 关闭连接
  close(sock);
  free(backend_ip);

  printf("\nGoodbye!\n");
  return 0;
}
