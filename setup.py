# File: setup.py
import os
import subprocess
import re
import time

print("--- RDP Setup Script v7.2 (Branded by ZainShiraz) ---")

# --- CONFIGURATION ---
USERNAME = "user"
PASSWORD = "root"
PIN = "123456" 

# --- Helper Functions ---
def run_command(command, shell=False):
    """A helper function to run shell commands efficiently and reliably."""
    try:
        subprocess.run(
            command,
            check=True,
            shell=shell,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode().strip()
        print(f"\n❌ Command Error: {error_message}")
        exit(1)

def print_branding():
    """Prints the custom ZainShiraz branding in solid red."""
    RED = "\033[91m"
    RESET = "\033[0m"
    art = [
        "███████╗ █████╗ ██╗███╗   ██╗   ███████╗██╗  ██╗██╗██████╗  █████╗ ███████╗",
        "╚══███╔╝██╔══██╗██║████╗  ██║   ██╔════╝██║  ██║██║██╔══██╗██╔══██╗██╔════╝",
        "  ███╔╝ ███████║██║██╔██╗ ██║   ███████╗███████║██║██████╔╝███████║███████╗",
        " ███╔╝  ██╔══██║██║██║╚██╗██║   ╚════██║██╔══██║██║██╔══██╗██╔══██║╚════██║",
        "███████╗██║  ██║██║██║ ╚████║   ███████║██║  ██║██║██║  ██║██║  ██║███████║",
        "╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"
    ]
    print("\n")
    for line in art:
        print(f"{RED}{line}{RESET}")
    print("\n")

def setup_user():
    print("🚀 Configuring user account...")
    if subprocess.run(['id', USERNAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        run_command(['useradd', '-m', '-s', '/bin/bash', USERNAME])
        print(f" M-^User '{USERNAME}' created.")
    else:
        print(f"👍 User '{USERNAME}' already exists.")
    run_command(f"echo '{USERNAME}:{PASSWORD}' | chpasswd", shell=True)
    run_command(['adduser', USERNAME, 'sudo'])
    print(f"✅ User '{USERNAME}' is configured.")

def finalize_setup(auth_code):
    print("🚀 Finalizing CRD setup...")
    run_command(['adduser', USERNAME, 'chrome-remote-desktop'])
    start_command = (
        f"/opt/google/chrome-remote-desktop/start-host "
        f"--code=\"{auth_code}\" "
        f"--redirect-url=https://remotedesktop.google.com/_/oauthredirect "
        f"--name=$(hostname) "
        f"--pin={PIN}"
    )
    print("🔐 Launching CRD host service...")
    run_command(['su', '-', USERNAME, '-c', start_command])
    run_command(['service', 'chrome-remote-desktop', 'start'])
    print("✅ CRD Service Started.")

# --- Main Execution Block ---
if __name__ == "__main__":
    user_input = input("➡️ Enter your Google CRD Authorization Code (or paste the full command): ").strip()
    if not user_input:
        print("\n❌ Error: Input cannot be empty.")
        exit(1)
    auth_code = user_input
    if "start-host" in user_input:
        print("👍 Full command pasted. Extracting authorization code...")
        match = re.search(r'--code="?([^"\s]+)"?', user_input)
        if match:
            auth_code = match.group(1)
            print(f"✅ Code extracted successfully: {auth_code[:15]}...")
        else:
            print("\n❌ Error: Could not find a valid code in the command.")
            exit(1)
    print("\n⚡ Starting Fast Installation...")
    print(" M-^Updating package lists...")
    run_command(['apt-get', 'update'])
    print(" M-^Downloading CRD and Chrome...")
    run_command(['wget', 'https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb', '-O', 'crd.deb'])
    run_command(['wget', 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb', '-O', 'chrome.deb'])
    print(" M-^Installing desktop environment and apps...")
    repo_packages = [ "xfce4", "xfce4-terminal", "dbus-x11", "xscreensaver", "task-xfce-desktop" ]
    run_command(['apt-get', 'install', '-y', '--no-install-recommends'] + repo_packages)
    print(" M-^Setting up CRD and Chrome...")
    run_command(['dpkg', '-i', 'crd.deb', 'chrome.deb'], shell=False)
    print(" M-^Fixing dependencies...")
    run_command(['apt-get', 'install', '-f', '-y'])
    print(" M-^Cleaning up...")
    os.remove('crd.deb')
    os.remove('chrome.deb')
    print(" M-^Configuring system...")
    run_command('bash -c \'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session\'', shell=True)
    setup_user()
    finalize_setup(auth_code)
    print("\n🎉 SETUP COMPLETE! 🎉")
    print("==================================================")
    print("You can now connect using Chrome Remote Desktop.")
    print(f"✔️ Username: {USERNAME}")
    print(f"✔️ Password: {PASSWORD}")
    print(f"✔️ PIN: {PIN}")
    print("==================================================")
    print_branding()
    while True:
        pass
