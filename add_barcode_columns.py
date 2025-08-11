import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3

# ডাটাবেজের অবস্থান
DB_PATH = "database/smartshop.db"

def add_barcode_column(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # barcode কলাম যুক্ত করার চেষ্টা
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN barcode TEXT")
        print(f"✅ '{table_name}' টেবিলে 'barcode' কলাম সফলভাবে যুক্ত হয়েছে।")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"⚠️ '{table_name}' টেবিলে 'barcode' কলাম ইতিমধ্যে আছে।")
        else:
            print(f"❌ '{table_name}' টেবিলে ত্রুটি: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # দুইটি টেবিলে barcode কলাম যুক্ত করা হবে
    add_barcode_column("products")
    add_barcode_column("sales")
