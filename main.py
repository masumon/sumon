import sys
import os
import ttkbootstrap as tb

# ----------------- Python Path Fix -----------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------- Local Module Imports --------
from ui.ui_main import MainApp
from ui.ui_login import LoginUI
from db import init_all_tables
from auth.user import create_user, get_all_users

# ----------------- Window Helper -----------------
def center_window(win, width, height):
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    win.geometry(f"{width}x{height}+{x}+{y}")

# ----------------- Main Program -----------------
if __name__ == "__main__":
    # Initialize database and default admin user
    init_all_tables()
    if not get_all_users():
        create_user("admin", "admin123", "admin")

    # Create main window
    root = tb.Window(title="SmartShop POS", themename="flatly", size=(1200, 700))
    center_window(root, 1200, 700)

    # ----------------- UI Helpers -----------------
    def clear_window():
        for widget in root.winfo_children():
            widget.destroy()

    def launch_dashboard(user):
        """Called after successful login"""
        clear_window()
        app = MainApp(master=root, logout_callback=launch_login)
        app.pack(fill=tb.constants.BOTH, expand=True)
        app.login_success(user)

    def launch_login():
        """Show login screen"""
        clear_window()
        LoginUI(root, launch_dashboard).frame.pack(fill=tb.constants.BOTH, expand=True)

    # ----------------- Start with Login -----------------
    launch_login()
    root.mainloop()
