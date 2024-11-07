
import os
import subprocess
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Güvenlik için kullanılan gizli anahtar

snort_process = None  # Snort sürecini global olarak takip etmek için değişken
snort_log_file = "/var/log/snort/snort_alerts.log"  # Logların kaydedileceği dosya yolu

def install_snort():
    """Snort'un kurulu olup olmadığını kontrol eder ve gerekirse kurar."""
    try:
        # Snort'un yüklü olup olmadığını kontrol et
        subprocess.run(["snort", "-V"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Snort is already installed.")
    except FileNotFoundError:
        # Eğer Snort kurulu değilse, yükleme işlemi
        print("Snort not found, installing...")
        os.system("sudo apt-get update && sudo apt-get install -y snort")

def configure_snort():
    """Snort yapılandırma dosyalarını kontrol eder ve eksik dosyaları oluşturur."""
    config_path = "/etc/snort/snort.conf"
    rules_path = "/etc/snort/rules/local.rules"
    
    if not os.path.exists(config_path):
        print(f"Configuration file {config_path} not found.")
        return False
    
    if not os.path.exists(rules_path):
        # Eğer local.rules dosyası yoksa oluştur
        print(f"Rules file {rules_path} not found. Creating default rules.")
        with open(rules_path, "w") as f:
            f.write("# Default local rules\n")
    print("Snort is configured.")
    return True

def start_snort(interface='lo', log_dir='/var/log/snort'):
    """Snort'u belirtilen ağ arayüzünde başlatır."""
    global snort_process
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    command = f"snort -i {interface} -A console -c /etc/snort/snort.conf -l {log_dir} -K ascii"
    try:
        # Snort'u başlat ve çıktıyı ayrı bir thread üzerinde işle
        snort_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        threading.Thread(target=log_snort_output).start()
    except Exception as e:
        print(f"Failed to start Snort: {e}")

def stop_snort():
    """Çalışan Snort sürecini durdurur."""
    global snort_process
    if snort_process:
        snort_process.terminate()
        snort_process = None

def log_snort_output():
    """Snort çıktısını log dosyasına yazar."""
    global snort_process
    if snort_process:
        with open(snort_log_file, "w") as log_file:
            for line in iter(snort_process.stdout.readline, b''):
                log_file.write(line.decode('utf-8'))

@app.route('/')
def index():
    """Ana sayfa: Snort durumu ve kontrol butonları."""
    status = "Running" if snort_process else "Stopped"
    return render_template('index.html', status=status)

@app.route('/start', methods=['POST'])
def start():
    """Snort'u başlatır."""
    interface = request.form.get('interface', 'lo')
    start_snort(interface)
    flash("Snort started successfully.", "success")
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    """Snort'u durdurur."""
    stop_snort()
    flash("Snort stopped successfully.", "info")
    return redirect(url_for('index'))

@app.route('/logs')
def logs():
    """Snort loglarını gösterir."""
    if os.path.exists(snort_log_file):
        with open(snort_log_file, 'r') as file:
            logs = file.readlines()
    else:
        logs = ["No logs available."]
    return render_template('logs.html', logs=logs)

@app.route('/configure', methods=['GET', 'POST'])
def configure():
    """Snort kurallarını düzenlemek için bir form sunar."""
    if request.method == 'POST':
        rules = request.form.get('rules')
        with open("/etc/snort/rules/local.rules", "w") as f:
            f.write(rules)
        flash("Rules updated successfully.", "success")
        return redirect(url_for('configure'))
    else:
        with open("/etc/snort/rules/local.rules", "r") as f:
            current_rules = f.read()
        return render_template('configure.html', rules=current_rules)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
