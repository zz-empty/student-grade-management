import socket
from config import Config
from thread_pool import thread_pool
from request_handler import RequestHandler
from logger import request_logger


class GradeServer:
    def __init__(self):
        self.config = Config()
        self.server_socket = None
        self.running = False

    def start(self):
        self.running = True

        # 创建服务器套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            # 绑定端口
            self.server_socket.bind(("0.0.0.0", self.config.server_port))
            self.server_socket.listen(5)

            print(f"Server started on port {self.config.server_port}")
            request_logger.log(
                "SERVER", "START", True, extra=f"Port: {self.config.server_port}"
            )

            # 主循环接受连接
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    if self.config.debug_mode:
                        print(f"New connection from {client_address}")

                    # 将任务提交给线程池
                    thread_pool.submit(
                        self.handle_client, client_socket, client_address
                    )
                except socket.error:
                    if self.running:
                        print("Socket accept error")
                    break

        finally:
            if self.server_socket:
                self.server_socket.close()
            print("Server stopped")

    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            # 创建一个虚拟连接来打破accept阻塞
            try:
                dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dummy.connect(("localhost", self.config.server_port))
                dummy.close()
            except:
                pass

    def handle_client(self, client_socket, client_address):
        """处理客户端连接"""
        handler = RequestHandler(client_socket, client_address)
        handler.run()


if __name__ == "__main__":
    server = GradeServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()
