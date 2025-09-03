import sys
import os
import sqlite3
from db import get_connection
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ---------------------------
# Product Management
# ---------------------------
def add_product(name, sale_price, stock=0, purchase_price=0, code="", source="", source_desc=""):
    """
    Product add করে। source এবং source_desc নতুন optional fields হিসেবে যুক্ত করা হলো।
    """
    conn = get_connection()
    cursor = conn.cursor()
    if code:
        cursor.execute("SELECT id FROM products WHERE code=?", (code,))
        if cursor.fetchone():
            conn.close()
            return False, "Code already exists!"
    cursor.execute("""
        INSERT INTO products (name, sale_price, purchase_price, stock, code, source, source_desc)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, sale_price, purchase_price, stock, code, source, source_desc))
    conn.commit()
    conn.close()
    return True, "Product added successfully."


def get_product_by_id(product_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_product_by_name_or_code(search_value):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products
        WHERE name LIKE ? OR code = ?
        ORDER BY name
    """, (f"%{search_value}%", search_value))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_product(product_id, **kwargs):
    if not kwargs:
        return False, "No fields to update."
    conn = get_connection()
    cursor = conn.cursor()
    if "code" in kwargs and kwargs["code"]:
        cursor.execute("SELECT id FROM products WHERE code=? AND id<>?", (kwargs["code"], product_id))
        if cursor.fetchone():
            conn.close()
            return False, "Code already exists!"
    fields = ", ".join([f"{k}=?" for k in kwargs])
    values = list(kwargs.values()) + [product_id]
    cursor.execute(f"UPDATE products SET {fields}, updated_at=CURRENT_TIMESTAMP WHERE id=?", values)
    conn.commit()
    conn.close()
    return True, "Product updated successfully."


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    return True, "Product deleted successfully."


def get_all_products():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------
# Stock Management
# ---------------------------
def get_product_stock(product_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, stock, sale_price, purchase_price FROM products WHERE id=?', (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_stock(product_id, quantity_change, note=None, entry_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT stock FROM products WHERE id=?", (product_id,))
        row = cursor.fetchone()
        if not row:
            return False
        current_stock = row[0]
        new_stock = current_stock + quantity_change
        if new_stock < 0:
            return False

        cursor.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, product_id))
        cursor.execute("""
            INSERT INTO stock (product_id, quantity, entry_type, note)
            VALUES (?, ?, ?, ?)
        """, (product_id, quantity_change, entry_type, note))
        conn.commit()
        return True
    finally:
        conn.close()


def update_stock_by_name(name, delta_qty, note=None, entry_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, stock FROM products WHERE name=?", (name,))
        row = cursor.fetchone()
        if not row:
            return False
        pid, current_stock = row
        new_stock = current_stock + delta_qty
        if new_stock < 0:
            return False
        cursor.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, pid))
        cursor.execute("""
            INSERT INTO stock (product_id, quantity, entry_type, note)
            VALUES (?, ?, ?, ?)
        """, (pid, delta_qty, entry_type, note))
        conn.commit()
        return True
    finally:
        conn.close()

# ---------------------------
# Sale Price Fetch
# ---------------------------
def get_product_sale_price(product_id):
    """product_id অনুযায়ী sale_price ফেরত দেয়"""
    product = get_product_by_id(product_id)
    if product:
        return product.get("sale_price", 0)
    return 0

# ---------------------------
# Purchase Price Fetch
# ---------------------------
def get_product_purchase_price(product_id):
    """product_id অনুযায়ী purchase_price ফেরত দেয়"""
    product = get_product_by_id(product_id)
    if product:
        return product.get("purchase_price", 0)
    return 0

# ---------------------------
# Product Name Fetch (for report.py)
# ---------------------------
def get_product_name(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""
