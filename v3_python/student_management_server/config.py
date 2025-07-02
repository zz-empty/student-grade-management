import json
import os


class Config:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.data = self._load_config()

    def _load_config(self):
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)

            # 验证必要配置项
            required_keys = [
                "server_port",
                "log_file",
                "session_timeout",
                "database",
            ]
            if not all(key in config for key in required_keys):
                raise ValueError("Missing required configuration keys")

            # 添加默认日志配置
            config.setdefault("log_max_bytes", 1048576)  # 默认1MB
            config.setdefault("log_backup_count", 3)  # 默认保留3个备份

            return config
        except Exception as e:
            print(f"Config load error: {str(e)}")
            raise

    @property
    def server_port(self):
        return self.data["server_port"]

    @property
    def log_file(self):
        return self.data["log_file"]

    @property
    def session_timeout(self):
        return self.data["session_timeout"]

    @property
    def database_config(self):
        return self.data["database"]

    @property
    def log_max_bytes(self):
        return self.data["log_max_bytes"]

    @property
    def log_backup_count(self):
        return self.data["log_backup_count"]


# 测试代码
if __name__ == "__main__":
    try:
        config = Config()
        print(f"Port: {config.server_port}")
        print(f"DB Host: {config.database_config['host']}")
        print(f"Log Max Bytes: {config.log_max_bytes}")
        print(f"Log Backup Count: {config.log_backup_count}")
        print("Config test passed!")
    except Exception as e:
        print(f"Config test failed: {str(e)}")
