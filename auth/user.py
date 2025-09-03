# auth/user.py (Final Version - Fixed Imports)
import hashlib
from db import get_connection, db_retry  # <-- Absolute import

def hash_password(password: str) -> str:
    """SHA-256 দিয়ে পাসওয়ার্ড হ্যাশ করা"""
    return hashlib.sha256(password.encode()).hexdigest()

@db_retry
def authenticate_user(username: str, password: str):
    """লগইন যাচাই"""
    hashed = hash_password(password)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role FROM users WHERE username=? AND password=?",
            (username, hashed)
        )
        row = cursor.fetchone()
    if row:
        return {"id": row["id"], "username": row["username"], "role": row["role"]}
    return None

@db_retry
def create_user(username: str, password: str, role="user"):
    """নতুন ইউজার তৈরি"""
    hashed = hash_password(password)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, datetime('now','localtime'))",
            (username, hashed, role)
        )
        conn.commit()

@db_retry
def reset_password(username: str, new_password: str):
    """পাসওয়ার্ড রিসেট"""
    hashed = hash_password(new_password)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password=? WHERE username=?",
            (hashed, username)
        )
        conn.commit()

@db_retry
def get_all_users():
    """সব ইউজার তালিকা"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role, created_at FROM users ORDER BY id"
        )
        return cursor.fetchall()