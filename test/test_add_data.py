# test/test_add_data.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_connection

def insert_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    # ➤ User
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                   ('admin', 'admin123', 'admin'))

    # ➤ Product
    cursor.execute("INSERT INTO products (name, purchase_price, sale_price, stock, category) VALUES (?, ?, ?, ?, ?)", 
                   ('Samsung Galaxy A10', 12000, 14000, 10, 'Mobile'))

    # ➤ Stock
    cursor.execute("INSERT INTO stock (product_id, quantity, added_date) VALUES (?, ?, ?)",
                   (1, 10, '2025-08-08'))

    # ➤ Sale
    cursor.execute("INSERT INTO sales (product_id, quantity, sale_price, total, sale_date) VALUES (?, ?, ?, ?, ?)",
                   (1, 2, 14000, 28000, '2025-08-08'))

    # ➤ Expense Category
    cursor.execute("INSERT INTO expense_categories (name) VALUES (?)", ('Electricity',))

    # ➤ Expense
    cursor.execute("INSERT INTO expenses (category_id, amount, expense_date, description) VALUES (?, ?, ?, ?)",
                   (1, 500, '2025-08-08', 'Monthly electricity bill'))

    # ➤ Service
    cursor.execute("INSERT INTO services (name, description, price) VALUES (?, ?, ?)",
                   ('Mobile Repair', 'Screen replacement', 800))

    # ➤ Recharge
    cursor.execute("INSERT INTO recharges (mobile_number, amount, recharge_date) VALUES (?, ?, ?)",
                   ('01710000000', 100, '2025-08-08'))

    # ➤ Barcode
    cursor.execute("INSERT INTO barcodes (product_id, barcode) VALUES (?, ?)",
                   (1, '123456789012'))

    # ➤ Purchase
    cursor.execute("INSERT INTO purchase (product_id, quantity, purchase_price, supplier, notes) VALUES (?, ?, ?, ?, ?)",
                   (1, 5, 11500, 'Samsung Dealer', 'Extra stock'))

    conn.commit()
    conn.close()
    print("✅ Sample data inserted successfully!")

if __name__ == "__main__":
    insert_sample_data()
