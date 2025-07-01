import socket
import threading
import json
import time
from config import Config
from logger import CustomLogger
from db_utils import DatabaseManager
import secrets


class ClientHandler:
    def __init__(
        self, client_socket, client_address, db_manager, logger, session_timeout
    ):
        self.client_socket = client_socket
        self.client_address = client_address
        self.db_manager = db_manager
        self.logger = logger
        self.session_timeout = session_timeout
        self.user_info = None
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
                        f"用户: {self.user_info['usrname'] if self.user_info else '未认证'}",
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
                        if action == "query":
                            self.handle_query(request)
                        elif action == "add":
                            self.handle_add(request)
                        elif action == "update":
                            self.handle_update(request)
                        elif action == "delete":
                            self.handle_delete(request)
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

    def send_response(self, status_code, message, data=None):
        """发送标准响应到客户端"""
        response = {"status": status_code, "message": message, "data": data}

        if self.session_token:
            response["token"] = self.session_token

        self.client_socket.sendall(json.dumps(response).encode("utf-8"))

    def handle_login(self, request):
        username = request.get("username")
        password = request.get("password")

        if not username or not password:
            self.send_response(400, "用户名和密码不能为空")
            return

        user_data, message = self.db_manager.verify_user(username, password)

        if not user_data:
            self.send_response(401, message)
            return

        self.user_info = user_data
        self.session_token = self.generate_session_token()
        self.send_response(
            200,
            "登陆成功",
            {"permission": user_data["permission"], "token": self.session_token},
        )

    def handle_register(self, request):
        """处理注册请求"""
        username = request.get("username")
        password = request.get("password")

        if not username or not password:
            self.send_response(400, "用户名和密码不能为空")
            return

        success, message = self.db_manager.register_user(username, password)
        if success:
            self.send_response(201, message)
        else:
            self.send_response(400, message)

    def handle_logout(self):
        """处理注销请求"""
        self.send_response(200, "注销成功")
        self.running = False

    def handle_query(self, request):
        # 根据权限返回不同数据
        # TODO 实现数据库查询逻辑
        self.send_response(200, "查询成功", {"data": "成绩信息"})

    def handle_add(self, request):
        """处理添加学生请求"""
        if self.user_info and self.user_info["permission"] != "admin":
            self.send_response(403, "权限不足")
            return

        # TODO 实现数据库添加逻辑
        self.send_response(201, "添加成功")

    def handle_update(self, request):
        """处理更新学生成绩请求"""
        if self.user_info and self.user_info["permission"] != "admin":
            self.send_response(403, "权限不足")
            return

        # TODO 实现数据库更新逻辑
        self.send_response(200, "更新成功")

    def handle_delete(self, request):
        """处理删除学生记录请求"""
        if self.user_info and self.user_info["permission"] != "admin":
            self.send_response(403, "权限不足")
            return

        # TODO 实现数据库删除逻辑
        self.send_response(200, "删除成功")


class GradeServer:
    def __init__(self, config, logger, db_manager):
        self.config = config
        self.logger = logger
        self.db_manager = db_manager
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

            self.logger.log_info(f"服务器启动，监听接口{self.config.server_port}")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.logger.log_info(f"接收来自{client_address}的连接")

                    # 创建新客户端处理程序
                    handler = ClientHandler(
                        client_socket,
                        client_address,
                        self.db_manager,
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

        finally:
            self.stop()

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

    # 初始化数据库
    db_manager = DatabaseManager(config.database_config)

    # 启动服务器
    server = GradeServer(config, logger, db_manager)
    server.start()
