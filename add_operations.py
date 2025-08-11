import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
from db import get_connection  # আগের db.py থেকে কানেকশন ফাংশন নেওয়া হচ্ছে

# ======================
# USERS টেবিল CRUD
# ======================

def create_user(username: str, password: str, role: str = 'user'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, password, role) VALUES (?, ?, ?)
    ''', (username, password, role))
    conn.commit()
    conn.close()

def get_user_by_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_username(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_role(user_id: int, new_role: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET role = ?, updated_at = datetime("now", "localtime") WHERE id = ?', (new_role, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


# ======================
# PRODUCTS টেবিল CRUD
# ======================

def create_product(name: str, purchase_price: float = 0.0, sale_price: float = 0.0, stock: int = 0, category: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, purchase_price, sale_price, stock, category) VALUES (?, ?, ?, ?, ?)
    ''', (name, purchase_price, sale_price, stock, category))
    conn.commit()
    conn.close()

def get_product_by_id(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def update_product_stock(product_id: int, new_stock: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET stock = ?, updated_at = datetime("now", "localtime") WHERE id = ?', (new_stock, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Delete related entries from dependent tables
    cursor.execute('DELETE FROM purchase WHERE product_id = ?', (product_id,))
    cursor.execute('DELETE FROM stock WHERE product_id = ?', (product_id,))
    cursor.execute('DELETE FROM sales WHERE product_id = ?', (product_id,))
    cursor.execute('DELETE FROM barcodes WHERE product_id = ?', (product_id,))
    
    # DO NOT delete from 'expenses' since it has no product_id column

    # Finally delete the product itself
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()


# ======================
# STOCK টেবিল CRUD
# ======================

def add_stock(product_id: int, quantity: int, added_date: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO stock (product_id, quantity, added_date) VALUES (?, ?, ?)
    ''', (product_id, quantity, added_date))
    conn.commit()
    conn.close()

def get_stock_by_product(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stock WHERE product_id = ?', (product_id,))
    stocks = cursor.fetchall()
    conn.close()
    return stocks

def update_stock_quantity(stock_id: int, new_quantity: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE stock SET quantity = ?, updated_at = datetime("now", "localtime") WHERE id = ?', (new_quantity, stock_id))
    conn.commit()
    conn.close()

def delete_stock(stock_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM stock WHERE id = ?', (stock_id,))
    conn.commit()
    conn.close()


# ======================
# SALES টেবিল CRUD
# ======================

def create_sale(product_id: int, quantity: int, sale_price: float, total: float, sale_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sales (product_id, quantity, sale_price, total, sale_date) VALUES (?, ?, ?, ?, ?)
    ''', (product_id, quantity, sale_price, total, sale_date))
    conn.commit()
    conn.close()

def get_sale_by_id(sale_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sales WHERE id = ?', (sale_id,))
    sale = cursor.fetchone()
    conn.close()
    return sale

def update_sale(sale_id: int, product_id: int = None, quantity: int = None, sale_price: float = None, total: float = None, sale_date: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    fields = []
    params = []
    if product_id is not None:
        fields.append("product_id = ?")
        params.append(product_id)
    if quantity is not None:
        fields.append("quantity = ?")
        params.append(quantity)
    if sale_price is not None:
        fields.append("sale_price = ?")
        params.append(sale_price)
    if total is not None:
        fields.append("total = ?")
        params.append(total)
    if sale_date is not None:
        fields.append("sale_date = ?")
        params.append(sale_date)

    if not fields:
        conn.close()
        return

    params.append(sale_id)
    sql = f"UPDATE sales SET {', '.join(fields)}, updated_at = datetime('now', 'localtime') WHERE id = ?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()

def delete_sale(sale_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sales WHERE id = ?', (sale_id,))
    conn.commit()
    conn.close()


# ======================
# EXPENSES টেবিল CRUD
# ======================

def create_expense(category_id: int, amount: float, expense_date: str, description: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (category_id, amount, expense_date, description) VALUES (?, ?, ?, ?)
    ''', (category_id, amount, expense_date, description))
    conn.commit()
    conn.close()

def get_expense_by_id(expense_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
    expense = cursor.fetchone()
    conn.close()
    return expense

def update_expense(expense_id: int, category_id: int = None, amount: float = None, expense_date: str = None, description: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    fields = []
    params = []
    if category_id is not None:
        fields.append("category_id = ?")
        params.append(category_id)
    if amount is not None:
        fields.append("amount = ?")
        params.append(amount)
    if expense_date is not None:
        fields.append("expense_date = ?")
        params.append(expense_date)
    if description is not None:
        fields.append("description = ?")
        params.append(description)

    if not fields:
        conn.close()
        return

    params.append(expense_id)
    sql = f"UPDATE expenses SET {', '.join(fields)}, updated_at = datetime('now', 'localtime') WHERE id = ?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()

def delete_expense(expense_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()


# ======================
# SERVICES টেবিল CRUD
# ======================

def create_service(name: str, description: str = None, price: float = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO services (name, description, price) VALUES (?, ?, ?)
    ''', (name, description, price))
    conn.commit()
    conn.close()

def get_service_by_id(service_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services WHERE id = ?', (service_id,))
    service = cursor.fetchone()
    conn.close()
    return service

def update_service(service_id: int, name: str = None, description: str = None, price: float = None):
    conn = get_connection()
    cursor = conn.cursor()
    fields = []
    params = []
    if name is not None:
        fields.append("name = ?")
        params.append(name)
    if description is not None:
        fields.append("description = ?")
        params.append(description)
    if price is not None:
        fields.append("price = ?")
        params.append(price)

    if not fields:
        conn.close()
        return

    params.append(service_id)
    sql = f"UPDATE services SET {', '.join(fields)}, updated_at = datetime('now', 'localtime') WHERE id = ?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()

def delete_service(service_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
    conn.commit()
    conn.close()


# ======================
# RECHARGES টেবিল CRUD
# ======================

def create_recharge(mobile_number: str, amount: float, recharge_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recharges (mobile_number, amount, recharge_date) VALUES (?, ?, ?)
    ''', (mobile_number, amount, recharge_date))
    conn.commit()
    conn.close()

def get_recharge_by_id(recharge_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recharges WHERE id = ?', (recharge_id,))
    recharge = cursor.fetchone()
    conn.close()
    return recharge

def update_recharge(recharge_id: int, mobile_number: str = None, amount: float = None, recharge_date: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    fields = []
    params = []
    if mobile_number is not None:
        fields.append("mobile_number = ?")
        params.append(mobile_number)
    if amount is not None:
        fields.append("amount = ?")
        params.append(amount)
    if recharge_date is not None:
        fields.append("recharge_date = ?")
        params.append(recharge_date)

    if not fields:
        conn.close()
        return

    params.append(recharge_id)
    sql = f"UPDATE recharges SET {', '.join(fields)}, updated_at = datetime('now', 'localtime') WHERE id = ?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()

def delete_recharge(recharge_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recharges WHERE id = ?', (recharge_id,))
    conn.commit()
    conn.close()


# ======================
# BARCODES টেবিল CRUD
# ======================

def create_barcode(product_id: int, barcode: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO barcodes (product_id, barcode) VALUES (?, ?)
    ''', (product_id, barcode))
    conn.commit()
    conn.close()

def get_barcode_by_id(barcode_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM barcodes WHERE id = ?', (barcode_id,))
    barcode = cursor.fetchone()
    conn.close()
    return barcode

def get_barcode_by_code(barcode_str: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM barcodes WHERE barcode = ?', (barcode_str,))
    barcode = cursor.fetchone()
    conn.close()
    return barcode

def update_barcode(barcode_id: int, product_id: int = None, barcode: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    fields = []
    params = []
    if product_id is not None:
        fields.append("product_id = ?")
        params.append(product_id)
    if barcode is not None:
        fields.append("barcode = ?")
        params.append(barcode)

    if not fields:
        conn.close()
        return

    params.append(barcode_id)
    sql = f"UPDATE barcodes SET {', '.join(fields)}, updated_at = datetime('now', 'localtime') WHERE id = ?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()

def delete_barcode(barcode_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM barcodes WHERE id = ?', (barcode_id,))
    conn.commit()
    conn.close()


# ======================
# PURCHASE টেবিল CRUD
# ======================

def create_purchase(product_id, quantity, purchase_price, supplier='', notes=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO purchase (product_id, quantity, purchase_price, supplier, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (product_id, quantity, purchase_price, supplier, notes))
    conn.commit()
    conn.close()

def get_purchase_by_id(purchase_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM purchase WHERE id = ?', (purchase_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_purchase(purchase_id, quantity=None, price=None, supplier=None, notes=None):
    conn = get_connection()
    cursor = conn.cursor()
    fields = []
    values = []

    if quantity is not None:
        fields.append("quantity = ?")
        values.append(quantity)
    if price is not None:
        fields.append("purchase_price = ?")
        values.append(price)
    if supplier is not None:
        fields.append("supplier = ?")
        values.append(supplier)
    if notes is not None:
        fields.append("notes = ?")
        values.append(notes)

    values.append(purchase_id)
    sql = f'UPDATE purchase SET {", ".join(fields)} WHERE id = ?'
    cursor.execute(sql, tuple(values))
    conn.commit()
    conn.close()

def delete_purchase(purchase_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM purchase WHERE id = ?', (purchase_id,))
    conn.commit()
    conn.close()
