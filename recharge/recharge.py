from db import get_connection
from datetime import datetime
from typing import List, Tuple, Optional

# ========== রিচার্জ সম্পর্কিত টেবিল তৈরি ==========
def initialize_recharge_tables() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recharges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile_number TEXT NOT NULL,
            operator_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            recharge_date TEXT NOT NULL,
            FOREIGN KEY (operator_id) REFERENCES operators(id)
        )
    ''')

    conn.commit()
    conn.close()

# ========== অপারেটর ফিচার ==========
def add_operator(name: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO operators (name) VALUES (?)', (name,))
        conn.commit()
        return True
    except Exception as e:
        print("অপারেটর যোগে ত্রুটি:", e)
        return False
    finally:
        conn.close()

def get_all_operators() -> List[Tuple[int, str]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM operators ORDER BY name')
    operators = cursor.fetchall()
    conn.close()
    return operators

def update_operator(operator_id: int, name: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE operators SET name=? WHERE id=?', (name, operator_id))
        conn.commit()
        return True
    except Exception as e:
        print("অপারেটর আপডেটে ত্রুটি:", e)
        return False
    finally:
        conn.close()

def delete_operator(operator_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM operators WHERE id=?', (operator_id,))
        conn.commit()
        return True
    except Exception as e:
        print("অপারেটর মুছতে সমস্যা:", e)
        return False
    finally:
        conn.close()

# ========== রিচার্জ ফিচার ==========
def add_recharge(mobile_number: str, operator_id: int, amount: float) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    recharge_date = datetime.now().strftime("%Y-%m-%d")
    try:
        cursor.execute('''
            INSERT INTO recharges
            (mobile_number, operator_id, amount, recharge_date)
            VALUES (?, ?, ?, ?)
        ''', (mobile_number, operator_id, amount, recharge_date))
        conn.commit()
        return True
    except Exception as e:
        print("রিচার্জ যোগে ত্রুটি:", e)
        return False
    finally:
        conn.close()

def get_all_recharges() -> List[Tuple]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, r.mobile_number, o.name, r.amount, r.recharge_date
        FROM recharges r
        JOIN operators o ON r.operator_id = o.id
        ORDER BY r.recharge_date DESC
    ''')
    recharges = cursor.fetchall()
    conn.close()
    return recharges

def update_recharge(
    recharge_id: int,
    mobile_number: Optional[str] = None,
    operator_id: Optional[int] = None,
    amount: Optional[float] = None
) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    if mobile_number is not None:
        fields.append('mobile_number=?')
        values.append(mobile_number)
    if operator_id is not None:
        fields.append('operator_id=?')
        values.append(operator_id)
    if amount is not None:
        fields.append('amount=?')
        values.append(amount)

    if not fields:
        return False

    values.append(recharge_id)

    try:
        query = f"UPDATE recharges SET {', '.join(fields)} WHERE id=?"
        cursor.execute(query, tuple(values))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("রিচার্জ আপডেটে ত্রুটি:", e)
        return False
    finally:
        conn.close()

def delete_recharge(recharge_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM recharges WHERE id=?', (recharge_id,))
        conn.commit()
        return True
    except Exception as e:
        print("রিচার্জ মুছতে সমস্যা:", e)
        return False
    finally:
        conn.close()

# ========== রিপোর্ট ফিচার ==========
def get_daily_total_recharge(date_str: str) -> float:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount) FROM recharges WHERE recharge_date=?', (date_str,))
    total = cursor.fetchone()[0]
    conn.close()
    return total or 0.0

def get_daily_recharge_by_operator(date_str: str) -> List[Tuple[str, float]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.name, SUM(r.amount)
        FROM recharges r
        JOIN operators o ON r.operator_id = o.id
        WHERE r.recharge_date=?
        GROUP BY o.name
    ''', (date_str,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_monthly_total_recharge(year_month: str) -> float:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(amount) FROM recharges
        WHERE recharge_date LIKE ?
    ''', (year_month + '%',))
    total = cursor.fetchone()[0]
    conn.close()
    return total or 0.0


if __name__ == "__main__":
    initialize_recharge_tables()
    print("✅ রিচার্জ টেবিল সফলভাবে তৈরি হয়েছে।")
