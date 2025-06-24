#ifndef MENU_H
#define MENU_H

// 用户结构体
typedef struct {
  char *username;
  char *permission;
} User;

// 登录界面
User *login_menu(int sock);

// 主菜单
void main_menu(int sock, User *user);

// 管理员菜单
void admin_menu(int sock);

// 普通用户菜单
void user_menu(int sock, const char *username);

// 释放用户结构体
void free_user(User *user);

#endif
