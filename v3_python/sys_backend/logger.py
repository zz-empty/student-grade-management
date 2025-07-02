import logging
import logging.handlers
import os
import sys
from datetime import datetime
import socket


class CustomLogger:
    def __init__(
        self, log_file, log_to_console=True, max_bytes=1024 * 1024, backup_count=3
    ):
        """
        创建自定义日志记录器

        参数:
        log_file: 日志文件名（不含路径）
        log_to_console: 是否输出到控制台
        max_bytes: 单个日志文件最大字节数（默认1MB）
        backup_count: 保留的备份日志文件数量（默认3个）
        """

        self.logger = logging.getLogger("server_logger")
        self.logger.setLevel(logging.INFO)

        # 确保日志目录存在
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 完整日志路径
        log_path = os.path.join(log_dir, log_file)

        # 设置日志格式
        formatter = logging.Formatter(
            "%(asctime)s -[%(levelname)s]  -%(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 文件处理器（带轮转功能）
        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 控制台处理器
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def log_request(self, client_ip, action, success, additional_info=""):
        """记录客户端请求日志"""
        status = "SUCCESS" if success else "FAIL"
        message = f"IP:{client_ip}  -ACTION:{action}\t-STATUS:{success}"
        if additional_info:
            message += f"  \t-INFO=({additional_info})"
        self.logger.info(message)

    def log_error(self, error_message):
        self.logger.error(error_message)

    def log_info(self, info_message):
        self.logger.info(info_message)

    def log_debug(self, debug_message):
        self.logger.debug(debug_message)


# 测试代码
if __name__ == "__main__":
    # 创建测试日志
    logger = CustomLogger("test_log.log", max_bytes=102400, backup_count=2)

    # 生成足够多的日志以触发轮转
    for i in range(1000):
        logger.log_info(
            f"测试日志条目 #{i + 1}: 这是一个测试消息，用于验证日志轮转功能是否正常工作"
        )

    print("日志轮转测试完成。请检查 logs/ 目录下的日志文件。")

    # 测试不同日志级别
    logger.log_request("192.168.1.100", "LOGIN", True, "User:admin")
    logger.log_request("192.168.130.127", "LOGIN", False, "Permission denied")
    logger.log_info("Server starting...")
    logger.log_error("Database connect failed")
    logger.log_debug("Debugging connection pool")

    print("Logger test completed. Cleck test_log.log for output")
