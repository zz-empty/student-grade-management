import logging
import sys
from datetime import datetime
import socket


class CustomLogger:
    def __init__(self, log_file, log_to_console=True):
        self.logger = logging.getLogger("server_logger")
        self.logger.setLevel(logging.INFO)

        # 设置日志格式
        formatter = logging.Formatter(
            "%(asctime)s -[%(levelname)s]  -%(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 文件处理器
        file_handler = logging.FileHandler(log_file)
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
    logger = CustomLogger("test_log.log")

    # 测试不同日志级别
    logger.log_request("192.168.1.100", "LOGIN", True, "User:admin")
    logger.log_request("192.168.130.127", "LOGIN", False, "Permission denied")
    logger.log_info("Server starting...")
    logger.log_error("Database connect failed")
    logger.log_debug("Debugging connection pool")

    print("Logger test completed. Cleck test_log.log for output")
