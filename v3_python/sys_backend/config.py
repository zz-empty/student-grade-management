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


# 测试代码
if __name__ == "__main__":
    try:
        config = Config()
        print(f"Port: {config.server_port}")
        print(f"DB Host: {config.database_config['host']}")
        print("Config test passed!")
    except Exception as e:
        print(f"Config test failed: {str(e)}")
