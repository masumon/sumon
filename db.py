import sqlite3
import os
import time
from datetime import datetime
import threading

# ---------------------------
# Database setup
# ---------------------------
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DB_FOLDER = os.path.join(PROJECT_ROOT, "database")
os.makedirs(DB_FOLDER, exist_ok=True)
DB_PATH = os.path.join(DB_FOLDER, "smartshop.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def db_retry(func):
    def wrapper(*args, **kwargs):
        retries = 3
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if 'locked' in str(e).lower():
                    time.sleep(0.1)
                    continue
                else:
                    raise
        raise sqlite3.OperationalError("Database is locked after multiple retries.")
    return wrapper

# ---------------------------
# Tables initialization
# ---------------------------
@db_retry
def init_all_tables():
    with get_connection() as conn:
        cursor = conn.cursor()
        # Products
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                purchase_price REAL DEFAULT 0,
                sale_price REAL DEFAULT 0,
                stock INTEGER DEFAULT 0,
                code TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                updated_at TEXT DEFAULT (datetime('now','localtime')),
                source TEXT,
                source_desc TEXT
            )
        """)
        # Stock
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                added_date TEXT DEFAULT (datetime('now','localtime')),
                entry_type TEXT,
                location TEXT,
                note TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        # Sales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                sale_price REAL DEFAULT 0,
                total REAL DEFAULT 0,
                date TEXT DEFAULT (datetime('now','localtime')),
                discount REAL DEFAULT 0,
                tax REAL DEFAULT 0,
                total_after_discount_tax REAL DEFAULT 0,
                due_amount REAL DEFAULT 0,
                due_received_by TEXT,
                barcode TEXT,
                sold_by TEXT,
                invoice_no TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        # Recharge
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recharge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                mobile TEXT NOT NULL,
                operator TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            )
        """)
        # Expenses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                amount REAL DEFAULT 0,
                date TEXT DEFAULT (datetime('now','localtime')),
                note TEXT,
                FOREIGN KEY(category_id) REFERENCES expense_categories(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        # Due Payment
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS due_payment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT,
                sale_id INTEGER,
                date TEXT DEFAULT (datetime('now','localtime')),
                product_name TEXT,
                quantity INTEGER,
                FOREIGN KEY(sale_id) REFERENCES sales(id)
            )
        """)
        # Due
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS due (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)
        # Service Types
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        # Service Requests
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_type_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                details TEXT,
                status TEXT,
                price REAL DEFAULT 0,
                requested_at TEXT DEFAULT (datetime('now','localtime')),
                payment_status TEXT DEFAULT 'Unpaid',
                due_amount REAL DEFAULT 0,
                attachment TEXT,
                completed_at TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY(service_type_id) REFERENCES service_types(id)
            )
        """)
        # Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()

# ---------------------------
# CRUD generator
# ---------------------------
@db_retry
def get_columns(table_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row["name"] for row in cursor.fetchall()]

def generate_crud(table_name):
    @db_retry
    def add(data_dict=None, **kwargs):
        if data_dict is None:
            data_dict = kwargs
        cols = ", ".join(data_dict.keys())
        placeholders = ", ".join("?" for _ in data_dict)
        values = list(data_dict.values())
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        columns_in_table = get_columns(table_name)
        if 'created_at' in columns_in_table and 'created_at' not in data_dict:
            cols += ", created_at"
            placeholders += ", ?"
            values.append(now)
        if 'updated_at' in columns_in_table and 'updated_at' not in data_dict:
            cols += ", updated_at"
            placeholders += ", ?"
            values.append(now)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})", values)
            conn.commit()
            return cursor.lastrowid

    @db_retry
    def get_all():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            return cursor.fetchall()

    @db_retry
    def update(row_id, data_dict=None, **kwargs):
        if data_dict is None:
            data_dict = kwargs
        fields = ", ".join(f"{k}=?" for k in data_dict.keys())
        values = list(data_dict.values())
        if 'updated_at' in get_columns(table_name) and 'updated_at' not in data_dict:
            fields += ", updated_at=?"
            values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        values.append(row_id)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE {table_name} SET {fields} WHERE id=?", values)
            conn.commit()

    @db_retry
    def delete(row_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (row_id,))
            conn.commit()

    return add, get_all, update, delete

# ---------------------------
# Generate CRUD aliases
# ---------------------------
tables = [
    "products","stock","sales","recharge",
    "expenses","expense_categories",
    "due_payment","due",
    "service_types","service_requests",
    "users"
]

crud_functions = {}
for table in tables:
    crud_functions[table] = generate_crud(table)

add_product, get_all_products, update_product, delete_product = crud_functions["products"]
add_stock, get_all_stock, update_stock, delete_stock = crud_functions["stock"]
add_sale, get_all_sales, update_sale, delete_sale = crud_functions["sales"]
add_recharge, get_all_recharges, update_recharge, delete_recharge = crud_functions["recharge"]
add_expense, get_all_expenses, update_expense, delete_expense = crud_functions["expenses"]
add_expense_category, get_all_expense_categories, update_expense_category, delete_expense_category = crud_functions["expense_categories"]
add_due_payment, get_all_due_payment, update_due_payment, delete_due_payment = crud_functions["due_payment"]
add_due, get_all_due, update_due, delete_due = crud_functions["due"]
add_service_type, get_all_service_types, update_service_type, delete_service_type = crud_functions["service_types"]
add_service_request, get_all_service_requests, update_service_request, delete_service_request = crud_functions["service_requests"]
add_user, get_all_users, update_user, delete_user = crud_functions["users"]

# ---------------------------
# User helper
# ---------------------------
def update_user_info(user_id, username=None, password=None):
    data = {}
    if username:
        data["username"] = username
    if password:
        data["password"] = password
    if data:
        update_user(user_id, data)

# ---------------------------
# Safe fetch helpers
# ---------------------------
def safe_rows(rows, default_template):
    safe_list = []
    for r in rows:
        row_dict = dict(r)
        safe_row = {k: row_dict.get(k, default_template.get(k)) for k in default_template}
        safe_list.append(safe_row)
    return safe_list

def safe_get_all_products():
    defaults = {"id":None,"name":"","purchase_price":0,"sale_price":0,"stock":0,"code":"","created_at":"","updated_at":"","source":"","source_desc":""}
    return safe_rows(get_all_products(), defaults)

def safe_get_all_sales():
    defaults = {"id":None,"product_id":None,"quantity":0,"sale_price":0,"total":0,"date":"","discount":0,"tax":0,"total_after_discount_tax":0,"due_amount":0,"due_received_by":"","barcode":"","sold_by":"","invoice_no":""}
    return safe_rows(get_all_sales(), defaults)

def safe_get_all_due_payment():
    defaults = {"id":None,"customer":"","amount":0,"due_date":"","sale_id":None,"date":"","product_name":"","quantity":0}
    return safe_rows(get_all_due_payment(), defaults)

def safe_get_all_due():
    defaults = {"id":None,"customer":"","amount":0,"date":""}
    return safe_rows(get_all_due(), defaults)

def safe_get_all_service_requests():
    defaults = {"id":None,"service_type_id":None,"customer_name":"","details":"","status":"","price":0,"requested_at":"","payment_status":"Unpaid","due_amount":0,"attachment":"","completed_at":"","created_at":"","updated_at":""}
    return safe_rows(get_all_service_requests(), defaults)

# ---------------------------
# Sale + stock auto-sync
# ---------------------------
@db_retry
def record_sale_and_update_stock(product_id, quantity, sale_price, discount=0, tax=0, sold_by="", barcode="", invoice_no=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    product = next((p for p in safe_get_all_products() if p["id"] == product_id), None)
    if not product:
        raise ValueError("Product not found")
    total = sale_price * quantity
    total_after_discount_tax = total - discount + tax
    sale_id = add_sale(product_id=product_id, quantity=quantity, sale_price=sale_price, total=total, date=now,
                       discount=discount, tax=tax, total_after_discount_tax=total_after_discount_tax, due_amount=0,
                       due_received_by=None, barcode=barcode, sold_by=sold_by, invoice_no=invoice_no)
    new_stock = (product["stock"] or 0) - quantity
    update_product(product_id, stock=new_stock)
    add_stock(product_id=product_id, quantity=-quantity, added_date=now, entry_type='sale', location='main', note=f"Sold by {sold_by}")
    return sale_id

sale_and_stock_update = record_sale_and_update_stock

# ---------------------------
# Due sync from sales and service requests
# ---------------------------
def sync_due_from_sales_and_service():
    # Sales
    for s in safe_get_all_sales():
        if s["due_amount"] > 0:
            existing = [d for d in safe_get_all_due_payment() if d["sale_id"] == s["id"]]
            if not existing:
                product_name = next((p["name"] for p in safe_get_all_products() if p["id"] == s["product_id"]), "")
                add_due_payment(customer="", amount=s["due_amount"], due_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                sale_id=s["id"], product_name=product_name, quantity=s["quantity"])
    # Service Requests
    for sr in safe_get_all_service_requests():
        if sr["payment_status"].lower() != "paid" and sr["due_amount"] > 0:
            existing = [d for d in safe_get_all_due_payment() if d["sale_id"] == sr["id"]]
            if not existing:
                add_due_payment(customer=sr["customer_name"], amount=sr["due_amount"], due_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                sale_id=sr["id"], product_name="Service Request", quantity=1)

# ---------------------------
# Background due sync thread
# ---------------------------
def start_background_due_sync(interval_seconds=2):
    def run_sync():
        while True:
            try:
                sync_due_from_sales_and_service()
            except Exception as e:
                print(f"Background due sync error: {e}")
            time.sleep(interval_seconds)
    thread = threading.Thread(target=run_sync, daemon=True)
    thread.start()
