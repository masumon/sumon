# ui/ui_recharge.py

import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import pandas as pd
from db import add_recharge, get_all_recharges, get_connection

PAGE_SIZE = 20

class RechargeUI(ttk.Frame):
    """রিচার্জ ব্যবস্থাপনা UI"""
    def __init__(self, master=None):
        super().__init__(master)
        self.frame = self
        self.pack(fill="both", expand=True)
        self.selected_recharge_id = None
        self.current_page = 1
        self.filtered_data = None
        self.hovered_row = None

        # ===== স্টাইল =====
        self.style = ttk.Style()
        self.style.configure(
            "Header.TLabel",
            font=("Kalpurush", 22, "bold"),
            foreground="#1a237e",
            background="#f3f6fa",
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Kalpurush", 12, "bold"),
            foreground="#0d47a1"
        )
        self.style.configure(
            "Treeview",
            font=("Kalpurush", 11)
        )

        # ===== উপরের বড় শিরোনাম =====
        header_label = ttk.Label(self, text="রিচার্জ ব্যবস্থাপনা", style="Header.TLabel")
        header_label.pack(pady=(10, 20))

        # ===== মূল ফর্ম =====
        self.create_widgets()
        self.load_recharges()

    # ---------------- উইজেট ----------------
    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", padx=10, pady=5)

        # এন্ট্রি ফিল্ড
        ttk.Label(form_frame, text="গ্রাহকের নাম:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.customer_name_entry = ttk.Entry(form_frame, width=30)
        self.customer_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="মোবাইল:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.mobile_entry = ttk.Entry(form_frame, width=30)
        self.mobile_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="অপারেটর:").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.operator_combo = ttk.Combobox(
            form_frame,
            values=["রবি", "গ্রামীণফোন", "বাংলালিঙ্ক", "টেলিটক", "এয়ারটেল", "বিকাশ", "রকেট"],
            state="readonly",
            width=28
        )
        self.operator_combo.grid(row=2, column=1, padx=5, pady=5)
        self.operator_combo.set("রবি")

        ttk.Label(form_frame, text="টাকার পরিমাণ:").grid(row=3, column=0, sticky=W, padx=5, pady=5)
        self.amount_entry = ttk.Entry(form_frame, width=30)
        self.amount_entry.grid(row=3, column=1, padx=5, pady=5)

        # বাটন
        self.add_btn = ttk.Button(form_frame, text="রিচার্জ যোগ করুন", command=self.add_recharge_entry, bootstyle="success")
        self.add_btn.grid(row=4, column=0, pady=10)
        self.update_btn = ttk.Button(form_frame, text="রিচার্জ আপডেট করুন", command=self.update_recharge_entry, bootstyle="warning")
        self.update_btn.grid(row=4, column=1, pady=10)
        self.delete_btn = ttk.Button(form_frame, text="রিচার্জ মুছুন", command=self.delete_recharge_entry, bootstyle="danger")
        self.delete_btn.grid(row=4, column=2, pady=10)
        self.refresh_btn = ttk.Button(form_frame, text="রিফ্রেশ", command=self.load_recharges, bootstyle="info")
        self.refresh_btn.grid(row=4, column=3, pady=10, padx=10)

        # ফিল্টার
        ttk.Label(form_frame, text="তারিখ ফিল্টার (YYYY-MM-DD):").grid(row=5, column=0, sticky=W, padx=5, pady=5)
        self.filter_entry = ttk.Entry(form_frame, width=20)
        self.filter_entry.grid(row=5, column=1, padx=5, pady=5)
        self.filter_btn = ttk.Button(form_frame, text="ফিল্টার প্রয়োগ করুন", command=self.apply_date_filter, bootstyle="secondary")
        self.filter_btn.grid(row=5, column=2, padx=5, pady=5)

        ttk.Label(form_frame, text="মাস/বছর (MM-YYYY):").grid(row=6, column=0, sticky=W, padx=5, pady=5)
        self.month_filter_entry = ttk.Entry(form_frame, width=20)
        self.month_filter_entry.grid(row=6, column=1, padx=5, pady=5)
        self.month_filter_btn = ttk.Button(form_frame, text="মাস ফিল্টার প্রয়োগ করুন", command=self.apply_month_filter, bootstyle="secondary")
        self.month_filter_btn.grid(row=6, column=2, padx=5, pady=5)

        ttk.Label(form_frame, text="সার্চ:").grid(row=7, column=0, sticky=W, padx=5, pady=5)
        self.search_entry = ttk.Entry(form_frame, width=30)
        self.search_entry.grid(row=7, column=1, padx=5, pady=5)
        self.search_btn = ttk.Button(form_frame, text="খুঁজুন", command=self.apply_search, bootstyle="secondary")
        self.search_btn.grid(row=7, column=2, padx=5, pady=5)

        # এক্সপোর্ট
        self.export_btn = ttk.Button(form_frame, text="এক্সেল-এ রপ্তানি করুন", command=self.export_to_excel, bootstyle="success")
        self.export_btn.grid(row=8, column=0, columnspan=2, pady=10)
        self.pdf_export_btn = ttk.Button(form_frame, text="PDF-এ রপ্তানি করুন", command=self.export_to_pdf, bootstyle="primary")
        self.pdf_export_btn.grid(row=8, column=2, columnspan=2, pady=10)

        # Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("ID","Customer","Mobile","Operator","Amount","Date"), show="headings", bootstyle="info")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=50, width=100, anchor=CENTER)
        self.tree.pack(fill="both", expand=True, side="left")

        # Scrollbars
        self.v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=self.v_scroll.set, xscroll=self.h_scroll.set)
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")

        # Row tags
        self.tree.tag_configure('oddrow', background="#e8f0ff")
        self.tree.tag_configure('evenrow', background="#ffffff")
        self.tree.tag_configure('selectedrow', background="#c6f7d0")
        self.tree.tag_configure('hover', background="#d1e9ff")

        # Pagination
        page_frame = ttk.Frame(self)
        page_frame.pack(pady=5)
        self.prev_btn = ttk.Button(page_frame, text="<< পূর্ববর্তী", command=self.prev_page, bootstyle="secondary")
        self.prev_btn.grid(row=0, column=0, padx=10)
        self.page_label = ttk.Label(page_frame, text="পৃষ্ঠা 1")
        self.page_label.grid(row=0, column=1, padx=10)
        self.next_btn = ttk.Button(page_frame, text="পরবর্তী >>", command=self.next_page, bootstyle="secondary")
        self.next_btn.grid(row=0, column=2, padx=10)

        # Bindings
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Motion>", self.on_hover)
        self.tree.bind("<MouseWheel>", self.on_mousewheel)

    # ---------------- CRUD ----------------
    def add_recharge_entry(self):
        cname = self.customer_name_entry.get().strip()
        mobile = self.mobile_entry.get().strip()
        operator = self.operator_combo.get().strip()
        amount_text = self.amount_entry.get().strip()

        if not cname or not mobile or not operator or not amount_text:
            messagebox.showerror("ত্রুটি", "সকল ফিল্ড পূরণ করুন!")
            return

        try:
            amount = float(amount_text)
        except:
            messagebox.showerror("ত্রুটি", "টাকার পরিমাণ অবশ্যই সংখ্যা হতে হবে!")
            return

        add_recharge({
            "customer_name": cname,
            "mobile": mobile,
            "operator": operator,
            "amount": amount,
            "date": datetime.now()
        })

        messagebox.showinfo("সফল", "রিচার্জ যোগ হয়েছে!")
        self.clear_entries()
        self.load_recharges()

    def update_recharge_entry(self):
        if not self.selected_recharge_id:
            messagebox.showerror("ত্রুটি","আপডেট করতে একটি এন্ট্রি নির্বাচন করুন!")
            return
        cname=self.customer_name_entry.get().strip()
        mobile=self.mobile_entry.get().strip()
        operator=self.operator_combo.get().strip()
        amount_text=self.amount_entry.get().strip()
        if not cname or not mobile or not operator or not amount_text:
            messagebox.showerror("ত্রুটি","সকল ফিল্ড পূরণ করুন!")
            return
        try: amount=float(amount_text)
        except: messagebox.showerror("ত্রুটি","টাকার পরিমাণ অবশ্যই সংখ্যা হতে হবে!"); return
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute(
            "UPDATE recharge SET customer_name=?,mobile=?,operator=?,amount=? WHERE id=?",
            (cname,mobile,operator,amount,self.selected_recharge_id)
        )
        conn.commit(); conn.close()
        messagebox.showinfo("সফল","রিচার্জ আপডেট হয়েছে!")
        self.clear_entries()
        self.load_recharges()

    def delete_recharge_entry(self):
        if not self.selected_recharge_id:
            messagebox.showerror("ত্রুটি","মুছতে একটি এন্ট্রি নির্বাচন করুন!")
            return
        if messagebox.askyesno("নিশ্চিতকরণ","নির্বাচিত রিচার্জ মুছে ফেলবেন?"):
            conn=get_connection(); cursor=conn.cursor()
            cursor.execute("DELETE FROM recharge WHERE id=?",(self.selected_recharge_id,))
            conn.commit(); conn.close()
            messagebox.showinfo("মুছে ফেলা হয়েছে","রিচার্জ মুছে ফেলা হয়েছে!")
            self.clear_entries()
            self.load_recharges()

    # ---------------- Selection ----------------
    def on_tree_select(self,event):
        sel=self.tree.selection()
        if sel:
            values=self.tree.item(sel[0],"values")
            self.selected_recharge_id=values[0]
            self.customer_name_entry.delete(0,tk.END); self.customer_name_entry.insert(0,values[1])
            self.mobile_entry.delete(0,tk.END); self.mobile_entry.insert(0,values[2])
            self.operator_combo.set(values[3])
            self.amount_entry.delete(0,tk.END); self.amount_entry.insert(0,values[4])
            for idx,item in enumerate(self.tree.get_children()):
                self.tree.item(item,tags=('evenrow' if idx%2==0 else 'oddrow',))
            self.tree.item(sel[0],tags=('selectedrow',))

    def clear_entries(self):
        self.customer_name_entry.delete(0,tk.END)
        self.mobile_entry.delete(0,tk.END)
        self.amount_entry.delete(0,tk.END)
        self.operator_combo.set("রবি")
        self.selected_recharge_id=None

    # ---------------- Load / Pagination / Filter / Search ----------------
    def load_recharges(self,recharges=None):
        for item in self.tree.get_children(): self.tree.delete(item)
        if recharges is None: recharges=get_all_recharges()
        self.filtered_data=recharges
        self.current_page=1
        self.show_page()

    def show_page(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        start=(self.current_page-1)*PAGE_SIZE
        end=start+PAGE_SIZE
        page_items=self.filtered_data[start:end]
        for idx,r in enumerate(page_items):
            tag='evenrow' if idx%2==0 else 'oddrow'
            self.tree.insert("",tk.END,values=(r["id"],r["customer_name"],r["mobile"],r["operator"],r["amount"],r["date"]),tags=(tag,))
        total_pages=max(1,(len(self.filtered_data)-1)//PAGE_SIZE+1)
        self.page_label.config(text=f"পৃষ্ঠা {self.current_page} / {total_pages}")

    def next_page(self):
        total_pages=max(1,(len(self.filtered_data)-1)//PAGE_SIZE+1)
        if self.current_page<total_pages: self.current_page+=1; self.show_page()

    def prev_page(self):
        if self.current_page>1: self.current_page-=1; self.show_page()

    def apply_date_filter(self):
        text=self.filter_entry.get().strip()
        if not text: self.load_recharges(); return
        try: datetime.strptime(text,"%Y-%m-%d")
        except: messagebox.showerror("ত্রুটি","তারিখ অবশ্যই YYYY-MM-DD ফরম্যাটে হতে হবে!"); return
        all_data=get_all_recharges()
        filtered=[r for r in all_data if r["date"].startswith(text)]
        self.load_recharges(filtered)

    def apply_month_filter(self):
        text=self.month_filter_entry.get().strip()
        if not text: self.load_recharges(); return
        try: datetime.strptime(text,"%m-%Y")
        except: messagebox.showerror("ত্রুটি","মাস/বছর অবশ্যই MM-YYYY ফরম্যাটে হতে হবে!"); return
        all_data=get_all_recharges()
        filtered=[r for r in all_data if datetime.strptime(r["date"],"%Y-%m-%d %H:%M:%S").strftime("%m-%Y")==text]
        self.load_recharges(filtered)

    def apply_search(self):
        text=self.search_entry.get().strip().lower()
        if not text: self.load_recharges(); return
        all_data=get_all_recharges()
        filtered=[r for r in all_data if text in r["customer_name"].lower() or text in r["mobile"].lower() or text in r["operator"].lower()]
        self.load_recharges(filtered)

    # ---------------- Export ----------------
    def export_to_excel(self):
        items=self.tree.get_children()
        if not items: messagebox.showerror("ত্রুটি","রপ্তানি করার জন্য ডেটা নেই!"); return
        data=[]
        for item in items:
            values=self.tree.item(item,"values")
            data.append({"আইডি":values[0],"গ্রাহক":values[1],"মোবাইল":values[2],"অপারেটর":values[3],"টাকার পরিমাণ":values[4],"তারিখ":values[5]})
        df=pd.DataFrame(data)
        file_path=filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel ফাইল","*.xlsx")])
        if file_path: df.to_excel(file_path,index=False); messagebox.showinfo("সফল",f"ডেটা {file_path} এ রপ্তানি করা হয়েছে!")

    # ---------------- PDF Export ----------------
    def export_to_pdf(self):
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("ত্রুটি","FPDF লাইব্রেরি ইনস্টল করুন: pip install fpdf")
            return

        items = self.tree.get_children()
        if not items:
            messagebox.showerror("ত্রুটি","PDF তৈরি করার জন্য ডেটা নেই!")
            return

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ===== বাংলা ফন্ট যোগ =====
        font_path = r"D:\abo_enterprise_project\smartshop_pos\report\fonts\Kalpurush.ttf"
        pdf.add_font("Kalpurush", "", font_path, uni=True)
        pdf.add_font("Kalpurush", "B", font_path, uni=True)

        # ===== শিরোনাম =====
        pdf.set_font("Kalpurush", "B", 16)
        pdf.cell(0, 12, "রিচার্জ রিপোর্ট", ln=True, align="C")
        pdf.set_font("Kalpurush", "", 10)
        pdf.cell(0, 8, f"তৈরির তারিখ: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", ln=True, align="R")
        pdf.ln(5)

        # ===== কলাম ও ডেটা সংগ্রহ =====
        headers = ["ID","গ্রাহক","মোবাইল","অপারেটর","টাকার পরিমাণ","তারিখ"]
        data_rows = [self.tree.item(i,"values") for i in items]

        # ===== কলাম প্রস্থ অটো ক্যালকুলেশন =====
        col_widths=[]
        pdf.set_font("Kalpurush","B",12)
        for col_idx in range(len(headers)):
            max_width=pdf.get_string_width(headers[col_idx])+6
            for row in data_rows:
                cell_width=pdf.get_string_width(str(row[col_idx]))+6
                if cell_width>max_width: max_width=cell_width
            col_widths.append(max_width)

        # ===== হেডার =====
        pdf.set_fill_color(200,200,200)
        for idx,h in enumerate(headers):
            pdf.cell(col_widths[idx],10,h,border=1,align="C",fill=True)
        pdf.ln()

        # ===== ডেটা =====
        pdf.set_font("Kalpurush","",12)
        fill=False
        for row in data_rows:
            for idx,v in enumerate(row):
                pdf.cell(col_widths[idx],8,str(v),border=1,align="C",fill=fill)
            pdf.ln(); fill=not fill

        # ===== Footer =====
        for i in range(1,pdf.page_no()+1):
            pdf.page=i
            pdf.set_y(-10)
            pdf.set_font("Kalpurush","",8)
            pdf.cell(0,10,f"পৃষ্ঠা {i}",align="C")

        file_path=filedialog.asksaveasfilename(defaultextension=".pdf",filetypes=[("PDF File","*.pdf")])
        if file_path: pdf.output(file_path); messagebox.showinfo("সফল",f"PDF {file_path} এ সংরক্ষিত হয়েছে!")

    # ---------------- Hover Effect ----------------
    def on_hover(self,event):
        row_id=self.tree.identify_row(event.y)
        if self.hovered_row!=row_id:
            if self.hovered_row:
                tags=self.tree.item(self.hovered_row,"tags")
                self.tree.item(self.hovered_row,tags=tags)
            if row_id: self.tree.item(row_id,tags=("hover",))
            self.hovered_row=row_id

    # ---------------- Mouse Wheel ----------------
    def on_mousewheel(self,event):
        self.tree.yview_scroll(int(-1*(event.delta/120)),"units")
