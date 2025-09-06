# report/report.py

import sqlite3
import os
from datetime import datetime
from db import get_connection

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "smartshop.db")

# ---------------- Sales Report ----------------
def get_sales_report():
    """
    Sales রিপোর্ট। সকল sales ডাটা।
    """
    try:
        from product.product import get_product_name
        conn = get_connection()
        if not conn:
            return []
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, product_id, quantity, sale_price, total, date, discount, tax, total_after_discount_tax, due_amount, sold_by
            FROM sales
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        sales = []
        for r in rows:
            sales.append({
                "id": r["id"],
                "product": get_product_name(r["product_id"]),
                "quantity": r["quantity"],
                "sale_price": r["sale_price"],
                "total": r["total"],
                "date": r["date"],
                "discount": r["discount"],
                "tax": r["tax"],
                "total_after_discount_tax": r["total_after_discount_tax"],
                "due_amount": r["due_amount"],
                "sold_by": r["sold_by"],
            })
        return sales
    except Exception as e:
        print("Error in get_sales_report:", e)
        return []
    finally:
        if conn:
            conn.close()

# ---------------- Sales Report by Date ----------------
def get_sales_report_by_date(start_date, end_date):
    """
    start_date, end_date: 'YYYY-MM-DD' ফরম্যাট
    """
    try:
        conn = get_connection()
        if not conn:
            return []
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, product_id, quantity, sale_price, total, date, discount, tax, total_after_discount_tax, due_amount, sold_by
            FROM sales
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        """, (start_date, end_date))
        rows = cursor.fetchall()
        sales = []
        for r in rows:
            sales.append({
                "id": r["id"],
                "product_id": r["product_id"],
                "quantity": r["quantity"],
                "sale_price": r["sale_price"],
                "total": r["total"],
                "date": r["date"],
                "discount": r["discount"],
                "tax": r["tax"],
                "total_after_discount_tax": r["total_after_discount_tax"],
                "due_amount": r["due_amount"],
                "sold_by": r["sold_by"],
            })
        return sales
    except Exception as e:
        print("Error in get_sales_report_by_date:", e)
        return []
    finally:
        if conn:
            conn.close()

# ---------------- Monthly Profit Report ----------------
def get_monthly_profit_report(month, year):
    """
    মাসিক profit রিপোর্ট।
    month: int 1-12
    year: int
    """
    try:
        conn = get_connection()
        if not conn:
            return {"total_sales": 0, "profit": 0}
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(total_after_discount_tax) as total_sales,
                   SUM(total_after_discount_tax - (quantity * sale_price)) as profit
            FROM sales
            WHERE strftime('%Y', date)=? AND strftime('%m', date)=?
        """, (str(year), f"{month:02d}"))
        row = cursor.fetchone()
        return {
            "total_sales": row["total_sales"] or 0,
            "profit": row["profit"] or 0
        }
    except Exception as e:
        print("Error in get_monthly_profit_report:", e)
        return {"total_sales": 0, "profit": 0}
    finally:
        if conn:
            conn.close()

# ---------------- Due Report ----------------
def get_due_report():
    """
    Due রিপোর্ট। central due_payment table থেকে।
    Duplicate safe.
    """
    try:
        conn = get_connection()
        if not conn:
            return []
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, customer, amount, due_date, sale_id, date
            FROM due_payment
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        seen = set()
        dues = []
        for r in rows:
            key = (r["customer"] or "Unknown", r["sale_id"], r["due_date"])
            if key in seen:
                continue
            seen.add(key)
            dues.append({
                "id": r["id"],
                "customer": r["customer"] or "Unknown",
                "amount": r["amount"],
                "due_date": r["due_date"],
                "sale_id": r["sale_id"],
                "date": r["date"],
            })
        return dues
    except Exception as e:
        print("Error in get_due_report:", e)
        return []
    finally:
        if conn:
            conn.close()

# ---------------- Due Report by Date ----------------
def get_due_report_by_date(start_date, end_date):
    """
    start_date, end_date: 'YYYY-MM-DD' ফরম্যাট
    Duplicate safe.
    """
    try:
        conn = get_connection()
        if not conn:
            return []
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, customer, amount, due_date, sale_id, date
            FROM due_payment
            WHERE due_date BETWEEN ? AND ?
            ORDER BY due_date DESC
        """, (start_date, end_date))
        rows = cursor.fetchall()
        seen = set()
        dues = []
        for r in rows:
            key = (r["customer"] or "Unknown", r["sale_id"], r["due_date"])
            if key in seen:
                continue
            seen.add(key)
            dues.append({
                "id": r["id"],
                "customer": r["customer"] or "Unknown",
                "amount": r["amount"],
                "due_date": r["due_date"],
                "sale_id": r["sale_id"],
                "date": r["date"]
            })
        return dues
    except Exception as e:
        print("Error in get_due_report_by_date:", e)
        return []
    finally:
        if conn:
            conn.close()

# ---------------- Customer Due Summary ----------------
def get_customer_due_summary(customer_name):
    """
    নির্দিষ্ট কাস্টমারের Sales + Service dues summary।
    """
    try:
        conn = get_connection()
        if not conn:
            return {"total_due":0, "total_sales_due":0, "total_service_due":0}
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(amount) FROM due_payment WHERE customer=?", (customer_name,))
        total_due = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM due_payment WHERE customer=? AND sale_id IS NOT NULL", (customer_name,))
        total_sales_due = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM due_payment WHERE customer=? AND sale_id IS NULL", (customer_name,))
        total_service_due = cursor.fetchone()[0] or 0

        return {
            "total_due": total_due,
            "total_sales_due": total_sales_due,
            "total_service_due": total_service_due
        }
    except Exception as e:
        print("Error in get_customer_due_summary:", e)
        return {
            "total_due": 0,
            "total_sales_due": 0,
            "total_service_due": 0
        }
    finally:
        if conn:
            conn.close()
