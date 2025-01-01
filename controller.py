# snort_manager/controller.py
import os
import subprocess
import threading
from config import Config

snort_process = None

def start_snort(interface="lo"):
    global snort_process
    
    log_dir = Config.SNORT_LOG_DIR
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    command = f"snort -i {interface} -A console -c {Config.SNORT_CONFIG_PATH} -l {log_dir} -K ascii"
    
    try:
        snort_process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        # Logları ayrı bir thread’de dosyaya aktar
        threading.Thread(target=_capture_logs).start()
    except Exception as e:
        print(f"Failed to start Snort: {e}")

def stop_snort():
    global snort_process
    if snort_process:
        snort_process.terminate()
        snort_process = None

def get_snort_status():
    global snort_process
    if snort_process and snort_process.poll() is None:
        return "Running"
    return "Stopped"

def _capture_logs():
    """Snort stdout çıktısını yakalayıp log dosyasına yazar."""
    global snort_process
    if snort_process:
        with open(Config.SNORT_LOG_FILE, "a") as log_file:
            for line in iter(snort_process.stdout.readline, b''):
                log_file.write(line.decode('utf-8', errors='ignore'))
