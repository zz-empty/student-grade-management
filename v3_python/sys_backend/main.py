import signal
import sys
from config import Config
from logger import CustomLogger
from db_utils import AccountManager, StudentManager
from network import GradeServer


class GradeServerApp:
    def __init__(self):
        # 加载配置
        self.config = Config()

        # 初始化日志
        self.logger = CustomLogger(self.config.log_file)

        # 初始化数据库管理器
        self.account_manager = AccountManager(self.config.database_config)
        self.student_manager = StudentManager(self.config.database_config)

        # 初始化服务器
        self.server = GradeServer(
            self.config, self.logger, self.account_manager, self.student_manager
        )

        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """处理退出信号"""
        self.logger.log_info(f"接收到终止信号（{signum}）, 正在关闭资源...")
        self.server.stop()
        sys.exit(0)

    def run(self):
        """启动服务器"""
        self.logger.log_info("启动学生成绩管理系统服务器")
        self.logger.log_info(f"服务器端口: {self.config.server_port}")
        self.logger.log_info(f"会话超时: {self.config.session_timeout}秒")

        try:
            self.server.start()
        except KeyboardInterrupt:
            self.logger.log_info("用户中断, 正在关闭服务器...")
            self.server.stop()
        except Exception as e:
            self.logger.log_error(f"服务器运行异常: {str(e)}")
            self.server.stop()
            sys.exit(1)


if __name__ == "__main__":
    app = GradeServerApp()
    app.run()
