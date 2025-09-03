import os
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Updated imports from print_utils
from print.print_utils import print_file, print_barcode_pdf

class PrintUI(ttk.Frame):
    """Print Utilities UI"""
    def __init__(self, master=None):
        super().__init__(master)
        self.frame = self  # Add frame attribute for compatibility
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.LabelFrame(self, text="Print Utilities", padding=20)
        frame.pack(padx=10, pady=10, fill="x")

        # Text file print
        ttk.Label(frame, text="Text File:").grid(row=0, column=0, padx=5, pady=5)
        self.text_file_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.text_file_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse", bootstyle="info", command=self.browse_text_file).grid(row=0, column=2, padx=5)
        ttk.Button(frame, text="Print Text", bootstyle="success", command=self.print_text).grid(row=0, column=3, padx=5)

        # Barcode image print
        ttk.Label(frame, text="Barcode Image:").grid(row=1, column=0, padx=5, pady=5)
        self.image_file_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.image_file_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse", bootstyle="info", command=self.browse_image_file).grid(row=1, column=2, padx=5)
        ttk.Button(frame, text="Print Image", bootstyle="success", command=self.print_image).grid(row=1, column=3, padx=5)

    def browse_text_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.text_file_var.set(file_path)

    def browse_image_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_file_var.set(file_path)

    def print_text(self):
        file_path = self.text_file_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a text file")
            return
        try:
            print_file(file_path)  # updated function
            messagebox.showinfo("Success", f"Text file sent to printer: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def print_image(self):
        file_path = self.image_file_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select an image file")
            return
        try:
            print_barcode_pdf(file_path)  # updated function
            messagebox.showinfo("Success", f"Image sent to printer: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
