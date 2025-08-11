from db import get_connection

def add_updated_at_column_if_missing():
    conn = get_connection()
    cursor = conn.cursor()

    tables = [
        'users', 'products', 'stock', 'sales',
        'expense_categories', 'expenses', 'services',
        'recharges', 'barcodes'
    ]

    for table in tables:
        try:
            # প্রথমে চেক করি কলাম আছে কি না
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            if 'updated_at' not in columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN updated_at TEXT")
                print(f"'updated_at' কলাম {table} টেবিলে যোগ হয়েছে।")
            else:
                print(f"{table} টেবিলে ইতোমধ্যে 'updated_at' কলাম আছে।")
        except Exception as e:
            print(f"{table} টেবিলে কলাম যোগ করতে সমস্যা: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_updated_at_column_if_missing()
