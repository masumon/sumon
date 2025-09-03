import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from product.product import (
    add_product,
    get_all_products,
    update_product,
    delete_product,
    get_product_stock,
    get_product_sale_price,
)

# ---------------- UI ক্লাস ----------------
class ProductUI(ttk.Frame):
    """পণ্য ব্যবস্থাপনা UI"""
    SOURCES = ["লোকাল বাজার", "সরবরাহকারী", "অনলাইন ক্রয়", "বিক্রেতা", "অন্যান্য"]
    PAGE_SIZE = 20

    def __init__(self, master=None):
        super().__init__(master)
        self.frame = self  # Add frame attribute for compatibility
        self.pack(fill="both", expand=True)
        self.selected_product_id = None
        self.current_page = 0
        self.products_cache = []
        self.create_widgets()
        self.load_products()

    # ===== UI Widget তৈরি =====
    def create_widgets(self):
        # সার্চ ফ্রেম
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text="খুঁজুন:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", padx=5)
        ttk.Button(search_frame, text="খুঁজুন", bootstyle="info", command=self.search_products).pack(side="left", padx=5)
        ttk.Button(search_frame, text="রিফ্রেশ", bootstyle="secondary", command=self.load_products).pack(side="left", padx=5)

        # ফর্ম ফ্রেম
        form_frame = ttk.Labelframe(self, text="পণ্যের বিস্তারিত", padding=(10, 10))
        form_frame.pack(fill="x", padx=10, pady=5)
        labels = ["নাম", "ক্রয়মূল্য", "বিক্রয়মূল্য", "স্টক", "কোড", "ক্রয় উৎস", "অন্যান্য বিবরণ"]
        for idx, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=idx//3, column=(idx%3)*2, padx=5, pady=5, sticky="w")
        self.name_var = tk.StringVar()
        self.purchase_var = tk.StringVar()
        self.sale_var = tk.StringVar()
        self.stock_var = tk.StringVar()
        self.code_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.source_desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.purchase_var).grid(row=0, column=3, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.sale_var).grid(row=0, column=5, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.stock_var).grid(row=1, column=1, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.code_var).grid(row=1, column=3, padx=5, pady=5)
        self.source_dropdown = ttk.Combobox(form_frame, values=self.SOURCES, textvariable=self.source_var, state="readonly")
        self.source_dropdown.grid(row=1, column=5, padx=5, pady=5)
        self.source_dropdown.set(self.SOURCES[0])
        self.source_dropdown.bind("<<ComboboxSelected>>", self.on_source_change)
        self.source_desc_entry = ttk.Entry(form_frame, textvariable=self.source_desc_var, state="disabled")
        self.source_desc_entry.grid(row=2, column=1, columnspan=5, sticky="we", padx=5, pady=5)

        # বোতাম ফ্রেম
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=6, pady=10)
        ttk.Button(btn_frame, text="পণ্য যোগ করুন", bootstyle="success", command=self.add_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="পণ্য হালনাগাদ করুন", bootstyle="primary", command=self.update_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="পণ্য মুছে ফেলুন", bootstyle="danger", command=self.delete_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="ফর্ম পরিষ্কার করুন", bootstyle="secondary", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Export Excel", bootstyle="info", command=self.export_excel).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Export PDF", bootstyle="info", command=self.export_pdf).pack(side="left", padx=5)

        # Treeview with scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        columns = ("id", "name", "purchase_price", "sale_price", "stock", "code", "source", "source_desc", "created_at", "updated_at")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        column_widths = {
            "id": 50, "name": 150, "purchase_price": 80, "sale_price": 80, "stock": 60,
            "code": 80, "source": 100, "source_desc": 200, "created_at": 120, "updated_at": 120
        }
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center", stretch=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    # ===== বাকি ফাংশন =====
    def on_source_change(self, event=None):
        if self.source_var.get() == "অন্যান্য":
            self.source_desc_entry.config(state="normal")
        else:
            self.source_desc_entry.config(state="disabled")
            self.source_desc_var.set("")

    def load_products(self):
        products = get_all_products()
        self.products_cache = [
            (
                p["id"],
                p["name"],
                p.get("purchase_price", 0),
                p.get("sale_price", 0),
                p.get("stock", 0),
                p.get("code", ""),
                p.get("source", ""),
                p.get("source_desc", ""),
                p.get("created_at", ""),
                p.get("updated_at", "")
            )
            for p in products
        ]
        self.current_page = 0
        self.display_page()

    def display_page(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        start = self.current_page * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        for p in self.products_cache[start:end]:
            iid = self.tree.insert("", "end", values=p)
            if int(p[4]) < 5:
                self.tree.item(iid, tags=("low",))
            elif int(p[4]) < 10:
                self.tree.item(iid, tags=("medium",))
            else:
                self.tree.item(iid, tags=("high",))
        self.tree.tag_configure("low", background="#FFCCCC")
        self.tree.tag_configure("medium", background="#FFF2CC")
        self.tree.tag_configure("high", background="#CCFFCC")

    def search_products(self):
        query = self.search_var.get().strip().lower()
        filtered = [p for p in self.products_cache if query in p[1].lower() or query in str(p[5]).lower() or query in str(p[6]).lower() or query in str(p[7]).lower()]
        self.products_cache = filtered
        self.current_page = 0
        self.display_page()

    def clear_form(self):
        self.selected_product_id = None
        self.name_var.set("")
        self.purchase_var.set("")
        self.sale_var.set("")
        self.stock_var.set("")
        self.code_var.set("")
        self.source_var.set(self.SOURCES[0])
        self.source_desc_var.set("")
        self.source_desc_entry.config(state="disabled")

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            self.selected_product_id = values[0]
            self.name_var.set(values[1])
            self.purchase_var.set(values[2])
            self.sale_var.set(values[3])
            self.stock_var.set(values[4])
            self.code_var.set(values[5])
            self.source_var.set(values[6])
            self.source_desc_var.set(values[7])
            if values[6] == "অন্যান্য":
                self.source_desc_entry.config(state="normal")
            else:
                self.source_desc_entry.config(state="disabled")
            if int(values[4]) < 5:
                messagebox.showwarning("স্টক সতর্কতা", f"{values[1]} পণ্যের স্টক খুব কম ({values[4]})")

    def add_product(self):
        try:
            purchase = float(self.purchase_var.get()) if self.purchase_var.get().strip() else 0.0
            sale = float(self.sale_var.get()) if self.sale_var.get().strip() else 0.0
            stock = int(self.stock_var.get()) if self.stock_var.get().strip() else 0
        except ValueError:
            messagebox.showerror("ত্রুটি", "দয়া করে মূল্য এবং স্টকের জন্য সঠিক সংখ্যা লিখুন।")
            return
        success, msg = add_product(
            name=self.name_var.get(),
            sale_price=sale,
            stock=stock,
            purchase_price=purchase,
            code=self.code_var.get(),
            source=self.source_var.get(),
            source_desc=self.source_desc_var.get()
        )
        if success:
            messagebox.showinfo("সফল", msg)
            self.load_products()
            self.clear_form()
        else:
            messagebox.showerror("ত্রুটি", msg)

    def update_product(self):
        if not self.selected_product_id:
            messagebox.showwarning("সতর্কতা", "দয়া করে হালনাগাদ করার জন্য একটি পণ্য নির্বাচন করুন।")
            return
        try:
            purchase = float(self.purchase_var.get()) if self.purchase_var.get().strip() else 0.0
            sale = float(self.sale_var.get()) if self.sale_var.get().strip() else 0.0
            stock = int(self.stock_var.get()) if self.stock_var.get().strip() else 0
        except ValueError:
            messagebox.showerror("ত্রুটি", "দয়া করে মূল্য এবং স্টকের জন্য সঠিক সংখ্যা লিখুন।")
            return
        success, msg = update_product(
            int(self.selected_product_id),
            name=self.name_var.get(),
            purchase_price=purchase,
            sale_price=sale,
            stock=stock,
            code=self.code_var.get(),
            source=self.source_var.get(),
            source_desc=self.source_desc_var.get()
        )
        if success:
            messagebox.showinfo("সফল", msg)
            self.load_products()
            self.clear_form()
        else:
            messagebox.showerror("ত্রুটি", msg)

    def delete_product(self):
        if not self.selected_product_id:
            messagebox.showwarning("সতর্কতা", "দয়া করে মুছে ফেলার জন্য একটি পণ্য নির্বাচন করুন।")
            return
        if messagebox.askyesno("নিশ্চিত করুন", "আপনি কি নিশ্চিত যে এই পণ্য মুছে ফেলতে চান?"):
            success, msg = delete_product(int(self.selected_product_id))
            if success:
                messagebox.showinfo("সফল", msg)
                self.load_products()
                self.clear_form()
            else:
                messagebox.showerror("ত্রুটি", msg)

    # ===== Export =====
    def export_excel(self):
        if not self.products_cache:
            messagebox.showinfo("তথ্য নেই", "কোনো পণ্য নেই।")
            return
        df = pd.DataFrame(self.products_cache, columns=["ID","নাম","ক্রয়মূল্য","বিক্রয়মূল্য","স্টক","কোড","ক্রয় উৎস","অন্যান্য বিবরণ","Created At","Updated At"])
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("সফল", f"Excel এ export সম্পন্ন হয়েছে: {file_path}")

    def export_pdf(self):
        if not self.products_cache:
            messagebox.showinfo("তথ্য নেই", "কোনো পণ্য নেই।")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
        if file_path:
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4
            y = height - 50
            c.setFont("Helvetica-Bold", 12)
            c.drawString(30, y, "Product Report")
            y -= 30
            c.setFont("Helvetica", 10)
            for p in self.products_cache:
                text = f"ID:{p[0]} | Name:{p[1]} | Purchase:{p[2]} | Sale:{p[3]} | Stock:{p[4]} | Code:{p[5]} | Source:{p[6]} | Desc:{p[7]} | Created:{p[8]}"
                c.drawString(30, y, text)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50
            c.save()
            messagebox.showinfo("সফল", f"PDF এ export সম্পন্ন হয়েছে: {file_path}")
