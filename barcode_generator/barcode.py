import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import barcode
from barcode.writer import ImageWriter

# এই ফাইলের ডিরেক্টরি (অর্থাৎ barcode.py যেখানে আছে)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# generated_barcodes ফোল্ডারের পূর্ণ path
SAVE_DIR = os.path.join(BASE_DIR, "generated_barcodes")

# যদি ফোল্ডারটি না থাকে তাহলে তৈরি করো
os.makedirs(SAVE_DIR, exist_ok=True)

def generate_barcode(data, filename="barcode"):
    """
    বারকোড তৈরি করে barcode_generator/generated_barcodes ফোল্ডারে সেভ করে।
    
    :param data: যেকোনো স্ট্রিং ডেটা (যেমন: product id)
    :param filename: সেভ করার জন্য ফাইল নাম (এক্সটেনশন ছাড়াই)
    :return: সেভ করা ফাইলের পূর্ণ path
    """
    # Code128 বারকোড ক্লাস ব্যবহার
    barcode_class = barcode.get_barcode_class('code128')
    barcode_obj = barcode_class(data, writer=ImageWriter())
    
    # ফাইল সেভের সম্পূর্ণ পাথ
    save_path = os.path.join(SAVE_DIR, filename)
    
    # বারকোড সেভ (ex: test_barcode.png)
    final_path = barcode_obj.save(save_path)
    
    print(f"✅ বারকোড সেভ হয়েছে এখানে: {final_path}")
    return final_path

# নতুন ফাংশন: generate_barcode_image (অ্যালিয়াস)
def generate_barcode_image(data, filename="barcode"):
    """
    generate_barcode ফাংশনের আলিয়াস,
    backward compatibility এর জন্য।
    """
    return generate_barcode(data, filename)
