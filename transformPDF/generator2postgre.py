import psycopg2, img2pdf, psutil
import os, time, shutil, zipfile, configparser, imghdr, hashlib, datetime, threading
from PyPDF2 import PdfFileReader as pdfreader, PdfFileWriter as pdfwriter

from file_obj import MyOriginFile, MySQLFile
from postgres_table_sql import PDF_SEQ, ORIGIN_SEQ, ALL_SEQ, DB_NAME, DB_NAME_EXIST
from postgres_table_sql import PDF_ZIP_TABLE, PDF_ORIGIN_FILES, ALL_ORIGIN_FILES
from postgres_func_sql import DROP_INSERT_FUNCTION_SQL, DROP_ORIGIN_FUNCTION_SQL, DROP_UPDATE_FUNCTION_SQL, DROP_EXIST_FUNCTION_SQL
from postgres_func_sql import INSERT_SQL_ORIGIN, INSERT_SQL_PDF, UPDATE_SQL_PDF, FILE_OBJ_EXIST
from mytkinter import CheckTK, MyPDFTk
from constants import second2human, get_threadpool_count, getdirsize, get_ftpserver_last_name

from settings import drive_name
from settings import use_threadingpool
from settings import local_address_host as local_host, local_address_port as local_port
from settings import DATABASE_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
from settings import TABLE_PDF_ZIP, TABLE_PDF_ORIGIN, TABLE_ALL_ORIGIN
from settings import FTP_FOLDER_MAX_SIZE, FTP_FOLDER_MAX_COUNT, FTP_Server_Dir, use_ftp_server

from mythreading_pool import ThreadManger, ThreadPoolManger

ftd_folder_list = []

class MyPdfZip(object):
    def __init__(self):
        self.py_windows = MyPDFTk(self.threading_begin, self.query_fail_reson, self.handle_fail_file, self.threading_stop)
        self.path1 = self.py_windows.path1
        self.path2 = self.py_windows.path2
        self.chose_fail = self.py_windows.chose_fail
        self.show_error = self.py_windows.show_error
        self.path3 = self.py_windows.path3
        self.fail_file_obj = []
        self.postgre_func_isfirst = True
        self.current_finish_size = 0
    
        self.t1 = threading.Thread(target=self.start)
        self.t1.setDaemon(True)


    def run(self):
        if use_ftp_server == 'true':
            self.init_ftp_list()
        self.init_db_create()
        self.conn = psycopg2.connect(database=DATABASE_NAME, user=DB_USER, password=DB_PASSWORD,host=DB_HOST,port=DB_PORT)
        # 初始化postgresql 表
        self.init_db_table()
        # 初始化postgresql 函数
        self.init_postgresqk_func()
        # 启动前查询数据库中失败的文件
        self.query_fail_files()
        self.current_totalsize()
        self.py_windows.run()

    def init_ftp_list(self):
        global ftd_folder_list
        ftd_folder_list = []
        if not os.path.exists(FTP_Server_Dir):
            try:
                os.makedirs(FTP_Server_Dir)
            except FileExistsError:
                pass
        _,ftp_dirs,_ = next(os.walk(FTP_Server_Dir))
        if len(ftp_dirs) != 0:
            for ftp_dir in ftp_dirs:
                ftd_folder_list.append(ftp_dir)
        print('时间：{}，FTP服务器文件夹：{}'.format(datetime.datetime.now(), ftd_folder_list))
        

    def current_totalsize(self):
        cur = self.conn.cursor()
        if self.path3.get() != '':
            SQL1 = 'select sum(s_files_totalsize) from {}'.format(TABLE_ALL_ORIGIN)
            cur.execute(SQL1)
            copy_totalsize_sum = cur.fetchone()
            cur.close()
            if copy_totalsize_sum[0]:
                self.current_finish_size = copy_totalsize_sum[0] / (1024 * 1024)
                print('=='*50)
                print('<<<数据库中已经完成{} GB文件的拷贝>>>'.format(round(self.current_finish_size, 2)))
                print('=='*50)
        else:
            SQL2 = 'select sum(s_files_totalsize) from {}'.format(TABLE_PDF_ORIGIN)
            cur.execute(SQL2)
            pdf_totalsize_sum = cur.fetchone()
            if pdf_totalsize_sum[0]:
                self.current_finish_size = pdf_totalsize_sum[0] / (1024 * 1024)
                print('<<<数据库中已经完成{} GB文件的PDF 文件合成>>>'.format(round(self.current_finish_size, 2)))
            

    def generate_allfiles(self, t_pool=None):
        rootdir = self.path1.get()
        path_g_obj = os.walk(rootdir)
        while True:
            try:
                list_dir = next(path_g_obj)
                # None 说明不是处理的失败的文件，否则此处应该放(目标路径, 复制路径)
                list_dir = list_dir + (None, None)
            except StopIteration:
                break
            else:
                if t_pool:
                    t_pool.add_job(self.composite_files, *(list_dir,))
                else:
                    self.composite_files(list_dir)
                
        
    def recode_origin_files(self, obj, file_root, file_names_list):
        O_SQL_FIELD = '{f_name, file_dir, s_files_name, s_files_md5, s_files_size, s_files_totalsize, remark1}'
        if obj.copy_name and obj.file_name[-3:] != 'pdf':
            self.generate_zipfile(obj, file_names_list, generate_type='copy')
            self.shutil_move(obj, shutil_type='copy')
            obj.remark1 = 'ALL2ZIP'
            # 完成流程
            self.current_totalsize()
            

        # 记录源文件的父名字，所有文件名字，大小，md5，等等
        for origin_file in file_names_list:
            # 初始化源文件 文件对象
            o_obj = MyOriginFile()
            o_obj.file_name = origin_file[len(file_root) + 1:]
            o_obj.file_size = os.path.getsize(origin_file) / 1024  # 大小的单位是KB
            o_obj.file_type = imghdr.what(origin_file)
            with open(origin_file, 'rb') as f:
                contents = f.read()
            o_obj.file_md5 = hashlib.md5(contents).hexdigest()
            obj.son_files_name += o_obj.file_name + '&'
            obj.son_files_md5 += o_obj.file_md5 + '&'
            obj.son_files_size += str(o_obj.file_size) + '&'
            obj.son_files_totalsize += o_obj.file_size
        O_SQL_DATA = (
        obj.file_name, obj.file_dir, obj.son_files_name[:-1], obj.son_files_md5[:-1], obj.son_files_size[:-1],
        obj.son_files_totalsize, obj.remark1)
        origin_sql_command = (O_SQL_FIELD, O_SQL_DATA)
        self.current_totalsize()
        
        # 查看当前生成PDF 文件的大小
        current_pdf_size = round(obj.son_files_totalsize/1024, 4)
        return (origin_sql_command, current_pdf_size)

    def composite_files(self, current_dir):
        if not isinstance(self.path2, str):
            path2 = self.path2.get()
            print(path2)
            if self.path2.get() == '':
                self.path2 = FTP_Server_Dir
            else:
                self.path2 = path2
        
        
        parent, _, filenames, fail_tar_path, fail_copy_path = current_dir
        name_str = parent.split('/')[-1].split('\\')[-1]
    
        file_name_all = []
        file_name_pdf = []
        file_name_zip = []
       

        # 格式错误的文件
        format_error_files = ''
        for filename in filenames:
            oldfilepath = os.path.join(parent + '/' + filename)
            if self.path3.get() != '' or fail_copy_path is not None:
                file_name_all.append(oldfilepath)
            if filename[-3:] == 'jpg':
                # 判断文件是否能打开，不能打开则不处理整个文件夹，且记录一下
                if imghdr.what(oldfilepath) == 'jpeg':
                    file_name_pdf.append(oldfilepath)
                else:
                    # 记录打不开的文件名
                    format_error_files += filename + '&'
            elif filename[-3:] == 'tif':
                if imghdr.what(oldfilepath) == 'tiff':
                    file_name_pdf.append(oldfilepath)
                else:
                    # 记录打不开的文件名
                    format_error_files += filename + '&'
            else:
                file_name_zip.append(oldfilepath)

        if format_error_files != '':
            file_name_pdf = []
            file_name_zip = []
            file_name_all = []
            f_obj = MySQLFile(parent, drive_name, self.path2)
            if self.path3.get() != '':
                f_obj.copy_name = os.path.join(u'' + self.path3.get() + '/' + parent[3:])
            if fail_tar_path:
                f_obj.target_name = fail_tar_path
            if fail_copy_path:
                f_obj.copy_name = fail_copy_path
            f_obj.file_type = 'pdf'
            f_obj.file_name = name_str + '.pdf'
            f_obj.remark1 = 'error: {} '.format(str(format_error_files))
            if self.query_sql_exist(f_obj) == 'None':
                self.insert_function_sql(f_obj)
                self.py_windows.insert_fail_file(f_obj)
                self.fail_file_obj.append(f_obj)
                
        # 复制所有文件到指定路径
        if file_name_all != []:
            af_obj = MySQLFile(parent, drive_name, self.path3.get())
            af_obj.file_name = name_str
            sql_dir = af_obj.file_dir
            if fail_copy_path:
                af_obj.copy_name = fail_copy_path
            else:
                af_obj.copy_name = af_obj.target_name
            
            if not self.exist_all_file(sql_dir):
                # 拷贝并记录的所有的源文件
                all_origin_sql, _ = self.recode_origin_files(af_obj, parent, file_name_all)
                # postgreSQL 函数名：origin_insert_function ， 表名： TABLE_ALL_ORIGIN
                FUNC_SQL = "SELECT origin_insert_function('{}','{}','''{}''','''{}''','''{}''','''{}''','''{}''',{}, '''{}''')".format(
                    TABLE_ALL_ORIGIN, all_origin_sql[0], all_origin_sql[1][0], all_origin_sql[1][1],
                    all_origin_sql[1][2], all_origin_sql[1][3], all_origin_sql[1][4], all_origin_sql[1][5], all_origin_sql[1][6])
                cur = self.conn.cursor()
                cur.execute(FUNC_SQL)
                self.conn.commit()
                cur.close()
                            
        # 生成PDF 文件
        if file_name_pdf != []:
            # 初始化PDF 文件对象
            f_obj = MySQLFile(parent, drive_name, self.path2)
            if fail_tar_path:
                f_obj.target_name = fail_tar_path
            f_obj.file_type = 'pdf'
            f_obj.file_name = name_str + '.pdf'
            if self.path3.get() != '':
                f_obj.copy_name = os.path.join(u'' + self.path3.get() + '/' + parent[3:])
            elif fail_copy_path:
                f_obj.copy_name = fail_copy_path
            exist_flag = self.query_sql_exist(f_obj).lower()
            
            if exist_flag != 'true':
                # 记录源文件的名字，大小，md5 的Postgresql 函数参数（field， values）
                o_sql_param, pdf_file_size = self.recode_origin_files(f_obj, parent, file_name_pdf)
                f_obj.start_time = time.time()
                try:
                    # 开始将jpg 和 tif 转换成pdf
                    self.generate_pdffile(f_obj, file_name_pdf)
                    # 开始为PDF 文件添加书签
                    self.pdf_add_bookmark(f_obj, file_name_pdf)
                    # 移动文件
                    move_pdf_begin_time = time.time()
                    self.shutil_move(f_obj)
                    move_pdf_end_time = time.time()
                    move_pdf_use_time = move_pdf_end_time - move_pdf_begin_time
                    move_pdf_speed = pdf_file_size / move_pdf_use_time
                    print('移动文件：{}， 耗时：{} 秒'.format(f_obj.file_name, round(move_pdf_use_time, 2)))
                    print('移动文件：{}， 速度：{} M/s'.format(f_obj.file_name, round(move_pdf_speed, 2)))       
                except Exception:
                    f_obj.remark1 = '文件：{} 生成或移动失败'.format(f_obj.file_name)
                    o_sql_param = None
                    self.py_windows.insert_fail_file(f_obj)
                    self.fail_file_obj.append(f_obj)
                finally:
                    f_obj.complete_time = time.time()
                    if exist_flag == 'none':
                        self.insert_function_sql(f_obj, o_sql_param)
                    elif exist_flag == 'false':
                        self.update_function_sql(f_obj, o_sql_param)
               

        # 生成ZIP 文件
        if file_name_zip != []:
            # 初始化ZIP 文件对象
            f_obj = MySQLFile(parent, drive_name, self.path2)
            if fail_tar_path:
                f_obj.target_name = fail_tar_path
            f_obj.file_type = 'zip'
            f_obj.file_name = name_str + '.zip'
            if self.path3.get() != '':
                f_obj.copy_name = os.path.join(u'' + self.path3.get() + '/' + parent[3:])
            elif fail_copy_path:
                f_obj.copy_name = fail_copy_path
            exist_flag = self.query_sql_exist(f_obj).lower()
            if exist_flag != 'true':
                # 生成ZIP 文件
                f_obj.start_time = time.time()
                try:
                    # 生成ZIP 文件
                    self.generate_zipfile(f_obj, file_name_zip)
                    # 移动文件
                    self.shutil_move(f_obj)
                except:
                    f_obj.remark1 = '文件：{} 生成或移动失败'.format(f_obj.file_name)
                    self.py_windows.insert_fail_file(f_obj)
                    self.fail_file_obj.append(f_obj)
                finally:
                    f_obj.complete_time = time.time()
                    if exist_flag == 'none':
                        self.insert_function_sql(f_obj)
                    elif exist_flag == 'false':
                        self.update_function_sql(f_obj)
            

    def exist_all_file(self, sql_dir):
        cur = self.conn.cursor()
        SQL = 'select file_dir from {};'.format(TABLE_ALL_ORIGIN)
        cur.execute(SQL)
        result = cur.fetchall()
        cur.close()

        if result and (sql_dir,) in result:
            return True

    def generate_pdffile(self, obj, pdf_names):
        with open(obj.file_name, 'wb') as f:
            f.write(img2pdf.convert(pdf_names))

    def pdf_add_bookmark(self, obj, pdf_names):
        reader_obj = pdfreader(obj.file_name)
        pdf_writer = pdfwriter()
        pdf_writer.cloneDocumentFromReader(reader_obj)
        for i, v in enumerate(pdf_names):
            pdf_writer.addBookmark(u'' + v.split('\\')[-1], i)
        with open(obj.file_name, 'wb') as font:
            pdf_writer.write(font)

    def generate_zipfile(self, obj, zip_names, generate_type='move'):
        if generate_type == 'copy':
            origin_name = obj.file_name + '.zip'
        else:
            origin_name = obj.file_name
        z = zipfile.ZipFile(origin_name, 'w', zipfile.ZIP_DEFLATED)
        for zip_file in zip_names:
            z.write(zip_file)
        z.close()

    def shutil_move(self, obj, shutil_type='move'):
        ftp_folder_name = FTP_Server_Dir
        folder_name = ''
        if use_ftp_server == 'true':    
            _, ftpdirs, _ = next(os.walk(ftp_folder_name))
            y_m_d = datetime.datetime.now()
            base_ftp_son_name = str(y_m_d).split(' ')[0]

            if len(ftpdirs) == 0:
                folder_name = base_ftp_son_name + '-' + ('%09d' % 1)
            else:
                folder_name = get_ftpserver_last_name(ftp_folder_name, ftd_folder_list)
                ftp_dir = os.path.join(ftp_folder_name, folder_name)
                current_folder_size = getdirsize((ftp_dir))
                if current_folder_size > FTP_FOLDER_MAX_SIZE:
                    folder_name = folder_name[:-9] + '%09d' % (int(folder_name[-9:])+1)
            
            if folder_name not in ftd_folder_list:
                ftd_folder_list.append(folder_name)

            while len(ftd_folder_list) > FTP_FOLDER_MAX_COUNT:
                # 如果FTP 目录中已经生成了设置的文件夹数，则阻塞5 秒不继续生成
                self.init_ftp_list()
                time.sleep(5)
    
        if shutil_type == 'copy':
            dspath = os.path.join(obj.copy_name + '/' + obj.file_name + '.zip')
            origin_name = obj.file_name + '.zip'
        else:
            if self.path2 == FTP_Server_Dir and use_ftp_server == 'true':
                dspath = os.path.join(obj.target_name + '.' + obj.file_type)
                dspath = os.path.join(ftp_folder_name+'/{}/'.format(folder_name)+dspath[len(ftp_folder_name):])
            else:
                dspath = os.path.join(obj.target_name + '/' + obj.file_name)
            origin_name = obj.file_name

        
     
        # 是否存在要移动的目录，如果不存在，就创建
        fpath, _ = os.path.split(dspath)
        if not os.path.exists(fpath):
            try:
                os.makedirs(fpath)
            except FileExistsError:
                pass
        # 移动
        shutil.move(os.getcwd() + '/' + origin_name, dspath)
        obj.remark2 = folder_name
        # 标记完成
        obj.complete_type = True

    def threading_begin(self):
        # 检查是否有起始路径，没有则报错
        if self.path1.get() != '':
            self.t1.start()
        else:
            msg = '请输入起始路径'
            self.py_windows.alert_warm_msg(msg)
            
    def threading_stop(self):
        pass
       
    def start(self):
        if use_threadingpool == 'true':
            # 查看CPU核心数，动态开启线程池
            thread_pool_count = get_threadpool_count()
            thread_pool = ThreadPoolManger(thread_pool_count)
            self.generate_allfiles(thread_pool)
        else:
            self.generate_allfiles()
        # 显示失败的文件列表
        self.query_fail_files()
        msg = '文件已经生成完成'
        self.py_windows.alert_warm_msg(msg)


    # 单独生成失败的文件
    def handle_fail_file(self):
        # 如果生成文件的线程没有运行
        if not self.t1.is_alive():
            self.current_chose_file = self.py_windows.get_current_chose()
            for fail_obj in self.fail_file_obj:
                if fail_obj.file_name == self.current_chose_file:
                    chose_path = fail_obj.file_dir
                    fail_tar_path = fail_obj.target_name
                    fail_copy_path = fail_obj.copy_name
                    fail_path_dirs = []
                    fail_path_files = []
                    # 拼接要处理的文件的数据（parent， dirs， files, fail_tar_path, fail_copy_path）
                    files = os.listdir(chose_path)
                    for fi in files:
                        fi_dir = os.path.join(chose_path, fi)
                        if os.path.isdir(fi_dir):
                            fail_path_dirs.append(fi)
                        else:
                            fail_path_files.append(fi)
                    fail_list_dir = (chose_path, fail_path_dirs, fail_path_files, fail_tar_path, fail_copy_path)
                    self.composite_files(fail_list_dir)
                    if self.py_windows:
                        if self.t1.is_alive():
                            self.threading_stop()
                        self.py_windows.destroy()
                        self.py_windows = MyPDFTk(self.threading_begin, self.query_fail_reson, self.handle_fail_file, self.threading_stop)
                        self.chose_fail = self.py_windows.chose_fail
                        self.show_error = self.py_windows.show_error
                        self.path3 = self.py_windows.path3
                        # 查询数据库中失败的文件，并展示
                        self.query_fail_files()
                        self.py_windows.run()

    def query_fail_files(self):
        cur = self.conn.cursor()
        SQL = 'select id, file_name, file_dir, file_type, copy_name, target_name, remark1 FROM {} WHERE complete_type=False;'.format(
            TABLE_PDF_ZIP)
        cur.execute(SQL)
        self.fail_file_obj = []
        fail_count = cur.fetchall()
        cur.close()
        if fail_count:
            # 查询失败文件的对象
            for sql_fail_file in fail_count:
                ff_path = self.path2 if isinstance(self.path2, str) else self.path2.get()
                ff_obj = MySQLFile('fail', drive_name, ff_path)
                ff_obj.file_name = sql_fail_file[1]
                ff_obj.file_dir = sql_fail_file[2]
                ff_obj.file_type = sql_fail_file[3]
                ff_obj.copy_name = sql_fail_file[4]
                ff_obj.target_name = sql_fail_file[5]
                ff_obj.remark1 = sql_fail_file[6]
                self.fail_file_obj.append(ff_obj)

        # 设置显示失败的内容
        fail_data = tuple()
        if self.fail_file_obj != []:
            for ff1_obj in self.fail_file_obj:
                fail_data += (ff1_obj.file_name,)
        
        self.chose_fail.set(fail_data)
        print('fail_file:{}'.format(fail_data))

    def query_fail_reson(self):
        self.current_chose_file = self.py_windows.get_current_chose()
        for obj in self.fail_file_obj:
            if obj.file_name == self.current_chose_file:
                try:
                    os.startfile(obj.file_dir)
                except FileNotFoundError:
                    error_info = '文件路径不对'
                    self.py_windows.alert_warm_msg(error_info)
                self.show_error.set(obj.remark1)

    # 查询该条数据是否已经成功插入或者是插入失败
    def query_sql_exist(self, obj):
        cur = self.conn.cursor()
        SQL = "SELECT query_obj_exist('{}','{}','''{}''','''{}''')".format(TABLE_PDF_ZIP, 'complete_type', obj.file_dir, obj.file_type)
        cur.execute(SQL)
        sql_result = cur.fetchall()
        cur.close()
        if sql_result:
            print('文件：{} 的状态是：{}'.format(obj.file_name, str(sql_result[0][0])))
            return str(sql_result[0][0])
        

    # 更新失败的任务
    def update_function_sql(self, obj, origin_sql=None):
        cur = self.conn.cursor()
        SQL = '{file_name, file_dir, file_type, target_username, copy_name, target_name, start_time, complete_time, complete_type, remark1, remark2}'
        SQL_DATA = (
            obj.file_name, obj.file_dir, obj.file_type, obj.target_username, obj.copy_name, obj.target_name,
            obj.start_time, obj.complete_time, obj.complete_type, obj.remark1, obj.remark2)
        FUNC_SQL = "SELECT pdf_update_function('{}', '{}', '''{}''','''{}''','''{}''','''{}''','''{}''','''{}''',{},{},{},'''{}''', '''{}''')".format(
            TABLE_PDF_ZIP, SQL, SQL_DATA[0], SQL_DATA[1], SQL_DATA[2], SQL_DATA[3], SQL_DATA[4], SQL_DATA[5],
            SQL_DATA[6], SQL_DATA[7], SQL_DATA[8], SQL_DATA[9], SQL_DATA[10])
        if origin_sql != None:
            FUNC_SQL = FUNC_SQL[:-1] + ",'{}','{}','''{}''','''{}''','''{}''','''{}''','''{}''',{}, '''{}''')".format(
                TABLE_PDF_ORIGIN, origin_sql[0], origin_sql[1][0], origin_sql[1][1], origin_sql[1][2], origin_sql[1][3],
                origin_sql[1][4], origin_sql[1][5], origin_sql[1][6])
        cur.execute(FUNC_SQL)
        self.conn.commit()
        cur.close()
       

    # 正常插入数据库
    def insert_function_sql(self, obj, origin_sql=None):
        cur = self.conn.cursor()
        SQL = '{file_name, file_dir, file_type, target_username, copy_name, target_name, start_time, complete_time, complete_type, remark1, remark2}'
        SQL_DATA = (
            obj.file_name, obj.file_dir, obj.file_type, obj.target_username, obj.copy_name, obj.target_name,
            obj.start_time, obj.complete_time, obj.complete_type, obj.remark1, obj.remark2)
        FUNC_SQL = "SELECT pdf_insert_function('{}', '{}', '''{}''','''{}''','''{}''','''{}''','''{}''','''{}''',{},{},{},'''{}''', '''{}''')".format(
            TABLE_PDF_ZIP, SQL, SQL_DATA[0], SQL_DATA[1], SQL_DATA[2], SQL_DATA[3], SQL_DATA[4], SQL_DATA[5],
            SQL_DATA[6], SQL_DATA[7], SQL_DATA[8], SQL_DATA[9], SQL_DATA[10])
        if origin_sql != None:
            FUNC_SQL = FUNC_SQL[:-1] + ",'{}','{}','''{}''','''{}''','''{}''','''{}''','''{}''',{}, '''{}''')".format(
                TABLE_PDF_ORIGIN, origin_sql[0], origin_sql[1][0], origin_sql[1][1], origin_sql[1][2], origin_sql[1][3],
                origin_sql[1][4], origin_sql[1][5], origin_sql[1][6])
        cur.execute(FUNC_SQL)
        self.conn.commit()
        cur.close()
        

    def init_postgresqk_func(self):
        cur = self.conn.cursor()
        if self.postgre_func_isfirst:
            cur.execute(DROP_INSERT_FUNCTION_SQL)
            cur.execute(DROP_ORIGIN_FUNCTION_SQL)
            cur.execute(DROP_UPDATE_FUNCTION_SQL)
            cur.execute(DROP_EXIST_FUNCTION_SQL)
            self.conn.commit()
            cur.execute(INSERT_SQL_ORIGIN)
            cur.execute(INSERT_SQL_PDF)
            cur.execute(UPDATE_SQL_PDF)
            cur.execute(FILE_OBJ_EXIST)
            self.conn.commit()
            cur.close()
            self.postgre_func_isfirst = False

    def init_db_create(self):
        db_create_conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        db_create_cur = db_create_conn.cursor()
        db_create_cur.execute(DB_NAME_EXIST)
        db_create_conn.commit()  # <-- ADD THIS LINE
        result = db_create_cur.fetchall()
        if result == []:
            db_create_conn.autocommit = True
            db_create_cur.execute(DB_NAME)
            # 这个连接直接关闭了，不需要下面这行代码了
            # db_create_conn.autocommit = False
        else:
            print('{} is exist'.format(DATABASE_NAME))
        db_create_cur.close()
        db_create_conn.close()


    def init_db_table(self):
        cur = self.conn.cursor()
        cur.execute(PDF_SEQ)
        cur.execute(PDF_ZIP_TABLE)
        cur.execute(ORIGIN_SEQ)
        cur.execute(PDF_ORIGIN_FILES)
        cur.execute(ALL_SEQ)
        cur.execute(ALL_ORIGIN_FILES)
        self.conn.commit()
        cur.close()
    


def begin():
    # # 验证功能
    # ctk = CheckTK()
    # if ctk.check:
    #     a = MyPdfZip()
    #     a.run()
    #     a.conn.close()
    # else:
    #     print('close gui')
    # # 无验证
    a = MyPdfZip()
    a.run()
    a.conn.close()


if __name__ == "__main__":
    start_time = time.time()
    begin()
    end_time = time.time()
    print('use time :{}'.format(end_time - start_time))
