from tkinter.filedialog import askdirectory
from tkinter import messagebox, StringVar, Label, Entry,Button, Listbox, Radiobutton, Text, Tk, E, W,BROWSE


"""
self.wm_minsize(1440, 776)                  # 设置窗口最小化大小
self.wm_maxsize(1440, 2800)                 # 设置窗口最大化大小
self.resizable(width=False, height=True)    # 设置窗口宽度不可变，高度可变
"""

# MyTk setting
TITLE = '封包导出'
SIZE = '750x450'


class MyPDFTk(Tk):
    def __init__(self, command1=None, command2=None, command3=None, command4=None):
        super(MyPDFTk, self).__init__()
        # super().__init__()
        self.wm_title(TITLE)
        self.geometry(SIZE)
        self.path1 = StringVar()
        self.path2 = StringVar()
        self.chose_fail = StringVar()
        self.show_error = StringVar()
        self.path3 = StringVar()
        self.choseifcopy = StringVar()
        self.choseifcopy.set('not_copy')
        self.command1 = command1
        self.command2 = command2
        self.command3 = command3
        self.command4 = command4
        

    def chose_folder1(self):
        self._path1 = askdirectory()
        self.path1.set(self._path1)

    def chose_folder2(self):
        self._path2 = askdirectory()
        self.path2.set(self._path2)

    def chose_folder3(self):
        if self.choseifcopy.get() == 'not_copy':
            messagebox.showinfo(title='警告',message='请选择复制')
        elif self.choseifcopy.get() == 'do_copy':
            self._path3 = askdirectory()
            self.path3.set(self._path3)
    def ifcopy(self):
        flag = self.choseifcopy.get()
        if flag == 'not_copy':
            self.path3.set('')
        

    def gui_init(self):
        Label(self, text='起始路径').grid(row=0, column=0)
        Entry(self, textvariable=self.path1).grid(row=0, column=1)
        Button(self, text='路径选择', command=self.chose_folder1).grid(row=0, column=2)
        Label(self, text='复制路径').grid(row=1, column=0)
        Entry(self, textvariable=self.path3).grid(row=1, column=1)
        Button(self, text='路径选择', command=self.chose_folder3).grid(row=1, column=2)
        # Button(self, text='复制', command=self.command1).grid(row=1, column=3)

        r1 = Radiobutton(self, text='复制', variable=self.choseifcopy, value='do_copy')
        r1.grid(row=1, column=3)
        r2 = Radiobutton(self, text='不复制', variable=self.choseifcopy, value='not_copy', command=self.ifcopy)
        r2.grid(row=1, column=4)

        Label(self, text='目标路径').grid(row=2, column=0)
        Entry(self, textvariable=self.path2).grid(row=2, column=1)
        Button(self, text='路径选择', command=self.chose_folder2).grid(row=2, column=2)
        Button(self, text='执行', command=self.command1).grid(row=2, column=3)
        # Button(self, text='停止', command=self.stop_gener).grid(row=3, column=4)
        Button(self, text='清空错误文件列表', command=self.clean_list).grid(row=3, column=2)
        self.lb1 = Listbox(self, selectmode = BROWSE, listvariable=self.chose_fail, width=30, height=10)
        self.lb1.grid(row=3, columnspan=2)
        # Button(self, text='打开文件', command=self.command2).grid(row=3, column=0)
        self.b1 = Button(self, text='重新生成', command=self.command3)
        self.b1.grid(row=4, column=1)
        Button(self, text='打开失败文件位置', command=self.command2).grid(row=5, column=3)
        Label(self, text='失败原因').grid(row=6, column=0)
        Label(self, textvariable=self.show_error, bg='white', fg='blue', font=('Arial', 8), width=60, height=3).grid(row=6,column=1)

    def clean_list(self):
        self.lb1.delete(0, 'end')

    def get_current_chose(self):
        return self.lb1.get(self.lb1.curselection())

    def insert_fail_file(self, fail_obj=None):
        if fail_obj:
            fail_name = fail_obj.file_name
            self.lb1.insert('end', fail_name)
    def stop_gener(self):
        cancel_flag = messagebox.askokcancel(title='警告',message='是否停止生成文件')
        if cancel_flag:
            self.command4()

    def alert_warm_msg(self, msg):
        messagebox.showinfo(title='警告',message=msg)

    def run(self):
        self.gui_init()
        # 进入消息循环
        self.mainloop()



class CheckTK(Tk):
    def __init__(self):
        super(CheckTK, self).__init__()
        # super().__init__()
        self.title('登录验证')
        self.u1 = StringVar()
        self.p1 = StringVar()
        self.check = False
        self.check_gui_init()

    def check_gui_init(self):
        Label(self,text='会员名称:').grid(row=0,column=0)
        Label(self,text='会员代号:').grid(row=1,column=0)
        e1 = Entry(self,textvariable=self.u1)    # Entry 是 Tkinter 用来接收字符串等输入的控件.
        e2 = Entry(self,textvariable=self.p1, show='#')
        e1.grid(row=0,column=1,padx=10,pady=5)  # 设置输入框显示的位置，以及长和宽属性
        e2.grid(row=1,column=1,padx=10,pady=5)
        Button(self,text='验证信息',width=10,command=lambda :self.auth(e1.get(), e2.get())).grid(row=2,column=0,sticky=W,padx=10,pady=5)
        Button(self,text='退出',width=10,command=self.quit).grid(row=2,column=1,sticky=E,padx=10,pady=5)

        self.mainloop()
    def auth(self, username, password):
        if username == 'jsjy' and password == '123456we':
            self.destroy()
            self.check = True
        else:
            messagebox.showinfo(title='警告',message='输入信息错误')
            print('验证失败')

if __name__ == '__main__':

    mtk = MyPDFTk()
    mtk.run()



    
