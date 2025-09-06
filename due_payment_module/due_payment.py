# due_payment_module/due_payment.py
import datetime
import os
import sys
import sqlite3

# Project root যোগ করা যাতে db module পাওয়া যায়
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from db import get_connection, db_retry

# -----------------
# Due Payment CRUD Functions
# -----------------

@db_retry
def get_all_due_payments():
    """
    Fetch all due payments from database.
    Returns list of dicts.
    """
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, customer, amount, due_date, sale_id, date FROM due_payment")
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        return result
    except sqlite3.Error as e:
        print(f"DB Error (get_all_due_payments): {e}")
        return []
    finally:
        if conn:
            conn.close()

@db_retry
def add_due_payment(customer, amount, due_date, sale_id=None):
    """
    Add a new due payment to database.
    """
    conn = get_connection()
    if not conn:
        raise ValueError("Database connection failed.")
    cursor = conn.cursor()
    try:
        # Duplicate check
        cursor.execute(
            "SELECT id FROM due_payment WHERE customer=? AND due_date=? AND sale_id IS ?",
            (customer, due_date, sale_id)
        )
        if cursor.fetchone():
            raise ValueError("Duplicate due payment detected.")
        cursor.execute(
            "INSERT INTO due_payment (customer, amount, due_date, sale_id, date) VALUES (?, ?, ?, ?, ?)",
            (customer, float(amount), due_date, sale_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
    except sqlite3.Error as e:
        raise ValueError(f"DB Error (add_due_payment): {e}")
    finally:
        if conn:
            conn.close()

@db_retry
def update_due_payment(due_id, customer, amount, due_date):
    """
    Update an existing due payment record.
    """
    conn = get_connection()
    if not conn:
        raise ValueError("Database connection failed.")
    cursor = conn.cursor()
    try:
        # Duplicate prevention
        cursor.execute(
            "SELECT id FROM due_payment WHERE customer=? AND due_date=? AND id!=?",
            (customer, due_date, due_id)
        )
        if cursor.fetchone():
            raise ValueError("Duplicate due payment detected after update.")
        cursor.execute(
            "UPDATE due_payment SET customer=?, amount=?, due_date=? WHERE id=?",
            (customer, float(amount), due_date, due_id)
        )
        conn.commit()
    except sqlite3.Error as e:
        raise ValueError(f"DB Error (update_due_payment): {e}")
    finally:
        if conn:
            conn.close()

@db_retry
def delete_due_payment(due_id):
    """
    Delete a due payment record.
    """
    conn = get_connection()
    if not conn:
        raise ValueError("Database connection failed.")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM due_payment WHERE id=?", (due_id,))
        conn.commit()
    except sqlite3.Error as e:
        raise ValueError(f"DB Error (delete_due_payment): {e}")
    finally:
        if conn:
            conn.close()

@db_retry
def get_customer_due_summary(customer_name):
    """
    Calculate total due for a specific customer.
    """
    conn = get_connection()
    if not conn:
        return {"total_due": 0, "total_sales_due": 0, "total_service_due": 0}
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT amount, sale_id FROM due_payment WHERE customer=?",
            (customer_name,)
        )
        rows = cursor.fetchall()
        total_due = 0
        total_sales_due = 0
        total_service_due = 0
        for row in rows:
            amount = row["amount"] if row["amount"] else 0
            total_due += amount
            if row["sale_id"]:
                total_sales_due += amount
            else:
                total_service_due += amount
        return {
            "total_due": total_due,
            "total_sales_due": total_sales_due,
            "total_service_due": total_service_due
        }
    except sqlite3.Error as e:
        print(f"DB Error (get_customer_due_summary): {e}")
        return {"total_due": 0, "total_sales_due": 0, "total_service_due": 0}
    finally:
        if conn:
            conn.close()

@db_retry
def sync_due_from_sales_and_service():
    """
    Synchronize dues from sales and service tables (placeholder logic).
    Returns True if new data added.
    """
    # TODO: Implement actual sync logic from sales/service tables
    print("Syncing due payments from sales and service...")
    return False

@db_retry
def get_due_payments_report(start_date=None, end_date=None):
    """
    Return list of due payments filtered by start_date and end_date.
    """
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    query = "SELECT id, customer, amount, due_date, sale_id, date FROM due_payment WHERE 1=1"
    params = []
    if start_date and end_date:
        query += " AND due_date BETWEEN ? AND ?"
        params = [start_date, end_date]
    elif start_date:
        query += " AND due_date >= ?"
        params = [start_date]
    elif end_date:
        query += " AND due_date <= ?"
        params = [end_date]
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        combined = []
        seen = set()
        for row in rows:
            key = (row['customer'], row['due_date'], row['sale_id'])
            if key in seen:
                continue
            seen.add(key)
            combined.append(dict(row))
        return combined
    except sqlite3.Error as e:
        print(f"DB Error (get_due_payments_report): {e}")
        return []
    finally:
        if conn:
            conn.close()
