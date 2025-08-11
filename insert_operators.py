import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3

DB_PATH = "database/smartshop.db"

# বাংলাদেশে প্রধান মোবাইল ও ফিনান্সিয়াল অপারেটর নাম (বাংলায়)
operators = [
    "গ্রামীণফোন",
    "রবি",
    "বাংলালিংক",
    "এয়ারটেল",
    "টেলিটক",
    "বিকাশ",
    "নগদ",
    "রকেট",
    "আপে"
]

def insert_operators():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for name in operators:
        try:
            cursor.execute("""
                INSERT INTO operators (name)
                VALUES (?)
            """, (name,))
        except sqlite3.IntegrityError:
            # যদি অপারেটর নাম আগে থেকেই থাকে, তাহলে এড়িয়ে যাবে
            pass

    conn.commit()
    conn.close()
    print("✅ অপারেটর নামগুলো বাংলায় সফলভাবে যুক্ত হয়েছে।")

if __name__ == "__main__":
    insert_operators()
