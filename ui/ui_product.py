import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import messagebox, ttk
from product import add_product, get_all_products, update_product

class ProductUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="#f9f9f9")
        self.pack(fill="both", expand=True)

        self.create_widgets()
        self.load_products()

    def create_widgets(self):
        # লেবেল ও ইনপুট ফিল্ডস
        form_frame = tk.Frame(self, bg="#f9f9f9")
        form_frame.pack(fill="x", padx=10, pady=10)

        # নাম
        tk.Label(form_frame, text="নাম:", bg="#f9f9f9").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_name = tk.Entry(form_frame)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        # ক্রয় মূল্য
        tk.Label(form_frame, text="ক্রয় মূল্য:", bg="#f9f9f9").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_purchase_price = tk.Entry(form_frame)
        self.entry_purchase_price.grid(row=1, column=1, padx=5, pady=5)

        # বিক্রয় মূল্য
        tk.Label(form_frame, text="বিক্রয় মূল্য:", bg="#f9f9f9").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_sale_price = tk.Entry(form_frame)
        self.entry_sale_price.grid(row=2, column=1, padx=5, pady=5)

        # মজুদ
        tk.Label(form_frame, text="মজুদ:", bg="#f9f9f9").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.entry_stock = tk.Entry(form_frame)
        self.entry_stock.grid(row=3, column=1, padx=5, pady=5)

        # ক্যাটেগরি
        tk.Label(form_frame, text="ক্যাটেগরি:", bg="#f9f9f9").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.entry_category = tk.Entry(form_frame)
        self.entry_category.grid(row=4, column=1, padx=5, pady=5)

        # বারকোড
        tk.Label(form_frame, text="বারকোড:", bg="#f9f9f9").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.entry_barcode = tk.Entry(form_frame)
        self.entry_barcode.grid(row=5, column=1, padx=5, pady=5)

        # বোতাম ফ্রেম
        btn_frame = tk.Frame(self, bg="#f9f9f9")
        btn_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_frame, text="➕ পণ্য যোগ করুন", command=self.add_product).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔄 তালিকা রিফ্রেশ করুন", command=self.load_products).pack(side="left", padx=5)

        # টেবিল ফ্রেম
        table_frame = tk.Frame(self, bg="#f9f9f9")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("আইডি", "নাম", "ক্রয় মূল্য", "বিক্রয় মূল্য", "মজুদ", "ক্যাটেগরি", "বারকোড")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)

    def add_product(self):
        name = self.entry_name.get().strip()
        purchase_price = self.entry_purchase_price.get().strip()
        sale_price = self.entry_sale_price.get().strip()
        stock = self.entry_stock.get().strip()
        category = self.entry_category.get().strip()
        barcode = self.entry_barcode.get().strip()

        if not name or not purchase_price or not sale_price:
            messagebox.showerror("ত্রুটি", "নাম, ক্রয় মূল্য ও বিক্রয় মূল্য আবশ্যক।")
            return

        try:
            purchase_price = float(purchase_price)
            sale_price = float(sale_price)
            stock = int(stock) if stock else 0
        except ValueError:
            messagebox.showerror("ত্রুটি", "দাম ও মজুদের ঘরে সঠিক সংখ্যা দিন।")
            return

        success = add_product(name, purchase_price, sale_price, stock, category, barcode)
        if success:
            messagebox.showinfo("সফল", "✅ পণ্য সফলভাবে যোগ হয়েছে!")
            self.clear_form()
            self.load_products()
        else:
            messagebox.showerror("ব্যর্থ", "❌ পণ্য যোগ করা যায়নি!")

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_purchase_price.delete(0, tk.END)
        self.entry_sale_price.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)
        self.entry_category.delete(0, tk.END)
        self.entry_barcode.delete(0, tk.END)

    def load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        products = get_all_products()
        for p in products:
            self.tree.insert('', tk.END, values=p)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("📦 পণ্যের মডিউল - SmartShop POS")
    root.geometry("800x500")
    app = ProductUI(root)
    root.mainloop()
