import os
import time
import threading
from constants import get_system_env
from settings import use_onedrivecmd


system_env = get_system_env()


class MySQLFile(object):
    def __init__(self, file_root, netdrive_name, tar_path):
        self.file_name = ''
        self.file_dir = file_root
        self.file_type = ''
        self.target_username = netdrive_name
        self.copy_name = ''

        # Ubuntu 下环境路径选项配置
        if system_env == 'linux':
            self.target_name = os.path.join(u'' + tar_path + '/'+file_root.split('/', 4)[4])
        # Window 下环境路径选项配置
        elif system_env == 'windows':
            self.target_name = os.path.join(u'' + tar_path +'/' +file_root[3:])
        if use_onedrivecmd == 'true':
            self.target_name = os.path.join(u'' + tar_path +'/' +file_root[3:].replace('$', '_'))
        
        self.start_time = time.time()
        self.complete_time = time.time()
        self.complete_type = False
        self.son_files_name = ''
        self.son_files_md5 = ''
        self.son_files_size = ''
        self.son_files_totalsize = 0
        self.remark1 = ''
        self.remark2 = ''
        self.fail_id = 0
        

class MyOriginFile(object):
    def __init__(self):
        self.p_name = ''
        self.file_name = ''
        self.file_dir = ''
        self.file_size = 0
        self.last_change_time = ''
        self.file_type = ''
        self.file_md5 = ''
        self.remark1 = ''
        self.remark2 = ''


