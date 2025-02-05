import tkinter as tk
from Cocoa import NSPasteboard
import threading
import time
import re
import pyperclip

class ClipboardMonitorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("剪贴板磁链监控")
        self.root.geometry("400x300")  # 缩小窗口大小
        self.root.config(bg="#f8f8f8")  # 背景颜色

        # 创建主框架
        self.main_frame = tk.Frame(self.root, bg="#f8f8f8")
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 显示磁力链接的文本框
        self.text_widget = tk.Text(self.main_frame, height=10, width=40, wrap=tk.WORD, font=("Arial", 12), bd=2, relief="sunken")
        self.text_widget.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # 添加滚动条
        self.scrollbar = tk.Scrollbar(self.text_widget)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_widget.yview)

        # 存储记录的磁力链接
        self.magnet_links = set()

        # 创建按钮框架
        self.button_frame = tk.Frame(self.main_frame, bg="#f8f8f8")
        self.button_frame.pack(fill=tk.X, pady=10)

        # 添加清空页面按钮
        self.clear_button = tk.Button(self.button_frame, text="清空页面", command=self.clear_page, font=("Arial", 12), width=15, height=2, bg="#4CAF50", fg="blue", relief="flat", padx=10, pady=5)
        self.clear_button.pack(side=tk.LEFT, padx=35)

        # 添加一键复制按钮
        self.copy_button = tk.Button(self.button_frame, text="复制所有磁链", command=self.copy_all_links, font=("Arial", 12), width=15, height=2, bg="#2196F3", fg="green", relief="flat", padx=10, pady=5)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        # 启动剪贴板监控线程
        self.running = True
        self.clipboard_thread = threading.Thread(target=self.monitor_clipboard)
        self.clipboard_thread.daemon = True  # 设置为守护线程，随主程序结束而结束
        self.clipboard_thread.start()

        # 启动GUI
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def monitor_clipboard(self):
        last_clipboard = None  # 初始化last_clipboard为None
        while self.running:
            current_clipboard = self.get_clipboard_content()
            if current_clipboard != last_clipboard:  # 只有剪贴板内容变化时才处理
                last_clipboard = current_clipboard
                if self.is_magnet_link(current_clipboard):
                    # 只有当链接不在集合中时，才添加到UI和集合
                    if current_clipboard not in self.magnet_links:
                        self.magnet_links.add(current_clipboard)
                        self.update_ui(f"{current_clipboard}")
                        print(f"检测到你复制了一条磁力链接，内容为：{current_clipboard}")  # 输出到终端
            time.sleep(1)  # 每秒检查一次剪贴板

    def get_clipboard_content(self):
        pasteboard = NSPasteboard.generalPasteboard()  # 获取系统剪贴板
        content = pasteboard.stringForType_(pasteboard.types()[0])  # 获取剪贴板中的文本
        return content if content else ""

    def is_magnet_link(self, link):
        # 简单判断是否为磁力链接
        magnet_regex = re.compile(r"magnet:\?xt=urn:btih:[a-fA-F0-9]{40}")
        return bool(magnet_regex.match(link))

    def update_ui(self, content):
        # 使用tkinter的after方法确保更新UI在主线程中执行
        self.root.after(0, self._update_ui, content)

    def _update_ui(self, content):
        # 在UI中更新磁力链接内容
        self.text_widget.insert(tk.END, content + "\n")
        self.text_widget.yview(tk.END)  # 自动滚动到文本框底部

    def clear_page(self):
        # 清空当前页面的所有磁力链接
        self.text_widget.delete(1.0, tk.END)
        self.magnet_links.clear()

    def copy_all_links(self):
        # 一键复制所有记录下来的磁力链接
        all_links = "\n".join(self.magnet_links)
        pyperclip.copy(all_links)  # 使用pyperclip复制到剪贴板
        print("所有磁力链接已复制到剪贴板。")  # 输出到终端

    def on_close(self):
        # 关闭时停止线程
        self.running = False
        self.root.quit()

if __name__ == "__main__":
    app = ClipboardMonitorApp()
