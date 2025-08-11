import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'smartshop.db')  # ডাটাবেসের পাথ

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    # users টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    # products টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            purchase_price REAL,
            sale_price REAL,
            stock INTEGER DEFAULT 0,
            category TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    # ... (আপনার আগের টেবিলগুলো এখানেই থাকবে, যেভাবে দিয়েছেন) ...

    conn.commit()
    conn.close()
    print("✅ ডাটাবেস ইনিশিয়ালাইজেশন সম্পন্ন হয়েছে।")

# --- এখন প্রয়োজনীয় ফাংশনগুলো ---

def hash_password(password: str) -> str:
    """পাসওয়ার্ড হ্যাশ করার জন্য (SHA256)"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(username: str, password: str, role: str = "user") -> bool:
    """
    নতুন ইউজার রেজিস্টার করবে।
    সফল হলে True রিটার্ন করবে,
    username আগে থেকে থাকলে False রিটার্ন করবে।
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        hashed_pw = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_pw, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # ইউজারনেম ডুপ্লিকেট হলে এই এরর আসবে
        return False
    finally:
        conn.close()

def login_user(username: str, password: str):
    """
    ইউজারনেম-পাসওয়ার্ড চেক করবে।
    লগইন সফল হলে ইউজারের রেকর্ড রিটার্ন করবে (tuple),
    না হলে None রিটার্ন করবে।
    """
    conn = get_connection()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)
    cursor.execute(
        "SELECT id, username, password, role FROM users WHERE username=? AND password=?",
        (username, hashed_pw)
    )
    user = cursor.fetchone()
    conn.close()

    return user

if __name__ == '__main__':
    initialize_db()
