import json
import os


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path) as f:
            config = json.load(f)

        self.server_port = config.get("server_port", 8888)
        self.debug_mode = config.get("debug_mode", False)

        db_config = config.get("database", {})
        self.db_host = db_config.get("host", "localhost")
        self.db_port = db_config.get("port", 3306)
        self.db_user = db_config.get("user", "v3mysql_usr")
        self.db_password = db_config.get("password", "v3mysql_usr_pwd")
        self.db_name = db_config.get("database", "student_grade_db")
        self.db_pool_size = db_config.get("pool_size", 5)

        self.log_file = config.get("log_file", "server_log")


# 初始化配置
def init_config():
    config_data = {
        "server_port": 8888,
        "debug_mode": True,
        "log_file": "server_log",
        "database": {
            "host": "localhost",
            "post": 3306,
            "user": "v3mysql_usr",
            "password": "v3mysql_usr_pwd",
            "database": "student_grade_db",
            "pool_size": 5,
        },
    }

    with open("config.json", "w") as f:
        json.dump(config_data, f, indent=2)

    print("配置文件已创建: config.json")


if __name__ == "__main__":
    init_config()
