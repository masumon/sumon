import ttkbootstrap as ttk
from datetime import datetime
import sqlite3

DB_PATH = "database/smartshop.db"

# -------------------------
# Timestamp Functions
# -------------------------
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


# -------------------------
# Barcode Validation Function
# -------------------------
def validate_barcode(barcode_code):
    """
    Barcode lookup validation: returns product info if exists
    Returns: dict with keys: product_id, name, sale_price
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT products.id, products.name, products.sale_price "
        "FROM products "
        "WHERE products.code = ?", 
        (barcode_code,)
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        product_id, name, sale_price = result
        return {"product_id": product_id, "name": name, "sale_price": sale_price}
    else:
        return None
