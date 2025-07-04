import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name):
    """配置日志记录器"""
    # 确保logs目录存在
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建日志文件路径
    log_file = os.path.join(log_dir, f"{name}.log")

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 日志格式
    formatter = logging.Formatter("%(asctime)s  -[%(levelname)s]  -%(message)s")

    # 文件处理器  --滚动日志（1MB * 3）
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1 * 1024 * 1024, backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台处理器（仅错误级别）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    test_logger = setup_logger("test")
    test_logger.info("这是一条测试信息")
    test_logger.warning("这是一条测试警告")
    test_logger.error("这是一个测试错误")
    print("✅ 日志测试完成，请检查 logs/test.log文件")
