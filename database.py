import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta  # Додайте pip install python-dateutil

def init_db():
    conn = sqlite3.connect("stats.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_seen TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS downloads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        download_date TEXT
    )''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect("stats.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, first_seen) VALUES (?, ?)",
              (user_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def add_download(user_id):
    conn = sqlite3.connect("stats.db")
    c = conn.cursor()
    c.execute("INSERT INTO downloads (user_id, download_date) VALUES (?, ?)",
              (user_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_total_users():
    conn = sqlite3.connect("stats.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    conn.close()
    return total

def get_active_users():
    conn = sqlite3.connect("stats.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(DISTINCT user_id) FROM downloads WHERE download_date > ?",
              ((datetime.now() - relativedelta(months=1)).isoformat(),))
    active = c.fetchone()[0]
    conn.close()
    return active

def get_total_downloads():
    conn = sqlite3.connect("stats.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM downloads")
    total = c.fetchone()[0]
    conn.close()
    return total

def get_monthly_downloads():
    conn = sqlite3.connect("stats.db")
    c = conn.cursor()
    c.execute("SELECT strftime('%Y-%m', download_date) AS month, COUNT(*) FROM downloads GROUP BY month")
    data = c.fetchall()
    conn.close()
    return dict(data)

def get_all_user_ids():
    conn = sqlite3.connect("stats.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in c.fetchall()]
    conn.close()
    return user_ids
