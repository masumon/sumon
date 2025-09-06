import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
from fpdf import FPDF
import os
import sys

# project root যোগ করা যাতে Python module ঠিকমত খুঁজে পায়
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from report.report import get_sales_report, get_sales_report_by_date, get_due_report, get_customer_due_summary
from due_payment_module.due_payment import sync_due_from_sales_and_service
from db import update_due, delete_due, update_sale, delete_sale  # CRUD functions

class ReportUI:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill="both", expand=True)

        # ===== স্টাইল =====
        self.style = ttk.Style()
        self.style.configure(
            "Header.TLabel",
            font=("Kalpurush", 22, "bold"),
            foreground="#1a237e",
            background="#f3f6fa",
        )

        # ===== উপরের বড় শিরোনাম =====
        header_label = ttk.Label(self.frame, text="রিপোর্ট ব্যবস্থাপনা", style="Header.TLabel")
        header_label.pack(pady=(10, 20))

        self.create_widgets()

        # auto sync dues from sales and service
        try:
            sync_due_from_sales_and_service()
        except Exception as e:
            print("Auto-sync error:", e)

    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.frame)
        self.tab_control.pack(fill="both", expand=True)

        # ---------- Sales Report Tab ----------
        self.sales_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(self.sales_frame, text="বিক্রয় রিপোর্ট")
        self.create_sales_tab()

        # ---------- Due Report Tab ----------
        self.due_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(self.due_frame, text="বাকি রিপোর্ট")
        self.create_due_tab()

    # ---------------- Sales Tab ----------------
    def create_sales_tab(self):
        # Filter Frame
        filter_frame = ttk.Frame(self.sales_frame)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="তারিখ (YYYY-MM-DD):").pack(side="left", padx=5)
        self.sales_date_entry = ttk.Entry(filter_frame, width=12)
        self.sales_date_entry.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="দৈনিক বিক্রয় দেখুন", bootstyle="info", command=self.filter_sales_by_date).pack(side="left", padx=5)

        ttk.Label(filter_frame, text="মাসিক (YYYY-MM):").pack(side="left", padx=5)
        self.sales_month_entry = ttk.Entry(filter_frame, width=8)
        self.sales_month_entry.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="মাসিক বিক্রয় দেখুন", bootstyle="info", command=self.filter_sales_by_month).pack(side="left", padx=5)

        ttk.Label(filter_frame, text="পন্য/কাস্টমার নাম:").pack(side="left", padx=5)
        self.sales_customer_entry = ttk.Entry(filter_frame, width=15)
        self.sales_customer_entry.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="সার্চ করুন", bootstyle="info", command=self.filter_sales_by_customer).pack(side="left", padx=5)

        # Action Buttons
        action_frame = ttk.Frame(self.sales_frame)
        action_frame.pack(fill="x", pady=5)
        ttk.Button(action_frame, text="Refresh", bootstyle="info", command=self.load_sales).pack(side="left", padx=5)
        ttk.Button(action_frame, text="PDF এক্সপোর্ট", bootstyle="primary", command=self.export_sales_pdf).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Excel এক্সপোর্ট", bootstyle="success", command=self.export_sales_excel).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Sale আপডেট", bootstyle="warning", command=self.update_sale_ui).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Sale ডিলিট", bootstyle="danger", command=self.delete_sale_ui).pack(side="left", padx=5)

        columns = ("id", "product", "quantity", "sale_price", "total", "date")
        self.sales_tree = ttk.Treeview(self.sales_frame, columns=columns, show="headings")
        for col in columns:
            self.sales_tree.heading(col, text=col.capitalize())
            self.sales_tree.column(col, anchor="center", width=120)
        self.sales_tree.pack(fill="both", expand=True)

        # Scrollbars
        vbar = ttk.Scrollbar(self.sales_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        hbar = ttk.Scrollbar(self.sales_frame, orient=tk.HORIZONTAL, command=self.sales_tree.xview)
        self.sales_tree.configure(yscroll=vbar.set, xscroll=hbar.set)
        vbar.pack(side="right", fill="y")
        hbar.pack(side="bottom", fill="x")
        self.sales_tree.bind("<MouseWheel>", lambda event: self.sales_tree.yview_scroll(int(-1*(event.delta/120)), "units"))

        self.load_sales()

    def load_sales(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        sales = get_sales_report()
        for s in sales:
            self.sales_tree.insert("", "end", values=(
                s.get("id"), s.get("product"), s.get("quantity"),
                s.get("sale_price"), s.get("total"), s.get("date")
            ))

    def filter_sales_by_date(self):
        date_str = self.sales_date_entry.get().strip()
        if not date_str:
            messagebox.showwarning("ত্রুটি", "তারিখ দিন।")
            return
        sales = get_sales_report_by_date(date_str, date_str)
        self._populate_sales_tree(sales)

    def filter_sales_by_month(self):
        month_str = self.sales_month_entry.get().strip()
        if not month_str:
            messagebox.showwarning("ত্রুটি", "মাস দিন।")
            return
        from datetime import datetime
        import calendar
        try:
            year, month = map(int, month_str.split("-"))
            start_date = f"{year}-{month:02d}-01"
            end_day = calendar.monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{end_day}"
        except:
            messagebox.showwarning("ত্রুটি", "সঠিক মাস ফরম্যাট দিন (YYYY-MM)।")
            return
        sales = get_sales_report_by_date(start_date, end_date)
        self._populate_sales_tree(sales)

    def filter_sales_by_customer(self):
        search_text = self.sales_customer_entry.get().strip()
        if not search_text:
            messagebox.showwarning("ত্রুটি", "পন্য বা কাস্টমার নাম দিন।")
            return

        sales = get_sales_report()  # সব sales নিন
        filtered_sales = []
        for s in sales:
            product = s.get("product", "").lower()
            customer = s.get("customer", "").lower()
            if search_text.lower() in product or search_text.lower() in customer:
                filtered_sales.append(s)
        
        self._populate_sales_tree(filtered_sales)

    def _populate_sales_tree(self, sales):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        for s in sales:
            self.sales_tree.insert("", "end", values=(
                s.get("id"), s.get("product"), s.get("quantity"),
                s.get("sale_price"), s.get("total"), s.get("date")
            ))

    # ---------------- Sales CRUD / Export ----------------
    def update_sale_ui(self):
        selected = self.sales_tree.selection()
        if not selected:
            messagebox.showwarning("ত্রুটি", "আপডেট করার জন্য একটি sale নির্বাচন করুন।")
            return
        sale_id = self.sales_tree.item(selected[0])['values'][0]
        new_qty = simpledialog.askinteger("Sale আপডেট", "নতুন quantity দিন:", minvalue=1)
        if new_qty is not None:
            update_sale(sale_id, quantity=new_qty)
            sync_due_from_sales_and_service()
            self.load_sales()
            self.load_due()
            messagebox.showinfo("সফল", f"Sale ID {sale_id} আপডেট হয়েছে।")

    def delete_sale_ui(self):
        selected = self.sales_tree.selection()
        if not selected:
            messagebox.showwarning("ত্রুটি", "ডিলিট করার জন্য একটি sale নির্বাচন করুন।")
            return
        sale_id = self.sales_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Sale ID {sale_id} ডিলিট করতে চান?"):
            delete_sale(sale_id)
            sync_due_from_sales_and_service()
            self.load_sales()
            self.load_due()
            messagebox.showinfo("সফল", f"Sale ID {sale_id} ডিলিট হয়েছে।")

    def export_sales_pdf(self):
        sales = get_sales_report()
        if not sales:
            messagebox.showwarning("ত্রুটি", "কোনো বিক্রয় ডেটা নেই।")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
        if not file_path:
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "বিক্রয় রিপোর্ট", 0, 1, "C")
        pdf.set_font("Arial", "B", 12)
        cols = ["ID", "Product", "Quantity", "Sale Price", "Total", "Date"]
        widths = [15, 50, 20, 25, 25, 35]
        for i, col in enumerate(cols):
            pdf.cell(widths[i], 8, col, 1, 0, "C")
        pdf.ln()
        pdf.set_font("Arial", "", 11)
        for s in sales:
            row = [str(s["id"]), s["product"], str(s["quantity"]), str(s["sale_price"]), str(s["total"]), str(s["date"])]
            for i, val in enumerate(row):
                pdf.cell(widths[i], 8, val, 1, 0, "C")
            pdf.ln()
        pdf.output(file_path)
        messagebox.showinfo("সফল", f"PDF Exported: {os.path.basename(file_path)}")

    def export_sales_excel(self):
        sales = get_sales_report()
        if not sales:
            messagebox.showwarning("ত্রুটি", "কোনো বিক্রয় ডেটা নেই।")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if not file_path:
            return
        df = pd.DataFrame(sales)
        df.to_excel(file_path, index=False)
        messagebox.showinfo("সফল", f"Excel Exported: {os.path.basename(file_path)}")

    # ---------------- Due Tab ----------------
    def create_due_tab(self):
        # Filter Frame
        filter_frame = ttk.Frame(self.due_frame)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="তারিখ (YYYY-MM-DD):").pack(side="left", padx=5)
        self.due_date_entry = ttk.Entry(filter_frame, width=12)
        self.due_date_entry.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="দৈনিক বাকি দেখুন", bootstyle="info", command=self.filter_due_by_date).pack(side="left", padx=5)

        ttk.Label(filter_frame, text="মাসিক (YYYY-MM):").pack(side="left", padx=5)
        self.due_month_entry = ttk.Entry(filter_frame, width=8)
        self.due_month_entry.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="মাসিক বাকি দেখুন", bootstyle="info", command=self.filter_due_by_month).pack(side="left", padx=5)

        ttk.Label(filter_frame, text="কাস্টমার নাম:").pack(side="left", padx=5)
        self.due_customer_entry = ttk.Entry(filter_frame, width=15)
        self.due_customer_entry.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="কাস্টমার বাকি দেখুন", bootstyle="info", command=self.filter_due_by_customer).pack(side="left", padx=5)

        # Action Buttons
        action_frame = ttk.Frame(self.due_frame)
        action_frame.pack(fill="x", pady=5)
        ttk.Button(action_frame, text="Refresh", bootstyle="info", command=self.load_due).pack(side="left", padx=5)
        ttk.Button(action_frame, text="PDF এক্সপোর্ট", bootstyle="primary", command=self.export_due_pdf).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Excel এক্সপোর্ট", bootstyle="success", command=self.export_due_excel).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Due আপডেট", bootstyle="warning", command=self.update_due_ui).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Due ডিলিট", bootstyle="danger", command=self.delete_due_ui).pack(side="left", padx=5)

        columns = ("id", "customer", "amount", "due_date", "sale_id", "date")
        self.due_tree = ttk.Treeview(self.due_frame, columns=columns, show="headings")
        for col in columns:
            self.due_tree.heading(col, text=col.capitalize())
            self.due_tree.column(col, anchor="center", width=120)
        self.due_tree.pack(fill="both", expand=True)

        # Scrollbars
        vbar = ttk.Scrollbar(self.due_frame, orient=tk.VERTICAL, command=self.due_tree.yview)
        hbar = ttk.Scrollbar(self.due_frame, orient=tk.HORIZONTAL, command=self.due_tree.xview)
        self.due_tree.configure(yscroll=vbar.set, xscroll=hbar.set)
        vbar.pack(side="right", fill="y")
        hbar.pack(side="bottom", fill="x")
        self.due_tree.bind("<MouseWheel>", lambda event: self.due_tree.yview_scroll(int(-1*(event.delta/120)), "units"))

        self.load_due()

    def load_due(self):
        for row in self.due_tree.get_children():
            self.due_tree.delete(row)
        dues = get_due_report()
        for d in dues:
            self.due_tree.insert("", "end", values=(
                d.get("id"), d.get("customer"), d.get("amount"),
                d.get("due_date"), d.get("sale_id"), d.get("date")
            ))

    def filter_due_by_date(self):
        date_str = self.due_date_entry.get().strip()
        if not date_str:
            messagebox.showwarning("ত্রুটি", "তারিখ দিন।")
            return
        dues = get_due_report()
        filtered = [d for d in dues if str(d.get("date")) == date_str]
        self._populate_due_tree(filtered)

    def filter_due_by_month(self):
        month_str = self.due_month_entry.get().strip()
        if not month_str:
            messagebox.showwarning("ত্রুটি", "মাস দিন।")
            return
        try:
            year, month = map(int, month_str.split("-"))
            filtered = []
            dues = get_due_report()
            for d in dues:
                d_date = str(d.get("date"))
                if d_date.startswith(f"{year}-{month:02d}"):
                    filtered.append(d)
            self._populate_due_tree(filtered)
        except:
            messagebox.showwarning("ত্রুটি", "সঠিক মাস ফরম্যাট দিন (YYYY-MM)।")

    def filter_due_by_customer(self):
        search_text = self.due_customer_entry.get().strip()
        if not search_text:
            messagebox.showwarning("ত্রুটি", "কাস্টমার নাম দিন।")
            return
        dues = get_due_report()
        filtered = [d for d in dues if search_text.lower() in str(d.get("customer","")).lower()]
        self._populate_due_tree(filtered)

    def _populate_due_tree(self, dues):
        for row in self.due_tree.get_children():
            self.due_tree.delete(row)
        for d in dues:
            self.due_tree.insert("", "end", values=(
                d.get("id"), d.get("customer"), d.get("amount"),
                d.get("due_date"), d.get("sale_id"), d.get("date")
            ))

    def update_due_ui(self):
        selected = self.due_tree.selection()
        if not selected:
            messagebox.showwarning("ত্রুটি", "আপডেট করার জন্য একটি due নির্বাচন করুন।")
            return
        due_id = self.due_tree.item(selected[0])['values'][0]
        new_amount = simpledialog.askfloat("Due আপডেট", "নতুন পরিমাণ দিন:", minvalue=0)
        if new_amount is not None:
            update_due(due_id, amount=new_amount)
            self.load_due()
            messagebox.showinfo("সফল", f"Due ID {due_id} আপডেট হয়েছে।")

    def delete_due_ui(self):
        selected = self.due_tree.selection()
        if not selected:
            messagebox.showwarning("ত্রুটি", "ডিলিট করার জন্য একটি due নির্বাচন করুন।")
            return
        due_id = self.due_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Due ID {due_id} ডিলিট করতে চান?"):
            delete_due(due_id)
            self.load_due()
            messagebox.showinfo("সফল", f"Due ID {due_id} ডিলিট হয়েছে।")

    def export_due_pdf(self):
        dues = get_due_report()
        if not dues:
            messagebox.showwarning("ত্রুটি", "কোনো বাকি ডেটা নেই।")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
        if not file_path:
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "বাকি রিপোর্ট", 0, 1, "C")
        pdf.set_font("Arial", "B", 12)
        cols = ["ID", "Customer", "Amount", "Due Date", "Sale ID", "Date"]
        widths = [15, 50, 25, 25, 25, 35]
        for i, col in enumerate(cols):
            pdf.cell(widths[i], 8, col, 1, 0, "C")
        pdf.ln()
        pdf.set_font("Arial", "", 11)
        for d in dues:
            row = [str(d["id"]), d["customer"], str(d["amount"]), str(d["due_date"]), str(d["sale_id"]), str(d["date"])]
            for i, val in enumerate(row):
                pdf.cell(widths[i], 8, val, 1, 0, "C")
            pdf.ln()
        pdf.output(file_path)
        messagebox.showinfo("সফল", f"PDF Exported: {os.path.basename(file_path)}")

    def export_due_excel(self):
        dues = get_due_report()
        if not dues:
            messagebox.showwarning("ত্রুটি", "কোনো বাকি ডেটা নেই।")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if not file_path:
            return
        df = pd.DataFrame(dues)
        df.to_excel(file_path, index=False)
        messagebox.showinfo("সফল", f"Excel Exported: {os.path.basename(file_path)}")
