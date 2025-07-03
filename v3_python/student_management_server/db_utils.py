from hmac import new
import mysql.connector
from mysql.connector import pooling
import hashlib
import os
import secrets


class BaseDBManager:
    def __init__(self, db_config):
        self.pool = self._create_pool(db_config)

    def _create_pool(self, db_config):
        """创建数据库连接池"""
        try:
            return pooling.MySQLConnectionPool(
                pool_name="grade_pool",
                pool_size=db_config["pool_size"],
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"],
                charset="utf8mb4",
            )
        except mysql.connector.Error as err:
            print(f"创建连接池失败: {err}")
            raise

    def get_connection(self):
        """从连接池中获取一个连接"""
        try:
            return self.pool.get_connection()
        except mysql.connector.Error as err:
            print(f"获取数据库连接失败: {err}")
            raise

    @staticmethod
    def generate_salt():
        """生成安全的随机盐值"""
        return secrets.token_hex(16)

    @staticmethod
    def hash_password(password, salt):
        """使用SHA-256算法哈希密码（密码+盐值）"""
        salted_password = password.encode() + salt.encode()
        return hashlib.sha256(salted_password).hexdigest()


class AccountManager(BaseDBManager):
    def verify_user(self, username, password):
        """验证用户凭证"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # 查询用户信息
            query = (
                "SELECT password, salt, permission FROM accounts WHERE username = %s"
            )
            cursor.execute(query, (username,))
            user = cursor.fetchone()

            if not user:
                return None, "用户不存在"

            # 验证密码
            hashed_password = self.hash_password(password, user["salt"])
            if hashed_password != user["password"]:
                return None, "密码错误"

            return {"username": username, "permission": user["permission"]}, "验证成功"

        except mysql.connector.Error as err:
            return None, f"数据库连接错误: {err}"
        except Exception as e:
            return None, f"系统错误: {str(e)}"

        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def register_user(self, username, password, permission="user"):
        """注册新用户"""
        conn = None
        cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 检查用户名是否存在
            check_query = "SELECT username FROM accounts WHERE username = %s"
            cursor.execute(check_query, (username,))
            if cursor.fetchone():
                return False, "用户名已存在"

            # 生成盐值和哈希密码
            salt = self.generate_salt()
            hashed_pwd = self.hash_password(password, salt)

            # 插入新用户
            insert_query = """
            INSERT INTO accounts (username, password, salt, permission)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (username, hashed_pwd, salt, permission))
            conn.commit()

            return True, "注册成功"

        except mysql.connector.Error as err:
            # 发生错误时回滚
            if conn and conn.is_connected():
                conn.rollback()
            return False, f"数据库错误: {err}"
        except Exception as e:
            return False, f"系统错误: {str(e)}"
        finally:
            # 安全关闭资源
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def change_password(self, username, old_password, new_password):
        """修改用户密码"""
        # 先验证旧密码
        user_info, msg = self.verify_user(username, old_password)
        if not user_info:
            return False, msg

        conn = None
        cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 生成新的盐值和哈希密码
            new_salt = self.generate_salt()
            new_hashed_pwd = self.hash_password(new_password, new_salt)

            # 更新密码和盐值
            update_query = """
                UPDATE accounts
                SET password = %s, salt = %s
                WHERE username = %s
            """
            cursor.execute(update_query, (new_hashed_pwd, new_salt, username))
            conn.commit()

            return True, "密码修改成功"

        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.rollback()
            return False, f"数据库错误: {err}"
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def list_accounts(self):
        """获取账户列表（仅限管理员使用）"""
        conn = None
        cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT username, permission, created_at FROM accounts"
            cursor.execute(query)
            accounts = cursor.fetchall()

            # 格式化时间字段
            formatted_accounts = []
            for account in accounts:
                # 将 datetime 对象转换为字符串
                if account.get("created_at"):
                    account["created_at"] = account["created_at"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                formatted_accounts.append(account)

            return True, "查询成功", formatted_accounts

        except mysql.connector.Error as err:
            return False, f"数据库错误: {err}", None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def update_permission(self, username, new_permission):
        """更新账户权限（仅限管理员使用）"""
        conn = None
        cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            update_query = """
                UPDATE accounts
                SET permission = %s
                WHERE username = %s 
            """
            cursor.execute(update_query, (new_permission, username))
            conn.commit()

            if cursor.rowcount == 0:
                return False, "用户不存在"

            return True, "权限修改成功"

        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.rollback()
            return False, f"数据库错误: {err}"
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def delete_accout(self, username):
        """删除用户（仅限管理员使用）"""
        conn = None
        cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            delete_query = "DELETE FROM accounts WHERE username = %s"
            cursor.execute(delete_query, (username,))
            conn.commit()

            if cursor.rowconunt == 0:
                return False, "用户不存在"

            return True, "账户删除成功"

        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.rollback()
            return False, f"数据库错误: {err}"
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()


class StudentManager(BaseDBManager):
    def query_students(self):
        """查询所有学生成绩（按总分降序排序）"""
        conn = None
        cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT student_id, name, gender, score1, score2, score3,
                   (score1 + score2 + score3) AS total
            FROM scores
            ORDER BY total DESC
            """
            cursor.execute(query)
            students = cursor.fetchall()

            # 将元组列表转换为字典列表
            columns = [col[0] for col in cursor.description]
            students_dict = [dict(zip(columns, row)) for row in students]

            return True, "查询成功", students_dict

        except mysql.connector.Error as err:
            return False, f"数据库错误: {err}", None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def get_statistics(self):
        """得到各科统计信息（平均分，最高分）"""
        conn = None
        cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT 
                AVG(score1) AS avg1, MAX(score1) AS max1,
                AVG(score2) AS avg2, MAX(score2) AS max2,
                AVG(score3) AS avg3, MAX(score3) AS max3
            FROM scores
            """
            cursor.execute(query)
            stats = cursor.fetchone()

            # 将结果转换为符合接口文档的字典格式
            result = {
                "score1": {"avg": stats[0], "max": stats[1]},
                "score2": {"avg": stats[2], "max": stats[3]},
                "score3": {"avg": stats[4], "max": stats[5]},
            }

            return True, "统计成功", result

        except mysql.connector.Error as err:
            return False, f"数据库错误: {err}", None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()


# 测试代码
if __name__ == "__main__":
    # 测试配置（实际使用时应从config.json加载）
    test_config = {
        "host": "localhost",
        "port": 3306,
        "user": "v3mysql_user",
        "password": "v3mysql_user_pwd",
        "database": "student_grade_db",
        "pool_size": 2,
    }

    # 测试账户管理
    account_manager = AccountManager(test_config)

    # 测试学生管理
    student_manager = StudentManager(test_config)

    # 测试修改密码
    # 先注册一个测试账户
    """
    account_manager.register_user("test_user99", "password99")
    success, msg = account_manager.change_password(
        "test_user99", "password99", "password999"
    )
    print(f"修改密码: {success}, {msg}")
    """

    # 测试验证用户登陆
    """
    user_info, msg = account_manager.verify_user("test_user", "password999")
    if user_info:
        print(f"测试结果: {user_info['username']}, {user_info['permission']}, {msg}")
    else:
        print(f"测试结果: {msg}")
    """

    # 测试管理员的查看用户列表
    user_info, msg = account_manager.verify_user("admin", "admin123")
    if user_info:
        print(f"测试结果: {user_info['username']}, {user_info['permission']}, {msg}")
    else:
        print(f"测试结果: {msg}")
    success, msg, data = account_manager.list_accounts()
    if success:
        print("用户列表:")
        print(data)
    else:
        print(msg)

    # 测试查询成绩表
    success, msg, students = student_manager.query_students()
    if success:
        print("查询学生")
        print(students)
    else:
        print(f"查询学生失败: {msg}")
