from db import get_connection

# ====== Expense Report Functions ======

def get_expense_report_by_date(start_date, end_date):
    """
    প্রদত্ত তারিখের মধ্যে খরচের রিপোর্ট রিটার্ন করবে।
    
    :param start_date: 'YYYY-MM-DD' ফরম্যাটে শুরু তারিখ
    :param end_date: 'YYYY-MM-DD' ফরম্যাটে শেষ তারিখ
    :return: list of tuples [(category_name, total_amount), ...]
    """
    try:
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
        return rows
    except Exception as e:
        print("রিপোর্ট লোডে ত্রুটি:", e)
        return []
    finally:
        conn.close()

def get_total_expense_by_month(month):
    """
    প্রদত্ত মাসের মোট খরচ রিটার্ন করবে। উদাহরণ: month='2025-08'
    
    :param month: 'YYYY-MM' ফরম্যাটে মাস
    :return: float মোট খরচ
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) FROM expenses
            WHERE strftime('%Y-%m', expense_date) = ?
        """, (month,))
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0.0
    except Exception as e:
        print("মাস ভিত্তিক খরচ লোডে ত্রুটি:", e)
        return 0.0
    finally:
        conn.close()
