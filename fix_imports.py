import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))  # smartshop_pos ফোল্ডার

def fix_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    new_lines = []

    has_sys_path = any("sys.path.append" in line for line in lines[:10])
    import_inserted = False

    for line in lines:
        # import লাইন আপডেট
        if line.strip().startswith("from database.db import"):
            line = line.replace("from database.db import", "from db import")
            changed = True

        # sys.path.append না থাকলে প্রথম ইমপোর্টের আগে যোগ করব
        if not has_sys_path and line.strip().startswith("import"):
            if not import_inserted:
                new_lines.append("import sys\n")
                new_lines.append("import os\n")
                new_lines.append("sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n")
                changed = True
                import_inserted = True

        new_lines.append(line)

    if changed:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"[FIXED] {file_path}")
    else:
        print(f"[OK] {file_path}")

def main():
    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith(".py"):
                fix_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
