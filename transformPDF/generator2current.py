import img2pdf, psutil
import os, time, shutil, zipfile, imghdr, datetime, threading
from PyPDF2 import PdfFileReader as pdfreader, PdfFileWriter as pdfwriter

from file_obj import MyOriginFile, MySQLFile
from mytkinter import CheckTK, MyPDFTk
from constants import second2human, get_threadpool_count, getdirsize, get_ftpserver_last_name

from settings import drive_name
from settings import use_threadingpool
from settings import FTP_FOLDER_MAX_SIZE, FTP_FOLDER_MAX_COUNT, FTP_Server_Dir, use_ftp_server  

from mythreading_pool import ThreadPoolManger



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
       
        self.t1 = threading.Thread(target=self.start)
        self.t1.setDaemon(True)

        

    def run(self):
        if use_ftp_server == 'true':
            self.init_ftp_list()
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
            
            self.py_windows.insert_fail_file(f_obj)
            self.fail_file_obj.append(f_obj)
                
        # 复制所有文件到指定路径
        if file_name_all != []:
            af_obj = MySQLFile(parent, drive_name, self.path3.get())
            af_obj.file_name = name_str
            if fail_copy_path:
                af_obj.copy_name = fail_copy_path
            else:
                af_obj.copy_name = af_obj.target_name
            try:
                self.generate_zipfile(af_obj, file_name_all, generate_type='copy')
                self.shutil_move(af_obj, shutil_type='copy')
            except Exception:
                af_obj.remark1 = '文件：{} 生成或移动失败'.format(af_obj.file_name)
                self.py_windows.insert_fail_file(af_obj)
                self.fail_file_obj.append(af_obj)
            else:
                af_obj.remark1 = 'ALL2ZIP'
            
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
            
            try:
                # 开始将jpg 和 tif 转换成pdf
                self.generate_pdffile(f_obj, file_name_pdf)
                # 开始为PDF 文件添加书签
                self.pdf_add_bookmark(f_obj, file_name_pdf)
        
                self.shutil_move(f_obj)
                    
            except Exception as e:
                print(e)
                f_obj.remark1 = '文件：{} 生成或移动失败'.format(f_obj.file_name)
                self.py_windows.insert_fail_file(f_obj)
                self.fail_file_obj.append(f_obj)
                
                
               

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
            try:
                # 生成ZIP 文件
                self.generate_zipfile(f_obj, file_name_zip)
                # 移动文件
                self.shutil_move(f_obj)
            except:
                f_obj.remark1 = '文件：{} 生成或移动失败'.format(f_obj.file_name)
                self.py_windows.insert_fail_file(f_obj)
                self.fail_file_obj.append(f_obj)
             
            

  
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

            # 如果FTP 目录中已经生成了设置的文件夹数，则阻塞5 秒不继续生成
            while len(ftd_folder_list) > FTP_FOLDER_MAX_COUNT:
                self.init_ftp_list()
                time.sleep(5)
        
        if shutil_type == 'copy':
            dspath = os.path.join(obj.copy_name + '/' + obj.file_name + '.zip')
            origin_name = obj.file_name + '.zip'
        else:
            # 如果path2 的路径是FTD_Server_Dir 且 选择了使用ftp_server
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
        # 检查是否正在运行，如果正在运行则警告
        if self.t1.is_alive():
            msg = '程序正在运行'
            self.py_windows.alert_warm_msg(msg)
        else:
            # 检查是否有起始路径，没有则警告
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
                        self.py_windows.run()

   
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
    


if __name__ == "__main__":
    start_time = time.time()
    begin()
    end_time = time.time()
    print('use time :{}'.format(end_time - start_time))
