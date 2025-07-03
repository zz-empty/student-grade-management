import socket
import threading
import json
import time
from config import Config
from logger import CustomLogger
from db_utils import AccountManager, StudentManager
import secrets
import mysql.connector


class ClientHandler:
    def __init__(
        self,
        client_socket,
        client_address,
        account_manager,
        student_manager,
        logger,
        session_timeout,
    ):
        self.client_socket = client_socket
        self.client_address = client_address
        self.account_manager = account_manager
        self.student_manager = student_manager
        self.logger = logger
        self.session_timeout = session_timeout
        self.user_info = {}
        self.last_activity = time.time()
        self.session_token = None
        self.running = True

    def start(self):
        """启动客户端处理线程"""
        threading.Thread(target=self.handle_client).start()

    def handle_client(self):
        """处理客户端连接的主循环"""
        try:
            self.logger.log_info(f"客户端{self.client_address}已连接")

            while self.running:
                # 检查会话超时
                if time.time() - self.last_activity > self.session_timeout:
                    self.send_response(408, "会话超时，请重新登录")
                    break

                # 接收数据
                try:
                    data = self.client_socket.recv(4096)
                    if not data:
                        break

                    self.last_activity = time.time()

                    # 解析请求
                    request = json.loads(data.decode("utf-8"))
                    action = request.get("action")

                    # 记录请求日志
                    self.logger.log_request(
                        self.client_address[0],
                        action,
                        True,
                        f"用户<{self.user_info['username'] if self.user_info else '未认证'}>",
                    )

                    # 处理请求
                    if action == "login":
                        self.handle_login(request)
                    elif action == "register":
                        self.handle_register(request)
                    elif action == "logout":
                        self.handle_logout()
                        break
                    elif self.user_info:
                        if action == "query_students":
                            self.handle_query_students()
                        elif action == "query_student_by_id":
                            self.handle_query_student_by_id(request)
                        elif action == "get_statistics":
                            self.handle_get_statistics()
                        elif action == "change_password":
                            self.handle_change_password(request)
                        elif action == "add_student":
                            self.handle_add_student(request)
                        elif action == "update_student":
                            self.handle_update_student(request)
                        elif action == "delete_student":
                            self.handle_delete_student(request)
                        elif action == "list_accounts":
                            self.handle_list_accounts()
                        elif action == "update_permission":
                            self.handle_update_permission(request)
                        elif action == "delete_account":
                            self.handle_delete_account(request)
                        else:
                            self.send_response(400, "未知操作")
                    else:
                        self.send_response(401, "请先登录")

                except json.JSONDecodeError:
                    self.send_response(400, "无效的JSON格式")
                except Exception as e:
                    self.logger.log_error(f"处理客户端请求时出错: {str(e)}")
                    self.send_response(500, "服务器内部错误")
                    break

        except Exception as e:
            self.logger.log_error(f"客户端处理异常: {str(e)}")
        finally:
            self.client_socket.close()
            self.logger.log_info(f"客户端{self.client_address}已断开连接")

    def generate_session_token(self):
        """生成安全的会话令牌"""
        return secrets.token_urlsafe(32)

    def send_response(self, status_code, message, data=None, include_token=False):
        """发送标准响应到客户端"""
        response = {"status": status_code, "message": message}

        if data is not None:
            response["data"] = data

        # 仅在登录响应中添加双重token
        if include_token and self.session_token:
            # 确保data存在
            if "data" not in response:
                response["data"] = {}
            # 添加data中的token
            response["data"]["token"] = self.session_token
            # 添加顶层token
            response["token"] = self.session_token

        # 修改发送格式，每条数据后加上\n作为结束标识
        response_json = json.dumps(response) + "\n"
        self.client_socket.sendall(response_json.encode("utf-8"))

    def handle_login(self, request):
        username = request.get("username")
        password = request.get("password")

        if not username or not password:
            self.send_response(400, "用户名和密码不能为空")
            return

        user_data, message = self.account_manager.verify_user(username, password)

        if not user_data:
            self.send_response(401, message)
            return

        self.user_info = user_data
        self.session_token = self.generate_session_token()

        # 构建符合文档的响应结构
        response_data = {
            "permission": user_data["permission"],
            "token": self.session_token,
        }

        # 发送响应并指定包含token
        self.send_response(200, "登陆成功", data=response_data, include_token=True)

    def handle_register(self, request):
        """处理注册请求"""
        username = request.get("username")
        password = request.get("password")

        if not username or not password:
            self.send_response(400, "用户名和密码不能为空")
            return

        success, message = self.account_manager.register_user(username, password)
        if success:
            self.send_response(201, message)
        else:
            self.send_response(400, message)

    def handle_logout(self):
        """处理注销请求"""
        self.send_response(200, "注销成功")
        self.running = False

    def handle_query_students(self):
        """处理查询所有学生请求"""
        # 所有登陆用户都可以查询所有学生信息
        success, msg, students = self.student_manager.query_students()
        if success:
            self.send_response(200, msg, students)
        else:
            self.send_response(500, msg)

    def handle_query_student_by_id(self, request):
        """按学号查询"""
        student_id = request.get("student_id")
        if not student_id:
            self.send_response(400, "学号不能为空")
            return

        # 所有登录用户都可以按照学号查询学生信息
        conn = None
        cursor = None

        try:
            conn = self.student_manager.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT student_id, name, gender, score1, score2, score3,
                    (score1 + score2 + score3) AS total
            FROM scores 
            WHERE student_id = %s 
            """
            cursor.execute(query, (student_id,))
            student = cursor.fetchone()

            if student:
                self.send_response(200, "查询成功", student)
            else:
                self.send_response(404, "未找到该学号对应的学生")

        except mysql.connector.Error as err:
            self.send_response(500, f"数据库错误: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def handle_get_statistics(self):
        """处理获取请求信息的请求"""
        # 所有登录用户都可以获取统计信息
        success, msg, status = self.student_manager.get_statistics()
        if success:
            self.send_response(200, msg, status)
        else:
            self.send_response(500, msg)

    def handle_change_password(self, request):
        """处理修改密码请求"""
        old_password = request.get("old_password")
        new_password = request.get("new_password")

        if not old_password or not new_password:
            self.send_response(400, "新旧密码都不能为空")
            return

        # 普通用户只能修改自己的密码
        success, msg = self.account_manager.change_password(
            self.user_info["username"],
            old_password,
            new_password,
        )

        if success:
            self.send_response(200, msg)
        else:
            self.send_response(400, msg)

    def handle_add_student(self, request):
        """处理添加学生请求"""
        if self.user_info and self.user_info["permission"] != "admin":
            self.send_response(403, "权限不足")
            return

        # 获取学生数据
        student_data = request["student_data"]
        if not student_data:
            self.send_response(400, "学生数据不能为空")
            return

        # 实现数据库添加逻辑
        conn = None
        cursor = None

        try:
            conn = self.student_manager.get_connection()
            cursor = conn.cursor()

            insert_query = """
            INSERT INTO scores (student_id, name, gender, score1, score2, score3) 
            VALUES (%s %s %s %s %s %s)
            """
            cursor.execute(
                insert_query,
                (
                    student_data["student_id"],
                    student_data["name"],
                    student_data["gender"],
                    student_data["score1"],
                    student_data["score2"],
                    student_data["score3"],
                ),
            )
            conn.commit()

            self.send_response(200, "添加学生成功")

        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.rollback()
            self.send_response(500, f"数据库错误: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def handle_update_student(self, request):
        """处理更新学生成绩请求"""
        if self.user_info and self.user_info["permission"] != "admin":
            self.send_response(403, "权限不足")
            return

        # 获取学生数据
        student_data = request.get("student_data")
        if not student_data:
            self.send_response(400, "学生数据不能为空")
            return

        # 实现数据库更新逻辑
        conn = None
        cursor = None
        try:
            conn = self.student_manager.get_connection()
            cursor = conn.cursor()

            update_query = """
            UPDATE scores 
            SET name = %s, gender = %s, score1 = %s, score2 = %s, score3 = %s
            WHERE student_id = %s
            """
            cursor.execute(
                update_query,
                (
                    student_data["name"],
                    student_data["gender"],
                    student_data["score1"],
                    student_data["score2"],
                    student_data["score3"],
                    student_data["student_id"],
                ),
            )
            conn.commit()

            if cursor.rowcount == 0:
                self.send_response(404, "未找到该学号对应的学生")
            else:
                self.send_response(200, "更新学生信息成功")
        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.rollback()
            self.send_response(500, f"数据库错误: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def handle_delete_student(self, request):
        """处理删除学生记录请求"""
        if self.user_info and self.user_info["permission"] != "admin":
            self.send_response(403, "权限不足")
            return

        student_id = request.get("student_id")
        if not student_id:
            self.send_response(400, "学号不能为空")
            return

        # 实现数据库删除逻辑
        conn = None
        cursor = None
        try:
            conn = self.student_manager.get_connection()
            cursor = conn.cursor()

            delete_query = "DELETE FROM scores WHERE student_id = %s"
            cursor.execute(delete_query, (student_id,))
            conn.commit()

            if cursor.rowcount == 0:
                self.send_response(404, "未找到该学号对应的学生")
            else:
                self.send_response(200, "删除学生成功")

        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.rollback()
            self.send_response(500, f"数据库错误: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def handle_list_accounts(self):
        """处理查看账户列表请求"""
        if self.user_info and self.user_info["permission"] != "admin":
            self.send_response(403, "权限不足")
            return

        # 管理员可以查看所有账户
        success, msg, accounts = self.account_manager.list_accounts()
        if success:
            self.send_response(200, msg, accounts)
        else:
            self.send_response(500, msg)

    def handle_update_permission(self, request):
        """处理修改账户权限请求"""
        if self.user_info and self.user_info["permission"] != "admin":
            self.send_response(403, "权限不足")
            return

        username = request.get("username")
        new_permission = request.get("new_permission")

        if not username or not new_permission:
            self.send_response(400, "用户名和新权限不能为空")
            return

        # 管理员可以修改账户权限
        success, msg = self.account_manager.update_permission(username, new_permission)
        if success:
            self.send_response(200, msg)
        else:
            self.send_response(400, msg)

    def handle_delete_account(self, request):
        """处理删除账户的请求"""
        if self.user_info and self.user_info["permission"] != "admin":
            self.send_response(403, "权限不足")
            return

        username = request["username"]
        if not username:
            self.send_response(400, "用户名不能为空")
            return

        # 管理员可以删除账户
        success, msg = self.account_manager.delete_account(username)
        if success:
            self.send_response(200, msg)
        else:
            self.send_response(400, msg)


class GradeServer:
    def __init__(self, config, logger, account_manager, student_manager):
        self.config = config
        self.logger = logger
        self.account_manager = account_manager
        self.student_manager = student_manager
        self.server_socket = None
        self.running = False
        self.thread_pool = []
        self.max_threads = 10  # 最大工作线程数

    def start(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("0.0.0.0", self.config.server_port))
            self.server_socket.listen(5)
            self.running = True

            self.logger.log_info(f"服务器启动，监听端口{self.config.server_port}")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.logger.log_info(f"接收来自{client_address}的连接")

                    # 创建新客户端处理程序
                    handler = ClientHandler(
                        client_socket,
                        client_address,
                        self.account_manager,
                        self.student_manager,
                        self.logger,
                        self.config.session_timeout,
                    )

                    # 启动新线程处理客户端
                    if len(self.thread_pool) < self.max_threads:
                        thread = threading.Thread(target=handler.handle_client)
                        thread_daemon = True
                        thread.start()
                        self.thread_pool.append(thread)
                    else:
                        self.logger.log_info("线程池已满，拒绝新连接")
                        client_socket.sendall(
                            json.dumps(
                                {"status": 503, "message": "服务器忙，请稍后再试"}
                            ).encode("utf-8")
                        )
                        client_socket.close()

                except socket.error:
                    if self.running:
                        self.logger.log_info("接收连接时出错")

        except Exception as e:
            self.logger.log_error(f"服务器启动失败: {str(e)}")
        # finally:
        # self.stop()

    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.logger.log_info("服务器已停止")


if __name__ == "__main__":
    # 加载配置
    config = Config()

    # 初始化日志
    logger = CustomLogger(config.log_file)

    # 初始化数据库管理器
    account_manager = AccountManager(config.database_config)
    student_manager = StudentManager(config.database_config)

    # 启动服务器
    server = GradeServer(config, logger, account_manager, student_manager)
    server.start()
