import mysql.connector
from mysql.connector import pooling
import hashlib
import os
import configparser


class DatabaseManager:
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
        return os.urandom(16).hex()

    @staticmethod
    def hash_password(password, salt):
        """使用SHA-256算法哈希密码（密码+盐值）"""
        salted_password = password.encode() + salt.encode()
        return hashlib.sha256(salted_password).hexdigest()

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

    try:
        db_manager = DatabaseManager(test_config)

        # 测试注册和验证
        username = "test_user3"
        password = "secure_password123"

        # 注册测试用户
        reg_success, reg_msg = db_manager.register_user(username, password)
        print(f"注册结果: {reg_success} , 消息: {reg_msg}")

        # 验证测试用户
        if reg_success:
            user_data, auth_msg = db_manager.verify_user(username, password)
            print(f"验证结果: {auth_msg}")
            if user_data:
                print(f"用户信息: {user_data}")

        # 测试错误密码
        _, auth_msg = db_manager.verify_user(username, "wrong_password")
        print(f"错误密码测试: {auth_msg}")

        # 测试不存在的用户
        _, auth_msg = db_manager.verify_user("non_existent_user", "any_password")
        print(f"不存在的用户测试: {auth_msg}")

    except Exception as e:
        print(f"数据库管理器初始化失败: {str(e)}")
