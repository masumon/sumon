import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from recharge.recharge import add_recharge, get_all_recharges, delete_recharge, get_all_operators

class RechargeUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="#f9f9f9")
        self.pack(fill="both", expand=True)

        self.operator_map = {}
        self.create_widgets()
        self.load_operators()
        self.load_recharges()

    def create_widgets(self):
        input_frame = tk.Frame(self, bg="#f9f9f9")
        input_frame.pack(padx=10, pady=10, fill="x")

        # মোবাইল নাম্বার
        tk.Label(input_frame, text="মোবাইল নাম্বার:", bg="#f9f9f9").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.mobile_entry = tk.Entry(input_frame)
        self.mobile_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # অপারেটর
        tk.Label(input_frame, text="অপারেটর:", bg="#f9f9f9").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.operator_combo = ttk.Combobox(input_frame, state="readonly")
        self.operator_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # পরিমাণ
        tk.Label(input_frame, text="টাকার পরিমাণ:", bg="#f9f9f9").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # রিচার্জ যোগ করুন বাটন
        tk.Button(input_frame, text="রিচার্জ যোগ করুন", bg="green", fg="white", command=self.add_recharge_data).grid(row=3, column=0, columnspan=2, pady=10)

        # সার্চ ফ্রেম
        search_frame = tk.Frame(self, bg="#f9f9f9")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="সার্চ মোবাইল নাম্বার:", bg="#f9f9f9").pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5)

        tk.Button(search_frame, text="সার্চ", command=self.search_recharge).pack(side="left", padx=5)
        tk.Button(search_frame, text="সব দেখাও", command=self.load_recharges).pack(side="left", padx=5)

        # টেবিল ফ্রেম
        table_frame = tk.Frame(self, bg="#f9f9f9")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "mobile_number", "operator", "amount", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="আইডি")
        self.tree.heading("mobile_number", text="মোবাইল নাম্বার")
        self.tree.heading("operator", text="অপারেটর")
        self.tree.heading("amount", text="টাকা")
        self.tree.heading("date", text="তারিখ")

        for col in columns:
            self.tree.column(col, anchor="center", width=100)

        self.tree.pack(fill="both", expand=True)

        # বাটন ফ্রেম
        btn_frame = tk.Frame(self, bg="#f9f9f9")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="🗑️ ডিলিট করুন", command=self.delete_selected).pack(side="left", padx=10)
        tk.Button(btn_frame, text="🖨️ প্রিন্ট করুন", command=self.print_selected).pack(side="left", padx=10)

    def load_operators(self):
        operators = get_all_operators()
        names = [op[1] for op in operators]
        self.operator_map = {op[1]: op[0] for op in operators}
        self.operator_combo['values'] = names
        if names:
            self.operator_combo.current(0)

    def add_recharge_data(self):
        mobile = self.mobile_entry.get().strip()
        operator_name = self.operator_combo.get().strip()
        amount = self.amount_entry.get().strip()

        if not mobile or not operator_name or not amount:
            messagebox.showerror("ত্রুটি", "সব ঘর পূরণ করুন।")
            return

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("ত্রুটি", "টাকার পরিমাণ সঠিক নয়।")
            return

        operator_id = self.operator_map.get(operator_name)
        if operator_id is None:
            messagebox.showerror("ত্রুটি", "অপারেটর সঠিক নয়।")
            return

        success = add_recharge(mobile_number=mobile, operator_id=operator_id, amount=amount)
        if success:
            messagebox.showinfo("সফল", "রিচার্জ সফলভাবে যোগ করা হয়েছে।")
            self.mobile_entry.delete(0, tk.END)
            self.operator_combo.set("")
            self.amount_entry.delete(0, tk.END)
            self.load_recharges()
        else:
            messagebox.showerror("ত্রুটি", "রিচার্জ যোগে সমস্যা হয়েছে।")

    def load_recharges(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = get_all_recharges()
        for recharge in data:
            self.tree.insert("", tk.END, values=recharge)

    def search_recharge(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_recharges()
            return

        all_recharges = get_all_recharges()
        filtered = [r for r in all_recharges if keyword in r[1]]

        for row in self.tree.get_children():
            self.tree.delete(row)
        for recharge in filtered:
            self.tree.insert("", tk.END, values=recharge)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("সতর্কতা", "কোনো রেকর্ড নির্বাচন করা হয়নি।")
            return

        item = self.tree.item(selected[0])
        recharge_id = item["values"][0]

        confirm = messagebox.askyesno("নিশ্চিত?", "আপনি কি নিশ্চিতভাবে মুছে ফেলতে চান?")
        if confirm:
            success = delete_recharge(recharge_id)
            if success:
                self.load_recharges()
                messagebox.showinfo("সফল", "রেকর্ড মুছে ফেলা হয়েছে।")
            else:
                messagebox.showerror("ত্রুটি", "রেকর্ড মুছতে সমস্যা হয়েছে।")

    def print_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("সতর্কতা", "কোনো রেকর্ড নির্বাচন করা হয়নি।")
            return

        item = self.tree.item(selected[0])
        values = item["values"]
        content = (
            f"রিচার্জ রেকর্ড:\n\n"
            f"আইডি: {values[0]}\n"
            f"মোবাইল: {values[1]}\n"
            f"অপারেটর: {values[2]}\n"
            f"পরিমাণ: {values[3]}\n"
            f"তারিখ: {values[4]}"
        )

        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)
            messagebox.showinfo("সফল", f"ফাইল সেভ হয়েছে: {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("রিচার্জ মডিউল - SmartShop POS")
    root.geometry("700x600")
    app = RechargeUI(root)
    root.mainloop()
