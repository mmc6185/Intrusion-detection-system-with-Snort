# webapp/routes.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .extensions import db, login_manager
from .models import User
from .forms import LoginForm, RegisterForm, RuleForm
from snort_manager.controller import start_snort, stop_snort, get_snort_status
from snort_manager.installer import check_and_install_snort, configure_snort
from config import Config

main_bp = Blueprint("main_bp", __name__)

@main_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.dashboard"))
    return render_template("home.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Basit bir gösterge paneli, grafik vs. için."""
    return render_template("dashboard.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful", "success")
            return redirect(url_for("main_bp.dashboard"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for("main_bp.login"))

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Yeni kullanıcı oluştur
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already in use.", "warning")
            return redirect(url_for("main_bp.register"))
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("main_bp.login"))
    return render_template("register.html", form=form)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main_bp.route("/snort_control", methods=["GET", "POST"])
@login_required
def snort_control():
    """Snort'un durumunu gösterir, başlat/durdur butonları vs."""
    if request.method == "POST":
        action = request.form.get("action")
        interface = request.form.get("interface", "lo")
        if action == "start":
            check_and_install_snort()
            configure_snort(Config.SNORT_CONFIG_PATH, Config.SNORT_RULES_PATH)
            start_snort(interface)
            flash(f"Snort started on interface {interface}", "success")
        elif action == "stop":
            stop_snort()
            flash("Snort stopped", "info")
        return redirect(url_for("main_bp.snort_control"))
    
    status = get_snort_status()
    return render_template("snort_control.html", status=status)

@main_bp.route("/logs")
@login_required
def show_logs():
    """Snort loglarını oku, tablo şeklinde göster."""
    if os.path.exists(Config.SNORT_LOG_FILE):
        with open(Config.SNORT_LOG_FILE, "r") as f:
            lines = f.read().splitlines()
    else:
        lines = ["No logs available."]
    return render_template("logs.html", logs=lines)

@main_bp.route("/rules", methods=["GET", "POST"])
@login_required
def manage_rules():
    form = RuleForm()
    if request.method == "POST":
        if form.validate_on_submit():
            with open(Config.SNORT_RULES_PATH, "w") as f:
                f.write(form.rules.data)
            flash("Rules updated successfully", "success")
            return redirect(url_for("main_bp.manage_rules"))
    else:
        # Mevcut rules dosyasını form alanına doldur
        if os.path.exists(Config.SNORT_RULES_PATH):
            with open(Config.SNORT_RULES_PATH, "r") as f:
                form.rules.data = f.read()
    return render_template("rules.html", form=form)

@main_bp.route("/api/log_stats", methods=["GET"])
@login_required
def log_stats():
    """
    Örnek bir endpoint: log verisini parse edip JSON dönelim.
    Front-end (chart.js) bunu alıp grafik olarak gösterebilir.
    """
    if not os.path.exists(Config.SNORT_LOG_FILE):
        return jsonify({"labels": [], "data": []})
    
    # Basit bir örnek: hangi IP adresine karşı kaç kere alert üretilmiş gibi bir mantık kuralım.
    ip_count = {}
    with open(Config.SNORT_LOG_FILE, "r") as f:
        for line in f:
            # Örnek: "[**] [1:1000001:0] ... -> 192.168.1.10"
            # Basit bir parse (Gerçek log formatına göre uyarlayın)
            if "->" in line:
                parts = line.split("->")
                if len(parts) == 2:
                    dst_part = parts[1].strip()
                    # IP'yi ayıklamaya çalışalım (çok basit parse)
                    ip = dst_part.split(":")[0]
                    ip_count[ip] = ip_count.get(ip, 0) + 1

    # Chart.js’e uygun format: labels[], data[]
    labels = list(ip_count.keys())
    data = list(ip_count.values())
    return jsonify({"labels": labels, "data": data})
