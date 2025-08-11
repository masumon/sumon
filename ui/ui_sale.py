import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from product.product import get_product_list
from product.sale import record_sale, get_product_stock

from print.print_utils import print_receipt_pdf
from ui.ui_print_utils import PrintUI

class SaleUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.products = get_product_list()
        self.product_dict = {f"{p[1]} (ID: {p[0]})": p[0] for p in self.products}
        self.product_name_map = {p[0]: p[1] for p in self.products}

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="পণ্য নির্বাচন করুন:", font=("Helvetica", 12)).pack(pady=5)

        self.product_combo = ttk.Combobox(self, values=list(self.product_dict.keys()), state="readonly", width=35)
        self.product_combo.pack()
        self.product_combo.bind("<<ComboboxSelected>>", self.show_stock)

        self.stock_label = tk.Label(self, text="বর্তমান মজুদ: --", font=("Helvetica", 11, "bold"), fg="blue")
        self.stock_label.pack(pady=5)

        tk.Label(self, text="পরিমাণ:", font=("Helvetica", 12)).pack(pady=5)
        self.quantity_entry = tk.Entry(self)
        self.quantity_entry.pack()
        self.quantity_entry.bind("<KeyRelease>", self.update_total)

        tk.Label(self, text="বিক্রয় মূল্য (প্রতি ইউনিট):", font=("Helvetica", 12)).pack(pady=5)
        self.sale_price_entry = tk.Entry(self)
        self.sale_price_entry.pack()
        self.sale_price_entry.bind("<KeyRelease>", self.update_total)

        self.total_label = tk.Label(self, text="মোট: ০ টাকা", font=("Helvetica", 12, "bold"), fg="blue")
        self.total_label.pack(pady=5)

        self.sale_button = tk.Button(self, text="✅ বিক্রয় করুন", command=self.process_sale, bg="#4CAF50", fg="white", font=("Helvetica", 12))
        self.sale_button.pack(pady=10)

        self.message_label = tk.Label(self, text="", font=("Helvetica", 11), fg="blue")
        self.message_label.pack(pady=5)

    def show_stock(self, event=None):
        selected = self.product_combo.get()
        if selected:
            product_id = self.product_dict[selected]
            stock = get_product_stock(product_id)
            if stock is not None:
                self.stock_label.config(text=f"বর্তমান মজুদ: {stock}")

                if stock == 0:
                    self.sale_button.config(state="disabled")
                    messagebox.showwarning("স্টক শেষ", "এই পণ্যের মজুদ শেষ হয়েছে!")
                else:
                    self.sale_button.config(state="normal")

                if 0 < stock < 5:
                    messagebox.showinfo("স্টক সতর্কবার্তা", f"এই পণ্যের মজুদ খুব কম ({stock})")
            else:
                self.stock_label.config(text="বর্তমান মজুদ: --")
                self.sale_button.config(state="disabled")

    def update_total(self, event=None):
        quantity = self.quantity_entry.get()
        sale_price = self.sale_price_entry.get()

        try:
            q = int(quantity)
            p = float(sale_price)
            total = q * p
            self.total_label.config(text=f"মোট: {total:.2f} টাকা")
        except:
            self.total_label.config(text="মোট: ০ টাকা")

    def process_sale(self):
        selected = self.product_combo.get()
        if not selected:
            messagebox.showerror("ত্রুটি", "অনুগ্রহ করে একটি পণ্য নির্বাচন করুন।")
            return

        product_id = self.product_dict[selected]
        quantity = self.quantity_entry.get()
        sale_price = self.sale_price_entry.get()

        if not quantity.isdigit() or not sale_price.replace('.', '', 1).isdigit():
            messagebox.showerror("ত্রুটি", "পরিমাণ এবং বিক্রয় মূল্য সঠিকভাবে লিখুন।")
            return

        quantity = int(quantity)
        sale_price = float(sale_price)
        sale_date = datetime.now().strftime("%Y-%m-%d")

        current_stock = get_product_stock(product_id)
        if current_stock is None or current_stock < quantity:
            messagebox.showerror("স্টক সমস্যা", "পর্যাপ্ত মজুদ নেই।")
            return

        success = record_sale(product_id, quantity, sale_price, sale_date)

        if success:
            self.message_label.config(text="✅ বিক্রয় সফলভাবে সম্পন্ন হয়েছে!", fg="green")
            self.quantity_entry.delete(0, tk.END)
            self.sale_price_entry.delete(0, tk.END)
            self.total_label.config(text="মোট: ০ টাকা")
            # অটো স্টক রিফ্রেশ
            self.product_combo.set(selected)
            self.show_stock()

            product_name = self.product_name_map[product_id]
            total_price = quantity * sale_price

            pdf_path = print_receipt_pdf(
                product=product_name,
                quantity=quantity,
                unit_price=sale_price,
                total_price=total_price,
                sale_date=sale_date
            )

            PrintUI(self.master, pdf_path)

        else:
            self.message_label.config(text="❌ বিক্রয় ব্যর্থ হয়েছে। স্টক আছে কি পরীক্ষা করুন।", fg="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = SaleUI(root)
    root.mainloop()
