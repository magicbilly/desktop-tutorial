import tkinter as tk
import magic
import os
import subprocess
import tkinter.messagebox
import tkinter.simpledialog
def check_file_type(file_path):
    file_type =magic.from_file(file_path,mime=True)
    if file_type in {"application/zip","application/x-tar","application/x-rar-compressed","application/x-7z-compressed"}:
        return True
    else:
        return False
def extract_7z(file,password_list):
    seven_zip_path = "D:\\360Downloads\\1download\\7-Zip-Zstandard\\7z.exe"
    for password in password_list:
        try:
            command = [seven_zip_path, "x", file, "-y", f"-o{os.path.dirname(file)}", f"-p{password}"]
            subprocess.run(command, check=True)
            return True, password
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
                return False,None
    return False,None
def get_password_list(path):
    path = path.strip('"')
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def main(path,password_file="D:\\360Downloads\\1download\\gal\\password.txt"):
    path = path.strip('"')
    if not os.path.exists(path):
        tishi("文件不存在！")
        return

    if not check_file_type(path):
        tishi("文件类型不支持！(目前仅支持zip、tar、rar、7z)(可以添加大概)")
        return

    password_list = get_password_list(password_file)
    a,password = extract_7z(path,password_list)
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
root = tk.Tk()
root.title("密码破解器")
root.geometry("300x300")
path_label = tk.Label(root,text="文件路径：")
path_label.pack(pady=10)
path_entry = tk.Entry(root)
path_entry.pack(pady=10)
password_label = tk.Label(root,text="密码文件路径：")
password_label.pack(pady=10)
password_entry = tk.Entry(root)
password_entry.pack(pady=10)
def select_path():
    if password_entry.get():
        main(path_entry.get(),password_entry.get())
    else:
        main(path_entry.get())
start_button = tk.Button(root,text="开始",command=select_path)
start_button.pack(pady=10)
root.mainloop()