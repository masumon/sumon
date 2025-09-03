import sqlite3
import os
import time
from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk, messagebox

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
        if not isinstance(data_dict, dict):
            raise ValueError("Data must be a dictionary or keyword arguments")

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
        if not isinstance(data_dict, dict):
            raise ValueError("Data must be a dictionary or keyword arguments")

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
    "products", "stock", "sales", "recharge",
    "expenses", "expense_categories",
    "due_payment", "due",
    "service_types", "service_requests",
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
    defaults = {"id":None, "name":"", "purchase_price":0, "sale_price":0, "stock":0, "code":"", "created_at":"", "updated_at":"", "source":"", "source_desc":""}
    return safe_rows(get_all_products(), defaults)

def safe_get_all_sales():
    defaults = {"id":None,"product_id":None,"quantity":0,"sale_price":0,"total":0,"date":"","discount":0,"tax":0,"total_after_discount_tax":0,"due_amount":0,"due_received_by":"","barcode":"","sold_by":"","invoice_no":""}
    return safe_rows(get_all_sales(), defaults)

def safe_get_all_recharges():
    defaults = {"id":None,"customer_name":"","mobile":"","operator":"","amount":0,"date":""}
    return safe_rows(get_all_recharges(), defaults)

def safe_get_all_expenses():
    defaults = {"id":None,"category_id":None,"amount":0,"date":"","note":""}
    return safe_rows(get_all_expenses(), defaults)

def safe_get_all_due_payment():
    defaults = {"id":None,"customer":"","amount":0,"due_date":"","sale_id":None,"date":"","product_name":"","quantity":0}
    return safe_rows(get_all_due_payment(), defaults)

def safe_get_all_due():
    defaults = {"id":None,"customer":"","amount":0,"date":""}
    return safe_rows(get_all_due(), defaults)

def safe_get_all_stock():
    defaults = {"id":None,"product_id":None,"quantity":0,"added_date":"","entry_type":"","location":"","note":"","created_at":""}
    return safe_rows(get_all_stock(), defaults)

def safe_get_all_service_types():
    defaults = {"id":None,"name":"","description":"","category":"","is_active":1,"created_at":"","updated_at":""}
    return safe_rows(get_all_service_types(), defaults)

def safe_get_all_service_requests():
    defaults = {"id":None,"service_type_id":None,"customer_name":"","details":"","status":"","price":0,"requested_at":"","payment_status":"Unpaid","due_amount":0,"attachment":"","completed_at":"","created_at":"","updated_at":""}
    return safe_rows(get_all_service_requests(), defaults)

def safe_get_all_users():
    defaults = {"id":None,"username":"","password":"","role":"user","created_at":""}
    return safe_rows(get_all_users(), defaults)

# ---------------------------
# Enhanced data retrieval for UI
# ---------------------------
@db_retry
def get_recent_sales_with_product_info():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                s.id,
                s.date,
                s.total_after_discount_tax AS total,
                s.due_amount,
                p.name AS product_name,
                s.quantity
            FROM sales s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.date DESC
        """)
        return cursor.fetchall()

@db_retry
def get_due_payments_with_product_info():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                dp.id,
                dp.customer,
                dp.amount,
                dp.due_date,
                dp.product_name,
                dp.quantity,
                s.invoice_no
            FROM due_payment dp
            LEFT JOIN sales s ON dp.sale_id = s.id
            ORDER BY dp.date DESC
        """)
        return cursor.fetchall()

# ---------------------------
# Sale + stock auto-sync
# ---------------------------
@db_retry
def record_sale_and_update_stock(
    product_id, quantity, sale_price,
    discount=0, tax=0, sold_by="",
    barcode="", invoice_no=None, **kwargs
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    product = [p for p in safe_get_all_products() if p["id"] == product_id]
    if not product:
        raise ValueError("Product not found")
    product = product[0]

    total = sale_price * quantity
    total_after_discount_tax = total - discount + tax

    sale_id = add_sale(
        product_id=product_id,
        quantity=quantity,
        sale_price=sale_price,
        total=total,
        date=now,
        discount=discount,
        tax=tax,
        total_after_discount_tax=total_after_discount_tax,
        due_amount=0,
        due_received_by=None,
        barcode=barcode,
        sold_by=sold_by,
        invoice_no=invoice_no
    )

    new_stock = (product["stock"] or 0) - quantity
    update_product(product_id, stock=new_stock)
    add_stock(
        product_id=product_id,
        quantity=-quantity,
        added_date=now,
        entry_type='sale',
        location='main',
        note=f"Sold by {sold_by}"
    )

    return sale_id

sale_and_stock_update = record_sale_and_update_stock

# ---------------------------
# Validation helpers
# ---------------------------
def validate_product_data(**kwargs):
    if 'name' in kwargs and not kwargs['name'].strip():
        raise ValueError("Product name cannot be empty")
    if 'sale_price' in kwargs and kwargs['sale_price'] < 0:
        raise ValueError("Sale price cannot be negative")
    if 'stock' in kwargs and kwargs['stock'] < 0:
        raise ValueError("Stock cannot be negative")
    return True

def validate_sale_data(**kwargs):
    if 'quantity' in kwargs and kwargs['quantity'] <= 0:
        raise ValueError("Quantity must be positive")
    if 'sale_price' in kwargs and kwargs['sale_price'] < 0:
        raise ValueError("Sale price cannot be negative")
    return True

def add_product_with_validation(**kwargs):
    validate_product_data(**kwargs)
    return add_product(**kwargs)

def add_sale_with_validation(**kwargs):
    validate_sale_data(**kwargs)
    return add_sale(**kwargs)

@db_retry
def update_user_info(user_id, username=None, password=None):
    kwargs = {}
    if username:
        kwargs["username"] = username
    if password:
        kwargs["password"] = password
    if kwargs:
        update_user(user_id, **kwargs)

@db_retry
def create_indexes():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_code ON products(code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales(product_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_product_id ON stock(product_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_date ON stock(added_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category_id)")
        conn.commit()

# ---------------------------
# Auto-refresh helper
# ---------------------------
class AutoRefresh:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.callbacks = []
        self._stop_event = threading.Event()
        self._thread = None

    def add_callback(self, func):
        if callable(func):
            self.callbacks.append(func)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def _run(self):
        while not self._stop_event.is_set():
            for cb in self.callbacks:
                try:
                    cb()
                except Exception as e:
                    print(f"[AutoRefresh error] {e}")
            time.sleep(self.interval)

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()

# ---------------------------
# UI Demo
# ---------------------------
class SmartShopUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SmartShop POS Demo")
        self.geometry("1000x600")

        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill="both")

        self.products_tab = ttk.Frame(self.tab_control)
        self.sales_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.products_tab, text="Products")
        self.tab_control.add(self.sales_tab, text="Sales")

        self.setup_products_tab()
        self.setup_sales_tab()
        
        self.cart_items = {}
        self.customer_var = tk.StringVar(value="")
        self.paid_var = tk.DoubleVar(value=0.0)
        self.cart_total_var = tk.DoubleVar(value=0.0)
        
        # We will keep the reference to the original function for comparison if needed
        self.finalize_sale = self.finalize_sale_updated
        
        self.auto_refresh = AutoRefresh(interval=2)
        self.auto_refresh.add_callback(self.refresh_products_tree)
        self.auto_refresh.add_callback(self.refresh_sales_tree)
        self.auto_refresh.start()

    def setup_products_tab(self):
        frm = ttk.Frame(self.products_tab)
        frm.pack(padx=10, pady=10, fill="x")

        ttk.Label(frm, text="Name:").grid(row=0, column=0)
        self.entry_product_name = ttk.Entry(frm)
        self.entry_product_name.grid(row=0, column=1)

        ttk.Label(frm, text="Price:").grid(row=0, column=2)
        self.entry_product_price = ttk.Entry(frm)
        self.entry_product_price.grid(row=0, column=3)

        ttk.Label(frm, text="Stock:").grid(row=0, column=4)
        self.entry_product_stock = ttk.Entry(frm)
        self.entry_product_stock.grid(row=0, column=5)

        ttk.Button(frm, text="Add Product", command=self.add_product_ui).grid(row=0, column=6, padx=10)

        self.tree_products = ttk.Treeview(self.products_tab, columns=("ID","Name","Price","Stock"), show="headings")
        self.tree_products.heading("ID", text="ID")
        self.tree_products.heading("Name", text="Name")
        self.tree_products.heading("Price", text="Price")
        self.tree_products.heading("Stock", text="Stock")
        self.tree_products.pack(fill="both", expand=True)

        self.refresh_products_tree()

    def add_product_ui(self):
        try:
            name = self.entry_product_name.get().strip()
            price = float(self.entry_product_price.get())
            stock = int(self.entry_product_stock.get())
            add_product_with_validation(name=name, sale_price=price, stock=stock)
            messagebox.showinfo("Success","Product added")
            self.entry_product_name.delete(0, tk.END)
            self.entry_product_price.delete(0, tk.END)
            self.entry_product_stock.delete(0, tk.END)
            self.refresh_products_tree()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_products_tree(self):
        for row in self.tree_products.get_children():
            self.tree_products.delete(row)
        for p in safe_get_all_products():
            self.tree_products.insert("", tk.END, values=(p["id"],p["name"],p["sale_price"],p["stock"]))

    def setup_sales_tab(self):
        frm = ttk.Frame(self.sales_tab)
        frm.pack(padx=10, pady=10, fill="x")

        ttk.Label(frm, text="Product ID:").grid(row=0, column=0)
        self.entry_sale_product_id = ttk.Entry(frm)
        self.entry_sale_product_id.grid(row=0, column=1)

        ttk.Label(frm, text="Quantity:").grid(row=0, column=2)
        self.entry_sale_qty = ttk.Entry(frm)
        self.entry_sale_qty.grid(row=0, column=3)

        ttk.Label(frm, text="Sale Price:").grid(row=0, column=4)
        self.entry_sale_price = ttk.Entry(frm)
        self.entry_sale_price.grid(row=0, column=5)
        
        ttk.Label(frm, text="Customer:").grid(row=1, column=0)
        self.entry_customer = ttk.Entry(frm, textvariable=self.customer_var)
        self.entry_customer.grid(row=1, column=1)
        
        ttk.Label(frm, text="Paid Amount:").grid(row=1, column=2)
        self.entry_paid = ttk.Entry(frm, textvariable=self.paid_var)
        self.entry_paid.grid(row=1, column=3)

        ttk.Button(frm, text="Record Sale", command=self.add_sale_to_cart).grid(row=0, column=6, padx=10)
        ttk.Button(frm, text="Finalize Sale", command=self.finalize_sale).grid(row=1, column=6, padx=10)

        self.tree_sales = ttk.Treeview(self.sales_tab, columns=("ID","Product ID","Qty","Price","Total","Date"), show="headings")
        self.tree_sales.heading("ID", text="ID")
        self.tree_sales.heading("Product ID", text="Product ID")
        self.tree_sales.heading("Qty", text="Qty")
        self.tree_sales.heading("Price", text="Price")
        self.tree_sales.heading("Total", text="Total")
        self.tree_sales.heading("Date", text="Date")
        self.tree_sales.pack(fill="both", expand=True)

        self.refresh_sales_tree()

    def add_sale_to_cart(self):
        try:
            product_id = int(self.entry_sale_product_id.get())
            qty = int(self.entry_sale_qty.get())
            price = float(self.entry_sale_price.get())
            
            if product_id not in self.cart_items:
                self.cart_items[product_id] = {"quantity": 0, "unit_price": price, "discount": 0.0}
            self.cart_items[product_id]["quantity"] += qty
            self.cart_total_var.set(self.cart_total_var.get() + (qty * price))
            
            messagebox.showinfo("Success", "Product added to cart.")
            self.entry_sale_product_id.delete(0, tk.END)
            self.entry_sale_qty.delete(0, tk.END)
            self.entry_sale_price.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def finalize_sale_updated(self, event=None):
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
            
        seller = "DemoUser"
        customer = self.customer_var.get().strip()
        paid_amount = self.paid_var.get()
        cart_total = self.cart_total_var.get()
        
        try:
            total_due_for_sale = max(0.0, cart_total - paid_amount)
            first_sale_id = None
            all_products = safe_get_all_products()
            product_names = []
            total_quantity = 0
            
            for pid, item in self.cart_items.items():
                qty = item["quantity"]
                unit_price = item["unit_price"]
                discount = item["discount"]
                
                # Fetch product name for the due payment record
                product_name = next((p["name"] for p in all_products if p["id"] == pid), "Unknown Product")
                product_names.append(f"{product_name} ({qty})")
                total_quantity += qty
                
                sale_id = sale_and_stock_update(
                    product_id=pid,
                    quantity=qty,
                    sale_price=unit_price,
                    discount=discount,
                    sold_by=seller
                )
                
                if first_sale_id is None:
                    first_sale_id = sale_id
            
            # Record a single due payment for the entire sale
            if total_due_for_sale > 0 and customer:
                add_due_payment(
                    customer=customer,
                    amount=total_due_for_sale,
                    due_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    sale_id=first_sale_id,
                    product_name=", ".join(product_names), # Update: Pass product names
                    quantity=total_quantity # Update: Pass total quantity
                )
            
            messagebox.showinfo("Success", f"বিক্রয় সম্পন্ন হয়েছে। মোট: {cart_total:.2f} ৳। বাকি: {total_due_for_sale:.2f} ৳")
            self.cart_items = {}
            self.cart_total_var.set(0.0)
            self.customer_var.set("")
            self.paid_var.set(0.0)
            self.refresh_sales_tree()
            self.refresh_products_tree()
        
        except Exception as e:
            messagebox.showerror("Error", f"বিক্রয় সম্পন্ন হয়নি:\n{e}")

    def refresh_sales_tree(self):
        for row in self.tree_sales.get_children():
            self.tree_sales.delete(row)
        for s in safe_get_all_sales():
            self.tree_sales.insert("", tk.END, values=(s["id"],s["product_id"],s["quantity"],s["sale_price"],s["total"],s["date"]))

# ---------------------------
# Main
# ---------------------------
if __name__=="__main__":
    init_all_tables()
    create_indexes()
    app = SmartShopUI()
    app.mainloop()
