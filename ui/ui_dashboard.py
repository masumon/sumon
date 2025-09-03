import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import datetime
from collections import defaultdict
from db import get_all_sales, get_all_expenses, get_all_due_payment, get_all_products, get_all_users
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams, font_manager
import logging
import traceback
import os
import textwrap

# ---------------- Logging Setup ----------------
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "dashboard.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# ---------------- Matplotlib Font Setup ----------------
try:
    font_path = os.path.join("report", "fonts", "Kalpurush.ttf")
    prop = font_manager.FontProperties(fname=font_path)
    rcParams['font.family'] = [prop.get_name(), 'DejaVu Sans']
except Exception as e:
    logging.error("Bengali font load failed: %s", e)
    traceback.print_exc()

# ---------------- Dashboard UI ----------------
class DashboardUI:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)
        try:
            self.build_ui()
        except Exception as e:
            logging.error("Dashboard load failed: %s", e)
            traceback.print_exc()
            fallback = ttk.Frame(parent)
            ttk.Label(fallback, text=f"Dashboard load failed:\n{e}", bootstyle="danger").pack(pady=30)
            fallback.pack(fill="both", expand=True, padx=10, pady=10)

    def build_ui(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        logging.info("Today's date: %s", today)

        # ---------------- Fetch Data ----------------
        try:
            sales_data = list(get_all_sales())
            expense_data = list(get_all_expenses())
            due_data = list(get_all_due_payment())
            product_data = list(get_all_products())
            user_data = list(get_all_users())
        except Exception as e:
            logging.error("Failed to fetch data from DB: %s", e)
            traceback.print_exc()
            sales_data = expense_data = due_data = product_data = user_data = []

        sales_dicts = [dict(s) for s in sales_data]
        expense_dicts = [dict(e) for e in expense_data]
        due_dicts = [dict(d) for d in due_data]
        product_dicts = [dict(p) for p in product_data]
        user_dicts = [dict(u) for u in user_data]

        # ---------------- Header ----------------
        header = ttk.Label(self.frame, text="স্বাগতম এবিও এন্টারপ্রাইজ", font=("Kalpurush", 26, "bold"), bootstyle="primary")
        header.pack(pady=15)

        # ---------------- KPI Section ----------------
        kpi_frame = ttk.Frame(self.frame)
        kpi_frame.pack(fill="x", pady=15, padx=10)

        total_sales = sum(s.get("total_after_discount_tax",0) for s in sales_dicts if s.get("date","").startswith(today))
        total_due = sum(s.get("due_amount",0) for s in sales_dicts if s.get("date","").startswith(today))
        total_expense = sum(e.get("amount",0) for e in expense_dicts if e.get("date","").startswith(today))
        low_stock_count = sum(1 for p in product_dicts if p.get("quantity",0) < 5)
        total_users = len(user_dicts)

        # KPI: Title + Value stacked
        kpi_info = [
            ("আজকের বিক্রয়", f"৳ {total_sales:.2f}", "success"),
            ("আজকের বাকি", f"৳ {total_due:.2f}", "warning"),
            ("আজকের খরচ", f"৳ {total_expense:.2f}", "danger"),
            ("Low Stock Items", f"{low_stock_count}", "info"),
            ("মোট ব্যবহারকারী", f"{total_users}", "secondary")
        ]

        for title, value, style in kpi_info:
            self.make_kpi(kpi_frame, title, value, style).pack(side="left", expand=True, padx=10, fill="x")

        # ---------------- Quick Actions ----------------
        actions_frame = ttk.Frame(self.frame)
        actions_frame.pack(fill="x", padx=10, pady=10)
        actions_frame.columnconfigure(tuple(range(5)), weight=1)  # Centering all buttons equally

        ttk.Button(actions_frame, text="🛒 নতুন বিক্রয়", bootstyle="success-outline", command=self.open_sale_module).grid(row=0,column=0, padx=5, sticky="ew")
        ttk.Button(actions_frame, text="📦 নতুন পণ্য", bootstyle="info-outline", command=self.open_product_module).grid(row=0,column=1, padx=5, sticky="ew")
        ttk.Button(actions_frame, text="⚡ রিচার্জ শুরু", bootstyle="warning-outline", command=self.open_recharge_module).grid(row=0,column=2, padx=5, sticky="ew")
        ttk.Button(actions_frame, text="💳 নতুন খরচ", bootstyle="danger-outline", command=self.open_expense_module).grid(row=0,column=3, padx=5, sticky="ew")
        ttk.Button(actions_frame, text="🛠️ সার্ভিস", bootstyle="secondary-outline", command=self.open_service_module).grid(row=0,column=4, padx=5, sticky="ew")

        # ---------------- Charts Section ----------------
        chart_frame = ttk.Frame(self.frame)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.render_charts(chart_frame, sales_dicts, expense_dicts, due_dicts, product_dicts)

        # ---------------- Low Stock List ----------------
        self.render_low_stock(product_dicts)

        # ---------------- Due Payments ----------------
        self.render_due_payments(due_dicts)

        # ---------------- Recent Sales ----------------
        self.render_recent_sales(sales_dicts)

    # ---------------- KPI Card ----------------
    def make_kpi(self, parent, title, value, style):
        card = ttk.Labelframe(parent, bootstyle=style, padding=15)
        ttk.Label(card, text=title, font=("Kalpurush",16,"bold")).pack()
        ttk.Label(card, text=value, font=("Kalpurush",14,"normal")).pack()
        return card

    # ---------------- Quick Actions Modules ----------------
    def open_sale_module(self):
        try:
            from ui.ui_sale import SaleUI
            SaleUI(self.frame).frame.tkraise()
        except Exception as e:
            logging.error("Opening Sale Module failed: %s", e)

    def open_product_module(self):
        try:
            from ui.ui_product import ProductUI
            ProductUI(self.frame).frame.tkraise()
        except Exception as e:
            logging.error("Opening Product Module failed: %s", e)

    def open_recharge_module(self):
        try:
            from ui.ui_recharge import RechargeUI
            RechargeUI(self.frame).frame.tkraise()
        except Exception as e:
            logging.error("Opening Recharge Module failed: %s", e)

    def open_expense_module(self):
        try:
            from ui.ui_expense import ExpenseUI
            ExpenseUI(self.frame).frame.tkraise()
        except Exception as e:
            logging.error("Opening Expense Module failed: %s", e)

    def open_service_module(self):
        try:
            from ui.ui_service import ServiceUI
            ServiceUI(self.frame).frame.tkraise()
        except Exception as e:
            logging.error("Opening Service Module failed: %s", e)

    # ---------------- Charts ----------------
    def render_charts(self, parent, sales, expenses, dues, products):
        total_sales = sum(s.get("total_after_discount_tax",0) for s in sales)
        total_expense = sum(e.get("amount",0) for e in expenses)
        total_due = sum(d.get("due_amount",0) for d in dues)

        fig1 = Figure(figsize=(5,3), dpi=100)
        ax1 = fig1.add_subplot(111)
        ax1.bar(["বিক্রয়","খরচ","বাকি"],[total_sales,total_expense,total_due],color=["#4CAF50","#F44336","#FF9800"])
        ax1.set_title("আজকের বিক্রয় / খরচ / বাকি", fontsize=12)
        canvas1 = FigureCanvasTkAgg(fig1, master=parent)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5, pady=5)

        low_stock_items = [p for p in products if p.get("quantity",0)<5]
        fig2 = Figure(figsize=(4,3), dpi=100)
        ax2 = fig2.add_subplot(111)
        if low_stock_items:
            names = [textwrap.fill(p.get("name","Unknown"), 12) for p in low_stock_items]
            qtys = [p.get("quantity",0) for p in low_stock_items]
            if sum(qtys) > 0:
                wedges,texts,autotexts = ax2.pie(qtys, labels=names, autopct='%1.1f%%', startangle=90, pctdistance=0.8, labeldistance=1.1, wedgeprops={'edgecolor':'white'}, textprops={'fontsize':8,'color':'black'})
                ax2.set_title("Low Stock Items", fontsize=10)
            else:
                ax2.text(0.5,0.5,"No Low Stock Items",ha='center',va='center',fontsize=12)
        else:
            ax2.text(0.5,0.5,"No Low Stock Items",ha='center',va='center',fontsize=12)
        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=parent)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5, pady=5)

    # ---------------- Treeview Helper ----------------
    def create_treeview(self, frame, columns, bootstyle, data, tags_even, tags_odd):
        tree = ttk.Treeview(frame, columns=columns, show="headings", bootstyle=bootstyle)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        for idx,row in enumerate(data):
            tree.insert("", "end", values=row, tags=(tags_odd if idx%2 else tags_even,))
        tree.tag_configure(tags_even, background='#f0f0f0')
        tree.tag_configure(tags_odd, background='#e0e0e0')
        return tree

    # ---------------- Low Stock ----------------
    def render_low_stock(self, products):
        frame = ttk.Labelframe(self.frame, text="Low Stock Items", bootstyle="warning", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        data = [(p.get("name","Unknown"), p.get("quantity",0)) for p in products if p.get("quantity",0)<5]
        self.create_treeview(frame, ("Product", "Quantity"), "warning", data, "oddrow", "evenrow")

    # ---------------- Due Payments ----------------
    def render_due_payments(self, dues):
        frame = ttk.Labelframe(self.frame, text="Pending Due Payments", bootstyle="danger", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        data = [(d.get("customer_name","Unknown"), f"৳ {d.get('due_amount',0):.2f}") for d in dues if d.get("due_amount",0)>0]
        self.create_treeview(frame, ("Customer", "Amount"), "danger", data, "oddrow", "evenrow")

    # ---------------- Recent Sales ----------------
    def render_recent_sales(self, sales):
        frame = ttk.Labelframe(self.frame, text="Recent Sales", bootstyle="info", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        recent_sales = sorted(sales, key=lambda x:x.get("date",""), reverse=True)[:5]
        data = [(s.get('date','Unknown'), s.get('customer_name','Unknown'), f"৳ {s.get('total_after_discount_tax',0):.2f}") for s in recent_sales]
        self.create_treeview(frame, ("Date", "Customer", "Total"), "info", data, "oddrow", "evenrow")
