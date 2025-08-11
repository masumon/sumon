import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from print.print_utils import (
    get_default_printer,
    set_default_printer,
    list_printers,
    print_file,
    print_barcode_pdf,
    print_receipt_pdf,
)

class PrintUI(tk.Frame):
    def __init__(self, master=None, pdf_path=None):
        super().__init__(master, bg="#f9f9f9")
        self.pdf_path = pdf_path
        self.create_widgets()

    def create_widgets(self):
        self.label_printers = tk.Label(self, text="ডিভাইস প্রিন্টার তালিকা:", bg="#f9f9f9")
        self.label_printers.pack(pady=5)

        self.combo_printers = ttk.Combobox(self, width=50, state="readonly")
        self.combo_printers.pack(pady=5)
        self.refresh_printers()

        self.button_set_default = tk.Button(self, text="ডিফল্ট প্রিন্টার সেট করুন", command=self.set_default)
        self.button_set_default.pack(pady=5)

        self.button_print_pdf = tk.Button(self, text="PDF প্রিন্ট করুন", command=self.threaded_print_pdf)
        self.button_print_pdf.pack(pady=10)

        self.button_select_file = tk.Button(self, text="PDF বা Image ফাইল সিলেক্ট করে প্রিন্ট করুন", command=self.threaded_select_and_print_file)
        self.button_select_file.pack(pady=10)

        self.button_barcode = tk.Button(self, text="বারকোড প্রিন্ট করুন", command=self.threaded_print_barcode)
        self.button_barcode.pack(pady=10)

        self.button_receipt = tk.Button(self, text="রসিদ প্রিন্ট করুন", command=self.threaded_print_receipt)
        self.button_receipt.pack(pady=10)

        self.disable_buttons_if_no_printer()

    def refresh_printers(self):
        printers = list_printers()
        self.combo_printers['values'] = printers
        if printers:
            default = get_default_printer()
            if default and default in printers:
                self.combo_printers.set(default)
            else:
                self.combo_printers.current(0)

    def disable_buttons_if_no_printer(self):
        if not self.combo_printers['values']:
            for btn in [
                self.button_set_default, self.button_print_pdf, self.button_select_file,
                self.button_barcode, self.button_receipt
            ]:
                btn.config(state="disabled")
            self.safe_showwarning("প্রিন্টার নেই", "কোনো প্রিন্টার পাওয়া যায়নি। প্রিন্টার যুক্ত করুন।")

    def get_selected_printer(self):
        printer = self.combo_printers.get()
        if not printer:
            self.safe_showwarning("ত্রুটি", "প্রিন্টার সিলেক্ট করা হয়নি!")
        return printer

    def set_default(self):
        printer = self.get_selected_printer()
        if printer:
            set_default_printer(printer)
            self.safe_showinfo("সফল", f"ডিফল্ট প্রিন্টার সেট হয়েছে: {printer}")

    # Threading helpers
    def threaded_print_pdf(self):
        threading.Thread(target=self.print_pdf, daemon=True).start()

    def threaded_select_and_print_file(self):
        threading.Thread(target=self.select_and_print_file, daemon=True).start()

    def threaded_print_barcode(self):
        threading.Thread(target=self.print_barcode, daemon=True).start()

    def threaded_print_receipt(self):
        threading.Thread(target=self.print_receipt, daemon=True).start()

    # Printing functions
    def print_pdf(self):
        if not self.pdf_path:
            self.safe_showwarning("ত্রুটি", "কোনো PDF ফাইল পাওয়া যায়নি!")
            return
        printer = self.get_selected_printer()
        if printer:
            try:
                self.show_loading("PDF প্রিন্ট হচ্ছে...")
                print_file(self.pdf_path, printer)
                self.hide_loading()
                self.safe_showinfo("সফল", "PDF প্রিন্ট হয়েছে!")
            except Exception as e:
                self.hide_loading()
                self.safe_showerror("ত্রুটি", str(e))

    def select_and_print_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF or Image Files", "*.pdf *.png *.jpg *.jpeg")])
        if filepath:
            printer = self.get_selected_printer()
            if printer:
                try:
                    self.show_loading("ফাইল প্রিন্ট হচ্ছে...")
                    print_file(filepath, printer)
                    self.hide_loading()
                    self.safe_showinfo("সফল", "ফাইল প্রিন্ট হয়েছে!")
                except Exception as e:
                    self.hide_loading()
                    self.safe_showerror("ত্রুটি", str(e))

    def print_barcode(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if filepath:
            output_pdf = "barcode_print.pdf"
            printer = self.get_selected_printer()
            if printer:
                try:
                    self.show_loading("বারকোড প্রিন্ট হচ্ছে...")
                    print_barcode_pdf(filepath, output_pdf)
                    print_file(output_pdf, printer)
                    self.hide_loading()
                    self.safe_showinfo("সফল", "বারকোড প্রিন্ট হয়েছে!")
                except Exception as e:
                    self.hide_loading()
                    self.safe_showerror("ত্রুটি", str(e))

    def print_receipt(self):
        if not self.pdf_path:
            self.safe_showwarning("ত্রুটি", "কোনো রসিদ পাওয়া যায়নি!")
            return
        printer = self.get_selected_printer()
        if printer:
            try:
                self.show_loading("রসিদ প্রিন্ট হচ্ছে...")
                print_file(self.pdf_path, printer)
                self.hide_loading()
                self.safe_showinfo("সফল", "রসিদ প্রিন্ট হয়েছে!")
            except Exception as e:
                self.hide_loading()
                self.safe_showerror("ত্রুটি", str(e))

    # Loading popup
    def show_loading(self, text="লোড হচ্ছে..."):
        self.loading_popup = tk.Toplevel(self)
        self.loading_popup.title("প্রসেস চলছে")
        self.loading_popup.geometry("300x100")
        self.loading_popup.transient(self)
        self.loading_popup.grab_set()
        tk.Label(self.loading_popup, text=text, font=("Arial", 12)).pack(expand=True)
        self.loading_popup.update()

    def hide_loading(self):
        if hasattr(self, 'loading_popup'):
            self.loading_popup.destroy()

    # Thread-safe messagebox wrappers (to call from threads)
    def safe_showinfo(self, title, message):
        self.after(0, lambda: messagebox.showinfo(title, message))

    def safe_showwarning(self, title, message):
        self.after(0, lambda: messagebox.showwarning(title, message))

    def safe_showerror(self, title, message):
        self.after(0, lambda: messagebox.showerror(title, message))
