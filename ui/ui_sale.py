import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from datetime import datetime, date
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Import db functions (use root import)
from db import (
    get_all_products, sale_and_stock_update, add_stock, get_all_sales, get_all_due_payment
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "smartshop.db")

def ask_wallet_info(method_name, parent=None):
    title = f"{method_name} পেমেন্ট তথ্য"
    txn = simpledialog.askstring(title, f"{method_name} Transaction ID লিখুন:", parent=parent)
    if txn is None:
        return None, None
    mobile = simpledialog.askstring(title, f"{method_name} মোবাইল নাম্বার লিখুন:", parent=parent)
    if mobile is None:
        return None, None
    return txn.strip(), mobile.strip()

# ----------- Tooltip Helper --------------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tipwindow or not self.text: return
        try:
            x = self.widget.winfo_rootx() + 25
            y = self.widget.winfo_rooty() + 20
        except Exception:
            x, y = 0, 0
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "9", "normal"))
        label.pack(ipadx=6)
    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw: tw.destroy()

class SaleUI:
    def __init__(self, master):
        self.frame = tb.Frame(master)
        self.frame.pack(fill="both", expand=True)
        self.style = tb.Style("flatly")

        # ---------- Multi-language Support ----------
        self.lang = tk.StringVar(value="bn")  # "bn" for Bangla, "en" for English
        self.texts = {
            "bn": {
                "today_sale": "আজকের মোট বিক্রয় (৳):",
                "cart_total": "কার্ট মোট (৳):",
                "refresh": "Refresh",
                "search_product": "পণ্য খুঁজুন:",
                "product": "পণ্য",
                "qty": "পরিমাণ",
                "discount": "ছাড় (৳)",
                "add_to_cart": "কার্টে যোগ করুন",
                "purchase_price": "ক্রয় মূল্য",
                "stock": "মজুদ",
                "sale_price": "বিক্রয় মূল্য",
                "line_total": "লাইন টোটাল (৳):",
                "cart": "কার্ট",
                "del_selected": "নির্বাচিত লাইন মুছুন",
                "clear_cart": "কার্ট খালি করুন",
                "seller": "বিক্রয়কারী:",
                "customer": "গ্রাহক:",
                "paid": "প্রদেয়:",
                "due": "বাকি:",
                "payment": "Payment:",
                "sale_done": "বিক্রয় সম্পন্ন করুন",
                "export_excel": "Export (Excel)",
                "print_receipt": "রসিদ মুদ্রণ",
                "recent_sale": "সাম্প্রতিক বিক্রয়",
                "due_payment": "বাকি প্রদায়ন",
                "customer_col": "গ্রাহক",
                "amount_col": "পরিমাণ",
                "date_col": "তারিখ",
                "monthly_sale": "মাসিক বিক্রয় (সামারি)",
                "date": "তারিখ",
                "total": "মোট (৳)",
                "lang_toggle": "EN",
                "help": "❓",
                "low_stock": "স্টকে পর্যাপ্ত পরিমাণ নেই।",
                "sale_success": "বিক্রয় সম্পন্ন হয়েছে।",
                "cart_empty": "কার্ট খালি।",
                "select_product": "একটি বৈধ পণ্য নির্বাচন করুন।"
            },
            "en": {
                "today_sale": "Today's Sales (৳):",
                "cart_total": "Cart Total (৳):",
                "refresh": "Refresh",
                "search_product": "Search Product:",
                "product": "Product",
                "qty": "Qty",
                "discount": "Discount (৳)",
                "add_to_cart": "Add to Cart",
                "purchase_price": "Purchase Price",
                "stock": "Stock",
                "sale_price": "Sale Price",
                "line_total": "Line Total (৳):",
                "cart": "Cart",
                "del_selected": "Delete Selected",
                "clear_cart": "Clear Cart",
                "seller": "Seller:",
                "customer": "Customer:",
                "paid": "Paid:",
                "due": "Due:",
                "payment": "Payment:",
                "sale_done": "Finalize Sale",
                "export_excel": "Export (Excel)",
                "print_receipt": "Print Receipt",
                "recent_sale": "Recent Sales",
                "due_payment": "Due Payments",
                "customer_col": "Customer",
                "amount_col": "Amount",
                "date_col": "Date",
                "monthly_sale": "Monthly Sales (Summary)",
                "date": "Date",
                "total": "Total (৳)",
                "lang_toggle": "BN",
                "help": "❓",
                "low_stock": "Not enough stock.",
                "sale_success": "Sale completed.",
                "cart_empty": "Cart is empty.",
                "select_product": "Select a valid product."
            }
        }

        self.products = []
        self.visible_products = []
        self.cart_items = {}

        self.selected_payment_method = tk.StringVar(value="ক্যাশ")
        self.last_txn_id = None
        self.last_mobile = None

        # ---------- Top summary ----------
        top_frame = tb.Frame(self.frame)
        top_frame.pack(fill="x", pady=6)

        self.today_total_var = tk.DoubleVar(value=0.0)
        self.cart_total_var = tk.DoubleVar(value=0.0)

        self.label_today_sale = tb.Label(top_frame, text=self.texts["bn"]["today_sale"], font=("Helvetica", 11, "bold"))
        self.label_today_sale.pack(side="left", padx=(6, 4))
        tb.Label(top_frame, textvariable=self.today_total_var, font=("Helvetica", 11), bootstyle="info").pack(side="left")
        self.label_cart_total = tb.Label(top_frame, text="  |  "+self.texts["bn"]["cart_total"], font=("Helvetica", 11, "bold"))
        self.label_cart_total.pack(side="left", padx=(10, 4))
        tb.Label(top_frame, textvariable=self.cart_total_var, font=("Helvetica", 11), bootstyle="primary").pack(side="left")
        self.btn_refresh = tb.Button(top_frame, text=self.texts["bn"]["refresh"], bootstyle="secondary", command=self.refresh_all)
        self.btn_refresh.pack(side="right", padx=6)
        ToolTip(self.btn_refresh, "সব তথ্য রিফ্রেশ করুন | Refresh all data")

        # ---------- Language toggle & Help ----------
        tb.Button(top_frame, text=self.texts["bn"]["lang_toggle"], width=3, command=self.toggle_language).pack(side="right", padx=4)
        self.btn_help = tb.Button(top_frame, text=self.texts["bn"]["help"], width=2, command=self.show_help)
        self.btn_help.pack(side="right", padx=2)
        ToolTip(self.btn_help, "সহায়তা | Help")

        # ---------- Product selection ----------
        product_frame = tb.Frame(self.frame)
        product_frame.pack(pady=6, fill="x")

        self.search_var = tk.StringVar()
        tb.Label(product_frame, text=self.texts["bn"]["search_product"], font=("Helvetica", 10)).grid(row=0, column=0, padx=4, pady=3, sticky="e")
        self.search_entry = tb.Entry(product_frame, textvariable=self.search_var, width=24)
        self.search_entry.grid(row=0, column=1, padx=4, pady=3, sticky="w")
        self.search_entry.bind("<KeyRelease>", self.update_product_list)
        self.search_entry.bind("<Control-f>", self.focus_search)
        ToolTip(self.search_entry, "পণ্য খুঁজুন | Search product (Ctrl+F)")

        tb.Label(product_frame, text=self.texts["bn"]["product"], font=("Helvetica", 10)).grid(row=0, column=2, padx=4, pady=3, sticky="e")
        self.product_combo = tb.Combobox(product_frame, width=30, bootstyle="info", state="readonly")
        self.product_combo.grid(row=0, column=3, padx=4, pady=3, sticky="w")
        self.product_combo.bind("<<ComboboxSelected>>", self.show_product_details)
        ToolTip(self.product_combo, "পণ্য নির্বাচন করুন | Select a product")

        tb.Label(product_frame, text=self.texts["bn"]["qty"], font=("Helvetica", 10)).grid(row=0, column=4, padx=4, pady=3, sticky="e")
        self.quantity_var = tk.IntVar(value=1)
        self.qty_entry = tb.Entry(product_frame, textvariable=self.quantity_var, width=6)
        self.qty_entry.grid(row=0, column=5, padx=4, pady=3, sticky="w")
        self.qty_entry.bind("<KeyRelease>", lambda e: self.update_current_line_total())
        self.qty_entry.bind("<FocusOut>", lambda e: self._normalize_int(self.quantity_var, minimum=1))
        ToolTip(self.qty_entry, "পরিমাণ লিখুন | Enter quantity")

        tb.Label(product_frame, text=self.texts["bn"]["discount"], font=("Helvetica", 10)).grid(row=0, column=6, padx=4, pady=3, sticky="e")
        self.discount_var = tk.DoubleVar(value=0.0)
        self.discount_entry = tb.Entry(product_frame, textvariable=self.discount_var, width=8)
        self.discount_entry.grid(row=0, column=7, padx=4, pady=3, sticky="w")
        self.discount_entry.bind("<KeyRelease>", lambda e: self.update_current_line_total())
        self.discount_entry.bind("<FocusOut>", lambda e: self._normalize_float(self.discount_var, minimum=0.0))
        ToolTip(self.discount_entry, "ছাড় লিখুন | Discount")

        self.btn_add_cart = tb.Button(product_frame, text=self.texts["bn"]["add_to_cart"], bootstyle="success", command=self.add_to_cart)
        self.btn_add_cart.grid(row=0, column=8, padx=6, pady=3, sticky="w")
        self.btn_add_cart.bind("<Return>", lambda e: self.add_to_cart())
        ToolTip(self.btn_add_cart, "কার্টে যোগ করুন | Add to cart (Enter)")

        self.product_info_var = tk.StringVar(value=f"{self.texts['bn']['purchase_price']}: - | {self.texts['bn']['stock']}: - | {self.texts['bn']['sale_price']}: -")
        tb.Label(product_frame, textvariable=self.product_info_var, font=("Helvetica", 10, "italic")).grid(row=1, column=0, columnspan=6, padx=4, pady=2, sticky="w")

        self.current_line_total_var = tk.DoubleVar(value=0.0)
        self.label_line_total = tb.Label(product_frame, text=self.texts["bn"]["line_total"], font=("Helvetica", 10, "bold"))
        self.label_line_total.grid(row=1, column=6, padx=4, pady=2, sticky="e")
        tb.Label(product_frame, textvariable=self.current_line_total_var, font=("Helvetica", 10), bootstyle="primary").grid(row=1, column=7, padx=4, pady=2, sticky="w")

        # ---------- Cart ----------
        cart_frame = tb.Labelframe(self.frame, text=self.texts["bn"]["cart"], padding=6, bootstyle="info")
        cart_frame.pack(pady=6, fill="both", expand=False)

        # Use fixed column keys, show texts as header
        self.cart_tree_columns = ("product", "qty", "unit_price", "discount", "total")
        self.cart_tree = ttk.Treeview(cart_frame, columns=self.cart_tree_columns, show="headings", height=6)
        for col in self.cart_tree_columns:
            self.cart_tree.heading(col, text=self.texts["bn"][col] if col in self.texts["bn"] else col)
            self.cart_tree.column(col, anchor=tk.CENTER, width=90)
        self.cart_tree.pack(fill="both", expand=True)
        ToolTip(self.cart_tree, "কার্ট | Cart")

        btn_row = tb.Frame(cart_frame)
        btn_row.pack(fill="x", pady=4)
        self.btn_remove_selected = tb.Button(btn_row, text=self.texts["bn"]["del_selected"], bootstyle="danger", command=self.remove_selected)
        self.btn_remove_selected.pack(side="left", padx=4)
        ToolTip(self.btn_remove_selected, "নির্বাচিত লাইন মুছুন | Delete selected lines")
        self.btn_clear_cart = tb.Button(btn_row, text=self.texts["bn"]["clear_cart"], bootstyle="secondary", command=self.clear_cart)
        self.btn_clear_cart.pack(side="left", padx=4)
        ToolTip(self.btn_clear_cart, "কার্ট খালি করুন | Clear cart")

        # ---------- Payment ----------
        pay_frame = tb.Frame(self.frame)
        pay_frame.pack(fill="x", pady=6)

        left_pay = tb.Frame(pay_frame)
        left_pay.pack(side="left", fill="x", expand=True, padx=6)

        tb.Label(left_pay, text=self.texts["bn"]["seller"], font=("Helvetica", 10)).grid(row=0, column=0, padx=3, pady=2, sticky="e")
        self.seller_var = tk.StringVar(value="Admin")
        tb.Entry(left_pay, textvariable=self.seller_var, width=16).grid(row=0, column=1, padx=3, pady=2, sticky="w")

        tb.Label(left_pay, text=self.texts["bn"]["customer"], font=("Helvetica", 10)).grid(row=0, column=2, padx=3, pady=2, sticky="e")
        self.customer_var = tk.StringVar()
        tb.Entry(left_pay, textvariable=self.customer_var, width=18).grid(row=0, column=3, padx=3, pady=2, sticky="w")

        tb.Label(left_pay, text=self.texts["bn"]["paid"], font=("Helvetica", 10)).grid(row=1, column=0, padx=3, pady=2, sticky="e")
        self.paid_var = tk.DoubleVar(value=0.0)
        paid_entry = tb.Entry(left_pay, textvariable=self.paid_var, width=14)
        paid_entry.grid(row=1, column=1, padx=3, pady=2, sticky="w")
        paid_entry.bind("<KeyRelease>", lambda e: self.update_due_amount())
        paid_entry.bind("<FocusOut>", lambda e: self._normalize_float(self.paid_var, minimum=0.0))
        ToolTip(paid_entry, "প্রদেয় টাকা | Paid Amount")

        tb.Label(left_pay, text=self.texts["bn"]["due"], font=("Helvetica", 10)).grid(row=1, column=2, padx=3, pady=2, sticky="e")
        self.due_var = tk.DoubleVar(value=0.0)
        tb.Label(left_pay, textvariable=self.due_var, font=("Helvetica", 11, "bold"), bootstyle="danger").grid(row=1, column=3, padx=3, pady=2, sticky="w")

        # ---------- Payment method and action buttons ----------
        right_pay = tb.Frame(pay_frame)
        right_pay.pack(side="right", padx=6)

        tb.Label(right_pay, text=self.texts["bn"]["payment"], font=("Helvetica", 10)).grid(row=0, column=0, padx=3, pady=2, sticky="e")
        self.payment_combo = tb.Combobox(right_pay, textvariable=self.selected_payment_method,
                                         values=["ক্যাশ", "বাকি", "নগদ", "রকেট", "বিকাশ", "অন্যান্য"],
                                         state="readonly", width=12, bootstyle="info")
        self.payment_combo.grid(row=0, column=1, padx=3, pady=2, sticky="w")
        ToolTip(self.payment_combo, "পেমেন্ট নির্বাচন | Select payment method")

        self.btn_finalize = tb.Button(right_pay, text=self.texts["bn"]["sale_done"], bootstyle="success", command=self.finalize_sale)
        self.btn_finalize.grid(row=1, column=0, columnspan=2, padx=3, pady=4)
        self.btn_finalize.bind("<Return>", lambda e: self.finalize_sale())
        ToolTip(self.btn_finalize, "বিক্রয় সম্পন্ন করুন | Finalize sale (Enter)")

        self.btn_export = tb.Button(right_pay, text=self.texts["bn"]["export_excel"], bootstyle="secondary", command=self.export_excel)
        self.btn_export.grid(row=2, column=0, padx=3, pady=2)
        ToolTip(self.btn_export, "Export Excel | Export to Excel")

        self.btn_print = tb.Button(right_pay, text=self.texts["bn"]["print_receipt"], bootstyle="primary", command=self.print_receipt)
        self.btn_print.grid(row=2, column=1, padx=3, pady=2)
        ToolTip(self.btn_print, "রসিদ প্রিন্ট | Print receipt")

        # ---------- Recent & Due ----------
        bottom_frame = tb.Frame(self.frame)
        bottom_frame.pack(fill="both", pady=6)

        recent_frame = tb.Labelframe(bottom_frame, text=self.texts["bn"]["recent_sale"], padding=6, bootstyle="secondary")
        recent_frame.pack(side="left", fill="both", expand=True, padx=6)
        recent_columns = ("product", "qty", "total", "due", "customer_col")
        self.recent_tree = ttk.Treeview(recent_frame, columns=recent_columns, show="headings", height=5)
        for col in recent_columns:
            self.recent_tree.heading(col, text=self.texts["bn"].get(col, col))
            self.recent_tree.column(col, anchor=tk.CENTER, width=80)
        self.recent_tree.pack(fill="both", expand=True)
        ToolTip(self.recent_tree, "সাম্প্রতিক বিক্রয় | Recent sales")

        due_frame = tb.Labelframe(bottom_frame, text=self.texts["bn"]["due_payment"], padding=6, bootstyle="danger")
        due_frame.pack(side="right", fill="both", expand=True, padx=6)
        due_columns = ("customer_col", "amount_col", "date_col")
        self.due_tree = ttk.Treeview(due_frame, columns=due_columns, show="headings", height=5)
        for col in due_columns:
            self.due_tree.heading(col, text=self.texts["bn"].get(col, col))
            self.due_tree.column(col, anchor=tk.CENTER, width=100)
        self.due_tree.pack(fill="both", expand=True)
        ToolTip(self.due_tree, "বাকি প্রদায়ন | Due payments")

        # ---------- Monthly summary table ----------
        monthly_frame = tb.Labelframe(self.frame, text=self.texts["bn"]["monthly_sale"], padding=6, bootstyle="info")
        monthly_frame.pack(fill="both", expand=False, padx=6, pady=4)
        monthly_columns = ("date", "total")
        self.monthly_tree = ttk.Treeview(monthly_frame, columns=monthly_columns, show="headings", height=4)
        for col in monthly_columns:
            self.monthly_tree.heading(col, text=self.texts["bn"][col])
            self.monthly_tree.column(col, anchor=tk.CENTER, width=120)
        self.monthly_tree.pack(fill="both", expand=True)
        ToolTip(self.monthly_tree, "মাসিক বিক্রয় | Monthly sales")

        # Initial loads
        self.load_products()
        self.load_today_total()
        self.load_recent_sales()
        self.load_monthly_sales()
        self.load_due_payments()
        self.update_current_line_total()

        # Keyboard shortcut: Ctrl+F for search
        self.frame.bind_all("<Control-f>", self.focus_search)
        # Keyboard shortcut: Enter for finalize sale (when focus on button)
        self.btn_finalize.bind("<Return>", lambda e: self.finalize_sale())
        # Keyboard shortcut: Enter for add to cart (when focus on button)
        self.btn_add_cart.bind("<Return>", lambda e: self.add_to_cart())

    # ---------- Multi-language toggle ----------
    def toggle_language(self):
        cur = self.lang.get()
        nxt = "en" if cur == "bn" else "bn"
        self.lang.set(nxt)
        t = self.texts[nxt]
        # Update all text labels/buttons
        self.label_today_sale.config(text=t["today_sale"])
        self.label_cart_total.config(text="  |  "+t["cart_total"])
        self.btn_refresh.config(text=t["refresh"])
        self.btn_help.config(text=t["help"])
        self.btn_add_cart.config(text=t["add_to_cart"])
        self.product_info_var.set(f"{t['purchase_price']}: - | "
                                 f"{t['stock']}: - | "
                                 f"{t['sale_price']}: -")
        self.label_line_total.config(text=t["line_total"])
        self.btn_remove_selected.config(text=t["del_selected"])
        self.btn_clear_cart.config(text=t["clear_cart"])
        self.payment_combo.config()
        self.btn_finalize.config(text=t["sale_done"])
        self.btn_export.config(text=t["export_excel"])
        self.btn_print.config(text=t["print_receipt"])
        # Treeviews headings update
        for i, col in enumerate(self.cart_tree_columns):
            self.cart_tree.heading(col, text=t.get(col, col))
        for i, col in enumerate(("product", "qty", "total", "due", "customer_col")):
            self.recent_tree.heading(col, text=t.get(col, col))
        for i, col in enumerate(("customer_col", "amount_col", "date_col")):
            self.due_tree.heading(col, text=t.get(col, col))
        for i, col in enumerate(("date", "total")):
            self.monthly_tree.heading(col, text=t.get(col, col))
        self.frame.update_idletasks()

    # ---------- Help popup ----------
    def show_help(self):
        help_text_bn = (
            "বিক্রয় UI ব্যবহারের টিপস:\n"
            "- পণ্য খুঁজুন (Ctrl+F)\n"
            "- পরিমাণ/ছাড় দিয়ে কার্টে যোগ করুন (Enter)\n"
            "- কার্ট থেকে পণ্য মুছে ফেলুন বা খালি করুন\n"
            "- বিক্রয়কারী/গ্রাহক/প্রদেয়/বাকি/পেমেন্ট নির্বাচন\n"
            "- বিক্রয় সম্পন্ন করুন (Enter)\n"
            "- Export/Print/Refresh\n"
            "- ভাষা টগল (EN/BN)\n"
            "- Tooltip-এ হোভার করলে সাহায্য পাওয়া যাবে\n"
        )
        help_text_en = (
            "Sale UI Usage Tips:\n"
            "- Search product (Ctrl+F)\n"
            "- Enter quantity/discount then add to cart (Enter)\n"
            "- Remove/clear items from cart\n"
            "- Select seller/customer/paid/due/payment\n"
            "- Finalize sale (Enter)\n"
            "- Export/Print/Refresh\n"
            "- Language toggle (EN/BN)\n"
            "- Hover for tooltips/help\n"
        )
        messagebox.showinfo("Help", help_text_bn if self.lang.get() == "bn" else help_text_en)

    # ---------- Focus search box ----------
    def focus_search(self, event=None):
        self.search_entry.focus_set()

    def _normalize_int(self, var: tk.IntVar, minimum=0):
        try:
            v = int(var.get())
        except Exception:
            v = minimum
        if v < minimum:
            v = minimum
        var.set(v)

    def _normalize_float(self, var: tk.DoubleVar, minimum=0.0):
        try:
            v = float(var.get())
        except Exception:
            v = minimum
        if v < minimum:
            v = minimum
        var.set(v)

    # ---------- Products ----------
    def load_products(self):
        try:
            products = get_all_products()
            self.products = [(p["id"], p["name"], p["purchase_price"], p["sale_price"], p["stock"]) for p in products]
        except Exception as e:
            messagebox.showerror("DB Error", f"Products load failed:\n{e}")
            self.products = []
        self.visible_products = list(self.products)
        self._fill_product_combo(self.visible_products)

    def _fill_product_combo(self, plist):
        names = [f"{p[1]} ({p[3]} ৳)" for p in plist]
        self.product_combo["values"] = names
        if names:
            self.product_combo.current(0)
            self.show_product_details()
        else:
            self.product_combo.set("")
            self.product_info_var.set(f"{self.texts[self.lang.get()]['purchase_price']}: - | "
                                     f"{self.texts[self.lang.get()]['stock']}: - | "
                                     f"{self.texts[self.lang.get()]['sale_price']}: -")
            self.current_line_total_var.set(0.0)

    # ---------- Enhanced Search/Filter & Live Suggestion ----------
    def update_product_list(self, event=None):
        key = self.search_var.get().lower().strip()
        # Filter by name or code (assuming code is in name or description)
        if not key:
            self.visible_products = list(self.products)
        else:
            self.visible_products = [p for p in self.products if key in p[1].lower()]
            # live suggestion: auto-select first matching product
            if self.visible_products:
                self.product_combo["values"] = [f"{p[1]} ({p[3]} ৳)" for p in self.visible_products]
                self.product_combo.current(0)
                self.show_product_details()
            else:
                self.product_combo.set("")
                self.product_info_var.set(f"{self.texts[self.lang.get()]['purchase_price']}: - | "
                                         f"{self.texts[self.lang.get()]['stock']}: - | "
                                         f"{self.texts[self.lang.get()]['sale_price']}: -")
                self.current_line_total_var.set(0.0)

    def show_product_details(self, event=None):
        idx = self.product_combo.current()
        if idx < 0 or idx >= len(self.visible_products):
            return
        p = self.visible_products[idx]
        name, purchase, sale, stock = p[1], p[2], p[3], p[4]
        self.product_info_var.set(f"{self.texts[self.lang.get()]['purchase_price']}: {purchase} | "
                                 f"{self.texts[self.lang.get()]['stock']}: {stock} | "
                                 f"{self.texts[self.lang.get()]['sale_price']}: {sale}")
        self.update_current_line_total()

    def update_current_line_total(self):
        idx = self.product_combo.current()
        if idx < 0 or idx >= len(self.visible_products):
            self.current_line_total_var.set(0.0)
            return
        p = self.visible_products[idx]
        unit_price = p[3]
        qty = self.quantity_var.get()
        discount = self.discount_var.get()
        total = max(0.0, unit_price * qty - discount)
        self.current_line_total_var.set(total)

    # ---------- Cart ----------
    def add_to_cart(self, event=None):
        idx = self.product_combo.current()
        if idx < 0 or idx >= len(self.visible_products):
            messagebox.showwarning("Warning", self.texts[self.lang.get()]["select_product"])
            return
        p = self.visible_products[idx]
        pid, name, purchase, sale, stock = p
        qty = self.quantity_var.get()
        discount = self.discount_var.get()
        if qty > stock:
            messagebox.showwarning("Warning", f"{self.texts[self.lang.get()]['low_stock']} ({self.texts[self.lang.get()]['stock']}: {stock})")
            return

        if pid in self.cart_items:
            self.cart_items[pid]["quantity"] += qty
            self.cart_items[pid]["discount"] += discount
        else:
            self.cart_items[pid] = {"name": name, "quantity": qty, "unit_price": sale, "discount": discount}

        self.refresh_cart()
        self.update_current_line_total()

    def refresh_cart(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
        total = 0.0
        for pid, item in self.cart_items.items():
            line_total = max(0.0, item["quantity"] * item["unit_price"] - item["discount"])
            self.cart_tree.insert("", "end", iid=str(pid),
                                 values=(item["name"], item["quantity"], item["unit_price"], item["discount"], line_total))
            total += line_total
        self.cart_total_var.set(total)
        self.update_due_amount()

    def remove_selected(self):
        sel = self.cart_tree.selection()
        for iid in sel:
            pid = int(iid)
            if pid in self.cart_items:
                del self.cart_items[pid]
        self.refresh_cart()

    def clear_cart(self):
        self.cart_items = {}
        self.refresh_cart()

    # ---------- Payment ----------
    def update_due_amount(self):
        due = max(0.0, self.cart_total_var.get() - self.paid_var.get())
        self.due_var.set(due)

    # ---------- Popup Notification/Alert & Animation ----------
    def finalize_sale(self, event=None):
        if not self.cart_items:
            messagebox.showwarning("Warning", self.texts[self.lang.get()]["cart_empty"])
            return
        seller = self.seller_var.get()
        customer = self.customer_var.get().strip()
        paid_amount = self.paid_var.get()
        payment_method = self.selected_payment_method.get()
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        txn_id, mobile = None, None
        if payment_method in ["রকেট", "বিকাশ"]:
            txn_id, mobile = ask_wallet_info(payment_method, self.frame)
            if txn_id is None:
                messagebox.showinfo("Info", f"{payment_method} তথ্য বাতিল হয়েছে। বিক্রয় স্থগিত।")
                return

        try:
            # Calculate due_amount for the whole sale
            total_price = self.cart_total_var.get()
            due_amount = max(0.0, total_price - paid_amount)
            
            # Use the new function signature
            sale_id = sale_and_stock_update(
                product_list=self.cart_items,
                total_price=total_price,
                discount=sum(item["discount"] for item in self.cart_items.values()),
                due_amount=due_amount,
                due_received_by=customer if due_amount > 0 else None,
                seller_name=seller,
                customer_name=customer,
                payment_method=payment_method,
                txn_id=txn_id,
                mobile_no=mobile,
            )

            self.sale_success_animation()
            messagebox.showinfo("Success", f"{self.texts[self.lang.get()]['sale_success']} {total_price:.2f} ৳")
            self.clear_cart()
            self.load_products()
            self.load_today_total()
            self.load_recent_sales()
            self.load_monthly_sales()
            self.load_due_payments()
        except Exception as e:
            messagebox.showerror("Error", f"বিক্রয় সম্পন্ন হয়নি:\n{e}")


    def sale_success_animation(self):
        # Animation: just flash the frame border color
        for i in range(2):
            self.frame.after(80)
            self.frame.update()
        # Animation is minimal to avoid ttkbootstrap error

    # ---------- Reports ----------
    def load_today_total(self):
        try:
            today = date.today().strftime("%Y-%m-%d")
            sales = get_all_sales()
            total = sum(s["total"] for s in sales if s["date"][:10] == today)
            self.today_total_var.set(total)
        except Exception:
            self.today_total_var.set(0.0)

    def load_recent_sales(self):
        try:
            sales = get_all_sales()
            sales_sorted = sorted(sales, key=lambda r: r["id"], reverse=True)[:10]
            products = {p["id"]: p["name"] for p in get_all_products()}
            for i in self.recent_tree.get_children():
                self.recent_tree.delete(i)
            for s in sales_sorted:
                pname = products.get(s["product_id"], "-")
                self.recent_tree.insert("", "end", values=(
                    pname,
                    s["quantity"],
                    s["total"],
                    s["due_amount"],
                    s["customer_name"] if s["customer_name"] else "-"
                ))
        except Exception:
            pass

    def load_monthly_sales(self):
        try:
            sales = get_all_sales()
            summary = {}
            for s in sales:
                d = s["date"][:10]
                summary[d] = summary.get(d, 0) + (s["total"] or 0)
            rows = sorted(summary.items(), key=lambda r: r[0], reverse=True)[:30]
            for i in self.monthly_tree.get_children():
                self.monthly_tree.delete(i)
            for r in rows:
                self.monthly_tree.insert("", "end", values=r)
        except Exception:
            pass

    def load_due_payments(self):
        try:
            dues = get_all_due_payment()
            rows = sorted(dues, key=lambda r: r["id"], reverse=True)[:10]
            for i in self.due_tree.get_children():
                self.due_tree.delete(i)
            for r in rows:
                self.due_tree.insert("", "end", values=(
                    r["customer"],
                    r["amount"],
                    r["date"][:10] if r["date"] else "-"
                ))
        except Exception:
            pass

    # ---------- Export / Print ----------
    def export_excel(self):
        if not self.cart_items:
            messagebox.showwarning("Warning", self.texts[self.lang.get()]["cart_empty"])
            return
        data = []
        for pid, item in self.cart_items.items():
            data.append({self.texts[self.lang.get()]["product"]: item["name"],
                          self.texts[self.lang.get()]["qty"]: item["quantity"],
                          "Unit Price": item["unit_price"],
                          self.texts[self.lang.get()]["discount"]: item["discount"],
                          "Total": max(0.0, item["unit_price"]*item["quantity"]-item["discount"])})
        df = pd.DataFrame(data)
        filename = f"sale_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        try:
            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")

    def print_receipt(self):
        if not self.cart_items:
            messagebox.showwarning("Warning", self.texts[self.lang.get()]["cart_empty"])
            return
        filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Smartshop রসিদ")
        y -= 30
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"{self.texts[self.lang.get()]['date']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y -= 20
        c.drawString(50, y, f"{self.texts[self.lang.get()]['seller']}: {self.seller_var.get()} | "
                                 f"{self.texts[self.lang.get()]['customer']}: {self.customer_var.get()}")
        y -= 30
        c.drawString(50, y, f"{self.texts[self.lang.get()]['product']:20}{self.texts[self.lang.get()]['qty']:>8}{'একক':>8}{self.texts[self.lang.get()]['discount']:>8}{'মোট':>8}")
        y -= 20
        for item in self.cart_items.values():
            line_total = max(0.0, item["quantity"]*item["unit_price"] - item["discount"])
            c.drawString(50, y, f"{item['name']:20}{item['quantity']:>8}{item['unit_price']:>8}{item['discount']:>8}{line_total:>8}")
            y -= 20
        y -= 10
        c.drawString(50, y, f"{self.texts[self.lang.get()]['total']}: {self.cart_total_var.get():.2f} ৳")
        c.save()
        messagebox.showinfo("Success", f"Receipt PDF: {filename}")

    # ---------- Refresh ----------
    def refresh_all(self):
        self.load_products()
        self.load_today_total()
        self.load_recent_sales()
        self.load_monthly_sales()
        self.load_due_payments()
        self.refresh_cart()