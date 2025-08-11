# init_db.py

from db import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')

    # PRODUCTS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        purchase_price REAL DEFAULT 0,
        sale_price REAL DEFAULT 0,
        stock INTEGER DEFAULT 0,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')

    # STOCK
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        added_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    ''')

    # SALES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        sale_price REAL,
        total REAL,
        sale_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    ''')

    # EXPENSE CATEGORIES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expense_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')

    # EXPENSES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        amount REAL NOT NULL,
        expense_date TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY(category_id) REFERENCES expense_categories(id)
    )
    ''')

    # SERVICES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')

    # RECHARGES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recharges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile_number TEXT NOT NULL,
        amount REAL NOT NULL,
        recharge_date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')

    # BARCODES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS barcodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        barcode TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    ''')

    # PURCHASE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchase (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        purchase_price REAL NOT NULL,
        supplier TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    create_tables()
