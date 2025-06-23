#include "../include/utils.h"
#include <readline/history.h>
#include <readline/readline.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

void clear_screen() { system("clear"); }

void pause_program() {
  printf("\n按回车键继续...");
  while (getchar() != '\n')
    ;        // 清空输入缓冲区
  getchar(); // 等待用户按回车
}

char *read_string(const char *prompt, int max_length) {
  char *input = NULL;
  size_t len = 0;

  while (1) {
    printf("%s", prompt);
    fflush(stdout);

    if (getline(&input, &len, stdin) == -1) {
      free(input);
      return NULL;
    }

    // 移除换行符
    if (input[strlen(input) - 1] == '\n') {
      input[strlen(input) - 1] = '\0';
    }

    if (strlen(input) > 0 && strlen(input) <= max_length) {
      return input;
    }

    printf("输入无效! 长度必须在1-%d个字符之间\n", max_length);
    free(input);
    input = NULL;
  }
}

int read_int(const char *prompt) {
  char *input = read_string(prompt, 20);
  if (input == NULL)
    return 0;

  char *endptr;
  long value = strtol(input, &endptr, 10);

  if (*endptr != '\0') {
    printf("输入无效! 请输入整数\n");
    free(input);
    return read_int(prompt);
  }

  free(input);
  return (int)value;
}

float read_float(const char *prompt) {
  char *input = read_string(prompt, 20);
  if (input == NULL)
    return 0.0f;

  char *endptr;
  float value = strtof(input, &endptr);

  if (*endptr != '\0') {
    printf("输入无效! 请输入数字\n");
    free(input);
    return read_float(prompt);
  }

  free(input);
  return value;
}

char *get_password(const char *prompt) {
  struct termios old_term, new_term;
  char *password = malloc(100);

  // 禁用终端回显
  tcgetattr(STDIN_FILENO, &old_term);
  new_term = old_term;
  new_term.c_lflag &= ~ECHO;
  tcsetattr(STDIN_FILENO, TCSANOW, &new_term);

  printf("%s", prompt);
  fflush(stdout);
  fgets(password, 100, stdin);

  // 恢复终端设置
  tcsetattr(STDIN_FILENO, TCSANOW, &old_term);
  printf("\n");

  // 移除换行符
  if (password[strlen(password) - 1] == '\n') {
    password[strlen(password) - 1] = '\0';
  }

  return password;
}
