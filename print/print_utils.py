import sys
import os
import platform
import tempfile
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from barcode_generator.barcode import generate_barcode_image

# ---------------- Printer Utilities ----------------
def get_default_printer():
    system_platform = platform.system()
    if system_platform == "Windows":
        try:
            import win32print
            return win32print.GetDefaultPrinter()
        except ImportError:
            print("Warning: win32print not installed. Install with: pip install pywin32")
            return None
    elif system_platform == "Linux":
        try:
            output = subprocess.check_output(['lpstat', '-d']).decode()
            return output.split(":")[1].strip()
        except:
            return None
    else:
        return None

def set_default_printer(printer_name):
    system_platform = platform.system()
    if system_platform == "Windows":
        try:
            import win32print
            win32print.SetDefaultPrinter(printer_name)
        except ImportError:
            print("Warning: win32print not installed. Install with: pip install pywin32")
    elif system_platform == "Linux":
        subprocess.run(["lpoptions", "-d", printer_name])
    else:
        raise NotImplementedError("Unsupported platform for setting default printer")

def list_printers():
    system_platform = platform.system()
    printers = []
    if system_platform == "Windows":
        try:
            import win32print
            printers_info = win32print.EnumPrinters(2)
            printers = [info[2] for info in printers_info]
        except ImportError:
            print("Warning: win32print not installed. Install with: pip install pywin32")
    elif system_platform == "Linux":
        try:
            output = subprocess.check_output(['lpstat', '-p']).decode()
            printers = [line.split()[1] for line in output.splitlines() if line.startswith("printer")]
        except:
            pass
    return printers

def print_file(file_path, printer_name=None):
    system_platform = platform.system()
    if system_platform == "Windows":
        if printer_name is None:
            printer_name = get_default_printer()
        cmd = f'PRINT /D:"{printer_name}" "{file_path}"'
        os.system(cmd)
    elif system_platform == "Linux":
        if printer_name:
            cmd = ["lp", "-d", printer_name, file_path]
        else:
            cmd = ["lp", file_path]
        subprocess.run(cmd)
    else:
        raise NotImplementedError("Unsupported platform for printing")

# ---------------- Barcode Utilities ----------------
def create_barcode_pdf(barcode_path: str, output_pdf_path: str):
    c = canvas.Canvas(output_pdf_path, pagesize=letter)
    c.drawImage(barcode_path, 100, 600, width=300, height=100)
    c.save()

def print_barcode_pdf(barcode_img_path: str, output_pdf_path: str = "barcode.pdf"):
    create_barcode_pdf(barcode_img_path, output_pdf_path)
    return output_pdf_path

def print_barcode(data: str, output_pdf_path: str = "barcode.pdf", printer_name: str = None):
    barcode_img_path = "barcode.png"
    generate_barcode_image(data, barcode_img_path)
    create_barcode_pdf(barcode_img_path, output_pdf_path)
    print_file(output_pdf_path, printer_name)

# ---------------- Receipt Utilities ----------------
def create_receipt_pdf(receipt_data: dict, output_pdf_path: str = "receipt.pdf"):
    c = canvas.Canvas(output_pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, receipt_data.get("store_name", "Store Name"))
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Date: {receipt_data.get('date', '')}")

    c.drawString(50, 690, "Items:")
    y = 670
    for name, qty, price in receipt_data.get("items", []):
        c.drawString(60, y, f"{name} (x{qty}) - {price} ৳")
        y -= 20

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 20, f"Total: {receipt_data.get('total', 0)} ৳")
    c.save()

def print_receipt(receipt_data: dict, printer_name: str = None):
    temp_pdf = tempfile.mktemp(suffix=".pdf")
    create_receipt_pdf(receipt_data, temp_pdf)
    print_file(temp_pdf, printer_name)

def print_receipt_pdf(product, quantity, unit_price, total_price, sale_date, output_pdf_path: str = "receipt.pdf"):
    receipt_data = {
        "store_name": "SmartShop",
        "date": sale_date,
        "items": [(product, quantity, unit_price)],
        "total": total_price
    }
    create_receipt_pdf(receipt_data, output_pdf_path)
    return output_pdf_path
