from db import get_connection
from datetime import datetime

# ====== Expense Category CRUD Functions ======

def add_category(name):
    """
    নতুন খরচের ক্যাটেগরি যোগ করবে।
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO expense_categories (name, created_at, updated_at)
            VALUES (?, ?, ?)
        """, (name, now, now))
        conn.commit()
        return True
    except Exception as e:
        print("ক্যাটেগরি যোগে ত্রুটি:", e)
        return False
    finally:
        conn.close()

def get_all_categories():
    """
    সকল খরচের ক্যাটেগরির তালিকা রিটার্ন করবে।
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM expense_categories ORDER BY name")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print("ক্যাটেগরি লোডে ত্রুটি:", e)
        return []
    finally:
        conn.close()

def delete_category(category_id):
    """
    নির্দিষ্ট খরচের ক্যাটেগরি ডিলিট করবে।
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expense_categories WHERE id=?", (category_id,))
        conn.commit()
        return True
    except Exception as e:
        print("ক্যাটেগরি ডিলিট করতে সমস্যা:", e)
        return False
    finally:
        conn.close()
