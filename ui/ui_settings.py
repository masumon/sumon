import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class SettingsUI:
    def __init__(self, parent, user, save_callback=None):
        """
        user: dict, current logged-in user data
        save_callback: function, called when settings are saved
        """
        self.parent = parent
        self.user = user
        self.save_callback = save_callback
        self.frame = ttk.Frame(parent)
        self.build_ui()

    def build_ui(self):
        ttk.Label(self.frame, text="Settings", font=("Helvetica", 16, "bold")).pack(pady=10)

        form_frame = ttk.Frame(self.frame)
        form_frame.pack(pady=10, padx=20, fill="x")

        # Username
        ttk.Label(form_frame, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.username_var = ttk.StringVar(value=self.user.get("username", ""))
        ttk.Entry(form_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, pady=5)

        # Email
        ttk.Label(form_frame, text="Email:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.email_var = ttk.StringVar(value=self.user.get("email", ""))
        ttk.Entry(form_frame, textvariable=self.email_var, width=30).grid(row=1, column=1, pady=5)

        # Password
        ttk.Label(form_frame, text="Password:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.password_var = ttk.StringVar(value=self.user.get("password", ""))
        ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=30).grid(row=2, column=1, pady=5)

        # Dark Mode Switch
        self.dark_mode_var = ttk.BooleanVar(value=self.user.get("dark_mode", False))
        ttk.Checkbutton(form_frame, text="🌙 Dark Mode", variable=self.dark_mode_var, bootstyle="success").grid(row=3, column=0, columnspan=2, pady=10, sticky="w")

        # Dashboard Switch
        self.dashboard_var = ttk.BooleanVar(value=self.user.get("start_dashboard", True))
        ttk.Checkbutton(form_frame, text="Start at Dashboard", variable=self.dashboard_var, bootstyle="info").grid(row=4, column=0, columnspan=2, pady=5, sticky="w")

        # Save button
        ttk.Button(self.frame, text="💾 Save Settings", bootstyle="success", command=self.save_settings).pack(pady=15)

    def save_settings(self):
        """
        Collect data and call save_callback if provided
        """
        new_info = {
            "username": self.username_var.get(),
            "email": self.email_var.get(),
            "password": self.password_var.get(),
            "dark_mode": self.dark_mode_var.get(),
            "start_dashboard": self.dashboard_var.get(),
        }
        if self.save_callback:
            self.save_callback(new_info)
        ttk.Label(self.frame, text="Settings saved successfully!", bootstyle="success").pack(pady=5)
