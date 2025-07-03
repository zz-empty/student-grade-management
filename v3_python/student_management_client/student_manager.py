import json
from os import error
from logger import setup_logger


class StudentManager:
    def __init__(self, network_client):
        self.network = network_client
        self.logger = setup_logger("student")

    def query_all_students(self):
        """查询所有学生成绩"""
        request = {"action": "query_students"}
        response = self.network.send_request(request)

        if response and response["status"] == 200:
            self.logger.info("成功查询所有学生")
            return True, response.get("data", [])
        else:
            error_msg = response.get("message", "查询失败") if response else "无响应"
            self.logger.warning(f"查询所有学生失败: {error_msg}")
            return False, error_msg

    def query_student_by_id(self, student_id):
        """按学号查询学生"""
        request = {"action": "query_student_by_id", "student_id": student_id}

        response = self.network.send_request(request)

        if response and response["status"] == 200:
            self.logger.info(f"查询成功: {student_id}")
            return True, response.get("data", {})
        elif response and response["status"] == 404:
            self.logger.warning(f"学生未找到: {student_id}")
            return False, "未找到该学生"
        else:
            error_msg = response.get("message", "查询失败") if response else "无响应"
            return False, error_msg

    def get_statistics(self):
        """获取成绩统计"""
        request = {"action": "get_statistics"}
        response = self.network.send_request(request)

        if response and response.get("status") == 200:
            self.logger.info("成功获取成绩统计")
            return True, response.get("data", {})
        else:
            error_msg = response.get("message", "统计失败") if response else "无响应"
            self.logger.warning(f"获取统计失败: {error_msg}")
            return False, error_msg


# 测试学生管理功能
if __name__ == "__main__":
    from network import NetworkClient
    from auth import AuthManager

    # 创建网络客户端
    client = NetworkClient()
    if not client.connect():
        exit(1)

    # 创建认证管理器并登录
    auth = AuthManager(client)
    success, message, permission = auth.login("test_user99", "password999")
    if not success:
        print(f"登录失败: {message}")
        client.close()
        exit(1)

    # 创建学生管理器
    student_manager = StudentManager(client)

    # 测试查询所有学生
    success, data = student_manager.query_all_students()
    if success:
        # 确保 data 是列表类型
        if isinstance(data, list):
            print(f"查询到 {len(data)} 名学生:")
            for student in data:
                # 确保 student 是字典类型
                if isinstance(student, dict):
                    student_id = student.get("student_id", "未知学号")
                    name = student.get("name", "未知姓名")
                    total = student.get("total", 0)
                    print(f"  {student_id} - {name}: {total}分")
                else:
                    print(f"无效的学生数据格式: {type(student)}")
        else:
            print(f"返回数据不是列表类型: {type(data)}")
    else:
        print(f"查询失败: {data}")

    # 测试按学号查询
    test_id = "S003"  # 使用实际存在的学号
    success, student = student_manager.query_student_by_id(test_id)
    if success:
        # 确保 student 是字典类型
        if isinstance(student, dict):
            print(f"学生详情: {student}")
        else:
            print(f"返回的学生数据不是字典类型: {type(student)}")
    else:
        print(f"按学号查询失败: {student}")

    # 测试获取统计
    success, stats = student_manager.get_statistics()
    if success:
        # 确保 stats 是字典类型
        if isinstance(stats, dict):
            print("成绩统计:")
            for subject, scores in stats.items():
                # 确保 scores 也是字典类型
                if isinstance(scores, dict):
                    avg = scores.get("avg", "未知")
                    max_score = scores.get("max", "未知")
                    print(f"  {subject}: 平均分 {avg}, 最高分 {max_score}")
                else:
                    print(f"科目 {subject} 的分数格式无效: {type(scores)}")
        else:
            print(f"返回的统计信息不是字典类型: {type(stats)}")
    else:
        print(f"获取统计失败: {stats}")

    # 注销并关闭连接
    auth.logout()
    client.close()
