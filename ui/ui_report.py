import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

from report.report import get_sales_report_by_date, get_monthly_profit_report
from report.excel_export import export_sales_report_excel, export_profit_report_excel
from report.pdf_export import export_sales_report_pdf, export_profit_report_pdf


class ReportUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.tabControl = ttk.Notebook(self)
        self.sales_tab = ttk.Frame(self.tabControl)
        self.profit_tab = ttk.Frame(self.tabControl)

        self.tabControl.add(self.sales_tab, text='📅 বিক্রয় রিপোর্ট')
        self.tabControl.add(self.profit_tab, text='📊 লাভ রিপোর্ট')
        self.tabControl.pack(expand=1, fill="both")

        self.create_sales_tab()
        self.create_profit_tab()

    # ------------------ Sales Tab ------------------
    def create_sales_tab(self):
        frame = ttk.Frame(self.sales_tab)
        frame.pack(pady=10, fill="x")

        ttk.Label(frame, text="শুরুর তারিখ (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(frame)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="শেষ তারিখ (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(frame)
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(frame, text="রিপোর্ট দেখাও", command=self.load_sales_report).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(frame, text="এক্সেল এক্সপোর্ট", command=lambda: self.ask_filename_and_run(self.export_sales_to_excel)).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(frame, text="PDF এক্সপোর্ট", command=lambda: self.ask_filename_and_run(self.export_sales_to_pdf)).grid(row=0, column=6, padx=5, pady=5)

        self.sales_tree = ttk.Treeview(self.sales_tab, columns=("ID", "Product", "Qty", "Price", "Total", "Date"), show='headings')
        for col in self.sales_tree["columns"]:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=120, anchor="center")
        self.sales_tree.pack(pady=10, fill="both", expand=True)

        self.total_sales_label = ttk.Label(self.sales_tab, text="মোট বিক্রয়: 0.00 টাকা", font=("Helvetica", 12, "bold"))
        self.total_sales_label.pack(pady=5)

    def load_sales_report(self):
        start = self.start_date_entry.get().strip()
        end = self.end_date_entry.get().strip()

        if not start or not end:
            messagebox.showwarning("⚠️ সতর্কতা", "তারিখ দিন")
            return

        try:
            rows = get_sales_report_by_date(start, end)
            self.sales_tree.delete(*self.sales_tree.get_children())

            total_sales = 0.0
            for r in rows:
                self.sales_tree.insert('', 'end', values=(
                    r['sale_id'], r['product_name'], r['quantity'], r['unit_price'], r['total_price'], r['sale_date']
                ))
                total_sales += r['total_price']

            self.total_sales_label.config(text=f"মোট বিক্রয়: {total_sales:.2f} টাকা")

        except Exception as e:
            messagebox.showerror("❌ ত্রুটি", f"রিপোর্ট লোড করতে সমস্যা হয়েছে:\n{e}")

    def ask_filename_and_run(self, export_func):
        """UI থেকে ফাইল নাম নিয়ে ব্যাকগ্রাউন্ড থ্রেডে প্রসেস চালানো হবে"""
        if "excel" in export_func.__name__:
            filetypes = [("Excel Files", "*.xlsx")]
            defext = ".xlsx"
        else:
            filetypes = [("PDF Files", "*.pdf")]
            defext = ".pdf"

        filename = filedialog.asksaveasfilename(defaultextension=defext, filetypes=filetypes)
        if filename:
            threading.Thread(target=export_func, args=(filename,), daemon=True).start()

    def export_sales_to_excel(self, filename):
        start = self.start_date_entry.get().strip()
        end = self.end_date_entry.get().strip()
        try:
            rows = get_sales_report_by_date(start, end)
            if not rows:
                self.show_message("ℹ️ তথ্য", "কোনো ডেটা পাওয়া যায়নি।", "info")
                return
            export_sales_report_excel(rows, start, end, filename)
            self.show_message("✅ সফল", "বিক্রয় রিপোর্ট Excel এ এক্সপোর্ট হয়েছে।", "info")
        except Exception as e:
            self.show_message("❌ ত্রুটি", f"এক্সপোর্ট করতে সমস্যা হয়েছে:\n{e}", "error")

    def export_sales_to_pdf(self, filename):
        start = self.start_date_entry.get().strip()
        end = self.end_date_entry.get().strip()
        try:
            rows = get_sales_report_by_date(start, end)
            if not rows:
                self.show_message("ℹ️ তথ্য", "কোনো ডেটা পাওয়া যায়নি।", "info")
                return
            export_sales_report_pdf(rows, start, end, filename)
            self.show_message("✅ সফল", "PDF রিপোর্ট সফলভাবে সংরক্ষণ হয়েছে।", "info")
        except Exception as e:
            self.show_message("❌ ত্রুটি", f"PDF তৈরি করতে সমস্যা হয়েছে:\n{e}", "error")

    # ------------------ Profit Tab ------------------
    def create_profit_tab(self):
        frame = ttk.Frame(self.profit_tab)
        frame.pack(pady=10, fill="x")

        ttk.Label(frame, text="মাস (১-১২):").grid(row=0, column=0, padx=5, pady=5)
        self.month_entry = ttk.Entry(frame)
        self.month_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="বছর (YYYY):").grid(row=0, column=2, padx=5, pady=5)
        self.year_entry = ttk.Entry(frame)
        self.year_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(frame, text="রিপোর্ট দেখাও", command=self.load_profit_report).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(frame, text="এক্সেল এক্সপোর্ট", command=lambda: self.ask_filename_and_run(self.export_profit_to_excel)).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(frame, text="PDF এক্সপোর্ট", command=lambda: self.ask_filename_and_run(self.export_profit_to_pdf)).grid(row=0, column=6, padx=5, pady=5)

        self.profit_tree = ttk.Treeview(self.profit_tab, columns=("Product", "Qty", "ক্রয়মূল্য", "বিক্রয়মূল্য", "মোট", "লাভ", "Date"), show='headings')
        for col in self.profit_tree["columns"]:
            self.profit_tree.heading(col, text=col)
            self.profit_tree.column(col, width=120, anchor="center")
        self.profit_tree.pack(pady=10, fill="both", expand=True)

        self.total_profit_label = ttk.Label(self.profit_tab, text="মোট লাভ: 0.00 টাকা", font=("Helvetica", 12, "bold"))
        self.total_profit_label.pack(pady=5)

    def load_profit_report(self):
        month = self.month_entry.get().strip()
        year = self.year_entry.get().strip()
        try:
            data = get_monthly_profit_report(month, year)
            self.profit_tree.delete(*self.profit_tree.get_children())
            total_profit = data.get('total_profit', 0)
            for r in data['details']:
                self.profit_tree.insert('', 'end', values=(
                    r['product_name'], r['quantity'], r['purchase_price'], r['sale_price'],
                    r['total_sell'], r['profit'], r['sale_date']
                ))
            self.total_profit_label.config(text=f"মোট লাভ: {total_profit:.2f} টাকা")
        except Exception as e:
            messagebox.showerror("❌ ত্রুটি", f"রিপোর্ট লোড করতে সমস্যা হয়েছে:\n{e}")

    def export_profit_to_excel(self, filename):
        month = self.month_entry.get().strip()
        year = self.year_entry.get().strip()
        try:
            data = get_monthly_profit_report(month, year)
            if not data['details']:
                self.show_message("ℹ️ তথ্য", "কোনো ডেটা পাওয়া যায়নি।", "info")
                return
            export_profit_report_excel(data, month, year, filename)
            self.show_message("✅ সফল", "লাভ রিপোর্ট Excel এ এক্সপোর্ট হয়েছে।", "info")
        except Exception as e:
            self.show_message("❌ ত্রুটি", f"এক্সপোর্ট করতে সমস্যা হয়েছে:\n{e}", "error")

    def export_profit_to_pdf(self, filename):
        month = self.month_entry.get().strip()
        year = self.year_entry.get().strip()
        try:
            data = get_monthly_profit_report(month, year)
            if not data['details']:
                self.show_message("ℹ️ তথ্য", "কোনো ডেটা পাওয়া যায়নি।", "info")
                return
            export_profit_report_pdf(data, month, year, filename)
            self.show_message("✅ সফল", "PDF রিপোর্ট সফলভাবে সংরক্ষণ হয়েছে।", "info")
        except Exception as e:
            self.show_message("❌ ত্রুটি", f"PDF তৈরি করতে সমস্যা হয়েছে:\n{e}", "error")

    # ------------------ Helper ------------------
    def show_message(self, title, message, mtype="info"):
        """Main thread থেকে messagebox দেখাবে"""
        self.after(0, lambda: getattr(messagebox, mtype)(title, message))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("রিপোর্ট - SmartShop POS")
    root.geometry("950x600")
    app = ReportUI(root)
    root.mainloop()
