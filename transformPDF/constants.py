import time
from functools import wraps
import psutil
import re, sys
import threading
import datetime
import logging
import platform
import os
from os.path import join, getsize


def get_current_time_human():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return current_time

def get_system_env():
    system_env = platform.platform()
    if system_env.startswith('Windows'):
        return 'windows'
    elif system_env.startswith('Linux'):
        return 'linux'
    
# 显示函数运行时间装饰器
def fn_timer(function):
    @wraps(function)
    def inner_function(*args, **kwargs):
        t0 = time.time()
        func_result = function(*args, **kwargs)
        t1 = time.time()
        print('Total time {} running:{} seconds'.format(function.__name__, round(t1-t0, 2)))
        return func_result
    return inner_function


# 显示函数上传流量及速度的装饰器
def upload_send_speed(function):
    @wraps(function)
    def inner_function(*args, **kwargs):
        bt = time.time()
        begin_info = psutil.net_io_counters()
        func_result = function(*args, **kwargs)
        et = time.time()
        end_info = psutil.net_io_counters()
        begin_send = int(re.findall(r'\d+', str(begin_info))[0])
        end_send = int(re.findall(r'\d+', str(end_info))[0])
        total_data = (end_send-begin_send)/(1024 * 1024) 
        print('Total send data:{} MB'.format(round(total_data, 6)))
        print('the speed is {} MB/s'.format(round(total_data/(et-bt), 6)))
        return func_result
    return inner_function



def get_send_speed():
    t1 = threading.Thread(target=_current_sent_speed)
    t1.setDaemon(True)
    t1.start()
     
def _current_sent_speed():
    begin_info = psutil.net_io_counters()
    time.sleep(1)
    end_info = psutil.net_io_counters()
    begin_send = int(re.findall(r'\d+', str(begin_info))[0])
    end_send = int(re.findall(r'\d+', str(end_info))[0])
    total_data = (end_send-begin_send)/(1024 * 1024) 
    current_sent_speed = round(total_data, 6)
    print('current sent speed is {} MB/s'.format(current_sent_speed))
    return current_sent_speed

# 物理CPU核心，非超线程
def get_cpu_count():
    return psutil.cpu_count(logical=False)


def get_threadpool_count():
    the_cpu_count = get_cpu_count()
    print('=='*50)
    print('CPU 物理核心数为：{}'.format(the_cpu_count))
    print('=='*50)
    if the_cpu_count < 8:
        thread_pool_count = the_cpu_count * 2
    else:
        thread_pool_count = the_cpu_count
    return thread_pool_count


# 字节大小转换
def bytes2human(n):
    """
    >>>bytes2human(10000)
    '9.8k'
    >>>bytes2human(100001221)
    '95.4M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2fB' % (n)

# 秒转年月日
def second2human(n):
    """
    年：31 536 000（天）
    年：31 104 000（月份）
    月：2 592 000
    天：86 400
    小时：3 600
    分钟：60
    """
    need_year = 0
    need_month = 0
    need_day = 0
    need_hour = 0
    need_minute = 0
    need_second = 0
    if n > 31536000:
        need_year = n // 31536000
        n = n % 31536000
    if n > 2592000:
        need_month = n // 2592000
        n = n % 2592000
    if n > 86400:
        need_day = n // 86400
        n = n % 86400
    if n > 3600:
        need_hour = n // 3600
        n = n % 3600
    if n > 60:
        need_minute = n // 60
        need_second = n % 60
    last_msg = '{}年{}月{}日{}小时{}分钟{}秒'.format(need_year, need_month, need_day, need_hour, need_minute, need_second)
    return last_msg

# 获取磁盘信息
def get_disk_info(folder):
    """
    Return folder info
    """
    disk_info = str(psutil.disk_usage(folder))
    # print(disk_info)
    disk_info_list = re.findall(r'\d+', disk_info)
    # print(disk_info_list)
    total_disk_size = int(disk_info_list[0])
    use_disk_size = int(disk_info_list[1])
    use_percent = round(use_disk_size/total_disk_size, 4)
    print('total_disk_size:{},use_disk_size:{},use_percent:{}%'.format(bytes2human(total_disk_size),bytes2human(use_disk_size), use_percent))



def getdirsize(path1):
    size = 0
    for root, _, files in os.walk(path1):
        size += sum([getsize(join(root, name)) for name in files])
    return size


def get_ftpserver_last_name(ftp_path, ftp_list):
    max_number = 0
    last_name = ''
    if len(ftp_list) != 0:
        for i in ftp_list:
            if int(i[-9:]) > max_number:
                max_number = int(i[-9:])
        last_name = ftp_list[0][:-9] + '%09d' % max_number

    return last_name


def set_logger_obj(logger_obj_name, logger_file_name, logger_level=logging.DEBUG):

    # 创建日志的实例
    logger = logging.getLogger(logger_obj_name)
    # 定制Logger的输出格式
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    # 时间，错误名称，错误级别
    # 创建日志，文件日志，终端日志
    file_handler = logging.FileHandler(logger_file_name)
    file_handler.setFormatter(formatter)
    consle_handler = logging.StreamHandler(sys.stdout)
    consle_handler.setFormatter(formatter)

    # 设置日志的默认级别
    logger.setLevel(logger_level)

    # 把文件日志和终端日志添加到日志处理器中
    logger.addHandler(file_handler)
    logger.addHandler(consle_handler)

    return logger





















# queue  error
# def get_ftpserver_last_name(path1, queue_obj):
#     last_name = ''
#     max_number = 0
#     queue_set = set()
#     queue_list = list()
#     current_name = ''
#     while queue_obj.qsize() != 0:
#         queue_set.add(queue_obj.get())
#         queue_list.append(queue_obj.get())
    

#     for i in os.listdir(path1):
#         if max_number != 0:
#             print(111111111111)
#             current_name = i[:-9] + '%09d' % max_number
#             print('current_name:{}'.format(current_name))
#         try:
#             last_number = int(i[-9:])
#         except:
#             print('{}名字后缀有问题'.format(i))
#         if os.path.isdir(os.path.join(path1, i)):
#             if last_number > max_number:
#                 if current_name != '':
#                     # queue_set.add(current_name)
#                     if current_name not in queue_list:
#                         queue_list.append(current_name)
#                 max_number = last_number
#                 last_name = i
            
#     # for j in queue_set:
#     for j in queue_list:
#         queue_obj.put(j)
#     # print('当前队列大小：{}'.format(queue_obj.qsize()))
#     # print('队列内容：{}'.format(queue_set))
#     return last_name



    


if __name__ == "__main__":
    pass
    # test_floder = 'D:/img'
    # # print(get_disk_info(test_floder))



    # size = getdirsize(test_floder)
    # print('There are %.3f' % (size / 1024 / 1024), 'Mbytes in {}'.format(test_floder))\
    second2human(86400)


