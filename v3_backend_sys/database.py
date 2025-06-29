import pymysql
import threading
from queue import Queue

from pymysql.cursors import DictCursor
from config import Config


class DBPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        config = Config()
        self.pool = Queue(config.db_pool_size)

        for _ in range(config.db_pool_size):
            conn = pymysql.connect(
                host=config.db_host,
                port=config.db_port,
                user=config.db_user,
                passwd=config.db_password,
                database=config.db_name,
                charset="utf8mb4",
                cursorclass=DictCursor,
            )

            # 设置事务的隔离级别为可重复读
            conn.autocommit(False)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ"
                )

            self.pool.put(conn)

    def get_connection(self):
        return self.pool.get()

    def release_connection(self, conn):
        self.pool.put(conn)

    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()


class DBManager:
    def __init__(self):
        self.pool = DBPool()
        self.conn = self.pool.get_connection()

    def __enter__(self):
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()  # 提交事务
        else:
            self.conn.rollback()  # 回滚事务

        # 正确做法：只归还连接，不关闭
        self.pool.release_connection(self.conn)

    def execute_query(self, query, args=None):
        with self as cursor:
            cursor.execute(query, args or ())
            return cursor.fetchall()

    def execute_update(self, query, args=None):
        with self as cursor:
            affected = cursor.execute(query, args or ())
            return affected

    def execute_insert(self, query, args=None):
        with self as cursor:
            cursor.execute(query, args or ())
            return cursor.lastrowid
