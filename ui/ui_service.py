import sys
import os
import sqlite3
from datetime import datetime, timedelta
import threading
import time
import webbrowser
import pandas as pd
from fpdf import FPDF

# ttkbootstrap / tkinter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog, simpledialog

# ---------------- Paths ----------------
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "smartshop.db")

# ---------------- Database Helpers ----------------
def execute_db(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetchall_db(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

# ---------------- Service Functions ----------------
def get_all_service_types():
    # আপনার টেবিলে id, name, description আছে—এখানে সেগুলোই ধরা হয়েছে
    return fetchall_db("SELECT id, name, description FROM service_types")

def add_service_type(name, description):
    try:
        execute_db("INSERT INTO service_types (name, description) VALUES (?, ?)", (name, description))
        return True
    except Exception as e:
        print("Add Service Type Error:", e)
        return False

def update_service_type(type_id, name, description):
    try:
        execute_db("UPDATE service_types SET name=?, description=? WHERE id=?", (name, description, type_id))
        return True
    except Exception as e:
        print("Update Service Type Error:", e)
        return False

def delete_service_type(type_id):
    try:
        execute_db("DELETE FROM service_types WHERE id=?", (type_id,))
        return True
    except Exception as e:
        print("Delete Service Type Error:", e)
        return False

def get_all_service_requests(filters=None):
    query = """
    SELECT r.id, t.name, r.customer_name, r.details, r.status, r.price, 
           r.due_amount, r.payment_status, r.requested_at, r.completed_at
    FROM service_requests r
    LEFT JOIN service_types t ON r.service_type_id = t.id
    """
    params = []
    if filters:
        conditions = []
        if "status" in filters:
            conditions.append("r.status=?")
            params.append(filters["status"])
        if "payment_status" in filters:
            conditions.append("r.payment_status=?")
            params.append(filters["payment_status"])
        if "service_type" in filters:
            conditions.append("t.name=?")
            params.append(filters["service_type"])
        if "from_date" in filters and "to_date" in filters:
            conditions.append("r.requested_at BETWEEN ? AND ?")
            params.append(filters["from_date"])
            params.append(filters["to_date"])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY r.id DESC"
    return fetchall_db(query, tuple(params))

def add_service_request(service_type_id, customer_name, details, price):
    try:
        execute_db("""
        INSERT INTO service_requests
        (service_type_id, customer_name, details, price, status, due_amount, payment_status, requested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (service_type_id, customer_name, details, price, "Pending", price, "Unpaid", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return True
    except Exception as e:
        print("Add Service Request Error:", e)
        return False

def delete_service_request(request_id):
    try:
        execute_db("DELETE FROM service_requests WHERE id=?", (request_id,))
        return True
    except Exception as e:
        print("Delete Request Error:", e)
        return False

def update_service_request_status(request_id, status):
    try:
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status=="Completed" else None
        execute_db("UPDATE service_requests SET status=?, completed_at=? WHERE id=?", (status, completed_at, request_id))
        if status=="Completed":
            generate_invoice_pdf(request_id)
        return True
    except Exception as e:
        print("Status Update Error:", e)
        return False

def update_request_payment(request_id, amount):
    try:
        data = fetchall_db("SELECT price, due_amount FROM service_requests WHERE id=?", (request_id,))[0]
        total_price, due = data
        new_due = max(due - amount, 0)
        payment_status = "Paid" if new_due==0 else "Partial Paid"
        execute_db("UPDATE service_requests SET due_amount=?, payment_status=? WHERE id=?", (new_due, payment_status, request_id))
        auto_update_status()
        return True
    except Exception as e:
        print("Payment Update Error:", e)
        return False

def generate_invoice_pdf(request_id):
    data = fetchall_db("""
        SELECT r.id, t.name, r.customer_name, r.details, r.price, r.due_amount, r.payment_status, r.completed_at
        FROM service_requests r
        LEFT JOIN service_types t ON r.service_type_id = t.id
        WHERE r.id=?
    """, (request_id,))
    if not data:
        return
    r = data[0]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, "সার্ভিস ইনভয়েস", 0, 1, "C")
    pdf.ln(4)
    pdf.set_font("Arial", "", 12)
    fields = [
        ("রিকোয়েস্ট ID", r[0]),
        ("সার্ভিস টাইপ", r[1]),
        ("কাস্টমার", r[2]),
        ("বিস্তারিত", r[3]),
        ("মোট মূল্য", r[4]),
        ("বাকি", r[5]),
        ("পেমেন্ট স্ট্যাটাস", r[6]),
        ("সমাপ্তির সময়", r[7]),
    ]
    for lbl, val in fields:
        pdf.cell(60, 9, f"{lbl}:", 0, 0)
        pdf.cell(0, 9, f"{val}", 0, 1)
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "invoices"), exist_ok=True)
    invoice_path = os.path.join(os.path.dirname(__file__), "..", "invoices", f"Invoice_{r[0]}.pdf")
    pdf.output(invoice_path)
    webbrowser.open(invoice_path)

# ---------------- Auto Status ----------------
PENDING_TO_PROCESSING_DELAY = 5  # minutes
BACKGROUND_INTERVAL = 60  # seconds

def auto_update_status():
    all_requests = fetchall_db("SELECT id, due_amount, status, payment_status, requested_at FROM service_requests")
    now = datetime.now()
    for r in all_requests:
        request_id, due, status, payment_status, requested_at = r
        requested_at_dt = datetime.strptime(requested_at, "%Y-%m-%d %H:%M:%S")
        new_status = status
        if status == "Pending" and payment_status == "Partial Paid":
            if (now - requested_at_dt).total_seconds() >= PENDING_TO_PROCESSING_DELAY*60:
                new_status = "Processing"
        if due == 0:
            new_status = "Completed"
        if new_status != status:
            update_service_request_status(request_id, new_status)

def background_status_updater(ui_instance):
    while True:
        try:
            auto_update_status()
            if hasattr(ui_instance, 'req_tree'):
                ui_instance.load_service_requests()
        except Exception as e:
            print("Background Updater Error:", e)
        time.sleep(BACKGROUND_INTERVAL)

# ---------------- UI ----------------
class ServiceUI(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.frame = self
        self.pack(fill="both", expand=True)

        # ------------ Global Style (Modern look) ------------
        style = ttk.Style()
        # থিম আপনি main-এ সেট করে থাকলে 그대로 থাকবে; নাহলে এখানে সেট করতে পারেন:
        # style.theme_use("flatly")  # optional
        
        # Treeview heading bold & row stripe
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=26)
        style.map("Treeview", background=[("selected", "#0d6efd")], foreground=[("selected", "white")])

        # ------------ Title ------------
        # বড়, রঙিন, মাঝখানে — bootstyle ব্যবহার
        self.title_label = ttk.Label(
            self,
            text="সার্ভিস ব্যবস্থাপনা",
            font=("Segoe UI", 22, "bold"),
            bootstyle="PRIMARY"
        )
        self.title_label.pack(pady=(12, 2))
        # পাতলা separator
        ttk.Separator(self, bootstyle="secondary").pack(fill="x", padx=10, pady=(0, 10))

        # ------------ Tabs ------------
        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.tab_type = ttk.Frame(self.notebook)
        self.tab_request = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_type, text='🛠️ সার্ভিস টাইপ')
        self.notebook.add(self.tab_request, text='📋 সার্ভিস রিকোয়েস্ট')
        self.notebook.pack(expand=1, fill='both')

        # Setup tabs
        self.setup_service_type_tab()
        self.setup_service_request_tab()

        # Start background thread for auto sync
        threading.Thread(target=background_status_updater, args=(self,), daemon=True).start()

    # ---------------- Service Type Tab ----------------
    def setup_service_type_tab(self):
        # Grid layout
        for i in range(4):
            self.tab_type.grid_columnconfigure(i, weight=1)
        self.tab_type.grid_rowconfigure(3, weight=1)

        frm_inputs = ttk.Labelframe(self.tab_type, text="নতুন/আপডেট সার্ভিস টাইপ", bootstyle="info")
        frm_inputs.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        ttk.Label(frm_inputs, text="নাম:").grid(row=0, column=0, padx=6, pady=6, sticky='e')
        self.entry_type_name = ttk.Entry(frm_inputs, width=30)
        self.entry_type_name.grid(row=0, column=1, padx=6, pady=6, sticky='w')

        ttk.Label(frm_inputs, text="বর্ণনা:").grid(row=1, column=0, padx=6, pady=6, sticky='e')
        self.entry_type_description = ttk.Entry(frm_inputs, width=40)
        self.entry_type_description.grid(row=1, column=1, padx=6, pady=6, sticky='w')

        # Buttons রঙিন
        btnbar = ttk.Frame(frm_inputs)
        btnbar.grid(row=2, column=0, columnspan=2, pady=(8,2))
        ttk.Button(btnbar, text="✅ যোগ করুন", command=self.add_service_type, bootstyle="success").pack(side="left", padx=4)
        ttk.Button(btnbar, text="✏️ Update", command=self.update_selected_type, bootstyle="warning").pack(side="left", padx=4)
        ttk.Button(btnbar, text="❌ Delete", command=self.delete_selected_type, bootstyle="danger").pack(side="left", padx=4)
        ttk.Button(btnbar, text="🔄 রিফ্রেশ", command=self.load_service_types, bootstyle="info").pack(side="left", padx=4)

        # Treeview area
        frm_table = ttk.Labelframe(self.tab_type, text="সার্ভিস টাইপ লিস্ট", bootstyle="secondary")
        frm_table.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

        cols = ("ID", "Name", "Description")
        self.type_tree = ttk.Treeview(frm_table, columns=cols, show="headings", bootstyle="info")
        for col in cols:
            self.type_tree.heading(col, text=col)
            self.type_tree.column(col, width=150, anchor='center')
        self.type_tree.grid(row=0, column=0, sticky='nsew')
        scr = ttk.Scrollbar(frm_table, orient='vertical', command=self.type_tree.yview, bootstyle="info-round")
        self.type_tree.configure(yscroll=scr.set)
        scr.grid(row=0, column=1, sticky='ns')
        frm_table.grid_rowconfigure(0, weight=1)
        frm_table.grid_columnconfigure(0, weight=1)

        self.load_service_types()

    def add_service_type(self):
        name = self.entry_type_name.get().strip()
        description = self.entry_type_description.get().strip()
        if not name:
            messagebox.showerror("ত্রুটি", "নাম অবশ্যই দিতে হবে।")
            return
        if add_service_type(name, description):
            messagebox.showinfo("সফল", "সার্ভিস টাইপ যোগ হয়েছে!")
            self.entry_type_name.delete(0, 'end')
            self.entry_type_description.delete(0, 'end')
            self.load_service_types()
        else:
            messagebox.showerror("ত্রুটি", "যোগ করা যায়নি।")

    def load_service_types(self):
        for row in self.type_tree.get_children():
            self.type_tree.delete(row)
        for t in get_all_service_types():
            self.type_tree.insert("", 'end', values=t)

    def update_selected_type(self):
        selected = self.type_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "একটি সার্ভিস টাইপ নির্বাচন করুন")
            return
        item = self.type_tree.item(selected[0])
        type_id = item['values'][0]
        new_name = self.entry_type_name.get().strip()
        new_desc = self.entry_type_description.get().strip()
        if not new_name:
            messagebox.showerror("Error", "নাম দিতে হবে।")
            return
        if update_service_type(type_id, new_name, new_desc):
            messagebox.showinfo("সফল", "সার্ভিস টাইপ আপডেট হয়েছে।")
            self.entry_type_name.delete(0, 'end')
            self.entry_type_description.delete(0, 'end')
            self.load_service_types()
        else:
            messagebox.showerror("Error", "আপডেট করা যায়নি।")

    def delete_selected_type(self):
        selected = self.type_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "একটি সার্ভিস টাইপ নির্বাচন করুন")
            return
        item = self.type_tree.item(selected[0])
        type_id = item['values'][0]
        if messagebox.askyesno("Confirm", "আপনি কি ডিলিট করতে চান?"):
            if delete_service_type(type_id):
                messagebox.showinfo("সফল", "সার্ভিস টাইপ ডিলিট হয়েছে।")
                self.load_service_types()
            else:
                messagebox.showerror("Error", "ডিলিট করা যায়নি।")

    # ---------------- Service Request Tab ----------------
    def setup_service_request_tab(self):
        # Grid layout
        for c in range(6):
            self.tab_request.grid_columnconfigure(c, weight=1)
        self.tab_request.grid_rowconfigure(6, weight=1)

        # --- Input Frame ---
        frm = ttk.Labelframe(self.tab_request, text="নতুন সার্ভিস রিকোয়েস্ট", bootstyle="primary")
        frm.grid(row=0, column=0, columnspan=6, padx=10, pady=10, sticky="nsew")

        # Customer
        ttk.Label(frm, text="কাস্টমারের নাম:").grid(row=0, column=0, padx=6, pady=6, sticky='e')
        self.entry_customer_name = ttk.Entry(frm, width=30)
        self.entry_customer_name.grid(row=0, column=1, padx=6, pady=6, sticky='w')

        # Service Type
        ttk.Label(frm, text="সার্ভিস টাইপ:").grid(row=1, column=0, padx=6, pady=6, sticky='e')
        self.combo_type = ttk.Combobox(frm, state='readonly', width=28)
        self.combo_type.grid(row=1, column=1, padx=6, pady=6, sticky='w')
        self.combo_type.bind("<<ComboboxSelected>>", self._on_type_change)

        # Description (auto from service type)
        ttk.Label(frm, text="বর্ণনা:").grid(row=2, column=0, padx=6, pady=6, sticky='e')
        self.entry_description_auto = ttk.Entry(frm, width=40)
        self.entry_description_auto.grid(row=2, column=1, padx=6, pady=6, sticky='w')
        self.entry_description_auto.configure(state="readonly")

        # Extra Details (user input)
        ttk.Label(frm, text="অতিরিক্ত বিস্তারিত:").grid(row=3, column=0, padx=6, pady=6, sticky='e')
        self.entry_details = ttk.Entry(frm, width=40)
        self.entry_details.grid(row=3, column=1, padx=6, pady=6, sticky='w')

        # Rate / Quantity / Total (auto calc)
        ttk.Label(frm, text="Rate (৳/Unit):").grid(row=0, column=2, padx=6, pady=6, sticky='e')
        self.entry_rate = ttk.Entry(frm, width=15)
        self.entry_rate.grid(row=0, column=3, padx=6, pady=6, sticky='w')
        self.entry_rate.bind("<KeyRelease>", self._recalc_total)

        ttk.Label(frm, text="Quantity:").grid(row=1, column=2, padx=6, pady=6, sticky='e')
        self.entry_qty = ttk.Entry(frm, width=15)
        self.entry_qty.grid(row=1, column=3, padx=6, pady=6, sticky='w')
        self.entry_qty.bind("<KeyRelease>", self._recalc_total)

        ttk.Label(frm, text="Total (৳):").grid(row=2, column=2, padx=6, pady=6, sticky='e')
        self.entry_total = ttk.Entry(frm, width=18)
        self.entry_total.grid(row=2, column=3, padx=6, pady=6, sticky='w')
        self.entry_total.configure(state="readonly")

        # Buttons (Colored)
        btnbar2 = ttk.Frame(frm)
        btnbar2.grid(row=4, column=0, columnspan=4, pady=(8, 4))
        ttk.Button(btnbar2, text="✅ রিকোয়েস্ট যোগ করুন", command=self.add_request, bootstyle="success").pack(side="left", padx=4)
        ttk.Button(btnbar2, text="🔄 রিফ্রেশ", command=self.load_service_requests, bootstyle="info").pack(side="left", padx=4)
        ttk.Button(btnbar2, text="📄 Excel Export", command=self.export_excel, bootstyle="secondary").pack(side="left", padx=4)
        ttk.Button(btnbar2, text="🖨️ PDF Export", command=self.export_pdf, bootstyle="secondary").pack(side="left", padx=4)
        ttk.Button(btnbar2, text="⚙️ Interval/Delay", command=self.configure_interval_delay, bootstyle="warning").pack(side="left", padx=4)
        ttk.Button(btnbar2, text="🔍 ফিল্টার", command=self.filter_requests, bootstyle="info").pack(side="left", padx=4)

        # --- Table Frame ---
        tbl = ttk.Labelframe(self.tab_request, text="রিকোয়েস্ট লিস্ট", bootstyle="secondary")
        tbl.grid(row=6, column=0, columnspan=6, padx=10, pady=(2,10), sticky="nsew")

        self.req_tree = ttk.Treeview(
            tbl,
            columns=("ID", "Type", "Customer", "Details", "Status", "Price", "Due", "Payment Status", "Requested At", "Completed At"),
            show="headings",
            bootstyle="info"
        )
        for col in self.req_tree['columns']:
            self.req_tree.heading(col, text=col)
            self.req_tree.column(col, width=120, anchor='center')
        self.req_tree.grid(row=0, column=0, sticky='nsew')
        sc2 = ttk.Scrollbar(tbl, orient='vertical', command=self.req_tree.yview, bootstyle="info-round")
        self.req_tree.configure(yscroll=sc2.set)
        sc2.grid(row=0, column=1, sticky='ns')
        tbl.grid_rowconfigure(0, weight=1)
        tbl.grid_columnconfigure(0, weight=1)

        # Double click → details & payment
        self.req_tree.bind("<Double-1>", self.show_request_details)

        # Load data
        self.load_types_combobox()
        self.load_service_requests()

    # ------- Helpers (Request Tab) -------
    def _on_type_change(self, event=None):
        """Service type select → description auto-fill"""
        idx = self.combo_type.current()
        if idx == -1:
            return
        desc = self.service_types[idx][2] if len(self.service_types[idx]) > 2 else ""
        self.entry_description_auto.configure(state="normal")
        self.entry_description_auto.delete(0, "end")
        self.entry_description_auto.insert(0, desc)
        self.entry_description_auto.configure(state="readonly")

    def _recalc_total(self, event=None):
        """rate × qty → total"""
        try:
            rate = float(self.entry_rate.get().strip() or 0)
            qty = float(self.entry_qty.get().strip() or 0)
            total = rate * qty
        except:
            total = 0
        self.entry_total.configure(state="normal")
        self.entry_total.delete(0, "end")
        self.entry_total.insert(0, f"{total:.2f}")
        self.entry_total.configure(state="readonly")

    # ---------------- Requests Functions ----------------
    def load_types_combobox(self):
        self.service_types = get_all_service_types()
        self.combo_type['values'] = [t[1] for t in self.service_types]

    def add_request(self):
        customer_name = self.entry_customer_name.get().strip()
        extra_details = self.entry_details.get().strip()
        # total price নেবো Total box থেকে (auto calculated)
        total_txt = self.entry_total.get().strip()
        type_index = self.combo_type.current()

        if type_index == -1:
            messagebox.showerror("ত্রুটি", "সার্ভিস টাইপ নির্বাচন করুন।")
            return
        service_type_id = self.service_types[type_index][0]

        if not customer_name:
            messagebox.showerror("ত্রুটি", "কাস্টমারের নাম দিতে হবে।")
            return

        # যদি user rate/qty না দেয় → fallback old price field
        price_val = None
        try:
            price_val = float(total_txt) if total_txt else None
        except:
            price_val = None

        if price_val is None or price_val == 0:
            # fallback: পুরনো মূল্য ফিল্ড (optional)
            # আপনি চাইলে এটি হাইডও করতে পারেন; এখানে রাখা হলো ব্যাকওয়ার্ড কম্প্যাটিবিলিটির জন্য
            price_fallback = simpledialog.askfloat("মূল্য", "মোট মূল্য (৳) দিন:", minvalue=0.0)
            if price_fallback is None:
                return
            price_val = float(price_fallback)

        # description auto + extra_details মার্জ করে details-এ রাখবো
        auto_desc = self.entry_description_auto.get().strip()
        details = auto_desc if not extra_details else f"{auto_desc} | {extra_details}"

        if add_service_request(service_type_id, customer_name, details, price_val):
            messagebox.showinfo("সফল", "সার্ভিস রিকোয়েস্ট যোগ হয়েছে!")
            # clear inputs
            self.entry_customer_name.delete(0, 'end')
            self.entry_details.delete(0, 'end')
            self.entry_rate.delete(0, 'end')
            self.entry_qty.delete(0, 'end')
            self.entry_total.configure(state="normal"); self.entry_total.delete(0, 'end'); self.entry_total.insert(0,"0.00"); self.entry_total.configure(state="readonly")
            self.load_service_requests()
        else:
            messagebox.showerror("ত্রুটি", "রিকোয়েস্ট যোগ করা যায়নি।")

    def load_service_requests(self, filters=None):
        auto_update_status()
        for row in self.req_tree.get_children():
            self.req_tree.delete(row)
        for r in get_all_service_requests(filters):
            # status অনুযায়ী row tag রঙ
            tags = ()
            if r[4] == "Pending":
                tags = ("pending",)
            elif r[4] == "Processing":
                tags = ("processing",)
            elif r[4] == "Completed":
                tags = ("completed",)
            self.req_tree.insert("", 'end', values=r, tags=tags)

        # Tag styles
        self.req_tree.tag_configure("pending", background="#fff9db")
        self.req_tree.tag_configure("processing", background="#e7f1ff")
        self.req_tree.tag_configure("completed", background="#e8fff1")

    # ---------------- Show Request Details + Payment ----------------
    def show_request_details(self, event):
        selected = self.req_tree.selection()
        if not selected:
            return
        item = self.req_tree.item(selected[0])
        values = item['values']
        popup = ttk.Toplevel(self)
        popup.title(f"রিকোয়েস্ট বিস্তারিত (ID: {values[0]})")
        popup.geometry("520x480")

        labels = ["ID","Service Type","Customer","Details","Status","Price","Due","Payment Status","Requested At","Completed At"]
        for i, (label, val) in enumerate(zip(labels, values)):
            ttk.Label(popup, text=f"{label}: ", font=("Segoe UI", 10, "bold")).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            ttk.Label(popup, text=f"{val}").grid(row=i, column=1, padx=10, pady=5, sticky='w')

        # Payment update
        rowi = len(labels)
        ttk.Label(popup, text="পরিশোধের পরিমাণ:", font=("Segoe UI", 10)).grid(row=rowi, column=0, sticky='e', padx=10, pady=5)
        pay_entry = ttk.Entry(popup)
        pay_entry.grid(row=rowi, column=1, padx=10, pady=5, sticky="w")

        def update_payment():
            try:
                amount = float(pay_entry.get())
            except:
                messagebox.showerror("ত্রুটি", "সঠিক সংখ্যা দিন।")
                return
            if update_request_payment(values[0], amount):
                messagebox.showinfo("সফল", "পেমেন্ট আপডেট হয়েছে।")
                popup.destroy()
                self.load_service_requests()
            else:
                messagebox.showerror("ত্রুটি", "পেমেন্ট আপডেট ব্যর্থ।")

        ttk.Button(popup, text="💰 পরিশোধ আপডেট করুন", command=update_payment, bootstyle="success").grid(row=rowi+1, column=0, columnspan=2, pady=10)

        # Delete Request
        def delete_request():
            if messagebox.askyesno("নিশ্চিত", "আপনি কি রিকোয়েস্টটি ডিলিট করতে চান?"):
                if delete_service_request(values[0]):
                    messagebox.showinfo("সফল", "রিকোয়েস্ট ডিলিট হয়েছে।")
                    popup.destroy()
                    self.load_service_requests()
                else:
                    messagebox.showerror("ত্রুটি", "ডিলিট করা যায়নি।")
        ttk.Button(popup, text="❌ রিকোয়েস্ট ডিলিট করুন", command=delete_request, bootstyle="danger").grid(row=rowi+2, column=0, columnspan=2, pady=5)

    # ---------------- Export ----------------
    def export_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if not path: 
            return
        data = [self.req_tree.item(i)['values'] for i in self.req_tree.get_children()]
        df = pd.DataFrame(data, columns=[c for c in self.req_tree['columns']])
        df.to_excel(path, index=False)
        messagebox.showinfo("সফল", f"Excel ফাইল তৈরি হয়েছে: {path}")

    def export_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
        if not path: 
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 11)

        cols = [c for c in self.req_tree['columns']]
        colw = 25  # simple fixed width; চাইলে ছোট/বড় করুন
        for col in cols:
            pdf.cell(colw, 9, col, 1, 0, 'C')
        pdf.ln()
        pdf.set_font("Arial", "", 10)
        for row_id in self.req_tree.get_children():
            values = self.req_tree.item(row_id)['values']
            for val in values:
                pdf.cell(colw, 8, str(val)[:18], 1, 0, 'C')
            pdf.ln()
        pdf.output(path)
        messagebox.showinfo("সফল", f"PDF তৈরি হয়েছে: {path}")

    # ---------------- Filter ----------------
    def filter_requests(self):
        popup = ttk.Toplevel(self)
        popup.title("Filter Requests")
        popup.geometry("360x260")

        ttk.Label(popup, text="Status:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        status_cb = ttk.Combobox(popup, values=["Pending","Processing","Completed"], state="readonly")
        status_cb.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Payment Status:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        payment_cb = ttk.Combobox(popup, values=["Unpaid","Partial Paid","Paid"], state="readonly")
        payment_cb.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Service Type:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        service_cb = ttk.Combobox(popup, values=[t[1] for t in get_all_service_types()], state="readonly")
        service_cb.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(popup, text="From (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        from_entry = ttk.Entry(popup)
        from_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(popup, text="To (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        to_entry = ttk.Entry(popup)
        to_entry.grid(row=4, column=1, padx=5, pady=5)

        def apply_filter():
            filters = {}
            if status_cb.get(): filters["status"] = status_cb.get()
            if payment_cb.get(): filters["payment_status"] = payment_cb.get()
            if service_cb.get(): filters["service_type"] = service_cb.get()
            if from_entry.get() and to_entry.get():
                filters["from_date"] = from_entry.get()
                filters["to_date"] = to_entry.get()
            self.load_service_requests(filters)
            popup.destroy()

        ttk.Button(popup, text="Apply Filter", command=apply_filter, bootstyle="primary").grid(row=5, column=0, columnspan=2, pady=12)

    # ---------------- Interval / Delay ----------------
    def configure_interval_delay(self):
        global BACKGROUND_INTERVAL, PENDING_TO_PROCESSING_DELAY
        interval = simpledialog.askinteger("Background Interval", "Background Update Interval (seconds):", initialvalue=BACKGROUND_INTERVAL)
        delay = simpledialog.askinteger("Pending→Processing Delay", "Pending → Processing Delay (minutes):", initialvalue=PENDING_TO_PROCESSING_DELAY)
        if interval:
            BACKGROUND_INTERVAL = interval
        if delay:
            PENDING_TO_PROCESSING_DELAY = delay
        messagebox.showinfo("সফল", f"Interval: {BACKGROUND_INTERVAL}s, Pending→Processing Delay: {PENDING_TO_PROCESSING_DELAY}m সেট হয়েছে।")
