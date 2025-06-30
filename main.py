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
    # Show error if pyperclip is not installed
    tkinter.messagebox.showerror("Can't found moudle: pyperclip","You can run \"pip install pyperclip\" to solve the problem Error\n\nError: ModuleNotFoundError")
    exit()

# Load settings from settings.json
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'settings.json')
with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
    settings = json.load(f)
lang_code = settings.get('language.use', 'en_us')
lang_file = f"lang_{lang_code}.json"
LANG_PATH = os.path.join(os.path.dirname(__file__), lang_file)
with open(LANG_PATH, 'r', encoding='utf-8') as f:
    LANG = json.load(f)

class main_window:
    def __init__(self) -> None:
        # Create main window
        self.window = tkinter.Tk()
        self.window.title(LANG["app.name"])

        # Load language list and translation settings
        self.language_list = LANG["language.list"]
        self.language_identifiers = settings["translation.translation_tool.language_identifiers"]
        self.translation_url = settings["translation.translation_tool.link"]

        # Clipboard monitor controls
        self.monitor_clipboard_label_frame = tkinter.ttk.LabelFrame(self.window, text=LANG["ui.main_window.monitor_clipboard_label_frame.text"])
        self.start_monitor_clipboard_button = tkinter.ttk.Button(self.monitor_clipboard_label_frame, text=LANG["ui.main_window.start_monitor_clipboard_button.text"], command=self.start_monitor)
        self.start_monitor_clipboard_button.pack(fill="x", side="left")
        self.stop_monitor_clipboard_button = tkinter.ttk.Button(self.monitor_clipboard_label_frame, text=LANG["ui.main_window.stop_monitor_clipboard_button.text"], command=self.stop_monitor, state="disabled")
        self.stop_monitor_clipboard_button.pack(fill="x", side="left")
        self.monitor_clipboard_label_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Language selection variables and controls
        self.language_label_frame = tkinter.ttk.LabelFrame(self.window, text=LANG["ui.main_window.language_label_frame.text"])
        lang_names = list(self.language_list.values())
        lang_keys = list(self.language_list.keys())
        self.from_language_var = tkinter.StringVar(value=lang_names[0])
        self.to_language_var = tkinter.StringVar(value=lang_names[1])
        self.from_language_label = tkinter.ttk.Label(self.language_label_frame, text=LANG["ui.main_window.from_language_label.text"])
        self.from_language_label.pack(side="left", padx=(5, 0), pady=5)
        self.from_language_combo = tkinter.ttk.Combobox(self.language_label_frame, textvariable=self.from_language_var, values=lang_names, state="readonly", width=15)
        self.from_language_combo.pack(side="left", padx=5, pady=5)
        self.to_language_label = tkinter.ttk.Label(self.language_label_frame, text=LANG["ui.main_window.to_language_label.text"])
        self.to_language_label.pack(side="left", padx=5, pady=5)
        self.to_language_combo = tkinter.ttk.Combobox(self.language_label_frame, textvariable=self.to_language_var, values=lang_names, state="readonly", width=15)
        self.to_language_combo.pack(side="left", padx=5, pady=5)
        self.language_label_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Multithreading for clipboard monitoring
        self.monitor_thread = None  # Clipboard monitor thread
        self.monitoring = threading.Event()  # Thread event control
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # Window close event

        self.window.mainloop()

    def start_monitor(self):
        # Start clipboard monitoring thread
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.monitoring.set()
            self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
            self.monitor_thread.start()
            self.start_monitor_clipboard_button.config(state="disabled")
            self.stop_monitor_clipboard_button.config(state="normal")

    def stop_monitor(self):
        # Stop clipboard monitoring thread
        self.monitoring.clear()
        self.start_monitor_clipboard_button.config(state="normal")
        self.stop_monitor_clipboard_button.config(state="disabled")

    def monitor_clipboard(self):
        # Monitor clipboard content and open translation URL if changed
        last_clipboard_content = ""
        lang_keys = list(self.language_list.keys())
        lang_names = list(self.language_list.values())
        while self.monitoring.is_set():
            try:
                current_clipboard_content = pyperclip.paste()
                if current_clipboard_content != last_clipboard_content:
                    # Get selected language keys
                    from_lang_name = self.from_language_var.get()
                    to_lang_name = self.to_language_var.get()
                    from_lang_key = lang_keys[lang_names.index(from_lang_name)]
                    to_lang_key = lang_keys[lang_names.index(to_lang_name)]
                    from_lang = self.language_identifiers.get(from_lang_key, "en")
                    to_lang = self.language_identifiers.get(to_lang_key, "zh_Hans")
                    url = self.translation_url.format(text=current_clipboard_content, from_lang=from_lang, to_lang=to_lang)
                    webbrowser.open_new(url)
                    last_clipboard_content = current_clipboard_content
            except:
                # Show error if clipboard reading fails
                tkinter.messagebox.showerror(LANG["app.name"], "An unknown error occurred while reading the clipboard.")
                break

    def on_close(self):
        # Handle window close event, stop thread and destroy window
        self.monitoring.clear()
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        self.window.destroy()

main_window()