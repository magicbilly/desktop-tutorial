import json
import os
import time
import requests
from PIL import Image
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import tkinter as tk
from tkinter import messagebox
import threading


# 配置 Selenium 浏览器
def configure_selenium():
    """配置并返回一个已初始化的无头浏览器实例"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
    chrome_options.set_capability("goog:loggingPrefs", capabilities['goog:loggingPrefs'])
    driver = webdriver.Chrome(options=chrome_options)
    return driver


# 下载图片并验证其有效性
def download_image(url, filename):
    for _ in range(3):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(response.content)

            # 验证图像
            with Image.open(filename) as img:
                img.verify()
            return

        except (Image.UnidentifiedImageError, ValueError):
            print("文件可能是视频格式，无法识别。")
            break
        except (IOError, SyntaxError):
            print("图片损坏")
            if os.path.exists(filename):
                os.remove(filename)
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"请求出现异常：{e}")
            time.sleep(2)


# 获取浏览器的性能日志
def get_performance_logs(driver, url):
    """获取浏览器的性能日志"""
    driver.get(url)
    time.sleep(5)  # 等待页面加载
    return driver.get_log('performance')


def create_save_dir(furl):
    """根据 URL 创建保存文件的目录"""
    parsed_url = urlparse(furl)

    # 提取主域名部分
    domain_parts = parsed_url.netloc.split('.')
    if len(domain_parts) > 2:
        domain = domain_parts[-2]  # 处理多级域名，如 www.example.com
    else:
        domain = parsed_url.netloc  # 处理二级域名，如 madosoft.net

    # 获取路径中的最后一个目录部分
    path_segments = parsed_url.path.strip('/').split('/')
    if len(path_segments) > 1:
        last_path_segment = path_segments[-2]  # 获取倒数第二个部分作为文件夹名称
    else:
        last_path_segment = domain  # 如果路径为空或只有根路径，使用主域名作为文件夹名称

    # 构造保存目录路径
    save_dir = os.path.join(os.getcwd(),'pictures', domain, last_path_segment)

    # 创建目录
    os.makedirs(save_dir, exist_ok=True)

    return save_dir


# 爬取页面中的资源并下载
def crawl_resources(driver, furl, save_dir):
    """爬取页面中的资源并下载"""
    logs = get_performance_logs(driver, furl)

    if not logs:
        print("没有获取到任何性能日志。")
    else:
        for log in logs:
            log_message = log.get('message')
            if log_message:
                try:
                    message = json.loads(log_message).get('message')
                    if message and message.get('method') == 'Network.requestWillBeSent':
                        url = message['params']['request']['url']
                        print(url)
                        if url.endswith(('jpg', 'png', 'gif', 'ico', 'mp4')):
                            file_path = os.path.join(save_dir, os.path.basename(url))
                            print(f"正在下载文件到：{file_path}")
                            download_image(url, file_path)
                except json.JSONDecodeError:
                    print("日志消息解析错误：", log_message)
                except KeyError as e:
                    print(f"缺少关键字: {e}")


# 主函数，协调各个功能模块
def main(furl):
    """主函数，接收URL并执行爬虫"""
    # 配置 Selenium 浏览器
    driver = configure_selenium()

    # 创建保存目录
    save_dir = create_save_dir(furl)
    print(f"创建的文件夹路径：{save_dir}")

    # 爬取页面中的资源
    crawl_resources(driver, furl, save_dir)

    # 退出浏览器
    driver.quit()


# GUI 部分
def start_crawl():
    """获取用户输入的URL并启动爬取"""
    furl = url_entry.get()  # 获取输入的URL

    if not furl:
        messagebox.showerror("输入错误", "请提供一个有效的URL。")
        return

    # 禁用按钮，避免重复点击
    start_button.config(state=tk.DISABLED, text="正在爬取...")

    try:
        # 在后台线程中启动爬虫
        crawl_thread = threading.Thread(target=run_crawl, args=(furl,))
        crawl_thread.start()
    except Exception as e:
        messagebox.showerror("错误", f"爬取过程中出现错误: {str(e)}")
        start_button.config(state=tk.NORMAL)


def run_crawl(furl):
    """在后台线程中运行爬虫并完成任务后弹出提示"""
    try:
        main(furl)  # 执行爬虫
        messagebox.showinfo("爬取完成", "爬取已完成，文件已下载。")
    except Exception as e:
        messagebox.showerror("错误", f"爬取过程中出现错误: {str(e)}")
    finally:
        start_button.config(state=tk.NORMAL)  # 任务完成后重新启用按钮


# 创建GUI窗口
root = tk.Tk()
root.title("图片简单爬取工具")

# 设置窗口大小
root.geometry("400x150")

# 创建标签
url_label = tk.Label(root, text="请输入要爬取的URL：")
url_label.pack(pady=10)

# 创建输入框
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=10)

# 创建开始按钮
start_button = tk.Button(root, text="开始爬取", command=start_crawl)
start_button.pack(pady=10)

# 运行GUI主循环
root.mainloop()
