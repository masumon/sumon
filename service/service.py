# File: smartshop_pos/service/service.py

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "smartshop.db")

# ------------------- Service Type Functions -------------------
def get_all_service_types():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, category, is_active FROM service_types")
    data = cursor.fetchall()
    conn.close()
    return data

def add_service_type(name, description="", category="", is_active=1, created_at=None):
    if created_at is None:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO service_types (name, description, category, is_active, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, category, is_active, created_at))
        conn.commit()
        return True
    except Exception as e:
        print("Add Service Type Error:", e)
        return False
    finally:
        conn.close()

def update_service_type(type_id, name, description="", category="", is_active=1, updated_at=None):
    if updated_at is None:
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE service_types
            SET name=?, description=?, category=?, is_active=?, updated_at=?
            WHERE id=?
        """, (name, description, category, is_active, updated_at, type_id))
        conn.commit()
        return True
    except Exception as e:
        print("Update Service Type Error:", e)
        return False
    finally:
        conn.close()

def delete_service_type(type_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM service_types WHERE id=?", (type_id,))
        conn.commit()
        return True
    except Exception as e:
        print("Delete Service Type Error:", e)
        return False
    finally:
        conn.close()

# ------------------- Service Request Functions -------------------
def get_all_service_requests():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, t.name, r.customer_name, r.details, r.status, r.price, r.payment_status,
               r.due_amount, r.attachment, r.completed_at, r.created_at
        FROM service_requests r
        LEFT JOIN service_types t ON r.service_type_id = t.id
        ORDER BY r.id DESC
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def add_service_request(service_type_id, customer_name, details="", price=0.0, payment_status="Unpaid",
                        due_amount=0.0, attachment="", created_at=None):
    if created_at is None:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO service_requests
            (service_type_id, customer_name, details, status, price, payment_status, due_amount, attachment, created_at)
            VALUES (?, ?, ?, 'Pending', ?, ?, ?, ?, ?)
        """, (service_type_id, customer_name, details, price, payment_status, due_amount, attachment, created_at))
        conn.commit()
        return True
    except Exception as e:
        print("Add Service Request Error:", e)
        return False
    finally:
        conn.close()

def update_service_request(req_id, service_type_id, customer_name, details="", price=0.0, payment_status="Unpaid",
                           due_amount=0.0, attachment="", updated_at=None):
    if updated_at is None:
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE service_requests
            SET service_type_id=?, customer_name=?, details=?, price=?, payment_status=?, due_amount=?, attachment=?, updated_at=?
            WHERE id=?
        """, (service_type_id, customer_name, details, price, payment_status, due_amount, attachment, updated_at, req_id))
        conn.commit()
        return True
    except Exception as e:
        print("Update Service Request Error:", e)
        return False
    finally:
        conn.close()

def delete_service_request(req_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM service_requests WHERE id=?", (req_id,))
        conn.commit()
        return True
    except Exception as e:
        print("Delete Service Request Error:", e)
        return False
    finally:
        conn.close()

def update_service_request_status(req_id, status, completed_at=None):
    if completed_at is None and status == "Completed":
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        if status == "Completed":
            cursor.execute("UPDATE service_requests SET status=?, completed_at=? WHERE id=?", (status, completed_at, req_id))
        else:
            cursor.execute("UPDATE service_requests SET status=? WHERE id=?", (status, req_id))
        conn.commit()
        return True
    except Exception as e:
        print("Update Request Status Error:", e)
        return False
    finally:
        conn.close()
