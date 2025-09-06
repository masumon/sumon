# product/sale.py
# বিক্রয় সম্পর্কিত সমস্ত লজিক ফাংশন এই মডিউলে থাকে।

import sqlite3
from db import get_connection
from datetime import datetime
from product.stock import reduce_stock

# -------------------------
# Helper function to fetch sales data and format it
# -------------------------
def _fetch_sales_data(cursor):
    """
    কোয়েরি করা বিক্রয় ডেটা নিয়ে ডিকশনারি লিস্ট হিসেবে ফরম্যাট করে।
    """
    rows = cursor.fetchall()
    sales = []
    for row in rows:
        sales.append({
            "id": row[0],
            "product_name": row[1],
            "quantity": row[2],
            "date": row[3],
            "total": row[4],
            "sale_price": row[5],
            "discount": row[6],
            "tax": row[7],
            "payment_method": row[8],
            "total_after_discount_tax": row[9],
            "due_amount": row[10],
            "due_received_by": row[11],
            "barcode": row[12]
        })
    return sales


# -------------------------
# Record a Sale
# -------------------------
def record_sale(product_id=None, quantity=1, sale_date=None, discount=0, tax=0, payment_method="Cash",
                due_amount=0, due_received_by="", barcode=""):
    """
    বিক্রয় রেকর্ড করে এবং stock কমায়। barcode দিলে barcode lookup করা হবে।
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if sale_date is None:
            sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Product validation using either product_id or barcode
        product_info = None
        if barcode:
            cursor.execute('SELECT id, sale_price FROM products WHERE barcode=?', (barcode,))
            result = cursor.fetchone()
            if result:
                product_id, sale_price = result
            else:
                return False, "এই বারকোডের জন্য কোন পণ্য পাওয়া যায়নি।"
        elif product_id is not None:
            cursor.execute('SELECT id, sale_price FROM products WHERE id=?', (product_id,))
            result = cursor.fetchone()
            if not result:
                return False, "পণ্য পাওয়া যায়নি।"
            product_id, sale_price = result
        else:
            return False, "কোন product_id বা barcode প্রদান করা হয়নি।"

        # Reduce stock using stock.py module
        success, msg = reduce_stock(product_id, quantity, entry_type='sale', note="Sale recorded")
        if not success:
            return False, msg

        total = sale_price * quantity
        total_after_discount_tax = total - (total * discount / 100) + (total * tax / 100)

        # Insert into sales table
        cursor.execute("""
            INSERT INTO sales (
                product_id, quantity, date, total, sale_price,
                discount, tax, payment_method, total_after_discount_tax,
                due_amount, due_received_by, barcode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id, quantity, sale_date, total, sale_price,
            discount, tax, payment_method, total_after_discount_tax,
            due_amount, due_received_by, barcode
        ))
        sale_id = cursor.lastrowid
        conn.commit()

        # If there is a due amount, add entry to due_payment
        if due_amount > 0 and due_received_by.strip() != "":
            # Note: This part assumes add_due_payment exists in a separate module
            # For this to work, make sure due_payment.due_payment.add_due_payment is imported and available
            from due_payment.due_payment import add_due_payment
            add_due_payment(due_received_by, due_amount, None, sale_id)

        return True, "বিক্রয় সফলভাবে রেকর্ড করা হয়েছে।"
    except Exception as e:
        conn.rollback()
        return False, f"বিক্রয় রেকর্ড করতে ব্যর্থ: {str(e)}"
    finally:
        conn.close()


# -------------------------
# Recent Sales
# -------------------------
def get_recent_sales(limit=50):
    """
    সাম্প্রতিক বিক্রয় ডেটা ফিরিয়ে দেয়, নির্দিষ্ট সীমা অনুযায়ী।
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT s.id, p.name as product_name, s.quantity, s.date, s.total, s.sale_price,
                   s.discount, s.tax, s.payment_method, s.total_after_discount_tax,
                   s.due_amount, s.due_received_by, s.barcode
            FROM sales s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.id DESC
            LIMIT ?
        ''', (limit,))
        return _fetch_sales_data(cursor)
    finally:
        conn.close()


# -------------------------
# Sales with Due
# -------------------------
def get_due_sales():
    """
    বাকি থাকা বিক্রয় ডেটা ফিরিয়ে দেয়।
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT s.id, p.name as product_name, s.quantity, s.date, s.total, s.sale_price,
                   s.discount, s.tax, s.payment_method, s.total_after_discount_tax,
                   s.due_amount, s.due_received_by, s.barcode
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.due_amount > 0
            ORDER BY s.id DESC
        ''')
        return _fetch_sales_data(cursor)
    finally:
        conn.close()


# -------------------------
# Sales by Product
# -------------------------
def get_sales_by_product(product_id):
    """
    নির্দিষ্ট পণ্যের জন্য সমস্ত বিক্রয় ডেটা ফিরিয়ে দেয়।
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT s.id, p.name as product_name, s.quantity, s.date, s.total, s.sale_price,
                   s.discount, s.tax, s.payment_method, s.total_after_discount_tax,
                   s.due_amount, s.due_received_by, s.barcode
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.product_id=?
            ORDER BY s.id DESC
        ''', (product_id,))
        return _fetch_sales_data(cursor)
    finally:
        conn.close()
