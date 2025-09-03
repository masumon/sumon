# SmartShop POS - এবিও এন্টারপ্রাইজ

একটি সম্পূর্ণ Point of Sale (POS) সিস্টেম মোবাইল বিক্রয় ও স্টক ব্যবস্থাপনার জন্য।

## ✨ বৈশিষ্ট্য

- 🛒 **বিক্রয় ব্যবস্থাপনা** - সহজ ও দ্রুত বিক্রয় প্রক্রিয়া
- 📦 **পণ্য ব্যবস্থাপনা** - পণ্য যোগ, সম্পাদনা ও মুছে ফেলা
- 📊 **স্টক ব্যবস্থাপনা** - রিয়েল-টাইম স্টক ট্র্যাকিং
- 🔧 **সার্ভিস ব্যবস্থাপনা** - গ্রাহক সার্ভিস ট্র্যাকিং
- 📱 **রিচার্জ সিস্টেম** - মোবাইল রিচার্জ ব্যবস্থাপনা
- 📈 **রিপোর্ট সিস্টেম** - বিক্রয়, খরচ ও অন্যান্য রিপোর্ট
- 💰 **খরচ ব্যবস্থাপনা** - ব্যবসায়িক খরচ ট্র্যাকিং
- 💳 **বাকি পেমেন্ট** - গ্রাহক বাকি টাকা ট্র্যাকিং
- 🏷️ **বারকোড জেনারেটর** - পণ্যের জন্য বারকোড তৈরি
- 🖨️ **প্রিন্ট সাপোর্ট** - রসিদ ও বারকোড প্রিন্ট

## 🚀 ইনস্টলেশন

### প্রয়োজনীয়তা
- Python 3.8+
- Windows 10+ (Linux/Mac supported)

### ধাপসমূহ

1. **প্রজেক্ট ডাউনলোড করুন:**
```bash
git clone <repository-url>
cd smartshop_pos
```

2. **Dependencies ইনস্টল করুন:**
```bash
pip install -r requirements.txt
```

3. **অ্যাপ্লিকেশন চালান:**
```bash
python main.py
```

## 🔑 লগইন তথ্য

**Default Admin:**
- Username: `admin`
- Password: `admin123`

## 📁 প্রজেক্ট স্ট্রাকচার

```
smartshop_pos/
│
├── main.py                 # মূল অ্যাপ্লিকেশন এন্ট্রি পয়েন্ট
├── settings.py             # কনফিগারেশন সেটিংস
├── db.py                   # ডাটাবেস কানেকশন ও CRUD
├── utils.py                # ইউটিলিটি ফাংশনসমূহ
├── requirements.txt        # Python dependencies
│
├── auth/                   # Authentication মডিউল
│   ├── login.py           # লগইন সিস্টেম
│   ├── role.py            # ইউজার রোল ম্যানেজমেন্ট  
│   └── user.py            # ইউজার ম্যানেজমেন্ট
│
├── product/               # Product মডিউল
│   ├── product.py         # প্রোডাক্ট CRUD
│   ├── stock.py           # স্টক ম্যানেজমেন্ট
│   └── sale.py            # সেল রেকর্ড
│
├── service/               # Service মডিউল
│   └── service.py         # সার্ভিস ম্যানেজমেন্ট
│
├── recharge/              # Recharge মডিউল
│   └── recharge.py        # রিচার্জ ম্যানেজমেন্ট
│
├── report/                # Report মডিউল
│   ├── report.py          # রিপোর্ট জেনারেশন
│   ├── export.py          # ডেটা এক্সপোর্ট
│   ├── pdf_export.py      # PDF এক্সপোর্ট
│   └── excel_export.py    # Excel এক্সপোর্ট
│
├── barcode_generator/     # Barcode মডিউল
│   └── barcode.py         # বারকোড জেনারেশন
│
├── expense_module/        # Expense মডিউল
│   ├── expense.py         # খরচ ম্যানেজমেন্ট
│   ├── expense_report.py  # খরচ রিপোর্ট
│   └── expense_category.py # খরচের ক্যাটাগরি
│
├── due_payment_module/    # Due Payment মডিউল
│   ├── due_payment.py     # বাকি পেমেন্ট ম্যানেজমেন্ট
│   └── due_payment_report.py # বাকি পেমেন্ট রিপোর্ট
│
├── ui/                    # User Interface মডিউল
│   ├── ui_main.py         # মূল UI
│   ├── ui_product.py      # প্রোডাক্ট UI
│   ├── ui_service.py      # সার্ভিস UI
│   ├── ui_recharge.py     # রিচার্জ UI
│   ├── ui_report.py       # রিপোর্ট UI
│   ├── ui_expense.py      # খরচ UI
│   ├── ui_login.py        # লগইন UI
│   ├── ui_barcode.py      # বারকোড UI
│   ├── ui_print_utils.py  # প্রিন্ট UI
│   ├── ui_sale.py         # সেল UI
│   ├── ui_due_payment.py  # বাকি পেমেন্ট UI
│   └── ui_stock.py        # স্টক UI
│
├── print/                 # Print মডিউল
│   └── print_utils.py     # প্রিন্টিং ইউটিলিটি
│
├── assets/                # Assets
│   ├── icon.ico           # অ্যাপ আইকন
│   ├── logo.png           # লোগো
│   └── icons/             # UI আইকনসমূহ
│
└── database/              # Database
    └── smartshop.db       # SQLite ডাটাবেস
```

## 🛠️ প্রযুক্তি

- **Frontend:** Python tkinter + ttkbootstrap
- **Database:** SQLite
- **Reports:** ReportLab (PDF), OpenPyXL (Excel)
- **Barcode:** python-barcode
- **UI Theme:** Modern Bootstrap themes

## 📊 ডাটাবেস স্কিমা

- **products** - পণ্যের তথ্য
- **stock** - স্টক ইতিহাস
- **sales** - বিক্রয় রেকর্ড
- **users** - ইউজার তথ্য
- **service_types** - সার্ভিস ধরন
- **service_requests** - সার্ভিস অনুরোধ
- **recharge** - রিচার্জ রেকর্ড
- **expenses** - খরচ রেকর্ড
- **expense_categories** - খরচের ক্যাটাগরি
- **due_payment** - বাকি পেমেন্ট

## 🎯 ব্যবহার

1. **লগইন করুন** admin credentials দিয়ে
2. **পণ্য যোগ করুন** Product মডিউল থেকে
3. **স্টক আপডেট করুন** Stock মডিউল থেকে
4. **বিক্রয় করুন** Sale মডিউল থেকে
5. **রিপোর্ট দেখুন** Report মডিউল থেকে

## 🔧 সাপোর্ট

**যোগাযোগ:**
- ই-মেইল: abo.enterprise@gmail.com
- ফোন: 01825007977
- ঠিকানা: খশির, আব্দুল্লাপুর, বৈরাগীবাজা, বিয়ানীবাজার, সিলেট

## 📝 লাইসেন্স

© ২০২৫ এবিও এন্টারপ্রাইজ। সর্বস্বত্ব সংরক্ষিত।

---

**SmartShop POS v1.0** - একটি আধুনিক ও সহজ POS সমাধান










