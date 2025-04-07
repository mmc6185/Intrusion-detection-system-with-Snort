#!/usr/bin/env python3
"""
bootstrap_env.py – Tek makinelik IDS laboratuvarı için otomatik kurulum sihirbazı.

Bu betik aşağıdakileri kontrol eder ve eksikse kurar/oluşturur:
  • Docker Engine + docker compose CLI
  • Snort 3 (native)  ➜ (Opsiyonel, konteyner içinde de çalışır)
  • Python 3.10+ ve pip + requirements.txt
  • docker‑compose yığını (ilk build & up)
  • config/thresholds.yaml ve docker-compose.yml şablonlarını üretir

Ubuntu/Debian tabanlı sistemlerde test edilmiştir. Diğer dağıtımlarda
uyarlama gerekebilir. Betik root veya sudo ile çalıştırılmalıdır.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
REQUIREMENTS = PROJECT_DIR / "requirements.txt"
DC_FILE = PROJECT_DIR / "docker-compose.yml"
THRESH_FILE = PROJECT_DIR / "config/thresholds.yaml"

DOCKER_COMPOSE_YML = """version: '3.9'
services:
  snort:
    image: ghcr.io/snort3/snort3:latest
    command: >-
      snort -c /etc/snort/snort.lua -A alert_json -l /logs $(python /detect_ifaces.py) -k none
    volumes:
      - ./logs:/logs
      - ./snort/rules:/etc/snort/rules
      - ./snort/detect_ifaces.py:/detect_ifaces.py
    network_mode: host

  processor:
    build: ./processor
    environment:
      - DB_URL=mysql+pymysql://ids:ids@db/ids
      - THRESHOLDS_FILE=/app/config/thresholds.yaml
    volumes:
      - ./logs:/logs
      - ./config:/app/config
    depends_on: [snort, db]

  api:
    build: ./api
    ports: ['5000:5000']
    environment:
      - DB_URL=mysql+pymysql://ids:ids@db/ids
    depends_on: [db]

  ui:
    build: ./ui
    ports: ['80:80']
    depends_on: [api]

  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: ids
      MYSQL_USER: ids
      MYSQL_PASSWORD: ids
    volumes:
      - ./db:/var/lib/mysql
"""

THRESHOLDS_YAML_CONTENT = """# Snort öncelik ➜ tehlike seviyesi eşlemesi
1: danger
2: warning
3: safe
4: safe
"""

# ------------------ Yardımcılar ------------------

def run(cmd: str, check: bool = True):
    print(f"[+] $ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        print(f"[!] Komut başarısız: {cmd}")
        sys.exit(1)
    return result.returncode == 0

def exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def require_root():
    if os.geteuid() != 0:
        print("Bu betik root yetkileriyle çalıştırılmalıdır. Sudo ile tekrar deneyin.")
        sys.exit(1)

# ------------------ Dosya Oluşturma ------------------

def ensure_files():
    # config klasörü
    (PROJECT_DIR / 'config').mkdir(exist_ok=True)
    if not DC_FILE.exists():
        print("[ ] docker-compose.yml bulunamadı, oluşturuluyor…")
        DC_FILE.write_text(DOCKER_COMPOSE_YML)
        print("[✓] docker-compose.yml oluşturuldu.")
    else:
        print("[✓] docker-compose.yml zaten mevcut.")

    if not THRESH_FILE.exists():
        print("[ ] thresholds.yaml bulunamadı, oluşturuluyor…")
        THRESH_FILE.write_text(THRESHOLDS_YAML_CONTENT)
        print("[✓] thresholds.yaml oluşturuldu.")
    else:
        print("[✓] thresholds.yaml zaten mevcut.")

# ------------------ Kurulum Adımları ------------------

def install_docker():
    if exists("docker"):
        print("[✓] Docker zaten kurulu.")
        return
    print("[ ] Docker bulunamadı, kuruluyor…")
    distro = platform.freedesktop_os_release().get("ID", "")
    if distro in ("ubuntu", "debian"):
        run("apt-get update -y")
        run("apt-get install -y ca-certificates curl gnupg lsb-release")
        run("mkdir -p /etc/apt/keyrings")
        run("curl -fsSL https://download.docker.com/linux/$(lsb_release -si | tr '[:upper:]' '[:lower:]')/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg")
        run("echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$(lsb_release -si | tr '[:upper:]' '[:lower:]') $(lsb_release -sc) stable\" > /etc/apt/sources.list.d/docker.list")
        run("apt-get update -y")
        run("apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin")
    else:
        print("[!] Docker kurulumu için otomatik desteklenmeyen dağıtım. Manuel kurun.")
        sys.exit(1)
    print("[✓] Docker kuruldu.")


def install_docker_compose():
    if run("docker compose version", check=False):
        print("[✓] docker compose CLI mevcut.")
        return
    print("[ ] docker compose CLI yok, kuruluyor…")
    compose_url = "https://github.com/docker/compose/releases/download/v2.24.7/docker-compose-linux-x86_64"
    target = "/usr/local/bin/docker-compose"
    run(f"curl -L {compose_url} -o {target}")
    run(f"chmod +x {target}")
    print("[✓] docker-compose binary kuruldu.")


def install_snort3():
    if exists("snort"):
        print("[✓] Snort zaten kurulu (native).")
        return
    print("[ ] Snort 3 bulunamadı, kuruluyor… (biraz sürebilir)")
    distro = platform.freedesktop_os_release().get("ID", "")
    if distro in ("ubuntu", "debian"):
        run("add-apt-repository -y ppa:snort3/snort3")
        run("apt-get update -y")
        run("apt-get install -y snort++")
    else:
        print("[!] Otomatik Snort 3 kurulumu desteklenmiyor, lütfen elle kurun veya konteyner kullanın.")
        return
    print("[✓] Snort 3 kuruldu.")


def install_python_requirements():
    pyver = sys.version_info
    if pyver < (3, 10):
        print("Python 3.10+ gereklidir. Lütfen yükseltin.")
        sys.exit(1)
    run("python3 -m pip install --upgrade pip")
    if REQUIREMENTS.exists():
        run(f"python3 -m pip install -r {REQUIREMENTS}")


def bring_up_compose():
    print("[ ] Docker Compose yığını başlatılıyor…")
    run("docker compose pull", check=False)
    run("docker compose up --build -d")
    print("[✓] Yığın çalışıyor. 'docker compose ps' ile kontrol edebilirsiniz.")

# ------------------ Ana Akış ------------------

def main():
    require_root()
    ensure_files()
    install_docker()
    install_docker_compose()
    install_snort3()
    install_python_requirements()
    bring_up_compose()
    print("\nKurulum tamamlandı! Dashboard'a http://localhost üzerinden erişebilirsiniz.")


if __name__ == "__main__":
    main()
