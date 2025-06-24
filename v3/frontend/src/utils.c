#include "../include/utils.h"
#include <errno.h>
#include <jansson.h>
#include <libgen.h>
#include <readline/readline.h>

// 从环境文件加载配置
void load_env_config(const char *env_file, char **ip, int *port) {
  FILE *fp = fopen(env_file, "r");
  if (!fp) {
    fprintf(stderr, "Error opening .env file\n");
    exit(1);
  }

  *ip = malloc(64); // 分配足够空间存储IP
  *port = 8888;     // 默认端口

  char line[256];
  while (fgets(line, sizeof(line), fp)) {
    if (strncmp(line, "BACKEND_IP=", 11) == 0) {
      sscanf(line + 11, "%63s", *ip);
    } else if (strncmp(line, "BACKEND_PORT=", 13) == 0) {
      *port = atoi(line + 13);
    }
  }

  fclose(fp);

  // 打印配置信息（调试用）
  printf("Loaded config: Backend server at %s:%d\n", *ip, *port);
}

int connect_to_server(const char *ip, int port) {
  int sock = 0;
  struct sockaddr_in serv_addr;

  int max_retries = 5;
  int retry_delay = 3; // 秒

  for (int attempt = 1; attempt <= max_retries; attempt++) {
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
      perror("Socket creation error");
      return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    // 转换IP地址
    if (inet_pton(AF_INET, ip, &serv_addr.sin_addr) <= 0) {
      perror("Invalid address / Address not supported");
      close(sock);
      return -1;
    }

    // 设置连接超时
    struct timeval timeout;
    timeout.tv_sec = 5;
    timeout.tv_usec = 0;

    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));

    // 连接服务器
    printf("Connecting to backend server (attempt %d/%d)...\n", attempt,
           max_retries);
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr))) {
      perror("Connection failed");
      close(sock);

      if (attempt < max_retries) {
        printf("Retrying in %d seconds...\n", retry_delay);
        sleep(retry_delay);
      }
    } else {
      printf("Successfully connected to backend server\n");
      return sock;
    }
  }

  fprintf(stderr, "Failed to connect after %d attempts\n", max_retries);
  return -1;
}

char *send_request(int sock, const char *request) {
  // 发送请求
  if (send(sock, request, strlen(request), 0) < 0) {
    perror("Send failed");
    return NULL;
  }

  // 接收响应
  static char buffer[4096];
  ssize_t bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0);

  if (bytes_received <= 0) {
    perror("Recv failed");
    return NULL;
  }

  buffer[bytes_received] = '\0';
  return buffer;
}

char *read_string(const char *prompt) {
  char *input = readline(prompt);

  if (!input) {
    return NULL;
  }

  // 去除换行符
  if (input[strlen(input) - 1] == '\n') {
    input[strlen(input) - 1] = '\0';
  }

  return input;
}

char *read_password(const char *prompt) {
  struct termios old_term, new_term;
  char *password = malloc(128);

  // 禁用终端回显
  tcgetattr(STDIN_FILENO, &old_term);
  new_term = old_term;
  new_term.c_lflag &= ~ECHO;
  tcsetattr(STDIN_FILENO, TCSANOW, &new_term);

  printf("%s", prompt);
  fflush(stdout);
  fgets(password, 128, stdin);

  // 恢复终端设置
  tcsetattr(STDIN_FILENO, TCSANOW, &old_term);
  printf("\n");

  // 去除换行符
  if (password[strlen(password) - 1] == '\n') {
    password[strlen(password) - 1] = '\0';
  }

  return password;
}

void clear_screen() { system("clear"); }

void pause_program() {
  printf("\nPress Enter to continue...");
  while (getchar() != '\n')
    ;        // 清空输入缓冲区
  getchar(); // 等待用户按回车
}
