# ui/ui_expense.py

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "smartshop.db")

# ---------------- Database Functions ----------------
def get_all_expenses():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, category_id, amount, date, note FROM expenses ORDER BY date DESC")
    expenses = cursor.fetchall()
    conn.close()
    return expenses

def add_expense(category_id, amount, date, note):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (category_id, amount, date, note) VALUES (?, ?, ?, ?)",
                       (category_id, amount, date, note))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("ব্যয় যোগ করার ত্রুটি", str(e))
        return False

def update_expense(expense_id, category_id, amount, date, note):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE expenses SET category_id=?, amount=?, date=?, note=? WHERE id=?",
                       (category_id, amount, date, note, expense_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("ব্যয় আপডেট করার ত্রুটি", str(e))
        return False

def delete_expense(expense_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("ব্যয় মুছার ত্রুটি", str(e))
        return False

# ---------------- UI Class ----------------
class ExpenseUI(ttk.Frame):
    """ব্যয় ব্যবস্থাপনা UI"""
    def __init__(self, master=None):
        super().__init__(master)
        self.frame = self
        self.pack(fill="both", expand=True)
        self.selected_expense_id = None

        # ===== স্টাইল =====
        self.style = ttk.Style()
        self.style.configure(
            "Header.TLabel",
            font=("Kalpurush", 22, "bold"),
            foreground="#1a237e",
            background="#f3f6fa",
        )

        # ===== উপরের বড় শিরোনাম =====
        header_label = ttk.Label(self, text="খরচ ব্যবস্থাপনা", style="Header.TLabel")
        header_label.pack(pady=(10, 20))

        # ===== মূল ফর্ম =====
        self.create_widgets()
        self.load_expenses()

    def create_widgets(self):
        # ===== ফর্ম ফ্রেম =====
        form_frame = ttk.LabelFrame(self, text="ব্যয় বিস্তারিত", padding=(10,10))
        form_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="ক্যাটেগরি ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(form_frame, text="পরিমাণ:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Label(form_frame, text="তারিখ:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(form_frame, text="বিবরণ:").grid(row=1, column=2, sticky="w", padx=5, pady=5)

        self.category_var = tk.StringVar()
        self.amount_var = tk.DoubleVar()
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.note_var = tk.StringVar()

        ttk.Entry(form_frame, textvariable=self.category_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.amount_var).grid(row=0, column=3, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.date_var).grid(row=1, column=1, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.note_var).grid(row=1, column=3, padx=5, pady=5)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text="যোগ করুন", bootstyle="success", command=self.add_expense).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="আপডেট করুন", bootstyle="primary", command=self.update_expense).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="মুছুন", bootstyle="danger", command=self.delete_expense).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="ফর্ম খালি করুন", bootstyle="secondary", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 রিফ্রেশ", bootstyle="info", command=self.load_expenses).pack(side="left", padx=5)

        # ===== Treeview ফ্রেম =====
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("id", "category_id", "amount", "date", "note")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", bootstyle="info")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").capitalize())
            self.tree.column(col, anchor="center", width=100)
        self.tree.pack(fill="both", expand=True, side="left")

        # ===== স্ক্রলবার =====
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    # ===== Methods =====
    def load_expenses(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        expenses = get_all_expenses()
        for e in expenses:
            self.tree.insert("", "end", values=e)

    def add_expense(self):
        if add_expense(self.category_var.get(), self.amount_var.get(), self.date_var.get(), self.note_var.get()):
            messagebox.showinfo("সফল", "ব্যয় সফলভাবে যোগ হয়েছে")
            self.load_expenses()
            self.clear_form()

    def update_expense(self):
        if not self.selected_expense_id:
            messagebox.showwarning("সতর্কতা", "দয়া করে আপডেট করার জন্য একটি ব্যয় নির্বাচন করুন")
            return
        if update_expense(self.selected_expense_id, self.category_var.get(), self.amount_var.get(),
                          self.date_var.get(), self.note_var.get()):
            messagebox.showinfo("সফল", "ব্যয় সফলভাবে আপডেট হয়েছে")
            self.load_expenses()
            self.clear_form()

    def delete_expense(self):
        if not self.selected_expense_id:
            messagebox.showwarning("সতর্কতা", "দয়া করে মুছার জন্য একটি ব্যয় নির্বাচন করুন")
            return
        if messagebox.askyesno("নিশ্চিত", "আপনি কি সত্যিই এই ব্যয় মুছতে চান?"):
            if delete_expense(self.selected_expense_id):
                messagebox.showinfo("সফল", "ব্যয় সফলভাবে মুছে ফেলা হয়েছে")
                self.load_expenses()
                self.clear_form()

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            self.selected_expense_id = values[0]
            self.category_var.set(values[1])
            self.amount_var.set(values[2])
            self.date_var.set(values[3])
            self.note_var.set(values[4])

    def clear_form(self):
        self.selected_expense_id = None
        self.category_var.set("")
        self.amount_var.set(0.0)
        self.date_var.set(datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.note_var.set("")
