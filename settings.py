import ttkbootstrap as ttk
# ====================== General Store Info ======================
STORE_NAME = "এবিও এন্টারপ্রাইজ"
PRINT_HEADER = "SmartShop POS - খশির আব্দুল্লাপুর"
DB_PATH = "database/smartshop.db"

# ====================== Store Contact Info ======================
ADDRESS = "খশির, আব্দুল্লাপুর, বৈরাগীবাজা, বিয়ানীবাজার, সিলেট"
OWNER = "মোমেইন আহমদ সুমন"
OWNER_MOBILE = "01825007977"
EMAIL = "abo.enterprise@gmail.com"
SUPPORT_PHONE = "01825007977"
OFFICE_TIME = "সকাল ৯টা - রাত ১১ টা"

# ====================== Managers ======================
MANAGERS = [
    {"name": "আব্দুর রহমান", "mobile": "01885411007"},
    {"name": "ওয়াহিদুর রহমান", "mobile": "01877264747"},
]

# ====================== Software Info ======================
SOFTWARE_DESC = "এবিও এন্টারপ্রাইজ মোবাইল বিক্রয় ও স্টক ব্যবস্থাপনা সফটওয়্যার।"
COPYRIGHT = "© ২০২৫ এবিও এন্টারপ্রাইজ। সর্বস্বত্ব সংরক্ষিত।"
VERSION = "v1.0"
RELEASE_DATE = "2025-08-09"

# ====================== Printer / Receipt Settings ======================
RECEIPT_HEADER = PRINT_HEADER
RECEIPT_FOOTER = f"{SOFTWARE_DESC}\n{COPYRIGHT}"

# ====================== Misc ======================
DEFAULT_CURRENCY = "৳"  # টাকা
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ====================== Optional Settings ======================
ENABLE_BARCODE = True        # বারকোড ব্যবহার করতে হলে True
ENABLE_EXCEL_EXPORT = True   # এক্সেল এক্সপোর্ট
ENABLE_PDF_EXPORT = True     # PDF এক্সপোর্ট
ENABLE_AI_MODULE = True      # AI / Predictive module
ENABLE_RECHARGE_MODULE = True
ENABLE_DUE_PAYMENT_MODULE = True
ENABLE_EXPENSE_MODULE = True
