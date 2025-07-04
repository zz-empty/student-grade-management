from os import error
import re
from sys import exc_info
from logger import setup_logger


class AdminStudentManager:
    def __init__(self, network_client):
        self.network = network_client
        self.logger = setup_logger("admin_student")

    def add_student(self, student_data):
        """添加学生信息"""
        request = {"action": "add_student", "student_data": student_data}

        response = self.network.send_request(request)

        if response and response.get("status") == 201:
            self.logger.info(f"添加学生成功: {student_data['student_id']}")
            return True, "添加学生成功"
        else:
            error_msg = response.get("message", "添加失败") if response else "无响应"
            self.logger.warning(f"添加学生失败: {error_msg}")
            return False, error_msg

    def update_student(self, student_data):
        """更新学生信息（管理员权限）"""
        request = {"action": "update_student", "student_data": student_data}

        response = self.network.send_request(request)

        if response and response.get("status") == 200:
            self.logger.info(f"更新学生成功: {student_data['student_id']}")
            return True, "更新学生信息成功"
        elif response and response.get("status") == 404:
            self.logger.warning(f"学生未找到: {student_data['student_id']}")
            return False, "未找到该学号对应的学生"
        else:
            error_msg = response.get("message", "更新失败") if response else "无响应"
            return False, error_msg

    def delete_student(self, student_id):
        """删除学生（管理员权限）"""
        request = {"action": "delete_student", "student_id": student_id}

        response = self.network.send_request(request)

        if response and response.get("status") == 200:
            self.logger.info(f"删除学生成功: {student_id}")
            return True, "删除成功"
        elif response and response.get("status") == 404:
            self.logger.warning(f"未找到该学生: {student_id}")
            return False, "未找到该学号对应的学生"
        else:
            error_msg = response.get("message", "删除失败") if response else "无响应"
            return False, error_msg


# 测试管理员学生管理的能力
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

    # 创建管理员学生管理器
    admin_student_manager = AdminStudentManager(client)

    # 测试添加学生
    new_student = {
        "student_id": "S100",
        "name": "测试人员",
        "gender": "男",
        "score1": 88,
        "score2": 89,
        "score3": 87,
    }

    success, message = admin_student_manager.add_student(new_student)
    print(f"添加学生测试: {'成功' if success else '失败'}  -{message}")

    # 测试更新学生
    update_student = {
        "student_id": "S100",
        "name": "测试老大",
        "gender": "女",
        "score1": 99,
        "score2": 98,
        "score3": 97,
    }

    success, message = admin_student_manager.update_student(update_student)
    print(f"更新学生测试: {'成功' if success else '失败'}  -{message}")

    # 测试添加学生
    success, message = admin_student_manager.delete_student("S100")
    print(f"删除学生测试: {'成功' if success else '失败'}  -{message}")

    # 注销并关闭连接
    auth.logout()
    client.close()
