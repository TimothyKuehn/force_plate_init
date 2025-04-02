import os
import sys
import threading
import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# --- Resource path handling for PyInstaller ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- HTTP logic in background thread ---
def send_request():
    host = "192.168.4.1:8080"  # Updated to include port 8080
    endpoint = "/config"

    data = {
        "SSID": SSID.get(),
        "password": password.get(),
        "hash": hash.get(),
    }

    url = f"http://{host}{endpoint}"

    try:
        response = requests.post(url, json=data, timeout=5)
        result = f"Response: {response.status_code} - {response.text}"
    except Exception as e:
        result = f"Error: {e}"

    result_label.after(0, lambda: result_label.config(text=result))

def send_request_threaded():
    threading.Thread(target=send_request, daemon=True).start()

def change_theme(event):
    theme_map = {"Light Mode": "flatly", "Dark Mode": "darkly"}  # Map user-friendly names to theme names
    selected_theme = theme_map.get(theme_selector.get(), "flatly")  # Default to "flatly" if not found
    try:
        root.style.theme_use(selected_theme)  # Apply the selected theme
    except Exception as e:
        print(f"Error changing theme: {e}")

# --- UI Setup ---
root = ttk.Window(themename="flatly")
root.title("Force Plate Pioneer WiFi Initializer")
root.geometry("1200x600")
root.resizable(True, True)

# Load icon from same folder as .exe or script
def exe_folder_path(filename):
    if getattr(sys, 'frozen', False):
        # Running as bundled .exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Running from .py script
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

icon_path = exe_folder_path("icon.ico")
root.iconbitmap(icon_path)


# --- Layout ---
frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=3)

def add_entry(label_text, default="", row=0):
    ttk.Label(frame, text=label_text).grid(column=0, row=row, sticky="w", pady=5)
    entry = ttk.Entry(frame, width=60)
    entry.insert(0, default)
    entry.grid(column=1, row=row, pady=5, padx=10, sticky="ew")
    return entry

SSID = add_entry("SSID:", "", 0)
password = add_entry("Password:", "", 1)
hash = add_entry("Hash:", "", 2)

ttk.Button(
    frame,
    text="Send HTTP Request",
    bootstyle="primary",
    command=send_request_threaded
).grid(column=0, row=3, columnspan=2, pady=15, sticky="ew")

result_label = ttk.Label(
    frame,
    text="",
    wraplength=750,
    justify="left",
    bootstyle="info"
)
result_label.grid(column=0, row=4, columnspan=2, pady=10, sticky="nsew")
frame.rowconfigure(4, weight=1)

# Add theme selector dropdown
theme_selector = ttk.Combobox(
    frame,
    values=["Light Mode", "Dark Mode"],  # User-friendly names
    state="readonly",
    width=10
)
theme_selector.set("Light Mode")  # Default to Light Mode
theme_selector.grid(column=0, row=5, columnspan=1, pady=10, padx=5, sticky="w")

theme_selector.bind("<<ComboboxSelected>>", change_theme)

root.mainloop()
