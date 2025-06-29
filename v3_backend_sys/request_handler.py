import json
from database import DBManager
from logger import request_logger
from utils import hash_password


class RequestHandler:
    # 权限定义
    PERMISSIONS = {
        "admin": [
            "add_student",
            "delete_student",
            "update_student",
            "get_student",
            "list_students",
            "get_statistic",
            "change_password",
        ],
        "user": ["get_student", "list_students", "get_statistic", "change_password"],
    }

    def __init__(self, client_socket, client_address):
        # 初始化客户端连接信息
        self.client_socket = client_socket
        self.client_address = client_address
        # 初始化用户状态
        self.username = None
        self.permission = None
        self.authenticated = False

    def run(self):
        """主入口方法，处理请求"""
        try:
            # 1. 接收请求数据
            data = self._receive_data()
            if not data:
                return

            # 2. 解析json
            try:
                request = json.loads(data)
            except json.JSONDecodeError:
                self._send_response(False, "Invalid JSON Format")
                return

            # 3. 获取操作类型
            action = request.get("action")
            if not action:
                self._send_response(False, "Missing action field")
                return

            # 4. 特殊处理登陆请求（不需要认证）
            if action == "login":
                self._handle_login(request)

            # 5. 检查认证状态
            if not self.authenticated:
                self._send_response(False, "Not authenticated")
                request_logger.log(
                    self.client_address[0],
                    action,
                    False,
                    extra="Authenticated required",
                )
                return

            # 6. 检查权限
            if (
                self.permission is not None
                and action not in self.PERMISSIONS[self.permission]
            ):
                self._send_response(False, "Permission denied")
                request_logger.log(
                    self.client_address[0],
                    action,
                    False,
                    self.username,
                    extra="Permission denied",
                )
                return

            # 路由到相应的处理方法
            hander = getattr(self, f"_handle_{action}", None)
            if hander:
                hander(request)
            else:
                self._send_response(False, f"Unsupported action: {action}")
                request_logger.log(
                    self.client_address[0],
                    action,
                    False,
                    self.username,
                    extra="Unsupported action",
                )

        except Exception as e:
            # 异常处理
            error_msg = f"Error processing request: {str(e)}"
            self._send_response(False, error_msg)
        finally:
            # 关闭处理
            self.client_socket.close()

    def _handle_login(self, request):
        """处理登陆请求"""
        # 1. 获取用户名和密码
        username = request.get("username")
        password = request.get("password")

        # 2. 验证参数
        if not username or not password:
            self._send_response(False, "Missing username and password")
            request_logger.log(
                self.client_address[0], "login", False, extra="Missing credentials"
            )
            return

        try:
            # 查找是否有这个用户
            with DBManager() as db:
                result = db.execute_query(
                    "SELECT * FROM accounts WHERE username = %s", (username,)
                )

            if not result:
                self._send_response(False, "User not found")
                request_logger.log(
                    self.client_address[0],
                    "login",
                    False,
                    username,
                    extra="User not found",
                )
                return

            # 比对密码
            user = result[0]
            hashed_password = hash_password(password)

            if user["password"] != hashed_password:
                self._send_response(False, "Invalid password")
                request_logger.log(
                    self.client_address[0],
                    "login",
                    False,
                    username,
                    extra="Invalid password",
                )
                return

            # 登陆成功
            self.authenticated = True
            self.username = username
            self.permission = user["permission"]

            self._send_response(
                True,
                "Login successful",
                {"username": username, "permission": self.permission},
            )

            request_logger.log(self.client_address[0], "login", True, username)
        except Exception as e:
            self._send_response(False, f"Login failed: {str(e)}")
            request_logger.log(
                self.client_address[0], "login", False, username, extra=str(e)
            )

    def _receive_data(self):
        """接收完整请求数据（简单实现）"""
        buffer = b""
        while True:
            chunk = self.client_socket.recv(4096)
            if not chunk:
                break
            buffer += chunk
            # 如果数据小于4096，认为接收完成
            if len(chunk) < 4096:
                break
        return buffer.decode("utf-8")

    def _send_response(self, success, message, data=None):
        """发送响应给客户端"""
        response = {"success": success, "message": message, "data": data}
        json_response = json.dumps(response)
        self.client_socket.sendall(json_response.encode("utf-8"))

    def _handle_add_student(self, request):
        """添加学生"""
        try:
            student_id = request["student_id"]
            name = request["name"]
            gender = request["gender"]
            score1 = request["score1"]
            score2 = request["score2"]
            score3 = request["score3"]

            with DBManager() as db:
                db.execute_update(
                    "INSERT INTO scores (student_id, name, gender, score1, score2, score3) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (student_id, name, gender, score1, score2, score3),
                )

            self._send_response(True, "Student added successfully")
            request_logger.log(
                self.client_address[0],
                "add_student",
                True,
                self.username,
                f"ID: {student_id}",
            )

        except KeyError as e:
            self._send_response(False, f"Missing required field: {str(e)}")
            request_logger.log(
                self.client_address[0],
                "add_studnet",
                False,
                self.username,
                f"Missing field: {str(e)}",
            )

        except Exception as e:
            self._send_response(False, f"Failed to add student: {str(e)}")
            request_logger.log(
                self.client_address[0],
                "add_student",
                False,
                self.username,
                f"Missing field: {str(e)}",
            )

    def _handle_delete_student(self, request):
        """删除学生"""
        try:
            student_id = request["student_id"]

            with DBManager() as db:
                affected = db.execute_update(
                    "DELETE FROM scores WHERE student_id = %s", (student_id,)
                )

                if affected == 0:
                    self._send_response(False, "Student not found")
                    request_logger.log(
                        self.client_address[0],
                        "delete_student",
                        False,
                        self.username,
                        f"ID: {student_id}",
                    )
                else:
                    self._send_response(True, "Student delete successfully")
                    request_logger.log(
                        self.client_address[0],
                        "delete_student",
                        True,
                        self.username,
                        f"ID: {student_id}",
                    )
        except KeyError:
            self._send_response(False, "Missing student_id")
            request_logger.log(
                self.client_address[0],
                "delete_student",
                False,
                self.username,
                "Missing student_id",
            )
        except Exception as e:
            self._send_response(False, f"Failed to delete student: {str(e)}")
            request_logger.log(
                self.client_address[0], "delete_student", False, self.username, str(e)
            )

    def _handle_update_student(self, request):
        """更新学生信息"""
        try:
            student_id = request["student_id"]
            updates = {}

            # 收集要更改的字段
            for field in ["name", "gender", "score1", "score2", "score3"]:
                if field in request:
                    updates[field] = request[field]

            if not updates:
                self._send_response(False, "No fields to update")
                request_logger.log(
                    self.client_address[0],
                    "update_student",
                    False,
                    self.username,
                    "No update fields provided",
                )
                return

            # 构建SQL更新语句
            set_clause = ",".join([f"{field} = %s" for field in updates.keys()])
            values = list(updates.values())
            values.append(student_id)

            with DBManager() as db:
                affected = db.execute_update(
                    f"UPDATE scores SET {set_clause} WHERE student_id = %s",
                    tuple(values),
                )

            if affected == 0:
                self._send_response(False, "Student not found")
                request_logger.log(
                    self.client_address[0],
                    "update_student",
                    False,
                    self.username,
                    f"ID: {student_id} not found",
                )
            else:
                self._send_response(True, "Student updated successfully")
                request_logger.log(
                    self.client_address[0],
                    "update_student",
                    True,
                    self.username,
                    f"ID: {student_id}",
                )
        except KeyError:
            self._send_response(False, "Missing student_id")
            request_logger.log(
                self.client_address[0],
                "update_student",
                False,
                self.username,
                "Missing student_id",
            )
        except Exception as e:
            self._send_response(False, f"Failed to update student: {str(e)}")
            request_logger.log(
                self.client_address[0], "update_student", False, self.username, str(e)
            )

    def _handle_get_student(self, request):
        """获取单个学生信息"""
        try:
            student_id = request.get("student_id")
            name = request.get("name")

            if not student_id and not name:
                self._send_response(False, "Provide student_id or name")
                request_logger.log(
                    self.client_address[0],
                    "get_student",
                    False,
                    self.username,
                    "No identifier provided",
                )
                return

            with DBManager() as db:
                if student_id:
                    result = db.execute_query(
                        "SELECT * FROM scores WHERE student_id = %s", (student_id,)
                    )
                else:
                    result = db.execute_query(
                        "SELECT * FROM scores WHERE name = %s", (name,)
                    )

            if not result:
                self._send_response(False, "Student not found")
                request_logger.log(
                    self.client_address[0],
                    "get_student",
                    False,
                    self.username,
                    f"ID: {student_id or name} not found",
                )
            else:
                self._send_response(True, "Student found", result[0])
                request_logger.log(
                    self.client_address[0],
                    "get_student",
                    True,
                    self.username,
                    f"ID: {student_id or name}",
                )
        except Exception as e:
            self._send_response(False, f"Failed to get student: {str(e)}")
            request_logger.log(
                self.client_address[0], "get_student", False, self.username, str(e)
            )

    def _handle_list_students(self, request):
        """列出所有学生"""
        try:
            with DBManager() as db:
                result = db.execute_query("SELECT * FROM scores")

            self._send_response(True, "Students retrieved", result)
            request_logger.log(
                self.client_address[0],
                "list_students",
                True,
                self.username,
                f"Count: {len(result)}",
            )
        except Exception as e:
            self._send_response(False, f"Failed to list students: {str(e)}")
            request_logger.log(
                self.client_address[0], "list_students", False, self.username, str(e)
            )

    def _handle_get_statistic(self, request):
        """获取统计信息"""
        try:
            with DBManager() as db:
                # 计算各科平均分
                avg_scores = db.execute_query(
                    "SELECT AVG(score1) as avg1, AVG(score2) as avg2, AVG(score3) as avg3 FROM scores"
                )[0]

                # 计算各科最高分
                max_scores = db.execute_query(
                    "SELECT MAX(score1) as max1, MAX(score2) as max2, MAX(score3) as max3 FROM scores"
                )[0]

                # 计算各科最低分
                min_scores = db.execute_query(
                    "SELECT MIN(score1) as min1, MIN(score2) as min2, MIN(score3) as min3 FROM scores"
                )[0]

                # 计算学生总数
                total_students = db.execute_query(
                    "SELECT COUNT(*) as total FROM scores"
                )[0]["total"]

                result = {
                    "average_scores": avg_scores,
                    "max_scores": max_scores,
                    "min_scores": min_scores,
                    "total_students": total_students,
                }

                self._send_response(True, "Statistics retrieved", result)
                request_logger.log(
                    self.client_address[0], "get_statistic", True, self.username
                )
        except Exception as e:
            self._send_response(False, f"Failed to get statistics: {str(e)}")
            request_logger.log(
                self.client_address[0], "get_statistic", False, self.username, str(e)
            )

    def _handle_change_password(self, request):
        try:
            old_password = request["old_password"]
            new_password = request["new_password"]

            # 验证旧密码
            with DBManager() as db:
                user = db.execute_query(
                    "SELECT password FROM accounts WHERE username = %s",
                    (self.username,),
                )[0]

            if user["password"] != hash_password(old_password):
                self._send_response(False, "Old password is incorrect")
                request_logger.log(
                    self.client_address[0],
                    "change_password",
                    False,
                    self.username,
                    "Incorrect old password",
                )
                return

            # 更新密码
            new_hashed = hash_password(new_password)
            with DBManager() as db:
                db.execute_update(
                    "UPDATE accounts SET password = %s WHERE username = %s",
                    (new_hashed, self.username),
                )

            self._send_response(True, "Password changed successfully")
            request_logger.log(
                self.client_address[0], "change_password", True, self.username
            )
        except KeyError:
            self._send_response(False, "Missing old_password or new_password")
            request_logger.log(
                self.client_address[0],
                "change_password",
                False,
                self.username,
                "Missing password fields",
            )
        except Exception as e:
            self._send_response(False, f"Failed to change password: {str(e)}")
            request_logger.log(
                self.client_address[0], "change_password", False, self.username, str(e)
            )
