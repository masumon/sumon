import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
from db import get_connection

def get_sales_report_by_date(start_date, end_date):
    """
    নির্দিষ্ট তারিখের মধ্যে বিক্রয়ের রিপোর্ট রিটার্ন করে।
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT s.id, s.product_id, p.name, s.quantity, s.sale_price, s.total, s.sale_date
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE DATE(s.sale_date) BETWEEN DATE(?) AND DATE(?)
            ORDER BY s.sale_date ASC
        """

        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()

        report = []
        for row in rows:
            report.append({
                'sale_id': row[0],
                'product_id': row[1],
                'product_name': row[2],
                'quantity': row[3],
                'unit_price': row[4],
                'total_price': row[5],
                'sale_date': row[6]
            })
        return report

    except sqlite3.Error as e:
        raise Exception(f"ডাটাবেজ এরর: {e}")
    except Exception as e:
        raise Exception(f"অপ্রত্যাশিত ত্রুটি: {e}")
    finally:
        if conn:
            conn.close()

def get_monthly_profit_report(month, year):
    """
    নির্দিষ্ট মাস ও বছরে লাভ রিপোর্ট রিটার্ন করে।
    """
    conn = None
    try:
        month = int(month)
        year = int(year)
        if not (1 <= month <= 12):
            raise ValueError("মাস অবশ্যই ১ থেকে ১২ এর মধ্যে হতে হবে।")

        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT s.product_id, p.name, s.quantity, s.sale_price, p.purchase_price, s.total, s.sale_date
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE strftime('%m', s.sale_date) = ? AND strftime('%Y', s.sale_date) = ?
            ORDER BY s.sale_date ASC
        """

        cursor.execute(query, (f"{month:02}", str(year)))
        rows = cursor.fetchall()

        total_buy = 0
        total_sell = 0
        report = []

        for row in rows:
            product_id, product_name, quantity, sale_price, purchase_price, total_price, sale_date = row

            total_buy += purchase_price * quantity
            total_sell += total_price

            report.append({
                'product_id': product_id,
                'product_name': product_name,
                'quantity': quantity,
                'purchase_price': purchase_price,
                'sale_price': sale_price,
                'total_sell': total_price,
                'sale_date': sale_date,
                'profit': (sale_price - purchase_price) * quantity
            })

        total_profit = total_sell - total_buy

        return {
            'details': report,
            'total_buy': total_buy,
            'total_sell': total_sell,
            'total_profit': total_profit
        }

    except sqlite3.Error as e:
        raise Exception(f"ডাটাবেজ এরর: {e}")
    except ValueError as e:
        raise Exception(f"ইনপুট এরর: {e}")
    except Exception as e:
        raise Exception(f"অপ্রত্যাশিত ত্রুটি: {e}")
    finally:
        if conn:
            conn.close()
