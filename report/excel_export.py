import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

def export_sales_report_excel(data, start_date, end_date, filename="sales_report.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "বিক্রয় রিপোর্ট"

    ws.merge_cells('A1:F1')
    ws['A1'] = f"বিক্রয় রিপোর্ট: {start_date} থেকে {end_date}"
    ws['A1'].font = Font(size=14, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')

    headers = ["আইডি", "পণ্য", "পরিমাণ", "ইউনিট মূল্য", "মোট মূল্য", "তারিখ"]
    ws.append(headers)

    for row in data:
        ws.append([
            row['sale_id'],
            row['product_name'],
            row['quantity'],
            row['unit_price'],
            row['total_price'],
            row['sale_date']
        ])

    for col_num in range(1, 7):
        ws.column_dimensions[get_column_letter(col_num)].width = 20

    wb.save(filename)
    return filename

def export_profit_report_excel(data, month, year, filename="profit_report.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "লাভ রিপোর্ট"

    ws.merge_cells('A1:G1')
    ws['A1'] = f"মাসিক লাভ রিপোর্ট: {month}/{year}"
    ws['A1'].font = Font(size=14, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')

    headers = ["পণ্য", "পরিমাণ", "ক্রয়মূল্য", "বিক্রয়মূল্য", "মোট বিক্রয়", "লাভ", "তারিখ"]
    ws.append(headers)

    for row in data['details']:
        ws.append([
            row['product_name'],
            row['quantity'],
            row['purchase_price'],
            row['sale_price'],
            row['total_sell'],
            row['profit'],
            row['sale_date']
        ])

    ws.append([])
    ws.append(["", "", "", "", "মোট লাভ:", data['total_profit']])

    for col_num in range(1, 8):
        ws.column_dimensions[get_column_letter(col_num)].width = 20

    wb.save(filename)
    return filename
