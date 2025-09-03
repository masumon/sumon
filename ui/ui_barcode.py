# ui/ui_barcode.py

import os
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import barcode
from barcode.writer import ImageWriter

BARCODE_DIR = os.path.join(os.path.dirname(__file__), "..", "barcode_images")
os.makedirs(BARCODE_DIR, exist_ok=True)

class BarcodeUI(ttk.Frame):
    """Barcode Generator UI"""
    def __init__(self, master=None):
        super().__init__(master)
        self.frame = self  # Add frame attribute for compatibility
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.LabelFrame(self, text="Generate Barcode", padding=20)
        frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame, text="Enter Code:").grid(row=0, column=0, padx=5, pady=5)
        self.code_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.code_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Generate", bootstyle="success", command=self.generate_barcode).grid(row=1, column=0, columnspan=2, pady=10)

    def generate_barcode(self):
        code = self.code_var.get().strip()
        if not code:
            messagebox.showwarning("Warning", "Please enter a code")
            return
        try:
            file_path = os.path.join(BARCODE_DIR, f"{code}.png")
            EAN = barcode.get_barcode_class('code128')
            ean = EAN(code, writer=ImageWriter())
            ean.save(file_path)
            messagebox.showinfo("Success", f"Barcode saved: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
