from add_operations import *

def test_users():
    print("\n=== Testing USERS ===")
    # Create
    create_user('testuser', 'password123', 'user')
    user = get_user_by_username('testuser')
    print("Created user:", user)

    # Read
    user_by_id = get_user_by_id(user[0])
    print("User by ID:", user_by_id)

    # Update
    update_user_role(user[0], 'admin')
    updated_user = get_user_by_id(user[0])
    print("Updated user role:", updated_user)

    # Delete
    delete_user(user[0])
    deleted_user = get_user_by_id(user[0])
    print("Deleted user (should be None):", deleted_user)

def test_products():
    print("\n=== Testing PRODUCTS ===")
    # Create
    create_product('Test Product', 100, 150, 10, 'Test Category')
    product = get_product_by_id(1)
    print("Created product:", product)

    # Update stock
    update_product_stock(product[0], 20)
    updated_product = get_product_by_id(product[0])
    print("Updated product stock:", updated_product)

    # Delete
    delete_product(product[0])
    deleted_product = get_product_by_id(product[0])
    print("Deleted product (should be None):", deleted_product)

def test_stock():
    print("\n=== Testing STOCK ===")
    create_product('StockTest', 50, 80, 5, 'Category1')
    product = get_product_by_id(2)
    add_stock(product[0], 10, '2025-08-08')
    stocks = get_stock_by_product(product[0])
    print("Added stock:", stocks)

    # Update stock quantity
    stock_id = stocks[0][0]
    update_stock_quantity(stock_id, 15)
    updated_stocks = get_stock_by_product(product[0])
    print("Updated stock quantity:", updated_stocks)

    # Delete stock
    delete_stock(stock_id)
    stocks_after_delete = get_stock_by_product(product[0])
    print("Stocks after delete:", stocks_after_delete)

    # Clean up product
    delete_product(product[0])

def run_tests():
    test_users()
    test_products()
    test_stock()
    print("\n✅ All CRUD tests completed!")

if __name__ == "__main__":
    run_tests()
