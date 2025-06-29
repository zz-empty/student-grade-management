import threading
import queue
from config import Config


class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        super().__init__(daemon=True)
        self.task_queue = task_queue

    def run(self):
        while True:
            task, args, kwargs = self.task_queue.get()
            try:
                task(*args, **kwargs)
            except Exception as e:
                print(f"Error in worker thread: {e}")
            finally:
                self.task_queue.task_done()


class ThreadPool:
    def __init__(self, num_threads=None):
        if num_threads is None:
            config = Config()
            num_threads = config.db_pool_size * 2

        self.task_queue = queue.Queue()
        self.threads = []

        for _ in range(num_threads):
            thread = WorkerThread(self.task_queue)
            thread.start()
            self.threads.append(thread)

    def submit(self, task, *args, **kwargs):
        self.task_queue.put((task, args, kwargs))

    def wait_completion(self):
        self.task_queue.join()


# 全局线程池实例
thread_pool = ThreadPool()
