import sqlite3
import os
from datetime import datetime
from db import get_connection
import pandas as pd
from fpdf import FPDF

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "smartshop.db")

# ---------------------------
# Stock Operations
# ---------------------------

def add_stock(product_id, quantity, entry_type='purchase', note=None):
    """স্টকে পন্য যোগ করে। products table-এ stock আপডেট হয়"""
    if not product_id or quantity <= 0:
        return False, "Invalid product or quantity."
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT stock FROM products WHERE id=?", (product_id,))
        row = cursor.fetchone()
        if not row:
            return False, "Product not found."
        current_stock = row["stock"]
        new_stock = current_stock + quantity

        cursor.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, product_id))
        cursor.execute("""
            INSERT INTO stock (product_id, quantity, entry_type, note)
            VALUES (?, ?, ?, ?)
        """, (product_id, quantity, entry_type, note))
        conn.commit()
        return True, f"Stock added. Current stock: {new_stock}"
    finally:
        conn.close()

def update_stock_quantity(product_id, quantity_change, note=None, entry_type=None):
    """Conflict এড়ানোর জন্য add_stock wrapper"""
    return add_stock(product_id, quantity_change, entry_type or "adjustment", note)

def reduce_stock(product_id, quantity, entry_type='sale', note=None):
    """স্টক থেকে পন্য কমায়। বিক্রয়ের সাথে sync থাকে"""
    if not product_id or quantity <= 0:
        return False, "Invalid product or quantity."
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT stock FROM products WHERE id=?", (product_id,))
        row = cursor.fetchone()
        if not row:
            return False, "Product not found."
        current_stock = row["stock"]
        if current_stock < quantity:
            return False, "Insufficient stock."
        new_stock = current_stock - quantity

        cursor.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, product_id))
        cursor.execute("""
            INSERT INTO stock (product_id, quantity, entry_type, note)
            VALUES (?, ?, ?, ?)
        """, (product_id, -quantity, entry_type, note))
        conn.commit()
        return True, f"Stock reduced. Current stock: {new_stock}"
    finally:
        conn.close()

def update_stock_entry(stock_id, quantity=None, entry_type=None, note=None):
    """Stock table entry update করে, products table sync হয় না"""
    if quantity is None and entry_type is None and note is None:
        return False, "Nothing to update."
    conn = get_connection()
    cursor = conn.cursor()
    try:
        fields = []
        values = []

        if quantity is not None:
            fields.append("quantity=?")
            values.append(quantity)
        if entry_type is not None:
            fields.append("entry_type=?")
            values.append(entry_type)
        if note is not None:
            fields.append("note=?")
            values.append(note)

        values.append(stock_id)
        sql = f"UPDATE stock SET {', '.join(fields)} WHERE id=?"
        cursor.execute(sql, tuple(values))
        conn.commit()
        return True, "Stock entry updated."
    finally:
        conn.close()

def delete_stock_entry(stock_id):
    """Stock table থেকে entry delete করে, products table sync হয় না"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM stock WHERE id=?", (stock_id,))
        conn.commit()
        return True, "Stock entry deleted."
    finally:
        conn.close()

def fetch_all_stock():
    """সমস্ত stock দেখায়, products table থেকে name fetch করে"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.id, s.product_id, s.quantity, s.entry_type, s.note, s.created_at, p.name as product_name
            FROM stock s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.created_at DESC
        """)
        rows = [dict(x) for x in cursor.fetchall()]
        result = []
        for r in rows:
            result.append({
                "id": r.get("id", ""),
                "product_id": r.get("product_id", ""),
                "product_name": r.get("product_name", ""),
                "quantity": r.get("quantity", ""),
                "entry_type": r.get("entry_type", ""),
                "note": r.get("note", ""),
                "added_date": r.get("added_date", r.get("created_at", ""))
            })
        return result
    finally:
        conn.close()

def get_stock_by_product(product_id):
    """একটি product এর সমস্ত stock history"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, quantity, entry_type, note, created_at
            FROM stock
            WHERE product_id=?
            ORDER BY created_at DESC
        """, (product_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_product_name(product_id):
    """product_id অনুযায়ী নাম ফেরত দেয়"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM products WHERE id=?", (product_id,))
        row = cursor.fetchone()
        return row["name"] if row else ""
    finally:
        conn.close()

def export_stock_to_excel(file_path):
    """Stock Excel export"""
    data = fetch_all_stock()
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    return True

def export_stock_to_pdf(file_path):
    """Stock PDF export"""
    data = fetch_all_stock()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    line_height = pdf.font_size * 2.5
    col_width = pdf.epw / 7  # 7 columns

    # Header
    headers = ["ID","Product","Quantity","Entry Type","Note","Created At"]
    for h in headers:
        pdf.cell(col_width, line_height, h, border=1)
    pdf.ln(line_height)

    # Data
    for row in data:
        pdf.cell(col_width, line_height, str(row["id"]), border=1)
        pdf.cell(col_width, line_height, row["product_name"], border=1)
        pdf.cell(col_width, line_height, str(row["quantity"]), border=1)
        pdf.cell(col_width, line_height, row["entry_type"], border=1)
        pdf.cell(col_width, line_height, str(row["note"] or ""), border=1)
        pdf.cell(col_width, line_height, str(row["created_at"]), border=1)
        pdf.ln(line_height)

    pdf.output(file_path)
    return True
