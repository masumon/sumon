import sqlite3
from datetime import datetime
from db import get_connection, db_retry

# -----------------
# রিপোর্টিং ফাংশন
# -----------------

@db_retry
def get_due_payments_report(start_date=None, end_date=None):
    """
    Central due_payment টেবিল থেকে Sales + Service dues রিপোর্ট।
    """
    conn = get_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()

    query = "SELECT id, customer, amount, due_date, sale_id, date FROM due_payment WHERE 1=1"
    params = []

    if start_date and end_date:
        query += " AND due_date BETWEEN ? AND ?"
        params = [start_date, end_date]
    elif start_date:
        query += " AND due_date >= ?"
        params = [start_date]
    elif end_date:
        query += " AND due_date <= ?"
        params = [end_date]

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        combined = []
        for row in rows:
            combined.append({
                "id": row['id'],
                "customer": row['customer'] if row['customer'] else "Unknown",
                "amount": row['amount'],
                "due_date": row['due_date'],
                "sale_id": row['sale_id'],
                "date": row['date']
            })

        return combined
    except sqlite3.Error as e:
        print(f"Error getting due payments report: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_monthly_due_summary(start_date=None, end_date=None):
    """
    নির্দিষ্ট সময়সীমার জন্য মাসিক বকেয়া পেমেন্টের সারাংশ প্রদান করে।
    """
    conn = get_connection()
    if not conn:
        print("Could not establish database connection for monthly summary.")
        return {}

    cursor = conn.cursor()
    
    query = "SELECT id, customer, amount, due_date, sale_id, date FROM due_payment WHERE 1=1"
    params = []

    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params = [start_date, end_date]

    summary = {
        'total_due': 0.0,
        'payments': [],
        'customers': {},
        'due_by_month': {}
    }

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        for row in rows:
            record = dict(row)
            try:
                # `due_date` ফাঁকা আছে কিনা এবং এর শেষে কোনো অতিরিক্ত স্পেস আছে কিনা তা পরীক্ষা করা
                due_date_str = record.get('due_date', '').strip()
                if not due_date_str:
                    print(f"Skipping record due to empty due_date: {record}")
                    continue

                # তারিখটিকে সঠিক ফরম্যাটে পার্স করা
                due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M:%S")
                month_key = due_date_obj.strftime("%Y-%m")
                
                # `amount` এর মান None হলে 0 হিসেবে বিবেচনা করা
                amount = float(record['amount']) if record['amount'] is not None else 0.0

                if month_key not in summary['due_by_month']:
                    summary['due_by_month'][month_key] = 0.0
                
                summary['due_by_month'][month_key] += amount
                summary['total_due'] += amount

                # কাস্টমার অনুযায়ী সারাংশ
                customer_name = record['customer'] if record['customer'] else 'Unknown'
                if customer_name not in summary['customers']:
                    summary['customers'][customer_name] = {'total_due': 0.0, 'dues': []}
                
                summary['customers'][customer_name]['total_due'] += amount
                summary['customers'][customer_name]['dues'].append({
                    'id': record['id'],
                    'amount': record['amount'],
                    'date': record['due_date']
                })
            
            except ValueError as e:
                # ত্রুটিপূর্ণ ডেটা রেকর্ড স্কিপ করা
                print(f"Error processing due record for monthly summary: {record}. Skipping. Error: {e}")
                continue

    except sqlite3.Error as e:
        print(f"Error executing monthly summary query: {e}")
    finally:
        if conn:
            conn.close()

    return summary
