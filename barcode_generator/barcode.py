import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import barcode
from barcode.writer import ImageWriter

# ফাইলের ডিরেক্টরি
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# generated_barcodes ফোল্ডারের পূর্ণ path
SAVE_DIR = os.path.join(BASE_DIR, "generated_barcodes")

# যদি ফোল্ডারটি না থাকে তাহলে তৈরি করো
os.makedirs(SAVE_DIR, exist_ok=True)

def generate_barcode(data: str, filename: str = None) -> str:
    """
    বারকোড তৈরি করে generated_barcodes ফোল্ডারে সেভ করে। 

    :param data: যেকোনো স্ট্রিং ডেটা (যেমন: product id)
    :param filename: সেভ করার জন্য ফাইল নাম (এক্সটেনশন ছাড়া)
                     যদি None হয়, data ব্যবহার হবে ফাইলনাম হিসেবে
    :return: সেভ করা ফাইলের পূর্ণ path
    """
    if filename is None:
        # unsafe char replace
        filename = "".join(c for c in data if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not filename:
            filename = "barcode"

    barcode_class = barcode.get_barcode_class('code128')
    barcode_obj = barcode_class(data, writer=ImageWriter())

    save_path = os.path.join(SAVE_DIR, filename)

    try:
        final_path = barcode_obj.save(save_path)
        print(f"✅ বারকোড সেভ হয়েছে এখানে: {final_path}")
        return final_path
    except Exception as e:
        print(f"❌ বারকোড সেভ করতে সমস্যা: {e}")
        return ""

# generate_barcode এর আলিয়াস
def generate_barcode_image(data: str, filename: str = None) -> str:
    return generate_barcode(data, filename)
