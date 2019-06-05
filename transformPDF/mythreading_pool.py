import threading
import time
from queue import Queue


class ThreadPoolManger(object):
    """线程池管理器"""
    def __init__(self, thread_num):
        # 初始化参数
        self.work_queue = Queue()
        self.thread_num = thread_num
        self.__init_threading_pool(self.thread_num)

    def __init_threading_pool(self, thread_num):
        # 初始化线程池，创建指定数量的线程池
        for _ in range(thread_num):
            thread = ThreadManger(self.work_queue)
            thread.setDaemon(True)
            thread.start()

    def add_job(self, func, *args):
        # 将任务放入队列，等待线程池阻塞读取，参数是被执行的函数和函数的参数
        self.work_queue.put((func, args))

class ThreadManger(threading.Thread):
    """定义线程类，继承threading.Thread"""
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        # super(ThreadManger, self).__init__()
        # super().__init__()
        self.work_queue = work_queue
        self.daemon = True

    def run(self):
        # 启动线程
        while True:
            target, args = self.work_queue.get()
            target(*args)
            self.work_queue.task_done()



if __name__ == '__main__':
    
    # 创建一个有4个线程的线程池
    thread_pool = ThreadPoolManger(4)

    def more_task(gener_obj):
        try:
            num = next(gener_obj)
        except StopIteration:
            pass
        else:
            print_num(num)

    def print_num(num):
        
        print('this num is {}'.format(num))
        print(threading.current_thread())
        time.sleep(5)


    g_obj = (x for x in range(100))
    # 循环等待接收客户端请求
    while True:
        thread_pool.add_job(more_task, *(g_obj, ))
        