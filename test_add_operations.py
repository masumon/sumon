import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from add_operations import *

def test_users():
    print("\n==== Testing USERS ====")
    # আগের testuser থাকলে ডিলিট করে নিন
    user = get_user_by_username('testuser')
    if user:
        delete_user(user[0])
        print("Previous test user deleted.")
    time.sleep(0.1)

    try:
        create_user('testuser', 'password123', 'admin')
        print("User created.")
    except Exception as e:
        print("User creation failed:", e)
    
    user = get_user_by_username('testuser')
    print("User fetched by username:", user)
    if user:
        user_by_id = get_user_by_id(user[0])
        print("User fetched by id:", user_by_id)

def test_products():
    print("\n==== Testing PRODUCTS ====")
    # আগের test product থাকলে ডিলিট করে নিন
    product = get_product_by_id(1)
    if product:
        delete_product(product[0])
        print("Previous test product deleted.")
    time.sleep(0.1)

    try:
        create_product('Mobile Phone', 10000.0, 12000.0, 50, 'Electronics')
        print("Product created.")
    except Exception as e:
        print("Product creation failed:", e)
    time.sleep(0.1)

    product = get_product_by_id(1)
    print("Product fetched:", product)

def test_stock():
    print("\n==== Testing STOCK ====")
    # আগের test product থাকলে ডিলিট করে নিন
    product = get_product_by_id(2)
    if product:
        delete_product(product[0])
        print("Previous test product deleted.")
    time.sleep(0.1)

    try:
        create_product('Headphones', 1500.0, 2000.0, 20, 'Electronics')
        print("Product created for stock test.")
    except Exception as e:
        print("Product creation failed:", e)
    time.sleep(0.1)
    
    product = get_product_by_id(2)
    print("Product fetched for stock test:", product)
    
    if product:
        try:
            add_stock(product[0], 10, '2025-08-08')
            print("Stock added.")
        except Exception as e:
            print("Adding stock failed:", e)
    time.sleep(0.1)

    stocks = get_stock_by_product(product[0])
    print("Stocks fetched:", stocks)

def run_all_tests():
    test_users()
    test_products()
    test_stock()

if __name__ == '__main__':
    run_all_tests()
