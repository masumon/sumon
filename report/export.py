from report.report import get_sales_report_by_date, get_monthly_profit_report

def fetch_sales_report(start_date, end_date):
    return get_sales_report_by_date(start_date, end_date)

def fetch_profit_report(month, year):
    return get_monthly_profit_report(month, year)
