import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
from datetime import datetime
from db import get_connection

def initialize_stock_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER,
            added_date TEXT,
            entry_type TEXT DEFAULT 'purchase',
            location TEXT DEFAULT 'main',
            note TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_stock(product_id, quantity, added_date, entry_type='purchase', location='main', note=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO stock (product_id, quantity, added_date, entry_type, location, note)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (product_id, quantity, added_date, entry_type, location, note))
        # products টেবিলের stock আপডেট
        cursor.execute('UPDATE products SET stock = stock + ? WHERE id=?', (quantity, product_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error adding stock:", e)
        return False

def reduce_stock(product_id, quantity):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT stock FROM products WHERE id=?', (product_id,))
        current_stock = cursor.fetchone()
        if current_stock is None or current_stock[0] < quantity:
            print("Not enough stock.")
            return False
        cursor.execute('UPDATE products SET stock = stock - ? WHERE id=?', (quantity, product_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error reducing stock:", e)
        return False

def get_stock_by_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, product_id, quantity, added_date, entry_type, location, note 
        FROM stock 
        WHERE product_id = ? 
        ORDER BY added_date DESC
    ''', (product_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_stock():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, product_id, quantity, added_date, entry_type, location, note 
        FROM stock 
        ORDER BY added_date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows
