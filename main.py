import tkinter
import tkinter.ttk
import tkinter.messagebox
import webbrowser
import threading
import json
import os
try:
    import pyperclip
except ModuleNotFoundError:
    tkinter.messagebox.showerror("Can't found moudle: pyperclip","You can run \"pip install pyperclip\" to solve the problem Error\n\nError: ModuleNotFoundError")
    exit()


# 读取设置和多语言文件
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'settings.json')
with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
    settings = json.load(f)
lang_code = settings.get('language.use', 'en_us')
lang_file = f"lang_{lang_code}.json"
LANG_PATH = os.path.join(os.path.dirname(__file__), lang_file)
with open(LANG_PATH, 'r', encoding='utf-8') as f:
    LANG = json.load(f)

APP_NAME = LANG["app.name"]
LANGUAGES_IDENTIFIERS = {
    LANG["language.list"]["zh_cn"]: "zh-Hans",
    LANG["language.list"]["en_us"]: "en"
}


class main_window:
    def __init__(self) -> None:
        # 主窗口
        self.window = tkinter.Tk()
        self.window.title(APP_NAME)

        # 剪贴板监听控件
        self.monitor_clipboard_label_frame = tkinter.ttk.LabelFrame(self.window, text=LANG["ui.main_window.monitor_clipboard_label_frame.text"])
        self.start_monitor_clipboard_button = tkinter.ttk.Button(self.monitor_clipboard_label_frame, text=LANG["ui.main_window.start_monitor_clipboard_button.text"], command=self.start_monitor)
        self.start_monitor_clipboard_button.pack(fill="x", side="left")
        self.stop_monitor_clipboard_button = tkinter.ttk.Button(self.monitor_clipboard_label_frame, text=LANG["ui.main_window.stop_monitor_clipboard_button.text"], command=self.stop_monitor, state="disabled")
        self.stop_monitor_clipboard_button.pack(fill="x", side="left")
        self.monitor_clipboard_label_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 语言选择变量&控件
        self.language_label_frame = tkinter.ttk.LabelFrame(self.window, text=LANG["ui.main_window.language_label_frame.text"])
        self.from_language_var = tkinter.StringVar(value=list(LANGUAGES_IDENTIFIERS.keys())[0])
        self.to_language_var = tkinter.StringVar(value=list(LANGUAGES_IDENTIFIERS.keys())[1])
        self.from_language_label = tkinter.ttk.Label(self.language_label_frame, text=LANG["ui.main_window.from_language_label.text"])
        self.from_language_label.pack(side="left", padx=(5, 0), pady=5)
        self.from_language_combo = tkinter.ttk.Combobox(self.language_label_frame, textvariable=self.from_language_var, values=list(LANGUAGES_IDENTIFIERS.keys()), state="readonly", width=15)
        self.from_language_combo.pack(side="left", padx=5, pady=5)
        self.to_language_label = tkinter.ttk.Label(self.language_label_frame, text=LANG["ui.main_window.to_language_label.text"])
        self.to_language_label.pack(side="left", padx=5, pady=5)
        self.to_language_combo = tkinter.ttk.Combobox(self.language_label_frame, textvariable=self.to_language_var, values=list(LANGUAGES_IDENTIFIERS.keys()), state="readonly", width=15)
        self.to_language_combo.pack(side="left", padx=5, pady=5)
        self.language_label_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 多线程
        self.monitor_thread = None  # 监听线程
        self.monitoring = threading.Event()  # 线程事件控制
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # 关闭事件

        self.window.mainloop()

    def start_monitor(self):
        # 启动剪贴板监听线程
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.monitoring.set()
            self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
            self.monitor_thread.start()
            self.start_monitor_clipboard_button.config(state="disabled")
            self.stop_monitor_clipboard_button.config(state="normal")

    def stop_monitor(self):
        # 停止剪贴板监听
        self.monitoring.clear()
        self.start_monitor_clipboard_button.config(state="normal")
        self.stop_monitor_clipboard_button.config(state="disabled")

    def monitor_clipboard(self):
        # 剪贴板内容变化时自动打开翻译页面
        last_clipboard_content = ""
        while self.monitoring.is_set():
            try:
                current_clipboard_content = pyperclip.paste()
                if current_clipboard_content != last_clipboard_content:
                    from_lang = LANGUAGES_IDENTIFIERS.get(self.from_language_var.get(), "en")
                    to_lang = LANGUAGES_IDENTIFIERS.get(self.to_language_var.get(), "zh-Hans")
                    url = f"https://cn.bing.com/translator?text={current_clipboard_content}&from={from_lang}&to={to_lang}"
                    webbrowser.open_new(url)
                    last_clipboard_content = current_clipboard_content
            except:
                tkinter.messagebox.showerror(APP_NAME, "An unknown error occurred while reading the clipboard.")
                break

    def on_close(self):
        # 关闭窗口时清理线程
        self.monitoring.clear()
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        self.window.destroy()


main_window()