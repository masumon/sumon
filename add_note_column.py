import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3

def add_note_column_to_stock(db_path="database/smartshop.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE stock ADD COLUMN note TEXT")
        print("✅ 'note' কলাম সফলভাবে stock টেবিলে যুক্ত হয়েছে।")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️ 'note' কলাম ইতিমধ্যে stock টেবিলে রয়েছে।")
        else:
            print("❌ ত্রুটি:", e)
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    add_note_column_to_stock()
