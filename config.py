import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "my_secret_key")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'snort_ids.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Snort ile ilgili varsayılan ayarlar
    SNORT_CONFIG_PATH = "/etc/snort/snort.conf"
    SNORT_RULES_PATH = "/etc/snort/rules/local.rules"
    SNORT_LOG_DIR = "/var/log/snort"
    SNORT_LOG_FILE = "/var/log/snort/snort_alerts.log"
