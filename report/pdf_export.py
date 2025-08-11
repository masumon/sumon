from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ফন্ট রেজিস্টার করুন
pdfmetrics.registerFont(TTFont('SiyamRupali', 'report/fonts/SiyamRupali.ttf'))

def export_sales_report_pdf(data, start_date, end_date, filename="sales_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Bangla', fontName='SiyamRupali', fontSize=12))

    elements = []

    title = Paragraph(f"📅 বিক্রয় রিপোর্ট: {start_date} থেকে {end_date}", styles['Bangla'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    headers = ["আইডি", "পণ্য", "পরিমাণ", "ইউনিট মূল্য", "মোট মূল্য", "তারিখ"]
    data_table = [headers]

    for row in data:
        data_table.append([
            str(row['sale_id']),
            row['product_name'],
            str(row['quantity']),
            f"{row['unit_price']:.2f}",
            f"{row['total_price']:.2f}",
            row['sale_date']
        ])

    table = Table(data_table, repeatRows=1)
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'SiyamRupali'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    elements.append(table)
    doc.build(elements)
    return filename


def export_profit_report_pdf(data, month, year, filename="profit_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Bangla', fontName='SiyamRupali', fontSize=12))

    elements = []

    title = Paragraph(f"📊 মাসিক লাভ রিপোর্ট: {month}/{year}", styles['Bangla'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    headers = ["পণ্য", "পরিমাণ", "ক্রয়মূল্য", "বিক্রয়মূল্য", "মোট বিক্রয়", "লাভ", "তারিখ"]
    data_table = [headers]

    for row in data['details']:
        data_table.append([
            row['product_name'],
            str(row['quantity']),
            f"{row['purchase_price']:.2f}",
            f"{row['sale_price']:.2f}",
            f"{row['total_sell']:.2f}",
            f"{row['profit']:.2f}",
            row['sale_date']
        ])

    # মোট লাভের সারি
    data_table.append([])
    data_table.append(["", "", "", "", "মোট লাভ:", f"{data['total_profit']:.2f} টাকা"])

    table = Table(data_table, repeatRows=1)
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'SiyamRupali'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -3), 0.5, colors.black),
        ('SPAN', (-2, -1), (-1, -1)),
        ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    elements.append(table)
    doc.build(elements)
    return filename
