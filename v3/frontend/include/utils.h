#ifndef UTILS_H
#define UTILS_H

#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <termios.h>
#include <unistd.h>

// 从环境文件加载配置
void load_env_config(const char *env_file, char **ip, int *port);

// 连接服务器
int connect_to_server(const char *ip, int port);

// 发送请求并接收响应
char *send_request(int sock, const char *request);

// 读取字符串输入
char *read_string(const char *prompt);

// 读取密码（不回显）
char *read_password(const char *prompt);

// 清屏
void clear_screen();

// 暂停程序
void pause_program();

#endif
