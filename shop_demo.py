import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# SMS (Twilio) import - সিমুলেটেড, আপনার অ্যাকাউন্ট ডিটেইলস দিন প্রয়োজনে
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

# প্রিন্টার ইন্টিগ্রেশন উইন্ডোজে(win32print) ব্যবহার করতে চাইলে pip install pywin32 প্রয়োজন,
# অথবা Tkinter এর print dialog ব্যাবহার করতে পারেন, cross-platform কিছু সীমাবদ্ধতা আছে

# -------------------------
#  ইউজার ও রোল ম্যানেজমেন্ট
# -------------------------
USERS_DB = {
    "admin": {"password": "admin123", "role": "admin"},
    "staff": {"password": "staff123", "role": "staff"},
}

class SmartShopPOS(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("SmartShop POS - Mobile & Printing Store")
        self.geometry("1200x750")
        self.minsize(1100, 700)

        self.light_theme = "flatly"
        self.dark_theme = "superhero"
        self.current_theme = self.light_theme

        self.sidebar_expanded = True
        self.sidebar_width_expanded = 220
        self.sidebar_width_collapsed = 70

        # ডাটা স্টোর
        self.products = []
        self.sales = []
        self.recharges = []
        self.printing_services = []

        self.users = USERS_DB
        self.logged_in_user = None
        self.logged_in_role = None

        self.shop_name = "SmartShop Mobile & Printing"
        self.shop_address = "Dhaka, Bangladesh"

        # Twilio config (যদি ব্যবহার করতে চান)
        self.twilio_sid = "YOUR_TWILIO_SID"
        self.twilio_token = "YOUR_TWILIO_TOKEN"
        self.twilio_from = "+1234567890"

        # UI নির্মাণ
        self.build_sidebar()
        self.build_topbar()
        self.build_main_area()
        self.create_pages()
        self.show_page("login")

    def build_sidebar(self):
        self.sidebar = tb.Frame(self, width=self.sidebar_width_expanded, bootstyle="dark")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.toggle_btn = tb.Button(self.sidebar, text="☰", bootstyle="secondary", command=self.toggle_sidebar)
        self.toggle_btn.pack(pady=10, padx=10)

        # রোল অনুসারে পেজ লিস্ট পরিবর্তন
        self.pages = {
            "dashboard": "ড্যাশবোর্ড",
            "sales": "বিক্রয়",
            "products": "পণ্য",
            "recharge": "রিচার্জ",
            "printing": "প্রিন্টিং সার্ভিস",
            "reports": "রিপোর্ট",
            "settings": "সেটিংস",
            "login": "লগইন",
        }

        self.sidebar_buttons = {}
        for key, name in self.pages.items():
            btn = tb.Button(self.sidebar, text=name, bootstyle="info-outline", command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", padx=10, pady=5)
            self.sidebar_buttons[key] = btn

    def build_topbar(self):
        self.topbar = tb.Frame(self, height=50, bootstyle="secondary")
        self.topbar.pack(side="top", fill="x")

        self.page_title = tb.Label(self.topbar, text="Welcome", font=("Helvetica", 16, "bold"), bootstyle="inverse-secondary")
        self.page_title.pack(side="left", padx=20)

        self.theme_btn = tb.Button(self.topbar, text="Switch Theme", bootstyle="secondary", command=self.toggle_theme)
        self.theme_btn.pack(side="right", padx=20)

        self.profile_label = tb.Label(self.topbar, text="Guest", bootstyle="inverse-secondary")
        self.profile_label.pack(side="right", padx=10)

        self.logout_btn = tb.Button(self.topbar, text="Logout", bootstyle="danger", command=self.logout_user)
        self.logout_btn.pack(side="right", padx=10)
        self.logout_btn.pack_forget()

    def build_main_area(self):
        self.main_area = tb.Frame(self, bootstyle="light")
        self.main_area.pack(side="right", fill="both", expand=True)

    def create_pages(self):
        self.pages_frames = {}

        # ড্যাশবোর্ড
        dash = tb.Frame(self.main_area, bootstyle="light")
        tb.Label(dash, text=self.shop_name, font=("Helvetica", 22, "bold")).pack(pady=10)
        tb.Label(dash, text=self.shop_address, font=("Helvetica", 14)).pack()
        self.daily_sales_label = tb.Label(dash, text="আজকের বিক্রয়: 0", font=("Helvetica", 18), bootstyle="success")
        self.daily_sales_label.pack(pady=30)
        dash.place(relwidth=1, relheight=1)
        self.pages_frames["dashboard"] = dash

        # বিক্রয়
        sales = tb.Frame(self.main_area, bootstyle="light")
        tb.Label(sales, text="বিক্রয়", font=("Helvetica", 20)).pack(pady=10)
        self.sale_product_cb = ttk.Combobox(sales, values=[], state="readonly")
        self.sale_product_cb.pack(pady=5)
        self.sale_quantity_var = tk.IntVar(value=1)
        tb.Label(sales, text="পরিমাণ").pack()
        tb.Entry(sales, textvariable=self.sale_quantity_var).pack(pady=5)
        tb.Button(sales, text="বিক্রয় করুন", bootstyle="success", command=self.add_sale).pack(pady=10)
        self.sales_listbox = tk.Listbox(sales)
        self.sales_listbox.pack(fill="both", expand=True, padx=20, pady=10)

        # এক্সেল ও পিডিএফ এক্সপোর্ট বাটন
        export_frame = tb.Frame(sales)
        export_frame.pack(pady=5)
        tb.Button(export_frame, text="Export to Excel", bootstyle="info", command=self.export_sales_excel).pack(side="left", padx=5)
        tb.Button(export_frame, text="Export to PDF", bootstyle="info", command=self.export_sales_pdf).pack(side="left", padx=5)

        sales.place(relwidth=1, relheight=1)
        self.pages_frames["sales"] = sales

        # পণ্য
        products = tb.Frame(self.main_area, bootstyle="light")
        tb.Label(products, text="পণ্য ব্যবস্থাপনা", font=("Helvetica", 20)).pack(pady=10)
        tb.Button(products, text="নতুন পণ্য যোগ করুন", bootstyle="primary", command=self.add_product_dialog).pack(pady=10)
        self.products_listbox = tk.Listbox(products)
        self.products_listbox.pack(fill="both", expand=True, padx=20, pady=10)
        products.place(relwidth=1, relheight=1)
        self.pages_frames["products"] = products

        # রিচার্জ
        recharge = tb.Frame(self.main_area, bootstyle="light")
        tb.Label(recharge, text="মোবাইল রিচার্জ", font=("Helvetica", 20)).pack(pady=10)
        tb.Label(recharge, text="অপারেটর নির্বাচন করুন:").pack()
        self.operator_var = tk.StringVar()
        operator_cb = ttk.Combobox(recharge, values=["GP", "Robi", "Airtel", "Banglalink"], textvariable=self.operator_var, state="readonly")
        operator_cb.pack(pady=5)
        tb.Label(recharge, text="মোবাইল নাম্বার:").pack()
        self.mobile_entry = tb.Entry(recharge)
        self.mobile_entry.pack(pady=5)
        tb.Label(recharge, text="টাকার পরিমাণ:").pack()
        self.amount_var = tk.DoubleVar()
        tb.Entry(recharge, textvariable=self.amount_var).pack(pady=5)
        tb.Button(recharge, text="রিচার্জ করুন", bootstyle="success", command=self.add_recharge).pack(pady=10)
        self.recharge_listbox = tk.Listbox(recharge)
        self.recharge_listbox.pack(fill="both", expand=True, padx=20, pady=10)
        recharge.place(relwidth=1, relheight=1)
        self.pages_frames["recharge"] = recharge

        # প্রিন্টিং সার্ভিস
        printing = tb.Frame(self.main_area, bootstyle="light")
        tb.Label(printing, text="প্রিন্টিং সার্ভিস", font=("Helvetica", 20)).pack(pady=10)
        tb.Label(printing, text="কালার প্রিন্টিং (প্রতি পৃষ্ঠা):").pack()
        self.color_price_var = tk.DoubleVar(value=10)
        tb.Entry(printing, textvariable=self.color_price_var).pack(pady=5)
        tb.Label(printing, text="ব্ল্যাক অ্যান্ড হোয়াইট (প্রতি পৃষ্ঠা):").pack()
        self.bw_price_var = tk.DoubleVar(value=5)
        tb.Entry(printing, textvariable=self.bw_price_var).pack(pady=5)
        tb.Label(printing, text="প্রিন্টের পৃষ্ঠা সংখ্যা:").pack()
        self.print_pages_var = tk.IntVar(value=1)
        tb.Entry(printing, textvariable=self.print_pages_var).pack(pady=5)
        tb.Button(printing, text="সার্ভিস যুক্ত করুন", bootstyle="success", command=self.add_printing_service).pack(pady=10)
        self.printing_listbox = tk.Listbox(printing)
        self.printing_listbox.pack(fill="both", expand=True, padx=20, pady=10)

        # প্রিন্ট সার্ভিসের রিপোর্ট এক্সপোর্ট বাটন
        tb.Button(printing, text="Export Printing Report Excel", bootstyle="info", command=self.export_printing_excel).pack(pady=5)

        printing.place(relwidth=1, relheight=1)
        self.pages_frames["printing"] = printing

        # রিপোর্ট
        reports = tb.Frame(self.main_area, bootstyle="light")
        tb.Label(reports, text="রিপোর্ট", font=("Helvetica", 20)).pack(pady=10)
        self.report_text = tk.Text(reports, state="disabled")
        self.report_text.pack(fill="both", expand=True, padx=20, pady=10)
        tb.Button(reports, text="আজকের বিক্রয় রিপোর্ট দেখুন", bootstyle="info", command=self.show_daily_report).pack(pady=5)

        # রিপোর্ট এক্সপোর্ট বাটন
        export_frame = tb.Frame(reports)
        export_frame.pack(pady=5)
        tb.Button(export_frame, text="Export Full Report Excel", bootstyle="info", command=self.export_full_report_excel).pack(side="left", padx=5)
        tb.Button(export_frame, text="Export Full Report PDF", bootstyle="info", command=self.export_full_report_pdf).pack(side="left", padx=5)

        reports.place(relwidth=1, relheight=1)
        self.pages_frames["reports"] = reports

        # সেটিংস
        settings = tb.Frame(self.main_area, bootstyle="light")
        tb.Label(settings, text="সেটিংস", font=("Helvetica", 20)).pack(pady=10)
        tb.Label(settings, text="দোকানের নাম:").pack()
        self.shop_name_var = tk.StringVar(value=self.shop_name)
        tb.Entry(settings, textvariable=self.shop_name_var).pack(pady=5)
        tb.Label(settings, text="ঠিকানা:").pack()
        self.shop_address_var = tk.StringVar(value=self.shop_address)
        tb.Entry(settings, textvariable=self.shop_address_var).pack(pady=5)
        tb.Button(settings, text="সেভ করুন", bootstyle="primary", command=self.save_settings).pack(pady=10)

        # SMS Config (Optional)
        tb.Separator(settings).pack(fill='x', pady=10)
        tb.Label(settings, text="SMS Configuration (Twilio)", font=("Helvetica", 16, "bold")).pack(pady=5)
        tb.Label(settings, text="Twilio SID:").pack()
        self.twilio_sid_var = tk.StringVar(value=self.twilio_sid)
        tb.Entry(settings, textvariable=self.twilio_sid_var).pack(pady=5)
        tb.Label(settings, text="Twilio Token:").pack()
        self.twilio_token_var = tk.StringVar(value=self.twilio_token)
        tb.Entry(settings, textvariable=self.twilio_token_var, show="*").pack(pady=5)
        tb.Label(settings, text="From Number (+1234567890):").pack()
        self.twilio_from_var = tk.StringVar(value=self.twilio_from)
        tb.Entry(settings, textvariable=self.twilio_from_var).pack(pady=5)
        tb.Button(settings, text="সেভ করুন", bootstyle="primary", command=self.save_sms_settings).pack(pady=10)

        settings.place(relwidth=1, relheight=1)
        self.pages_frames["settings"] = settings

        # লগইন
        login = tb.Frame(self.main_area, bootstyle="light")
        tb.Label(login, text="লগইন", font=("Helvetica", 20)).pack(pady=20)
        tb.Label(login, text="Username:").pack()
        self.username_entry = tb.Entry(login)
        self.username_entry.pack(pady=5)
        tb.Label(login, text="Password:").pack()
        self.password_entry = tb.Entry(login, show="*")
        self.password_entry.pack(pady=5)
        tb.Button(login, text="Login", bootstyle="primary", command=self.login_user).pack(pady=10)
        login.place(relwidth=1, relheight=1)
        self.pages_frames["login"] = login

    def show_page(self, key):
        # Role based access
        if key != "login" and not self.logged_in_user:
            messagebox.showwarning("অনুমতি প্রয়োজন", "অনুগ্রহ করে প্রথমে লগইন করুন।")
            self.show_page("login")
            return

        # Staff limitations (example)
        if self.logged_in_role == "staff" and key in ["settings", "products"]:
            messagebox.showinfo("Access Denied", "আপনার রোল এই পেজ অ্যাক্সেসের অনুমতি নেই।")
            return

        frame = self.pages_frames.get(key)
        if frame:
            frame.tkraise()
        name = self.pages.get(key, key)
        self.page_title.config(text=name)

        for k, btn in self.sidebar_buttons.items():
            if k == key:
                btn.configure(bootstyle="info")
            else:
                btn.configure(bootstyle="info-outline")

        if key == "login":
            self.logout_btn.pack_forget()
            self.profile_label.config(text="Guest")
        else:
            self.logout_btn.pack(side="right", padx=10)
            self.profile_label.config(text=f"{self.logged_in_user} ({self.logged_in_role})")

    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar.config(width=self.sidebar_width_collapsed)
            for btn in self.sidebar_buttons.values():
                btn.pack_forget()
            self.toggle_btn.pack_forget()
            self.toggle_btn.pack(pady=10, padx=10)
            self.sidebar_expanded = False
        else:
            self.sidebar.config(width=self.sidebar_width_expanded)
            for btn in self.sidebar_buttons.values():
                btn.pack(fill="x", padx=10, pady=5)
            self.toggle_btn.pack(pady=10, padx=10)
            self.sidebar_expanded = True

    def toggle_theme(self):
        if self.current_theme == self.light_theme:
            self.style.theme_use(self.dark_theme)
            self.current_theme = self.dark_theme
        else:
            self.style.theme_use(self.light_theme)
            self.current_theme = self.light_theme

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username in self.users and self.users[username]["password"] == password:
            self.logged_in_user = username
            self.logged_in_role = self.users[username]["role"]
            self.profile_label.config(text=f"Welcome, {username}")
            messagebox.showinfo("লগইন সফল", f"স্বাগতম {username}!")
            self.show_page("dashboard")
            self.refresh_products()
            self.refresh_sale_products()
            self.refresh_sales()
            self.refresh_recharges()
            self.refresh_printing()
        else:
            messagebox.showerror("ত্রুটি", "ভুল ইউজারনেম বা পাসওয়ার্ড!")

    def logout_user(self):
        self.logged_in_user = None
        self.logged_in_role = None
        self.profile_label.config(text="Guest")
        messagebox.showinfo("লগআউট", "আপনি সফলভাবে লগআউট হয়েছেন।")
        self.show_page("login")

    # Product management
    def add_product_dialog(self):
        dialog = ProductDialog(self)
        self.wait_window(dialog.top)
        if dialog.result:
            self.products.append(dialog.result)
            self.refresh_products()
            self.refresh_sale_products()

    def refresh_products(self):
        self.products_listbox.delete(0, tk.END)
        for p in self.products:
            display_text = f"{p['name']} ({p['category']}) - স্টক: {p['stock']} দাম: {p['price']} টাকা"
            self.products_listbox.insert(tk.END, display_text)

    def refresh_sale_products(self):
        product_names = [p["name"] for p in self.products]
        self.sale_product_cb["values"] = product_names

    # Sales
    def add_sale(self):
        product_name = self.sale_product_cb.get()
        quantity = self.sale_quantity_var.get()
        if not product_name:
            messagebox.showwarning("ত্রুটি", "পণ্য নির্বাচন করুন।")
            return
        if quantity <= 0:
            messagebox.showwarning("ত্রুটি", "পরিমাণ অবশ্যই ১ বা তার বেশি হতে হবে।")
            return

        product = next((p for p in self.products if p["name"] == product_name), None)
        if not product:
            messagebox.showerror("ত্রুটি", "পণ্য পাওয়া যায়নি।")
            return

        if product["stock"] < quantity:
            messagebox.showwarning("ত্রুটি", "স্টক পর্যাপ্ত নেই।")
            return

        total_price = product["price"] * quantity
        product["stock"] -= quantity
        sale_record = {
            "product": product_name,
            "quantity": quantity,
            "price_per_unit": product["price"],
            "total": total_price,
            "datetime": datetime.now()
        }
        self.sales.append(sale_record)
        self.refresh_products()
        self.refresh_sales()
        self.update_daily_sales()
        messagebox.showinfo("বিক্রয় সফল", f"{quantity} টি {product_name} বিক্রয় হয়েছে।")

        # SMS নোটিফিকেশন (ঐচ্ছিক)
        if TWILIO_AVAILABLE:
            self.send_sms_notification(f"{quantity} টি {product_name} বিক্রয় হয়েছে। মোট দাম: {total_price} টাকা।")

    def refresh_sales(self):
        self.sales_listbox.delete(0, tk.END)
        for s in self.sales:
            time_str = s["datetime"].strftime("%Y-%m-%d %H:%M")
            line = f"{time_str} - {s['product']} - পরিমাণ: {s['quantity']} - মূল্য: {s['total']} টাকা"
            self.sales_listbox.insert(tk.END, line)

    # Recharge
    def add_recharge(self):
        operator = self.operator_var.get()
        mobile = self.mobile_entry.get().strip()
        amount = self.amount_var.get()
        if not operator or not mobile or amount <= 0:
            messagebox.showwarning("ত্রুটি", "সঠিক তথ্য প্রদান করুন।")
            return
        record = {
            "operator": operator,
            "mobile": mobile,
            "amount": amount,
            "datetime": datetime.now()
        }
        self.recharges.append(record)
        self.refresh_recharges()
        messagebox.showinfo("রিচার্জ সফল", f"{mobile} নম্বরে {amount} টাকা রিচার্জ হয়েছে।")

        # SMS নোটিফিকেশন (ঐচ্ছিক)
        if TWILIO_AVAILABLE:
            self.send_sms_notification(f"{mobile} নম্বরে {amount} টাকা রিচার্জ হয়েছে।")

    def refresh_recharges(self):
        recharge_frame = self.pages_frames.get("recharge")
        if recharge_frame:
            listbox = recharge_frame.children.get("!listbox")
            if listbox:
                listbox.delete(0, tk.END)
                for r in self.recharges:
                    time_str = r["datetime"].strftime("%Y-%m-%d %H:%M")
                    line = f"{time_str} - {r['operator']} - {r['mobile']} - {r['amount']} টাকা"
                    listbox.insert(tk.END, line)

    # Printing service
    def add_printing_service(self):
        color_price = self.color_price_var.get()
        bw_price = self.bw_price_var.get()
        pages = self.print_pages_var.get()
        if pages <= 0:
            messagebox.showwarning("ত্রুটি", "পৃষ্ঠা সংখ্যা অবশ্যই ১ বা তার বেশি হতে হবে।")
            return
        choice = messagebox.askquestion("প্রিন্ট টাইপ", "কালার প্রিন্টিং করবেন? না ব্ল্যাক অ্যান্ড হোয়াইট?")
        if choice == "yes":
            price = color_price * pages
            print_type = "কালার"
        else:
            price = bw_price * pages
            print_type = "ব্ল্যাক অ্যান্ড হোয়াইট"

        record = {
            "type": print_type,
            "pages": pages,
            "price": price,
            "datetime": datetime.now()
        }
        self.printing_services.append(record)
        self.sales.append(record)  # একত্রিত রিপোর্টের জন্য
        self.refresh_printing()
        self.update_daily_sales()
        messagebox.showinfo("সার্ভিস যুক্ত", f"{pages} পৃষ্ঠা {print_type} প্রিন্ট যোগ করা হয়েছে।")

        # SMS নোটিফিকেশন (ঐচ্ছিক)
        if TWILIO_AVAILABLE:
            self.send_sms_notification(f"{pages} পৃষ্ঠা {print_type} প্রিন্ট হয়েছে। দাম: {price} টাকা।")

    def refresh_printing(self):
        printing_frame = self.pages_frames.get("printing")
        if printing_frame:
            listbox = printing_frame.children.get("!listbox")
            if listbox:
                listbox.delete(0, tk.END)
                for p in self.printing_services:
                    time_str = p["datetime"].strftime("%Y-%m-%d %H:%M")
                    line = f"{time_str} - {p['type']} - পৃষ্ঠা: {p['pages']} - দাম: {p['price']} টাকা"
                    listbox.insert(tk.END, line)

    # Daily Sales update
    def update_daily_sales(self):
        today = datetime.now().date()
        total_sales = sum(s["total"] for s in self.sales if "total" in s and s["datetime"].date() == today)
        total_recharge = sum(r["amount"] for r in self.recharges if r["datetime"].date() == today)
        total_print = sum(p["price"] for p in self.printing_services if p["datetime"].date() == today)

        total = total_sales + total_recharge + total_print
        self.daily_sales_label.config(text=f"আজকের মোট আয়: {total} টাকা")

    # রিপোর্ট
    def show_daily_report(self):
        today = datetime.now().date()
        total_sales = sum(s["total"] for s in self.sales if "total" in s and s["datetime"].date() == today)
        total_recharge = sum(r["amount"] for r in self.recharges if r["datetime"].date() == today)
        total_print = sum(p["price"] for p in self.printing_services if p["datetime"].date() == today)

        report = f"""
আজকের রিপোর্ট ({today}):
-----------------------------
বিক্রয় থেকে আয়: {total_sales} টাকা
রিচার্জ থেকে আয়: {total_recharge} টাকা
প্রিন্টিং থেকে আয়: {total_print} টাকা
-----------------------------
মোট আয়: {total_sales + total_recharge + total_print} টাকা
"""
        self.report_text.config(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)
        self.report_text.config(state="disabled")

    # এক্সেল/পিডিএফ এক্সপোর্ট (Sales)
    def export_sales_excel(self):
        if not self.sales:
            messagebox.showwarning("ত্রুটি", "কোনো বিক্রয় রেকর্ড নেই।")
            return
        df = pd.DataFrame(self.sales)
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if filename:
            df.to_excel(filename, index=False)
            messagebox.showinfo("সফল", f"বিক্রয় রিপোর্ট এক্সেল ফাইলে সেভ হয়েছে:\n{filename}")

    def export_sales_pdf(self):
        if not self.sales:
            messagebox.showwarning("ত্রুটি", "কোনো বিক্রয় রেকর্ড নেই।")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if not filename:
            return
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, height - 40, f"বিক্রয় রিপোর্ট - {datetime.now().date()}")
        c.setFont("Helvetica", 12)
        y = height - 70
        for s in self.sales:
            line = f"{s['datetime'].strftime('%Y-%m-%d %H:%M')} | {s['product']} | Qty: {s['quantity']} | Price: {s['total']} টাকা"
            c.drawString(30, y, line)
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
        messagebox.showinfo("সফল", f"বিক্রয় রিপোর্ট পিডিএফ ফাইলে সেভ হয়েছে:\n{filename}")

    # এক্সেল প্রিন্টিং রিপোর্ট এক্সপোর্ট
    def export_printing_excel(self):
        if not self.printing_services:
            messagebox.showwarning("ত্রুটি", "কোনো প্রিন্টিং রেকর্ড নেই।")
            return
        df = pd.DataFrame(self.printing_services)
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if filename:
            df.to_excel(filename, index=False)
            messagebox.showinfo("সফল", f"প্রিন্টিং রিপোর্ট এক্সেল ফাইলে সেভ হয়েছে:\n{filename}")

    # সম্পূর্ণ রিপোর্ট এক্সপোর্ট (Excel + PDF)
    def export_full_report_excel(self):
        data = {
            "Sales": self.sales,
            "Recharges": self.recharges,
            "Printing": self.printing_services
        }
        # Combine to one Excel with multiple sheets
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not filename:
            return
        with pd.ExcelWriter(filename) as writer:
            if self.sales:
                pd.DataFrame(self.sales).to_excel(writer, sheet_name="Sales", index=False)
            if self.recharges:
                pd.DataFrame(self.recharges).to_excel(writer, sheet_name="Recharges", index=False)
            if self.printing_services:
                pd.DataFrame(self.printing_services).to_excel(writer, sheet_name="Printing", index=False)
        messagebox.showinfo("সফল", f"সম্পূর্ণ রিপোর্ট এক্সেল ফাইলে সেভ হয়েছে:\n{filename}")

    def export_full_report_pdf(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if not filename:
            return
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 18)
        c.drawString(30, height - 40, f"SmartShop সম্পূর্ণ রিপোর্ট")
        y = height - 70
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "বিক্রয়:")
        y -= 25
        c.setFont("Helvetica", 12)
        if self.sales:
            for s in self.sales:
                line = f"{s['datetime'].strftime('%Y-%m-%d %H:%M')} | {s['product']} | Qty: {s['quantity']} | Price: {s['total']} টাকা"
                c.drawString(30, y, line)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50
        else:
            c.drawString(30, y, "কোনো বিক্রয় রেকর্ড নেই।")
            y -= 20

        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "রিচার্জ:")
        y -= 25
        c.setFont("Helvetica", 12)
        if self.recharges:
            for r in self.recharges:
                line = f"{r['datetime'].strftime('%Y-%m-%d %H:%M')} | {r['operator']} | {r['mobile']} | Amount: {r['amount']} টাকা"
                c.drawString(30, y, line)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50
        else:
            c.drawString(30, y, "কোনো রিচার্জ রেকর্ড নেই।")
            y -= 20

        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "প্রিন্টিং সার্ভিস:")
        y -= 25
        c.setFont("Helvetica", 12)
        if self.printing_services:
            for p in self.printing_services:
                line = f"{p['datetime'].strftime('%Y-%m-%d %H:%M')} | {p['type']} | পৃষ্ঠা: {p['pages']} | দাম: {p['price']} টাকা"
                c.drawString(30, y, line)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50
        else:
            c.drawString(30, y, "কোনো প্রিন্টিং রেকর্ড নেই।")
            y -= 20

        c.save()
        messagebox.showinfo("সফল", f"সম্পূর্ণ রিপোর্ট পিডিএফ ফাইলে সেভ হয়েছে:\n{filename}")

    # সেটিংস সেভ
    def save_settings(self):
        self.shop_name = self.shop_name_var.get()
        self.shop_address = self.shop_address_var.get()
        messagebox.showinfo("সেটিংস সেভ হয়েছে", "দোকানের তথ্য সফলভাবে আপডেট হয়েছে।")
        self.pages_frames["dashboard"].winfo_children()[0].config(text=self.shop_name)
        self.pages_frames["dashboard"].winfo_children()[1].config(text=self.shop_address)

    def save_sms_settings(self):
        self.twilio_sid = self.twilio_sid_var.get()
        self.twilio_token = self.twilio_token_var.get()
        self.twilio_from = self.twilio_from_var.get()
        messagebox.showinfo("সেটিংস সেভ হয়েছে", "SMS সেটিংস সফলভাবে আপডেট হয়েছে।")

    # SMS Notification via Twilio
    def send_sms_notification(self, message):
        if not TWILIO_AVAILABLE:
            return
        try:
            client = Client(self.twilio_sid, self.twilio_token)
            # নম্বর পরিবর্তন করুন প্রয়োজন অনুযায়ী
            to_number = "+8801234567890"  
            client.messages.create(body=message, from_=self.twilio_from, to=to_number)
        except Exception as e:
            print("SMS পাঠানো ব্যর্থ:", e)

# নতুন পণ্য যোগ করার ডায়ালগ
class ProductDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None

        self.top = tb.Toplevel(parent)
        self.top.title("নতুন পণ্য যোগ করুন")
        self.top.geometry("350x300")
        self.top.resizable(False, False)

        tb.Label(self.top, text="পণ্যের নাম:").pack(pady=5)
        self.name_entry = tb.Entry(self.top)
        self.name_entry.pack(pady=5)

        tb.Label(self.top, text="ক্যাটাগরি:").pack(pady=5)
        self.category_entry = tb.Entry(self.top)
        self.category_entry.pack(pady=5)

        tb.Label(self.top, text="স্টক পরিমাণ:").pack(pady=5)
        self.stock_var = tk.IntVar(value=0)
        tb.Entry(self.top, textvariable=self.stock_var).pack(pady=5)

        tb.Label(self.top, text="মূল্য (টাকা):").pack(pady=5)
        self.price_var = tk.DoubleVar(value=0.0)
        tb.Entry(self.top, textvariable=self.price_var).pack(pady=5)

        tb.Button(self.top, text="যোগ করুন", bootstyle="success", command=self.on_add).pack(pady=10)

    def on_add(self):
        name = self.name_entry.get().strip()
        category = self.category_entry.get().strip()
        stock = self.stock_var.get()
        price = self.price_var.get()
        if not name or not category or stock < 0 or price <= 0:
            messagebox.showerror("ত্রুটি", "সঠিক তথ্য প্রদান করুন।")
            return
        self.result = {
            "name": name,
            "category": category,
            "stock": stock,
            "price": price
        }
        self.top.destroy()

if __name__ == "__main__":
    app = SmartShopPOS()
    app.mainloop()
