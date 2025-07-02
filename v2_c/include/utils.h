#ifndef UTILS_H
#define UTILS_H

#include <stdio.h>
#include <stdlib.h>

// 清屏
void clear_screen();

// 暂停程序
void pause_program();

// 安全读取字符串
char *read_string(const char *prompt, int max_length);

// 安全读取整数
int read_int(const char *prompt);

// 安全读取浮点数
float read_float(const char *prompt);

// 密码输入
char *get_password(const char *prompt);

#endif
