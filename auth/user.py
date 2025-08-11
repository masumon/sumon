from db import get_connection
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import hashlib

def hash_password(password: str) -> str:
    """পাসওয়ার্ড হ্যাশ করার জন্য (সাধারণ SHA256 হ্যাশ)"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(username, password, role="user"):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', (username, hashed_password, role))
        conn.commit()
        return True
    except Exception as e:
        print(f"[register_user] Error: {e}")
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone()

def initialize_auth_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    conn.commit()
    conn.close()
