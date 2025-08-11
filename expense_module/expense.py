from db import get_connection
from datetime import datetime

def add_expense(category_id, amount, description, expense_date):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO expenses (category_id, amount, description, expense_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (category_id, amount, description, expense_date, now, now))

    conn.commit()
    conn.close()

def get_all_expenses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT expenses.id, expense_categories.name, amount, description, expense_date
        FROM expenses
        LEFT JOIN expense_categories ON expenses.category_id = expense_categories.id
        ORDER BY expense_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()
