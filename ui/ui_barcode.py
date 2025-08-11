import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import messagebox
from barcode_generator.barcode import generate_barcode
import ttkbootstrap as ttk

class BarcodeUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build_ui()
        self.pack(fill="both", expand=True)

    def build_ui(self):
        ttk.Label(self, text="বারকোডের ডেটা:", font=("Helvetica", 12)).pack(pady=(20, 5))
        self.entry_data = ttk.Entry(self, font=("Helvetica", 12), width=30)
        self.entry_data.pack(pady=5)

        ttk.Label(self, text="ফাইল নাম (বিকল্প):", font=("Helvetica", 12)).pack(pady=(15, 5))
        self.entry_filename = ttk.Entry(self, font=("Helvetica", 12), width=30)
        self.entry_filename.pack(pady=5)

        ttk.Button(
            self,
            text="বারকোড তৈরি করুন",
            bootstyle="success",
            command=self.create_barcode
        ).pack(pady=20)

    def create_barcode(self):
        data = self.entry_data.get().strip()
        filename = self.entry_filename.get().strip()

        if not data:
            messagebox.showerror("ত্রুটি", "বারকোডের ডেটা লিখুন।")
            return

        if not filename:
            filename = "barcode"  # ডিফল্ট নাম

        try:
            path = generate_barcode(data, filename)
            messagebox.showinfo("সফল", f"বারকোড সেভ হয়েছে:\n{path}")
        except Exception as e:
            messagebox.showerror("ব্যর্থ", f"বারকোড তৈরি করা যায়নি:\n{e}")
