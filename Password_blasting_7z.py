import tkinter as tk
import magic
import os
import subprocess
import tkinter.messagebox
from PIL import Image,ImageTk
import tkinter.simpledialog
from tkinter import ttk

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

def get_gal_password_list(path):
    try:
        password_index_file ="D:\\360Downloads\\1download\\gal\\password.txt"
        password_list = get_password_list(password_index_file)
        try:
            a,password = extract_7z(path, password_list)
            return a,password
        except Exception:
            return False,None
    except FileNotFoundError:
        return False,None
def get_password_list_from_file(path,password_file):
    files = os.listdir(password_file)
    for file in files:
        temporary_path=os.path.join(password_file,file)
        if not os.path.isdir(temporary_path):
            if os.path.isfile(temporary_path):
                password_list = get_password_list(temporary_path)
                a,password = extract_7z(path,password_list)
                if a:
                    return True,password
                else:
                    continue
    return False,None


def check_file_type(file_path):
    file_type =magic.from_file(file_path,mime=True)
    if file_type in {"application/zip","application/x-tar","application/x-rar-compressed","application/x-7z-compressed"}:
        return True
    else:
        return False
def extract_7z(file,password_list):
    seven_zip_path = "7-Zip-Zstandard\\7z.exe"
    for password in password_list:
        try:
            command = [seven_zip_path, "x", file, "-y", f"-o{os.path.dirname(file)}", f"-p{password}"]
            subprocess.run(command, check=True)
            return True, password
        except subprocess.CalledProcessError:
            continue
        except Exception as e:
            try:
                command = ["7z", "x", file, "-y", f"-o{os.path.dirname(file)}"]
                subprocess.run(command, check=True)
                return True, None
            except RuntimeError:
                pass
            except subprocess.CalledProcessError:
                continue
            except OSError as o:
                tishi(f"7z.exe路径错误！或是找不到7z.exe！请检查环境变量！{o}")
                exit()
        else:
            return False,None
def get_password_list(path):
    path = path.strip('"')
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def main(path,password_file="Blasting_dictionary-master"):
    path = path.strip('"')
    if not os.path.exists(path):
        tishi("文件不存在！")
        return
    if not check_file_type(path):
        tishi("文件类型不支持！(目前仅支持zip、tar、rar、7z)(可以添加大概)")
        return

    a,password = get_gal_password_list(path)
    if a:
        pass
    else:
        a,password = get_password_list_from_file(path,password_file)
    if a:
        tishi(f"密码找到！密码为：{password}")
    else:
        while True:
            if xunwen("所有密码均尝试失败，是否重试？"):
                password = get_key("请输入密码：")
                if extract_7z(path,[password]):
                    tishi("密码正确！")
                    break
                else:
                    tishi("密码错误！")
            else:
                tishi("退出程序")
                break
def tishi(text):
    tk.messagebox.showinfo("提示",text)
def xunwen(text):
    return tk.messagebox.askyesno("询问",text)
def get_key(text):
    return tk.simpledialog.askstring("输入",text)
def resize_image(event):
    global bg_image
    # 根据窗口当前大小调整图片尺寸
    resized_image = photo.resize((event.width, event.height))
    bg_image = ImageTk.PhotoImage(resized_image)
    bg_label.config(image=bg_image)  # 更新背景图片
photo = Image.open("4549B6C1E9876362174435B2630555D1.jpg")
root = tk.Tk()
root.title("密码破解器")
root.geometry("500x300")
bg_image = ImageTk.PhotoImage(photo.resize((600, 400)))  # 初始大小
bg_label = tk.Label(root, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # 背景覆盖整个窗口

# 绑定窗口大小改变事件
root.bind("<Configure>", resize_image)
# 输入框
path_label = tk.Label(root,text="文件路径：",bg="lightblue",fg="black")
path_label.place(x=100,y=80)
path_entry = tk.Entry(root)
path_entry.place(x=170,y=80)
password_label = tk.Label(root,text="密码目录：",highlightthickness=0,bg="lightblue",fg="black")
password_label.place(x=100,y=150)
label = tk.Label(root,text="（密码目录留空则使用默认密码文件）（只能输人目录）",bg="lightblue",fg="black")
label.place(x=110,y=180)
password_entry = tk.Entry(root)
password_entry.place(x=170,y=150)
def select_path():
    if password_entry.get():
        main(path_entry.get(),password_entry.get().strip('"'))
    else:
        main(path_entry.get())
start_button = ttk.Button(root,text="开始",command=select_path)
start_button.place(x=200,y=210)
root.mainloop()