import hashlib
import logging

from config import Config


# 加密密码
def hash_password(password):
    """使用SHA256加密密码"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# 返回一个日志记录器
# 参数：模块名字，日志文件名，记录日志等级
def setup_logger(name, log_file, level=logging.INFO):
    """创建并配置日志记录器"""
    # 格式器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 文件处理器
    handler = logging.FileHandler(log_file)
    # 应用格式器
    handler.setFormatter(formatter)

    # 记录器
    logger = logging.getLogger(name)
    # 记录什么级别的日志
    logger.setLevel(level)
    # 添加文件处理器
    logger.addHandler(handler)

    return logger


# 记录一条日志
# 参数：日志记录器，客户端的ip，请求的行为，是否成功，用户名，额外信息
def log_request(logger, client_ip, action, success, username=None, extra=""):
    """请求记录日志"""
    status = "SUCCESS" if success else "FAILED"
    user_info = f"by {username}" if username else ""
    message = f"{action}{user_info} - {status} - {client_ip}"

    if extra:
        message += f"- {extra}"

    logger.info(message)
    if Config().debug_mode:
        print(f"[DEBUG] {message}")
