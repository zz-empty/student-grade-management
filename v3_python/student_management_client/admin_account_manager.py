from logger import setup_logger


class AdminAccountManager:
    def __init__(self, network_client):
        self.network = network_client
        self.logger = setup_logger("admin_account")

    def list_accounts(self):
        """查看账户列表（管理员权限）"""
        request = {"action": "list_accounts"}

        response = self.network.send_request(request)

        if response and response.get("status") == 200:
            self.logger.info("成功获取账户列表")
            return True, response.get("data", [])
        else:
            error_msg = (
                response.get("message", "获取账户列表失败") if response else "无响应"
            )
            self.logger.warning(f"获取账户列表失败: {error_msg}")
            return False, error_msg

    def update_permission(self, username, new_permission):
        """修改账户权限（管理员权限）"""
        request = {
            "action": "update_permission",
            "username": username,
            "new_permission": new_permission,
        }

        response = self.network.send_request(request)

        if response and response.get("status") == 200:
            self.logger.info(f"成功更新{username}的权限为{new_permission}")
            return True, "权限更新成功"
        else:
            error_msg = (
                response.get("message", "权限更新失败") if response else "无响应"
            )
            self.logger.warning(f"权限更新失败: {error_msg}")
            return False, error_msg

    def delete_account(self, username):
        """删除账户（管理员权限）"""
        request = {"action": "delete_account", "username": username}

        response = self.network.send_request(request)

        if response and response.get("status") == 200:
            self.logger.info(f"成功删除账户: {username}")
            return True, "账户删除成功"
        else:
            error_msg = (
                response.get("message", "账户删除失败") if response else "无响应"
            )
            self.logger.warning(f"删除账户失败: {username}")
            return False, error_msg


# 测试管理员账户管理功能
if __name__ == "__main__":
    from network import NetworkClient
    from auth import AuthManager

    # 创建网络客户端
    client = NetworkClient()
    if not client.connect():
        exit(1)

    # 创建认证管理器并登录管理员账户
    auth = AuthManager(client)
    success, message, permission = auth.login("admin", "admin123")
    if not success:
        print(f"登录失败: {message}")
        client.close()
        exit(1)

    # 创建管理员账户管理器
    admin_account_manager = AdminAccountManager(client)

    # 测试查看账户列表功能
    success, accounts = admin_account_manager.list_accounts()
    if success:
        print("账户列表:")
        for account in accounts:
            if isinstance(account, dict):
                print(
                    f"    用户名: {account['username']}, 权限: {account['permission']}"
                )
    else:
        print(f"获取账户列表失败: {accounts}")

    # 测试修改权限
    test_username = "test_user99"
    success, message = admin_account_manager.update_permission(test_username, "admin")
    print(f"修改权限测试: {'成功' if success else '失败'}")

    # 测试删除账户
    success, message = admin_account_manager.delete_account(test_username)
    print(f"删除账户测试: {'成功' if success else '失败'}")

    # 注销并关闭连接
    auth.logout()
    client.close()
