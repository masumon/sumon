from db import get_connection
from datetime import datetime

def add_category(name):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO expense_categories (name, created_at, updated_at)
            VALUES (?, ?, ?)
        """, (name, now, now))
        conn.commit()
    except Exception as e:
        print("Error adding category:", e)
    finally:
        conn.close()

def get_all_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM expense_categories ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_category(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expense_categories WHERE id=?", (category_id,))
    conn.commit()
    conn.close()
