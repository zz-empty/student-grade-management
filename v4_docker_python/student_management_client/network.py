import socket
import json
from datetime import datetime
from logger import setup_logger


class NetworkClient:
    def __init__(self, host="localhost", port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.token = None
        self.last_activity = datetime.now()
        self.logger = setup_logger("network")  # 添加日志记录器

    def connect(self):
        """建立TCP连接"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.logger.info(f"成功连接到服务器 {self.host}:{self.port}")
            print(f"✅ 成功连接到服务器 {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"连接失败: {str(e)}")
            print(f"❌ 连接失败: {str(e)}")
            return False

    def send_request(self, request_data):
        """发送请求并获取响应"""
        if not self.socket:
            self.logger.warning("尝试发送请求但未连接到服务器")
            print("⚠️ 未连接到服务器，请先连接")
            return None

        # 更新活动时间
        self.last_activity = datetime.now()

        # 添加token到请求（如果存在）
        if self.token:
            request_data["token"] = self.token

        # 发送请求
        try:
            request_json = json.dumps(request_data) + "\n"
            self.socket.sendall(request_json.encode("utf-8"))
            self.logger.debug(f"发送请求: {request_json.strip()}")

            # 接收响应
            response_data = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b"\n" in chunk:
                    break

            response = json.loads(response_data.decode("utf-8").strip())
            self.logger.debug(f"收到响应: {response}")
            return response
        except Exception as e:
            self.logger.error(f"通信错误: {str(e)}")
            print(f"❌ 通信错误: {str(e)}")
            return None

    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()
            self.socket = None
            self.logger.info("连接已关闭")
            print("🔌 连接已关闭")

    def check_timeout(self):
        """检查超时（30分钟无活动）"""
        idle_time = (datetime.now() - self.last_activity).total_seconds()
        return idle_time > 1800  # 30分钟


# 测试网络连接
if __name__ == "__main__":
    client = NetworkClient()
    if client.connect():
        response = client.send_request({"action": "test"})
        print("测试响应:", response)
        client.close()
