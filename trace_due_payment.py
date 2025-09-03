import sqlite3
from db import get_connection

def clean_duplicate_due_payments():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Step 1: Fetch all due_payment entries grouped by sale_id and customer
        cursor.execute("""
            SELECT sale_id, customer, COUNT(*) as count
            FROM due_payment
            GROUP BY sale_id, customer
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()

        for sale_id, customer, count in duplicates:
            print(f"[CLEANING DUPLICATE] Sale ID {sale_id}, Customer: {customer}, Count: {count}")
            # Keep the earliest entry, delete the rest
            cursor.execute("""
                DELETE FROM due_payment
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM due_payment
                    WHERE sale_id=? AND customer=?
                ) AND sale_id=? AND customer=?
            """, (sale_id, customer, sale_id, customer))
            conn.commit()

        # Step 2: Fix entries where customer='Unknown' but due_received_by is not empty
        cursor.execute("""
            SELECT dp.id, dp.sale_id, dp.customer, dp.amount, s.due_received_by
            FROM due_payment dp
            JOIN sales s ON dp.sale_id = s.id
            WHERE dp.customer='Unknown' AND s.due_received_by != ''
        """)
        mismatched = cursor.fetchall()

        for dp_id, sale_id, customer, amount, due_received_by in mismatched:
            print(f"[FIXING UNKNOWN] Updating due_payment id {dp_id} for Sale ID {sale_id} to customer='{due_received_by}'")
            cursor.execute("""
                UPDATE due_payment
                SET customer=?
                WHERE id=?
            """, (due_received_by, dp_id))
            conn.commit()

        print("Duplicate and mismatched due_payment entries cleaned successfully.")

    finally:
        conn.close()

if __name__ == "__main__":
    clean_duplicate_due_payments()
