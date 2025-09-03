from db import get_connection
from datetime import datetime

# ====== Expense Category Functions ======

def init_expense_tables():
    """
    খরচ সম্পর্কিত টেবিলগুলো তৈরি করবে (যদি আগে না থাকে)।
    """
    conn = get_connection()
    cur = conn.cursor()

    # Category table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expense_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    # Expense table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            amount REAL,
            description TEXT,
            expense_date TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (category_id) REFERENCES expense_categories(id)
        )
    """)

    conn.commit()
    conn.close()


def add_expense_category(name: str) -> bool:
    """
    নতুন খরচের ক্যাটাগরি যোগ করবে।
    """
    if not name.strip():
        print("ক্যাটাগরি নাম খালি হতে পারবে না।")
        return False
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO expense_categories (name) VALUES (?)", (name.strip(),))
        conn.commit()
        return True
    except Exception as e:
        print("ক্যাটাগরি যোগে ত্রুটি:", e)
        return False
    finally:
        conn.close()


def get_expense_categories():
    """
    সকল খরচের ক্যাটাগরি লিস্ট রিটার্ন করবে।
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM expense_categories ORDER BY name")
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print("ক্যাটাগরি লোডে ত্রুটি:", e)
        return []
    finally:
        conn.close()


# ====== Expense CRUD Functions ======

def add_expense(category_id: int, amount: float, description: str, expense_date: str) -> bool:
    """
    নতুন খরচ যোগ করবে।
    """
    if not category_id or amount <= 0:
        print("সঠিক ক্যাটাগরি এবং পরিমাণ দিতে হবে।")
        return False
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO expenses (category_id, amount, description, expense_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (category_id, amount, description.strip(), expense_date, now, now))
        conn.commit()
        return True
    except Exception as e:
        print("খরচ যোগে ত্রুটি:", e)
        return False
    finally:
        conn.close()


def get_all_expenses():
    """
    সকল খরচের তালিকা রিটার্ন করবে।
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT expenses.id, expense_categories.name, expenses.amount, expenses.description, expenses.expense_date
            FROM expenses
            LEFT JOIN expense_categories ON expenses.category_id = expense_categories.id
            ORDER BY expense_date DESC
        """)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print("খরচ লোডে ত্রুটি:", e)
        return []
    finally:
        conn.close()


def delete_expense(expense_id: int) -> bool:
    """
    নির্দিষ্ট খরচ ডিলিট করবে।
    """
    if not expense_id:
        print("সঠিক খরচ আইডি দিতে হবে।")
        return False
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        return True
    except Exception as e:
        print("খরচ ডিলিট করতে সমস্যা:", e)
        return False
    finally:
        conn.close()


def update_expense(expense_id: int, category_id: int, amount: float, description: str, expense_date: str) -> bool:
    """
    নির্দিষ্ট খরচ আপডেট করবে।
    """
    if not expense_id or not category_id or amount <= 0:
        print("সঠিক তথ্য দিতে হবে।")
        return False
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE expenses
            SET category_id=?, amount=?, description=?, expense_date=?, updated_at=?
            WHERE id=?
        """, (category_id, amount, description.strip(), expense_date, now, expense_id))
        conn.commit()
        return True
    except Exception as e:
        print("খরচ আপডেটে ত্রুটি:", e)
        return False
    finally:
        conn.close()
