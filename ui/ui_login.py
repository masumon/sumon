import ttkbootstrap as ttk
from tkinter import messagebox

class LoginWindow(ttk.Frame):
    def __init__(self, parent, login_success_callback):
        super().__init__(parent)
        self.parent = parent
        self.login_success_callback = login_success_callback

        ttk.Label(self, text="ব্যবহারকারীর নাম").pack(pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        ttk.Label(self, text="পাসওয়ার্ড").pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        login_btn = ttk.Button(self, text="লগইন", command=self.check_login)
        login_btn.pack(pady=20)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # TODO: এখানে আপনার ডাটাবেস/অথেন্টিকেশন চেক করবেন
        # নিচে একটি ডেমো লগিক দেওয়া হল
        if username == "admin" and password == "admin123":
            role = "admin"
        elif username == "user" and password == "user123":
            role = "user"
        else:
            messagebox.showerror("ত্রুটি", "ভুল ব্যবহারকারীর নাম অথবা পাসওয়ার্ড")
            return

        self.login_success_callback(username, role)
