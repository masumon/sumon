import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from db import get_connection

def initialize_product_tables():
    """
    পণ্যের টেবিল তৈরি করবে যদি না থাকে:
    - products: পণ্যের ডিটেইলস (barcode সহ)
    - sales: বিক্রয় সংক্রান্ত তথ্য
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            purchase_price REAL NOT NULL,
            sale_price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            category TEXT,
            barcode TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            sale_price REAL NOT NULL,
            total REAL NOT NULL,
            sale_date TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_product(name, purchase_price, sale_price, stock=0, category=None, barcode=None):
    """
    নতুন পণ্য যোগ করবে (barcode সহ)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO products (name, purchase_price, sale_price, stock, category, barcode)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, purchase_price, sale_price, stock, category, barcode))
        conn.commit()
        return True
    except Exception as e:
        print("পণ্য যোগে ত্রুটি:", e)
        return False
    finally:
        conn.close()

def get_all_products():
    """
    সব পণ্যের তালিকা ফেরত দিবে (barcode সহ)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, purchase_price, sale_price, stock, category, barcode FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

def get_product_by_id(product_id):
    """
    আইডি অনুযায়ী একটি পণ্যের তথ্য ফিরিয়ে দিবে (barcode সহ)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, purchase_price, sale_price, stock, category, barcode FROM products WHERE id=?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def update_product(product_id, name=None, purchase_price=None, sale_price=None, stock=None, category=None, barcode=None):
    """
    একটি পণ্য আপডেট করবে, প্রয়োজনীয় ক্ষেত্রগুলো (barcode সহ)
    """
    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    if name is not None:
        fields.append('name=?')
        values.append(name)
    if purchase_price is not None:
        fields.append('purchase_price=?')
        values.append(purchase_price)
    if sale_price is not None:
        fields.append('sale_price=?')
        values.append(sale_price)
    if stock is not None:
        fields.append('stock=?')
        values.append(stock)
    if category is not None:
        fields.append('category=?')
        values.append(category)
    if barcode is not None:
        fields.append('barcode=?')
        values.append(barcode)

    values.append(product_id)

    try:
        query = f"UPDATE products SET {', '.join(fields)} WHERE id=?"
        cursor.execute(query, tuple(values))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("পণ্য আপডেট করতে সমস্যা:", e)
        return False
    finally:
        conn.close()

def delete_product(product_id):
    """
    একটি পণ্য মুছে ফেলবে
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("পণ্য মুছতে সমস্যা:", e)
        return False
    finally:
        conn.close()

def get_product_list():
    """
    বিক্রয়ের জন্য Combobox বা Dropdown-এ দেখানোর জন্য শুধু id এবং name রিটার্ন করবে
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

if __name__ == "__main__":
    # টেস্টিং (পুনরায় চালানোর জন্য)
    initialize_product_tables()

    if add_product("টেস্ট পণ্য", 100, 150, 10, "ইলেক্ট্রনিক্স", "1234567890123"):
        print("পণ্য সফলভাবে যোগ হয়েছে।")

    products = get_all_products()
    print("সব পণ্য:")
    for p in products:
        print(p)

    product = get_product_by_id(1)
    print("আইডি ১ এর পণ্য:", product)

    if update_product(1, sale_price=200, barcode="9876543210987"):
        print("পণ্য সফলভাবে আপডেট হয়েছে।")

    if delete_product(1):
        print("পণ্য সফলভাবে মুছে ফেলা হয়েছে।")
