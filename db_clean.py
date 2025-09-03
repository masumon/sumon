import sqlite3

conn = sqlite3.connect("database/smartshop.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM due_payment WHERE customer IS NULL OR customer='' OR customer='unknown'")
conn.commit()
conn.close()
print("Unknown due payments deleted.")
