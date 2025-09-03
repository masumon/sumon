import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from product.stock import (
    add_stock,
    reduce_stock,
    update_stock_entry,
    delete_stock_entry,
    fetch_all_stock,
    get_stock_by_product,
    get_product_name,
    export_stock_to_excel,
    export_stock_to_pdf,
    update_stock_quantity
)
from product.product import get_all_products

class StockUI:
    def __init__(self, master):
        self.master = master
        # Create a dedicated container frame for this module
        self.frame = tb.Frame(master)

        title_label = tk.Label(self.frame, text="স্টক ব্যবস্থাপক", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        self.products = get_all_products()
        self.product_dict = {f"{p['name']} ({p['code']})": p['id'] for p in self.products}

        self.create_widgets()
        self.refresh_stock()

    def create_widgets(self):
        frame = tb.Frame(self.frame)
        frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tb.Label(frame, text="Search Product:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_entry = tb.Entry(frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_autocomplete())
        self.search_entry.bind("<Return>", self.select_autocomplete)

        self.listbox = tk.Listbox(frame, height=5)
        self.listbox.grid(row=1, column=1, sticky="we", padx=5)
        self.listbox.bind("<Double-1>", self.select_autocomplete)
        self.listbox.bind("<Return>", self.select_autocomplete)
        self.listbox.grid_remove()

        tb.Label(frame, text="পণ্য নির্বাচন করুন:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.product_combo = tb.Combobox(frame, values=list(self.product_dict.keys()))
        self.product_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tb.Label(frame, text="পরিমাণ:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.qty_entry = tb.Entry(frame)
        self.qty_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.btn_add = tb.Button(frame, text="স্টক যোগ করুন", bootstyle="success", command=self.add_stock)
        self.btn_add.grid(row=4, column=0, pady=5)
        self.btn_update = tb.Button(frame, text="স্টক আপডেট করুন", bootstyle="warning", command=self.update_stock)
        self.btn_update.grid(row=4, column=1, pady=5)
        self.btn_delete = tb.Button(frame, text="স্টক মুছুন", bootstyle="danger", command=self.delete_stock)
        self.btn_delete.grid(row=4, column=2, pady=5)
        self.btn_refresh = tb.Button(frame, text="রিফ্রেশ", bootstyle="info", command=self.refresh_stock)
        self.btn_refresh.grid(row=4, column=3, pady=5)

        self.btn_excel = tb.Button(frame, text="Export Excel", bootstyle="secondary", command=self.export_excel)
        self.btn_excel.grid(row=5, column=0, pady=5)
        self.btn_pdf = tb.Button(frame, text="Export PDF", bootstyle="secondary", command=self.export_pdf)
        self.btn_pdf.grid(row=5, column=1, pady=5)

        tree_frame = tb.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.columns = ("id","product_name","quantity","added_date","entry_type","note")
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120, stretch=True)

        self.v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self.on_double_click)

    def update_autocomplete(self):
        query = self.search_entry.get().lower()
        matches = [name for name in self.product_dict.keys() if query in name.lower()]
        if matches:
            self.listbox.delete(0, tk.END)
            for m in matches:
                self.listbox.insert(tk.END, m)
            self.listbox.grid()
        else:
            self.listbox.grid_remove()
        self.filter_stock(query)

    def select_autocomplete(self, event=None):
        if self.listbox.size() == 0:
            return
        selection = self.listbox.get(tk.ACTIVE)
        self.product_combo.set(selection)
        self.listbox.grid_remove()
        self.search_entry.delete(0, tk.END)
        self.filter_stock()

    def add_stock(self):
        product_name = self.product_combo.get()
        product_id = self.product_dict.get(product_name)
        qty = self.qty_entry.get().strip()
        if not qty.isdigit() or int(qty)<=0:
            messagebox.showerror("ত্রুটি", "সঠিক পরিমাণ লিখুন")
            return
        success, message = add_stock(product_id, int(qty))
        if success:
            messagebox.showinfo("সফল", message)
            self.refresh_stock()
        else:
            messagebox.showerror("ত্রুটি", message)

    def update_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("ত্রুটি", "একটি স্টক সিলেক্ট করুন")
            return
        stock_id = self.tree.item(selected[0])['values'][0]
        qty = self.qty_entry.get().strip()
        if not qty.isdigit() or int(qty)<0:
            messagebox.showerror("ত্রুটি", "সঠিক পরিমাণ লিখুন")
            return
        success, message = update_stock_entry(stock_id, int(qty))
        if success:
            messagebox.showinfo("সফল", message)
            self.refresh_stock()
        else:
            messagebox.showerror("ত্রুটি", message)

    def delete_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("ত্রুটি", "একটি স্টক সিলেক্ট করুন")
            return
        stock_id = self.tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("নিশ্চিতকরণ", "আপনি কি সত্যিই এই স্টক মুছে ফেলতে চান?")
        if confirm:
            success, message = delete_stock_entry(stock_id)
            if success:
                messagebox.showinfo("সফল", message)
                self.refresh_stock()
            else:
                messagebox.showerror("ত্রুটি", message)

    def refresh_stock(self):
        self.all_rows = fetch_all_stock()
        self.filter_stock()

    def filter_stock(self, query=None):
        if query is None:
            query = self.search_entry.get().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in self.all_rows:
            product_name = get_product_name(r.get("product_id", ""))
            if query in product_name.lower():
                self.tree.insert(
                    "", tk.END,
                    values=(
                        r.get("id", ""),
                        product_name,
                        r.get("quantity", ""),
                        r.get("added_date", ""),
                        r.get("entry_type", ""),
                        r.get("note", "")
                    )
                )

    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item_id or column not in ("#3","#6"):
            return

        x, y, width, height = self.tree.bbox(item_id, column)
        value = self.tree.set(item_id, column)
        self.edit_box = tk.Entry(self.tree)
        self.edit_box.place(x=x, y=y, width=width, height=height)
        self.edit_box.insert(0, value)
        self.edit_box.focus()

        def save_edit(event):
            new_value = self.edit_box.get()
            if column=="#3" and (not new_value.isdigit() or int(new_value)<0):
                messagebox.showerror("ত্রুটি", "সঠিক পরিমাণ লিখুন")
                return
            stock_id = self.tree.item(item_id)["values"][0]
            if column=="#3":
                update_stock_entry(stock_id, int(new_value))
            elif column=="#6":
                update_stock_entry(stock_id, note=new_value)
            self.edit_box.destroy()
            self.refresh_stock()

        self.edit_box.bind("<Return>", save_edit)
        self.edit_box.bind("<FocusOut>", lambda e: self.edit_box.destroy())

    def export_excel(self):
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if file:
            success = export_stock_to_excel(file)
            if success:
                messagebox.showinfo("সফল", f"Excel export সম্পন্ন: {file}")
            else:
                messagebox.showerror("ত্রুটি", "Export ব্যর্থ হয়েছে")

    def export_pdf(self):
        file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
        if file:
            success = export_stock_to_pdf(file)
            if success:
                messagebox.showinfo("সফল", f"PDF export সম্পন্ন: {file}")
            else:
                messagebox.showerror("ত্রুটি", "Export ব্যর্থ হয়েছে")


if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app = StockUI(root)
    root.mainloop()
