import os
import subprocess
import re
import time

# --- RDP Setup Script v9.0 (Live Output Edition) ---
print("--- RDP Setup Script v9.0 (Live Output Edition) ---")

# --- CONFIGURATION ---
USERNAME = "user"
PASSWORD = "root"
PIN = "123456" 

# --- Helper Functions ---
def run_command_with_output(command, shell=False):
    """Runs a command and shows its live output in the terminal."""
    try:
        # By not setting stdout or stderr, they will print directly to the terminal
        subprocess.run(command, check=True, shell=shell)
    except subprocess.CalledProcessError:
        print(f"\n❌ Command Error occurred while running: {' '.join(command) if isinstance(command, list) else command}")
        exit(1)
        
def run_silent_command(command, shell=False):
    """Runs a command silently in the background."""
    try:
        subprocess.run(command, check=True, shell=shell, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode().strip()
        print(f"\n❌ Command Error: {error_message}")
        exit(1)

def print_branding():
    """Prints the custom ZainShiraz branding in solid red."""
    RED = "\033[91m"
    RESET = "\03.3[0m"
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

# --- Main Execution Block ---
if __name__ == "__main__":
    start_time = time.time()
    
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

    print("\n⚡ Starting Installation with Live Output...")
    
    # --- Installation Steps with Live Output ---
    print("\n--- Step 1: Updating package lists ---")
    run_command_with_output(['apt-get', 'update'])

    print("\n--- Step 2: Downloading CRD and Chrome ---")
    run_command_with_output(['wget', '-c', 'https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb', '-O', 'crd.deb'])
    run_command_with_output(['wget', '-c', 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb', '-O', 'chrome.deb'])

    print("\n--- Step 3: Installing Desktop Environment & Apps ---")
    repo_packages = [ "xfce4", "xfce4-terminal", "dbus-x11", "xscreensaver", "task-xfce-desktop" ]
    run_command_with_output(['apt-get', 'install', '-y'] + repo_packages)

    print("\n--- Step 4: Setting up CRD and Chrome from downloaded files ---")
    try:
        subprocess.run(['dpkg', '-i', 'crd.deb', 'chrome.deb'], check=True)
    except subprocess.CalledProcessError:
        print("\n--- Step 5: Fixing any broken dependencies ---")
        run_command_with_output(['apt-get', 'install', '-f', '-y'])
    
    # --- Silent Configuration Steps ---
    print("\n--- Step 6: Final Configuration ---")
    
    # Configure User
    if subprocess.run(['id', USERNAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        run_silent_command(['useradd', '-m', '-s', '/bin/bash', USERNAME])
    run_silent_command(f"echo '{USERNAME}:{PASSWORD}' | chpasswd", shell=True)
    run_silent_command(['adduser', USERNAME, 'sudo'])
    print("✔️ User configured.")

    # Configure CRD Session
    run_silent_command('bash -c \'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session\'', shell=True)
    run_silent_command(['adduser', USERNAME, 'chrome-remote-desktop'])
    print("✔️ CRD session configured.")
    
    # Launch CRD Host
    start_command = (
        f"/opt/google/chrome-remote-desktop/start-host "
        f"--code=\"{auth_code}\" "
        f"--redirect-url=https://remotedesktop.google.com/_/oauthredirect "
        f"--name=$(hostname) "
        f"--pin={PIN}"
    )
    print("✔️ Launching CRD host service...")
    run_silent_command(['su', '-', USERNAME, '-c', start_command])
    run_silent_command(['service', 'chrome-remote-desktop', 'start'])
    print("✔️ CRD Service Started.")
    
    # Cleanup
    os.remove('crd.deb')
    os.remove('chrome.deb')
    print("✔️ Cleanup complete.")
    
    # --- Final Summary ---
    total_time = time.time() - start_time
    mins, secs = divmod(int(total_time), 60)

    print(f"\n🎉 SETUP COMPLETE! (Total Time: {mins:02d}:{secs:02d}) 🎉")
    print("==================================================")
    print("You can now connect using Chrome Remote Desktop.")
    print(f"✔️ Username: {USERNAME}")
    print(f"✔️ Password: {PASSWORD}")
    print(f"✔️ PIN: {PIN}")
    print("==================================================")
    
    print_branding()
    
    while True:
        pass
