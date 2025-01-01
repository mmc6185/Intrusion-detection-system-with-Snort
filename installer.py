# snort_manager/installer.py
import os
import subprocess

def check_and_install_snort():
    try:
        subprocess.run(["snort", "-V"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Snort is already installed.")
    except FileNotFoundError:
        print("Snort not found, installing...")
        os.system("sudo apt-get update && sudo apt-get install -y snort")

def configure_snort(config_path, rules_path):
    if not os.path.exists(config_path):
        print(f"Configuration file {config_path} not found.")
        return False
    
    if not os.path.exists(rules_path):
        print(f"Rules file {rules_path} not found. Creating default rules.")
        with open(rules_path, "w") as f:
            f.write("# Default local rules\n")
    
    print("Snort is configured.")
    return True
