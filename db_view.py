import sqlite3

# ডাটাবেস ফাইলের পাথ
DB_PATH = "database/smartshop.db"

def get_table_schemas(db_path):
    # ডাটাবেস কানেকশন
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # সব টেবিলের নাম নিন
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name_tuple in tables:
        table_name = table_name_tuple[0]
        print(f"\nTable: {table_name}")
        print("-" * (len(table_name) + 7))

        # টেবিলের কলাম তথ্য নিন
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        # Column info: (cid, name, type, notnull, dflt_value, pk)
        print(f"{'CID':<5} {'Name':<25} {'Type':<15} {'NotNull':<8} {'Default':<15} {'PK':<3}")
        print("-" * 80)
        for col in columns:
            cid, name, col_type, notnull, dflt_value, pk = col
            print(f"{cid:<5} {name:<25} {col_type:<15} {notnull:<8} {str(dflt_value):<15} {pk:<3}")

    conn.close()

if __name__ == "__main__":
    get_table_schemas(DB_PATH)
