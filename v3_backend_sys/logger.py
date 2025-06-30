import logging
from config import Config


class RequestLogger:
    def __init__(self) -> None:
        config = Config()
        self.logger = logging.getLogger("request_logger")
        self.logger.setLevel(logging.INFO)

        # 文件处理器
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        self.logger.addHandler(file_handler)

        # 控制台处理器（如果开启debug模式）
        if config.debug_mode:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
            self.logger.addHandler(console_handler)

    def log(self, client_ip, action, success, username=None, extra=""):
        status = "SUCCESS" if success else "FAILED"
        user_info = f" by {username}" if username else ""
        message = f"{action}{user_info} - {status} - {client_ip}"
        if extra:
            message += f" - {extra}"

        self.logger.info(message)


# 全局日志实例
request_logger = RequestLogger()
