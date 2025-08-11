from db import get_connection
from datetime import datetime

def initialize_service_tables():
    """
    সার্ভিস সম্পর্কিত টেবিল তৈরি করবে যদি না থাকে:
    - service_types (সার্ভিসের ধরন)
    - service_requests (সার্ভিসের আবেদন/রিকোয়েস্ট)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_type_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            details TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            price REAL,
            requested_at TEXT NOT NULL,
            FOREIGN KEY (service_type_id) REFERENCES service_types(id)
        )
    ''')
    conn.commit()
    conn.close()

# ====== সার্ভিস টাইপ সম্পর্কিত CRUD ফাংশন ======

def add_service_type(name, description):
    """
    নতুন সার্ভিস টাইপ যোগ করবে
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO service_types (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
        return True
    except Exception as e:
        print("সার্ভিস টাইপ যোগে ত্রুটি:", e)
        return False
    finally:
        conn.close()

def get_all_service_types():
    """
    সকল সার্ভিস টাইপের তালিকা (id, name, description) রিটার্ন করবে
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description FROM service_types ORDER BY name')
    services = cursor.fetchall()
    conn.close()
    return services

def update_service_type(service_type_id, name, description):
    """
    নির্দিষ্ট সার্ভিস টাইপ আপডেট করবে
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE service_types SET name=?, description=? WHERE id=?', (name, description, service_type_id))
        conn.commit()
        return True
    except Exception as e:
        print("সার্ভিস টাইপ আপডেটে ত্রুটি:", e)
        return False
    finally:
        conn.close()

def delete_service_type(service_type_id):
    """
    নির্দিষ্ট সার্ভিস টাইপ মুছে ফেলবে
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM service_types WHERE id=?', (service_type_id,))
        conn.commit()
        return True
    except Exception as e:
        print("সার্ভিস টাইপ মুছতে সমস্যা:", e)
        return False
    finally:
        conn.close()

# ====== সার্ভিস রিকোয়েস্ট সম্পর্কিত CRUD ফাংশন ======

def add_service_request(service_type_id, customer_name, details, price):
    """
    নতুন সার্ভিস রিকোয়েস্ট যোগ করবে
    """
    conn = get_connection()
    cursor = conn.cursor()
    requested_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute('''
            INSERT INTO service_requests
            (service_type_id, customer_name, details, status, price, requested_at)
            VALUES (?, ?, ?, 'Pending', ?, ?)
        ''', (service_type_id, customer_name, details, price, requested_at))
        conn.commit()
        return True
    except Exception as e:
        print("সার্ভিস রিকোয়েস্ট যোগে ত্রুটি:", e)
        return False
    finally:
        conn.close()

def get_all_service_requests():
    """
    সকল সার্ভিস রিকোয়েস্টের তালিকা রিটার্ন করবে,
    সাথে সার্ভিস টাইপের নামও দেখাবে
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sr.id, st.name, sr.customer_name, sr.details, sr.status, sr.price, sr.requested_at
        FROM service_requests sr
        JOIN service_types st ON sr.service_type_id = st.id
        ORDER BY sr.requested_at DESC
    ''')
    requests = cursor.fetchall()
    conn.close()
    return requests

def update_service_request_status(request_id, new_status):
    """
    সার্ভিস রিকোয়েস্টের স্ট্যাটাস আপডেট করবে (Pending, Processing, Completed)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE service_requests SET status=? WHERE id=?', (new_status, request_id))
        conn.commit()
        return True
    except Exception as e:
        print("সার্ভিস রিকোয়েস্ট স্ট্যাটাস আপডেটে ত্রুটি:", e)
        return False
    finally:
        conn.close()

def delete_service_request(request_id):
    """
    সার্ভিস রিকোয়েস্ট মুছে ফেলবে
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM service_requests WHERE id=?', (request_id,))
        conn.commit()
        return True
    except Exception as e:
        print("সার্ভিস রিকোয়েস্ট মুছতে সমস্যা:", e)
        return False
    finally:
        conn.close()

# ====== টেস্ট রানের জন্য ইনিশিয়ালাইজ কল ======
if __name__ == "__main__":
    initialize_service_tables()
    print("✅ সার্ভিস সম্পর্কিত টেবিল সফলভাবে তৈরি হয়েছে।")
