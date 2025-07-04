from network import NetworkClient
from logger import setup_logger


class AuthManager:
    def __init__(self, network_client):
        self.network = network_client
        self.logger = setup_logger("auth")
        self.permission = None

    def register(self, username, password):
        """注册新用户"""
        requset = {"action": "register", "username": username, "password": password}

        response = self.network.send_request(requset)

        if response and response.get("status") == 201:
            self.logger.info(f"用户注册成功: {username}")
            return True, "注册成功"
        else:
            error_msg = response.get("message", "未知错误") if response else "无响应"
            self.logger.warning(f"注册失败: {error_msg}")
            return False, error_msg

    def login(self, username, password):
        """用户登录"""
        requset = {"action": "login", "username": username, "password": password}

        response = self.network.send_request(requset)

        if response and response.get("status") == 200:
            self.network.token = response.get("token")
            self.permission = response["data"]["permission"]
            self.logger.info(f"登录成功: {username}, 权限: {self.permission}")
            return True, "登录成功", self.permission
        else:
            error_msg = response.get("message", "登录失败") if response else "无响应"
            self.logger.warning(f"登录失败: {error_msg}")
            return False, error_msg, None

    def logout(self):
        """用户注销"""
        request = {"action": "logout"}

        response = self.network.send_request(request)

        if response and response.get("status") == 200:
            self.permission = None
            self.network.token = None
            self.logger.info("注销成功")
            return True, "注销成功"
        else:
            error_msg = response.get("message", "注销失败") if response else "无响应"
            self.logger.warning(f"注销失败: {error_msg}")
            return False, error_msg

    def change_password(self, old_password, new_password):
        """修改密码"""
        request = {
            "action": "change_password",
            "old_password": old_password,
            "new_password": new_password,
        }

        response = self.network.send_request(request)

        if response and response.get("status") == 200:
            self.logger.info("密码修改成功")
            return True, "密码修改成功"
        else:
            error_msg = response.get("message", "修改失败") if response else "无响应"
            self.logger.warning(f"密码修改失败: {error_msg}")
            return False, error_msg


# 测试用户认证功能
if __name__ == "__main__":
    # 创建网络客户端
    client = NetworkClient()
    if not client.connect():
        exit(1)

    # 创建认证管理器
    auth = AuthManager(client)

    # 测试注册
    username = "test_user22"
    password = "test_password"

    # success, message = auth.register(username, password)
    # print(f"注册测试: {'成功' if success else '失败'} - {message}")

    # 测试登录
    success, message, permission = auth.login(username, password)
    print(f"登录测试: {'成功' if success else '失败'} - {message}, 权限: {permission}")

    # 测试修改密码
    success, message = auth.change_password(password, "new_password")
    print(f"修改密码测试: {'成功' if success else '失败'} - {message}")

    # 测试注册
    success, message = auth.logout()
    print(f"注销测试: {'成功' if success else '失败'} - {message}")

    # 关闭连接
    client.close()
