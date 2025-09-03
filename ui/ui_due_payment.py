import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
from fpdf import FPDF
import datetime
import sys
import os

# ====================================================================
# sys.path এ মূল ফোল্ডার যোগ করা হয়েছে, যাতে ইমপোর্ট ঠিকমতো কাজ করে।
# ====================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from due_payment_module.due_payment import (
        get_all_due_payments,
        add_due_payment,
        update_due_payment,
        delete_due_payment,
        get_customer_due_summary,
        sync_due_from_sales_and_service,
        get_due_payments_report
    )
except ImportError as e:
    messagebox.showerror("ইমপোর্ট ত্রুটি", f"due_payment_module/due_payment.py ফাইলটি খুঁজে পাওয়া যায়নি।\n\nError: {e}")
    sys.exit()

# --- Main Application Class ---
class DuePaymentUI:
    def __init__(self, master):
        self.master = master
        if isinstance(self.master, tk.Tk):
            self.master.title("বাকি ব্যবস্থাপনা")

        self.style = ttk.Style()
        self.style.configure("Header.TLabel", font=("Kalpurush", 22, "bold"), foreground="#1a237e", background="#f3f6fa")
        self.style.configure("TLabelframe", background="#f3f6fa")
        self.style.configure("TFrame", background="#f3f6fa")

        self.frame = ttk.Frame(master, padding=20, style="TFrame")
        self.frame.pack(fill=BOTH, expand=True)

        heading = ttk.Label(self.frame, text="বাকি ব্যবস্থাপনা", style="Header.TLabel", anchor="center")
        heading.grid(row=0, column=0, columnspan=10, pady=(0, 18), sticky="nsew")

        # ---------- Form Box ----------
        form_box = ttk.Labelframe(self.frame, text="নতুন/আপডেট", padding=(14,9))
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

        self.add_btn = ttk.Button(form_box, text="যোগ", bootstyle=SUCCESS, width=8, command=self.add_due)
        self.add_btn.grid(row=0, column=6, padx=2, pady=3)

        self.update_btn = ttk.Button(form_box, text="আপডেট", bootstyle=WARNING, width=8, command=self.update_due)
        self.update_btn.grid(row=0, column=7, padx=2, pady=3)

        self.delete_btn = ttk.Button(form_box, text="ডিলিট", bootstyle=DANGER, width=8, command=self.delete_due)
        self.delete_btn.grid(row=0, column=8, padx=2, pady=3)

        # ---------- Export Box ----------
        export_box = ttk.Labelframe(self.frame, text="এক্সপোর্ট", padding=(14,6))
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
        
        # ---------- Reports Box ----------
        reports_box = ttk.Labelframe(self.frame, text="রিপোর্ট", padding=(14,6))
        reports_box.grid(row=3, column=0, columnspan=10, sticky="ew", padx=1, pady=8)
        
        self.monthly_summary_btn = ttk.Button(reports_box, text="মাসিক সারসংক্ষেপ", width=16, bootstyle=INFO, command=self.show_monthly_summary)
        self.monthly_summary_btn.grid(row=0, column=1, padx=4)

        # নতুন রিফ্রেশ বাটন যোগ করা হলো
        self.refresh_btn = ttk.Button(reports_box, text="রিফ্রেশ", width=12, bootstyle=SUCCESS, command=self.refresh_data)
        self.refresh_btn.grid(row=0, column=2, padx=4)

        # ---------- Data Table ----------
        columns = ("ID","ক্রেতা","বাকি অর্থ","বাকি তারিখ","বিক্রয় আইডি","রেকর্ডের সময়")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", bootstyle="success")
        for col in columns:
            self.tree.heading(col, text=col)
            width = 120
            if col in ("ক্রেতা","রেকর্ডের সময়"):
                width=160
            self.tree.column(col, anchor="center", width=width)
        self.tree.grid(row=4, column=0, columnspan=7, sticky="nsew", pady=(10,0), padx=(3,3))
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        vbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        hbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=vbar.set, xscroll=hbar.set)
        vbar.grid(row=4, column=7, sticky="ns", pady=(10,0))
        hbar.grid(row=5, column=0, columnspan=7, sticky="ew", padx=(3,3))

        for i in range(7):
            self.frame.columnconfigure(i, weight=1)
        self.frame.rowconfigure(4, weight=1)
        self.tree.tag_configure("evenrow", background="#f5f9ff")
        self.tree.tag_configure("oddrow", background="#ffffff")

        # ---------- Customer Summary ----------
        summary_box = ttk.Labelframe(self.frame, text="কাস্টমারের সারসংক্ষেপ", padding=(14,6))
        summary_box.grid(row=6, column=0, columnspan=8, sticky="ew", padx=1, pady=8)

        ttk.Label(summary_box, text="ক্রেতার নাম:").grid(row=0, column=0, padx=2, pady=3)
        self.summary_customer_entry = ttk.Entry(summary_box, width=18)
        self.summary_customer_entry.grid(row=0, column=1, padx=2)

        self.summary_btn = ttk.Button(summary_box, text="দেখুন", width=10, bootstyle=INFO, command=self.show_customer_summary)
        self.summary_btn.grid(row=0, column=2, padx=2)

        self.summary_label = ttk.Label(summary_box, text="", anchor="w")
        self.summary_label.grid(row=1, column=0, columnspan=8, sticky="w", padx=2, pady=4)

        # --- Auto Sync Feature ---
        self.auto_sync()
        self.refresh_tree()
        
    def auto_sync(self):
        """স্বয়ংক্রিয়ভাবে ডেটা সিঙ্ক্রোনাইজ করে এবং টেবিল রিফ্রেশ করে"""
        try:
            sync_due_from_sales_and_service()
            self.refresh_tree()
            # This print statement is for debugging and will not show on the UI
            print("Due payments synced successfully in the background.")
        except Exception as e:
            print(f"স্বয়ংক্রিয় সিঙ্ক্রোনাইজেশন ত্রুটি: {e}")
        finally:
            self.master.after(30000, self.auto_sync)  # প্রতি 30 সেকেন্ড পর পর রান হবে।

    def refresh_data(self):
        """ম্যানুয়ালি ডেটা সিঙ্ক্রোনাইজ করে এবং টেবিল রিফ্রেশ করে"""
        try:
            sync_due_from_sales_and_service()
            self.refresh_tree()
            messagebox.showinfo("সফল", "ডেটা সফলভাবে রিফ্রেশ করা হয়েছে।")
        except Exception as e:
            messagebox.showerror("ত্রুটি", f"ডেটা রিফ্রেশ করার সময় একটি ত্রুটি হয়েছে: {e}")

    # ---------------------------
    # Tree Methods
    # ---------------------------
    def refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # ডেটাবেস থেকে ডেটা লোড করা
        data = get_all_due_payments()
        
        for idx, due in enumerate(data):
            tags = ("evenrow",) if idx%2==0 else ("oddrow",)
            self.tree.insert("", tk.END, values=(
                due.get("id", "N/A"),
                due.get("customer", "N/A"),
                due.get("amount", 0),
                due.get("due_date", "N/A"),
                due.get("sale_id", "N/A"),
                due.get("date", "N/A")),
                tags=tags
            )
        self.selected_id = None

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
            self.due_date_entry.insert(0, values[3])
        else:
            self.selected_id = None

    # ---------------------------
    # CRUD Methods
    # ---------------------------
    def add_due(self):
        customer = self.customer_entry.get().strip()
        amount = self.amount_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        if not customer or not amount or not due_date:
            messagebox.showwarning("ত্রুটি","সকল তথ্য পূরণ করুন")
            return
        try:
            add_due_payment(customer, float(amount), due_date, sale_id=None)
            messagebox.showinfo("সফল","বাকি যোগ হয়েছে।")
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

    def update_due(self):
        if not hasattr(self,"selected_id") or not self.selected_id:
            messagebox.showwarning("ত্রুটি","সিলেক্ট করুন কোন বাকি আপডেট করবেন।")
            return
        customer = self.customer_entry.get().strip()
        amount = self.amount_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        if not customer or not amount or not due_date:
            messagebox.showwarning("ত্রুটি","সকল তথ্য পূরণ করুন")
            return
        try:
            update_due_payment(self.selected_id, customer, float(amount), due_date)
            messagebox.showinfo("সফল","বাকি আপডেট হয়েছে।")
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

    def delete_due(self):
        if not hasattr(self,"selected_id") or not self.selected_id:
            messagebox.showwarning("ত্রুটি","সিলেক্ট করুন কোন বাকি মুছবেন।")
            return
        sure = messagebox.askyesno("নিশ্চিত?","আপনি কি বাকি সত্যিই মুছে ফেলতে চান?")
        if not sure:
            return
        try:
            delete_due_payment(self.selected_id)
            messagebox.showinfo("সফল","বাকি ডিলিট হয়েছে।")
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

    # ---------------------------
    # Export Methods
    # ---------------------------
    def export_pdf(self):
        try:
            import fpdf
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("ত্রুটি", "Please install the fpdf2 library: pip install fpdf2")
            return

        start_date = self.export_start.get().strip() or None
        end_date = self.export_end.get().strip() or None
        
        # ডেটাবেস থেকে রিপোর্ট ডেটা লোড করা
        filtered_data = get_due_payments_report(start_date, end_date)

        if not filtered_data:
            messagebox.showwarning("ত্রুটি","এই তারিখে কোনো ডেটা নেই।")
            return
        
        class MyFPDF(FPDF):
            def header(self):
                self.set_font('Kalpurush', '', 12)
                self.cell(0, 10, 'বাকি ব্যবস্থাপনা রিপোর্ট', 0, 1, 'C')

            def footer(self):
                self.set_y(-15)
                self.set_font('Kalpurush', '', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        pdf = MyFPDF()
        try:
            pdf.add_font("Kalpurush", "", "Kalpurush.ttf", uni=True)
        except Exception as e:
            messagebox.showerror("ফন্ট ত্রুটি", f"ফন্ট ফাইল পাওয়া যায়নি। অনুগ্রহ করে 'Kalpurush.ttf' ফাইলটি একই ফোল্ডারে রাখুন।\n\nError: {e}")
            return
        
        pdf.set_font("Kalpurush", "", 10)
        pdf.add_page()

        columns = ["আইডি","ক্রেতা","বাকি অর্থ","তারিখ","বিক্রয় আইডি","রেকর্ড"]
        col_widths=[18,38,28,26,26,36]
        
        pdf.set_font("Kalpurush", '', 10)
        for idx, col in enumerate(columns):
            pdf.cell(col_widths[idx], 10, col, 1, 0, "C")
        pdf.ln()

        for row in filtered_data:
            lst=[str(row.get("id")),str(row.get("customer")),str(row.get("amount")),str(row.get("due_date")),str(row.get("sale_id")),str(row.get("date"))]
            for idx,item in enumerate(lst):
                pdf.cell(col_widths[idx], 8, item, 1, 0, "L")
            pdf.ln()

        try:
            pdf_path = "due_payments_report.pdf"
            pdf.output(pdf_path)
            messagebox.showinfo("সফল","PDF Report: due_payments_report.pdf")
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

    def export_excel(self):
        start_date = self.export_start.get().strip() or None
        end_date = self.export_end.get().strip() or None
        
        # ডেটাবেস থেকে রিপোর্ট ডেটা লোড করা
        filtered_data = get_due_payments_report(start_date, end_date)
        
        if not filtered_data:
            messagebox.showwarning("ত্রুটি","এই তারিখে কোনো ডেটা নেই।")
            return
        df = pd.DataFrame(filtered_data)
        try:
            df.to_excel("due_payments_report.xlsx",index=False)
            messagebox.showinfo("সফল","Excel Report: due_payments_report.xlsx")
        except Exception as e:
            messagebox.showerror("ত্রুটি",str(e))

    # ---------------------------
    # Reports Methods
    # ---------------------------
    def show_monthly_summary(self):
        try:
            # ডেটাবেস থেকে সমস্ত ডেটা লোড করা
            all_dues = get_all_due_payments()
            
            monthly_summary = {}
            for due in all_dues:
                try:
                    # 'due_date' ব্যবহার করে মাসিক সারাংশ গণনা
                    due_date = datetime.datetime.strptime(due.get("due_date"), "%Y-%m-%d")
                    month_year = due_date.strftime("%Y-%m")
                    if month_year not in monthly_summary:
                        monthly_summary[month_year] = 0
                    monthly_summary[month_year] += due.get("amount", 0)
                except (ValueError, TypeError, KeyError) as e:
                    print(f"Error processing due record for monthly summary: {due}. Skipping. Error: {e}")
                    continue

            if not monthly_summary:
                messagebox.showinfo("মাসিক সারসংক্ষেপ", "কোনো বাকি ডেটা নেই।")
                return
            
            report_text = "মাসিক সারসংক্ষেপ:\n"
            for month, amount in monthly_summary.items():
                report_text += f"\n{month}: {amount} টাকা"
            
            messagebox.showinfo("মাসিক সারসংক্ষেপ", report_text)
        except Exception as e:
            messagebox.showerror("ত্রুটি", f"মাসিক সারসংক্ষেপ লোড করার সময় একটি ত্রুটি হয়েছে। দয়া করে নিশ্চিত করুন যে সকল ডেটা সঠিক এবং সম্পূর্ণ।\n\nError: {e}")

    # ---------------------------
    # Customer Summary
    # ---------------------------
    def show_customer_summary(self):
        customer_name = self.summary_customer_entry.get().strip()
        if not customer_name:
            messagebox.showwarning("ত্রুটি","ক্রেতার নাম লিখুন")
            return
        try:
            summary = get_customer_due_summary(customer_name)
            text = f"ক্রেতা: {customer_name} | মোট বাকি: {summary['total_due']} | Sales বাকি: {summary['total_sales_due']} | Service বাকি: {summary['total_service_due']}"
            self.summary_label.config(text=text)
        except Exception as e:
            messagebox.showerror("ত্রুটি", str(e))

if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = DuePaymentUI(root)
    root.mainloop()
