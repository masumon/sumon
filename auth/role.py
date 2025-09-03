# auth/role.py

def is_admin(user: dict) -> bool:
    """Check if user is admin"""
    return user.get("role") == "admin"

def is_employee(user: dict) -> bool:
    """Check if user is employee"""
    return user.get("role") == "employee"
