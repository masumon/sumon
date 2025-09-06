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
def add_due_source_column_if_not_exists():
    """
    Checks if the 'source' column exists in the 'due' table and adds it if it doesn't.
    This ensures backward compatibility for existing databases.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(due)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'source' not in columns:
            print("Adding 'source' column to 'due' table...")
            cursor.execute("ALTER TABLE due ADD COLUMN source TEXT")
            conn.commit()

@db_retry
def update_db_schema():
    """
    Updates the database schema by adding new columns to existing tables.
    This ensures the database is compatible with new features without a full reset.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Add new columns to 'due_payment' table
        cursor.execute("PRAGMA table_info(due_payment)")
        due_payment_cols = [col[1] for col in cursor.fetchall()]
        if 'balance_due' not in due_payment_cols:
            cursor.execute("ALTER TABLE due_payment ADD COLUMN balance_due REAL DEFAULT 0")
        if 'payment_method' not in due_payment_cols:
            cursor.execute("ALTER TABLE due_payment ADD COLUMN payment_method TEXT")
        if 'invoice_no' not in due_payment_cols:
            cursor.execute("ALTER TABLE due_payment ADD COLUMN invoice_no TEXT")

        # Add new columns to 'sales' table
        cursor.execute("PRAGMA table_info(sales)")
        sales_cols = [col[1] for col in cursor.fetchall()]
        if 'payment_method' not in sales_cols:
            cursor.execute("ALTER TABLE sales ADD COLUMN payment_method TEXT")
        if 'txn_id' not in sales_cols:
            cursor.execute("ALTER TABLE sales ADD COLUMN txn_id TEXT")
        if 'mobile_no' not in sales_cols:
            cursor.execute("ALTER TABLE sales ADD COLUMN mobile_no TEXT")
        
        # Add new columns to 'service_requests' table
        cursor.execute("PRAGMA table_info(service_requests)")
        service_requests_cols = [col[1] for col in cursor.fetchall()]
        if 'customer_mobile_no' not in service_requests_cols:
            cursor.execute("ALTER TABLE service_requests ADD COLUMN customer_mobile_no TEXT")
        
        conn.commit()

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
                customer_name TEXT,
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
                source TEXT,
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
        
        # Ensure 'source' column exists in 'due' table
        add_due_source_column_if_not_exists()
        
        # Update other table schemas with new columns
        update_db_schema()

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
    defaults = {"id":None,"product_id":None,"quantity":0,"sale_price":0,"total":0,"date":"","discount":0,"tax":0,"total_after_discount_tax":0,"due_amount":0,"due_received_by":"","barcode":"","sold_by":"","invoice_no":"","customer_name":""}
    return safe_rows(get_all_sales(), defaults)

def safe_get_all_due_payment():
    defaults = {"id":None,"customer":"","amount":0,"due_date":"","sale_id":None,"date":"","product_name":"","quantity":0}
    return safe_rows(get_all_due_payment(), defaults)

def safe_get_all_due():
    defaults = {"id":None,"customer":"","amount":0,"source":"", "date":""}
    return safe_rows(get_all_due(), defaults)

def safe_get_all_service_requests():
    defaults = {"id":None,"service_type_id":None,"customer_name":"","details":"","status":"","price":0,"requested_at":"","payment_status":"Unpaid","due_amount":0,"attachment":"","completed_at":"","created_at":"","updated_at":""}
    return safe_rows(get_all_service_requests(), defaults)

# ---------------------------
# Sale + stock auto-sync
# ---------------------------
@db_retry
def record_sale_and_update_stock(product_list, total_price, discount, due_amount, due_received_by, seller_name, customer_name, payment_method, txn_id=None, mobile_no=None):
    """
    Records a complete sale and updates product stock in a single transaction.
    
    Args:
        product_list (dict): Dictionary of products sold, e.g., {product_id: {'quantity': 1, ...}}
        total_price (float): The total price of the entire sale.
        discount (float): Total discount for the sale.
        due_amount (float): The remaining due amount.
        due_received_by (str): The name of the person who owes the due amount.
        seller_name (str): The name of the seller.
        customer_name (str): The name of the customer.
        payment_method (str): The payment method used.
        txn_id (str, optional): Transaction ID for wallet payments.
        mobile_no (str, optional): Mobile number for wallet payments.
    """
    conn = get_connection()
    if not conn:
        raise Exception("Database connection failed.")

    try:
        with conn:
            cursor = conn.cursor()
            
            # Use a single invoice number for the entire transaction
            invoice_no = datetime.now().strftime("INV-%Y%m%d%H%M%S")
            
            for product_id, item in product_list.items():
                quantity = item["quantity"]
                unit_price = item["unit_price"]
                item_discount = item.get("discount", 0)
                item_total = max(0, quantity * unit_price - item_discount)
                
                # Check current stock before sale
                cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
                current_stock = cursor.fetchone()[0]
                if current_stock < quantity:
                    raise ValueError(f"Not enough stock for product ID {product_id}. Available: {current_stock}, Requested: {quantity}")

                # Insert sale record for each product item
                cursor.execute("""
                    INSERT INTO sales (
                        product_id, quantity, sale_price, total, discount, due_amount,
                        due_received_by, sold_by, customer_name, invoice_no, payment_method, txn_id, mobile_no
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id,
                    quantity,
                    unit_price,
                    item_total,
                    item_discount,
                    due_amount if len(product_list) == 1 else 0, # Only set due_amount on a single-item sale for simplicity
                    due_received_by if due_amount > 0 and len(product_list) == 1 else None,
                    seller_name,
                    customer_name,
                    invoice_no,
                    payment_method,
                    txn_id,
                    mobile_no
                ))
                
                # Update product stock
                cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
            
            # Insert due payment record if there is a due amount
            if due_amount > 0:
                cursor.execute("""
                    INSERT INTO due_payment (customer, amount, date, due_date, balance_due, payment_method, invoice_no)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer_name,
                    due_amount,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    datetime.now().strftime("%Y-%m-%d"), # Assuming due date is same as sale date
                    total_price - due_amount,
                    payment_method,
                    invoice_no
                ))
            
            # Record recharge or other payment info if necessary
            if payment_method in ["নগদ", "রকেট", "বিকাশ"] and txn_id and mobile_no:
                # Add a record to a "payments" or "recharge" table
                # For now, we'll assume a record can be added to the recharge table
                cursor.execute("""
                    INSERT INTO recharge (customer_name, mobile, operator, amount)
                    VALUES (?, ?, ?, ?)
                """, (customer_name, mobile_no, payment_method, total_price - due_amount))

            conn.commit()
            return True

    except Exception as e:
        conn.rollback()
        raise e

sale_and_stock_update = record_sale_and_update_stock

# ---------------------------
# Consolidated Due Sync
# ---------------------------
@db_retry
def sync_all_dues_to_main_table():
    """
    Consolidates due amounts from sales and service requests into the `due` table.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Clear the main `due` table to prepare for fresh data
        cursor.execute("DELETE FROM due")

        # 2. Get consolidated due amounts from `sales` table
        cursor.execute("""
            SELECT customer_name, SUM(due_amount) as total_due
            FROM sales
            WHERE due_amount > 0
            GROUP BY customer_name
        """)
        sales_dues = cursor.fetchall()

        # 3. Get consolidated due amounts from `service_requests` table
        cursor.execute("""
            SELECT customer_name, SUM(due_amount) as total_due
            FROM service_requests
            WHERE due_amount > 0
            GROUP BY customer_name
        """)
        service_dues = cursor.fetchall()

        # 4. Merge the results and insert into `due` table with source info
        for row in sales_dues:
            customer = row["customer_name"]
            amount = row["total_due"]
            if amount > 0:
                cursor.execute("""
                    INSERT INTO due (customer, amount, source, date)
                    VALUES (?, ?, ?, ?)
                """, (customer, amount, 'বিক্রয়', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        for row in service_dues:
            customer = row["customer_name"]
            amount = row["total_due"]
            if amount > 0:
                cursor.execute("""
                    INSERT INTO due (customer, amount, source, date)
                    VALUES (?, ?, ?, ?)
                """, (customer, amount, 'সেবা অনুরোধ', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()

# ---------------------------
# Background due sync thread
# ---------------------------
def start_background_due_sync(interval_seconds=2):
    def run_sync():
        while True:
            try:
                sync_all_dues_to_main_table()
            except Exception as e:
                print(f"Background due sync error: {e}")
            time.sleep(interval_seconds)
    thread = threading.Thread(target=run_sync, daemon=True)
    thread.start()
