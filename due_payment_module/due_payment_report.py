# due_payment_module/due_payment_report.py

import os
import sys

# project root যোগ করা যাতে Python module ঠিকমত খুঁজে পায়
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# মূল due_payment.py থেকে ফাংশনগুলো import
from due_payment_module.due_payment import (
    get_customer_due_summary as real_get_customer_due_summary,
    get_due_payments_report as real_get_due_payments_report
)

# -----------------
# Legacy support functions for UI compatibility
# -----------------

def get_customer_due_summary(customer_name):
    """
    Legacy function to maintain compatibility with UI imports.
    Calls the real function from due_payment.py
    """
    return real_get_customer_due_summary(customer_name)

def get_due_payments_report(start_date=None, end_date=None):
    """
    Legacy function to maintain compatibility with UI imports.
    Calls the real function from due_payment.py
    """
    return real_get_due_payments_report(start_date, end_date)
