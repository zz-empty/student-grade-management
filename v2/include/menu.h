#ifndef MENU_H
#define MENU_H

#include "auth.h"

// 显示登录界面
User *login_ui(MYSQL *conn);

// 显示主菜单
void main_menu(MYSQL *conn, User *user);

// 管理员菜单
void admin_menu(MYSQL *conn);

// 普通用户菜单
void user_menu(MYSQL *conn, const char *username);

#endif
