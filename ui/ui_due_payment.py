import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
from fpdf import FPDF
import sys
import os
from datetime import datetime

# project root যোগ করা যাতে Python module ঠিকমত খুঁজে পায়
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from due_payment_module.due_payment import (
    get_all_due_payments,
    add_due_payment,
    update_due_payment,
    delete_due_payment,
    sync_due_from_sales_and_service,
    get_customer_due_summary,
)

class DuePaymentUI:
    def __init__(self, master):
        self.master = master
        if isinstance(self.master, tk.Tk):
            self.master.title("বাকি ব্যবস্থাপনা")

        # Auto sync dues
        try:
            sync_due_from_sales_and_service()
        except Exception as e:
            print("Auto-sync error:", e)

        # ---------- Styles ----------
        self.style = ttk.Style()
        self.style.configure(
            "Header.TLabel",
            font=("Kalpurush", 22, "bold"),
            foreground="#1a237e",
            background="#f3f6fa",
        )
        self.style.configure("TLabelframe", background="#f3f6fa")
        self.style.configure("TFrame", background="#f3f6fa")

        self.frame = ttk.Frame(master, padding=20, style="TFrame")
        self.frame.pack(fill=BOTH, expand=True)

        # ---------- Header ----------
        heading = ttk.Label(
            self.frame, text="বাকি ব্যবস্থাপনা", style="Header.TLabel", anchor="center"
        )
        heading.grid(row=0, column=0, columnspan=10, pady=(0, 18), sticky="nsew")

        # ---------- Form Box ----------
        form_box = ttk.Labelframe(self.frame, text="নতুন/আপডেট", padding=(14, 9))
        form_box.grid(row=1, column=0, columnspan=10, sticky="ew", padx=1, pady=6)

        ttk.Label(form_box, text="ক্রেতার নাম:").grid(row=0, column=0, sticky=W, padx=4, pady=3)
        self.customer_entry = ttk.Entry(form_box, width=18)
        self.customer_entry.grid(row=0, column=1, padx=4, pady=3)

        ttk.Label(form_box, text="বাকি অর্থ:").grid(row=0, column=2, sticky=W, padx=4, pady=3)
        self.amount_entry = ttk.Entry(form_box, width=10)
        self.amount_entry.grid(row=0, column=3, padx=4, pady=3)

        ttk.Label(form_box, text="বাকি তারিখ (YYYY-MM-DD):").grid(row=0, column=4, sticky=W, padx=4)
        self.due_date_entry = ttk.Entry(form_box, width=15)
        self.due_date_entry.grid(row=0, column=5, padx=4, pady=3)

        # Buttons
        self.add_btn = ttk.Button(form_box, text="যোগ", bootstyle=SUCCESS, width=8, command=self.add_due)
        self.add_btn.grid(row=0, column=6, padx=2, pady=3)

        self.update_btn = ttk.Button(form_box, text="আপডেট", bootstyle=WARNING, width=8, command=self.update_due)
        self.update_btn.grid(row=0, column=7, padx=2, pady=3)

        self.delete_btn = ttk.Button(form_box, text="ডিলিট", bootstyle=DANGER, width=8, command=self.delete_due)
        self.delete_btn.grid(row=0, column=8, padx=2, pady=3)

        self.refresh_btn = ttk.Button(form_box, text="রিফ্রেশ", bootstyle=INFO, width=8, command=self.refresh_tree)
        self.refresh_btn.grid(row=0, column=9, padx=2, pady=3)

        # ---------- Export Box ----------
        export_box = ttk.Labelframe(self.frame, text="এক্সপোর্ট", padding=(14, 6))
        export_box.grid(row=2, column=0, columnspan=10, sticky="ew", padx=1, pady=8)

        ttk.Label(export_box, text="তারিখ (শুরু)").grid(row=0, column=0, padx=2, pady=3)
        self.export_start = ttk.Entry(export_box, width=12)
        self.export_start.grid(row=0, column=1, padx=2)

        ttk.Label(export_box, text="শেষ:").grid(row=0, column=2, padx=2)
        self.export_end = ttk.Entry(export_box, width=12)
        self.export_end.grid(row=0, column=3, padx=2)

        self.pdf_btn = ttk.Button(export_box, text="PDF", width=8, bootstyle=INFO, command=self.export_pdf)
        self.pdf_btn.grid(row=0, column=4, padx=2)

        self.excel_btn = ttk.Button(export_box, text="Excel", width=8, bootstyle=PRIMARY, command=self.export_excel)
        self.excel_btn.grid(row=0, column=5, padx=2)

        # ---------- Data Table ----------
        columns = ("ID", "ক্রেতা", "বাকি অর্থ", "উৎস", "বাকি তারিখ", "বিক্রয় আইডি", "রেকর্ডের সময়")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", bootstyle="success")
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 120
            if col in ("ক্রেতা", "রেকর্ডের সময়"):
                width = 160
            elif col == "বাকি অর্থ":
                width = 100
            elif col == "উৎস":
                width = 100
            self.tree.column(col, anchor="center", width=width)
            
        self.tree.grid(row=3, column=0, columnspan=7, sticky="nsew", pady=(10, 0), padx=(3, 3))
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        vbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        hbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=vbar.set, xscroll=hbar.set)
        vbar.grid(row=3, column=7, sticky="ns", pady=(10, 0))
        hbar.grid(row=4, column=0, columnspan=7, sticky="ew", padx=(3, 3))

        for i in range(7):
            self.frame.columnconfigure(i, weight=1)
        self.frame.rowconfigure(3, weight=1)

        self.tree.tag_configure("evenrow", background="#f5f9ff")
        self.tree.tag_configure("oddrow", background="#ffffff")

        # ---------- Entry Count Label ----------
        self.entry_count_label = ttk.Label(self.frame, text="", anchor="e", font=("Kalpurush", 10, "bold"))
        self.entry_count_label.grid(row=4, column=7, sticky="e", padx=(3,3), pady=(5,0))

        # ---------- Customer Summary Box ----------
        summary_box = ttk.Labelframe(self.frame, text="কাস্টমারের সারসংক্ষেপ", padding=(14, 6))
        summary_box.grid(row=5, column=0, columnspan=10, sticky="ew", padx=1, pady=8)

        ttk.Label(summary_box, text="ক্রেতার নাম:").grid(row=0, column=0, padx=2, pady=3)
        self.summary_customer_entry = ttk.Entry(summary_box, width=18)
        self.summary_customer_entry.grid(row=0, column=1, padx=2)

        self.summary_btn = ttk.Button(summary_box, text="দেখুন", width=10, bootstyle=INFO, command=self.show_customer_summary)
        self.summary_btn.grid(row=0, column=2, padx=2)

        self.summary_label = ttk.Label(summary_box, text="", anchor="w")
        self.summary_label.grid(row=1, column=0, columnspan=10, sticky="w", padx=2, pady=4)

        # Load initial data
        self.refresh_tree()

    # --------------------------- Tree Methods ---------------------------
    def refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = get_all_due_payments()
        seen_ids = set()
        filtered_data = []
        for d in data:
            if d.get("id") not in seen_ids and d.get("customer"):
                filtered_data.append(d)
                seen_ids.add(d["id"])
        for idx, due in enumerate(filtered_data):
            tags = ("evenrow",) if idx % 2 == 0 else ("oddrow",)
            self.tree.insert(
                "", tk.END,
                values=(due["id"], due["customer"], due["amount"], due.get("source", "N/A"), due["due_date"], due["sale_id"], due["date"]),
                tags=tags
            )
        self.selected_id = None

        # Update entry count
        self.entry_count_label.config(text=f"মোট এন্ট্রি: {len(filtered_data)}")

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            self.selected_id = values[0]
            self.customer_entry.delete(0, tk.END)
            self.customer_entry.insert(0, values[1])
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, values[2])
            self.due_date_entry.delete(0, tk.END)
            self.due_date_entry.insert(0, values[4]) # Adjusted index for due_date
        else:
            self.selected_id = None

    # --------------------------- CRUD Methods ---------------------------
    def add_due(self):
        customer = self.customer_entry.get().strip()
        amount = self.amount_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        if not customer or not amount or not due_date:
            messagebox.showwarning("ত্রুটি", "সকল তথ্য পূরণ করুন")
            return
        if not self.validate_date(due_date):
            messagebox.showwarning("ত্রুটি", "তারিখ ফরম্যাট সঠিক নয় (YYYY-MM-DD)")
            return
        try:
            add_due_payment(customer, float(amount), due_date)
            messagebox.showinfo("সফল", "বাকি যোগ হয়েছে।")
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

    def update_due(self):
        if getattr(self, "selected_id", None) is None:
            messagebox.showwarning("ত্রুটি", "সিলেক্ট করুন কোন বাকি আপডেট করবেন।")
            return
        customer = self.customer_entry.get().strip()
        amount = self.amount_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        if not customer or not amount or not due_date:
            messagebox.showwarning("ত্রুটি", "সকল তথ্য পূরণ করুন")
            return
        if not self.validate_date(due_date):
            messagebox.showwarning("ত্রুটি", "তারিখ ফরম্যাট সঠিক নয় (YYYY-MM-DD)")
            return
        try:
            update_due_payment(self.selected_id, customer, float(amount), due_date)
            messagebox.showinfo("সফল", "বাকি আপডেট হয়েছে।")
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

    def delete_due(self):
        if getattr(self, "selected_id", None) is None:
            messagebox.showwarning("ত্রুটি", "সিলেক্ট করুন কোন বাকি মুছবেন।")
            return
        sure = messagebox.askyesno("নিশ্চিত?", "আপনি কি বাকি সত্যিই মুছে ফেলতে চান?")
        if not sure:
            return
        try:
            delete_due_payment(self.selected_id)
            messagebox.showinfo("সফল", "বাকি ডিলিট হয়েছে।")
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

    # --------------------------- Export Methods ---------------------------
    def export_pdf(self):
        start_date = self.export_start.get().strip()
        end_date = self.export_end.get().strip()
        data = [
            d for d in get_all_due_payments()
            if (not start_date or d["due_date"] >= start_date)
            and (not end_date or d["due_date"] <= end_date)
            and d.get("customer")
        ]
        if not data:
            messagebox.showwarning("ত্রুটি", "এই তারিখে কোনো ডেটা নেই।")
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt="বাকি ব্যবস্থাপনা রিপোর্ট", ln=1, align="C")
        columns = ["আইডি", "ক্রেতা", "বাকি অর্থ", "উৎস", "তারিখ", "বিক্রয় আইডি", "রেকর্ড"]
        col_widths = [18, 38, 28, 26, 26, 26, 36]
        for idx, col in enumerate(columns):
            pdf.cell(col_widths[idx], 10, col, 1, 0, "C")
        pdf.ln()
        for row in data:
            lst = [str(row["id"]), str(row["customer"]), str(row["amount"]), str(row.get("source", "N/A")), str(row["due_date"]),
                   str(row["sale_id"]), str(row["date"])]
            for idx, item in enumerate(lst):
                pdf.cell(col_widths[idx], 8, item, 1, 0, "L")
            pdf.ln()
        try:
            filename = f"due_payments_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(filename)
            messagebox.showinfo("সফল", f"PDF Report: {filename}")
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

    def export_excel(self):
        start_date = self.export_start.get().strip()
        end_date = self.export_end.get().strip()
        data = [
            d for d in get_all_due_payments()
            if (not start_date or d["due_date"] >= start_date)
            and (not end_date or d["due_date"] <= end_date)
            and d.get("customer")
        ]
        if not data:
            messagebox.showwarning("ত্রুটি", "এই তারিখে কোনো ডেটা নেই।")
            return
        df = pd.DataFrame(data)
        try:
            filename = f"due_payments_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            messagebox.showinfo("সফল", f"Excel Report: {filename}")
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

    # --------------------------- Customer Summary Method ---------------------------
    def show_customer_summary(self):
        customer_name = self.summary_customer_entry.get().strip()
        if not customer_name:
            messagebox.showwarning("ত্রুটি", "ক্রেতার নাম লিখুন")
            return
        try:
            summary = get_customer_due_summary(customer_name)
            text = (
                f"ক্রেতা: {customer_name} | "
                f"মোট বাকি: {summary.get('total_due', 0)} | "
                f"Sales বাকি: {summary.get('total_sales_due', 0)} | "
                f"Service বাকি: {summary.get('total_service_due', 0)}"
            )
            self.summary_label.config(text=text)
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

    # --------------------------- Helper Methods ---------------------------
    @staticmethod
    def validate_date(date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False
