# auth/login.py

from auth.user import authenticate_user

def login(username: str, password: str):
    """লগইন ফাংশন যা ui_login.py থেকে কল হবে"""
    return authenticate_user(username, password)
