import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import sys
import re
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

def ensure_init_py(folder):
    """Ensure __init__.py exists in the given folder"""
    init_path = os.path.join(folder, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("# Auto-generated init file\n")
        print(f"[FIX] Created {init_path}")
    else:
        pass  # No need to print every time

def fix_import_paths():
    """Ensure ui and database are proper Python packages"""
    for folder in ["database", "ui"]:
        folder_path = os.path.join(PROJECT_ROOT, folder)
        if os.path.exists(folder_path):
            ensure_init_py(folder_path)
        else:
            print(f"[WARNING] '{folder}' folder not found!")

def auto_fix_imports_in_files():
    """Scan all .py files and fix wrong import paths"""
    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith(".py") and file != os.path.basename(__file__):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content = re.sub(
                    r"from\s+db\s+import",
                    "from database.db import",
                    content
                )

                if content != new_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"[FIX] Updated imports in: {file_path}")

def run_main():
    """Run main.py after fixing imports"""
    main_path = os.path.join(PROJECT_ROOT, "main.py")
    if os.path.exists(main_path):
        print("\n[RUNNING] Launching SmartShop POS...\n")
        subprocess.run([sys.executable, main_path])
    else:
        print("[ERROR] main.py not found!")

if __name__ == "__main__":
    fix_import_paths()
    auto_fix_imports_in_files()
    run_main()
