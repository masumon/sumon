import os
import sys
import json
import threading
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.ui_login import LoginWindow
from ui.ui_sale import SaleUI
from ui.ui_service import ServiceUI
from ui.ui_recharge import RechargeUI
from ui.ui_barcode import BarcodeUI
from ui.ui_report import ReportUI
from ui.ui_product import ProductUI
from ui.ui_stock import StockUI
from ui.ui_print_utils import PrintUI
from ui.ui_expense import ExpenseUI

from service.service import initialize_service_tables
from product.product import initialize_product_tables
from auth.user import initialize_auth_tables
from recharge.recharge import initialize_recharge_tables

from settings import *

SETTINGS_FILE = "config/settings.json"
MAX_TABS = 10


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Settings load error: {e}")
    return {
        "theme": "superhero",
        "store_name": STORE_NAME,
        "owner_mobile": OWNER_MOBILE,
        "email": EMAIL,
    }


def save_settings(settings):
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Settings save error: {e}")


class CreateToolTip:
    def __init__(self, widget, text='টুলটিপ'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") or (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 30
        y = y + cy + self.widget.winfo_rooty() + 30
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, justify='left',
                          background="#ffffe0", relief='solid', borderwidth=1,
                          font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, background="#f9f9f9")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="My.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")


class SettingsWindow(ttk.Toplevel):
    def __init__(self, parent, current_settings, apply_theme_callback):
        super().__init__(parent)
        self.title("সেটিংস")
        self.geometry("400x350")
        self.resizable(False, False)
        self.apply_theme_callback = apply_theme_callback
        self.settings = current_settings

        ttk.Label(self, text="থিম নির্বাচন করুন:", font=("Arial", 12, "bold")).pack(pady=(15, 5))

        self.theme_var = ttk.StringVar(value=self.settings.get("theme", "superhero"))
        themes = ["superhero", "flatly", "darkly", "cosmo", "litera", "minty", "solar", "pulse"]
        self.theme_combo = ttk.Combobox(self, values=themes, textvariable=self.theme_var, state="readonly")
        self.theme_combo.pack(pady=5, padx=30, fill="x")
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)

        ttk.Label(self, text="দোকানের নাম:", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        self.store_name_var = ttk.StringVar(value=self.settings.get("store_name", ""))
        self.store_name_entry = ttk.Entry(self, textvariable=self.store_name_var)
        self.store_name_entry.pack(pady=5, padx=30, fill="x")

        ttk.Label(self, text="মালিকের মোবাইল:", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        self.owner_mobile_var = ttk.StringVar(value=self.settings.get("owner_mobile", ""))
        self.owner_mobile_entry = ttk.Entry(self, textvariable=self.owner_mobile_var)
        self.owner_mobile_entry.pack(pady=5, padx=30, fill="x")

        ttk.Label(self, text="ইমেইল:", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        self.email_var = ttk.StringVar(value=self.settings.get("email", ""))
        self.email_entry = ttk.Entry(self, textvariable=self.email_var)
        self.email_entry.pack(pady=5, padx=30, fill="x")

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)

        save_btn = ttk.Button(button_frame, text="সেভ করুন", bootstyle="success", command=self.save_settings)
        save_btn.pack(side="left", padx=10)

        cancel_btn = ttk.Button(button_frame, text="বাতিল", bootstyle="secondary", command=self.destroy)
        cancel_btn.pack(side="left", padx=10)

    def on_theme_change(self, event=None):
        new_theme = self.theme_var.get()
        self.apply_theme_callback(new_theme)

    def save_settings(self):
        self.settings["theme"] = self.theme_var.get()
        self.settings["store_name"] = self.store_name_var.get()
        self.settings["owner_mobile"] = self.owner_mobile_var.get()
        self.settings["email"] = self.email_var.get()

        save_settings(self.settings)
        messagebox.showinfo("সফল", "সেটিংস সেভ হয়েছে!")
        self.destroy()


class LoadingSpinner(ttk.Toplevel):
    def __init__(self, parent, message="লোড হচ্ছে..."):
        super().__init__(parent)
        self.title("")
        self.geometry("250x80")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        ttk.Label(self, text=message, font=("Arial", 12)).pack(pady=20)
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.progress.pack(fill='x', padx=20)
        self.progress.start(10)


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("এবিও এন্টারপ্রাইজ")
        self.settings = load_settings()
        self.style = ttk.Style()

        try:
            self.style.theme_use(self.settings.get("theme", "superhero"))
        except Exception:
            self.style.theme_use("superhero")

        self.center_window(0.9, 0.8)
        self.current_user = None
        self.current_user_role = None
        self.status_var = tk.StringVar(value="সফটওয়্যার চালু হয়েছে।")

        self.build_dashboard()
        self.dashboard_frame.pack_forget()

        self.login_frame = LoginWindow(self.root, self.on_login_success)
        self.login_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.root.bind_all("<Control-q>", lambda e: self.exit_app())
        self.root.bind_all("<Control-s>", lambda e: self.open_settings())
        self.root.bind_all("<Control-l>", lambda e: self.logout())

    def center_window(self, width_ratio=0.9, height_ratio=0.8):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * width_ratio)
        window_height = int(screen_height * height_ratio)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 500)
        self.root.maxsize(screen_width, screen_height)
        self.root.configure(bg="#f9f9f9")

    def build_dashboard(self):
        self.dashboard_frame = ttk.Frame(self.root, style="My.TFrame")

        self.header_frame = ttk.Frame(self.dashboard_frame, height=120, bootstyle="primary")
        self.header_frame.pack(fill="x")

        self.store_name_label = ttk.Label(self.header_frame, text=self.settings.get("store_name", STORE_NAME),
                                          font=("Arial", 24, "bold"), bootstyle="inverse-primary")
        self.store_name_label.pack(anchor="w", padx=15, pady=10)

        self.owner_mobile_label = ttk.Label(self.header_frame,
                                           text=f"মোবাইল: {self.settings.get('owner_mobile', OWNER_MOBILE)}",
                                           bootstyle="inverse-primary")
        self.owner_mobile_label.pack(anchor="w", padx=15)

        self.email_label = ttk.Label(self.header_frame,
                                     text=f"ইমেইল: {self.settings.get('email', EMAIL)}",
                                     bootstyle="inverse-primary")
        self.email_label.pack(anchor="w", padx=15)

        main_frame = ttk.Frame(self.dashboard_frame, style="My.TFrame")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        canvas_left = tk.Canvas(left_panel, bg="#f9f9f9", highlightthickness=0, width=200)
        scrollbar_left = ttk.Scrollbar(left_panel, orient="vertical", command=canvas_left.yview)
        scrollable_left = ttk.Frame(canvas_left)

        scrollable_left.bind(
            "<Configure>",
            lambda e: canvas_left.configure(scrollregion=canvas_left.bbox("all"))
        )

        canvas_left.create_window((0, 0), window=scrollable_left, anchor="nw")
        canvas_left.configure(yscrollcommand=scrollbar_left.set)

        canvas_left.pack(side="left", fill="both", expand=True)
        scrollbar_left.pack(side="right", fill="y")

        self.modules = [
            ("বিক্রয় করুন", self.open_sale_tab, "success"),
            ("সার্ভিস পরিচালনা", self.open_service_tab, "primary"),
            ("পণ্য যোগ করুন", self.open_product_tab, "info"),
            ("স্টক পরিচালনা", self.open_stock_tab, "secondary"),
            ("রিচার্জ করুন", self.open_recharge_tab, "warning"),
            ("বারকোড মডিউল", self.open_barcode_tab, "danger"),
            ("রিপোর্ট", self.open_report_tab, "dark"),
            ("প্রিন্ট অপশন", self.open_print_tab, "light"),
            ("খরচ পরিচালনা", self.open_expense_tab, "orange"),
        ]

        for text, cmd, style in self.modules:
            btn = ttk.Button(scrollable_left, text=text, bootstyle=style + " outline", command=cmd, width=20)
            btn.pack(pady=4, padx=8)
            CreateToolTip(btn, text=f"{text} মডিউল খুলুন")

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill="both", expand=True)

        self.tab_menu = tk.Menu(self.root, tearoff=0)
        self.tab_menu.add_command(label="ট্যাব বন্ধ করুন", command=self.close_current_tab)
        self.tab_menu.add_command(label="সব ট্যাব বন্ধ করুন", command=self.close_all_tabs)
        self.notebook.bind("<Button-3>", self.show_tab_menu)

        self.create_welcome_tab()

        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, bootstyle="info", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")

    def refresh_header_info(self):
        self.store_name_label.config(text=self.settings.get("store_name", STORE_NAME))
        self.owner_mobile_label.config(text=f"মোবাইল: {self.settings.get('owner_mobile', OWNER_MOBILE)}")
        self.email_label.config(text=f"ইমেইল: {self.settings.get('email', EMAIL)}")

    def create_welcome_tab(self):
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, option="text") == "স্বাগতম":
                self.notebook.select(tab_id)
                welcome_tab = self.notebook.nametowidget(tab_id)
                for widget in welcome_tab.winfo_children():
                    widget.destroy()
                welcome_label = ttk.Label(welcome_tab, text=f"স্বাগতম, {self.current_user or 'অতিথি'}!", font=("Arial", 18, "bold"))
                welcome_label.pack(pady=30)
                return

        welcome_tab = ttk.Frame(self.notebook)
        self.notebook.add(welcome_tab, text="স্বাগতম")
        self.notebook.select(welcome_tab)

        welcome_label = ttk.Label(welcome_tab, text=f"স্বাগতম, {self.current_user or 'অতিথি'}!", font=("Arial", 18, "bold"))
        welcome_label.pack(pady=30)

    def add_tab(self, title, window_class):
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, option="text") == title:
                self.notebook.select(tab_id)
                return

        if len(self.notebook.tabs()) >= MAX_TABS:
            messagebox.showwarning("সতর্কতা", "অতিরিক্ত ট্যাব খোলা যাবে না। কিছু ট্যাব বন্ধ করুন।")
            return

        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=title)
        self.notebook.select(tab_frame)

        spinner = LoadingSpinner(self.root, f"{title} মডিউল লোড হচ্ছে...")
        def load_module():
            try:
                scrollable_area = ScrollableFrame(tab_frame)
                scrollable_area.pack(fill="both", expand=True)
                window_class(scrollable_area.scrollable_frame)
            except Exception as e:
                messagebox.showerror("ত্রুটি", f"{title} মডিউল লোড করতে সমস্যা হয়েছে:\n{e}")
            finally:
                spinner.destroy()

        threading.Thread(target=load_module, daemon=True).start()

    def open_sale_tab(self): self.add_tab("বিক্রয় করুন", SaleUI)
    def open_service_tab(self): self.add_tab("সার্ভিস পরিচালনা", ServiceUI)
    def open_product_tab(self): self.add_tab("পণ্য যোগ করুন", ProductUI)
    def open_stock_tab(self): self.add_tab("স্টক পরিচালনা", StockUI)
    def open_recharge_tab(self): self.add_tab("রিচার্জ করুন", RechargeUI)
    def open_barcode_tab(self): self.add_tab("বারকোড মডিউল", BarcodeUI)
    def open_report_tab(self): self.add_tab("রিপোর্ট", ReportUI)
    def open_print_tab(self): self.add_tab("প্রিন্ট অপশন", PrintUI)
    def open_expense_tab(self): self.add_tab("খরচ পরিচালনা", ExpenseUI)

    def close_current_tab(self):
        current = self.notebook.select()
        if current:
            tab_text = self.notebook.tab(current, "text")
            if tab_text == "স্বাগতম":
                messagebox.showinfo("তথ্য", "স্বাগতম ট্যাব বন্ধ করা যাবে না।")
                return
            confirm = messagebox.askyesno("নিশ্চিত করুন", f"আপনি '{tab_text}' ট্যাবটি বন্ধ করতে চান?")
            if confirm:
                self.notebook.forget(current)

    def close_all_tabs(self):
        tabs = list(self.notebook.tabs())
        closable_tabs = [tab for tab in tabs if self.notebook.tab(tab, "text") != "স্বাগতম"]
        if not closable_tabs:
            messagebox.showinfo("তথ্য", "বন্ধ করার জন্য কোনো ট্যাব নেই।")
            return
        confirm = messagebox.askyesno("নিশ্চিত করুন", "সব ট্যাব বন্ধ করতে চান?")
        if confirm:
            for tab_id in closable_tabs:
                self.notebook.forget(tab_id)

    def show_tab_menu(self, event):
        try:
            self.tab_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tab_menu.grab_release()

    def on_login_success(self, username, role):
        self.current_user = username
        self.current_user_role = role
        self.status_var.set(f"স্বাগত {username}! আপনি লগইন হয়েছেন।")

        self.login_frame.pack_forget()
        self.dashboard_frame.pack(fill="both", expand=True)
        self.refresh_header_info()
        self.create_welcome_tab()

    def logout(self):
        answer = messagebox.askyesno("লগআউট", "আপনি কি লগআউট করতে চান?")
        if answer:
            self.current_user = None
            self.current_user_role = None
            self.status_var.set("লগআউট হয়েছে।")

            self.dashboard_frame.pack_forget()
            self.login_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

            tabs = list(self.notebook.tabs())
            for tab_id in tabs:
                self.notebook.forget(tab_id)

    def open_settings(self):
        SettingsWindow(self.root, self.settings, self.apply_theme)

    def apply_theme(self, theme_name):
        try:
            self.style.theme_use(theme_name)
            self.settings["theme"] = theme_name
            save_settings(self.settings)
        except Exception as e:
            messagebox.showerror("ত্রুটি", f"থিম পরিবর্তন করা যায়নি:\n{e}")

    def exit_app(self):
        if messagebox.askokcancel("প্রস্থান", "আপনি কি সফটওয়্যার থেকে বের হতে চান?"):
            self.root.destroy()


def main():
    root = ttk.Window(title="এবিও এন্টারপ্রাইজ", themename="superhero")

    icon_path = os.path.join("assets", "icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    # ডাটাবেজ টেবিল ইনিশিয়ালাইজেশন
    initialize_auth_tables()
    initialize_product_tables()
    initialize_service_tables()
    initialize_recharge_tables()

    app = MainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
