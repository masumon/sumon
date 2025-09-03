import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
from auth.user import authenticate_user, create_user, reset_password

class LoginUI:
    """
    লগইন স্ক্রিন UI
    on_success: callback যা MainApp এ লগইন সফল হলে কল হবে
    """
    def __init__(self, parent, on_success):
        self.parent = parent
        self.on_success = on_success
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(self.frame, text="লগইন করুন", font=("Helvetica", 18)).pack(pady=10)

        # Username
        ttk.Label(self.frame, text="ইউজার আইডি").pack(anchor="w")
        self.username_entry = ttk.Entry(self.frame)
        self.username_entry.pack(fill="x", pady=5)

        # Password
        ttk.Label(self.frame, text="পাসওয়ার্ড").pack(anchor="w")
        self.password_entry = ttk.Entry(self.frame, show="*")
        self.password_entry.pack(fill="x", pady=5)

        # Buttons
        ttk.Button(self.frame, text="লগইন", bootstyle="success", command=self.login).pack(pady=10)
        ttk.Button(self.frame, text="পাসওয়ার্ড রিসেট", bootstyle="warning-outline", command=self.reset_password_ui).pack(pady=5)
        ttk.Button(self.frame, text="নতুন ইউজার তৈরি", bootstyle="info-outline", command=self.new_user_ui).pack(pady=5)

    # ---------------- LOGIN ----------------
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = authenticate_user(username, password)
        if user:
            messagebox.showinfo("সফল", f"স্বাগতম {user['username']}!")
            self.frame.pack_forget()
            self.on_success(user)
        else:
            messagebox.showerror("ত্রুটি", "ইউজার আইডি বা পাসওয়ার্ড ভুল")

    # ---------------- PASSWORD RESET ----------------
    def reset_password_ui(self):
        username = self.username_entry.get()
        if not username:
            messagebox.showerror("ত্রুটি", "ইউজার আইডি দিন")
            return

        new_password = simpledialog.askstring("Password Reset", "নতুন পাসওয়ার্ড লিখুন", show="*")
        if new_password:
            reset_password(username, new_password)
            messagebox.showinfo("সফল", "পাসওয়ার্ড আপডেট হয়েছে")

    # ---------------- NEW USER ----------------
    def new_user_ui(self):
        username = simpledialog.askstring("নতুন ইউজার", "ইউজার নাম লিখুন")
        password = simpledialog.askstring("নতুন ইউজার", "পাসওয়ার্ড লিখুন", show="*")
        if username and password:
            create_user(username, password, "user")
            messagebox.showinfo("সফল", "নতুন ইউজার তৈরি হয়েছে")
