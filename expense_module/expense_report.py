from db import get_connection

def get_expense_report_by_date(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT expense_categories.name, SUM(amount)
        FROM expenses
        LEFT JOIN expense_categories ON expenses.category_id = expense_categories.id
        WHERE expense_date BETWEEN ? AND ?
        GROUP BY expense_categories.name
    """, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_total_expense_by_month(month):  # example input: '2025-08'
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(amount) FROM expenses
        WHERE strftime('%Y-%m', expense_date) = ?
    """, (month,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0.0
