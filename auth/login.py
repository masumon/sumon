from auth.user import get_user_by_username
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import hashlib

def hash_password(password: str) -> str:
    """পাসওয়ার্ড হ্যাশ করার জন্য (সাধারণ SHA256 হ্যাশ)"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def login_user(username, password):
    user = get_user_by_username(username)
    if user:
        hashed_input_password = hash_password(password)
        stored_password_hash = user[2]  # user = (id, username, password_hash, role)
        if hashed_input_password == stored_password_hash:
            return user
    return None
