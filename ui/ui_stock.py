import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk, messagebox
from product.stock import add_stock, get_all_stock
from product.product import get_all_products
from datetime import datetime

class StockUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.product_list = get_all_products()
        self.product_dict = {p[1]: p[0] for p in self.product_list}

        tk.Label(self, text="পণ্য নির্বাচন করুন:", font=('Arial', 12)).pack(pady=5)
        self.product_combobox = ttk.Combobox(self, values=list(self.product_dict.keys()), font=('Arial', 12), width=40)
        self.product_combobox.pack(pady=5)

        tk.Label(self, text="পরিমাণ যোগ করুন:", font=('Arial', 12)).pack(pady=5)
        self.quantity_entry = tk.Entry(self, font=('Arial', 12), width=20)
        self.quantity_entry.pack(pady=5)

        tk.Button(self, text="স্টকে যোগ করুন", command=self.add_stock_entry, font=('Arial', 12), bg="green", fg="white").pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("id", "product_id", "quantity", "added_date", "entry_type", "location", "note"), show="headings", height=10)
        headings = {
            "id": "আইডি",
            "product_id": "পণ্য আইডি",
            "quantity": "পরিমাণ",
            "added_date": "তারিখ",
            "entry_type": "ধরণ",
            "location": "লোকেশন",
            "note": "নোট"
        }
        for col, label in headings.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.load_all_stock()

    def add_stock_entry(self):
        product_name = self.product_combobox.get()
        quantity = self.quantity_entry.get()

        if not product_name or not quantity.isdigit():
            messagebox.showerror("ত্রুটি", "সঠিক পণ্য এবং পরিমাণ লিখুন!")
            return

        product_id = self.product_dict[product_name]
        quantity = int(quantity)
        added_date = datetime.now().strftime("%Y-%m-%d")

        success = add_stock(product_id, quantity, added_date)

        if success:
            messagebox.showinfo("সফল", "স্টকে সফলভাবে যোগ হয়েছে!")
            self.quantity_entry.delete(0, tk.END)
            self.load_all_stock()
        else:
            messagebox.showerror("ব্যর্থ", "স্টকে যোগ করা যায়নি।")

    def load_all_stock(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        stocks = get_all_stock()
        for s in stocks:
            self.tree.insert("", tk.END, values=s)


if __name__ == "__main__":
    root = tk.Tk()
    app = StockUI(root)
    root.mainloop()
