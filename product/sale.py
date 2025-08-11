import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from db import get_connection

def get_product_stock(product_id):
    """নির্দিষ্ট পণ্যের বর্তমান স্টক ফেরত দেবে"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT stock FROM products WHERE id=?', (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def record_sale(product_id, quantity, sale_price, sale_date):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        current_stock = get_product_stock(product_id)
        if current_stock is None:
            print(f"[record_sale] Product ID {product_id} not found.")
            return False

        print(f"[record_sale] Current stock before sale: {current_stock}")

        if current_stock < quantity:
            print("[record_sale] Error: Not enough stock to sell")
            return False

        total = quantity * sale_price

        cursor.execute('''
            INSERT INTO sales (product_id, quantity, sale_price, total, sale_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, quantity, sale_price, total, sale_date))

        cursor.execute('UPDATE products SET stock = stock - ? WHERE id=?', (quantity, product_id))

        conn.commit()

        updated_stock = get_product_stock(product_id)
        print(f"[record_sale] Stock after sale: {updated_stock}")

        return True
    except Exception as e:
        print("Error recording sale:", e)
        return False
    finally:
        conn.close()

def get_sales_by_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, product_id, quantity, sale_price, total, sale_date FROM sales WHERE product_id=?', (product_id,))
    sales = cursor.fetchall()
    conn.close()
    return sales

if __name__ == "__main__":
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    if record_sale(1, 3, 150, today):
        print("Sale recorded successfully")

    sales = get_sales_by_product(1)
    print("Sales for product 1:")
    for s in sales:
        print(s)
