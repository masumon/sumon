import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk, messagebox
from service.service import (
    get_all_service_types, add_service_type, get_all_service_requests,
    add_service_request, update_service_request_status
)

class ServiceUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tab_control = ttk.Notebook(self)

        self.tab_type = ttk.Frame(tab_control)
        self.tab_request = ttk.Frame(tab_control)

        tab_control.add(self.tab_type, text='🛠️ সার্ভিস টাইপ')
        tab_control.add(self.tab_request, text='📋 সার্ভিস রিকোয়েস্ট')

        tab_control.pack(expand=1, fill='both')

        self.setup_service_type_tab()
        self.setup_service_request_tab()

    def setup_service_type_tab(self):
        tk.Label(self.tab_type, text="নাম:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_type_name = tk.Entry(self.tab_type)
        self.entry_type_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.tab_type, text="বর্ণনা:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_type_description = tk.Entry(self.tab_type)
        self.entry_type_description.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.tab_type, text="✅ যোগ করুন", command=self.add_service_type).grid(row=2, column=1, pady=10)

        tk.Button(self.tab_type, text="🔄 রিফ্রেশ", command=self.load_service_types).grid(row=2, column=0, pady=10)

        self.type_tree = ttk.Treeview(self.tab_type, columns=("ID", "Name", "Description"), show="headings")
        self.type_tree.heading("ID", text="আইডি")
        self.type_tree.heading("Name", text="নাম")
        self.type_tree.heading("Description", text="বর্ণনা")
        self.type_tree.grid(row=3, column=0, columnspan=2, pady=10, sticky='nsew')

        self.tab_type.grid_rowconfigure(3, weight=1)
        self.tab_type.grid_columnconfigure(1, weight=1)

        self.load_service_types()

    def add_service_type(self):
        name = self.entry_type_name.get().strip()
        description = self.entry_type_description.get().strip()

        if not name:
            messagebox.showerror("ত্রুটি", "নাম অবশ্যই দিতে হবে।")
            return

        success = add_service_type(name, description)
        if success:
            messagebox.showinfo("সফল", "সার্ভিস টাইপ যোগ হয়েছে!")
            self.entry_type_name.delete(0, tk.END)
            self.entry_type_description.delete(0, tk.END)
            self.load_service_types()
        else:
            messagebox.showerror("ত্রুটি", "সার্ভিস টাইপ যোগ করা যায়নি।")

    def load_service_types(self):
        for row in self.type_tree.get_children():
            self.type_tree.delete(row)
        for t in get_all_service_types():
            self.type_tree.insert("", tk.END, values=t)

    def setup_service_request_tab(self):
        tk.Label(self.tab_request, text="কাস্টমারের নাম:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_customer_name = tk.Entry(self.tab_request)
        self.entry_customer_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.tab_request, text="সার্ভিস টাইপ:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.combo_type = ttk.Combobox(self.tab_request, state='readonly')
        self.combo_type.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.tab_request, text="বিস্তারিত:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.entry_details = tk.Entry(self.tab_request)
        self.entry_details.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.tab_request, text="মূল্য:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.entry_price = tk.Entry(self.tab_request)
        self.entry_price.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(self.tab_request, text="✅ রিকোয়েস্ট যোগ করুন", command=self.add_request).grid(row=4, column=1, pady=10, sticky='e')

        tk.Button(self.tab_request, text="🔄 রিফ্রেশ", command=self.load_service_requests).grid(row=4, column=0, pady=10, sticky='w')

        self.req_tree = ttk.Treeview(self.tab_request, columns=("ID", "Type", "Customer", "Details", "Status", "Price", "Date"), show="headings")
        self.req_tree.heading("ID", text="আইডি")
        self.req_tree.heading("Type", text="টাইপ")
        self.req_tree.heading("Customer", text="কাস্টমার")
        self.req_tree.heading("Details", text="বিস্তারিত")
        self.req_tree.heading("Status", text="স্ট্যাটাস")
        self.req_tree.heading("Price", text="মূল্য")
        self.req_tree.heading("Date", text="তারিখ")
        self.req_tree.grid(row=5, column=0, columnspan=3, pady=10, sticky='nsew')

        tk.Label(self.tab_request, text="নতুন স্ট্যাটাস:").grid(row=6, column=0, padx=5, pady=5, sticky='e')
        self.status_combo = ttk.Combobox(self.tab_request, values=["Pending", "Processing", "Completed"], state="readonly")
        self.status_combo.grid(row=6, column=1, padx=5, pady=5, sticky='w')

        self.update_status_btn = tk.Button(self.tab_request, text="স্ট্যাটাস আপডেট করুন", command=self.update_status)
        self.update_status_btn.grid(row=6, column=2, padx=5, pady=5)

        self.tab_request.grid_rowconfigure(5, weight=1)
        self.tab_request.grid_columnconfigure(1, weight=1)

        self.load_types_combobox()
        self.load_service_requests()

        self.req_tree.bind("<<TreeviewSelect>>", self.on_request_select)

    def load_types_combobox(self):
        self.service_types = get_all_service_types()
        self.combo_type['values'] = [t[1] for t in self.service_types]

    def add_request(self):
        customer_name = self.entry_customer_name.get().strip()
        details = self.entry_details.get().strip()
        price = self.entry_price.get().strip()

        type_index = self.combo_type.current()
        if type_index == -1:
            messagebox.showerror("ত্রুটি", "সার্ভিস টাইপ নির্বাচন করুন।")
            return

        service_type_id = self.service_types[type_index][0]

        if not customer_name:
            messagebox.showerror("ত্রুটি", "কাস্টমারের নাম দিতে হবে।")
            return

        if not price:
            messagebox.showerror("ত্রুটি", "মূল্য দিতে হবে।")
            return

        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("ত্রুটি", "মূল্য সঠিক সংখ্যা হতে হবে।")
            return

        success = add_service_request(service_type_id, customer_name, details, price)
        if success:
            messagebox.showinfo("সফল", "সার্ভিস রিকোয়েস্ট যোগ হয়েছে!")
            self.entry_customer_name.delete(0, tk.END)
            self.entry_details.delete(0, tk.END)
            self.entry_price.delete(0, tk.END)
            self.load_service_requests()
        else:
            messagebox.showerror("ত্রুটি", "রিকোয়েস্ট যোগ করা যায়নি।")

    def load_service_requests(self):
        for row in self.req_tree.get_children():
            self.req_tree.delete(row)
        for r in get_all_service_requests():
            self.req_tree.insert("", tk.END, values=r)
        self.status_combo.set("")

    def on_request_select(self, event):
        selected = self.req_tree.selection()
        if selected:
            item = self.req_tree.item(selected[0])
            status = item['values'][4]
            self.status_combo.set(status)

    def update_status(self):
        selected = self.req_tree.selection()
        if not selected:
            messagebox.showerror("ত্রুটি", "অনুগ্রহ করে একটি রিকোয়েস্ট নির্বাচন করুন।")
            return
        new_status = self.status_combo.get()
        if new_status not in ["Pending", "Processing", "Completed"]:
            messagebox.showerror("ত্রুটি", "সঠিক স্ট্যাটাস নির্বাচন করুন।")
            return

        request_id = self.req_tree.item(selected[0])['values'][0]
        success = update_service_request_status(request_id, new_status)
        if success:
            messagebox.showinfo("সফল", "স্ট্যাটাস সফলভাবে আপডেট হয়েছে।")
            self.load_service_requests()
        else:
            messagebox.showerror("ত্রুটি", "স্ট্যাটাস আপডেট করা যায়নি।")


if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceUI(root)
    root.mainloop()
