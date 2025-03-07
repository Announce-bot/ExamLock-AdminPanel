import os
import sys
import time
import logging
import tkinter as tk
from tkinter import simpledialog, messagebox
import webbrowser
import threading
import ctypes
import winsound
import psutil
from pynput import keyboard

# Configuration
EXAM_URL = "https://lms.lau.edu.gy"  # Allowed exam site
LOG_FILE = "exam_log.txt"
LOCKED = True
ADMIN_PASSWORD = "admin123"
EXIT_SEQUENCE = ["end", "end", "end"]
exit_attempts = []

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# Function to log events
def log_event(event):
    logging.info(event)

# Function to prevent task switching
def restrict_task_manager():
    while LOCKED:
        for process in psutil.process_iter():
            try:
                if process.name() in ["taskmgr.exe", "cmd.exe", "powershell.exe", "explorer.exe"]:
                    process.kill()
                    log_event(f"Unauthorized process terminated: {process.name()}")
            except:
                pass
        time.sleep(2)

# Function to restrict key presses
def on_key_press(key):
    global exit_attempts
    try:
        key_name = key.char.lower()
    except AttributeError:
        key_name = key.name.lower()

    restricted_keys = {"alt", "ctrl", "cmd", "esc", "tab"}
    if key_name in restricted_keys:
        log_event(f"Unauthorized key detected: {key_name}")
        trigger_violation()

    # Secret exit sequence check
    exit_attempts.append(key_name)
    if exit_attempts[-3:] == EXIT_SEQUENCE:
        request_admin_exit()

# Function to display violation screen
def trigger_violation():
    global LOCKED
    LOCKED = True

    # Play alert sound
    for _ in range(5):
        winsound.Beep(800, 500)

    # Lock screen GUI
    root = tk.Tk()
    root.title("SECURITY VIOLATION")
    root.geometry("600x400")
    root.configure(bg="red")
    root.resizable(False, False)

    tk.Label(root, text="⚠ SECURITY VIOLATION ⚠", font=("Arial", 20, "bold"), bg="red", fg="white").pack(pady=20)
    tk.Label(root, text="Unauthorized action detected!", font=("Arial", 14, "bold"), bg="red", fg="white").pack()
    tk.Label(root, text="Exam mode is now locked.", font=("Arial", 12), bg="red", fg="white").pack(pady=10)

    # Flashing screen effect
    def flash_screen():
        while LOCKED:
            root.configure(bg="blue")
            time.sleep(0.5)
            root.configure(bg="red")
            time.sleep(0.5)

    threading.Thread(target=flash_screen, daemon=True).start()

    # Unlock with Admin Password
    tk.Label(root, text="Enter Admin Password:", bg="red", fg="white").pack(pady=10)
    password_entry = tk.Entry(root, show="*", width=30)
    password_entry.pack(pady=5)

    # Submit unlock code
    def unlock_exam():
        if password_entry.get() == ADMIN_PASSWORD:
            global LOCKED
            LOCKED = False
            log_event("Admin unlocked exam.")
            root.destroy()
        else:
            messagebox.showerror("Error", "Incorrect Password")

    tk.Button(root, text="Unlock", command=unlock_exam, font=("Arial", 12)).pack(pady=10)

    root.mainloop()

# Function to request Admin Exit
def request_admin_exit():
    global LOCKED
    admin_input = simpledialog.askstring("Admin Exit", "Enter Admin Password:", show="*")
    if admin_input == ADMIN_PASSWORD:
        LOCKED = False
        log_event("Admin exited exam mode")
        sys.exit()
    else:
        messagebox.showerror("Error", "Incorrect Password")

# Function to ensure the exam page is always open
def ensure_exam_page():
    while LOCKED:
        time.sleep(5)
        if "chrome.exe" not in (p.name() for p in psutil.process_iter()):
            webbrowser.open(EXAM_URL)
        elif "firefox.exe" in (p.name() for p in psutil.process_iter()) or "edge.exe" in (p.name() for p in psutil.process_iter()):
            log_event("Unauthorized browser detected! Restarting LMS...")
            os.system("taskkill /IM firefox.exe /F")
            os.system("taskkill /IM edge.exe /F")
            webbrowser.open(EXAM_URL)

# Start exam mode
def start_exam():
    log_event("Exam started")
    webbrowser.open(EXAM_URL)

    threading.Thread(target=restrict_task_manager, daemon=True).start()
    threading.Thread(target=ensure_exam_page, daemon=True).start()

    with keyboard.Listener(on_press=on_key_press) as listener:
        listener.join()

if __name__ == "__main__":
    start_exam()
