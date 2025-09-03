# ui/ui_main.py

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar, messagebox
import traceback

from .ui_dashboard import DashboardUI
from .ui_login import LoginUI
from .ui_settings import SettingsUI
from .ui_product import ProductUI
from .ui_stock import StockUI
from .ui_service import ServiceUI
from .ui_recharge import RechargeUI
from .ui_report import ReportUI
from .ui_expense import ExpenseUI
from .ui_due_payment import DuePaymentUI
from .ui_sale import SaleUI
from .ui_barcode import BarcodeUI
from .ui_print_utils import PrintUI
from db import update_user_info, safe_get_all_products

# ---------------- Sidebar Button ----------------
class SidebarButton(ttk.Button):
    def __init__(self, parent, text, command, active=False):
        super().__init__(
            parent,
            text=text,
            bootstyle="primary" if active else "secondary-outline",
            width=20,
            style="Sidebar.TButton",
            command=command,
        )
        self.pack(pady=(2, 0), padx=7, fill="x", anchor="n")

# ---------------- Main Application ----------------
class MainApp(ttk.Frame):
    def __init__(self, master=None, logout_callback=None):
        super().__init__(master)
        self.master = master
        self.logout_callback = logout_callback
        if master:
            master.title("SmartShop POS")
            master.geometry("1200x700")
            master.minsize(1100, 650)

        self.light_theme = "flatly"
        self.dark_theme = "darkly"
        self.current_theme = self.light_theme
        self.logged_in_user = None
        self.dashboard_mode = True  # True = Dashboard, False = Module

        # Layout
        self.left_frame = ttk.Frame(self, width=180, bootstyle="dark")
        self.left_frame.pack(side="left", fill="y")
        self.main_frame = ttk.Frame(self, bootstyle="light")
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Header
        self.header = ttk.Frame(self.main_frame, bootstyle="secondary")
        self.header.pack(fill="x")
        self.user_lbl = ttk.Label(
            self.header, text="👤 User", font=("Noto Sans Bengali", 14, "bold"), bootstyle="inverse-secondary"
        )
        self.user_lbl.pack(side="left", padx=15, pady=8)

        self.search_var = StringVar()
        self.search_entry = ttk.Entry(self.header, textvariable=self.search_var, width=25)
        self.search_entry.pack(side="right", padx=10)
        ttk.Button(self.header, text="🔍", bootstyle="secondary-outline").pack(side="right")
        self.settings_btn = ttk.Button(
            self.header, text="⚙️ Settings", bootstyle="secondary-outline", command=self.show_settings
        )
        self.settings_btn.pack(side="right", padx=5)
        ttk.Button(self.header, text="🔄 Refresh", bootstyle="secondary-outline", command=self.refresh_dashboard).pack(
            side="right", padx=5
        )
        self.logout_btn = ttk.Button(
            self.header, text="🚪 Logout", bootstyle="danger-outline", command=self.logout
        )
        self.logout_btn.pack(side="right", padx=5)

        # Right Frame
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(fill="both", expand=True)

        # Sidebar Separator
        ttk.Separator(self, orient="vertical").place(x=180, rely=0, y=0, relheight=1, bordermode="outside")

        # Modules
        self.modules = [
            ("🛒 বিক্রয়", "sale", SaleUI),
            ("📦 পণ্য", "product", ProductUI),
            ("📋 স্টক", "stock", StockUI),
            ("💼 সার্ভিস", "service", ServiceUI),
            ("⚡ রিচার্জ", "recharge", RechargeUI),
            ("📈 রিপোর্ট", "report", ReportUI),
            ("💳 খরচ", "expense", ExpenseUI),
            ("⏳ বাকি", "due", DuePaymentUI),  # 'বাকি ব্যবস্থাপনা'
            ("🔗 বারকোড", "barcode", BarcodeUI),
            ("🖨️ প্রিন্ট", "print", PrintUI),
        ]

        style = ttk.Style()
        style.configure("Sidebar.TButton", font=("Noto Sans Bengali", 13, "bold"), anchor="w", padding=(10, 7))
        style.map("Sidebar.TButton", background=[("active", "#2684ff")], foreground=[("active", "#fff")])

        self.module_buttons = {}
        self.modules_ui = {}   # key -> instance (lazy)
        self.active_module = None

        # Quick Actions (Dashboard)
        self.quick_actions_frame = None

        # Dark Mode & Dashboard Switch
        self.mode_switch = ttk.Checkbutton(
            self.left_frame, text="🌙 Dark Mode", bootstyle="secondary", command=self.toggle_theme
        )
        self.mode_switch.pack(pady=16, anchor="n")
        self.dashboard_switch = ttk.Checkbutton(
            self.left_frame, text="🏠 Dashboard / Module", bootstyle="secondary", command=self.toggle_dashboard_mode
        )
        self.dashboard_switch.pack(pady=8, anchor="n")

        self.init_modules()
        self.show_login()  # প্রথমে Login দেখানো হবে

    # ---------------- MODULE INITIALIZATION ----------------
    def init_modules(self):
        # শুধুই বাটন বানাই—মডিউলগুলো এখন 'lazy' তৈরি হবে (ক্লিকের সময়)
        for _, key, _ in self.modules:
            btn = SidebarButton(self.left_frame,
                                next(lbl for lbl, k, _ in self.modules if k == key),
                                command=lambda k=key: self.load_module(k),
                                active=False)
            self.module_buttons[key] = btn

    # ---------------- LOGIN / LOGOUT ----------------
    def login_success(self, user):
        self.logged_in_user = user
        self.user_lbl.config(text=f"👤 {user['username']}")
        self.show_dashboard()

    def logout(self):
        if messagebox.askyesno("Logout", "আপনি কি সত্যিই লগআউট করতে চান?"):
            self.logged_in_user = None
            self.clear_right_frame()
            self.user_lbl.config(text="👤 User")
            self.show_login()
            if self.logout_callback:
                self.logout_callback()

    # ---------------- DASHBOARD / MODULE ----------------
    def show_dashboard(self):
        self.clear_right_frame()
        try:
            self.dashboard_ui = DashboardUI(self.right_frame)
            if not hasattr(self.dashboard_ui, "frame"):
                self.dashboard_ui.frame = ttk.Frame(self.right_frame)
            self.dashboard_ui.frame.pack(fill="both", expand=True, padx=10, pady=10)
            self.render_quick_actions()
        except Exception:
            fallback = ttk.Frame(self.right_frame)
            ttk.Label(fallback, text="Dashboard failed to load", bootstyle="danger").pack(pady=30)
            fallback.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- QUICK ACTIONS ----------------
    def render_quick_actions(self):
        if self.quick_actions_frame:
            self.quick_actions_frame.destroy()
        self.quick_actions_frame = ttk.Labelframe(
            self.dashboard_ui.frame, text="Quick Actions", bootstyle="primary", padding=10
        )
        self.quick_actions_frame.pack(fill="x", pady=10)

        actions = [
            ("🛒 নতুন বিক্রয়", "sale"),
            ("📦 নতুন পণ্য", "product"),
            ("💼 সার্ভিস শুরু", "service"),
            ("⚡ রিচার্জ শুরু", "recharge"),
            ("💳 নতুন খরচ", "expense"),
        ]

        for name, key in actions:
            ttk.Button(
                self.quick_actions_frame, text=name, bootstyle="success-outline",
                command=lambda k=key: self.load_module_from_dashboard(k)
            ).pack(side="left", padx=5)

    def load_module_from_dashboard(self, key):
        self.dashboard_mode = False
        self.load_module(key)

    def toggle_dashboard_mode(self):
        self.dashboard_mode = not self.dashboard_mode
        if self.dashboard_mode:
            self.show_dashboard()
        elif self.active_module:
            self.load_module(self.active_module)

    # ---------------- SETTINGS ----------------
    def show_settings(self):
        self.clear_right_frame()
        if self.logged_in_user:
            self.settings_ui = SettingsUI(self.right_frame, self.logged_in_user, self.update_user_callback)
            self.settings_ui.frame.pack(fill="both", expand=True, padx=10, pady=10)

    def update_user_callback(self, new_info):
        update_user_info(self.logged_in_user["id"], username=new_info["username"], password=new_info["password"])
        self.logged_in_user.update(new_info)
        self.user_lbl.config(text=f"👤 {new_info['username']}")
        messagebox.showinfo("Success", "User info updated successfully!")

    # ---------------- MODULE (Lazy Load + Diagnostics) ----------------
    def _ensure_module_instance(self, key):
        """প্রয়োজনে মডিউল ইনস্ট্যান্স তৈরি করে self.modules_ui[key]-এ রাখে"""
        if key in self.modules_ui and self.modules_ui[key] is not None:
            return  # already created

        cls = next((cls for _, k, cls in self.modules if k == key), None)
        if cls is None:
            return

        try:
            instance = cls(self.right_frame)
            if not hasattr(instance, "frame"):
                instance.frame = ttk.Frame(self.right_frame)
            self.modules_ui[key] = instance
        except Exception as e:
            # ডায়াগনস্টিকস: আসল কারণ দেখাতে পপআপ
            tb = traceback.format_exc()
            print(f"[Module Load Error] key={key}\n{tb}")
            messagebox.showerror(
                "Module Load Failed",
                f"Module '{key}' লোড করতে সমস্যা হয়েছে:\n{e}\n\nDetails:\n{tb}"
            )
            # fallback frame দেখাই (আগের মতই)
            fallback = ttk.Frame(self.right_frame)
            ttk.Label(fallback, text=f"Module '{key}' failed to load", bootstyle="danger").pack(pady=30)
            self.modules_ui[key] = type("FallbackUI", (), {"frame": fallback})()

    def load_module(self, key):
        self.clear_right_frame()
        if self.dashboard_mode:
            self.show_dashboard()
        else:
            self._ensure_module_instance(key)
            module_instance = self.modules_ui.get(key)
            if module_instance and hasattr(module_instance, "frame"):
                module_instance.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.active_module = key
        self.update_sidebar_styles()

    # ---------------- UTILS ----------------
    def clear_right_frame(self):
        for child in self.right_frame.winfo_children():
            child.pack_forget()

    def update_sidebar_styles(self):
        for key, btn in self.module_buttons.items():
            btn.configure(bootstyle="primary" if key == self.active_module else "secondary-outline")

    def toggle_theme(self):
        style = ttk.Style()
        if self.current_theme == self.light_theme:
            style.theme_use(self.dark_theme)
            self.current_theme = self.dark_theme
        else:
            style.theme_use(self.light_theme)
            self.current_theme = self.light_theme

    def refresh_dashboard(self):
        if self.dashboard_mode:
            self.show_dashboard()
        elif self.active_module:
            self.load_module(self.active_module)

    # ---------------- LOGIN SCREEN ----------------
    def show_login(self):
        self.clear_right_frame()
        self.login_ui = LoginUI(self.right_frame, self.login_success)
        self.login_ui.frame.pack(fill="both", expand=True, padx=0, pady=0)
