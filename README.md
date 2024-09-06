# Kiroku Keylogger

Kiroku keylogger designed to capture keystrokes, clipboards, screenshots and send them to a remote server at regular intervals. This tool is intended for ethical hacking and educational purposes only. Misuse of this tool for illegal activities is strictly prohibited.

## Payload Features

- **Keystroke Logging**: Captures all keystrokes, including special keys like Enter, Tab, and Backspace, and sends them to a specified server.
- **Clipboard Monitoring**: Continuously monitors clipboard content, detecting changes and sending the updated data to the server.
- **Screenshot Capture**: Takes screenshots at regular intervals and sends them to the server in a base64-encoded format.
- **Modifier Key Tracking**: Tracks the state of Ctrl, Alt, and Shift keys to accurately capture key combinations.
- **Configurable Intervals**: Allows customization of the intervals for sending keystrokes, clipboard data, and screenshots.
- **JSON Payloads**: Packages keystrokes, clipboard data, and screenshots into JSON format for server transmission.
- **Threaded Execution**: Runs keystroke logging, clipboard monitoring, and screenshot capture in separate threads for efficient performance.
- **Automatic Transmission**: Periodically sends captured data to the server without user intervention.
- **Base64 Encoding**: Encodes screenshots in base64 format before transmission to reduce the payload size.
- **Platform Compatibility**: Designed to work seamlessly on multiple platforms with minimal configuration changes.

## Server Features

- **Keystroke Logging**: Receives and logs keystrokes from the payload, saving them to a specified file.
- **Clipboard Data Capture**: Captures clipboard content from the payload and saves it to a specified file. Optionally logs clipboard data based on user preference.
- **Screenshot Handling**: Receives base64-encoded screenshots from the payload, decodes them, and saves them as PNG files in a specified directory.
- **Victim IP Logging**: Logs the IP address of the victim alongside captured data to identify the source.
- **JSON Parsing and Error Handling**: Parses incoming data in JSON format and handles errors like invalid JSON or server issues with detailed logging.
- **Customizable Configuration**: Allows customization of the server port, file paths for saved keystrokes, clipboard data, and screenshot storage directory.
- **Threaded Execution**: Handles incoming POST requests concurrently, ensuring smooth and efficient server performance.
- **Logging**: Provides detailed logging of all activities, including received data, errors, and server operations.
- **Session Persistence**: Automatically reconnects and continues sessions if the server is restarted while the payload is still running, ensuring uninterrupted data capture.

## Installation

- **Clone the repository:**
  ```bash
  git clone https://github.com/Kuraiyume/Kiroku
  ```

- **Install the necessary libraries:**
  ```bash
  pip3 install -r requirements.txt
  ```
_ **On the attacker machine, run the server:**
  ```bash
  ruby server.rb
  ```
  *If ruby is not installed, install it using 'sudo apt install ruby-full ruby'*

- **On the victim device configure the script and run the script:**
  ```bash
  python3 payload.py
  ```

## Disclaimer

This tool is intended for educational and ethical hacking purposes only. Unauthorized use of this tool for illegal activities is strictly prohibited.

## Author

Kuraiyume
