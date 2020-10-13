# 1. 选择路径，判断路径是否为目录 
#     是目录->循环遍历，合成pdf   
#     是文件->判断是否是pdf格式，是的话，生成同名文件夹，里面为拆分的图片


from tkinter import Tk, StringVar, Label, Entry, Button
from tkinter.filedialog import askdirectory, askopenfilename
import os



# handle

def compose_file(path):
    
    print(path)
    pass

def split_file(path):
    print(path)
    pass

# GUI 


root_win = Tk()

path1 = StringVar()
path2 = StringVar()

def chose_folder():
    _path1 = askdirectory()
    path1.set(_path1)

def chose_file():
    _path2 = askopenfilename()
    path2.set(_path2)


def handle_file():
    # h = a-b if a>b else a+b
    # file_path = path1.get() if path1.get() != '' and path2.get() ==''
    compose_path = path1.get()
    split_path = path2.get()
    if compose_path != '' and split_path == '':
        compose_file(compose_path)
    elif split_path != '' and compose_path == '':
        split_file(split_path)
    else:
        # warning error path
        print('error path')
        pass

l1 = Label(root_win, text='合成')
l1.grid(row=0, column=0)
e1 = Entry(root_win, textvariable=path1)
e1.grid(row=0, column=1)
b1 = Button(root_win, text='路径选择', command=chose_folder)
b1.grid(row=0, column=2)

l2 = Label(root_win, text='拆分')
l2.grid(row=1, column=0)
e2 = Entry(root_win, textvariable=path2)
e2.grid(row=1, column=1)
b2 = Button(root_win, text='路径选择', command=chose_file)
b2.grid(row=1, column=2)

b3 = Button(root_win, text='执行', command=handle_file)
b3.grid(row=2, column=0)



root_win.mainloop()




