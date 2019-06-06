import os
import configparser




DIR_PATH = os.path.split(os.path.realpath(__file__))[0]

conf = configparser.ConfigParser()
conf_path = os.path.join(DIR_PATH, 'myapp_config.txt')
conf.read(conf_path)

# address_info
local_address_host = conf.get('socket_info', 'socket_server_host')
local_address_port = conf.get('socket_info', 'socket_server_port')

# ftp_info
use_ftp_server = conf.get('ftp_info', 'use_ftp_server')
FTP_Server_Dir = conf.get('ftp_info', 'ftp_server_dir')
ftp_folder_max_count = conf.get('ftp_info', 'ftp_folder_max_count')
ftp_folder_max_size = conf.get('ftp_info', 'ftp_folder_max_size')

FTP_FOLDER_MAX_COUNT = int(ftp_folder_max_count)
FTP_FOLDER_MAX_SIZE = int(ftp_folder_max_size) * (1024 * 1024)  # M

# onedrive_info
use_onedrivecmd = conf.get('onedrive_info', 'use_onedrive_cmd')
drive_name = conf.get('onedrive_info', 'netdrive_name')

# database_info
USE_DB = conf.get('postgres_info', 'use_postgres')
DATABASE_NAME = conf.get('postgres_info', 'db_name')
DB_USER = conf.get('postgres_info', 'db_user')
DB_PASSWORD = conf.get('postgres_info', 'db_passwd')
DB_HOST = conf.get('postgres_info', 'db_host')
DB_PORT = conf.get('postgres_info', 'db_port')

# table_info
TABLE_PDF_ZIP = conf.get('postgres_info', 'pdf_table')
TABLE_PDF_ORIGIN = conf.get('postgres_info', 'pdf_origin_table')
TABLE_ALL_ORIGIN = conf.get('postgres_info', 'all_origin_table')


# threading_info
use_threadingpool = conf.get('thread_use', 'use_threading')




