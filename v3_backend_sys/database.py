import pymysql
import threading
from queue import Queue
from config import Config
import logging

from pymysql.cursors import DictCursor

# 设置日志
logger = logging.getLogger('database')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class DBPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.init_pool()
        return cls._instance

    def init_pool(self):
        config = Config()
        self.pool = Queue(config.db_pool_size)
        self.pool_size = config.db_pool_size
        
        logger.info(f"Initializing database pool with {self.pool_size} connections")
        
        for _ in range(self.pool_size):
            try:
                conn = pymysql.connect(
                    host=config.db_host,
                    port=config.db_port,
                    user=config.db_user,
                    password=config.db_password,  # 修复：使用正确的参数名 'password'
                    database=config.db_name,
                    charset="utf8mb4",
                    cursorclass=DictCursor,
                )

                # 设置事务的隔离级别为可重复读
                conn.autocommit(False)
                with conn.cursor() as cursor:
                    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                
                self.pool.put(conn)
                logger.debug("Created database connection")
                
            except pymysql.Error as e:
                logger.error(f"Failed to create database connection: {e}")
                # 如果无法创建连接，添加 None 作为占位符
                self.pool.put(None)

    def get_connection(self):
        conn = self.pool.get()
        if conn is None:
            # 尝试重新创建连接
            try:
                config = Config()
                conn = pymysql.connect(
                    host=config.db_host,
                    port=config.db_port,
                    user=config.db_user,
                    password=config.db_password,
                    database=config.db_name,
                    charset="utf8mb4",
                    cursorclass=DictCursor,
                )
                conn.autocommit(False)
                with conn.cursor() as cursor:
                    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                logger.info("Recreated database connection")
            except pymysql.Error as e:
                logger.error(f"Failed to recreate database connection: {e}")
                raise
        return conn

    def release_connection(self, conn):
        if conn and not conn.open:
            # 如果连接已关闭，创建新连接替代
            try:
                config = Config()
                new_conn = pymysql.connect(
                    host=config.db_host,
                    port=config.db_port,
                    user=config.db_user,
                    password=config.db_password,
                    database=config.db_name,
                    charset="utf8mb4",
                    cursorclass=DictCursor,
                )
                new_conn.autocommit(False)
                with new_conn.cursor() as cursor:
                    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                self.pool.put(new_conn)
                logger.info("Replaced closed database connection")
            except pymysql.Error as e:
                logger.error(f"Failed to replace closed connection: {e}")
                self.pool.put(None)
        else:
            self.pool.put(conn)

    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            if conn:
                try:
                    conn.close()
                except:
                    pass


class DBManager:
    def __init__(self):
        self.pool = DBPool()
        self.conn = self.pool.get_connection()

    def __enter__(self):
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
                logger.error(f"Database operation failed: {exc_val}")
        except pymysql.Error as e:
            logger.error(f"Commit/rollback failed: {e}")
        finally:
            try:
                self.cursor.close()
            except:
                pass
            
            # 释放连接回连接池
            self.pool.release_connection(self.conn)

    def execute_query(self, query, args=None):
        try:
            with self as cursor:
                cursor.execute(query, args or ())
                return cursor.fetchall()
        except pymysql.Error as e:
            logger.error(f"Query failed: {e}\nQuery: {query}\nArgs: {args}")
            raise

    def execute_update(self, query, args=None):
        try:
            with self as cursor:
                affected = cursor.execute(query, args or ())
                return affected
        except pymysql.Error as e:
            logger.error(f"Update failed: {e}\nQuery: {query}\nArgs: {args}")
            raise

    def execute_insert(self, query, args=None):
        try:
            with self as cursor:
                cursor.execute(query, args or ())
                return cursor.lastrowid
        except pymysql.Error as e:
            logger.error(f"Insert failed: {e}\nQuery: {query}\nArgs: {args}")
            raise
