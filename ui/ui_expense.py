import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from expense_module import expense_category, expense, expense_report

class ExpenseUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f9f9f9")
        self.pack(fill="both", expand=True)

        # UI তৈরি ও ডাটা লোড
        self.create_widgets()
        self.load_categories()
        self.load_expenses()

    def create_widgets(self):
        # ক্যাটেগরি ফ্রেম
        cat_frame = ttk.LabelFrame(self, text="ক্যাটেগরি যোগ করুন")
        cat_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(cat_frame, text="ক্যাটেগরির নাম:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cat_name_var = tk.StringVar()
        ttk.Entry(cat_frame, textvariable=self.cat_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(cat_frame, text="যোগ করুন", command=self.add_category).grid(row=0, column=2, padx=5, pady=5)

        # খরচ ফ্রেম
        expense_frame = ttk.LabelFrame(self, text="খরচ যোগ করুন")
        expense_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(expense_frame, text="ক্যাটেগরি:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.exp_cat_var = tk.StringVar()
        self.exp_cat_combo = ttk.Combobox(expense_frame, textvariable=self.exp_cat_var, state="readonly", width=28)
        self.exp_cat_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(expense_frame, text="পরিমাণ:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.amount_var = tk.StringVar()
        ttk.Entry(expense_frame, textvariable=self.amount_var, width=15).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(expense_frame, text="বিবরণ:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.desc_var = tk.StringVar()
        ttk.Entry(expense_frame, textvariable=self.desc_var, width=60).grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        ttk.Label(expense_frame, text="তারিখ (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(expense_frame, textvariable=self.date_var, width=15).grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(expense_frame, text="খরচ যোগ করুন", command=self.add_expense).grid(row=2, column=3, padx=5, pady=5)

        # খরচ তালিকা ফ্রেম
        list_frame = ttk.LabelFrame(self, text="খরচ তালিকা")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "category", "amount", "description", "date")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("id", text="আইডি")
        self.tree.column("id", width=50, anchor="center")
        self.tree.heading("category", text="ক্যাটেগরি")
        self.tree.column("category", width=150, anchor="w")
        self.tree.heading("amount", text="পরিমাণ")
        self.tree.column("amount", width=100, anchor="e")
        self.tree.heading("description", text="বিবরণ")
        self.tree.column("description", width=300, anchor="w")
        self.tree.heading("date", text="তারিখ")
        self.tree.column("date", width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)

        ttk.Button(list_frame, text="মুছে ফেলুন", command=self.delete_expense).pack(pady=5)

        # রিপোর্ট ফ্রেম
        report_frame = ttk.LabelFrame(self, text="তারিখ অনুযায়ী রিপোর্ট")
        report_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(report_frame, text="শুরু তারিখ (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_date_var = tk.StringVar()
        ttk.Entry(report_frame, textvariable=self.start_date_var, width=15).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(report_frame, text="শেষ তারিখ (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.end_date_var = tk.StringVar()
        ttk.Entry(report_frame, textvariable=self.end_date_var, width=15).grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(report_frame, text="রিপোর্ট দেখুন", command=self.show_report).grid(row=0, column=4, padx=5, pady=5)

        self.report_text = tk.Text(report_frame, height=8, wrap="word")
        self.report_text.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="ew")

    def load_categories(self):
        categories = expense_category.get_all_categories()
        names = [c[1] for c in categories]
        self.exp_cat_combo['values'] = names
        if names:
            self.exp_cat_combo.current(0)

    def add_category(self):
        name = self.cat_name_var.get().strip()
        if not name:
            messagebox.showwarning("সতর্কতা", "ক্যাটেগরির নাম দিন")
            return
        expense_category.add_category(name)
        messagebox.showinfo("সফল", "ক্যাটেগরি যোগ করা হয়েছে")
        self.cat_name_var.set("")
        self.load_categories()

    def add_expense(self):
        category_name = self.exp_cat_var.get()
        categories = expense_category.get_all_categories()
        category_dict = {name: cid for cid, name in categories}
        category_id = category_dict.get(category_name)

        if category_id is None:
            messagebox.showerror("ত্রুটি", "সঠিক ক্যাটেগরি নির্বাচন করুন")
            return

        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("ত্রুটি", "সঠিক পরিমাণ দিন")
            return

        description = self.desc_var.get().strip()
        expense_date = self.date_var.get().strip()

        try:
            datetime.strptime(expense_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("ত্রুটি", "তারিখের ফরম্যাট সঠিক নয় (YYYY-MM-DD)")
            return

        expense.add_expense(category_id, amount, description, expense_date)
        messagebox.showinfo("সফল", "খরচ যোগ করা হয়েছে")

        self.amount_var.set("")
        self.desc_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.load_expenses()

    def load_expenses(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = expense.get_all_expenses()
        for r in rows:
            self.tree.insert("", "end", values=r)

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("সতর্কতা", "একটি খরচ নির্বাচন করুন")
            return

        confirm = messagebox.askyesno("নিশ্চিতকরণ", "আপনি কি এই খরচটি মুছে ফেলতে চান?")
        if not confirm:
            return

        item = self.tree.item(selected[0])
        expense_id = item['values'][0]
        expense.delete_expense(expense_id)
        messagebox.showinfo("সফল", "খরচ মুছে ফেলা হয়েছে")
        self.load_expenses()

    def show_report(self):
        start = self.start_date_var.get().strip()
        end = self.end_date_var.get().strip()

        if not start or not end:
            messagebox.showwarning("সতর্কতা", "শুরু ও শেষ তারিখ দিন")
            return

        try:
            datetime.strptime(start, "%Y-%m-%d")
            datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("ত্রুটি", "তারিখের ফরম্যাট সঠিক নয় (YYYY-MM-DD)")
            return

        report = expense_report.get_expense_report_by_date(start, end)

        self.report_text.delete("1.0", tk.END)
        if not report:
            self.report_text.insert(tk.END, "কোন খরচ পাওয়া যায়নি।\n")
            return

        self.report_text.insert(tk.END, f"{'ক্যাটেগরি':<20} | {'মোট পরিমাণ':>10}\n")
        self.report_text.insert(tk.END, "-"*35 + "\n")
        for cat_name, total in report:
            self.report_text.insert(tk.END, f"{cat_name:<20} | {total:>10.2f}\n")
