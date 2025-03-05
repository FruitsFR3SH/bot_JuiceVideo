from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta

stats_bp = Blueprint('stats', __name__, url_prefix='/stats', static_folder='static', template_folder='templates')
STATS_PASSWORD = "admin123"

def password_required(f):
    def decorated_function(*args, **kwargs):
        if 'stats_logged_in' not in session or not session['stats_logged_in']:
            return redirect(url_for('stats.stats_login'))  # Перенаправлення на логін
        return f(*args, **kwargs)
    return decorated_function

@stats_bp.route('/login', methods=['GET', 'POST'])
def stats_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == STATS_PASSWORD:
            session['stats_logged_in'] = True
            return redirect(url_for('stats.stats_dashboard'))
        return render_template('stats_login.html', error="Невірний пароль")
    return render_template('stats_login.html')

@stats_bp.route('/dashboard', methods=['GET'])  # Явно вказуємо GET
@password_required
def stats_dashboard():
    context = request.bot_context
    month_ago = datetime.now() - timedelta(days=30)
    
    print("Bot data:", context.bot_data)  # Відладковий вивід
    
    videos_all = context.bot_data.get("videos_downloaded", [])
    videos_month = [t for t in videos_all if t > month_ago]
    messages_all = context.bot_data.get("messages", [])
    messages_month = [t for t in messages_all if t > month_ago]
    donations_all = context.bot_data.get("total_donations", [])
    donations_month = [d for d in donations_all if d["time"] > month_ago]
    
    stats = {
        "users_count": len(context.bot_data.get("users", {})),
        "messages_total": len(messages_all),
        "messages_month": len(messages_month),
        "videos_total": len(videos_all),
        "videos_month": len(videos_month),
        "donations_total": sum(d["amount"] for d in donations_all) if donations_all else 0,
        "donations_month": sum(d["amount"] for d in donations_month) if donations_month else 0
    }
    return render_template('stats_dashboard.html', stats=stats)

@stats_bp.route('/logout', methods=['GET'])
def stats_logout():
    session.pop('stats_logged_in', None)
    return redirect(url_for('stats.stats_login'))
