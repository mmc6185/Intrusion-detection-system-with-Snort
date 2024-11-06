
import os
import subprocess
import time
from datetime import datetime

def install_snort():
    """Function to check and install Snort if not already installed."""
    try:
        subprocess.run(["snort", "-V"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Snort is already installed.")
    except FileNotFoundError:
        print("Snort not found, installing...")
        os.system("sudo apt-get update && sudo apt-get install -y snort")

def configure_snort():
    """Function to configure Snort for monitoring and alerting."""
    config_path = "/etc/snort/snort.conf"
    rules_path = "/etc/snort/rules/local.rules"
    if not os.path.exists(config_path):
        print(f"Configuration file {config_path} not found.")
        return
    if not os.path.exists(rules_path):
        print(f"Rules file {rules_path} not found. Creating default rules.")
        with open(rules_path, "w") as f:
            f.write("# Default local rules\n")
    print("Snort is configured.")

def start_snort(interface='eth0', log_dir='/var/log/snort'):
    """Start Snort in alert mode."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    command = f"snort -i {interface} -A console -c /etc/snort/snort.conf -l {log_dir}"
    print(f"Starting Snort on interface {interface}. Logs will be saved to {log_dir}.")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"Failed to start Snort: {e}")
        return None

def monitor_snort_output(process):
    """Monitor Snort output for alerts."""
    print("Monitoring Snort alerts...")
    try:
        while True:
            output = process.stdout.readline()
            if output:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] {output.strip().decode('utf-8')}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")
    finally:
        process.terminate()

if __name__ == "__main__":
    install_snort()
    configure_snort()
    snort_process = start_snort()
    if snort_process:
        monitor_snort_output(snort_process)
