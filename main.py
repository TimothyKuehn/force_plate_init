import os
import sys
import threading
import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import PhotoImage

# --- Resource path handling for PyInstaller ---
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS  # Set by PyInstaller at runtime
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- HTTP logic in background thread ---
def send_request():
    host = entry_host.get().strip()
    endpoint = entry_endpoint.get().strip()
    if not host or not endpoint:
        result_label.after(0, lambda: result_label.config(text="Host and endpoint are required."))
        return

    data = {
        "SSID": SSID.get(),
        "password": password.get(),
        "hash": hash.get(),
    }

    url = f"http://{host}:8080/{endpoint.lstrip('/')}"

    try:
        response = requests.post(url, json=data, timeout=5)
        result = f"Response: {response.status_code} - {response.text}"
    except Exception as e:
        result = f"Error: {e}"

    result_label.after(0, lambda: result_label.config(text=result))

def send_request_threaded():
    threading.Thread(target=send_request, daemon=True).start()

# --- UI Setup ---
root = ttk.Window(themename="flatly")
root.title("WiFi HTTP Request Sender")
root.geometry("800x600")
root.resizable(True, True)



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

entry_host = add_entry("Target Host (IP or hostname):", "192.168.4.1", 0)
entry_endpoint = add_entry("Endpoint (e.g., /config):", "/config", 1)
SSID = add_entry("SSID:", "", 2)
password = add_entry("Password:", "", 3)
hash = add_entry("Hash:", "", 4)

ttk.Button(
    frame,
    text="Send HTTP Request",
    bootstyle="primary",
    command=send_request_threaded
).grid(column=0, row=5, columnspan=2, pady=15, sticky="ew")

result_label = ttk.Label(
    frame,
    text="",
    wraplength=750,
    justify="left",
    bootstyle="info"
)
result_label.grid(column=0, row=6, columnspan=2, pady=10, sticky="nsew")
frame.rowconfigure(6, weight=1)

root.mainloop()
