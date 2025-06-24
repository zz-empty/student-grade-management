#include "../include/db.h"
#include "../include/request_handler.h"
#include <netinet/in.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT 8888
#define BUFFER_SIZE 4096
#define MAX_CONNECTIONS 10

volatile sig_atomic_t keep_running = 1;

void handle_signal(int sig) { keep_running = 0; }

// 客户端处理线程
void *client_handler(void *arg) {
  int client_socket = *((int *)arg);
  free(arg);

  // 从环境变量或配置文件加载数据库配置
  MYSQL *conn = NULL;
#ifdef USE_ENV_CONFIG
  DBConfig config = load_db_config_from_env();
  conn = db_init(config);

  // 释放配置内存
  free(config.host);
  free(config.user);
  free(config.password);
  free(config.database);
#else
  conn = db_init(load_db_config("config.json"));
#endif

  if (!conn) {
    fprintf(stderr, "Failed to connect to database\n");
    close(client_socket);
    return NULL;
  }

  char buffer[BUFFER_SIZE];

  while (1) {
    memset(buffer, 0, BUFFER_SIZE);
    ssize_t bytes_read = read(client_socket, buffer, BUFFER_SIZE - 1);

    if (bytes_read <= 0) {
      break; // 客户端断开连接
    }

    // 解析请求类型
    RequestType type = parse_request_type(buffer);
    char *response = NULL;

    // 根据请求类型调用相应的处理函数
    switch (type) {
    case REQ_LOGIN:
      response = handle_login(conn, buffer);
      break;
    case REQ_ADD_STUDENT:
      response = handle_add_student(conn, buffer);
      break;
    case REQ_DELETE_STUDENT:
      response = handle_delete_student(conn, buffer);
      break;
    case REQ_UPDATE_STUDENT:
      response = handle_update_student(conn, buffer);
      break;
    case REQ_GET_STUDENT:
      response = handle_get_student(conn, buffer);
      break;
    case REQ_LIST_STUDENTS:
      response = handle_list_students(conn, buffer);
      break;
    case REQ_GET_STATISTICS:
      response = handle_get_statistics(conn, buffer);
      break;
    case REQ_CHANGE_PASSWORD:
      response = handle_change_password(conn, buffer);
      break;
    default:
      response =
          strdup("{\"status\":\"error\",\"message\":\"Unknown action\"}");
      break;
    }

    if (response) {
      write(client_socket, response, strlen(response));
      free(response);
    }
  }

  db_close(conn);
  close(client_socket);
  return NULL;
}

int main() {
  // 注册信号处理
  signal(SIGINT, handle_signal);
  signal(SIGTERM, handle_signal);

  int server_fd, new_socket;
  struct sockaddr_in address;
  int opt = 1;
  int addrlen = sizeof(address);

  // 创建Socket
  if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
    perror("socket failed");
    exit(EXIT_FAILURE);
  }

  // 设置Socket选项
  if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt,
                 sizeof(opt))) {
    perror("setsockopt");
    exit(EXIT_FAILURE);
  }

  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons(PORT);

  // 绑定Socket
  if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
    perror("bind failed");
    exit(EXIT_FAILURE);
  }

  // 监听
  if (listen(server_fd, MAX_CONNECTIONS) < 0) {
    perror("listen");
    exit(EXIT_FAILURE);
  }

  printf("Backend server listening on port %d...\n", PORT);

  while (keep_running) {
    // 接受新连接
    if ((new_socket = accept(server_fd, (struct sockaddr *)&address,
                             (socklen_t *)&addrlen)) < 0) {
      if (keep_running) {
        perror("accept");
      }
      continue;
    }

    // 为每个客户端创建新线程
    pthread_t thread_id;
    int *client_socket = malloc(sizeof(int));
    *client_socket = new_socket;

    if (pthread_create(&thread_id, NULL, client_handler,
                       (void *)client_socket) < 0) {
      perror("could not create thread");
      close(new_socket);
      free(client_socket);
    } else {
      // 分离线程，使其结束后自动释放资源
      pthread_detach(thread_id);
    }
  }

  printf("Shutting down server...\n");
  close(server_fd);
  return 0;
}
